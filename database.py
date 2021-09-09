import sqlite3
from flask import g

DATABASE = 'C:\\Users\\Administrator\\PycharmProjects\\IoS\\db.sql'


def select_db(query, args=(), one=False):
    con = sqlite3.connect(DATABASE, check_same_thread=False)
    cur = con.execute(query, args)
    rv = cur.fetchall()
    con.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    try:
        con = sqlite3.connect(DATABASE, check_same_thread=False)
        cur = con.cursor()
        cur.execute(query, args)
        con.commit()
        con.close()
        return True
    except sqlite3.Error:
        return False

