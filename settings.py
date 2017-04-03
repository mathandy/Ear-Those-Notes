# # For python 3 compatibility
# from __future__ import division, absolute_import, print_function
# try: input = raw_input
# except: pass
#
# # External Dependencies
# import argparse, os
# import mingus.core.notes as notes
#
#
# def get_user_args():
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument(
#         # '-', '--bpm',
#         # default=40,
#         help="Specify the BPM."
#         )
#
#     parser.add_argument(
#         # '-', '--bpm',
#         # default=40,
#         help="Specify the number of notes/chords to be played at a time."
#         )
#
#     parser.add_argument(
#         # '-', '--bpm',
#         # default=40,
#         help="Specify the lowest note to be included (e.g. C0 or A4)."
#         )
#
#     parser.add_argument(
#         # '-', '--bpm',
#         # default=40,
#         help="Specify the highest note to be included (e.g. C8 or A5)."
#         )
#
#     parser.add_argument(
#         '--max',
#         type=int,
#         default=12,
#         help=("The maximum interval (in semitones) between successive (root) "
#               "notes.")
#         )
#
#     parser.add_argument(
#         '-k', '--key',
#         default="R",
#         help=("The key (defaults to random major).  Use lower case for minor "
#               "and upper case for major (e.g. 'Cb' for Cb-Major or c# for "
#               "c#-minor).\n"
#               "Use R or r for a random Major or minor key respectively.")
#         )
#
#     parser.add_argument(
#         '-r', '--triads',
#         action='store_true',
#         default=False,
#         help='If this flag is included, triad chords will be used.'
#         )
#
#     parser.add_argument(
#         '-s', '--sevenths',
#         action='store_true',
#         default=False,
#         help='If this flag is included, sevenths chords will be used.'
#         )
#
#     parser.add_argument(
#         '-f', '--sound_font',
#         action='store_true',
#         default=os.path.join(os.path.dirname(__file__), "fluid-soundfont",
#                 "FluidR3 GM2-2.SF2"),
#         help=("You can use this flag to specify a sound font (.sf2) file. "
#               "By default ")
#         )
#
#     return parser.parse_args()
#
#
# # Setup settings for use in other modules
# user_args = get_user_args()
# SOUNDFONT = user_args.sound_font
# KEY = user_args.key.upper()
# if user_args.sevenths:
#     [I, II, III, IV, V, VI, VII] = \
#         ["I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"]
#     TONES = [1, 3, 5, 7]
# else:
#     [I, II, III, IV, V, VI, VII] = ["I", "II", "III", "IV", "V", "VI", "VII"]
#     TONES = [1, 3, 5]
#
# CADENCE = [I, IV, V, I]
# NUMERALS = [I, II, III, IV, V, VI, VII]
#
# if not notes.is_valid_note(KEY):
#     print("ATTENTION: User-input key, {}, not valid, using C Major "
#           "instead.".format(KEY))
#     KEY = "C"
#
#
# # DELAY = user_args.delay
# PROGRESSION_MODE = False
# BPM = 60 * user_args.delay
#
# # Other args that should be user-adjustable, but aren't yet
# PROG_LENGTHS = range(2, 5)  # Number of strums in a progression
# CHORD_LENGTHS = range(1, 3)  # Number of strums per chord
# RESOLVE_WHEN_INCORRECT = True
# RESOLVE_WHEN_CORRECT = True
# ARPEGGIATE_WHEN_CORRECT = True
# ARPEGGIATE_WHEN_INCORRECT = True
# INTERVALS = [2, 3, 4, 5, 6, 7, 8]
# INTERVAL_MODE = "ascending"
# HARMONIC_INTERVALS = False  # if false 'interval' mode will play melodic ints
# # OCTAVES = range(1, 8)  # if many_octaves flag invoked
# DEFAULT_IOCTAVE = 4
# INITIAL_MODE = 'interval'
# FIXED_ROOT = 0  # Fix root of interval, 0 for unfixed
# NAME_INTERVAL = False

import os
# Inelegant storage
NEWQUESTION = True
CURRENT_MODE = None
CURRENT_Q_INFO = None
SCORE = 0
COUNT = 0
ALTERNATIVE_CHORD_TONE_RESOLUTION = 2
SOUNDFONT = os.path.join(os.path.dirname(__file__),
                         "fluid-soundfont", "FluidR3 GM2-2.SF2")