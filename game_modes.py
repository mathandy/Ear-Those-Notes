# For python 3 compatible
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass

from getch import getch
import game_structure as gs
from musictools import play_progression, random_progression, random_key, isvalidnote, resolve_with_chords, chordname
import settings as st

# External Dependencies
import time, random, sys
from mingus.midi import fluidsynth  # requires FluidSynth is installed
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note


# Decorators
def repeat_question(func):
   def func_wrapper(*args, **kwargs):
       st.NEWQUESTION = False
       return func(*args, **kwargs)
   return func_wrapper


def new_question(func):
   def func_wrapper(*args, **kwargs):
       st.NEWQUESTION = True
       return func(*args, **kwargs)
   return func_wrapper


# Menu Command Actions
@repeat_question
def play_cadence():
    play_progression(st.CADENCE, st.KEY, delay=st.DELAY, Iup=st.I)


@repeat_question
def set_delay():
    st.DELAY = float(input("Enter the desired delay time (in seconds): "))


@new_question
def toggle_triads7ths():
    if st.I == "I7":
        st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII = \
            "I", "II", "III", "IV", "V", "VI", "VII"
    else:
        st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII = \
            "I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"
    st.NUMERALS = st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII


@new_question
def set_key():
    mes = ("Enter the desired key, use upper-case for major "
           "and lower-case for minor (e.g. C or c).\n"
            "Enter R/r for a random major/minor key.")
    newkey = input(mes)
    keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab']
    if newkey == 'R':
        st.KEY = random.choice(keys)
    elif newkey == 'r':
        st.KEY = random.choice(keys).lower()
    elif notes.is_valid_note(newkey):
        st.KEY = newkey
    else:
        print("Input key not understood, key unchanged.")
    intro(cadence=st.CADENCE, key=st.KEY)


@repeat_question
def toggle_many_octaves():
    st.MANY_OCTAVES = not st.MANY_OCTAVES


@repeat_question
def arpeggiate():
    chord = st.CURRENT_Q_INFO["chord"]
    for x in chord:
        fluidsynth.play_Note(x)
        time.sleep(st.DELAY/2)


def change_game_mode(new_mode):
    @new_question
    def _change_mode():
        st.CURRENT_MODE = game_modes[new_mode]
    return _change_mode

@repeat_question
def play_question_again():
    return

menu_commands = [
    gs.MenuCommand("v", "hear the cadence", play_cadence),
    gs.MenuCommand("w", "change the delay between chords", set_delay),
    gs.MenuCommand("s", "toggle between hearing triads and hearing seventh chords", toggle_triads7ths),
    gs.MenuCommand("k", "change the key", set_key),
    gs.MenuCommand("o", "toggle between using one octave or many", toggle_many_octaves),
    gs.MenuCommand("m", "to arpeggiate chord (not available in progression mode)", arpeggiate),
    gs.MenuCommand("p", "switch to random progression mode (experimental)", change_game_mode('progression')),
    gs.MenuCommand("h", "switch to chord tone mode", change_game_mode('chord_tone')),
    gs.MenuCommand("q", "quit", sys.exit),
    gs.MenuCommand("", "hear the chord or progression again", play_question_again,
                 input_description="Press Enter"),
]
menu_commands = dict([(mc.command, mc) for mc in menu_commands])


# Game Mode Intro Functions
def intro():
    print("\n" + "~" * 20 + "\n")

    # List menu_commands
    print("Note: At any time enter")
    for mc in menu_commands.values():
        print(mc.input_description, "to", mc.description)
    print("\n" + "-" * 10 + "\n")

    # Display key
    if st.KEY == st.KEY.lower():
        print("KEY:", st.KEY.upper(), "min")
    else:
        print("KEY:", st.KEY, "Maj")
    print("-" * 10)

    # Play cadence
    play_progression(st.CADENCE, st.KEY, delay=st.DELAY, Iup=st.I)
    time.sleep(2*st.DELAY)
    return


# New Question Functions
@new_question
def eval_single_chord(usr_ans, correct_numeral, root_note):
    correct_ = False
    if usr_ans == str(st.NUMERALS.index(correct_numeral) + 1):
        correct_ = True
    else:
        try:
            usr_note_val = int(Note(usr_ans[0].upper() + usr_ans[1:])) % 12
            correct_note_val = int(Note(root_note)) % 12
            if usr_note_val == correct_note_val:
                correct_ = True
        except:
            pass
    return correct_


