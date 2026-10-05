"""
Conversations for the vertical slice. Each line is (speaker, portrait, text).
Speaker keys pick the name plate; long lines are wrapped and split into
3-line pages automatically when the text costumes are rendered.
"""

NAMEPLATE = {
    'hotaru': 'name_hotaru', 'kuro': 'name_kuro', 'tetsu': 'name_tetsu',
    'daicam': 'name_daicam', 'unknown': 'name_unknown', 'luck': 'name_lady_luck', 'system': 'name_system',
}

CONVERSATIONS = {
    'boot0': [
        ('system', 'sys_boot', "KANSHI DYNAMICS // SHINOBI UNIT. Status: DECOMMISSIONED. Dumped in Sump Scrapyard 9."),
        ('system', 'sys_boot', "Emergency reboot... Motor control: OK. Visor: OK. Memory index: NOT FOUND."),
    ],
    'boot': [
        ('hotaru', 'hotaru_neutral', "...Rain. Cold. Scrap metal everywhere. Where am I?"),
        ('hotaru', 'hotaru_neutral', "My name is Hotaru. I know that much. Everything before tonight is just... static."),
        ('unknown', 'kuro_smirk', "Good. You're awake. Try not to die before I figure out whose body this is."),
        ('hotaru', 'hotaru_neutral', "Mine."),
        ('unknown', 'kuro_smirk', "We'll see."),
        ('hotaru', 'hotaru_angry', "Who said that? There's no one here."),
        ('kuro', 'kuro_neutral', "Not out there. In here. I'm wired into your combat software. A voice in your audio feed."),
        ('hotaru', 'hotaru_angry', "And the purple ghost flickering at the edge of my visor?"),
        ('kuro', 'kuro_smirk', "Also me. Call me Kuro. Somebody filed my engram under 'scrap'. Same as you."),
        ('hotaru', 'hotaru_visor_up', "I'm not scrap. I'm a person. Somebody rebuilt me with chrome, that's all."),
        ('kuro', 'kuro_neutral', "Then let's find out who. See that tower? The Kanshi Spire. Sump to sky, Kanshi owns it all."),
        ('kuro', 'kuro_smirk', "Whatever they took out of your head is up there. So are my answers. Up it is."),
    ],
    'drones': [
        ('kuro', 'kuro_neutral', "Scavenger drones. They strip anything that stops moving."),
        ('kuro', 'kuro_smirk', "So don't stop moving. Cut them down before they dive."),
    ],
    'turret': [
        ('kuro', 'kuro_neutral', "Wall turret. You can't reach it from here."),
        ('kuro', 'kuro_smirk', "Catch the round on your blade at the last instant and send it home."),
    ],
    'barrier': [
        ('kuro', 'kuro_neutral', "Kanshi laser fence. Solid to meat. But you're not all meat, are you?"),
        ('hotaru', 'hotaru_angry', "I'm human."),
        ('kuro', 'kuro_smirk', "Sure. Phase through it anyway."),
    ],
    'tetsu': [
        ('tetsu', 'tetsu_neutral', "Well, look what the storm dragged in."),
        ('tetsu', 'tetsu_neutral', "Gourd's topped up, kid. Same price as always: you come back down here in one piece."),
        ('hotaru', 'hotaru_neutral', "I've never been here before."),
        ('tetsu', 'tetsu_neutral', "Sure you haven't."),
        ('tetsu', 'tetsu_neutral', "That vending machine's a Shrine. Hacked it myself. Rest there and it'll remember you, even if the Spire won't."),
        ('kuro', 'kuro_smirk', "Nice old man. He's lying about something."),
        ('hotaru', 'hotaru_visor_up', "So are you."),
    ],
    'tetsu2': [
        ('tetsu', 'tetsu_neutral', "Freight lift's past the scrap drones. Ride it up to Neon Alley."),
        ('tetsu', 'tetsu_neutral', "And kid... eat something when you get back."),
    ],
    'lift': [
        ('kuro', 'kuro_neutral', "Freight lift to the market tiers. Step on and ride it up."),
        ('hotaru', 'hotaru_neutral', "And then?"),
        ('kuro', 'kuro_smirk', "Then we keep climbing until somebody tells us the truth."),
    ],
    'ch1': [
        ('kuro', 'kuro_neutral', "Neon Alley. The Hannya Boys run these floors. Oni masks, steel pipes, bad manners."),
        ('hotaru', 'hotaru_neutral', "They'll move."),
        ('kuro', 'kuro_smirk', "Ha. Now you sound like me."),
    ],
    'integrity': [
        ('kuro', 'kuro_neutral', "See the bar over his head? That's his Integrity."),
        ('kuro', 'kuro_neutral', "Deflect his swings and hit him hard. When he cracks, a reticle shows. Click it and finish him."),
    ],
    'daicam1': [
        ('daicam', 'daicam_neutral', "Okay chat, okay, this is fine. This is content."),
        ('daicam', 'daicam_neutral', "Guys? Guys, we can talk about this! I have a very large audience!"),
        ('kuro', 'kuro_smirk', "Let's give him something to film."),
    ],
    'daicam2': [
        ('daicam', 'daicam_neutral', "Chat, we have a NINJA. Say hi to the chat."),
        ('daicam', 'daicam_neutral', "Okay, she's not saying hi. Chat, she's walking away."),
        ('hotaru', 'hotaru_neutral', "Get off this floor. It isn't safe."),
        ('daicam', 'daicam_neutral', "Nothing about the Spire is safe! That's the brand! Smash that follow, ninja lady!"),
    ],
    'breach': [
        ('kuro', 'kuro_neutral', "That one's got a red diamond over him. That's a Breach."),
        ('kuro', 'kuro_neutral', "You can't block it and you can't deflect it. Phase Step straight through him."),
    ],
    'ambush': [
        ('kuro', 'kuro_neutral', "Three of them, and they've locked the doors. Use the platforms. Don't get surrounded."),
    ],
    'boss_gate': [
        ('kuro', 'kuro_neutral', "Big one up ahead. Slow, though."),
        ('kuro', 'kuro_neutral', "When he lifts that club over his head, you hit him hard or you get out of the way."),
        ('hotaru', 'hotaru_neutral', "Hit him hard. Got it."),
        ('kuro', 'kuro_smirk', "Rest at the Shrine first. I'd hate to lose this body. I'm just getting used to it."),
    ],
    'oni': [
        ('kuro', 'kuro_neutral', "That's the gang boss. Big Oni. Deflect the club swings."),
        ('kuro', 'kuro_neutral', "Heavy Strikes stagger him: Phase Step, then attack. Fill his Integrity and sever him."),
    ],
    'oni2': [
        ('kuro', 'kuro_neutral', "He's angry now. Watch the overhead slam. It's a Breach, and it shakes the whole roof."),
        ('kuro', 'kuro_smirk', "Jump the shockwave or phase through it."),
    ],
    'oni_dead': [
        ('kuro', 'kuro_smirk', "Ha! Severed. The Hannya Boys will be telling that story for years."),
        ('hotaru', 'hotaru_visor_up', "He had a Kanshi chip in his neck. Same as the drones."),
        ('kuro', 'kuro_neutral', "Everything up here is Kanshi. And everything up here bleeds. Keep climbing."),
        ('hotaru', 'hotaru_neutral', "Kuro. Whose memories are these? The fighting. The way my hands know where to go."),
        ('kuro', 'kuro_neutral', "Mine. I think. Ask me again at the top."),
        ('daicam', 'daicam_neutral', "...and CUT. Chat, did everybody clip that?! Ninja lady just took down Big Oni! We're trending!"),
    ],
    'shard1': [
        ('kuro', 'kuro_neutral', "...A courtyard. Rain on a tiled roof. Someone is teaching me to hold a blade."),
        ('kuro', 'kuro_neutral', "A woman. She's laughing at me."),
        ('hotaru', 'hotaru_visor_up', "That's your memory?"),
        ('kuro', 'kuro_smirk', "It was. Now it's ours, I suppose."),
    ],
    'shard2': [
        ('kuro', 'kuro_neutral', "...An office at the top of the Spire. The Daimyo, before he was a machine."),
        ('kuro', 'kuro_neutral', "He's shaking my hand. Thanking me for my service."),
        ('kuro', 'kuro_neutral', "Then the lights go out."),
        ('hotaru', 'hotaru_angry', "He did this to you."),
        ('kuro', 'kuro_neutral', "To us. Keep climbing."),
    ],
    'ch2': [
        ('kuro', 'kuro_neutral', "The Pachinko Vaults. Every floor up here is a casino, and the house always wins."),
        ('hotaru', 'hotaru_neutral', "Then we don't play."),
        ('kuro', 'kuro_smirk', "Everybody plays. The lasers decide when."),
    ],
    'lasers': [
        ('kuro', 'kuro_neutral', "Laser grid. It pulses on and off, and Kanshi stations dealers behind it."),
        ('kuro', 'kuro_neutral', "Wait for a gap, or Phase Step straight through it. Mid-fight, if you have to."),
    ],
    'slots': [
        ('kuro', 'kuro_neutral', "Slot turrets. Three card-blades at a time."),
        ('kuro', 'kuro_smirk', "Deflect the one coming at you and it goes straight back to whoever threw it."),
    ],
    'rollers': [
        ('kuro', 'kuro_neutral', "High rollers' lounge. The dealers here throw from the balconies. Get up there with them."),
    ],
    'daicam3': [
        ('daicam', 'daicam_neutral', "Chat, I am currently being held as collateral. My debt is... unclear."),
        ('daicam', 'daicam_neutral', "Ninja lady! You came back for me! For the content!"),
        ('hotaru', 'hotaru_neutral', "I came for the elevator."),
        ('daicam', 'daicam_neutral', "Same thing! Hit the cage! Hit it with the sword!"),
    ],
    'daicam3b': [
        ('daicam', 'daicam_neutral', "FREEDOM! Chat, she freed me. I'm calling this episode 'Jackpot'."),
        ('hotaru', 'hotaru_visor_up', "Stop following me."),
        ('daicam', 'daicam_neutral', "I'm not following you, I'm documenting you. Totally different. Byeee!"),
    ],
    'luck_gate': [
        ('kuro', 'kuro_neutral', "Lady Luck runs every table on this tier. The machine behind her picks her moves."),
        ('kuro', 'kuro_neutral', "Watch the reels. Spades, sevens, cherries... and if they land on skulls, get off the floor."),
        ('hotaru', 'hotaru_neutral', "And if it hits the jackpot?"),
        ('kuro', 'kuro_smirk', "Then we find out how fast you are."),
    ],
    'luck': [
        ('luck', 'luck_neutral', "A scrapped Shinobi unit at my table. The house is feeling generous tonight."),
        ('luck', 'luck_neutral', "Place your bet, little firefly. Everything you have."),
        ('hotaru', 'hotaru_angry', "Deal."),
    ],
    'luck2': [
        ('luck', 'luck_neutral', "Double or nothing!"),
        ('kuro', 'kuro_neutral', "Jackpot means lasers. Phase Step through them!"),
    ],
    'luck_dead': [
        ('luck', 'luck_neutral', "The house... doesn't... lose..."),
        ('kuro', 'kuro_smirk', "It does now."),
        ('hotaru', 'hotaru_visor_up', "Those reels weren't random. Something upstairs was picking her moves."),
        ('kuro', 'kuro_neutral', "Something upstairs is picking everybody's moves. The Server Gardens are next."),
        ('kuro', 'kuro_neutral', "Whatever runs this tower lives up there."),
        ('daicam', 'daicam_neutral', "Chat, the ninja just broke the bank. Literally. Somebody clip the reels!"),
    ],
    'shard3': [
        ('kuro', 'kuro_neutral', "...The Academy. Rows of us, practicing the same cut a thousand times."),
        ('kuro', 'kuro_neutral', "Mukuro was there, before they emptied him out."),
        ('hotaru', 'hotaru_neutral', "Mukuro?"),
        ('kuro', 'kuro_neutral', "You'll meet him. I'm sorry in advance."),
    ],
}

