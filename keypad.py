#!/usr/bin/env python3
"""Read and program the PCsensor MK321BT 3-key keypad from macOS.

Usage:
  keypad.py read
  keypad.py set <key 1-3> <combo>     e.g.  keypad.py set 1 cmd+shift+4

Keys are numbered right-to-left: key 1 is the physical right key, key 3 the left.

A combo is zero or more modifiers (cmd, ctrl, alt/opt, shift; prefix r_ for the
right-hand one) plus at most one key, joined with "+". Settings are stored on
the keypad itself, so they survive unplugging and work on any computer.
"""
import sys
import time

import hid

VID, PID = 0x3553, 0xC130
CONFIG_INTERFACE = 1

MODIFIERS = {
    "ctrl": 0x01, "shift": 0x02, "alt": 0x04, "opt": 0x04, "cmd": 0x08,
    "r_ctrl": 0x10, "r_shift": 0x20, "r_alt": 0x40, "r_opt": 0x40, "r_cmd": 0x80,
}

# USB HID keyboard usage codes
KEYS = {chr(ord("a") + i): 0x04 + i for i in range(26)}
KEYS.update({str(n): 0x1E + n - 1 for n in range(1, 10)})
KEYS.update({f"f{n}": 0x3A + n - 1 for n in range(1, 13)})
KEYS.update({f"f{n}": 0x68 + n - 13 for n in range(13, 25)})
KEYS.update({
    "0": 0x27, "enter": 0x28, "esc": 0x29, "backspace": 0x2A, "tab": 0x2B,
    "space": 0x2C, "-": 0x2D, "=": 0x2E, "[": 0x2F, "]": 0x30, "\\": 0x31,
    ";": 0x33, "'": 0x34, "`": 0x35, ",": 0x36, ".": 0x37, "/": 0x38,
    "insert": 0x49, "home": 0x4A, "pageup": 0x4B, "delete": 0x4C, "end": 0x4D,
    "pagedown": 0x4E, "right": 0x4F, "left": 0x50, "down": 0x51, "up": 0x52,
    "mute": 0x7F, "volup": 0x80, "voldown": 0x81,
})
KEY_NAMES = {code: name for name, code in KEYS.items()}
MODIFIER_NAMES = [(bit, name) for name, bit in MODIFIERS.items() if name not in ("opt", "r_opt")]

KEY_TYPE = 0x01


def open_keypad():
    for info in hid.enumerate(VID, PID):
        if info["interface_number"] == CONFIG_INTERFACE:
            dev = hid.device()
            dev.open_path(info["path"])
            return dev
    sys.exit("Keypad not found. Is it plugged in via USB?")


def send(dev, packet):
    dev.write(bytes(packet))
    time.sleep(0.03)


def read_key(dev, key):
    send(dev, [0x01, 0x82, 0x08, key, 0, 0, 0, 0])
    return dev.read(8, 500)


def describe(data):
    if not data or data[1] == 0:
        return "unconfigured"
    if data[1] not in (KEY_TYPE, 0x81):
        return "raw " + " ".join(f"{b:02x}" for b in data)
    parts = [name for bit, name in MODIFIER_NAMES if data[2] & bit]
    if data[3]:
        parts.append(KEY_NAMES.get(data[3], f"0x{data[3]:02x}"))
    return "+".join(parts) or "nothing"


def parse_combo(combo):
    modifiers, keycode = 0, 0
    for part in combo.lower().split("+"):
        if part in MODIFIERS:
            modifiers |= MODIFIERS[part]
        elif part in KEYS and not keycode:
            keycode = KEYS[part]
        else:
            sys.exit(f"Don't understand '{part}' in '{combo}'")
    return modifiers, keycode


def write_key(dev, key, modifiers, keycode):
    send(dev, [0x01, 0x81, 0x08, key, 0, 0, 0, 0])
    send(dev, [0x08, KEY_TYPE, modifiers, keycode, 0, 0, 0, 0])
    dev.read(8, 500)  # the keypad acknowledges each write; discard it


def main(argv):
    if len(argv) == 2 and argv[1] == "read":
        dev = open_keypad()
        for key in (1, 2, 3):
            print(f"key {key}: {describe(read_key(dev, key))}")
    elif len(argv) == 4 and argv[1] == "set" and argv[2] in ("1", "2", "3"):
        key = int(argv[2])
        modifiers, keycode = parse_combo(argv[3])
        dev = open_keypad()
        write_key(dev, key, modifiers, keycode)
        print(f"key {key}: {describe(read_key(dev, key))}")
    else:
        sys.exit(__doc__)
    dev.close()


if __name__ == "__main__":
    main(sys.argv)
