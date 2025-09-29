import os
import sys
import time
import re
import copy
import json
import random
from db import DB, init_db, load_stories, load_story, save_story
from ansitext import Style, Color, stylize
from texttable import Texttable
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from google.genai import types
from yaspin import yaspin


# Gemini API key global
api_key = None


# Gemini API retry config
MAX_RETRIES = 5
INITIAL_DELAY_SECONDS = 15


# Gemini response schema
class StorySentence(BaseModel):
    german: str
    english: str


# Gemini response schema
class Story(BaseModel):
    story_name: str
    sentences: list[StorySentence]


# Gemini response schema
class Feedback(BaseModel):
    correct: bool
    feedback: str


# Logo
logo = """
 _  __                          _
| |/ /   _ _ __ ___  _ __   ___| |
| ' / | | | '_ ` _ \| '_ \ / _ \ |
| . \ |_| | | | | | | |_) |  __/ |
|_|\_\__,_|_| |_| |_| .__/ \___|_|
                    |_|
"""


# Header display
arrow = stylize(Color.YELLOW, "  ", Style.BOLD)
header = stylize(Color.YELLOW, " ", Style.BOLD)
story_length = 0
story_progress = []


def main():
    global api_key
    global story_length
    load_dotenv()
    api_key = os.environ.get("KUMPEL_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Add KUMPEL_GEMINI_API_KEY to kumpel/.env e.g. KUMPEL_GEMINI_API_KEY=your_api_key")
    try:
        update_header(stylize(Color.CYAN, "Start"))
        new_screen()
        print(stylize(Color.BLUE, logo, Style.BOLD))
        story = get_story()
        story_length = len(story["content"].sentences)
        update_header(arrow + stylize(Color.CYAN, "Story: ") + story['content'].story_name)
        mode = get_mode()
        new_screen()
        conduct_session(story, mode)
        new_screen()
        save(story)
        print(stylize(Color.MAGENTA, "I hope you enjoyed the story! Goodbye!\n"))
    except KeyboardInterrupt:
        os.system("clear")
        print("Goodbye!")
        sys.exit(0)


def new_screen():
    global header
    global story_length
    global story_progress
    os.system("clear")
    print(header, "\n")
    if len(story_progress) > 0:
        print(stylize(Color.YELLOW, "Progress", Style.UNDERLINE) + stylize(Color.YELLOW, f" ({len(story_progress)}/{story_length})"))
        for sentence in story_progress:
            print(sentence)
        print()


def update_header(update):
    global header
    header += update


def get_story():
    if not os.path.exists(DB):
        init_db()

    stories = load_stories()
    if not stories:
        print(stylize(Color.MAGENTA, "You have no saved stories. Let's generate a story.\n"))
        input("Hit Enter to proceed.")
    else:
        message = f"""{stylize(Color.MAGENTA, "What do you want to do?")}

1. Use a saved story.
2. Generate a new story.

Respond with the number for your selection."""
        pattern = r"^[1,2]$"
        invalid_message = "Answer must be a number: 1 or 2"
        source = get_user_input(message, pattern, invalid_message)
        if source == "1":
            return get_saved_story(stories)

    update_header(arrow + stylize(Color.CYAN, "Generate story"))
    new_screen()
    level = get_german_level()
    new_screen()
    topic = get_user_topic()
    new_screen()
    style = get_particular_style()
    new_screen()
    model = get_model_choice()
    new_screen()
    content = generate_story(level, topic, style, model)
    story = dict(id=None, level=level, topic=topic, style=style, model=model, content=content)
    return story


def print_saved_stories(stories):
    saved_stories = copy.deepcopy(stories)
    # id, name, level, topic, style, model
    table = Texttable()
    table.set_cols_align(["c", "l", "c", "l", "l", "c"])
    table.set_cols_valign(["t", "t", "t", "t", "t", "t"])
    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.HLINES)
    table.set_cols_dtype(["t", "t", "t", "t", "t", "t"])
    for story in saved_stories:
        if story["level"] == "complete beginner":
            story["level"] = "Beginner"
        story["model"] = model_code_to_text(story["model"])
    headers = list(saved_stories[0].keys())
    headers = ["ID"] + [header.capitalize() for header in headers[1:]]
    data = [headers] + [list(story.values()) for story in saved_stories]
    table.add_rows(data)
    print(stylize(Color.BLUE, "Saved Stories", Style.BOLD))
    print("\033[34m")
    print(table.draw(), "\n")
    print("\033[0m", end="")


