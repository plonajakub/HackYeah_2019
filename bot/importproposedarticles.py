import mysql.connector as mariadb
import json

dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')


def import_proposed_articles(articles):
    print(articles)
    userid = articles['user_id']
    format_strings = ','.join(['%s'] * len(articles['sorted_urls']))
    sql_get_guids = "SELECT guid FROM articles WHERE url IN (%s)"
    c = dbconn.cursor(buffered=True)
    c.execute(sql_get_guids % format_strings, articles['sorted_urls'])
    for guid in c:
        cx = dbconn.cursor()
        cx.execute("INSERT INTO links_for_readers (guid, reader, article)  VALUES (uuid(), %s, %s)", (userid, str(guid[0])))
        dbconn.commit()
        cx.close()

    c.close()


if __name__ == '__main__':
    text = """{"user_id": 297962379, "sorted_urls": ["https://wiadomosci.onet.pl/swiat/wymiana-jencow-miedzy-rosja-i-ukraina-zdjecia/df7wemh", "https://wiadomosci.onet.pl/swiat/rosja-i-ukraina-dokonaly-wymiany-wiezniow-msz-polski-reaguje/c5tdd3e", "https://kultura.onet.pl/muzyka/gatunki/jazz/slawek-jaskulke-sextet-komeda-recomposed-recenzja/53ty7jg", "https://wiadomosci.onet.pl/swiat/erdogan-chce-wiecej-pieniedzy-od-ue-by-zatrzymac-uchodzcow-w-turcji/jh32bnb", "https://kultura.onet.pl/muzyka/gatunki/jazz/soyka-w-krakowie-na-summer-jazz-festiwal/w5r8b8t"]}"""
    import_proposed_articles(json.loads(text))