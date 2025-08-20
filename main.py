import os
import re
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from google.genai import types


class StorySentence(BaseModel):
    german: str
    english: str


class Story(BaseModel):
    story_name: str
    sentences: list[StorySentence]


def main():
    load_dotenv()
    api_key = os.environ.get("KUMPEL_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Add KUMPEL_GEMINI_API_KEY to kumpel/.env e.g. KUMPEL_GEMINI_API_KEY=your_api_key")

    os.system("clear");
    print("Hello from Kumpel!\n")
    level = get_german_level()
    os.system("clear")
    topic = get_user_topic()
    os.system("clear")
    style = get_particular_style()
    os.system("clear")
    output_medium = get_output_medium()
    os.system("clear")
    input_medium = get_input_medium()
    os.system("clear")
    model = get_model_choice()
    os.system("clear")
    spec = dict(level=level, topic=topic, style=style, output_medium=output_medium, input_medium=input_medium, model=model, api_key=api_key)
    session = conduct_session(spec)
    print(f"session: {session}")


def get_german_level():
    message = """What is your level of German?\n
1. Complete beginner
2. Before A1
3. A1
4. A2
5. B1
6. B2
7. C1
8. C2\n
Respond with the number for your selection."""
    pattern = r"^[1,2,3,4,5,6,7,8]$"
    invalid_message = "Answer must be a number from 1 to 8."
    level = get_user_input(message, pattern, invalid_message)
    match level:
        case "1":
            return "complete beginner"
        case "2":
            return "below A1"
        case "3":
            return "A1"
        case "4":
            return "A2"
        case "5":
            return "B1"
        case "6":
            return "B2"
        case "7":
            return "C1"
        case "8":
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


def get_output_medium():
    message = """Do you want to read or hear the text? Or both?\n
1. Read
2. Hear
3. Both"""
    pattern = r"^[1,2,3]$"
    invalid_message = "Respond with 1, 2, or 3."
    user_input = get_user_input(message, pattern, invalid_message)
    return user_input


def get_input_medium():
    message = """Do you want to type or speak your answers?\n
1. Type
2. Speak"""
    pattern = r"^[1,2]$"
    invalid_message = "Respond with 1 or 2."
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
    return story


def get_story_json(spec):
    system_instruction = "You are a German storyteller. Your purpose is to provide a story which will help the user learn German."
    contents = get_prompt_contents(spec)
    client = genai.Client(api_key=spec["api_key"])
    response = client.models.generate_content(
        model=spec["model"],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Story,
        ),
        contents=contents,
    )
    story: Story = response.parsed
    return story


def get_prompt_contents(spec):
    contents = f"My current German level is: {spec['level']}. Provide me with a story to help me learn German."
    if spec["topic"]:
        contents += f"\nI want the story to be about this topic/theme: {spec['topic']}"
    if spec["style"]:
        contents += f"\nI want the story to be written in this style/genre: {spec['style']}"
    return contents


if __name__ == "__main__":
    main()