# Tutorial prompts: list of segments. ('k', costume) = key icon, ('t', text) = label.
HINTS = {
    'move': [('k', 'key_left'), ('k', 'key_right'), ('t', 'Run'), ('g',), ('k', 'key_up'), ('t', 'Jump (hold to jump higher)')],
    'jump': [('k', 'key_down'), ('t', '+'), ('k', 'key_space'), ('t', 'dash down through platforms')],
    'cling': [('t', 'Jump into a wall to cling to it'), ('n',), ('k', 'key_up'), ('t', 'while clinging: wall jump')],
    'attack': [('k', 'mouse_l'), ('t', '/'), ('k', 'key_x'), ('t', 'Attack'), ('n',), ('t', 'Keep pressing to chain a 4-hit combo')],
    'deflect': [('k', 'key_down'), ('t', 'Deflect right before a hit lands'), ('n',), ('t', 'Hold to block (blocking builds Heat)')],
    'dash': [('k', 'key_space'), ('t', 'Phase Step: an invincible dash'), ('n',), ('t', 'Passes through lasers and attacks')],
    'talk': [('k', 'key_e'), ('t', 'Talk')],
    'heal': [('k', 'key_r'), ('t', 'Drink from the Nano-Gourd'), ('n',), ('k', 'key_e'), ('t', 'Rest at a Shrine to refill everything')],
    'integrity': [('t', "Fill an enemy's INTEGRITY bar,"), ('n',), ('t', 'then'), ('k', 'mouse_l'), ('t', 'near the red reticle to SEVER')],
    'heavy': [('k', 'key_space'), ('t', 'then'), ('k', 'mouse_l'), ('t', 'Heavy Strike'), ('n',), ('t', 'Breaks guards. Big Integrity damage')],
    'breach': [('t', 'Red diamond = BREACH attack'), ('n',), ('t', "Can't block it:"), ('k', 'key_space'), ('t', 'Phase Step through')],
    'launch': [('k', 'key_up'), ('t', '+'), ('k', 'mouse_l'), ('t', 'Launcher: pops enemies into the air')],
    'upgrade': [('t', 'NANO-GOURD UPGRADED: now holds 4 charges')],
    'lasergrid': [('t', 'Laser grids pulse on and off.'), ('n',), ('t', 'Wait for a gap, or'), ('k', 'key_space'), ('t', 'Phase Step through')],
    'cards': [('k', 'key_down'), ('t', 'Deflect a card-blade to send it back'), ('n',), ('t', 'Returned cards hurt and crack Integrity')],
    'cage': [('k', 'mouse_l'), ('t', 'Attack the cage to free DaiCam')],
    'reels': [('t', 'Watch the reels: they pick her next move.'), ('n',), ('t', 'SKULL = Breach.  JACKPOT = lasers')],
}

