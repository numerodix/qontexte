import sqlite3

conn = sqlite3.connect('/tmp/example.db')
c = conn.cursor()
c.execute("""create table words (id int, word text)""")

f = open('ws.s', 'r')
for (i, w) in enumerate(f.xreadlines()):
    c.execute("""insert into words values (?, ?)""", (i, w))

conn.commit()

c.close()
