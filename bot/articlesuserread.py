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
    c = dbconn.cursor(buffered=True)
    c.execute(sql_user_articles, (readerid,))

    for guid, url in c:
        tags = {}

        cx = dbconn.cursor()
        cx.execute("SELECT tag, weight FROM articles_tags WHERE article = %s", (guid,))
        for tag, weight in cx:
            # tags.append({tag: float(weight)})
            tags[tag] = float(weight)

        visited_sites.append({"url": url, "tags": tags})
        cx.close()

    c.close()
    return {"user_id": readerid, "visited_sites": visited_sites}


if __name__ == '__main__':
    print(json.dumps(readerarticles(297962379)))
