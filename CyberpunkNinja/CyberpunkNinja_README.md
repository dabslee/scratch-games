# Cyberpunk Ninja

## Instructions
Click the green flag, press any key at the title screen, and choose "New Game" (or pick a chapter from "Chapters"). Hotaru, a decommissioned cyborg shinobi, reboots in a scrapyard in the Sump beneath the Kanshi Spire with no memory of anything before tonight. The only other voice is Kuro, a ninja's engram wired into her combat software, who speaks through her audio feed and flickers at the edge of her visor as a violet glitch. Climb the Spire for answers through the Prologue, Chapter 1: Neon Alley (boss: Big Oni of the Hannya Boys), Chapter 2: The Pachinko Vaults (boss: Lady Luck) Chapter 3: The Server Gardens (boss: Mukuro, a copy of Kuro) Chapter 4: Monorail Ascent (boss: Raijin, an armored locomotive), Chapter 5: Hollow Floor (boss: Kuro himself, inside Hotaru's head), Chapter 6: The Academy (boss: Mukuro II) and Chapter 7: The Tenshu (final boss: the Daimyo), followed by the epilogue.

CONTROLS:
- Arrow keys or A / D to run. Up or W to jump (hold for a higher jump). Jump into a wall to cling to it, then jump again to wall jump. Thin platforms can be jumped up through. To drop down through one, double-tap Down or Phase Step downward (Down + Space).
- Left click (or X / J) to attack. Keep pressing to chain a 4-hit combo. Up + attack is a rising Launcher.
- Space (or Z / K) to Phase Step: an invincible dash that passes through lasers and attacks. Hold the arrow keys to aim it, including diagonals and downward. You have 2 charges, shown by the color of Hotaru's scarf and the pips under her health bar; they refill when you land or perfectly deflect.
- Attack during or right after a Phase Step for a Heavy Strike, which breaks guards and deals big Integrity damage.
- Down (or S / L) to deflect right before a hit lands. Hold it to block, but blocking builds Heat (the bar at the bottom). If Heat fills up, Hotaru overheats and is defenseless for a moment. Press Up to jump out of a block, or Space to dash out of it.
- R to drink from the Nano-Gourd and heal. E to talk and to rest at Shrine Terminals. E, Enter or Space advances dialogue. P to pause.
- Scratch can't detect the Shift or Esc keys, so Phase Step is on Space and Pause is on P.

TIPS:
- Enemies flash white just before an attack lands: that's the moment to deflect.
- Deflects and Heavy Strikes fill an enemy's Integrity bar. When it's full, a red reticle appears: attack near it to perform a Severance. Regular enemies die instantly, and bosses lose a whole health segment.
- A red diamond over an enemy means a Breach attack, which can't be blocked or deflected. Phase Step through it (or jump over Big Oni's shockwave).
- Shrine Terminals (the hacked vending machines) heal you, refill your gourd, and become your respawn point.
- In The Vaults, laser grids pulse on and off and flicker just before they switch on. Wait for a gap or Phase Step through them.
- Lady Luck's slot machine decides her next attack. When the reels stop, the machine names the move ("CARD FAN!", "SHOCKWAVE!", "LASERS!"...).
- In the Server Gardens, step into the cooling mist to ride the updraft upward, steering left and right as you rise. Some vents pulse, so ride them while the mist is thick.
- Garden Wardens guard your normal attacks and counter if you keep swinging into their guard. Deflect their strikes (or Heavy Strike them) to break their Integrity, then attack while they recover.
- On the monorail roofs a headwind pushes you back, harder in the air. Gaps between cars are bottomless, but the couplers below can catch you. Watch the right edge of the screen for a warning sign: a signal post is about to sweep the roof, so jump it, Phase Step through it, or stand on a raised deck.
- Raijin's reactor core is shuttered except while it vents steam. Deflect its cannon shells to send them straight back into the core, deflect (or jump) its pantograph arm, step off roof sections that spark before they go live, and when you hear the horn in phase 2, jump the plow it drags across the roof.
- In Hollow Floor, glitch blocks phase in and out: one set is solid while the other is gone, and they flicker just before they swap. When the screen edges turn purple, Kuro has your controls and left and right are swapped (deflect and Phase Step still work).
- Kuro fights with your own moves: your 4-hit string, blink strikes from behind, and a Breach Phase Cut. When he Phase Cuts at you, Phase Step straight through him at the same moment to Clash, which breaks his posture and leaves him open.
- Academy Shells dash in and throw kunai (deflect them back). The Academy's training holograms phase like the glitch blocks.
- Mukuro II adds a kunai fan, a diving slam that sends shockwaves along the floor (jump them), and a shadow that strikes from behind you. When his last segment breaks, you choose: attack to destroy him, or press E to sever his loyalty protocol and set him free.
- The Daimyo fights in three forms. His samurai exoskeleton swings a nodachi: deflect the iaido draw and the 3-slash strings, jump the stomp's shockwaves, and Phase Step through the thruster charge. The castle's defense AI hangs out of reach, so deflect its bullet barrages back into it and strike when it descends. Finally his engram flies free: deflect the orbs, dodge the swoop, and strike while Kuro holds the mask down.
- Mukuro duels like Kuro: he guards everything except right after his combos. Deflect each strike to fill his Integrity, punish the openings with two or three hits (greed gets countered), and watch for held strikes in phase 2.
- Eight hidden Memory Shards unlock fragments of Kuro's past. One is up through the ceiling of the Gauntlet, one is behind a breakable ceiling in the Ambush room, one is in a back room above the High Rollers floor in The Vaults, one is at the top of the pulsing updraft in the Cooling Tower, one is in the Maintenance Bay behind the door in the Spiral Junction's tower wall, one is in the Locked Memory above the Possession room, one is in the Instructor's Loft above the Sparring Ring, and one is in the Daimyo's Study above the Defense Grid.
- Options include Assist Mode toggles (wider deflect window, slower game speed, slower Heat buildup, infinite gourd, invincibility), music and sound volume, and screen shake.

## Notes and Credits
The complete "Cyberpunk Ninja": the Prologue, all seven chapters and the epilogue, built from its game design brief. All art and the Shinobi Mono font come from the Cyberpunk Ninja asset pack. The music (synthwave with shamisen and taiko) and all sound effects were synthesized from scratch for this project.

The project is generated by the scripts in `build/`: game logic is written in a Python-syntax mini-language and compiled to Scratch 3 blocks, rooms are rendered from the pack's tilesets, and the audio is synthesized with numpy. To rebuild, run `CN_PACK=/path/to/CyberpunkNinja_AssetPack python3 build/build.py` (needs Pillow, numpy, scipy and ffmpeg).
