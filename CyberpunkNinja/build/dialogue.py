"""
Conversations for the vertical slice. Each line is (speaker, portrait, text).
Speaker keys pick the name plate; long lines are wrapped and split into
3-line pages automatically when the text costumes are rendered.
"""

NAMEPLATE = {
    'hotaru': 'name_hotaru', 'kuro': 'name_kuro', 'tetsu': 'name_tetsu',
    'daicam': 'name_daicam', 'unknown': 'name_unknown',
}

CONVERSATIONS = {
    'boot': [
        ('unknown', 'kuro_smirk', "Good. You're awake. Try not to die before I figure out whose body this is."),
        ('hotaru', 'hotaru_neutral', "Mine."),
        ('unknown', 'kuro_smirk', "We'll see."),
        ('hotaru', 'hotaru_angry', "Who's talking? Where are you?"),
        ('kuro', 'kuro_neutral', "In your head, apparently. Call me Kuro. Somebody filed my combat engram under 'scrap'. Same as you."),
        ('kuro', 'kuro_smirk', "Legs work? Good. The Spire's that way. Up. Everything worth knowing is up."),
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
        ('kuro', 'kuro_neutral', "Everything up here is Kanshi. Keep his shuriken pouch. You'll need it where we're going."),
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
}

# Tutorial prompts: list of segments. ('k', costume) = key icon, ('t', text) = label.
HINTS = {
    'move': [('k', 'key_left'), ('k', 'key_right'), ('t', 'Run'), ('g',), ('k', 'key_up'), ('t', 'Jump (hold to jump higher)')],
    'jump': [('k', 'key_down'), ('t', '+'), ('k', 'key_up'), ('t', 'Drop through thin platforms')],
    'cling': [('t', 'Jump into a wall to cling to it'), ('n',), ('k', 'key_up'), ('t', 'while clinging: wall jump')],
    'attack': [('k', 'mouse_l'), ('t', '/'), ('k', 'key_x'), ('t', 'Attack'), ('n',), ('t', 'Keep pressing to chain a 4-hit combo')],
    'deflect': [('k', 'key_down'), ('t', 'Deflect right before a hit lands'), ('n',), ('t', 'Hold to block (blocking builds Heat)')],
    'dash': [('k', 'key_space'), ('t', 'Phase Step: an invincible dash'), ('n',), ('t', 'Passes through lasers and attacks')],
    'talk': [('k', 'key_e'), ('t', 'Talk')],
    'heal': [('k', 'key_r'), ('t', 'Drink from the Nano-Gourd'), ('n',), ('k', 'key_e'), ('t', 'Rest at a Shrine to refill everything')],
    'integrity': [('t', "Fill an enemy's INTEGRITY bar,"), ('n',), ('t', 'then'), ('k', 'mouse_l'), ('t', 'near the red reticle to SEVER')],
    'heavy': [('k', 'key_space'), ('t', 'then'), ('k', 'mouse_l'), ('t', 'Heavy Strike'), ('n',), ('t', 'Breaks guards. Big Integrity damage')],
    'breach': [('t', 'Red diamond = BREACH attack'), ('n',), ('t', "Can't block it:"), ('k', 'key_space'), ('t', 'Phase Step through')],
    'launch': [('k', 'key_up'), ('t', '+'), ('k', 'mouse_l'), ('t', 'Launcher'), ('n',), ('k', 'key_down'), ('t', '+'), ('k', 'mouse_l'), ('t', 'in the air: Plunge')],
    'tool': [('k', 'key_q'), ('t', 'Throw a shuriken (refills at Shrines)')],
    'upgrade': [('t', 'SHURIKEN POUCH UPGRADED: 5 uses')],
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
    ('t', 'Prologue + Chapter 1 vertical slice'),
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
    ('t', 'the Hannya Boys and Big Oni'),
    ('s', ''),
    ('t', 'Thanks for playing!'),
]

CONTROLS = [
    ('b', 'CONTROLS'),
    ('c', 'Move', 'Arrows  or  A / D'),
    ('c', 'Jump (hold: higher)', 'Up  or  W'),
    ('c', 'Drop through', 'Hold Down + Up'),
    ('c', 'Attack (combo)', 'Click  or  X / J'),
    ('c', 'Launcher / Plunge', 'Up / Down + attack'),
    ('c', 'Phase Step (dash)', 'Space  or  Z / K'),
    ('c', 'Heavy Strike', 'Phase Step + attack'),
    ('c', 'Deflect / block', 'Down  or  S / L'),
    ('c', 'Heal', 'R'),
    ('c', 'Shuriken', 'Q'),
    ('c', 'Talk / Shrine / next', 'E  or  Enter'),
    ('c', 'Pause', 'P'),
    ('n', "(Scratch can't read Shift or Esc)"),
]

END_PAGE = [
    ('b', 'END OF CHAPTER 1'),
    ('t', 'NEON ALLEY'),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('s', ''),
    ('t', "Hotaru's climb continues in"),
    ('t', 'Chapter 2: The Pachinko Vaults.'),
    ('t', 'Thanks for playing this vertical slice!'),
]
