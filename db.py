import sqlite3


DB = 'stories.sqlite'


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = dict_factory
    return db


