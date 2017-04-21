# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try:
    input = raw_input
except:
    pass

import settings as st


# External Dependencies
import random
from mingus.midi import fluidsynth  # requires FluidSynth is installed
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note, Bar


def parse2note(x):
    if isinstance(x, int):
        return Note().from_int(x)  # if integer
    elif isinstance(x, str):
        try:
            return Note().from_int(str(x))  # if integer string
        except:
            return Note(x)  # if string note name
    elif isinstance(x, Note):
        return x  # if already Note
    else:
        raise Exception("Could not parse input {} of type {} to string."
                        "".format(x, type(x)))


def random_progression(number_strums, numerals, strums_per_chord=[1]):

    prog_strums = []
    prog = []
    numeral = ""
    while len(prog_strums) < number_strums:
        prev_numeral = numeral
        numeral = random.choice(numerals)
        if prev_numeral == numeral:  # check not same as previous chord
            continue

        strums = random.choice(strums_per_chord)

        # not very elegant/musical (i.e. a "jazzy" solution)
        if len(prog) + strums > number_strums:
            strums = number_strums - len(prog)

        prog_strums += [numeral] * strums
        prog += [numeral]
    return prog, prog_strums


def random_chord():
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
    return numeral, chord, Ioctave


# def get_numerals(key, sevenths=False):
#     if sevenths:
#         numerals = [I, II, III, IV, V, VI, VII] = \
#             ["I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"]
#         tones = [1, 3, 5, 7]
#     else:
#         numerals = [I, II, III, IV, V, VI, VII] = \
#             ["I", "II", "III", "IV", "V", "VI", "VII"]
#         tones = [1, 3, 5]
#     return numerals, tones


