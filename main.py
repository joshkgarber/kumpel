import os
import re


def main():
    os.system("clear");
    print("Hello from Kumpel!\n")
    level = get_german_level()
    os.system("clear")
    topic = get_user_topic()


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
    return get_user_input(message, pattern, invalid_message)


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
