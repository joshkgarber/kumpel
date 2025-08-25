# Kumpel

An LLM-assisted German language learning utility.

This project utilizes the Google Generative Language API (Gemini API). You need your own API key and running the program may incur costs. (See Gemini API Costs below for instructions on how to run it for free (probably).)

## What is Kumpel?

Kumpel is a terminal-based program which helps you to understand written German texts. It's a guided learning experience consisting of back-and-forth conversational style content. It's not intended to be a complete solution to learning German as it focuses on one aspect of language learning - reading (comprehension).

## Why use Kumpel?

Use Kumpel if you want to learn German for the purpose of reading German texts. For example, if you don't live in Germany (or Austria or Switzerland) and you want to enjoy reading German texts, you don't need to learn how to write, speak or listen to German - only how to read it. So use Kumpel to focus solely on the reading aspect of German learning.

## Quickstart

**Requirements**

- Linux (or WSL) or MacOS
- [uv](https://docs.astral.sh/uv/)
- python>=3.10
- [sqlite3](https://sqlite.org/index.html)
- [NerdFont icons](https://www.nerdfonts.com/font-downloads)

The following Python packages will be installed automatically into a new venv:

- google-genai
- python-dotenv
- texttable
- yaspin

**Steps**

1. Create a new Gemini API Key (to track costs separately)
2. Clone the repository: `git clone https://github.com/joshkgarber/kumpel.git`
3. Create a `.env` file for the API key containing `KUMPEL_GEMINI_API_KEY="your_api_key"`
4. Run the program with `uv run main.py`
5. Continue by following the prompts in the program.

## Gemini API Costs

You can run the program without incurring costs (probably, not a guarantee) if your Gemini API key is not connected to a billing account. This is because the program includes a retry sequence for cases when your activity hits the Free Tier Rate Limit.

### Run a (probably) Free Sample

You can make sure your session with Kumpel is free (probably) by using a Gemini API key that isn't connected to a billing account. ([Instructions](https://gemini.google.com/share/ce0701b3d1fb))

The Gemini API is called only after come configuration steps in the program. The cheapest (probably free) config is this:

- Level: Beginner
- Topic: None (i.e. respond with "No".)
- Style: "Very short story - only 5 sentences long." (This is not guaranteed to work. As an indication, during development without this directive stories were around 20 sentences long.)
- Model: Gemini 2.5 Flash-Lite
- Mode: Learn (assuming you don't speak German, otherwise Test)

### API Calls and Free Tier Rate Limits

The first Gemini API call is made after you choose the model. This is the call that generates the story for the session. Subsequent requests to the Gemini API are make every time you attempt a translation. In Learn mode, there will be 3 to 5+ API calls per sentence. In Test mode 2 to 4+. It's a range because getting a translation wrong triggers an API call and sometimes Gemini doesn't accept its own translation.

If you use the config described above it is highly unlikely that you will hit the TPM limit from one Kumpel session alone. If we assume the average sentence in beginner-level German is 6 words long, the average word has 7 characters, and each word produces 2 tokens. Then a sentence is approximately 84 tokens. The TPM limit for Flash-Lite is 250,000 tokens per minute. That's 2,976.19 sentences!

The RPM limit for the Flash-Lite Free Tier is 15 requests per minute. Best case scenario: you get everything right the first time (likely since it's beginner level and the sentences are very short and simple) and you don't hit the rate limit. If for some reason you do hit the rate limit (e.g. you have a longer story and you get some translations wrong), the program will catch the API error and start a retry sequence which will retry after 15-, 30-, 60-, 120-, and 240-second waiting windows.

**All of the above assumes that your API key is not connected to a billing account. If it is, the rate limit error will not occur, the retry sequence will not be triggered, and costs will be incurred.**

### Cost Estimate with Billing

If you enjoyed the sample and want to use the program regularly, you might want to connect it to a billing account so that you don't run into free tier rate limits. A convervative (i.e. rounded up) cost estimate of a session including story generation is USD 0.10. Please note: This is a rough estimate which I am guessing based on the costs incurred while creating the program. Later I'll provide a more useful and accurate breakdown of cost estimates measured in input/output tokens.
