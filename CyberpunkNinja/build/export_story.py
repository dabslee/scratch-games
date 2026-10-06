"""
Export the full story (every conversation in play order), the boss roster and
a summary of the mechanics to ../story.json. Dialogue text comes straight
from dialogue.py, so the export always matches the game.

    python3 build/export_story.py
"""
import json
import os

import dialogue
import levels

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'story.json')

SPEAKERS = {
    'hotaru': 'Hotaru', 'kuro': 'Kuro', 'tetsu': 'Tetsu', 'daicam': 'DaiCam', 'unknown': '???',
    'luck': 'Lady Luck', 'system': 'System', 'mukuro': 'Mukuro', 'daimyo': 'The Daimyo',
}
# who is really talking when the name plate reads "???"
PORTRAIT_OWNER = {'kuro': 'Kuro', 'mukuro': 'Mukuro', 'daimyo': 'The Daimyo'}

ROOMS = {r.key: r.title for r in levels.ROOMS}

# (conversation, room, trigger, optional/condition)
SCENES = {
    'prologue': [
        ('boot0', 'p1', 'Game start: system boot log', None),
        ('boot', 'p1', 'Game start', None),
        ('drones', 'p3', 'First scavenger drones', None),
        ('turret', 'p4', 'First wall turret', None),
        ('barrier', 'p5', 'First laser fence', None),
        ('tetsu', 'p6', 'Talk to Tetsu (E)', None),
        ('tetsu2', 'p6', 'Talk to Tetsu again', 'optional'),
        ('shard1', 'p7s', 'Memory Shard 1 (hidden above the Gauntlet)', 'optional'),
        ('lift', 'p8', 'Reach the freight lift', None),
    ],
    'ch1': [
        ('ch1', 'a1', 'Chapter start', None),
        ('integrity', 'a2', 'First Hannya Boy', None),
        ('daicam1', 'a4', 'DaiCam cornered by gang members', None),
        ('daicam2', 'a4', 'After saving DaiCam', None),
        ('breach', 'a5', 'First Breach attacker', None),
        ('ambush', 'a7', 'Doors lock: three-enemy ambush', None),
        ('shard2', 'a8', 'Memory Shard 2 (behind a breakable ceiling in the Ambush room)', 'optional'),
        ('boss_gate', 'a9', 'Before the boss arena', None),
        ('oni', 'a10', 'Boss fight starts', None),
        ('oni2', 'a10', 'Boss phase 2', None),
        ('oni_dead', 'a10', 'Big Oni defeated', None),
    ],
    'ch2': [
        ('ch2', 'b1', 'Chapter start', None),
        ('lasers', 'b2', 'First laser grid', None),
        ('slots', 'b3', 'First slot turrets', None),
        ('rollers', 'b5', 'Dealers on the balconies', None),
        ('shard3', 'b5s', 'Memory Shard 3 (back room above the High Rollers floor)', 'optional'),
        ('daicam3', 'b6', 'DaiCam caged as collateral', None),
        ('daicam3b', 'b6', 'After breaking the cage', None),
        ('luck_gate', 'b7', 'Before the boss arena', None),
        ('luck', 'b8', 'Boss fight starts', None),
        ('luck2', 'b8', 'Boss phase 2', None),
        ('luck_dead', 'b8', 'Lady Luck defeated', None),
    ],
    'ch3': [
        ('ch3', 'c1', 'Chapter start', None),
        ('mist', 'c2', 'First coolant updraft', None),
        ('racks', 'c3', 'The engram racks', None),
        ('warden', 'c3', 'First Garden Warden', None),
        ('shard4', 'c5s', 'Memory Shard 4 (top of the pulsing updraft in the Cooling Tower)', 'optional'),
        ('daicam4', 'c6', 'DaiCam stuck hovering in the mist', None),
        ('daicam4b', 'c6', 'After clearing the Wardens', None),
        ('muk_gate', 'c7', 'Before the boss arena', None),
        ('mukuro', 'c8', 'Boss fight starts', None),
        ('mukuro2', 'c8', 'Boss phase 2', None),
        ('muk_dead', 'c8', 'Mukuro defeated', None),
        ('muk_gone', 'c8', 'Mukuro vanishes', None),
    ],
    'ch4': [
        ('ch4', 'd1', 'Chapter start', None),
        ('wind', 'd2', 'First headwind on the train roof', None),
        ('posts', 'd3', 'Signal posts ahead', None),
        ('junction', 'd4', 'The track splits', None),
        ('shard5', 'd5s', "Memory Shard 5 (Maintenance Bay behind the Spiral Junction's tower door)", 'optional'),
        ('daicam5', 'd6', 'DaiCam in the dining car with Kanshi guards', None),
        ('daicam5b', 'd6', 'After clearing the guards', None),
        ('raijin_gate', 'd7', 'Something approaches on the other track', None),
        ('raijin', 'd8', 'Boss fight starts', None),
        ('raijin2', 'd8', 'Boss phase 2', None),
        ('raijin_dead', 'd8', 'Raijin defeated', None),
        ('record', 'd8', "The black box: Hotaru's manufacturing record", None),
    ],
    'ch5': [
        ('ch5', 'e1', 'Chapter start (inside Hotaru\'s head)', None),
        ('glitch', 'e1', 'First glitch blocks', None),
        ('sump_mem', 'e2', 'Memory of the Sump', None),
        ('tetsu_mem', 'e3', 'Memory of young Tetsu', None),
        ('possess', 'e5', 'Kuro takes the controls for the first time', None),
        ('shard6', 'e5s', 'Memory Shard 6 (Locked Memory above the Possession room)', 'optional'),
        ('white_room', 'e6', 'The room where Kuro was uploaded', None),
        ('daicam6', 'e6', 'A memory of DaiCam', None),
        ('kuro_gate', 'e7', 'Before the boss arena', None),
        ('kuro_fight', 'e8', 'Boss fight starts', None),
        ('kuro2', 'e8', 'Boss phase 2', None),
        ('kuro_dead', 'e8', 'Kuro defeated', None),
    ],
    'ch6': [
        ('ch6', 'f1', 'Chapter start', None),
        ('shell', 'f2', 'First Academy Shell', None),
        ('holo', 'f3', 'First training holograms', None),
        ('spar', 'f5', 'The sparring ring locks', None),
        ('shard7', 'f5s', "Memory Shard 7 (Instructor's Loft above the Sparring Ring)", 'optional'),
        ('daicam7', 'f6', 'DaiCam has enrolled', None),
        ('instances', 'f7', 'The Hall of Instances', None),
        ('muk2', 'f8', 'Boss fight starts', None),
        ('muk2b', 'f8', 'Boss phase 2', None),
        ('muk2_choice', 'f8', 'Mukuro kneels: the choice', None),
        ('muk2_freed', 'f8', 'Choice: sever his loyalty protocol (press E)', 'branch: Mukuro freed'),
        ('muk2_destroyed', 'f8', 'Choice: strike him down (attack)', 'branch: Mukuro destroyed'),
    ],
    'ch7': [
        ('ch7', 'g1', 'Chapter start', None),
        ('mukuro_ally', 'g1', 'Mukuro arrives to help', 'only if Mukuro was freed'),
        ('bailey', 'g2', 'Windy rooftops', None),
        ('grid', 'g4', 'Castle defenses', None),
        ('shard8', 'g4s', "Memory Shard 8 (the Daimyo's Study above the Defense Grid)", 'optional'),
        ('harvest', 'g5', 'The Harvest Hall', None),
        ('daicam8', 'g6', 'DaiCam streaming from the castle', None),
        ('throne', 'g7', 'At the throne room door', None),
        ('daimyo_fight', 'g8', 'Final boss starts (form 1: exoskeleton)', None),
        ('dm2', 'g8', 'Form 2: the castle defense AI', None),
        ('dm3', 'g8', 'Form 3: the Daimyo\'s engram', None),
        ('dm_pin', 'g8', 'Kuro pins the mask', None),
        ('ending', 'g8', 'The Daimyo falls', None),
        ('ending2', 'g8', 'Kuro anchors the core', None),
    ],
    'epilogue': [
        ('epilogue', 'ep', 'Back at Tetsu\'s cart, in the rain', None),
        ('ep_mukuro', 'ep', 'Mukuro is at the cart too', 'only if Mukuro was freed'),
        ('epilogue2', 'ep', 'Tetsu remembers Kuro', None),
        ('epilogue3', 'ep', "Hotaru's scarf flickers Kuro's violet for a moment", None),
    ],
}

