import os
import re


def main():
    os.system("clear");
    print("Hello from Kumpel!\n")
    level = get_german_level()
    os.system("clear")
    topic = get_user_topic()
    os.system("clear")
    style = get_particular_style()
    print(f"style: {style}")


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
    return get_user_input(message, pattern, invalid_message)


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
    pattern = r"^[1, 2]$"
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


if __name__ == "__main__":
    main()
