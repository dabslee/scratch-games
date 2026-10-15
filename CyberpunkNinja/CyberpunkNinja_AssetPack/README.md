# Cyberpunk Ninja: Asset Pack

Pixel art asset pack for *Cyberpunk Ninja*, a combat-first platformer. Everything is drawn natively at a **240×180 base resolution** (Scratch's 4:3 stage at half size) with one shared 34-color palette.

## Specs

**Base resolution:** 240×180. One art pixel = 2 Scratch stage units (the 480×360 stage).
**Facing:** every character faces right. Flip with Scratch's `left-right` rotation style.
**Anchors:** character frames are 48×40 with the feet at (24, 37). Big Oni frames are 112×88 with the feet at (50, 85). Every costume's rotation center is set to its anchor, so swapping costumes never makes a sprite jitter.
**Overlay FX:** `SlashFX` uses the same 48×40 frame and anchor as Hotaru. Put the FX clone at Hotaru's x/y and direction and the arcs line up with her sword.
**Palette:** `palette/` has `.gpl` (Aseprite, GIMP), `.hex`, `.json`, and swatches.

## Folder map

| Folder | What's inside |
|---|---|
| `scratch/CyberpunkNinja_Starter.sb3` | Every asset loaded into one Scratch project. Click the green flag to play the animated title screen |
| `scratch/sprite3/` | One `.sprite3` per sprite, for adding pieces to an existing project |
| `scratch/backdrops_480x360/` | Backdrops sized for drag-and-drop upload |
| `sprites/` | 1x horizontal strips per animation plus JSON (frame size, count, fps, loop, anchor) for other engines. `atlas.json` indexes everything |
| `backgrounds/` | Four chapter sets (`sump`, `neon_alley`, `server_gardens`, `tenshu`), each with `sky`, `far`, and `mid` layers, plus rain overlay frames |
| `tilesets/` | 8×8 tile atlases for four materials and `layout.json` |
| `fonts/` | Shinobi Mono Regular and Bold as `.ttf`, plus bitmap sheets |
| `title_screen/` | 8 animated title frames, with and without "PRESS ANY KEY" |
| `previews/` | Animated GIFs of every animation and mockup screenshots |

## Using it in Scratch

**Fastest start:** File > Load from your computer > `CyberpunkNinja_Starter.sb3`. All sprites are hidden; show the ones you need. The Stage already has a script that loops the title animation.

**Adding to an existing project:** Choose a Sprite > Upload Sprite > pick files from `scratch/sprite3/`. Costumes come in at the correct resolution and pivot; don't upload loose PNGs for characters, because Scratch resamples them.

**Playing an animation:** costumes are named `<anim>_<frame>`, so one variable drives everything:

```
switch costume to (join (anim) (join "_" (frame)))
```

Advance `frame` with a timer at the fps listed below and wrap at the frame count.

**Hotaru's scarf shows dash charges:** cyan costumes have no suffix, magenta (1 charge) end in `_m`, and gray (0 charges) end in `_g`. Example: `run_3_m`.

**Text:** the `Font` and `FontBold` sprites have one white costume per printable ASCII character named `ch_<char>` (`ch_A`, `ch_a`, `ch_?`). Stamp or clone a glyph per letter with `switch costume to (join "ch_" (letter (i) of (text)))`, then advance x by the costume width plus 1 art pixel (2 stage units). Costume names are case-sensitive, which also tells uppercase from lowercase. Tint with the color effect.

**Bars and counters:** HUD costumes are pre-baked by level: `hp_00` to `hp_10`, `heat_00` to `heat_16` (+ `heat_max_flash`), `integrity_00` to `integrity_16`, `enemy_int_0` to `enemy_int_8`, `boss_00` to `boss_20`, `dash_0` to `dash_2`, `gourd_0` to `gourd_5`, and `tool_*`. Use `switch costume to (join "hp_" (hp))`, padding with a leading zero where the name has one.

**Parallax:** `Parallax_far` and `Parallax_mid` have one costume per chapter and tile horizontally (240 wide). Use two clones per layer offset by 480 stage units and scroll far at about 0.25× and mid at 0.5× camera speed. Sky gradients are stage backdrops (`sky_<chapter>`). `Rain` is a 4-frame full-screen overlay.

**Tiles:** `Tiles_<material>` sprites have one costume per tile, centered (4, 4), so a tile at grid (col, row) goes to x = -236 + 16 × col, y = 172 - 16 × row.

## Tile autotiling

Pick the tile by which of the 4 neighbors are solid (up, down, left, right):

| Up | Down | Left | Right | Tile |
|---|---|---|---|---|
| no | yes | no | yes | `top_left` |
| no | yes | yes | yes | `top` |
| no | yes | yes | no | `top_right` |
| yes | yes | no | yes | `left` |
| yes | yes | yes | yes | `center` (or `inner_tl`/`inner_tr` when the diagonal above is open) |
| yes | yes | yes | no | `right` |
| yes | no | no | yes | `bottom_left` |
| yes | no | yes | yes | `bottom` |
| yes | no | yes | no | `bottom_right` |
| no | yes | no | no | `col_top` (then `col_mid`, `col_bottom`) |
| no | no | any | any | `single`, `row_l`, `row_m`, `row_r` |

One-way platforms are `plat_l`, `plat_m`, `plat_r`, and `plat_single`. Hazards: `spikes_up`, `spikes_down`, and `electro_0` to `electro_3` (animated). Decor: pipes, neon trims, vents, grates, windows, ladders, and breakable blocks.

## Animation reference

| Sprite | Animations (frames @ fps) |
|---|---|
| Hotaru | idle (4 @ 6), run (8 @ 12), jump (5 @ 10), land (2 @ 12), wall_cling (2 @ 6), dash (4 @ 16), attack1 (4 @ 14), attack2 (4 @ 14), attack3 (4 @ 14), attack4 (5 @ 14), air_attack (4 @ 14), launcher (4 @ 14), plunge (3 @ 12), heavy (6 @ 10), deflect (3 @ 14), block (1 @ 1), hurt (2 @ 10), overheat (4 @ 6), heal (6 @ 8), death (6 @ 8), throw (3 @ 14), severance (5 @ 12) |
| Mukuro | idle (4 @ 6), run (8 @ 12), jump (5 @ 10), dash (4 @ 16), attack1 (4 @ 14), attack2 (4 @ 14), attack3 (4 @ 14), heavy (6 @ 10), deflect (3 @ 14), block (1 @ 1), hurt (2 @ 10), overheat (4 @ 6), death (6 @ 8) |
| Kuro | idle (4 @ 6), run (8 @ 12), jump (5 @ 10), dash (4 @ 16), attack1 (4 @ 14), attack2 (4 @ 14), attack3 (4 @ 14), heavy (6 @ 10), deflect (3 @ 14), block (1 @ 1), hurt (2 @ 10), overheat (4 @ 6), death (6 @ 8) |
| HannyaBoy | idle (4 @ 5), walk (6 @ 8), attack (6 @ 10), hurt (2 @ 10), death (5 @ 8) |
| BigOni | idle (4 @ 5), walk (6 @ 6), slam (8 @ 10), stagger (3 @ 6), death (6 @ 6) |
| Tetsu | idle (4 @ 5), talk (4 @ 6) |
| DaiCam | idle (4 @ 6), wave (4 @ 8), panic (4 @ 10) |
| CamDrone | hover (4 @ 10) |
| ScavDrone | hover (4 @ 10), charge (4 @ 12), explode (6 @ 14) |
| Turret | idle (4 @ 4), charge (3 @ 10), fire (2 @ 14) |
| ShrineTerminal | idle (4 @ 5), active (4 @ 8) |
| MemoryShard | spin (6 @ 10) |
| NeonSign_Ramen | flicker (8 @ 8), on (1 @ 1), off (1 @ 1) |
| NeonSign_Ninja | flicker (8 @ 8), on (1 @ 1), off (1 @ 1) |
| NeonSign_Bar | flicker (8 @ 8), on (1 @ 1), off (1 @ 1) |
| NeonSign_Danger | flicker (8 @ 8), on (1 @ 1), off (1 @ 1) |
| LaserBarrier | on (4 @ 12), off (1 @ 1) |
| Crate | intact (1 @ 1), cracked (1 @ 1), break (3 @ 12) |
| ShockPuddle | spark (4 @ 12) |
| MovingPlatform | hover (2 @ 10) |
| SecurityDoor | closed (1 @ 1), open (5 @ 14) |
| RamenCart | idle (4 @ 6) |
| Lantern | sway (4 @ 4) |
| ServerRack | blink (4 @ 6) |
| SlashFX | slash1 (4 @ 14), slash2 (4 @ 14), thrust (4 @ 14), finisher (4 @ 14), air (4 @ 14), launcher (4 @ 14), heavy (4 @ 12), mukuro (4 @ 14) |
| CombatFX | deflect (5 @ 16), hit (4 @ 16), hit_enemy (4 @ 16), breach (4 @ 8), severance (2 @ 4), explosion (5 @ 14), shockwave (5 @ 12), heal (6 @ 10), steam (4 @ 8), sync (6 @ 12) |
| MoveFX | run_dust (4 @ 12), land_dust (4 @ 12), wall_spark (3 @ 12), afterimage (2 @ 1), rain_splash (3 @ 12) |
| Projectiles | shuriken (4 @ 16), bullet (2 @ 8) |

## Notes

The sprites are generated from code in a consistent style, so recoloring is a palette swap: replace colors exactly (no anti-aliasing anywhere). All art is original to this pack.