OPTION_LABELS = {
    'wide': 'Wide deflect window',
    'slow': 'Slower game speed',
    'heat': 'Slower Heat buildup',
    'gourd': 'Infinite Nano-Gourd',
    'god': 'Invincibility',
    'music': 'Music volume',
    'sfx': 'Sound volume',
    'shake': 'Screen shake',
    'controls': 'Controls',
}

CREDITS = [
    ('b', 'CYBERPUNK NINJA'),
    ('t', 'Prologue, Chapter 1 and Chapter 2'),
    ('s', ''),
    ('h', 'GAME DESIGN BRIEF & ART'),
    ('t', 'Cyberpunk Ninja asset pack'),
    ('t', 'Pixel art, Shinobi Mono font, palette'),
    ('s', ''),
    ('h', 'SCRATCH BUILD, MUSIC & SOUND'),
    ('t', 'Generated with Claude Code'),
    ('t', 'Synthwave, shamisen & taiko synthesized from scratch'),
    ('s', ''),
    ('h', 'STARRING'),
    ('t', 'Hotaru, Kuro, Tetsu, DaiCam,'),
    ('t', 'the Hannya Boys, Big Oni and Lady Luck'),
    ('s', ''),
    ('t', 'Thanks for playing!'),
]

CONTROLS = [
    ('b', 'CONTROLS'),
    ('c', 'Move', 'Arrows  or  A / D'),
    ('c', 'Jump (hold: higher)', 'Up  or  W'),
    ('c', 'Through platforms', 'Phase Step up / down'),
    ('c', 'Attack (combo)', 'Click  or  X / J'),
    ('c', 'Launcher', 'Up + attack'),
    ('c', 'Phase Step (dash)', 'Space  or  Z / K'),
    ('c', 'Heavy Strike', 'Phase Step + attack'),
    ('c', 'Deflect / block', 'Down  or  S / L'),
    ('c', 'Heal', 'R'),
    ('c', 'Talk / Shrine / next', 'E  or  Enter'),
    ('c', 'Pause', 'P'),
    ('n', "(Scratch can't read Shift or Esc)"),
]

END_PAGE = [
    ('b', 'END OF CHAPTER 2'),
    ('t', 'THE PACHINKO VAULTS'),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('t', "Hotaru's climb continues in"),
    ('t', 'Chapter 3: The Server Gardens.'),
    ('t', 'Thanks for playing this vertical slice!'),
]
