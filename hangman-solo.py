# Our hangman game will be relavitely standard.
# A random word is chosen from a list of words. On the
# first round, an underscore will be displayed for each
# character in the chosen word. The player will then have a fixed number
#  of chances to guess all the letters correctly.
# With each correct guess, display the letter in its position.
# With each incorrect guess, display an appropriate message to the user.
# Hints
# One simple way to get your random word at the start of each
# game is to create a list of words, then generate a random
# number and use it as the index of the word to be used.
# You need to keep track of how many incorrect wrong_guesses
# the user has made, and ‘hang’ the user when a limit is reached!
from random import randint
import os

WORDS = ["word", "object", "radiant", "wave", "stream", "jazz", "wisdom", 
"flow", "california", "metal", "book", "hero", "democracy", "beet", "tissue", 
"shall", "imminent", "delightful", "magnificent", "awful", "switzerland", 
"unbelievable", "none", "plus", "one", 
"crocodile", "architecture", "monotheism", "philosophy", "practical"]
LIMIT = 8
ANSWERS = [f"Find the word in less than {LIMIT} guesses. Good luck!\n", 
           "Correct!\n", "Wrong guess.\n", "Wrong input. Type a single letter or 'exit'\n", 
           "You already tried that letter.\n"]
word = WORDS[randint(0, len(WORDS) - 1)].upper()
wrong_guesses = []
eval_guess = 0
outcome = ""
last_tried = ""
# build hidden word:
hidden_word = ["_" for i in range(len(word))]


# Prints the hangman progress, default value is zero. 'f-string' does not allow backslashes
def display_hangman(counter=0):
    '''Prints the hangman progress, default value is zero'''
    gallow = ( # this was an if/elif/else case before
        ' _____\n ', '|   \n', '   |    \n', '   |  \n', '   |   \n', '  |\n', '|\n'
    )
    if counter == 1:
        gallow = (
            ' _____\n ', '|   |\n', '   |    \n', '   |  \n', '   |   \n', '  |\n', '|\n'
        )
    elif counter == 2:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \n','   |   \n','  |\n','|\n'
        )
    elif counter == 3:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \\\n','   |   \n','  |\n','|\n'
        )
    elif counter == 4:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \\|\n','   |   \n','  |\n','|\n'
        )
    elif counter == 5:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \\|/\n','   |   \n','  |\n','|\n'
        )
    elif counter == 6:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \\|/\n','   |   |\n','   |\n','|\n'
        )
    elif counter == 7:
        gallow = (
            ' _____\n ','|   |\n','   |   O\n','   |  \\|/\n','   |   |\n','   |  / \n','|\n'
        )
    elif counter == 8:
        gallow = (
            ' _____\n ', '|   |\n', '   |   O\n', '   |  \\|/\n', '   |   |\n', '   |  / \\\n', '|\n'
        )

    print("{:^34}{}{:^31}{}{:^31}{}{:^30}".format(*gallow)) # arguments list unpacking


# clear the screen https://www.quora.com/Is-there-a-Clear-screen-function-in-Python
def clear_screen():
    '''Clear the screen
    Checks the whether Windows or Macos/Linux us running the program and clears the screen accordingly
    '''
    os.system('cls' if os.name == 'nt' else 'clear')


# display the messages of the game
def display_messages(wrong_guesses, hidden_word, eval_guess=0, LIMIT=8, outcome="", last_tried=""):
    clear_screen()
    print(f"\n{' HANGMAN ':*^36}")
    display_hangman(len(wrong_guesses))
    if outcome == 1:
        print(f"{'YOU WIN!':^36}\nYou rightly guessed: {word}")
        print("\nYou also tried: ", wrong_guesses)
    elif outcome == 0:
        print(f"{'GAME OVER.':^36}\n{'The word was:':^15}{word}")
        print("\nYou guessed:", hidden_word, "\nYou tried:", wrong_guesses)
    else:
        print(hidden_word, "\n")
        print(f"{ANSWERS[eval_guess]}")
        print(f"Wrong guesses: {wrong_guesses} Wrong guesses remaining: {LIMIT - len(wrong_guesses)}")
        print(f"Length: {len(hidden_word)} last letter tried: {last_tried}")


# core of the game
while True:
    if len(wrong_guesses) == LIMIT:
        display_messages(wrong_guesses, hidden_word, outcome=0)
        break
    if "_" not in hidden_word:
        display_messages(wrong_guesses, hidden_word, outcome=1)
        break
    # messages
    display_messages(wrong_guesses, hidden_word, eval_guess, LIMIT, outcome, last_tried)
    prompt = input("Pick a letter or type 'exit' to quit: ").upper()  #make input uppercase regardless
    if prompt.lower() == "exit":
        print("Bye.")
        break
    if prompt.isalpha() and len(prompt) == 1:  # check if input single letter
        if prompt in wrong_guesses or prompt in hidden_word:  # If letter already tried
            eval_guess = 4
        elif prompt in word:  # correct guess
            last_tried = prompt  # update last tried letter
            eval_guess = 1  # set the answer to 'Correct!'
            for i in range(len(word)):
                if prompt == word[i]:
                    hidden_word[i] = prompt  # replace "_" with the letter
        elif prompt not in wrong_guesses:  # Wrong guess. Add wrong letter to the wrong guesses list
            eval_guess = 2  # set the answer to 'Wrong guess!'
            wrong_guesses.append(prompt)
            last_tried = prompt
    else:
        eval_guess = 3  # wrong input
