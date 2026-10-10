# Building CyberpunkNinja.sb3

`CyberpunkNinja.sb3` is generated, not edited by hand. A Python build compiles the game
logic, renders the art, synthesizes the audio, and packs everything into a Scratch 3 project.

## What's where

| Path | What it is |
|---|---|
| `build/build.py` | Entry point. Assembles every sprite, costume, sound and script and writes `CyberpunkNinja.sb3` |
| `build/scratchc.py` | A small Python-to-Scratch compiler: game scripts are written in a Python subset and compiled to Scratch blocks |
| `build/logic/` | The game itself, in that Python subset: Hotaru (`hotaru.py`), enemies and bosses (`enemies.py`), objects, stage flow, menus, HUD |
| `build/levels.py` | Every room: tiles, objects, exits |
| `build/dialogue.py` | Loads `story.json` and the in-game hint boxes |
| `build/art_*.py` | Procedural and edited art: chapter tilesets, backgrounds, enemy recolors, sprite edits (`art_edits.py`), the Daimyo's mech rig (`art_mech.py`) |
| `build/audio.py` | Synthesized music and sound effects |
| `art/` | Hand-drawn source art: portraits, sprite edits, the Daimyo and Harmacist frames, the mech parts |
| `CyberpunkNinja_AssetPack/` | The base asset pack (palette, tilesets, backgrounds, character strips, fonts, and its starter `.sb3`, which supplies most base sprites) |
| `story.json` | All dialogue, in play order |
| `tools/playtest/` | Headless playtests: runs the `.sb3` in scratch-vm inside Chromium with a bot playing |

## Build

You need Python 3.11+ and `ffmpeg` on the PATH (sounds are encoded to MP3).

```sh
cd CyberpunkNinja
python3 -m pip install -r build/requirements.txt
python3 build/build.py
```

This writes `CyberpunkNinja.sb3` next to this file and prints its size, target count and
block count. A first build takes about a minute; the synthesized audio is cached in
`build/.audio_cache/` (ignored by git), so later builds are faster. The output is
deterministic: a clean build matches the committed `.sb3` byte for byte.

To build against another copy of the asset pack, set `CN_PACK=/path/to/CyberpunkNinja_AssetPack`.

**Size limit:** Scratch refuses a `project.json` over about 5 MB. Check it after a change:

```sh
unzip -l CyberpunkNinja.sb3 project.json
```

Logic is the main cost. `min()` and `max()` compile to expressions that repeat both
arguments, so prefer `x -= ...` followed by a clamp over `x = max(0, x - ...)` with a long
expression inside.

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
BOSS="start_ch8,84,daimyo_dead,250,dm" VARS=dm_ph KB=1 SHARDS=2 npm run boss
```

`BOSS` is `<chapter start event>,<room>,<boss-dead variable>,<seconds>,<log tag>`. `KB=1`
brings Kuro into the Daimyo fight (`KB=2` leaves him out) and `SHARDS` sets the Memory Shards.

**Warning-flash audit** (`tell_audit.js`, or `npm run tells`): records every white tell on
a sprite frame by frame and reports each flash's length and when the attack lands. A
correct tell is 9 frames long and lands on the 10th (Hotaru reacts the frame after a hit
resolves).

```sh
BOSS="start_ch7,74,60" SPR=Mukuro npm run tells
BOSS="start_ch4,46,80" SPR=Raijin NOBOT=1 V=1 npm run tells   # bot off, every flash listed
```

**Chapters and boss rooms.** Rooms are numbered from 1 in the order of `levels.ROOMS`.

| Chapter start event | Boss room | Boss sprite |
|---|---|---|
| `start_ch1` | 19 | `BigOni` |
| `start_ch2` | 28 | `LadyLuck` |
| `start_ch3` | 37 | `Dobunushi` |
| `start_ch4` | 46 | `Raijin` |
| `start_ch5` | 55 | `KuroBoss` |
| `start_ch6` | 65 | `Harmacist` (Wardens in rooms 57 to 63) |
| `start_ch7` | 74 | `Mukuro` |
| `start_ch8` | 84 | `Daimyo` |
