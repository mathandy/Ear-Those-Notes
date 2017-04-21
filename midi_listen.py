"""Listen for midi signals."""
# This is a modified version of the test_midiin_callback.py example from
# https://github.com/SpotlightKid/python-rtmidi


from __future__ import print_function
import logging
import sys
import time
from rtmidi.midiutil import open_midiinput

HISTORY = []  # collects notes for global use

def initialize_midi_input():
    log = logging.getLogger('midiin_callback')
    logging.basicConfig(level=logging.DEBUG)

    # Prompts user for MIDI input port, unless a valid port number or name
    # is given as the first argument on the command line.
    # API backend defaults to ALSA on Linux.
    port = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        midiin, port_name = open_midiinput(port)
    except (EOFError, KeyboardInterrupt):
        sys.exit()

    # print("Attaching MIDI input callback handler.")
    midiin.set_callback(MidiInputHandler(port_name))


class MidiKeyPress(object):
    def __init__(self, port, time, message):
        self.port = port
        self.time = time
        self.message = message
        self.note = message[1]
        self.velocity = message[2]
        self.channel = message[0]

    def __repr__(self):
        return "[%s] @%0.6f %r" % (self.port, self.time, self.message)



class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        HISTORY.append(MidiKeyPress(self.port, self._wallclock, message))





if __name__ == '__main__':
    print("Entering main loop. Press Control-C to exit.")
    ct = 0
    try:
        # Just wait for keyboard interrupt,
        # everything else is handled via the input callback.
        while True:
            if len(HISTORY) > ct:
                print(HISTORY[-1])
                ct += 1
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midiin.close_port()
        del midiin
