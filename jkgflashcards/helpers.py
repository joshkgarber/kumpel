import os
import textwrap
import time
import anthropic
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
from openai import OpenAI
import io


window_width = 100
def message_user(msg):
    print(textwrap.fill(msg, width=window_width))
    return


def choose_mode(spec): 
    message_user('Please choose a mode from the list.')
    print()
    message_user('1) Learn')
    message_user('2) Practice')
    print()
    message_user('Reply with the mode number.')
    print()
    mode_name = ''
    while not mode_name:
        mode_number = input()
        if mode_number in ['1','2']:
            if mode_number == '1':
                mode_name = 'learn'
            else:
                mode_name = 'practice'
        else:
            message_user('Please enter a valid mode number')
    set_mode(spec, mode_name)
    if mode_name == 'learn':
        get_learn_repeats(spec)
    print()
    return


def set_mode(spec, name):
    spec.mode = name 


def countdown(m, s):
    while s > 0:
        print(f"  {m} in {s} seconds.", end='\r')
        time.sleep(1)
        s-=1
    os.system("clear")
    return


def exit_program():
    print()
    countdown("The program will end", 5)
    print()
    message_user("Goodbye!")
    time.sleep(1)
    os.system("clear")
    exit(0)


def choose_cardset(spec):

    message_user('Please choose a cardset from the list.')
    print()
    
    # Show the options to the user
    for row in spec.cardsets:
        message_user(f'{row["number"]}) {row["name"]}')
    print() 

    # Ask the user for their choice of cardset
    cardset_id = ""
    message_user('Reply with the cardset number.')
    print()
    while not cardset_id: 
        cardset_number = input()
        for row in spec.cardsets:
            if row['number'] == cardset_number:
                cardset_id = row['id']
                cardset_name = row['name']
        if not cardset_id:
            message_user('Please enter a valid cardset number.')
    spec.cardset_id = cardset_id
    os.system('clear')
    print()


def show_instructions(spec):
    mode = spec.mode
    message_user('How it works:')
    print()
    if mode == 'learn':
        message_user('You will be shown the fronts and backs of each card in turn. You have to respond with the back content.')
    elif mode == 'practice':
        message_user('You will be shows the fronts of each card in turn. You have to respond with the back content.')
    print()
    message_user('If you get one wrong, you have to reattempt it until you get it right.')
    print()
    input('Hit Enter to continue.')
    return


def record_audio(recording, is_recording, samplerate, channels, dtype):
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while is_recording[0]:
            audio_chunk, _ = stream.read(1024)
            recording.append(audio_chunk)


def get_input_mode(spec):
    message_user('Would you like to type or record your answer?')
    print()
    message_user('1) Type')
    message_user('2) Record')
    print()
    message_user('Reply with the choice number.')
    print()
    mode_name = ''
    while not mode_name:
        mode_number = input()
        if mode_number in ['1','2']:
            mode_name = 'type' if mode_number == '1' else 'record'
        else:
            message_user('Please enter a valid choice number')
    spec.input_mode = mode_name
    return


def get_recorded_answer():
    '''adapted from ~/developing-audio-recording/with_ai_transcription.py'''
    samplerate = 44100
    channels = 1
    dtype = 'int16'
    recording = []
    is_recording = [True]

    record_thread = threading.Thread(target=record_audio, args=(recording, is_recording, samplerate, channels, dtype,))
    record_thread.start()

    print('Recording... Hit Enter to stop.\n')

    input()
    is_recording[0] = False
    
    record_thread.join()
    
    print('Recording stopped.\n')

    audio_data = np.concatenate(recording, axis=0)
    wav_buffer = io.BytesIO()
    wav.write(wav_buffer, samplerate, audio_data)
    wav_buffer.seek(0)
    wav_buffer.name = 'recording.wav'

    print('Transcribing answer...\n')
    client = OpenAI()
    
    transcription = client.audio.transcriptions.create(
        model='whisper-1',
        file=wav_buffer
    )

    print('Transcription completed:\n', transcription.text)
    print()
    return transcription.text


def ai_checker(answer, front, back):
    instructions = f'Your role is to provide feedback to the user as part of a learning system which utilizes flashcards. The user has been shown the front of the card, and will attempt to provide the back. The front of the card is "{front}". The true back of the card is "{back}". Be very strict with the assessment of the user\'s answer. The user MUST cover EVERY facet of the back content in their answer. They may use different words, have spelling mistakes, and use different grammatical constructs, but the content of their answer must cover the meaning of card back in to the utmost extent. Output only one word: either "correct" or "incorrect".' 
    system = [
        {
            'type': 'text',
            'text': instructions
        }
    ]
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": answer 
                }
            ]
        }
    ]
    try:
        message = anthropic.Anthropic().messages.create(
            model='claude-3-5-haiku-latest',
            system=system,
            messages=messages,
            max_tokens=1,
        )
        return dict(success=True, result=message.content[0].text)
    except Exception as e:
        return dict(success=False, error=f"Error: {str(e)}")


def exact_checker(answer, back):
    if answer == back:
        return dict(success=True, result='correct')
    return dict(success=True, result='incorrect')

def get_learn_repeats(spec):
    os.system('clear')
    repeats = ''
    while not repeats.isdigit():
        message_user('How many times would you like to work each card?')
        print()
        repeats = input('Enter a number: ')
    spec.learn_repeats = int(repeats)


def get_check_mode(spec): 
    message_user('Would you like AI or exact-matching for the checks?')
    print()
    message_user('1) AI')
    message_user('2) Exact Match')
    print()
    message_user('Reply with the mode number.')
    print()
    mode_name = ''
    while not mode_name:
        mode_number = input()
        if mode_number in ['1','2']:
            if mode_number == '1':
                mode_name = 'ai'
            else:
                mode_name = 'exact'
        else:
            message_user('Please enter a valid mode number')
    set_check_mode(spec, mode_name)
    return


def set_mode(spec, name):
    spec.mode = name 



def set_check_mode(spec, name):
    spec.check_mode = name 
