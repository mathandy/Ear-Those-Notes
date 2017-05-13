Ear-Those-Notes
===============

EarThoseNotes is a tool to help musicians learn to recognize notes (or the root of chords) in a functional context -- i.e. based on it's distance from the tonic of the key.  The motivation for this code came from the success the author has had learning melodic dictation using Alain Benbassat's method as found in the Android App "Functional Ear Trainer" by Serhii Korchan.  
If you enjoy this software, please consider making a donation to Alain Benbassat on his website www.miles.be or purchasing the "Functional Ear Trainer" app on Android.

Note: This is designed more advanced users who want to enter answers to question using a microphone or MIDI device.  If you're a beginner, you likely want to start with the "Functional Ear Trainer" app or the predecessor to Ear-Those-Notes, the `EarThoseChords<https://github.com/mathandy/EarThoseChords>` project.

What is Does
------------
Will play a random sequence of notes (or chords) and then way for a users answer (through a microphone, MIDI device, or computer-keyboard).

To Run
------
1. Follow the instructions below to install any prerequisites needed.

2. Download and unzip Ear-Those-Notes.

4. Open a terminal/command-prompt, navigate into the folder containing the "earthosenotes.py" file, and enter the following command (without the $).

$ python earthosenotes.py


Prerequisites
-------------
-  **python 2.x**
-  **mingus**
-  **sequencer**
-  **fluidsynth**

Setup
-----

**1. Get Python 2**

Note: If you have a **Mac** or are running **Linux**, you already have Python 2.x.  If you're on **Windows**, go download Python 2 and install it.

**2. Install mingus and sequencer python modules**

This is easy using pip (which typically comes with Python).  Just open up a terminal/command-prompt and enter the following two commands (without the $).

$ pip install mingus

$ pip install sequencer

**3. Install fluidsynth**

This is easy through a linux/mac package manager.

[On Linux:]

$ sudo apt-get install fluidsynth

[On OS X:] (assuming you have Homebrew installed)

$ brew install fluidsynth

[On Windows:]

You can either compile FluidSynth yourself or use the binary installer (.exe) that is available for its GUI, Qsynth.

For Help
--------
Contact me, AndyAPort@gmail.com

Licence
-------

This code is available for reuse under the Apache License.
