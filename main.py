import os
import sys
import time
import re
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from google.genai import types
from yaspin import yaspin


# Gemini API retry config
MAX_RETRIES = 5
INITIAL_DELAY_SECONDS = 2


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


def main():
    load_dotenv()
    api_key = os.environ.get("KUMPEL_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Add KUMPEL_GEMINI_API_KEY to kumpel/.env e.g. KUMPEL_GEMINI_API_KEY=your_api_key")
    try:
        os.system("clear");
        print("Hello from Kumpel!\n")
        mode = get_mode()
        os.system("clear")
        level = get_german_level()
        os.system("clear")
        topic = get_user_topic()
        os.system("clear")
        style = get_particular_style()
        os.system("clear")
        model = get_model_choice()
        os.system("clear")
        spec = dict(mode=mode, level=level, topic=topic, style=style, model=model, api_key=api_key)
        session = conduct_session(spec)
        print(f"I hope you enjoyed the story! Goodbye!")
    except KeyboardInterrupt:
        os.system("clear")
        print("Goodbye!")
        sys.exit(0)


def get_mode():
    message = """What do you want to do?

1. Learn
2. Practice
3. Test

Respond with the number for your selection."""
    pattern = r"^[1,2,3]$"
    invalid_message = "Answer must be a number from 1 to 3."
    level = get_user_input(message, pattern, invalid_message)
    match level:
        case "1":
            return "learn"
        case "2":
            return "practice"
        case "3":
            return "test"
        case _:
            raise Exception("Unsupported input value for mode")


def get_german_level():
    message = """What is your level of German?\n
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
    match level:
        case "1":
            return "below A1"
        case "2":
            return "A1"
        case "3":
            return "A2"
        case "4":
            return "B1"
        case "5":
            return "B2"
        case "6":
            return "C1"
        case "7":
            return "C2"
        case _:
            raise Exception("Unsupported input value for German level")


def get_user_topic():
    message = """Are there any particular topics or themes you would like to focus on?\n
1. Yes -> I'll decide.
2. No -> the LLM can decide."""
    pattern = r"^[1, 2]$"
    invalid_message = "Respond with 1 for yes or 2 for no."
    user_input = get_user_input(message, pattern, invalid_message)
    if user_input == "2":
        return None
    message = """
Which topics and/or themes would you like to cover in the session?

Respond in one line (140 characters max)."""
    pattern = r"^.{1,140}$"
    invalid_message = "Your answer must be in one line and 1 to 140 characters long."
    user_input = get_user_input(message, pattern, invalid_message)
    return user_input


def get_particular_style():
    message = """Is there any particular style or genre you would like the text be in?\n
For example:
- Casual/everyday street talk
- Formal language in a professional setting
- Sci-Fi, futuristic, and outer-space
- Medieval fairytales and poetry
- Ancient mythology and biblical\n
1. Yes -> I'll decide.
2. No -> the LLM can decide."""
    pattern = r"^[1,2]$"
    invalid_message = "Respond with 1 for yes or 2 for no."
    user_input = get_user_input(message, pattern, invalid_message)
    if user_input == "2":
        return None
    message = """
Which style or genre would you like to request?

Respond in one line (140 characters max)."""
    pattern = r"^.{1,140}$"
    invalid_message = "Your answer must be in one line and 1 to 140 characters long."
    user_input = get_user_input(message, pattern, invalid_message)
    return user_input


def get_model_choice():
    message = """Which model would you like to use?\n
1. Gemini 2.5 Flash (Recommended)
2. Gemini 2.5 Flash-Lite
3. Gemini 2.5 Pro"""
    pattern = r"^[1,2,3]$"
    invalid_message = "Respond with 1, 2, or 3."
    model_choice = get_user_input(message, pattern, invalid_message)
    match model_choice:
        case "1":
            return "gemini-2.5-flash"
        case "2":
            return "gemini-2.5-flash-lite"
        case "3":
            return "gemini-2.5-pro"
        case _:
            raise Exception("Unsupported input value for model choice")


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


def conduct_session(spec):
    story = get_story(spec)
    german_sentences = [sentence.german for sentence in story.sentences]
    german_story_string = " ".join(german_sentences)
    for sentence in story.sentences:
        if spec["mode"] == "learn":
            passed = False
            print(f"German:  {sentence.german}")
            print()
            input("Hit enter for translation. ")
            os.system("clear")
            print(f"German:  {sentence.german}")
            print(f"\nEnglish: {sentence.english}")
            while not passed:
                valid = False
                while not valid:
                    answer = input("\nRepeat:  ")
                    valid = answer_validation(answer, sentence.english)
                feedback = check_answer(sentence.german, answer, german_story_string, spec)
                if feedback.correct:
                    print("Correct!")
                    passed = True
                else:
                    print("Incorrect.\n")
                    print(feedback.feedback)
                if passed:
                    input("\nHit Enter to proceed. ")
                else:
                    print("\nTry again!")
            os.system("clear")
        passed = False
        print(f"German:  {sentence.german}")
        while not passed:
            valid = False
            while not valid:
                answer = input("\nEnglish: ")
                valid = answer_validation(answer, sentence.english)
            feedback = check_answer(sentence.german, answer, german_story_string, spec)
            if feedback.correct:
                print("Correct!\n")
                passed = True
            else:
                print("Incorrect.\n")
                if spec["mode"] == "practice":
                    print(feedback.feedback, "\n")
            if passed:
                input("Hit Enter to proceed. ")
            else:
                print("Try again.")
        os.system("clear")


def get_story(spec):
    with yaspin(text="Generating story") as sp:
        system_instruction = "You are a German storyteller. Your purpose is to provide a story which will help the user learn German."
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Story,
        )
        contents = get_story_prompt_contents(spec)
        validated = False
        retry_count = 0
        delay = INITIAL_DELAY_SECONDS
        while not validated and retry_count < MAX_RETRIES:
            gemini_response = get_gemini_response(spec, config, contents)
            story: Story = gemini_response.parsed
            if isinstance(story, Story):
                validated = True
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

    os.system("clear")
    return story


def get_story_prompt_contents(spec):
    contents = f"My current German level is: {spec['level']}. Provide me with a story to help me learn German."
    if spec["topic"]:
        contents += f"\nI want the story to be about this topic/theme: {spec['topic']}"
    if spec["style"]:
        contents += f"\nI want the story to be written in this style/genre: {spec['style']}"
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


def check_answer(german, english, story, spec):
    print()
    with yaspin(text="Checking answer") as sp:
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
        contents = f"Here is the sentence I am attempting to translate: {german}.\nHere is my translation: {english}\nPlease check my translation and give me your feedback."
        validated = False
        retry_count = 0
        delay = INITIAL_DELAY_SECONDS
        while not validated and retry_count < MAX_RETRIES:
            gemini_response = get_gemini_response(spec, config, contents)
            feedback: Feedback = gemini_response.parsed
            if isinstance(feedback, Feedback):
                validated = True
                sp.text = ""
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


def get_gemini_response(spec, config, contents):
    client = genai.Client(api_key=spec["api_key"])
    gemini_success = False
    retry_count = 0
    delay = INITIAL_DELAY_SECONDS

    while not gemini_success and retry_count < MAX_RETRIES:
        try:
            response = client.models.generate_content(
                model=spec["model"],
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
