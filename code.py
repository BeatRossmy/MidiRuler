import os
import board
from digitalio import DigitalInOut, Direction

import time
import touchio

import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# CHANGE MIDI NOTES OR CHANNEL
midi_notes = [60,61,62,63]
midi_channel = 16

DEBUG = False

if DEBUG:
    print(dir(board), os.uname())

midi_usb = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1], out_channel=midi_channel - 1
)

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

touches = [DigitalInOut(board.CAP0)]
for p in (board.CAP1, board.CAP2, board.CAP3):
    touches.append(touchio.TouchIn(p))

leds = []
for p in (board.LED4, board.LED5, board.LED6, board.LED7):
    led = DigitalInOut(p)
    led.direction = Direction.OUTPUT
    led.value = True
    time.sleep(0.25)
    leds.append(led)
for led in leds:
    led.value = False

cap_touches = [False, False, False, False]
caps = [False, False, False, False]

def read_caps():
    t0_count = 0
    t0 = touches[0]
    t0.direction = Direction.OUTPUT
    t0.value = True
    t0.direction = Direction.INPUT
    for i in range(15):
        t0_count = t0_count + t0.value

    cap_touches[0] = t0_count > 1
    cap_touches[1] = touches[1].raw_value > 3000
    cap_touches[2] = touches[2].raw_value > 3000
    cap_touches[3] = touches[3].raw_value > 3000

    return cap_touches

while True:
    old_caps = caps.copy()
    caps = read_caps()

    for i,c in enumerate(caps):
        # IF CHANGE
        if c != old_caps[i]:
            # LED
            leds[i].value = c
            # MIDI
            if DEBUG:
                print(str(i), midi_notes[i], "on" if c else "off")
            if c:
                midi_usb.send(NoteOn(midi_notes[i],100))
            else:
                midi_usb.send(NoteOff(midi_notes[i],0))

    time.sleep(0.01)
