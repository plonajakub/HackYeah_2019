import mysql.connector as mariadb
from flask import Flask, redirect

dbconn = mariadb.connect(user='hackyeah', password='hackyeah', database='hackyeah')
dbconn.autocommit = True
app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello, world!"


@app.route('/<uuid:art>')
def redirect_to_art(art):
    sql_select_url = """SELECT articles.url AS url, links_for_readers.visited AS visited 
    FROM links_for_readers, articles 
    WHERE articles.guid = links_for_readers.article AND links_for_readers.guid = %s"""
    c = dbconn.cursor()
    c.execute(sql_select_url, (str(art),))
    for url, visited in c:
        c.execute("""UPDATE links_for_readers SET visited = %s WHERE guid = %s""", (visited + 1, str(art),))
        dbconn.commit()
        return redirect(url)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
