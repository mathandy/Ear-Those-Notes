# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try:
    input = raw_input
except:
    pass

from musictools import easy_play, play_wait, parse2note
import settings as st
from game_modes import repeat_question, new_question  # Decorators
from midi_listen import MidiListener
from mic_listen import MicListener
import time


def intro_rn():
    print("And away we go!")


@new_question
def eval_rn(user_notes, correct_notes, gst):
    """Takes in notes as list of `int` or `Note` objects."""

    user_notes = [parse2note(x) for x in user_notes]
    correct_notes = [parse2note(x) for x in correct_notes]

    if user_notes:
        answers_correct = [(int(nu) - int(nc)) % 12 == 0
                           for nu, nc in zip(user_notes, correct_notes)]
    else:
        answers_correct = [False] * len(correct_notes)

    print("Correct answer:", " ".join([x.name for x in correct_notes]))
    print("Your answer:   ", " ".join([x.name for x in user_notes]))

    if all(answers_correct):
        st.SCORE += 1
        print("Good Job!")
        print()
    else:
        print("It's ok, you'll get 'em next time.")
        print()
    # time.sleep(st.DELAY)
    # play_wait(bpm=gst.bpm)


def parse_midi_input(midi_key_presses):
    """Takes in a list of MidiKeyPress objects, returns the notes, ordered by 
    time pressed."""
    midi_key_presses.sort(key=lambda x: x.time)
    return [x.note for x in midi_key_presses if x.velocity > 0]


def new_question_rn(game_settings):
    gst = game_settings
    if st.NEWQUESTION:
        if st.COUNT:
            print("score: {} / {} = {:.2%}".format(st.SCORE, st.COUNT,
                                                    st.SCORE/st.COUNT))
        st.COUNT += 1
        # Find random melody/progression
        try:
            previous_note = st.CURRENT_Q_INFO['notes'][-1]
        except:
            previous_note = None
        notes = gst.scale.bounded_random_notes(gst.low,
                                               gst.high,
                                               gst.max_int,
                                               gst.notes_per_phrase,
                                               previous_note)

        # store question info
        st.CURRENT_Q_INFO = {'notes': notes}
    else:
        notes = st.CURRENT_Q_INFO['notes']

    # Play melody/progression
    # start_time = time.time()
    # i0 = len(HISTORY)
    if gst.single_notes:
        easy_play(notes, bpm=gst.bpm)
    else:
        easy_play([gst.scale.root2chord(n, gst.chord_type) for n in notes],
                  bpm=gst.bpm)

    # def midi_listen(notes):
    #     i0 = len(HISTORY)
    #     quarter_notes_per_second = 4*gst.bpm/60
    #     time.sleep(gst.notes_per_phrase*quarter_notes_per_second)
    #     # play_wait(notes, bpm=gst.bpm)
    #     return HISTORY[i0:]

    # Request user's answer
    if isinstance(gst.listener, MidiListener):
        user_response = \
            gst.listener.listen(num_notes=gst.notes_per_phrase)
        user_response_notes = parse_midi_input(user_response)
        eval_rn(user_response_notes, notes, gst)
        play_wait(3, bpm=gst.bpm)
    elif isinstance(gst.listener, MicListener):
        user_response_notes = gst.listener.listen(notes, (gst.low, gst.high),
                                                  mingus_range=True)
        eval_rn(user_response_notes, notes, gst)
    else:
        play_wait(3, bpm=gst.bpm)


