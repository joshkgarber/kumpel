import sqlite3
import json


DB = "story.sqlite"


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = dict_factory
    return db


def init_db():
    db = get_db()
    db.executescript("""
BEGIN;
DROP TABLE IF EXISTS story;
DROP TABLE IF EXISTS sentence;
DROP TABLE IF EXISTS cache;
CREATE TABLE story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    topic TEXT,
    style TEXT,
    model TEXT
);
CREATE TABLE sentence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (story_id) REFERENCES story (id)
);
CREATE TABLE cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (sentence_id)REFERENCES sentence (id)
);
COMMIT;
    """)
    db.close()


def load_stories():
    db = get_db()
    stories = db.execute("SELECT id, name, level, topic, style, model FROM story").fetchall()
    db.close()
    return stories


def load_story(story_id):
    db = get_db()
    sentences = db.execute("SELECT content FROM sentence WHERE story_id = ?", (story_id,)).fetchall()
    db.close()
    return sentences


def save_story(story):
    story_name = story["content"].story_name
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO story (name, level, topic, style, model)"
        " VALUES (?, ?, ?, ?, ?)",
        (story_name, story["level"], story["topic"], story["style"], story["model"])
    )
    story_id = cur.lastrowid
    story_sentences = story["content"].sentences
    content = []
    for sentence in story_sentences:
        content.append([story_id, sentence.english])
        content.append([story_id, sentence.german])
    cur.executemany(
        "INSERT INTO sentence (story_id, content)"
        " VALUES (?, ?)",
        content
    )
    db.commit()
    db.close()