def get_saved_story(stories):
    update_header(arrow + stylize(Color.CYAN, "Load story"))
    new_screen()
    print_saved_stories(stories)
    story_ids = [str(story["id"]) for story in stories]
    message = f"""{stylize(Color.MAGENTA, "Which story would you like to use?")}

Respond with the story ID."""
    id_string = "|".join(story_ids)
    pattern = rf"^({id_string})$"
    invalid_message = "Answer must be one of the story IDs."
    story_id = get_user_input(message, pattern, invalid_message)
    story = next((story for story in stories if str(story["id"]) == story_id), None)
    if story:
        new_screen()
        print(f"{stylize(Color.GREEN, '✔ Loaded story:')} {story['name']}\n")
        level = story["level"]
        topic = "Custom" if story["topic"] else "None"
        style = "Custom" if story["style"] else "None"
        model = model_code_to_text(story["model"])
        story_jsonstring = load_story(story["id"])["jsonstring"]
        story["content"] = parse_story_json(story["name"], story_jsonstring)
        update_header(
            arrow +
            stylize(Color.CYAN, "Level: ") + level +
            arrow +
            stylize(Color.CYAN, "Topic: ") + topic +
            arrow +
            stylize(Color.CYAN, "Style: ") + style +
            arrow +
            stylize(Color.CYAN, "Model: ") + model
        )
        return story
    raise Exception("An error occurred getting saved story.")


def parse_story_json(name, jsonstring):
    sentences = json.loads(jsonstring)
    content = Story(story_name=name, sentences=[])
    for sentence in sentences:
        story_sentence = StorySentence(
            english=sentence["english"],
            german=sentence["german"]
        )
        content.sentences.append(story_sentence)
    return content


def model_code_to_text(model_code):
    match model_code:
        case "gemini-2.5-pro":
            return "Pro"
        case "gemini-2.5-flash":
            return "Flash"
        case "gemini-2.5-flash-lite":
            return "Flash-Lite"
        case _:
            raise Exception("Unsupported model code.")


def get_mode():
    message = f"""{stylize(Color.MAGENTA, "What do you want to do?")}

{stylize(Color.MAGENTA, "1. Learn", Style.BOLD)} (See English once and get feedback for incorrect answers)

{stylize(Color.MAGENTA, "2. Practice", Style.BOLD)} (No English given. Get feedback for incorrect answers)

{stylize(Color.MAGENTA, "3. Test", Style.BOLD)} (No English and no feedback)

Respond with the number for your selection."""
    pattern = r"^[1,2,3]$"
    invalid_message = "Answer must be a number from 1 to 3."
    level = get_user_input(message, pattern, invalid_message)
    match level:
        case "1":
            update_header(arrow + stylize(Color.CYAN, "Mode: ") + "Learn")
            return "learn"
        case "2":
            update_header(arrow + stylize(Color.CYAN, "Mode: ") + "Practice")
            return "practice"
        case "3":
            update_header(arrow + stylize(Color.CYAN, "Mode: ") + "Test")
            return "test"
        case _:
            raise Exception("Unsupported input value for mode")


def get_german_level():
    message = f"""{stylize(Color.MAGENTA, "Choose a level of German.")}\n
1. Beginner
2. A1
3. A2
4. B1
5. B2
6. C1
7. C2\n
Respond with the number for your selection."""
    pattern = r"^[1,2,3,4,5,6,7]$"
    invalid_message = "Answer must be a number from 1 to 7."
    level = get_user_input(message, pattern, invalid_message)
    update_header(arrow + stylize(Color.CYAN, "Level: "))
    match level:
        case "1":
            update_header("Beginner")
            return "complete beginner"
        case "2":
            update_header("A1")
            return "A1"
        case "3":
            update_header("A2")
            return "A2"
        case "4":
            update_header("B1")
            return "B1"
        case "5":
            update_header("B2")
            return "B2"
        case "6":
            update_header("C1")
            return "C1"
        case "7":
            update_header("C2")
            return "C2"
        case _:
            raise Exception("Unsupported input value for German level")


def get_user_topic():
    message = f"""{stylize(Color.MAGENTA, "Are there any particular topics or themes you would like to focus on?")}\n
{stylize(Color.GREEN, "1. Yes 󰁕")} I'll decide.
{stylize(Color.RED, "2. No 󰁕")} the LLM can decide."""
    pattern = r"^[1, 2]$"
    invalid_message = "Respond with 1 for yes or 2 for no."
    user_input = get_user_input(message, pattern, invalid_message)
    update_header(arrow + stylize(Color.CYAN, "Topic: "))
    if user_input == "2":
        update_header("None")
        return None
    message = f"""
{stylize(Color.MAGENTA, "Which topics and/or themes would you like to cover in the session?")}

Respond in one line (140 characters max)."""
    pattern = r"^.{1,140}$"
    invalid_message = "Your answer must be in one line and 1 to 140 characters long."
    user_input = get_user_input(message, pattern, invalid_message)
    update_header("Custom")
    return user_input


