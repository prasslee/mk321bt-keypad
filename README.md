# MK321BT keypad (macOS)

Programs the PCsensor MK321BT 3-key keypad from macOS, without the vendor's Windows software.

## Current layout

Example layout:

| Physical key | Does | Tool key number |
|---|---|---|
| Left | Right Ctrl+Right Option+Right Cmd | 3 |
| Middle | Enter | 2 |
| Right | Right Ctrl+Right Shift+Right Cmd | 1 |

The keypad numbers its keys right-to-left. The layout is stored on the keypad itself.

## Changing a key

The keypad must be in USB mode (mode switch set to USB, cable plugged in). It cannot be programmed over Bluetooth.
If `keypad.py` says the keypad is not found, turn off the Mac's Bluetooth so the keypad falls back to the cable.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python keypad.py read
.venv/bin/python keypad.py set 2 enter
```

Update the table above whenever the layout changes.

Some apps do not see F18 even though the keypad accepts it (`read` shows it). Prefer a modifier combo like the ones above.

Modifier-only combos are the most reliable for global shortcuts. When any app leaves macOS Secure Keyboard Entry on (Chrome does after a password field), global shortcut listeners stop seeing ordinary keys like 1, 2 or 9, but still see modifiers. Right Ctrl is useful because the MacBook keyboard has none, so these combos can only come from the keypad.
