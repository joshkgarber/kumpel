import sqlite3


DB = 'story.sqlite'


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = dict_factory
    return db


def load_stories():
    db = get_db()
    stories = db.execute("SELECT id, name, level, topic, style, model FROM story").fetchall()
    db.close()
    return stories


def load_story(story_id):
    db = get_db()
    story = db.execute("SELECT jsonstring FROM story WHERE id = ?", story_id).fetchone()
    db.close()
    return story

