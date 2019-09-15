from telegram import ParseMode, ChatAction
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
import logging
import mysql.connector as mariadb
from profiler.src import profiling_scripts as ps
from bot import articlesuserread, importproposedarticles
import json
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class BotDatabase:
    dbconn = None

    def __init__(self):
        self.dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')
        self.dbconn.autocommit = True

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

        self.send_to_karol()
        ExtravaganzaBot.updater.start_polling(1.0)
        ExtravaganzaBot.updater.idle()

    def send_direct_message(self, chat_id, message, parse_mode=ParseMode.MARKDOWN, disable_notification=False):
        self.updater.bot.send_message(chat_id, message, parse_mode=parse_mode,
                                      disable_notification=disable_notification)
        logging.info("Sent message „%s” to chat %s." % (message, chat_id))

    def notify_about_new_articles(self, onet=False):
        c = self.db.dbconn.cursor(buffered=True)
        c.execute("SELECT links_for_readers.guid, links_for_readers.reader, articles.url FROM links_for_readers, articles WHERE articles.guid = links_for_readers.article AND links_for_readers.new = 1 LIMIT 5")
        # print(c)
        users_in_progress = []
        for guid, reader, url in c:
            if reader not in users_in_progress:
                cx = self.db.dbconn.cursor()
                cx.execute("SELECT first_name FROM readers WHERE id = %s", (reader,))
                for x in cx:
                    first_name = x
                self.db.dbconn.commit()
                cx.close()

                self.send_direct_message(reader, "Hi %s! Here are events from your local area, curated by our 'Axel News' - best application that lets you stay up to date!" % (first_name))
                users_in_progress.append(reader)
            if onet:
                msg = "[%s](%s)" % (url, url)
            else:
                msg = "[http://frappe.iiar.pwr.edu.pl:5000/%s](http://frappe.iiar.pwr.edu.pl:5000/%s)" % (guid, guid)

            self.updater.bot.send_chat_action(chat_id=reader, action=ChatAction.TYPING)
            time.sleep(0.5)
            self.send_direct_message(reader, msg)

            cx = self.db.dbconn.cursor()
            cx.execute("UPDATE links_for_readers SET new = 0 WHERE guid = %s", (guid,))
            self.db.dbconn.commit()
            cx.close()
        self.db.dbconn.commit()
        c.close()

    def start(self, update, context):
        if update.message.chat.type == 'private':
            user = update.message.chat.first_name
            title = update.message.chat.username
        else:
            user = update.message.chat.title
            title = user

        context.bot.send_message(chat_id=update.message.chat_id, text="Hi, %s! Soon you will receive information about the most interesting events in your local area!" % user)
        logging.info("Chat ID: %s; Chat @: %s" % (update.message.chat_id, title))
        self.db.new_reader(update.message.chat_id, update.message.chat.first_name, update.message.chat.last_name,
                           title)
        self.send_to_karol()

    def notify(self, update, context):
        if update.message.chat_id in ExtravaganzaBot.admins:
            context.bot.send_message(chat_id=update.message.chat_id, text="Notification launched.")
            self.notify_about_new_articles()
        else:
            self.unknown(update, context)

    def notify_onet(self, update, context):
        if update.message.chat_id in ExtravaganzaBot.admins:
            context.bot.send_message(chat_id=update.message.chat_id, text="Notification launched.")
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
        context.bot.send_message(chat_id=update.message.chat_id, text="I don't know this command. :-(",
                                 reply_to_message_id=update.message.message_id)

    def send_to_karol(self):
        self.updater.bot.send_message(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, text="Hi Karol! Here are events from your local area, curated by our _Axel News_ - best application that lets you stay up to date!")
        self.updater.bot.send_message(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, text="This week we think that you might be interested in topic of *Jazz*.")
        self.updater.bot.send_animation(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, animation="http://giphygifs.s3.amazonaws.com/media/JdCz7YXOZAURq/giphy.gif")
        self.updater.bot.send_message(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, text="*Narodowe Forum Muzyki* is organising the best music shows in *Wroclaw*, so you might be interested in *Jazztopad*. Check it out under this link [http://www.jazztopad.pl](http://www.jazztopad.pl).")
        self.updater.bot.send_message(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, text="Do you know the shady part of *Miles Davis* life? Read this article about the most popular Jazzman in history. [https://kultura.onet.pl/muzyka/gatunki/jazz/miles-davis-szpan-boks-i-jazz/ykf77cf](https://kultura.onet.pl/muzyka/gatunki/jazz/miles-davis-szpan-boks-i-jazz/ykf77cf)")
        self.updater.bot.send_message(parse_mode=ParseMode.MARKDOWN, chat_id=389659954, text="Want to expand your music collection? Check out this top jazz album chart. [https://kultura.onet.pl/muzyka/gatunki/jazz/5-albumow-jazzowych-dla-poczatkujacych/g7v0qw6](https://kultura.onet.pl/muzyka/gatunki/jazz/5-albumow-jazzowych-dla-poczatkujacych/g7v0qw6).")





db = BotDatabase()
bot = ExtravaganzaBot(db)

bot.send_direct_message(ExtravaganzaBot.admins[0], "ExtravaganzaBot was just *stopped*.", disable_notification=True)
