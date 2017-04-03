######################################################################

######################################################################
# This file uses code repurposed from Matt Zucker's python guitar/uke tuner.
# GitHub:  https://github.com/mzucker/python-tuner/blob/master/tuner.py
# Original Author:  Matt Zucker
# Date:    July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#          https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################
from __future__ import division, print_function
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from mingus.containers import Note
from time import time

######################################################################
# Feel free to play with these numbers. Might want to change NOTE_MIN
# and NOTE_MAX especially for guitar/bass. Probably want to keep
# FRAME_SIZE and FRAMES_PER_FFT to be powers of two.

NOTE_MIN = 40  # E2
NOTE_MAX = 96  # C7
FSAMP = 22050  # Sampling frequency in Hz
FRAME_SIZE = 2048  # How many samples per frame?
FRAMES_PER_FFT = 16  # FFT takes average across how many frames?

######################################################################
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (so
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE * FRAMES_PER_FFT
FREQ_STEP = float(FSAMP) / SAMPLES_PER_FFT

######################################################################
# For printing out notes

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()


######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

def freq_to_number(f):
    """Converts a frequency (Hz) to MIDI number.
    E.g. 27.5(A0)-->21"""
    return 69 + 12 * np.log2(f / 440.0)


def number_to_freq(n):
    """Converts a MIDI number to frequency (Hz).
    E.g. 21(A0)-->27.5"""
    return 440 * 2.0 ** ((n - 69) / 12.0)


# def note_name(n): return NOTE_NAMES[n % 12] + str(n / 12 - 1)


def note_name(n):
    # Note: mingus note-integer convention differs by 12
    return Note().from_int(n - 12)


# See docs for numpy.rfftfreq()
def note_to_fftbin(n): return number_to_freq(n) / FREQ_STEP


def listen(notes, instrument_range=(NOTE_MIN, NOTE_MAX),
           input_device_index=None, output_on=False, mingus_range=False):
    """Listens for the input sequence of notes.  Returns a score in the form of
    a sequence of booleans."""
    if mingus_range:
        note_min = int(Note(instrument_range[0])) + 12
        note_max = int(Note(instrument_range[1])) + 12
    else:
        note_min, note_max = instrument_range


    # Get min/max index within FFT of notes we care about.
    imin = max(0, int(np.floor(note_to_fftbin(note_min - 1))))
    imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(note_max + 1))))

    # Create Hanning window function
    window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, SAMPLES_PER_FFT, False)))

    notes_in_range = range(note_min, note_max + 1)
    fftfreqs = np.fft.rfftfreq(len(window), 1./FSAMP)
    note_freqs = map(number_to_freq, notes_in_range)
    # note_bins = map(note_to_fftbin, notes_in_range)
    note_names = map(note_name, notes_in_range)

    # Allocate space to run an FFT.
    buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
    num_frames = 0

    # Initialize audio
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=FSAMP,
                                    input=True,
                                    frames_per_buffer=FRAME_SIZE,
                                    input_device_index=input_device_index)

    # for plotting
    # plt.ion()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.set_xlabel(note_names)

    stream.start_stream()

    # Print initial text
    if output_on:
        print('sampling at', FSAMP, 'Hz with max resolution of',
              FREQ_STEP, 'Hz', '\n')

    class Timer:
        def __init__(self):
            start = time()

    old_mes = ''
    plot_time = time()
    response_notes = []
    while stream.is_active():

        # Shift the buffer down, place new samples at the end
        buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
        buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)
        frame = buf * window
        num_frames += 1

        # if loud enough and buffer is full, find note
        rms = np.sqrt(np.mean(frame * frame))  # used to estimate amplitude
        # print(rms)
        if rms > 10 and num_frames >= FRAMES_PER_FFT:
            # Run the FFT on the windowed buffer
            fft = np.abs(np.fft.rfft(frame))
            note_fft = np.interp(note_freqs, fftfreqs, fft)

            # # Plot results
            # if time() > plot_time + 1:
            #     try:
            #         for bar, h in zip(bars, note_fft):
            #             bar.set_height(h)
            #     except:
            #         bars = ax.bar(left=notes_in_range,
            #                       height=note_fft,
            #                       align='center')
            #     # fig.canvas.draw()
            #     plot_time = time()

            # Get frequency of maximum response in range
            freq = note_freqs[note_fft.argmax()]
            # freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

            # Get note number and nearest note
            n = freq_to_number(freq)
            n0 = int(round(n))

            # Console output once we have a full buffer
            mes = ('freq: {:4.2f} Hznote: {:>3s} {:+.2f}'
                   ''.format(freq, note_name(n0), n - n0))
            if mes != old_mes:
                if output_on:
                    print(mes)
                # print('%s\r' % mes, end='')
                old_mes = mes
                response_notes.append(note_name(n0))
            if notes is not None and len(response_notes) == len(notes):
                return response_notes
        else:
            # print('%s\r' % rms, end='')
            bla = 1

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get(
              'maxInputChannels')) > 0:
            print("Input Device id ", i, " - ",
                  p.get_device_info_by_host_api_device_index(0, i).get('name'))
    input_device = input("Select device:")
    print(listen(['A']*15, input_device, output_on=True))
