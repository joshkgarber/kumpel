import os
import sys
import time
import re
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from google.genai import types


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
        level = get_german_level()
        os.system("clear")
        topic = get_user_topic()
        os.system("clear")
        style = get_particular_style()
        os.system("clear")
        model = get_model_choice()
        os.system("clear")
        spec = dict(level=level, topic=topic, style=style, model=model, api_key=api_key)
        session = conduct_session(spec)
        print(f"session: {session}")
    except KeyboardInterrupt:
        os.system("clear")
        print("Goodbye!")
        sys.exit(0)


def get_german_level():
    message = """What is your level of German?\n
1. Before A1
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
1. Gemini 2.5 Pro
2. Gemini 2.5 Flash
3. Gemini 2.5 Flash-Lite"""
    pattern = r"^[1,2,3]$"
    invalid_message = "Respond with 1, 2, or 3."
    model_choice = get_user_input(message, pattern, invalid_message)
    match model_choice:
        case "1":
            return "gemini-2.5-pro"
        case "2":
            return "gemini-2.5-flash"
        case "3":
            return "gemini-2.5-flash-lite"
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
    story = get_story_json(spec)
    german_sentences = [sentence.german for sentence in story.sentences]
    german_story_string = " ".join(german_sentences)
    for sentence in story.sentences:
        for i in range(2):
            passed = False
            print(sentence.german)
            print(sentence.english)
            while not passed:
                answer = input("\n")
                feedback = check_answer(sentence.german, answer, german_story_string, spec)
                if feedback.correct:
                    print("\nCorrect!")
                    passed = True
                else:
                    print("\nIncorrect.\n")
                    print(feedback.feedback)
                if passed:
                    input("\nHit Enter to proceed. ")
                else:
                    print("\nTry again!")
            os.system("clear")
        passed = False
        print(sentence.german)
        while not passed:
            answer = input()
            feedback = check_answer(sentence.german, answer, german_story_string, spec)
            if feedback.correct:
                print("\nCorrect!\n")
                print(feedback.feedback)
                passed = True
            else:
                print("\nIncorrect.\n")
                print(feedback.feedback)
            if passed:
                input("\nHit Enter to proceed. ")
            else:
                print("\nTry again:\n")
        os.system("clear")
    return "complete"


def get_story_json(spec):
    print("Generating story...\n")
    system_instruction = "You are a German storyteller. Your purpose is to provide a story which will help the user learn German."
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=Story,
    )
    contents = get_story_prompt_contents(spec)
    gemini_response = get_gemini_response(spec, config, contents)
    story: Story = gemini_response.parsed
    os.system("clear")
    return story


def get_story_prompt_contents(spec):
    contents = f"My current German level is: {spec['level']}. Provide me with a story to help me learn German."
    if spec["topic"]:
        contents += f"\nI want the story to be about this topic/theme: {spec['topic']}"
    if spec["style"]:
        contents += f"\nI want the story to be written in this style/genre: {spec['style']}"
    return contents


def check_answer(german, english, story, spec):
    system_instruction = f"""
You are a German tutor. Your purpose is to check the user's translation of a sentence and provide friendly feedback in English (max 25 words). Do not provide direct translations in the feedback.
The sentence the user will attempt to translate: {german}
Note the user has only seen the story up until that sentence. Here is the full story for context:
{story}"""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=Feedback,
    )
    contents = english
    gemini_response = get_gemini_response(spec, config, contents)
    feedback: Feedback = gemini_response.parsed
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
                    print(f"\nGemini error (Code: {error_code}). Retrying in {delay} seconds... (Attempt {retry_count}/{MAX_RETRIES})\n")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"\nGemini error (Code: {error_code}). Maximum retries reached.\n")
            else:
                print(f"An unrecoverable error occurred: {str(e)}")
                print("Exiting. Goodbye!")
                sys.exit(1)

    if not gemini_success:
        print("Failed to get a response from Gemini after multiple attempts. Exiting.")
        sys.exit(1)

    return response


if __name__ == "__main__":
    main()