class Diatonic(object):
    def __init__(self, key, Ioctave=None, minor=False):
        self.minor = minor
        if not Ioctave:
            Ioctave = Note(key).octave
        self.Ioctave = Ioctave

        if minor or key[0] == key[0].lower():  # natural minor
            self.rel_semitones = [0, 2, 3, 5, 7, 8, 10]
            self.keyname = key[0].upper + key[1:] + " Major"
        elif key[0] == key[0].upper():  # major
            self.rel_semitones = [0, 2, 4, 5, 7, 9, 11]
            self.keyname = key + " Minor"
        self.tonic = Note(name=key[0].upper() + key[1:], octave=Ioctave)

        self.abs_semitones = [int(self.tonic) + x for x in self.rel_semitones]
        self.notes = [Note().from_int(x) for x in self.abs_semitones]
        self.numdict = dict([(k + 1, n) for k, n in enumerate(self.notes)])
        self.base_semitones = [x % 12 for x in self.abs_semitones]

    def semitone_distance2note(self, dist):
        """Returns the note that is the input semitone distance from the tonic.
        """
        return Note().from_int(int(self.tonic) + dist)

    def degree2note(self, degree):
        """Converts diatonic degree to `Note` object."""
        assert degree > 0
        rel_semi = \
            self.rel_semitones[(degree - 1) % 8] + 12 * ((degree - 1) // 8)
        return self.semitone_distance2note(rel_semi)

    def note2degree(self, note):
        """Converts a `Note` object to a diatonic degree."""
        base_semitones = [x % 12 for x in self.abs_semitones]
        note_base_semi = int(note) % 12
        try:
            return base_semitones.index(note_base_semi) + 1
        except:
            raise ValueError("{} is not a note in {}.".format(note.name, 
                             self.keyname))

    def degrees2semidist(self, num1, num2):
        """Find the distance in semitones between two diatonic degrees."""
        assert 1 <= num1 <= 7
        assert 1 <= num2 <= 7
        return abs(int(self.degree2note(num2)) - int(self.degree2note(num1)))

    def interval(self, number, root=None, ascending=True):
        assert number > 0
        if root is None:
            root = self.notes[0]

        root_num = self.note2degree(root)
        if ascending:
            second_note_num = (self.note2degree(root) + (number - 1)) % 7
            if second_note_num == 0:
                second_note_num = 7
            semi_dist = self.degrees2semidist(root_num, second_note_num)
            if second_note_num < root_num:
                semi_dist = 12 - semi_dist
            second_note_int = int(root) + semi_dist + 12*((number-1)//7)
        else:
            second_note_num = (self.note2degree(root) - (number - 1)) % 7
            if second_note_num == 0:
                second_note_num = 7
            semi_dist = self.degrees2semidist(root_num, second_note_num)
            if second_note_num > root_num:
                semi_dist = 12 - semi_dist
            second_note_int = int(root) - semi_dist - 12*((number-1)//7)

        return NoteContainer(sorted([root, Note().from_int(second_note_int)]))

    def random_note(self):
        return random.choice(self.notes)

    def bounded_random_notes(self, low, high, max_int, n, previous_note=None):
        note_int_range = [x for x in range(int(parse2note(low)), int(parse2note(high)) + 1)
                            if (x % 12) in self.base_semitones]


        if previous_note is None:
            previous_note = Note().from_int(random.choice(note_int_range))

        notes = []
        for k in range(n):
            potential_notes = [x for x in note_int_range
                               if abs(x - int(previous_note)) <= max_int]
            notes.append(Note().from_int(random.choice(potential_notes)))
            previous_note = notes[-1]
        return notes

    def root2chord(root_pitch, type='triad'):
        """Given a `Note` object, returns a `NoteContainer`.  `type` determines
        the chord type and voicing."""
        if type == 'triad':
            tones = [1, 3, 5]
        elif type == 'sevenths':
            tones = [1, 3, 5, 7]
        elif type == 'triadbar':
            tones == [1, 5, 8, 10, 12, 15]
        else:
            tones = type
        degrees = [self.note2degree(root_pitch) + (d-1) for d in tones]
        return NoteContainer(map(self.degree2note, degrees))

    
def isvalidnote(answer):
    try:  # return True if response is numerical 1-7
        return int(answer) in range(1, 8)
    except:
        pass
    try:  # return True if response is a valid note name
        return notes.is_valid_note(answer[0].upper() + answer[1:])
    except:
        pass
    return False


def random_key(minor=False, output_on=True):
    """Returns a random major or minor key.
    Minor in lower case, major in upper case."""
    keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab']
    key = random.choice(keys)
    if minor and random.choice([0, 1]):  # minor or major
        key = key.lower()

    # Inform user of new key
    if output_on:
        print("\n" + "-" * 10 + "\n")
        if key == key.lower():
            print("KEY:", key.upper(), "min")
        else:
            print("KEY:", key, "Maj")
        print("-" * 10)

    return key


def easy_bar(notes, durations=None):
    _default_note_duration = 4
    if not durations and notes is not None:
        durations = [_default_note_duration]*len(notes)

    # setup Bar object
    bar = Bar()
    if (isinstance(notes, NoteContainer) or 
            isinstance(notes, Note) or notes is None):
        bar.place_notes(notes, _default_note_duration)
    elif notes is None:
        bar.place_notes(notes, _default_note_duration)
    else:
        for x, d in zip(notes, durations):
            bar.place_notes(x, d)
    return bar


def easy_play(notes, durations=None, bpm=None):
    """`notes` should be a list of notes and/or note_containers.
    durations will all default to 4 (quarter notes).
    bpm will default current BPM setting, `st.BPM`."""
    # if bpm is None:
    #     bpm = st.BPM
    assert bpm is not None
    fluidsynth.play_Bar(easy_bar(notes, durations), bpm=bpm)


def play_wait(duration=None, notes=None, bpm=None):
    if notes and bpm is not None:
        easy_play([None]*len(notes), bpm=bpm)
    elif notes and bpm is None:
        raise NotImplementedError
    if bpm is None:
        assert duration is not None
        easy_play([None], durations=[duration])
    elif duration is None:
        assert bpm is not None
        easy_play([None], bpm=bpm)


def play_progression(prog, key, octaves=None, Ioctave=4, Iup = "I", bpm=None):
    """ Converts a progression to chords and plays them using fluidsynth.
    Iup will be played an octave higher than other numerals by default.
    Set Ioctave to fall for no octave correction from mingus default behavior.
    """
    if octaves:
        assert len(prog) == len(octaves)

    if not octaves:
        I_chd = NoteContainer(progressions.to_chords([st.I], key)[0])
        I_chd[0].octave = Ioctave
        I_val = int(I_chd[0])

    chords = []
    for i, numeral in enumerate(prog):

        # find chords from numerals and key
        if numeral == "Iup":
            chord = NoteContainer(progressions.to_chords([Iup], key)[0])
        else:
            chord = NoteContainer(progressions.to_chords([numeral], key)[0])

        # Set octaves
        if octaves:
            d = octaves[i] - chord[0].octave
            for x in chord:
                x.octave += d
        elif Ioctave:  # make sure notes are all at least pitch of that 'I' root
            while int(chord[0]) > I_val:
                for x in chord:
                    x.octave_down()
            while int(chord[0]) < I_val:
                for x in chord:
                    x.octave_up()
        if numeral == "Iup":
            for x in chord:
                x.octave_up()

        chords.append(chord)

    easy_play(chords, bpm=bpm)


def resolve_with_chords(num2res, key, Ioctave, numerals, bpm=None):
    """"Note: only relevant for major scale triads."""
    [I, II, III, IV, V, VI, VII] = numerals

    resdict = {
        I : [I],
        II : [II, I],
        III : [III, II, I],
        IV : [IV, III, II, I],
        V : [V, VI, VII, "Iup"],
        VI : [VI, VII, "Iup"],
        VII : [VII, "Iup"],
    }

    res = resdict[num2res]
    play_progression(res, key, Ioctave=Ioctave, Iup=I, bpm=bpm)
    return res


def chordname(chord, numeral=None):
    s = ""
    if numeral:
        s = numeral + " - "
    s += "  ::  ".join(ch.determine([x.name for x in chord], True))
    s += " -- " + " ".join([x.name for x in chord])
    return s


