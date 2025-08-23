import sqlite3
from db import get_db


def main():
    db = get_db()
    db.executescript("""
BEGIN;
DROP TABLE IF EXISTS story;
CREATE TABLE story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    topic TEXT,
    style TEXT,
    model TEXT,
    jsonstring TEXT NOT NULL
);
COMMIT;
    """)
    db.close()
    print("Initialized the database.")


if __name__ == "__main__":
    main()
