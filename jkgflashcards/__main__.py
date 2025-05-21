import csv
import os
import time
import random
from .helpers import message_user, choose_cardset, countdown, exit_program, ai_checker, get_recorded_answer, choose_mode, show_instructions, get_input_mode

class Spec():
    def __init__(self):
        self.cards = list()
        self.carsets = list()
        self.cardset_id = int()
        self.cardset = list()
        self.mode = str()
        self.input_mode = str()
        self.learn_repeats = 1
        self.load_cards()
        self.load_cardsets()

    def load_cards(self):
        with open('cards.csv', mode='r', newline='', encoding='utf-8') as cards_csv:
            cards_csv_reader = csv.DictReader(cards_csv)
            self.cards = [row for row in cards_csv_reader]

    def load_cardsets(self):
        with open('cardsets.csv', mode='r', newline='', encoding='utf-8') as cardsets_csv:
            cardsets_csv_reader = csv.DictReader(cardsets_csv)
            self.cardsets = [row for row in cardsets_csv_reader]


def main():
    spec = Spec()
    os.system('clear')
    choose_mode(spec)
    choose_cardset(spec)
    get_input_mode(spec)
    os.system('clear')
    show_instructions(spec)
    os.system('clear')

    shuffle = ''
    while shuffle not in ['y','n']:
        shuffle = input('Do you want to shuffle the cards? (y/n): ')
    os.system('clear')

    input('Hit Enter to start the session!')
    os.system('clear')

    for card in spec.cards:
        if card['cardset_id'] == spec.cardset_id:
            spec.cardset.append(card)
    if shuffle == 'y':
        random.shuffle(spec.cardset)
    
    while True: 
        results = run_session(spec)

        if len(results['incorrects']) == 0:
            print('Well done! You got them all right!')
            print()

        print(f"Learning time: {results['duration']} seconds.")
        print()

        print('Take a short break and breathe deeply for the next 10 seconds.')
        time.sleep(10)
        print()
       
        if len(results['incorrects']) > 0:       
            redo_incorrects = ''
            while redo_incorrects not in ['y', 'n'] and len(results['incorrects']) > 0:
                redo_incorrects = input('Would you to redo the ones you got wrong? (y/n): ')
                if redo_incorrects == 'y':
                    spec.cardset = results['incorrects']
                    print()
                elif redo_incorrects == 'n':
                    break
        else:
            break


def run_session(spec):
    mode = spec.mode
    cardset = spec.cardset
    tally = dict(corrects=list(), incorrects=list())
    countdown('The session will start', 5)
    start_time = time.time()
    while len(tally["corrects"]) != len(cardset):
        for card in cardset:
            learn_repeats = spec.learn_repeats
            front = card['front']
            back = card['back']
            while learn_repeats > 0:
                if card not in tally['corrects']:
                    in_game_display(tally, len(cardset))
                    message_user(front)
                    print()
                    if mode == 'learn':
                        message_user(back)
                        print()
                    correct = False
                    attempts = 0
                    while not correct:
                        if mode == 'practice' and attempts > 4:
                            message_user(f'Correct answer: {back}')
                            print()
                        input_mode = spec.input_mode
                        if input_mode == 'record':
                            input('Hit Enter to start recording your answer.')
                            answer = get_recorded_answer()
                        elif input_mode == 'type':
                            answer = ''
                            while not answer or answer.isspace():
                                answer = input('Your answer: ')
                        print('\nChecking answer... ', end='\a')
                        ai_response = ai_checker(answer, front, back)
                        if ai_response['success']:
                            if ai_response['result'] == 'correct':
                                correct = True
                                print('Correct!')
                                learn_repeats -= 1
                                if mode == 'learn':
                                    if learn_repeats == 0:
                                        tally["corrects"].append(card)
                                elif mode == 'practice':
                                    tally["corrects"].append(card)
                                input("\nHit Enter to continue.")
                            else:
                                print('Incorrect.\n')
                                attempts += 1
                                if card not in tally["incorrects"]:
                                    tally['incorrects'].append(card)
                        else:
                            print(ai_response['error'])


    
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
        if restart == 'n':
            exit_program()