CHAPTERS = [
    ('prologue', 'Prologue', 'Sump Scrapyard', None,
     "Hotaru reboots in a scrapyard with no memories. A voice in her combat software, Kuro, says the answers "
     "are at the top of the Kanshi Spire. Tetsu, an old noodle cook, acts like he already knows her."),
    ('ch1', 'Chapter 1', 'Neon Alley', 'Big Oni',
     "The Hannya Boys gang runs the market tiers. Hotaru meets DaiCam the livestreamer and severs the gang boss, "
     "Big Oni, who has a Kanshi chip in his neck."),
    ('ch2', 'Chapter 2', 'The Pachinko Vaults', 'Lady Luck',
     "Casino floors full of lasers and card-throwing dealers. Lady Luck's slot machine picks her moves, "
     "and Hotaru realizes something upstairs is picking everyone's moves."),
    ('ch3', 'Chapter 3', 'The Server Gardens', 'Mukuro',
     "A rooftop zen garden built on a server farm full of harvested minds (engrams). Mukuro appears: "
     "a loyal copy of Kuro with everything that ever said no stripped out."),
    ('ch4', 'Chapter 4', 'Monorail Ascent', 'Raijin',
     "Riding train roofs around the Spire. The Daimyo speaks for the first time and sends Raijin, an armored "
     "locomotive. Its black box reveals Hotaru was grown from Kuro's engram: 'Instance 3 of 3'."),
    ('ch5', 'Chapter 5', 'Hollow Floor', 'Kuro',
     "The shock breaks the wall between them. Inside Hotaru's head, among Kuro's memories, Kuro tries to take "
     "the body back. She beats him, and he agrees to ride along as a partner."),
    ('ch6', 'Chapter 6', 'The Academy', 'Mukuro II',
     "Kanshi's ninja school, where 412 empty Hotaru-shaped shells wait for a mind. Upgraded Mukuro returns; "
     "the player chooses to free him or destroy him."),
    ('ch7', 'Chapter 7', 'The Tenshu', 'The Daimyo',
     "The Daimyo's castle under a painted moon, powered by 1.2 million harvested minds. Hotaru defeats him in "
     "three forms. Kuro stays behind as the anchor that releases every mind."),
    ('epilogue', 'Epilogue', "Tetsu's Cart", None,
     "Ramen in the rain with Tetsu, DaiCam and (if freed) Mukuro. Hotaru's scarf flashes Kuro's violet: "
     "some part of him is still with her."),
]