def new_question_single_chord():
    # Choose new chord+octave/Progression
    # Single chord mode
    if st.NEWQUESTION:
        # Pick random chord
        numeral = random.choice(st.NUMERALS)
        chord = NoteContainer(progressions.to_chords([numeral], st.KEY)[0])

        # Pick random octave, set chord to octave
        if st.MANY_OCTAVES:
            octave = random.choice(st.OCTAVES)
            d = octave - chord[0].octave
            for x in chord:
                x.octave = x.octave + d

            # Find Ioctave
            dist_to_tonic = (int(chord[0]) - int(Note(st.KEY))) % 12
            I_root = Note().from_int(int(chord[0]) - dist_to_tonic)
            Ioctave = I_root.octave
        else:
            Ioctave = st.DEFAULT_IOCTAVE

        # store question info
        st.CURRENT_Q_INFO = {'numeral': numeral,
                             'chord': chord,
                             'Ioctave': Ioctave}
    else:
        numeral = st.CURRENT_Q_INFO['numeral']
        chord = st.CURRENT_Q_INFO['chord']
        Ioctave = st.CURRENT_Q_INFO['Ioctave']

    # Play chord
    play_progression([numeral], st.KEY, Ioctave=Ioctave)

    # Request user's answer
    ans = getch("Enter 1-7 or root of chord: ").strip()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        if isvalidnote(ans):
            if eval_single_chord(ans, numeral, chord[0].name):
                print("Yes!", chordname(chord, numeral))
                if st.RESOLVE_WHEN_CORRECT:
                    resolve_with_chords(numeral, key=st.KEY, Ioctave=Ioctave, numerals=st.NUMERALS)
            else:
                print("No!", chordname(chord, numeral))
                if st.RESOLVE_WHEN_INCORRECT:
                    resolve_with_chords(numeral, key=st.KEY, Ioctave=Ioctave, numerals=st.NUMERALS)
        else:
            print("User input not understood.  Please try again.")
    return


@new_question
def eval_progression(ans, prog, prog_strums):
    try:
        int(ans)
        answers = [x for x in ans]
    except:
        answers = ans.split(" ")

    for i, answer in enumerate(answers):
        try:
            root = NoteContainer(progressions.to_chords([prog[i]], st.KEY)[0])[0].name
            print(eval_single_chord(answer, prog[i][i], root))
        except IndexError:
            print("too many answers")
    if len(answers) < len(prog):
        print("too few answers")

    print("Progression:", " ".join(prog_strums))
    print("Correct Answer:", " ".join([str(st.NUMERALS.index(x) + 1) for x in prog]))
    time.sleep(st.DELAY)


def new_question_progression():
    if st.NEWQUESTION:
        # Find random chord progression
        prog_length = random.choice(st.PROG_LENGTHS)
        prog, prog_strums = random_progression(prog_length, st.NUMERALS, st.CHORD_LENGTHS)

        # store question info
        st.CURRENT_Q_INFO = {'prog': prog,
                             'prog_strums': prog_strums}
    else:
        prog = st.CURRENT_Q_INFO['prog']
        prog_strums = st.CURRENT_Q_INFO['prog_strums']

    # Play chord/progression
    play_progression(prog_strums, st.KEY)

    # Request user's answer
    ans = input("Enter your answer using root note names "
                "or numbers 1-7 seperated by spaces: ").strip()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        eval_progression(ans, prog, prog_strums)

    # Request user's answer
    ans = input("Enter your answer using root note names "
                "or numbers 1-7 seperated by spaces: ").strip()
    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        eval_progression(ans, prog, prog_strums)


@new_question
def eval_chord_tone(ans, chord, tone):
    tone_idx = [n for n in chord].index(tone)
    correct_ans = st.TONES[tone_idx]
    return ans == correct_ans


def new_question_chord_tone():
    if st.NEWQUESTION:
        # Pick random chord
        numeral = random.choice(st.NUMERALS)
        chord = NoteContainer(progressions.to_chords([numeral], st.KEY)[0])

        # Pick random octave, set chord to octave
        if st.MANY_OCTAVES:
            octave = random.choice(st.OCTAVES)
            d = octave - chord[0].octave
            for x in chord:
                x.octave = x.octave + d

            # Find Ioctave
            dist_to_tonic = (int(chord[0]) - int(Note(st.KEY))) % 12
            I_root = Note().from_int(int(chord[0]) - dist_to_tonic)
            Ioctave = I_root.octave
        else:
            Ioctave = st.DEFAULT_IOCTAVE

        # Pick a random tone in the chord
        tone = random.choice(chord)

        # store question info
        st.CURRENT_Q_INFO = {'numeral': numeral,
                             'chord': chord,
                             'Ioctave': Ioctave,
                             'tone': tone}
    else:
        numeral = st.CURRENT_Q_INFO['numeral']
        chord = st.CURRENT_Q_INFO['chord']
        Ioctave = st.CURRENT_Q_INFO['Ioctave']
        tone = st.CURRENT_Q_INFO['tone']

    # Play chord, then tone
    play_progression([numeral], st.KEY, Ioctave=Ioctave)
    time.sleep(st.DELAY)
    fluidsynth.play_Note(tone)

    # Request user's answer
    ans = getch("Which tone did you hear?\n""Enter {}, or {}: ".format(
            ", ".join([str(t) for t in st.TONES[:-1]]),
            st.TONES[-1])
        ).strip()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        try:
            ans = int(ans)
        except:
            print("User input not understood.  Please try again.")
            st.NEWQUESTION = False

        if ans in st.TONES:
            if eval_chord_tone(ans, chord, tone):
                print("Yes!", chordname(chord, numeral))
                if st.ARPEGGIATE_WHEN_CORRECT:
                    arpeggiate()  # sets NEWQUESTION = False
                    st.NEWQUESTION = True
            else:
                print("No!", chordname(chord, numeral))
                if st.ARPEGGIATE_WHEN_INCORRECT:
                    arpeggiate()  # sets NEWQUESTION = False
                    st.NEWQUESTION = True
        else:
            print("User input not understood.  Please try again.")
            st.NEWQUESTION = False
    return


game_modes = {
    'single_chord': gs.GameMode(intro, new_question_single_chord),
    'progression': gs.GameMode(intro, new_question_progression),
    'chord_tone': gs.GameMode(intro, new_question_chord_tone),
    }