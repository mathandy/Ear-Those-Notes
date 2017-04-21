"""A module of convenient tools to listen for and record midi key presses."""
# Some code here is recycled from rtmidi's `test_midiin_callback.py` example
# available at: https://github.com/SpotlightKid/python-rtmidi

from __future__ import print_function
import logging
import sys
import time
from rtmidi.midiutil import open_midiinput


class MidiKeyPress(object):
    """A container class for an individual midi key-press event."""
    def __init__(self, port_description, timestamp, message):
        self.port_info = port_description
        self.time = timestamp
        self.message = message
        self.channel = message[0]
        self.note = message[1]
        self.velocity = message[2]

    def __repr__(self):
        return "[%s] @%0.6f %r" % (self.port_info, self.time, self.message)


class MidiListener:
    """Create midi_listener object to record midi events.
    
    All midi events will be recorded in `ml.history` as `MidiKeyPress`
    objects unless the optional `always_recording` argument is set to 
    `False`.  
    If you prefer, you can set `always_recording=False` and use the 
    `ml.start_recording`, `ml.stop_recording`, and `ml.listen()` to control 
    when midi events are recorded.
    """

    def __init__(self, port=None, always_recording=True):
        """
        
        Args:
            port (int, optional): specifies a midi device/port option.  Only 
            useful if you already know how your available midi ports will be 
            listed.
            always_recording (bool):   
        """
        self.always_recording = always_recording
        self.currently_recording = always_recording
        self.time_to_stop_recording = None
        self.history = []  # collects note history as MidiKeyPress objects
        self._port = port
        self._wallclock = time.time()
        self.debug_mode = False
        # self.log = logging.getLogger('midiin_callback')
        # logging.basicConfig(level=logging.DEBUG)

        # Prompts user for MIDI input port, unless a valid port number or name
        # is given as the first argument on the command line.
        # API backend defaults to ALSA on Linux.
        try:
            self._midiin, self._port = open_midiinput(self._port)
        except (EOFError, KeyboardInterrupt):
            sys.exit()

        # print("Attaching MIDI input callback handler.")
        self._midiin.set_callback(self._midi_input_handler)

    def _midi_input_handler(self, event, data=None):

        # if it's time, stop recording
        if (self.time_to_stop_recording is not None and
                    time.time() >= self.time_to_stop_recording):
            self.currently_recording = False

        # otherwise, record any midi events
        if self.currently_recording:
            message, deltatime = event
            self._wallclock += deltatime
            self.history.append(
                MidiKeyPress(self._port, self._wallclock, message))

            if self.debug_mode:
                print(self.history[-1])

    def start_recording(self, stop_time=None):
        self.currently_recording = True
        self.time_to_stop_recording = stop_time

    def stop_recording(self, stop_time=None):
        """Use default (stop_time=None) to stop now."""
        self.currently_recording = False
        self.time_to_stop_recording = stop_time

    def listen(self, duration=None, num_notes=None, wait_for_key_release=False):
        """Returns just those MidiKeyPress objects created over the next 
        `duration` seconds of time or after the next `num_notes` are played, 
        whichever comes first.
        
        duration (int or float, optional): If `duration` is specified, will 
        return MidiKeyPress objects created over the next `duration` seconds of 
        time.  Optional if `num_notes` is specified.  Defaults to None.
        
        num_notes (int, optional): If `num_notes` is specified, will return as 
        soon as `num_notes` notes have been played.  Optional if `duration` is 
        specified.  Defaults to None.
        
        wait_for_key_release (bool): If `False` and `num_notes` is not None, 
            will not wait for the release of each note played.  Defaults 
            to False."""

        if num_notes is None:
            num_notes = float("inf")

        if duration is None:
            stop_time = float("inf")
        else:
            stop_time = duration + time.time()

        i0 = max(len(self.history) - 1, 0)
        if not self.always_recording:
            self.start_recording()

        def is_released(ix):
            notes_released_since_ix = [_.note for _ in self.history[ix + 1:]
                                       if _.velocity == 0]
            return self.history[ix].note in notes_released_since_ix

        note_count = 0
        cursor = i0
        released = []
        unreleased = []
        while time.time() < stop_time and note_count < num_notes:

            if len(self.history) > i0 + 1 + note_count:  # if new notes heard
                new_presses = [ix for ix in range(cursor, len(self.history))
                               if self.history[ix].velocity > 0]
                new_releases = [ix for ix in range(cursor, len(self.history))
                                if self.history[ix].velocity == 0]
                cursor = len(self.history)

                if wait_for_key_release:
                    # check of older presses were released
                    for ix in new_releases:
                        for jx_idx, jx in enumerate(unreleased):
                            if self.history[ix].note == self.history[jx].note:
                                released.append(unreleased.pop(jx_idx))
                                break

                    # divvy up new_presses into released and unreleased
                    if new_presses:
                        tmp = [(is_released(ix), ix) for ix in new_presses]
                        released += [ix for rel, ix in tmp if rel]
                        unreleased += [ix for rel, ix in tmp if not rel]
                        if self.debug_mode:
                            # print("note_count:", note_count)
                            print("released:", released)
                            print("unreleased:", unreleased)
                            print("new_presses", new_presses)

                    note_count = len(released)
                else:
                    note_count = sum(1 for x in self.history[i0:]
                                     if x.velocity > 0)

        if not self.always_recording:
            self.stop_recording()

        return self.history[i0:]

    def close(self):
        self._midiin.close_port()
        del self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    # with MidiListener() as ml:
    with MidiListener(0) as ml:
        ml.debug_mode = False
        wait = False

        print("Test mode: Listening for 5 seconds...")
        for x in ml.listen(5, None, wait):
            print(x)

        print("done.\n")

        print("Test mode: Listening for 4 notes...")
        for x in ml.listen(None, 4, wait):
            print(x)
        print("done.\n")

        print("Test mode: Listening for 3 notes or 5 seconds...")
        for x in ml.listen(5, 3, wait):
            print(x)
        print("done.\n")
