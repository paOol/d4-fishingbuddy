# D4 FishingBuddy 🎣

A safe, lightweight fishing helper for **Diablo 4** on Windows.

It works **only** by reading pixels off your screen and sending normal keyboard
key presses — **no memory reading, no DLL injection, no game-file edits, nothing
that touches the game process.** It's the software equivalent of a person
watching the screen and pressing a key when they see the icon.

It does exactly what you'd do by hand:

```
F1 (cast)  →  watch above your character for the fishing icon  →  A (hook)  →  wait  →  repeat
```

---

## ⚠️ Read this first

- Automating input in an online game can violate Blizzard's Terms of Service even
  when no memory hacks are involved, and **could risk your account.** You are
  responsible for how you use this. Use it on the character/region you're willing
  to risk, and don't run it unattended for long stretches.
- This tool never reads or writes game memory and never modifies game files. That
  makes it far less likely to trip anti-cheat than a true "hack," but it is **not
  a guarantee.**

---

## Requirements

- Windows 10/11
- [Python 3.10+](https://www.python.org/downloads/) (check "Add Python to PATH"
  during install)
- **Diablo 4 set to Display Mode = "Windowed Fullscreen" (borderless).**
  Exclusive *Fullscreen* often hands screen-capture tools black frames, and the
  detector will never see the icon. Borderless looks identical and captures fine.

## Install

1. Download/clone this folder.
2. Double-click **`setup.bat`** (installs the Python packages).

## Setup (one time, ~2 minutes)

The icon position depends on your resolution, so you calibrate once.

### 1. Aim the scan box — `calibrate_roi.bat`
A live preview of your screen appears with a **green box** centered above the red
crosshair (screen center). Your character sits at screen center, and the fishing
icon pops up above their head — get that area inside the green box.

| Key | Action |
|-----|--------|
| Arrow keys / WASD | move the box |
| `+` / `-` | grow / shrink |
| `[` `]` | narrower / wider |
| `;` `'` | taller / shorter |
| `s` | **save** to `config.json` |
| `q` / `Esc` | quit |

Keep the box reasonably tight around where the icon appears — smaller box = faster
and fewer false matches.

### 2. Capture the icon — `capture_template.bat`
1. Run it (right-click → **Run as administrator** if D4 is elevated).
2. Alt-tab into D4, cast a line with **F1**.
3. The moment the **fishing icon** appears over your head, press **F7**.
   Two beeps = saved (`icon_template.png`).
4. Do it 2–3 times; the latest grab wins (all are archived in `templates/`).
   Pick the cleanest one and copy it over `icon_template.png` if needed.

That's it — you're ready.

## Run — `start.bat`

| Hotkey | Action |
|--------|--------|
| **F8** | toggle fishing **ON / OFF** |
| **F9** | quit |

Feedback so you know what's happening without alt-tabbing:
- **Beeps:** rising tone = armed, falling = paused, bright double-tone = fish
  hooked, soft click = cast.
- **Console:** colored status lines (cast / detected + confidence score / hook /
  no-bite).

> Run **`start.bat` as administrator** if your key presses don't reach the game.
> When Battle.net/D4 runs elevated, a non-elevated script can't send it input.

---

## Tuning (`config.json`)

Everything lives in `config.json`. Highlights:

| Field | Meaning |
|-------|---------|
| `keys.cast` / `hook` / `toggle` / `quit` | key bindings (default F1 / A / F8 / F9) |
| `roi.*` | scan box — set by `calibrate_roi.bat` |
| `detection.method` | `"template"` (recommended) or `"color"` |
| `detection.match_threshold` | template confidence 0–1. **Too many false hooks → raise** (e.g. 0.8). **Missing real bites → lower** (e.g. 0.65). Watch the score the console prints. |
| `timing.max_wait_for_icon` | seconds to wait for a bite before recasting |
| `timing.settle_after_cast` | pause after F1 before watching |
| `timing.after_hook_delay` | pause after hooking, before next cast |
| `timing.reaction_delay` | extra delay before pressing A (set >0 to feel less robotic) |
| `timing.humanize` / `humanize_jitter` | randomize delays so timing isn't identical every cast |

### Color mode (no template)
If template matching is finicky, set `detection.method` to `"color"`. It hooks
when enough pixels in the box fall inside an HSV color band (`lower_hsv`/`upper_hsv`,
`min_pixels`), tuned for the icon's teal/cyan glow. Adjust `min_pixels` up if it
false-triggers on watery terrain.

---

## How it works

```
fishingbuddy.py        main loop + global hotkeys + feedback
calibrate_roi.py       aim the scan box (live preview)
capture_template.py    grab the icon image with F7
config.json            all settings
core/
  config.py    load/save config + ROI geometry
  screen.py    mss screen capture (pixels only)
  detect.py    OpenCV template match + HSV color mask
  input.py     pydirectinput key presses + keyboard hotkeys
  feedback.py  console colors + winsound beeps
```

## Troubleshooting

- **Black/no detection in fullscreen** → switch D4 to *Windowed Fullscreen*.
- **Keys don't reach the game** → run `start.bat` as administrator.
- **Hooks too early / on nothing** → raise `match_threshold`, tighten the ROI.
- **Misses real bites** → lower `match_threshold`, shrink `poll_interval`, make
  sure the icon falls fully inside the green box, re-capture a cleaner template.
- **"template not found"** → run `capture_template.bat`, or set
  `detection.method` to `"color"`.
- **Hotkeys do nothing** → the `keyboard` library needs admin on some systems;
  run as administrator.