BOSSES = {
    'Big Oni': {
        'chapter': 'ch1', 'who': 'Gang boss of the Hannya Boys, a huge brute with a club.',
        'mechanics': [
            'Slow club swings: deflect them.',
            'Heavy Strikes (Phase Step, then attack) stagger him.',
            'Phase 2 overhead slam is a Breach that sends a shockwave across the roof: jump it or Phase Step through.',
        ],
    },
    'Lady Luck': {
        'chapter': 'ch2', 'who': 'Croupier who runs every table on the Vaults tier.',
        'mechanics': [
            'A slot machine behind her picks each attack, and names it when the reels stop (CARD FAN!, SHOCKWAVE!, LASERS!...).',
            'Deflect her card-blades to send them back.',
            'SHOCKWAVE is a Breach: jump or Phase Step. Jackpot turns on laser grids: Phase Step through them.',
        ],
    },
    'Mukuro': {
        'chapter': 'ch3', 'who': "Copy two of Kuro's engram, loyalty-locked to Kanshi.",
        'mechanics': [
            'A duelist who guards everything except right after his own combos.',
            'Deflect each strike to fill his Integrity, then punish openings with two or three hits; greed gets countered.',
            'Phase 2 adds held strikes to bait early deflects.',
        ],
    },
    'Raijin': {
        'chapter': 'ch4', 'who': "The Daimyo's armored freight locomotive.",
        'mechanics': [
            'Its reactor core is shuttered except while it vents steam: strike it then.',
            'Deflect its cannon shells straight back into the core.',
            'Deflect or jump the pantograph arm; step off roof sections that spark before they go live.',
            'Phase 2: when the horn sounds, jump the plow it drags across the roof.',
        ],
    },
    'Kuro': {
        'chapter': 'ch5', 'who': "The engram in Hotaru's head, fighting for control of her body.",
        'mechanics': [
            "Uses Hotaru's own moves: the 4-hit string, blink strikes from behind, and a Breach Phase Cut.",
            'When he Phase Cuts at you, Phase Step through him at the same moment to Clash, which breaks his posture.',
            'Possession: when the screen edges turn purple, left and right are swapped.',
        ],
    },
    'Mukuro II': {
        'chapter': 'ch6', 'who': 'Mukuro, recompiled and upgraded.',
        'mechanics': [
            'Adds a kunai fan, a diving slam that sends shockwaves along the floor (jump them), and a shadow that strikes from behind.',
            'When his last segment breaks he kneels: attack to destroy him, or press E to sever his loyalty protocol and free him.',
        ],
    },
    'The Daimyo': {
        'chapter': 'ch7', 'who': "Kanshi's ruler, who uploaded Kuro and powers the Spire with stolen minds.",
        'forms': [
            {'name': 'Samurai exoskeleton', 'mechanics': 'Deflect the iaido draw and 3-slash nodachi strings, jump the stomp shockwaves, Phase Step through the thruster charge, strike while the armor recovers.'},
            {'name': 'Castle defense AI (the eye)', 'mechanics': 'Hangs out of reach: deflect its bullet barrages back into it and strike when it descends.'},
            {'name': 'Engram (the mask)', 'mechanics': 'Deflect the orbs back, dodge the swoop, and strike while Kuro holds the mask down.'},
        ],
    },
}

