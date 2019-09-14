import mysql.connector as mariadb
import json

dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')


def readerarticles(readerid):
    visited_sites = []

    sql_user_articles = """SELECT articles.guid, articles.url 
    FROM articles, links_for_readers
    WHERE articles.guid = links_for_readers.article 
        AND links_for_readers.reader = %s
        AND links_for_readers.reader > 0"""
    c = dbconn.cursor()
    c.execute(sql_user_articles, (readerid,))

    for guid, url in c:
        tags = []

        c.execute("SELECT tag, weight FROM articles_tags WHERE article = %s", (guid,))
        for tag, weight in c:
            tags.append({tag: float(weight)})

        visited_sites.append({"url": url, "tags": tags})

    return {"user_id": readerid, "visited_sites": visited_sites}


if __name__ == '__main__':
    print(json.dumps(readerarticles(297962379)))
