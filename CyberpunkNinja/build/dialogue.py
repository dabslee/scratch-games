"""
Dialogue, tutorial prompts and menu text. Long dialogue lines are wrapped and
split into 3-line pages automatically when the text costumes are rendered.
"""

import json
import os

# The story (every conversation, in play order) lives in ../story.json; edit it there
# and rebuild. Each scene's lines become one conversation, keyed by the scene id.
STORY = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'story.json')))

SPEAKER_KEY = {
    'Hotaru': 'hotaru', 'Kuro': 'kuro', 'Tetsu': 'tetsu', 'DaiCam': 'daicam', 'Lady Luck': 'luck',
    'System': 'system', 'Mukuro': 'mukuro', 'The Daimyo': 'daimyo', 'Big Oni': 'oni',
    'The Harmacist': 'harm', '???': 'unknown',
}
NAMEPLATE = {
    'hotaru': 'name_hotaru', 'kuro': 'name_kuro', 'tetsu': 'name_tetsu',
    'daicam': 'name_daicam', 'unknown': 'name_unknown', 'luck': 'name_lady_luck', 'system': 'name_system',
    'mukuro': 'name_mukuro', 'daimyo': 'name_the_daimyo', 'oni': 'name_big_oni', 'harm': 'name_the_harmacist',
}
PORTRAIT = {
    'hotaru': 'hotaru_neutral', 'kuro': 'kuro_neutral', 'tetsu': 'tetsu_neutral', 'daicam': 'daicam_neutral',
    'luck': 'luck_neutral', 'system': 'sys_boot', 'mukuro': 'mukuro_neutral', 'daimyo': 'daimyo_neutral',
    'oni': 'oni_neutral', 'harm': 'harm_neutral',
}
# (scene id, line index) -> portrait, where the speaker's default expression doesn't fit
EXPRESSION = {
    ('boot', 2): 'kuro_smirk', ('boot', 3): 'hotaru_visor_up', ('boot', 4): 'kuro_smirk',
    ('boot', 5): 'hotaru_angry', ('boot', 7): 'hotaru_angry', ('boot', 13): 'kuro_smirk',
    ('boot', 15): 'hotaru_visor_up', ('boot', 17): 'kuro_smirk', ('drones', 1): 'kuro_smirk',
    ('turret', 1): 'kuro_smirk', ('tetsu', 5): 'hotaru_visor_up', ('tetsu', 8): 'kuro_smirk',
    ('tetsu', 9): 'hotaru_visor_up', ('shard1', 3): 'hotaru_visor_up', ('ch1', 2): 'kuro_smirk',
    ('daicam1', 2): 'kuro_smirk', ('shard2', 3): 'hotaru_visor_up', ('boss_gate', 4): 'kuro_smirk',
    ('oni2', 1): 'kuro_smirk', ('oni_dead', 3): 'hotaru_visor_up', ('drainling', 0): 'hotaru_visor_up',
    ('daicam_sewer', 2): 'hotaru_angry', ('dobu_dead', 3): 'kuro_smirk', ('slots', 1): 'kuro_smirk',
    ('debtors', 0): 'hotaru_angry', ('luck_gate', 3): 'kuro_smirk', ('luck', 1): 'hotaru_angry',
    ('luck', 3): 'hotaru_angry', ('ch4', 0): 'hotaru_visor_up', ('warden', 1): 'kuro_smirk',
    ('pricing', 2): 'hotaru_angry', ('pricing', 4): 'hotaru_angry', ('daicam4', 1): 'hotaru_visor_up',
    ('harm', 2): 'hotaru_angry', ('harm_dead', 1): 'hotaru_angry', ('ch5', 3): 'kuro_smirk',
    ('wind', 1): 'kuro_smirk', ('posts', 1): 'kuro_smirk', ('daicam5', 1): 'hotaru_angry',
    ('raijin', 2): 'kuro_smirk', ('record', 10): 'hotaru_angry', ('ch6', 3): 'kuro_smirk',
    ('ch6', 4): 'hotaru_angry', ('glitch', 0): 'kuro_smirk', ('tetsu_mem', 4): 'hotaru_visor_up',
    ('possess', 0): 'kuro_smirk', ('possess', 1): 'hotaru_angry', ('white_room', 3): 'hotaru_visor_up',
    ('daicam6', 3): 'hotaru_angry', ('kuro_fight', 1): 'hotaru_angry', ('kuro2', 1): 'hotaru_angry',
    ('kuro_spared', 3): 'hotaru_visor_up', ('kuro_spared', 4): 'kuro_smirk', ('kuro_destroyed', 0): 'hotaru_angry',
    ('ch7', 1): 'kuro_smirk', ('ch7_alone', 0): 'hotaru_visor_up', ('trainee', 2): 'hotaru_visor_up',
    ('spar', 0): 'kuro_smirk', ('shard8', 3): 'hotaru_visor_up', ('shard8', 4): 'kuro_smirk',
    ('intake', 3): 'hotaru_angry', ('mukuro', 1): 'kuro_smirk', ('mukuro', 4): 'kuro_smirk',
    ('muk_dead', 6): 'hotaru_visor_up', ('ch8', 0): 'hotaru_visor_up', ('ch8', 4): 'kuro_smirk',
    ('ch8_alone', 0): 'hotaru_visor_up', ('shard9', 3): 'hotaru_visor_up', ('shard9', 5): 'kuro_smirk',
    ('shard9_alone', 1): 'hotaru_visor_up', ('muster', 1): 'hotaru_angry', ('transfer', 5): 'kuro_smirk',
    ('throne', 6): 'hotaru_angry', ('throne_alone', 1): 'hotaru_angry', ('daimyo_fight', 2): 'hotaru_angry',
    ('daimyo_fight', 5): 'hotaru_angry', ('kuro_falls', 1): 'hotaru_angry', ('dm3', 2): 'hotaru_angry',
    ('ending', 2): 'hotaru_angry', ('ending', 6): 'kuro_smirk', ('ending_alone', 1): 'hotaru_visor_up',
    ('epilogue', 2): 'hotaru_visor_up', ('ep_spared', 5): 'hotaru_visor_up', ('ep_spared2', 2): 'hotaru_visor_up',
    ('ep_destroyed', 3): 'hotaru_visor_up', ('barrier', 1): 'hotaru_visor_up', ('ch1', 1): 'hotaru_angry',
    ('daicam2', 2): 'hotaru_angry', ('ch2', 2): 'kuro_smirk', ('ch2', 3): 'hotaru_angry',
    ('luck_dead', 1): 'hotaru_angry', ('harm_gate', 1): 'hotaru_angry', ('shard7', 3): 'hotaru_angry',
    ('kuro2', 2): 'hotaru_angry', ('kuro_spared', 5): 'hotaru_visor_up', ('dm_ally', 0): 'kuro_smirk',
    ('dm_dead', 1): 'hotaru_angry', ('record', 13): 'hotaru_visor_up', ('oni_dead', 4): 'hotaru_angry',
    ('throne', 1): 'hotaru_angry',
}


