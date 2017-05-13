#! /usr/bin/env python

"""
Author: Andy Port
Website: https://github.com/mathandy/EarThoseChords
Email: AndyAPort@gmail.com

EarThoseChords is a tool to help musicians learn to 
recognized the root of chords based on it's distance 
from the tonic of the key.  The motivation for this 
code came from the success the author has had learning 
melodic dictation using Alain Benbassat's method (as 
found in the Android App "Functional Ear Trainer" by 
Serhii Korchan).  
If you enjoy this software, please consider making a 
donation to Alain Benbassat on his website www.miles.be

For help, see README file.
"""


# Just in case the prereqs become python 3 compatible some day
from __future__ import division, absolute_import, print_function
try:
    input = raw_input
except NameError:
    pass

# Standard Library Dependencies
import os
import dill as pickle
from copy import copy

# Internal Dependencies
import settings as st
from getch import getch
from musictools import random_key, Diatonic
from game_structure import SettingsContainer
from new_question import new_question_rn
from midi_listen import MidiListener
from mic_listen import MicListener

# External Dependencies
from mingus.midi import fluidsynth  # requires FluidSynth is installed
import mingus.core.notes as notes
from mingus.containers import Note


def parentdir(path_, n=1):
    for i in range(n):
        path_ = os.path.dirname(path_)
    return path_


# Check that saved game directory exists, if not, create it
_saved_game_dir = os.path.join(parentdir(__file__), 'saved_games')
if not os.path.exists(_saved_game_dir):
    os.makedirs(_saved_game_dir)


def load_listener(x):
    if x is None:
        return x
    elif x == "microphone":
        return MicListener()
    elif x == "midi":
        return MidiListener()
    else:
        raise Exception("Loading error: listener not properly specified in "
                        "save.")


def load_game(saved_game):
    with open(saved_game) as data_file:
        settings = pickle.load(data_file)
    settings.update({'listener': load_listener(settings['listener'])})
    return settings


def saveable_listener(x):
    if x is None:
        return x
    elif isinstance(x, MicListener):
        return "microphone"
    elif isinstance(x, MidiListener):
        return "midi"
    else:
        return False


def save_game(settings):
    """Saves (and returns) settings dictionary."""
    num = len(os.listdir(_saved_game_dir)) + 1
    new_save_file = os.path.join(_saved_game_dir, 'save{}.p'.format(num))

    saveable_settings = copy(settings)
    saveable_settings.update(
        {'listener': saveable_listener(settings['listener'])}
    )
    with open(new_save_file, 'w') as outfile:
        pickle.dump(saveable_settings, outfile)
    return settings


def user_input(mes='', default=None, acceptable=None, parser=str):
    user_response = input(mes)
    if user_response:
        user_response = parser(user_response)
    else:
        return default

    if acceptable is None:
        isacceptable = True
    elif callable(acceptable):
        isacceptable = acceptable(user_response)
    else:
        isacceptable = user_response in acceptable

    if not isacceptable:
        print("\nI don't understand, please try again\n.")
        return user_input(mes=mes, acceptable=acceptable)
    return user_response


def create_new_game():
    print("\nOK! Let's create a new game.")
    print("Press enter to select the default for any question.")

    def input_method_parser(x):
        if int(x) == 0:
            return None
        elif int(x) == 1:
            return MicListener()
        elif int(x) == 2:
            return MidiListener()
            input_method = "midi"
        else:
            return "try again"

    def acceptable_input_methods(x):
        if x is None:
            return True
        elif isinstance(x, MicListener):
            return True
        elif isinstance(x, MidiListener):
            return True
        else:
            return False


    listener = user_input("Input method?\n"
                          "0: No evaluation (default)\n"
                          "1: Microphone\n"
                          "2: Midi\n",
                            'note', acceptable_input_methods,
                                    input_method_parser)

    chord_types = ['note', 'triad', 'seventh', 'triadbar']
    def chord_type_parser(x):
        return chord_types[int(x)]
    chord_type = user_input("Notes, triads, or chords?\n"
                            "0: Notes (default)\n"
                            "1: triads\n"
                            "2: sevenths\n",
                            'note', chord_types, chord_type_parser)

    notes_per_phrase = user_input("Specify the number of notes/chords to be "
                                  "played before you're asked to repeat what "
                                  "you heard (default 1): ",
                                  1, lambda x: x > 0, int)

    bpm = user_input("Specify the BPM (default 40).",
                     40, lambda x: x > 1, float)

    def key_parser(key):
        if key == 'R':
            return random_key(minor=False)
        elif key == 'r':
            return random_key(minor=True)
        else:
            return key

    def is_valid_note(key):
        return notes.is_valid_note(key[0].upper() + key[1:])

    key = user_input("Specify the key (defaults to R).  Use lower case for "
                     "minor and upper case for major (e.g. 'Cb' for Cb-Major "
                     "or c# for c#-minor).\n"
                     "Use R or r for a random Major or minor key respectively.",
                     random_key(), is_valid_note, key_parser)

    def is_note(x):
        try:
            Note(x)
            return True
        except:
            print('bla')
            return False

    low = user_input("Specify the lowest note to be included (default E-2).\n"
                     #"You can use R to specify the tonic, e.g. if A is the "
                     #"key, inputting 'R-4' would set the lowest note to A4."
                     "Note: In case you didn't know, the lowest note on a "
                     "guitar is typically E-2.", 'E-2', is_note, str)

    high = user_input("Specify the highest note to be included (default C-7).",
                      'C-7', is_note, str)

    max_int = user_input("Specify the maximum interval between successive "
                         "notes (in semitones).  Defaults to 12.",
                         lambda x: x > 0, int)

    if key == key.lower():
        minor = True
        key = key[0].upper() + key[1:]
    else:
        minor = False

    settings = {'chord_type': chord_type,
                'notes_per_phrase': notes_per_phrase,
                'bpm': bpm,
                'low': low,
                'high': high,
                'key': key,
                'max_int': max_int,
                'listener': listener}

    settings.update({
        'scale': Diatonic(key, minor=minor),
        'minor': minor,
        'sound_font': st.SOUNDFONT,
        'single_notes': chord_type == 'note',
    })
    return save_game(settings)


def game_menu():
    saved_games = os.listdir(_saved_game_dir)
    choices = ['New Game'] + saved_games
    mes = "Please select a game:\n"
    mes += '\n'.join(["{}: {}".format(k, g) for k, g in enumerate(choices)])
    selection = getch(mes)

    if selection == '0':
        return create_new_game()
    try:
        return load_game(os.path.join(_saved_game_dir, choices[int(selection)]))
    except ValueError:
        return game_menu()


def main():

    # Parse command-line user arguments and initializes settings
    fluidsynth.init(st.SOUNDFONT)  # start FluidSynth

    # Change instrument
    # fluidsynth.set_instrument(1, 14)

    # Select game
    settings = SettingsContainer(game_menu())

    # Play Game
    while 1:
        new_question_rn(settings)


# Play the Game!!!
if __name__ == '__main__':
    main()