def get_particular_style():
    message = f"""{stylize(Color.MAGENTA, "Is there any particular style or genre you would like the text be in?")}\n
For example:
- Casual/everyday street talk
- Formal language in a professional setting
- Sci-Fi, futuristic, and outer-space
- Medieval fairytales and poetry
- Ancient mythology and biblical\n
{stylize(Color.GREEN, "1. Yes 󰁕")} I'll decide.
{stylize(Color.RED, "2. No 󰁕")} the LLM can decide."""
    pattern = r"^[1,2]$"
    invalid_message = "Respond with 1 for yes or 2 for no."
    user_input = get_user_input(message, pattern, invalid_message)
    update_header(arrow + stylize(Color.CYAN, "Style: "))
    if user_input == "2":
        update_header("None")
        return None
    message = f"""
{stylize(Color.MAGENTA, "Which style or genre would you like to request?")}

Respond in one line (140 characters max)."""
    pattern = r"^.{1,140}$"
    invalid_message = "Your answer must be in one line and 1 to 140 characters long."
    user_input = get_user_input(message, pattern, invalid_message)
    update_header("Custom")
    return user_input


def get_model_choice():
    message = f"""{stylize(Color.MAGENTA, "Which model would you like to use?")}\n
1. Gemini 2.5 Flash (Recommended)
2. Gemini 2.5 Flash-Lite
3. Gemini 2.5 Pro"""
    pattern = r"^[1,2,3]$"
    invalid_message = "Respond with 1, 2, or 3."
    model_choice = get_user_input(message, pattern, invalid_message)
    update_header(arrow + stylize(Color.CYAN, "Model: "))
    match model_choice:
        case "1":
            update_header("Flash")
            return "gemini-2.5-flash"
        case "2":
            update_header("Flash Lite")
            return "gemini-2.5-flash-lite"
        case "3":
            update_header("Pro")
            return "gemini-2.5-pro"
        case _:
            raise Exception("Unsupported input value for model choice")


def save(story):
    if story["id"] is None:
        message = f"""Do you want to save the story?

{stylize(Color.GREEN, "1. Yes")}
{stylize(Color.RED, "2. No")}"""
        pattern = r"^[1,2]$"
        invalid_message = "Respond with 1 or 2."
        save = get_user_input(message, pattern, invalid_message)
        print()
        if save == "1":
            with yaspin(text="Saving story") as sp:
                save_story(story)
                sp.text = "Story saved"
                sp.green.ok("✔")
                print()



def get_user_input(message, pattern, invalid_message):
    valid_input = False
    print(message + "\n")
    while valid_input == False:
        user_input = input("Your answer: ")
        valid_input = validate_input(user_input, pattern, invalid_message)
    return user_input


def validate_input(user_input, pattern, invalid_message):
    match = re.fullmatch(pattern, user_input)
    if match:
        return True
    print(invalid_message)
    return False


def conduct_session(story, mode):
    global story_progress
    german_sentences = [sentence.german for sentence in story["content"].sentences]
    german_story_string = " ".join(german_sentences)
    for sentence in story["content"].sentences:
        if mode == "learn":
            passed = False
            print(stylize(Color.BLUE, "German: ", Style.BOLD), sentence.german)
            print()
            input(stylize(Color.MAGENTA, "Read the sentence.", Style.BOLD) + " Then hit Enter for the translation. ")
            new_screen()
            print(stylize(Color.BLUE, "German: ", Style.BOLD), sentence.german)
            print()
            print(stylize(Color.BLUE, "English:", Style.BOLD), sentence.english)
            while not passed:
                valid = False
                while not valid:
                    print()
                    answer = input(stylize(Color.MAGENTA, "Repeat:  ", Style.BOLD))
                    valid = answer_validation(answer, sentence.english)
                feedback = check_answer(sentence.german, sentence.english, answer, german_story_string, story["model"])
                if feedback.correct:
                    passed = True
                else:
                    print(feedback.feedback)
                if passed:
                    input("\nHit Enter to proceed. ")
                else:
                    print("\nTry again!")
            new_screen()
        passed = False
        print(stylize(Color.BLUE, "German: ", Style.BOLD), sentence.german)
        while not passed:
            valid = False
            while not valid:
                print()
                answer = input(stylize(Color.BLUE, 'English: ', Style.BOLD))
                valid = answer_validation(answer, sentence.english)
            feedback = check_answer(sentence.german, sentence.english, answer, german_story_string, story["model"])
            if feedback.correct:
                passed = True
            else:
                if mode == "practice" or mode == "learn":
                    print(feedback.feedback)
            if passed:
                story_progress.append(sentence.german)
                input("\nHit Enter to proceed. ")
            else:
                print("\nTry again.")
        new_screen()


