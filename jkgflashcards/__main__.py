import csv
import os
import time
import random
from .helpers import message_user, choose_cardset, countdown, exit_program, ai_checker, get_recorded_answer, choose_mode, show_instructions, get_input_mode

spec = {
    'cards': [],
    'cardsets': [],
    'cardset_id': 0,
    'cardset': [],
    'mode': [],
    'input_mode': []
}

with open('cards.csv', mode='r', newline='', encoding='utf-8') as cards_csv:
    cards_csv_reader = csv.DictReader(cards_csv)
    spec['cards'] = [row for row in cards_csv_reader]


with open('cardsets.csv', mode='r', newline='', encoding='utf-8') as cardsets_csv:
    cardsets_csv_reader = csv.DictReader(cardsets_csv)
    spec['cardsets'] = [row for row in cardsets_csv_reader]


def main():
    os.system('clear')
    choose_mode(spec)
    choose_cardset(spec)
    get_input_mode(spec)
    os.system('clear')
    show_instructions(spec)
    os.system('clear')


    shuffle = ""
    while shuffle not in ["y","n"]:
        shuffle = input('Do you want to shuffle the cards? (y/n): ')
    os.system("clear")


    ready = ""
    while ready not in ["y","n"]:
        ready = input('Are you ready to start the session? ("y" to start, "n" to exit.): ')
    if ready == "n":
        os.system("clear")
        exit(1)
    os.system("clear")


    for card in spec['cards']:
        if card['cardset_id'] == spec['cardset_id']:
            spec['cardset'].append(card)
    if shuffle == "y":
        random.shuffle(spec['cardset'])
    
    while True: 
        results = run_session()

        if len(results['incorrects']) == 0:
            print("Well done! You got them all right!")
            print()

        print(f"Learning time: {results['duration']} seconds.")
        print()

        time.sleep(2)
        print("Take a short break and breathe deeply for the next 10 seconds.")
        time.sleep(12)
        print()
       
        if len(results['incorrects']) > 0:       
            redo_incorrects = ''
            while redo_incorrects not in ['y', 'n'] and len(results['incorrects']) > 0:
                redo_incorrects = input('Would you to redo the ones you got wrong? (y/n): ')
                if redo_incorrects == 'y':
                    spec['cardset'] = results['incorrects']
                    print()
                elif redo_incorrects == 'n':
                    results['corrects'].clear()
                    results['incorrects'].clear()
        break


def run_session():
    cardset = spec['cardset']
    tally = dict(corrects=list(), incorrects=list())
    countdown('The session will start', 5)
    start_time = time.time()
    while len(tally["corrects"]) != len(cardset):
        for card in cardset:
            front = card['front']
            back = card['back']
            if card not in tally['corrects']:
                in_game_display(tally, len(cardset))
                message_user(front)
                print()
                if spec['mode'][0] == 'learn':
                    message_user(back)
                    print()
                correct = False
                attempts = 0
                while not correct:
                    if spec['mode'][0] == 'practice' and attempts > 4:
                        message_user(f'Correct answer: {back}')
                        print()
                    input_mode = spec['input_mode'][0]
                    if input_mode == 'record':
                        input('Hit Enter to start recording your answer.')
                        answer = get_recorded_answer()
                    elif input_mode == 'type':
                        answer = ''
                        while len(answer) < 1:
                            answer = input('Your answer: ')
                    print('\nChecking answer... ', end='\a')
                    ai_response = ai_checker(answer, front, back)
                    if ai_response['success']:
                        if ai_response['result'] == 'correct':
                            print('Correct!')
                            correct = True
                            input("\nHit Enter to continue.")
                        else:
                            print('Incorrect.\n')
                            correct = False
                            attempts += 1
                    else:
                        print(ai_response['error'])
                    if not correct and ai_response['success']:
                        if card not in tally["incorrects"]:
                            tally['incorrects'].append(card)
                    else:
                        tally["corrects"].append(card)
    
    end_time = time.time()
    os.system('clear')
    duration = round(end_time - start_time)

    results = {
        'duration': duration,
        'corrects': tally['corrects'],
        'incorrects': tally['incorrects']
    }

    return results    


def in_game_display(tally, n):
    os.system('clear')
    print(f"Done     ({len(tally['corrects'])}/{n}):")
    for card in tally['corrects']:
        message_user(card['front'])
    print()
    print(f"Mistakes ({len(tally['incorrects'])}/{n}):")
    for card in tally['incorrects']:
        message_user(card['front'])
    print()
    print()

# if __name__ == '__main__':
os.system('clear')
message_user("Welcome to flashcards!")
print()
input('Hit Enter to start.')
while True:
    main()
    os.system('clear')
    restart = ''
    while restart not in ['y', 'n']:
        restart = input('Do you want to restart? (y/n): ')
        if restart == 'y':
            spec['cardset'].clear()
        elif restart == 'n':
            exit_program()