MECHANICS = {
    'controls': [{'action': a, 'keys': k} for t, *rest in dialogue.CONTROLS if t == 'c' for a, k in [rest]],
    'core_combat': [
        'Attack chains into a 4-hit combo; Up + attack is a rising Launcher.',
        'Phase Step (Space): an invincible, aimable dash with 2 charges (shown by the scarf color). Passes through lasers and attacks; refills on landing or a perfect deflect.',
        'Heavy Strike: attack during or right after a Phase Step. Breaks guards and deals big Integrity damage.',
        'Deflect: press Down right before a hit lands (enemies flash white just before). Holding Down blocks but builds Heat; full Heat overheats Hotaru.',
        "Integrity: deflects and Heavy Strikes fill an enemy's Integrity bar. When full, a red reticle appears: attack near it to Sever (instant kill for regular enemies, a whole health segment for bosses).",
        'Breach: a red diamond marks an attack that cannot be blocked or deflected. Phase Step through it or jump it.',
    ],
    'survival': [
        'Nano-Gourd (R) heals; upgraded to 4 charges after Big Oni.',
        'Shrine Terminals (hacked vending machines, E) heal, refill the gourd and set the respawn point.',
    ],
    'traversal': [
        'Wall cling and wall jump; jump up through thin platforms, double-tap Down (or Phase Step down) to drop through.',
        'Laser grids pulse on and off (Vaults, Castle).',
        'Coolant mist updrafts carry you upward; some vents pulse (Server Gardens).',
        'Headwind, bottomless gaps between cars, and sweeping signal posts (Monorail).',
        'Phasing blocks: two sets alternate being solid every few seconds; the incoming set lights up and turns solid just before the other vanishes (Hollow Floor, Academy).',
        'Possession: Kuro periodically swaps left and right (Hollow Floor).',
    ],
    'enemies': [
        'Scavenger drones and wall turrets (Prologue).',
        'Hannya Boys gang members (Neon Alley).',
        'Croupier dealers who throw card-blades, and slot turrets (Pachinko Vaults).',
        'Garden Wardens: guarded duelists you must deflect to break (Server Gardens).',
        'Kanshi train guards (Monorail).',
        'Memory echoes of Wardens and drones (Hollow Floor).',
        'Academy Shells: unfinished Hotaru bodies that dash in and throw kunai (Academy).',
        'Castle turrets, beams and lasers (Tenshu).',
    ],
    'collectibles': 'Eight hidden Memory Shards, one per area, each unlocking a fragment of Kuro\'s past.',
    'assist_options': [v for k, v in dialogue.OPTION_LABELS.items() if k not in ('music', 'sfx', 'shake', 'controls')],
}

