# import sqlite3
import json
import logging
import mysql.connector as mariadb

# sqldb = "data.db"
# dbconn = sqlite3.connect(sqldb)
dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')


def db_exec_query(sql):
    try:
        c = dbconn.cursor()
        c.execute(sql)
        dbconn.commit()
    except mariadb.Error as e:
        logging.error(e)


def prepare_db():
    sql_create_table_readers = """CREATE TABLE IF NOT EXISTS readers
                                (
                                    id         integer primary key,
                                    first_name varchar(255),
                                    last_name  varchar(255),
                                    username   varchar(255)
                                )"""
    sql_create_table_articles = """CREATE TABLE IF NOT EXISTS articles
                                    (
                                        guid varchar(36) primary key,
                                        url  text not null
                                    )"""
    sql_create_table_articles_tags = """CREATE TABLE IF NOT EXISTS articles_tags
                                        (
                                            article varchar(36) not null,
                                            tag varchar(255) not null,
                                            foreign key (article) references articles (guid)
                                        )"""
    sql_create_table_links_for_readers = """CREATE TABLE IF NOT EXISTS links_for_readers
                                            (
                                                guid    varchar(36) primary key,
                                                reader  integer     not null,
                                                article varchar(36) not null,
                                                visited integer     not null default 0, -- >1 -- link visited more than once. :)
                                                foreign key (reader) references readers (id),
                                                foreign key (article) references articles (guid)
                                            )"""

    if dbconn is not None:
        db_exec_query(sql_create_table_readers)
        db_exec_query(sql_create_table_articles)
        db_exec_query(sql_create_table_articles_tags)
        db_exec_query(sql_create_table_links_for_readers)
    else:
        logging.error("Brak połączenia z bazą danych.")


# rawdata = r"""{"art…""" — uzupełnij!

data = json.loads(rawdata)
for article in data['articles']:
    guid = article['guid']
    url = article['url']
    tags = article['tags']

    sql_new_article = """INSERT INTO articles VALUES (%s, %s)"""
    cur = dbconn.cursor()
    cur.execute(sql_new_article, (guid, url))
    dbconn.commit()
    print(guid)

    for tag in tags:
        cur = dbconn.cursor()
        cur.execute("""INSERT INTO articles_tags VALUES (%s, %s)""", (guid, tag))
        dbconn.commit()

