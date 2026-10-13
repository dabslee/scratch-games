# Building CyberpunkNinja.sb3

`CyberpunkNinja.sb3` is generated, not edited by hand. A Python build compiles the game
logic, renders the art, synthesizes the audio, and packs everything into a Scratch 3 project.

## What's where

```
CyberpunkNinja/
├── CyberpunkNinja.sb3            the game (generated; don't edit by hand)
├── CyberpunkNinja_README.md      instructions, controls and credits
├── BUILDING.md                   this file
├── story.json                    all dialogue, in play order (also documents plot, cast and bosses)
├── art/                          hand-drawn source art
│   ├── splash_logo.png           the splash screen logo
│   ├── portraits/                the dialogue portrait sheet, its manifest and preview
│   │   └── sources/              hand-drawn portraits installed into the sheet
│   └── characters/               sprite art: townspeople, the receptionist, Dobunushi, the Daimyo's
│                                 frames and mech parts, the Harmacist's frames, edits to pack characters
├── CyberpunkNinja_AssetPack/     the base asset pack (palette, tilesets, backgrounds, characters, fonts)
├── src/                          the build
│   ├── build.py                  entry point
│   ├── scratchc.py               Python-to-Scratch compiler
│   ├── logic/                    the game itself, in the compiler's Python subset
│   ├── gfx/                      procedural and edited art, one module per chapter
│   ├── levels.py                 every room
│   ├── dialogue.py               loads story.json and the hint boxes
│   ├── audio.py                  synthesized music and sound effects
│   ├── assets.py                 asset pack access, room rendering, text
│   └── export_portraits.py       rebuilds or installs into the portrait sheet
└── tools/playtest/               headless playtests
```

| Path | What it is |
|---|---|
| `src/build.py` | Entry point. Assembles every sprite, costume, sound and script and writes `CyberpunkNinja.sb3` |
| `src/scratchc.py` | A small Python-to-Scratch compiler: game scripts are written in a Python subset and compiled to Scratch blocks |
| `src/logic/` | The game itself, in that Python subset: Hotaru (`hotaru.py`), enemies and bosses (`enemies.py`), objects, stage flow, menus, HUD |
| `src/gfx/` | Generated and edited art. Shared helpers are in `util.py`, with one module per chapter (`vaults`, `sewers`, `monorail`, `hollow_floor`, `gardens`, `academy`, `tenshu`), plus `ui`, `portraits` and `npcs`. `mech.py` rigs the Daimyo's mech and `edits.py` carries edits to pack characters across their frames |
| `src/levels.py` | Every room: tiles, objects, exits |
| `src/dialogue.py` | Loads `story.json` and the in-game hint boxes |
| `src/audio.py` | Synthesized music and sound effects |
| `src/assets.py` | Reads the asset pack and `art/`, autotiles and renders rooms, draws text in Shinobi Mono |
| `src/export_portraits.py` | Rebuilds the portrait sheet's preview and manifest, and installs new portraits into it |
| `art/` | Hand-drawn source art (see the tree above) |
| `CyberpunkNinja_AssetPack/` | The base asset pack (palette, tilesets, backgrounds, character strips, fonts, and its starter `.sb3`, which supplies most base sprites) |
| `story.json` | All dialogue, in play order |
| `tools/playtest/` | Headless playtests: runs the `.sb3` in scratch-vm inside Chromium with a bot playing |

## Build

You need Python 3.11+ and `ffmpeg` on the PATH (sounds are encoded to MP3).

```sh
cd CyberpunkNinja
python3 -m pip install -r src/requirements.txt
python3 src/build.py
```

This writes `CyberpunkNinja.sb3` next to this file and prints its size, target count and
block count. A first build takes about a minute; the synthesized audio is cached in
`src/.audio_cache/` (ignored by git), so later builds are faster. The output is
deterministic: a clean build matches the committed `.sb3` file for file (only the zip
timestamps differ).

To build against another copy of the asset pack, set `CN_PACK=/path/to/CyberpunkNinja_AssetPack`.

**Size limit:** Scratch refuses a `project.json` over about 5 MB. Check it after a change:

```sh
unzip -l CyberpunkNinja.sb3 project.json
```

Logic is the main cost. Inside an expression, `min()` and `max()` compile to arithmetic that
repeats both arguments; assigned straight to a variable (`x = min(max(x + d, lo), hi)`) they
compile to a set and an `if` per bound instead, which is much smaller. The size that counts is
what Scratch saves after loading the file, which has the same layout as the build's output.

## Playtest

```sh
cd tools/playtest
npm ci
npx playwright-core install chromium     # or set CHROME_PATH to an existing Chrome/Chromium
cp ../../CyberpunkNinja.sb3 game.sb3
```

`node shot.js game.sb3 <test.js>` serves this folder, loads the game in headless Chromium,
and runs the test script. The bot in `bot.js` plays Hotaru: it moves, attacks, and reads
enemy states to deflect, block, jump or Phase Step. Tests use `lib.js` to jump to chapters
and rooms, read and set variables, press keys, and take screenshots (`s_<name>.png`).

**Boss run** (`boss_run.js`, or `npm run boss`): fights a boss and logs the state every 5 s.

```sh
BOSS="start_ch8,86,daimyo_dead,250,dm" VARS=dm_ph KB=1 SHARDS=2 npm run boss
```

`BOSS` is `<chapter start event>,<room>,<boss-dead variable>,<seconds>,<log tag>`. `KB=1`
brings Kuro into the Daimyo fight (`KB=2` leaves him out) and `SHARDS` sets the Memory Shards.

**Warning-flash audit** (`tell_audit.js`, or `npm run tells`): records every white tell on
a sprite frame by frame and reports each flash's length and when the attack lands. A
correct tell is 9 frames long and lands on the 10th (Hotaru reacts the frame after a hit
resolves).

```sh
BOSS="start_ch7,76,60" SPR=Mukuro npm run tells
BOSS="start_ch4,47,80" SPR=Raijin NOBOT=1 V=1 npm run tells   # bot off, every flash listed
```

**Chapters and boss rooms.** Rooms are numbered from 1 in the order of `levels.ROOMS`.

| Chapter start event | Boss room | Boss sprite |
|---|---|---|
| `start_ch1` | 19 | `BigOni` |
| `start_ch2` | 28 | `LadyLuck` |
| `start_ch3` | 38 | `Dobunushi` |
| `start_ch4` | 47 | `Raijin` |
| `start_ch5` | 56 | `KuroBoss` |
| `start_ch6` | 66 | `Harmacist` (Wardens in rooms 60 to 64) |
| `start_ch7` | 76 | `Mukuro` |
| `start_ch8` | 86 | `Daimyo` |

Both test scripts set `dmg_in` (the damage-taken multiplier) to 0 so the bot can't lose.