def _conversations():
    out = {}
    for ch in STORY['chapters']:
        for sc in ch['scenes']:
            lines = []
            for i, ln in enumerate(sc['lines']):
                spk = SPEAKER_KEY[ln['speaker']]
                who = SPEAKER_KEY[ln['actually']] if spk == 'unknown' else spk
                port = EXPRESSION.get((sc['id'], i)) or PORTRAIT[who]
                if spk == 'unknown' and who == 'kuro' and (sc['id'], i) not in EXPRESSION:
                    port = 'kuro_smirk'
                lines.append((spk, who, port, ln['text']))
            assert sc['id'] not in out, 'duplicate scene id %s' % sc['id']
            out[sc['id']] = lines
    return out


# scene id -> [(name plate key, real speaker, portrait, text)]
CONVERSATIONS = _conversations()

# Tutorial prompts: list of segments. ('k', costume) = key icon, ('t', text) = label.
HINTS = {
    'move': [('k', 'key_left'), ('k', 'key_right'), ('t', 'Run'), ('g',), ('k', 'key_up'), ('t', 'Jump (hold to jump higher)')],
    'jump': [('k', 'key_down'), ('k', 'key_down'), ('t', 'or'), ('k', 'key_down'), ('t', '+'), ('k', 'key_space'), ('t', 'drop through platforms')],
    'cling': [('t', 'Jump into a wall to cling to it'), ('n',), ('k', 'key_up'), ('t', 'while clinging: wall jump')],
    'attack': [('k', 'mouse_l'), ('t', '/'), ('k', 'key_x'), ('t', 'Attack'), ('n',), ('t', 'Keep pressing to chain a 4-hit combo')],
    'deflect': [('k', 'key_down'), ('t', 'Deflect right before a hit lands'), ('n',), ('t', 'Hold to block (it builds your Stance)')],
    'dash': [('k', 'key_space'), ('t', 'Phase Step: an invincible dash'), ('n',), ('t', 'Passes through lasers and attacks')],
    'talk': [('k', 'key_e'), ('t', 'Talk')],
    'heal': [('k', 'key_r'), ('t', 'Drink from the Nano-Gourd'), ('n',), ('k', 'key_e'), ('t', 'Rest at a Shrine to refill everything')],
    'integrity': [('t', "Fill an enemy's STANCE bar,"), ('n',), ('t', 'then'), ('k', 'mouse_l'), ('t', 'near the red reticle to EXECUTE')],
    'heavy': [('k', 'key_space'), ('t', 'then'), ('k', 'mouse_l'), ('t', 'Heavy Strike'), ('n',), ('t', 'Big Stance damage, even on a guard')],
    'breach': [('t', 'Red diamond = BREACH attack'), ('n',), ('t', "Can't block it:"), ('k', 'key_space'), ('t', 'Phase Step through')],
    'launch': [('k', 'key_up'), ('t', '+'), ('k', 'mouse_l'), ('t', 'Launcher: pops enemies into the air')],
    'upgrade': [('t', 'NANO-GOURD UPGRADED: now holds 4 charges')],
    'lasergrid': [('t', 'Laser grids pulse on and off.'), ('n',), ('t', 'Wait for a gap, or'), ('k', 'key_space'), ('t', 'Phase Step through')],
    'cards': [('k', 'key_down'), ('t', 'Deflect a card-blade to send it back'), ('n',), ('t', 'Returned cards hurt and build Stance')],
    'cage': [('k', 'mouse_l'), ('t', 'Attack the cage to free DaiCam')],
    'reels': [('t', 'Watch the reels: they pick her next move.'), ('n',), ('t', 'SHOCKWAVE is a Breach. Jump or Phase Step')],
    'mist': [('t', 'Step into the heat vent to ride it up'), ('n',), ('k', 'key_left'), ('k', 'key_right'), ('t', 'steer while rising')],
    'toxic': [('t', 'Glowing runoff burns.'), ('n',), ('t', 'Jump it, or'), ('k', 'key_space'), ('t', 'Phase Step across')],
    'drainling': [('t', 'Drainlings lunge and spit sludge.'), ('n',), ('k', 'key_down'), ('t', 'Deflect the spit back')],
    'tide': [('t', 'When the pumps gurgle, the tide rises.'), ('n',), ('t', 'Get up high and wait it out')],
    'dobu': [('t', 'Deflect an arm slam, then cut the arm.'), ('n',), ('t', 'With both arms gone, strike the core')],
    'harm': [('k', 'key_down'), ('t', 'Deflect vials back at her.'), ('n',), ('t', 'Heavy Strike to stop her healing')],
    'pulse': [('t', 'This vent pulses on and off.'), ('n',), ('t', 'Ride it while the heat is strong')],
    'warden': [('t', 'Wardens guard your attacks.'), ('n',), ('k', 'key_down'), ('t', 'Deflect their strikes, then counter')],
    'duel': [('t', 'Mukuro guards everything.'), ('n',), ('k', 'key_down'), ('t', 'Deflect to break him, then strike')],
    'wind': [('t', 'Headwind pushes you back.'), ('n',), ('k', 'key_space'), ('t', 'Phase Step across wide gaps')],
    'posts': [('t', 'Patrol crows skim the roof.'), ('n',), ('k', 'key_up'), ('t', 'Jump or'), ('k', 'key_space'), ('t', 'Phase Step through')],
    'raijin': [('t', 'Deflect shells back at the core.'), ('n',), ('t', 'Strike the core while it vents')],
    'glitch': [('t', 'Glitch blocks phase in and out.'), ('n',), ('t', 'They flicker just before they vanish')],
    'possess': [('t', 'When the screen turns purple,'), ('n',), ('k', 'key_left'), ('k', 'key_right'), ('t', 'are swapped')],
    'clash': [('t', 'When Kuro dashes at you,'), ('n',), ('k', 'key_space'), ('t', 'Phase Step through him to Clash')],
    'shell': [('t', 'Trainees dash in and throw kunai.'), ('n',), ('k', 'key_down'), ('t', 'Deflect, then counter')],
    'muk2': [('t', 'Jump his shockwaves.'), ('n',), ('t', 'His shadow strikes from behind you')],
    'choice': [('k', 'key_e'), ('t', 'Reach out'), ('g',), ('k', 'mouse_l'), ('t', 'Destroy his mind')],
    'exo': [('t', 'Deflect the nodachi. Jump the stomp.'), ('n',), ('t', 'Strike when the armor recovers')],
    'eye': [('k', 'key_down'), ('t', 'Deflect turret fire into the eye.'), ('n',), ('t', 'Strike it when it drops')],
    'duel3': [('k', 'key_down'), ('t', 'Deflect his cuts and slash waves.'), ('n',), ('t', "Don't strike into his raised guard."), ('n',),
              ('k', 'key_space'), ('t', 'Phase Step through the soul grab')],
}
# pre-boss tips: the same advice, labeled for the fight in the next room
for _k, _src, _boss in (('gate_oni', 'heavy', 'BIG ONI'), ('gate_dobu', 'dobu', 'DOBUNUSHI'),
                        ('gate_luck', 'reels', 'LADY LUCK'), ('gate_harm', 'harm', 'THE HARMACIST'),
                        ('gate_raijin', 'raijin', 'RAIJIN'), ('gate_kuro', 'clash', 'KURO'),
                        ('gate_muk', 'duel', 'MUKURO'), ('gate_dm', 'exo', 'THE DAIMYO')):
    HINTS[_k] = [('h', 'NEXT ROOM BOSS: ' + _boss), ('n',)] + HINTS[_src]

OPTION_LABELS = {
    'wide': 'Wide deflect window',
    'slow': 'Slower game speed',
    'heat': 'Slower Stance buildup',
    'gourd': 'Infinite Nano-Gourd',
    'god': 'Invincibility',
    'music': 'Music volume',
    'sfx': 'Sound volume',
    'shake': 'Screen shake',
    'controls': 'Controls',
}

CONTROLS = [
    ('b', 'CONTROLS'),
    ('c', 'Move', 'Arrows  or  A / D'),
    ('c', 'Jump (hold: higher)', 'Up  or  W'),
    ('c', 'Drop through', 'Double-tap Down'),
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

# The end card: the first two lines of story.json's end_card are the title, the rest
# is the closing text, which differs by branch.
END_PAGE = [('b', STORY['end_card']['kuro_spared'][0]), ('t', STORY['end_card']['kuro_spared'][1])]
END_NEXT = [('t', t) for t in STORY['end_card']['kuro_spared'][2:]]
END_NEXT_ALONE = [('t', t) for t in STORY['end_card']['kuro_destroyed'][2:]]
