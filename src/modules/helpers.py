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


def message_user(msg):
    window_width = 100
    print(textwrap.fill(msg, width=window_width))


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
    print("Goodbye!")
    time.sleep(1)
    os.system("clear")
    exit(0)


def choose_cardset(spec):

    message_user('Please choose a cardset from the list.')
    print()
    
    # Show the options to the user
    for row in spec['cardsets']:
        print(f'{row["number"]}) {row["name"]}')
    print() 

    # Ask the user for their choice of cardset
    cardset_id = ""
    message_user('Reply with the cardset number.')
    print()
    while not cardset_id: 
        cardset_number = input()
        for row in spec['cardsets']:
            if row['number'] == cardset_number:
                cardset_id = row['id']
                cardset_name = row['name']
        if not cardset_id:
            message_user('Please enter a valid cardset number.')
    print()

    # Confirm the choice of cardset with the user
    os.system('clear')
    message_user(f'You chose the cardset "{cardset_name}".')
    print()
    message_user('Reply with "ok" to proceed or "back" to go back. Reply with "exit" to exit the program.')
    print()
    response = ''
    while not response:
        response = input()
        if response == 'exit':
            exit_program()
        elif response == 'back':
            os.system('clear')
            choose_cardset(spec)
        elif response != 'ok':
            response = ''
        else:
            spec['cardset_id'] = cardset_id
            os.system('clear')
    return


def record_audio(recording, is_recording, samplerate, channels, dtype):
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while is_recording[0]:
            audio_chunk, _ = stream.read(1024)
            recording.append(audio_chunk)
    

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

    print('Transcription completed:', transcription.text)
    print()
    return transcription.text


def ai_checker(answer, front, back):
    instructions = f'Your role is to provide feedback to the user as part of a learning system which utilizes flashcards. The user has been shown the front of the card, and will attempt to provide the back. The front of the card is "{front}". The true back of the card is "{back}". Be extremely strict with the assessment of the user\'s answer. The user MUST cover EVERY facet of the back content in their answer. They may use different words, have spelling mistakes, and use different grammatical constructs, but the content of their answer must cover the meaning of card back in to the utmost extent. Output only one word: either "correct" or "incorrect".' 
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

