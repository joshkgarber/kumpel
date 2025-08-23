# Kumpel

An LLM-assisted flashcard-based German language learning utility.

This project utilizes the Google Generative Language API (Gemini API). You need your own API key and running the program may incur costs. (See *LLM Usage Costs* below.)

## What is Kumpel?

Kumpel is a terminal-based program which helps you to understand written German texts. It's a guided learning experience consisting of back-and-forth conversational style content. It's not intended to be a complete solution to learning German as it focuses on one aspect of language learning - reading (comprehension).

## Why use Kumpel?

Use Kumpel if you want to learn German for the purpose of reading German texts. For example, if you don't live in Germany (or any other German-speaking country) and you want to enjoy reading German texts, you don't need to learn how to write, speak or listen to German - only how to read it. So use Kumpel to focus solely on the reading aspect of German learning.

## LLM Usage Costs

It costs approximately $X.XX to complete a session with Kumpel. Here's the calculation:

(calculation goes here)

## Quickstart

**Requirements**

- Linux (or WSL) or MacOS
- [uv](https://docs.astral.sh/uv/)
- python>=3.10
- [sqlite3](https://sqlite.org/index.html)

The following Python packages will be installed automatically into a new venv:

- click
- google-genai
- python-dotenv
- texttable
- yaspin

**Steps**

1. Create a new Gemini API Key (to track costs separately)
2. Clone the repository: `git clone https://github.com/joshkgarber/kumpel.git`
3. Create a `.env` file for the API key containing `KUMPEL_GEMINI_API_KEY="your_api_key"`
4. Run the program with `uv run main.py`

## Command-line Config

You can pre-configure the session using command-line arguments. This bypasses the series of questions at the beginning.
