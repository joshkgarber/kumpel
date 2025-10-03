import unittest
from db import save_story
from main import Story, StorySentence 


class TestDB(unittest.TestCase):
    def test_save_story(self):
        sentences = [StorySentence(id=1, german="Hallo!", english="Hello!")]
        story_name = "Test Story"
        story_content = Story(story_name=story_name, sentences=sentences)
        story = dict(content=story_content, level=1, topic=None, style=None, model="gemini-2.5-flash-lite")
        save_story(story)