CAST = {
    'Hotaru': 'A decommissioned Kanshi Shinobi unit (H-0). Grown 14 months ago from Kuro\'s engram, instance 3 of 3. Named after Kuro\'s firefly charm and an Academy rival.',
    'Kuro': 'A Sump kid and Academy-trained ninja whose mind the Daimyo uploaded. His engram rides in Hotaru\'s combat software and appears as a violet glitch.',
    'Tetsu': "Kuro's best friend, who lost an arm pulling him out of a Kanshi raid. Runs a noodle cart in the Sump.",
    'DaiCam': 'A livestreamer who keeps turning up in danger. Comic relief.',
    'Mukuro': 'Copy two of Kuro, stripped of everything that ever said no. Can be freed in Chapter 6.',
    'Lady Luck': 'Croupier and boss of the Pachinko Vaults.',
    'The Daimyo': 'Ruler of Kanshi Dynamics. Uploaded Kuro and runs the Spire on harvested minds.',
}


def lines(key):
    out = []
    for spk, portrait, text in dialogue.CONVERSATIONS[key]:
        line = {'speaker': SPEAKERS[spk], 'text': text}
        if spk == 'unknown':
            line['actually'] = PORTRAIT_OWNER[portrait.split('_')[0]]
        out.append(line)
    return out


def main():
    used = set()
    chapters = []
    for key, label, title, boss, summary in CHAPTERS:
        scenes = []
        for conv, room, trigger, cond in SCENES[key]:
            used.add(conv)
            sc = {'id': conv, 'room': ROOMS[room], 'trigger': trigger}
            if cond:
                sc['condition'] = cond
            sc['lines'] = lines(conv)
            scenes.append(sc)
        ch = {'id': key, 'label': label, 'title': title}
        if boss:
            ch['boss'] = boss
        ch['summary'] = summary
        num = {'prologue': 0, 'epilogue': 8}.get(key) if key[:2] != 'ch' else int(key[2:])
        ch['rooms'] = [r.title for r in levels.ROOMS if r.chapter == num]
        ch['scenes'] = scenes
        chapters.append(ch)
    missing = set(dialogue.CONVERSATIONS) - used
    assert not missing, 'conversations missing from the export: %s' % sorted(missing)
    story = {
        'title': 'Cyberpunk Ninja',
        'premise': ("Kanshi Dynamics powers its tower, the Kanshi Spire, with minds (engrams) copied out of the city "
                    "below. Years ago its ruler, the Daimyo, uploaded a young ninja named Kuro; the human Kuro did not "
                    "survive. Kanshi used the upload as a template: copy two became the loyal enforcer Mukuro, and "
                    "copy three became Hotaru, a ninja body that was rejected and dumped in the Sump. She wakes up "
                    "with Kuro's engram talking in her head, and they climb the Spire for answers."),
        'cast': CAST,
        'bosses': BOSSES,
        'mechanics': MECHANICS,
        'chapters': chapters,
        'end_card': [t for _, t in dialogue.END_PAGE + dialogue.END_NEXT],
    }
    with open(OUT, 'w') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
        f.write('\n')
    n = sum(len(s['lines']) for c in chapters for s in c['scenes'])
    print('wrote %s: %d chapters, %d scenes, %d lines' % (os.path.normpath(OUT), len(chapters), len(used), n))


if __name__ == '__main__':
    main()
