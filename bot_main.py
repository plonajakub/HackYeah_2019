from telegram import ParseMode
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
import logging
import mysql.connector as mariadb
from profiler.src import profiling_scripts as ps
from bot import articlesuserread, importproposedarticles
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class BotDatabase:
    dbconn = None

    def __init__(self):
        self.dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')

    def new_reader(self, id, first_name, last_name, username):
        sql_insert_new_reader = """REPLACE INTO readers VALUES (%s, %s, %s, %s)""".format(id, first_name, last_name,
                                                                                          username)
        try:
            c = self.dbconn.cursor()
            c.execute(sql_insert_new_reader, (id, first_name, last_name, username))
            self.dbconn.commit()
        except mariadb.Error as e:
            logging.error(e)


class ExtravaganzaBot:
    updater = Updater(token='882199233:AAF4xv_sUi6vi3Lw8qTSqD4XR710IJ3hlOc', use_context=True)
    dispatcher = updater.dispatcher

    # 297962379 - Przemek
    # 545636484 - Sergiusz
    # 389659954
    admins = [297962379, 545636484, 389659954]

    def __init__(self, dbconn: BotDatabase):
        self.db = dbconn

        start_handler = CommandHandler('start', self.start)
        ExtravaganzaBot.dispatcher.add_handler(start_handler)

        notify_handler = CommandHandler('notify', self.notify)
        ExtravaganzaBot.dispatcher.add_handler(notify_handler)

        notify_onet_handler = CommandHandler('notifyonet', self.notify_onet)
        ExtravaganzaBot.dispatcher.add_handler(notify_onet_handler)

        notify_one_hour_later = CommandHandler('onehourlater', self.one_hour_later)
        ExtravaganzaBot.dispatcher.add_handler(notify_one_hour_later)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        ExtravaganzaBot.dispatcher.add_handler(unknown_handler)

        self.send_direct_message(ExtravaganzaBot.admins[0], "ExtravaganzaBot was just *started*.",
                                 disable_notification=True)

        ExtravaganzaBot.updater.start_polling(1.0)
        ExtravaganzaBot.updater.idle()

    def send_direct_message(self, chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_notification=False):
        self.updater.bot.send_message(chat_id, message, parse_mode=parse_mode,
                                      disable_notification=disable_notification)
        logging.info("Sent message „%s” to chat %s." % (message, chat_id))

    def notify_about_new_articles(self, onet=False):
        c = self.db.dbconn.cursor(buffered=True)
        c.execute("SELECT links_for_readers.guid, links_for_readers.reader, articles.url FROM links_for_readers, articles WHERE articles.guid = links_for_readers.article AND links_for_readers.new = 1")
        print(c)
        users_in_progress = []
        for guid, reader, url in c:
            if reader not in users_in_progress:
                cx = self.db.dbconn.cursor()
                cx.execute("SELECT first_name FROM readers WHERE id = %s", (reader,))
                for x in cx:
                    first_name = x
                cx.close()
                self.send_direct_message(reader, "Dzień dobry, %s! Oto najciekawsze, naszym zdaniem, wydarzenia z Twojej okolicy, przygotowane przez _Axel News_ - najlepszą aplikację, która pozwala Ci pozostać na bieżąco!" % (first_name))
                users_in_progress.append(reader)
                if onet:
                    msg = "[%s](%s)" % (url, url)
                else:
                    msg = "[http://frappe.iiar.pwr.edu.pl:5000/%s](http://frappe.iiar.pwr.edu.pl:5000/%s)" % (guid, guid)

            self.send_direct_message(reader, msg)

            cx = self.db.dbconn.cursor()
            cx.execute("UPDATE links_for_readers SET new = 0 WHERE guid = %s", (guid,))
            self.db.dbconn.commit()
            cx.close()
        c.close()

    def start(self, update, context):
        if update.message.chat.type == 'private':
            user = update.message.chat.first_name
            title = update.message.chat.username
        else:
            user = update.message.chat.title
            title = user

        context.bot.send_message(chat_id=update.message.chat_id, text="Cześć, %s! Wkrótce otrzymasz od nas informacje na temat najciekawszych wydarzeń w okolicy." % user)
        logging.info("Chat ID: %s; Chat @: %s" % (update.message.chat_id, title))
        self.db.new_reader(update.message.chat_id, update.message.chat.first_name, update.message.chat.last_name,
                           title)

    def notify(self, update, context):
        if update.message.chat_id in ExtravaganzaBot.admins:
            context.bot.send_message(chat_id=update.message.chat_id, text="Uruchomiono powiadamianie.")
            self.notify_about_new_articles()
        else:
            self.unknown(update, context)

    def notify_onet(self, update, context):
        if update.message.chat_id in ExtravaganzaBot.admins:
            context.bot.send_message(chat_id=update.message.chat_id, text="Uruchomiono powiadamianie.")
            self.notify_about_new_articles(onet=True)
        else:
            self.unknown(update, context)

    def one_hour_later(self, update, context):
        user_history = articlesuserread.readerarticles(update.message.chat_id)
        with open(r"profiler/data/articles.json") as x:
            articles = json.load(x)
        p = ps.Profiler().run(user_history, articles)
        importproposedarticles.import_proposed_articles(p)
        self.notify(update, context)

    def unknown(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Nie znam tego polecenia. :-(",
                                 reply_to_message_id=update.message.message_id)


db = BotDatabase()
bot = ExtravaganzaBot(db)

bot.send_direct_message(ExtravaganzaBot.admins[0], "ExtravaganzaBot was just *stopped*.", disable_notification=True)