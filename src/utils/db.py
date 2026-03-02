import sqlite3

DB_PATH = "heating_oil.db"

def get_conn():
    return sqlite3.connect(DB_PATH)