def generate_story(level, topic, style, model):
    new_screen()
    with yaspin(text="Generating story") as sp:
        system_instruction = "You are a German storyteller. Your purpose is to provide a story which will help the user learn German."
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Story,
        )
        contents = get_story_prompt_contents(level, topic, style)
        validated = False
        retry_count = 0
        delay = INITIAL_DELAY_SECONDS
        while not validated and retry_count < MAX_RETRIES:
            gemini_response = get_gemini_response(model, config, contents)
            story: Story = gemini_response.parsed
            if isinstance(story, Story):
                validated = True
                sp.text = f"{stylize(Color.GREEN, 'Generated story:')} {story.story_name}"
                sp.green.ok("✔")
                print()
            else:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    sp.write(f"The Gemini response is invalid. Retrying in {delay} seconds... (Attempt {retry_count}/{MAX_RETRIES})")
                    time.sleep(delay)
                    delay *= 2
                else:
                    sp.write(f"The Gemini response is invalid. Maximum retries reached.")
                    sp.red.fail("✘")

    if not validated:
        print("Gemini response was invalid after multiple attempts. Exiting.")
        sys.exit(1)

    return story


def get_story_prompt_contents(level, topic, style):
    contents = f"My current German level is: {level}. Provide me with a story to help me learn German."
    if topic:
        contents += f"\nI want the story to be about this topic/theme: {topic}"
    if style:
        contents += f"\nI want the story to be written in this style/genre: {style}"
    return contents


def answer_validation(answer, english):
    # Use statistical heuristic to validate based on word count
    sd_percentage = 0.25
    num_std_devs = 2
    len_correct = len(english.split())
    std_dev = len_correct * sd_percentage
    lower_bound = max(1, len_correct - (num_std_devs * std_dev))
    upper_bound = len_correct + (num_std_devs * std_dev)
    len_answer = len(answer.split())
    if len_answer < lower_bound:
        print("\nYour answer is too short. Try again.")
        return False
    elif len_answer > upper_bound:
        print("\nYour answer is too long. Try again.")
        return False
    else:
        return True


def check_answer(german, english, answer, story, model):
    print()
    with yaspin(text="Checking answer") as sp:
        if answer == english:
            s = random.uniform(0.65, 1.35)
            time.sleep(s)
            feedback = Feedback(correct=True, feedback="")
            sp.text = stylize(Color.GREEN, "Correct!", Style.BOLD)
            sp.green.ok("✔")
            return feedback
        system_instruction = f"""
You are a German tutor. Your purpose is to check the user's translation of a sentence.
Provide friendly feedback in English (max 25 words) if the translation is incorrect.
Do not provide direct translations in the feedback.
For context: the sentence comes from this text:
{story}"""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Feedback,
        )
        contents = f"Here is the sentence I am attempting to translate: {german}.\nHere is my translation: {answer}\nPlease check my translation and give me your feedback."
        validated = False
        retry_count = 0
        delay = INITIAL_DELAY_SECONDS
        while not validated and retry_count < MAX_RETRIES:
            gemini_response = get_gemini_response(model, config, contents)
            feedback: Feedback = gemini_response.parsed
            if isinstance(feedback, Feedback):
                validated = True
                if feedback.correct:
                    sp.text = stylize(Color.GREEN, "Correct!", Style.BOLD)
                    sp.green.ok("✔")
                else:
                    sp.text = stylize(Color.RED, "Incorrect.", Style.BOLD)
                    sp.red.fail("✘")
            else:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    sp.write(f"The Gemini response is invalid. Retrying in {delay} seconds... (Attempt {retry_count}/{MAX_RETRIES})\n")
                    time.sleep(delay)
                    delay *= 2
                else:
                    sp.write(f"The Gemini response is invalid. Maximum retries reached.")
                    sp.red.fail("✘")

    if not validated:
        print("Gemini response was invalid after multiple attempts. Exiting.")
        sys.exit(1)

    return feedback


def get_gemini_response(model, config, contents):
    global api_key
    client = genai.Client(api_key=api_key)
    gemini_success = False
    retry_count = 0
    delay = INITIAL_DELAY_SECONDS

    while not gemini_success and retry_count < MAX_RETRIES:
        try:
            response = client.models.generate_content(
                model=model,
                config=config,
                contents=contents,
            )
            gemini_success = True

        except Exception as e:
            retry_count += 1
            error_code = getattr(e, 'code', None)

            if error_code in [429, 500, 503, 504]:
                if retry_count < MAX_RETRIES:
                    print(f"Gemini error (Code: {error_code}). Retrying in {delay} seconds... (Attempt {retry_count}/{MAX_RETRIES})\n")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"Gemini error (Code: {error_code}). Maximum retries reached.")
            else:
                print(f"An unrecoverable error occurred: {str(e)}")
                print("Exiting. Goodbye!")
                sys.exit(1)

    if not gemini_success:
        print("Gemini failed to respond after multiple attempts. Exiting.")
        sys.exit(1)

    return response


if __name__ == "__main__":
    main()
