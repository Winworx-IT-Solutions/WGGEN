import sqlite3

path = "wgsm.db"
schema = "schema.sql"

with open(schema, 'r') as f:
    s = f.read()
    con = sqlite3.connect(path)
    cur = con.cursor()
    
    cur.executescript(s)
    con.commit()
    cur.close()
