# Cyberpunk Ninja: Assets

Every image in the game, as PNGs. Everything is drawn at a **240×180 base resolution** (Scratch's 4:3 stage at half size) in one shared 34-color palette, with no anti-aliasing, so a recolor is a straight palette swap. Folder and file names are lowercase `snake_case`.

## Folder map

```
assets/
├── characters/    one folder per character sprite: hotaru, kuro, mukuro, daimyo, big_oni, …
├── objects/       props and set pieces: props, crate, cage, slot_machine, phase_block, sludge, …
├── fx/            slash_fx, combat_fx, move_fx, projectiles, rain, glitch_bg, flash, fade, warmup
├── ui/            hud, enemy_ui, banners, dialogue, hints, menu; plus
│                  keys/ (key caps for the hint cards), hint_note.png and splash/splash_logo.png
├── backgrounds/   stage (the backdrops), sky, parallax_far, parallax_mid, ranks
├── tilesets/      an 8×8 atlas per material, layout.json (tile names) and toxic_8x8.png
├── portraits/     portraits.png (every dialogue portrait), portraits.json (cell order),
│                  Kuro's glitch frames and frame.png (the border export_portraits.py uses)
├── fonts/         Shinobi Mono, regular and bold: one glyph per character
└── palette/       palette.json, the 34 colors by name
```

Each sprite folder becomes one Scratch sprite (`backgrounds/stage` is the Stage). `src/build.py` lists which folder goes with which sprite.

## Costume folders

A costume folder holds one PNG per costume and a `costumes.json` that lists them in order:

```json
{"costumes": [
  {"name": "idle_0", "file": "idle_0.png", "anchor": [24, 37]},
  {"name": "dmf_idle_0", "file": "dmf_idle_0.png", "anchor": [40, 61], "scale": 3},
  {"generated": "hints"}
]}
```

- **name** is the costume's name in Scratch; the game's scripts switch costumes by name.
- **anchor** is the rotation center (where the sprite's x/y sits), in the PNG's pixels. Characters stand on it, so it's usually between the feet.
- **scale** is how far the PNG is blown up in the game. Leave it out for the usual 4 (one art pixel = 2 stage units). The Daimyo's and the Harmacist's frames use 3, which draws them at 1.5 stage units per pixel so they stand as tall as Hotaru.
- **generated** marks where the build inserts costumes it makes from data: `rooms` (from `src/levels.py`), `dialogue_pages`, `hints`, `option_labels`, `option_values` and `pages` (text from `story.json` and `src/dialogue.py`), and `portraits` (cut from `portraits/portraits.png`).

To change a costume, edit its PNG and rebuild. To add one, add the PNG and a line in `costumes.json`. Costumes are switched by name, so order only matters for scripts that step through them.

A file name is the costume name, with characters that can't go in a file name spelled out as hex (`ch_A` is `ch_x41.png`).

## Naming conventions

**Animations:** costumes are named `<anim>_<frame>` (`run_0` … `run_7`). Hotaru's frame counts and speeds are in `characters/hotaru/animations.json`.

**Hotaru's scarf shows dash charges:** cyan costumes have no suffix, magenta (1 charge) end in `_m`, and gray (0 charges) end in `_g`. Example: `run_3_m`.

**Variants share a sprite under a prefix:** for example, in `characters/hannya_boy`, `u_` is the suited grunt, `m_` and `mg_` are Kuro's memories of them, and `d_` is the Drainling.

**Text:** each font has one white glyph per printable ASCII character, named `ch_<char>`. The build sets dialogue, hints and menu text with them.

**Bars and counters:** HUD costumes are pre-made for each level: `hp_00` to `hp_10`, `heat_00` to `heat_16`, `integrity_00` to `integrity_16`, `boss_00` to `boss_20`, `dash_0` to `dash_2` and `gourd_0` to `gourd_5`.

## Tilesets

Rooms are built from the tile atlases: `layout.json` names each 8×8 cell, the same in every atlas. The build picks a wall tile by which of its 4 neighbors are solid:

| Up | Down | Left | Right | Tile |
|---|---|---|---|---|
| no | yes | no | yes | `top_left` |
| no | yes | yes | yes | `top` |
| no | yes | yes | no | `top_right` |
| yes | yes | no | yes | `left` |
| yes | yes | yes | yes | `center` (or `inner_tl`/`inner_tr`/`inner_bl`/`inner_br` when a diagonal is open) |
| yes | yes | yes | no | `right` |
| yes | no | no | yes | `bottom_left` |
| yes | no | yes | yes | `bottom` |
| yes | no | yes | no | `bottom_right` |
| no | yes | no | no | `col_top` (then `col_mid`, `col_bottom`) |
| no | no | any | any | `single`, `row_l`, `row_m`, `row_r` |

One-way platforms are `plat_l`, `plat_m`, `plat_r` and `plat_single`; spikes are `spikes_up` and `spikes_down`. `toxic_8x8.png` holds the Sewers' runoff: a row per bubbling frame, with the cell below the surface first, then six surface cells that repeat across the room.
