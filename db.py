import sqlite3
import json


DB = 'story.sqlite'


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


def load_stories():
    db = get_db()
    stories = db.execute("SELECT id, name, level, topic, style, model FROM story").fetchall()
    db.close()
    return stories


def load_story(story_id):
    db = get_db()
    story = db.execute("SELECT jsonstring FROM story WHERE id = ?", (story_id,)).fetchone()
    db.close()
    return story


def save_story(story):
    story_name = story["content"].story_name
    story_sentences = story["content"].sentences
    content = []
    for sentence in story_sentences:
        content.append(dict(german=sentence.german, english=sentence.english))
    jsonstring = json.dumps(content)
    db = get_db()
    db.execute(
        "INSERT INTO story (name, level, topic, style, model, jsonstring)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (story_name, story["level"], story["topic"], story["style"], story["model"], jsonstring)
    )
    db.commit()
    db.close()
