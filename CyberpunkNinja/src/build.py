"""
Build CyberpunkNinja.sb3 from the art in assets/, the room layouts, the dialogue
script, generated audio and the Scratch-DSL game logic in logic/.

    python3 build.py

Every costume comes from a folder in assets/ (its PNGs and costumes.json). The build
only draws what it makes from data: the rooms (levels.py), the splash screen (from
the logo), and text set in Shinobi Mono (dialogue, hints, option labels and pages).
"""
import hashlib
import json
import os
import sys
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'logic'))

import assets  # noqa: E402
import dialogue  # noqa: E402
import levels  # noqa: E402
import scratchc  # noqa: E402
from assets import PALETTE as P, CostumeSet, make_costume, up4  # noqa: E402
from logic import common, enemies, menu, objects, visuals  # noqa: E402

OUT = os.path.join(HERE, '..', 'CyberpunkNinja.sb3')
FILES = {}          # md5ext -> bytes
REG = assets.Font(False)
BOLD = assets.Font(True)


def read_logic(name):
    return open(os.path.join(HERE, 'logic', name)).read()


# ------------------------------------------------------------------ helpers
def costume_from(im_1x, name, cx1, cy1):
    """Register a 1x art image; (cx1, cy1) is the anchor in art pixels."""
    return make_costume(name, up4(im_1x), int(cx1 * 4), int(cy1 * 4), FILES)


def rgba(name, a=255):
    return P[name] + (a,)


def text_image(lines, font=REG, color=P['white'], line_h=11, align='left', width=None, shadow=None):
    w = width or max(1, max(font.width(l) for l in lines))
    im = Image.new('RGBA', (w + 1, line_h * len(lines)), (0, 0, 0, 0))
    for i, l in enumerate(lines):
        x = 0 if align == 'left' else (w - font.width(l)) // 2
        font.draw(im, x, i * line_h, l, color, shadow)
    return im


def panel_image(w, h, fill='night1', alpha=235, border='cyan2', accent='mag3'):
    """A UI panel of any size (the hint cards are as big as their text)."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 0, w - 2, h - 1], fill=rgba(fill, alpha))
    d.rectangle([0, 1, w - 1, h - 2], fill=rgba(fill, alpha))
    d.line([2, 0, w - 3, 0], fill=rgba(border))
    d.line([2, h - 1, w - 3, h - 1], fill=rgba(border))
    d.line([0, 2, 0, h - 3], fill=rgba(border))
    d.line([w - 1, 2, w - 1, h - 3], fill=rgba(border))
    for (x, y) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        im.putpixel((x, y), rgba(border))
    if accent:
        d.line([4, 2, 14, 2], fill=rgba(accent))
        d.line([w - 15, h - 3, w - 5, h - 3], fill=rgba(accent))
    return im


def image(*p):
    im = Image.open(assets.asset_path(*p))
    im.load()
    return im


# ------------------------------------------------------------------ project setup
proj = scratchc.Project()
C = {}           # compile-time constants
TARGETS = []


def target(name, stage=False):
    t = scratchc.Target(proj, name, stage)
    t.layer_order = len(proj.targets) - 1
    TARGETS.append(t)
    return t


GLOBALS = '''
mode menu frame ingame room chapter exL exR exU exD enter_dir want_room want_respawn
px py pface pst pinv pparry pblock pdash p_ground p_onplat p_cmd hp heat gourd gmax has_gourd
dash_ch hitstop shake shake_amp shx shy flash fade fade_to
kL kR kU kD kA kZ kS kH kE kN kP pU pD pL pR pA pZ pS pH pE p_ok p_click p_pause p_any
opt_wide opt_slow opt_heat opt_music opt_sfx opt_shake opt_preset opt_din opt_dout dmg_in dmg_out
banner banner_t card hint prompt_on prompt_x prompt_y dlg_req dlg_on dlg_spk dlg_port dlg_txt dlg_nm dlg_name
boss_on boss_hp boss_int boss_slot boss_phase boss_dead ambush_on mp_on mp_x mp_y lift_ride
cp_room cp_x cp_y has_save shards shard_id deaths play_time daicam_done cam_x cam_y music_cur music_want
first tstr pfr slash_fx slash_off dlg_t msel press_t chap_i
luck_dead boss_name slot_state slot_t slot_sym daicam3_done cage_broken
muk_dead muk_exit daicam4_done
raijin_dead daicam5_done wind moving rj_bx rj_arm rj_plow rj_open
kuro_dead kbranch kb_last kuro_in daicam6_done daicam7_done flip flip_warn gph ke1 ke2 sh_x sh_t sh_f
daicam8_done daimyo_dead dm_ph dm_vul eye_x eye_y eye_st mk_x mk_y mk_st ally_x ally_st
dobu_dead daicam2_done harm_dead tide_y tide_hi tide_force tide_lvl tide_t tide_warn
dobu_cut dobu_gen dobu_ph dobu_open dobu_turn
walk_to muk_bx muk_carry recep escort_go
ally_hp ally_lives ally_rev ally_inv ally_def ally_dash ally_shot fy_floor dm_z dm_hi dm_lh exo_x dm_st dm_t dm_fc dm_tell dm_fl
hold_x hold_y ke1_tell ke2_tell
flip_t dawn boss_dmul foes_left hint_hover clk_s splash_t dlg_c dlg_n dlg_pg
'''.split()

GLOBAL_LISTS = '''
grid R_GRID R_LEVEL R_CH R_L R_R R_U R_D R_BOSS O_FIRST O_NUM O_TYPE O_X O_Y O_A O_B
ent_type ent_x ent_y ent_w ent_h ent_hp ent_int ent_imax ent_alive ent_stag ent_dmg ent_idmg ent_kb ent_hk
ent_foe ent_obj ent_brk ent_sev hq_t hq_d hq_x cq_t cq_x cq_y cq_d mq_t mq_x mq_y mq_d
pq_t pq_x pq_y pq_vx pq_vy pk_x pk_y pz_x pz_y brk_hits sfxq ui_slot ui_role
trig_x trig_ev trig_on dead_objs seen got_shards broken dm_hits
CONV_NAME CONV_START CONV_LEN DL_SPK DL_PORT DL_TEXT DL_NAME
MI_KEY MI_X MI_Y MI_KIND HUD_ROLES DLG_ROLES FONT_W sl_q reel_q RZ R_WIND R_MOVE R_FLIP R_TIDE GL_I GL_T
R_LEVEL2 R_MOON DLL_N DLL_W PRESETS MULTS MULTN
'''.split()

for g in GLOBALS:
    proj.add_global(g, 0)
for g in GLOBAL_LISTS:
    proj.add_global_list(g, [])


def set_list(name, items):
    proj.add_global_list(name, items)


# ------------------------------------------------------------------ room data
ROOMS = levels.ROOMS
RI = levels.ROOM_INDEX
problems = levels.validate()
if problems:
    raise SystemExit('room validation failed:\n' + '\n'.join(problems))

set_list('R_GRID', [r.grid_string() for r in ROOMS])
set_list('R_LEVEL', ['room_' + r.key for r in ROOMS])
# rooms with toxic runoff have a second frame for it to bubble
BUBBLING = [r for r in ROOMS if any('w' in row for row in r.g)]
set_list('R_LEVEL2', ['room_' + r.key + ('_b' if r in BUBBLING else '') for r in ROOMS])
# the moon over the Tenshu sets as Hotaru climbs: its height per room (999 = below the clouds)
MOON_STEP = {'g1': 0, 'g2': 1, 'g3': 2, 'g4': 3, 'g4s': 3, 'g5': 4, 'g6': 5, 'g7': 6}
set_list('R_MOON', [96 - 28 * MOON_STEP[r.key] if r.key in MOON_STEP else 999 for r in ROOMS])
set_list('PRESETS', dialogue.PRESETS)
set_list('MULTS', dialogue.MULTS)
set_list('MULTN', dialogue.MULTN)
set_list('R_CH', [r.chapter for r in ROOMS])
for d in 'LRUD':
    set_list('R_' + d, [RI[r.exits[d]] if d in r.exits else 0 for r in ROOMS])
set_list('R_WIND', [r.wind for r in ROOMS])
set_list('R_MOVE', [r.moving for r in ROOMS])
set_list('R_FLIP', [r.flip for r in ROOMS])
set_list('R_TIDE', [levels.top(r.tide) if r.tide else 0 for r in ROOMS])
# per chapter (index = chapter + 1): first room and music
CH_FIRST = ['p1', 'a1', 'b1', 'w1', 'd1', 'e1', 'c0', 'f1', 'g1', 'ep']
set_list('CH_ROOM', [RI[k] for k in CH_FIRST])
set_list('CH_MUSIC', ['sump', 'alley', 'vaults', 'sewers', 'monorail', 'hollow', 'gardens', 'academy', 'tenshu', 'epilogue'])
set_list('R_BOSS', [max(1, r.chapter) if 'boss' in r.flags else 0 for r in ROOMS])
O_FIRST, O_NUM, OT, OX, OY, OA, OB = [], [], [], [], [], [], []
for r in ROOMS:
    O_FIRST.append(len(OT) + 1)
    O_NUM.append(len(r.objs))
    for o in r.objs:
        a = o['a']
        if o['type'] == 'sign':
            a = a.split('_')[1].lower()
        OT.append(o['type'])
        OX.append(round(o['x'], 2))
        OY.append(round(o['y'], 2))
        OA.append(a)
        OB.append(o['b'])
set_list('O_FIRST', O_FIRST)
set_list('O_NUM', O_NUM)
set_list('O_TYPE', OT)
set_list('O_X', OX)
set_list('O_Y', OY)
set_list('O_A', OA)
set_list('O_B', OB)
a1_start = [o for o in levels.a1.objs if o['type'] == 'start'][0]
w1_start = [o for o in levels.w1.objs if o['type'] == 'start'][0]
b1_start = [o for o in levels.b1.objs if o['type'] == 'start'][0]
c0_start = [o for o in levels.c0.objs if o['type'] == 'start'][0]
d1_start = [o for o in levels.d1.objs if o['type'] == 'start'][0]
e1_start = [o for o in levels.e1.objs if o['type'] == 'start'][0]
f1_start = [o for o in levels.f1.objs if o['type'] == 'start'][0]
g1_start = [o for o in levels.g1.objs if o['type'] == 'start'][0]
C.update({
    'C_ROOM_P1': RI['p1'], 'C_ROOM_A1': RI['a1'], 'C_A1_X': a1_start['x'], 'C_A1_Y': a1_start['y'],
    'C_ROOM_W1': RI['w1'], 'C_W1_X': w1_start['x'], 'C_W1_Y': w1_start['y'],
    'C_ROOM_B1': RI['b1'], 'C_B1_X': b1_start['x'], 'C_B1_Y': b1_start['y'],
    'C_ROOM_C0': RI['c0'], 'C_C0_X': c0_start['x'], 'C_C0_Y': c0_start['y'],
    'C_ROOM_D1': RI['d1'], 'C_D1_X': d1_start['x'], 'C_D1_Y': d1_start['y'],
    'C_ROOM_E1': RI['e1'], 'C_E1_X': e1_start['x'], 'C_E1_Y': e1_start['y'],
    'C_ROOM_F1': RI['f1'], 'C_F1_X': f1_start['x'], 'C_F1_Y': f1_start['y'],
    'C_ROOM_G1': RI['g1'], 'C_ROOM_E2': RI['e2'], 'C_ROOM_E6': RI['e6'], 'C_G1_X': g1_start['x'], 'C_G1_Y': g1_start['y'], 'C_ROOM_EP': RI['ep'], 'C_ROOM_G5': RI['g5'], 'C_ROOM_F7': RI['f7'],
    'C_LIFT_LOW': -200, 'C_LIFT_TOP': levels.top(19),
    'C_G': 1.5, 'C_JUMP': 16.5, 'C_WALLJUMP': 15, 'C_BOOST': 18, 'C_RUN': 6, 'C_MAXFALL': 13,
    'C_SLIDE': 3, 'C_DASHV': 21.3, 'C_DASHF': 6, 'C_HW': 7, 'C_PH': 34, 'C_COYOTE': 3,
    'C_JBUF': 4, 'C_PARRY': 6, 'C_PARRY_WIDE': 12, 'C_OVERHEAT': 36, 'C_IFRAMES': 30,
    'C_HEAL': 4, 'C_COMBO': 11,
})

# ------------------------------------------------------------------ dialogue pages
DLG_COSTUMES = []
CONV_NAME, CONV_START, CONV_LEN, DL_SPK, DL_PORT, DL_TEXT, DL_NAME = [], [], [], [], [], [], []
DLL_N, DLL_W = [], []    # per page, three entries: each line's characters and width (art px), for typing it out
page_no = 0
for cname, lines in dialogue.CONVERSATIONS.items():
    CONV_NAME.append(cname)
    CONV_START.append(len(DL_SPK) + 1)
    n = 0
    for spk, who, port, text in lines:
        # dialogue text is drawn at 3/4 of the usual pixel scale so more fits in the box
        wrapped = REG.wrap(text, 234)
        for i in range(0, len(wrapped), 3):
            page = wrapped[i:i + 3]
            for k in range(3):
                DLL_N.append(len(page[k]) if k < len(page) else 0)
                DLL_W.append(REG.width(page[k]) if k < len(page) else 0)
            page_no += 1
            name = 'txt_%d' % page_no
            tim = text_image(page, width=234)
            DLG_COSTUMES.append(make_costume(name, tim.resize((tim.width * 3, tim.height * 3), Image.NEAREST), 0, 0, FILES))
            DL_SPK.append(who)
            DL_PORT.append(port)
            DL_TEXT.append(name)
            DL_NAME.append(dialogue.NAMEPLATE[spk])
            n += 1
    CONV_LEN.append(n)
set_list('CONV_NAME', CONV_NAME)
set_list('CONV_START', CONV_START)
set_list('CONV_LEN', CONV_LEN)
set_list('DL_SPK', DL_SPK)
set_list('DL_PORT', DL_PORT)
set_list('DL_TEXT', DL_TEXT)
set_list('DL_NAME', DL_NAME)
set_list('DLL_N', DLL_N)
set_list('DLL_W', DLL_W)
set_list('HUD_ROLES', ['hp', 'dash', 'gourd', 'heat', 'bplate', 'bbar', 'bint'] + ['clk%d' % k for k in range(1, 7)])
# m1-m3 hide each line's untyped part; they're made after the text, so they draw over it
set_list('DLG_ROLES', ['box', 'port', 'name', 'text', 'm1', 'm2', 'm3', 'arrow'])
set_list('FONT_W', [REG.glyphs[ch].width for ch in REG.order])


# ------------------------------------------------------------------ hint cards
def hint_image(segs):
    rows = [[]]
    for s in segs:
        if s[0] == 'n':
            rows.append([])
        elif s[0] == 'k':
            rows[-1].append(('img', image('ui', 'keys', s[1] + '.png')))
        elif s[0] == 't':
            rows[-1].append(('img', text_image([s[1]], shadow=P['ink'])))
        elif s[0] == 'h':
            rows[-1].append(('img', text_image([s[1]], BOLD, P['mag3'], shadow=P['ink'])))
        else:
            rows[-1].append(('gap', 6))
    widths = [sum(p[1].width if p[0] == 'img' else p[1] for p in r) + 3 * (len(r) - 1) for r in rows]
    w = 8 + max(widths)
    rh = 17
    # a line under the rows for the small grey note: a click puts the card away
    h = 4 + rh * len(rows) + 5
    im = panel_image(w, h, alpha=215, accent=None, border='slate3')
    im.alpha_composite(HINT_NOTE, (w - HINT_NOTE.width - 4, h - 8))
    for ri, row in enumerate(rows):
        x = (w - widths[ri]) // 2
        cy = 2 + ri * rh + rh // 2
        for kind, p in row:
            if kind == 'img':
                im.alpha_composite(p, (x, cy - p.height // 2 + (1 if p.height < 12 else 0)))
                x += p.width + 3
            else:
                x += p + 3
    if w > 236:
        print('WARNING hint too wide', w, segs)
    return im


HINT_NOTE = image('ui', 'hint_note.png')
HINT_COSTUMES = []
for k, v in dialogue.HINTS.items():
    him = hint_image(v)
    HINT_COSTUMES.append(costume_from(him, 'hint_' + k, him.width / 2, him.height / 2))

# ------------------------------------------------------------------ option labels, values and pages
MENU = CostumeSet('ui/menu')
OPTION_LABELS = []
for key, label in dialogue.OPTION_LABELS.items():
    im = text_image([label], REG, P['white'], shadow=P['ink'])
    assert im.width <= 128, ('option label too wide', label, im.width)
    OPTION_LABELS.append(costume_from(im, 'lbl_' + key, 0, 5))
OPTION_VALUES = []
values = {'on': 'ON', 'off': 'OFF', 'view': 'VIEW'}
values.update(dialogue.VALUE_TEXT)
for i in range(6):
    values['vol%d' % i] = '%d%%' % (i * 20)
for vk, vt in values.items():
    for state in ('normal', 'hover'):
        base = MENU.image('blank_' + state).copy()
        tim = text_image([vt], BOLD, P['white'] if state == 'hover' else P['steel'])
        base.alpha_composite(tim, ((base.width - tim.width) // 2, 3))
        OPTION_VALUES.append(costume_from(base, 'val_%s_%s' % (vk, state), 40, 7))



def page_image(rows, width=200):
    lines = []
    for r in rows:
        kind = r[0]
        if kind == 's':
            lines.append(('gap', 5))
        elif kind == 'c':
            lines.append(('col', r[1], r[2]))
        elif kind == 'n':
            lines.append(('note', r[1]))
        else:
            lines.append((kind, r[1]))
    h = sum(5 if l[0] == 'gap' else 11 for l in lines)
    im = Image.new('RGBA', (width, h), (0, 0, 0, 0))
    y = 0
    for l in lines:
        if l[0] == 'gap':
            y += 5
            continue
        if l[0] == 'col':
            REG.draw(im, 2, y, l[1], P['steel'], P['ink'])
            REG.draw(im, 104, y, l[2], P['white'], P['ink'])
            assert REG.width(l[1]) < 100 and 104 + REG.width(l[2]) <= width, ('controls row too wide', l)
        elif l[0] == 'note':
            REG.draw(im, (width - REG.width(l[1])) // 2, y, l[1], P['slate3'], P['ink'])
        else:
            font = BOLD if l[0] in ('b', 'h') else REG
            col = {'b': P['cyan3'], 'h': P['mag3'], 't': P['white']}[l[0]]
            x = (width - font.width(l[1])) // 2
            font.draw(im, x, y, l[1], col, P['ink'] if l[0] != 'b' else P['mag2'])
        y += 11
    return im


PAGES = []
for key, rows, w in (('controls_page', dialogue.CONTROLS, 222),
                     ('end_page', dialogue.END_PAGE, 236), ('end_next', dialogue.END_NEXT, 236),
                     ('end_next_alone', dialogue.END_NEXT_ALONE, 236)):
    im = page_image(rows, w)
    if im.width > 0 and key == 'controls_page':
        for r in rows:
            if r[0] == 't' and REG.width(r[1]) > w:
                print('WARNING controls line too wide', r)
    PAGES.append(costume_from(im, key, im.width / 2, im.height / 2))

# ------------------------------------------------------------------ rooms
ROOM_COSTUMES = [make_costume('room_' + r.key, up4(assets.render_room(r)), 0, 0, FILES) for r in ROOMS]
ROOM_COSTUMES += [make_costume('room_' + r.key + '_b', up4(assets.render_room(r, 1)), 0, 0, FILES) for r in BUBBLING]


# ------------------------------------------------------------------ splash
def splash():
    """The splash logo (assets/ui/splash/splash_logo.png, any size), on white, filling the screen's height."""
    logo = Image.open(assets.asset_path('ui', 'splash', 'splash_logo.png')).convert('RGBA')
    sc = min(640 / logo.height, 900 / logo.width)
    logo = logo.resize((round(logo.width * sc), round(logo.height * sc)), Image.LANCZOS)
    im = Image.new('RGBA', (960, 720), (255, 255, 255, 255))
    im.alpha_composite(logo, ((960 - logo.width) // 2, (720 - logo.height) // 2))
    return [make_costume('splash', im, 480, 360, FILES)]


# ------------------------------------------------------------------ portraits
def sheet_portraits():
    """Every dialogue portrait, from assets/portraits/portraits.png (40x40 cells, in the order
    in portraits.json), each followed by its glitch frames (<name>_g1.png, ...) if it has any.
    export_portraits.py installs new portraits into the sheet."""
    sheet = image('portraits', 'portraits.png').convert('RGBA')
    meta = json.load(open(assets.asset_path('portraits', 'portraits.json')))
    cell = meta['cell']
    out = []
    for p in meta['portraits']:
        im = sheet.crop((p['col'] * cell, p['row'] * cell, (p['col'] + 1) * cell, (p['row'] + 1) * cell))
        out.append(costume_from(im, p['name'], cell / 2, cell / 2))
        k = 1
        while os.path.exists(assets.asset_path('portraits', '%s_g%d.png' % (p['name'], k))):
            out.append(costume_from(image('portraits', '%s_g%d.png' % (p['name'], k)), '%s_g%d' % (p['name'], k), cell / 2, cell / 2))
            k += 1
    missing = set(dialogue.PORTRAIT.values()) - {p['name'] for p in meta['portraits']}
    assert not missing, 'portraits missing from assets/portraits/portraits.png: %s' % missing
    return out


# ------------------------------------------------------------------ audio
import audio  # noqa: E402

SOUNDS = audio.build_all()   # name -> (wav bytes, rate, samples)


def sound_entry(name):
    data, rate, n, fmt = SOUNDS[name]
    md5 = hashlib.md5(data).hexdigest()
    FILES[md5 + '.' + fmt] = data
    return {'name': name, 'assetId': md5, 'dataFormat': fmt, 'format': '', 'rate': rate,
            'sampleCount': n, 'md5ext': md5 + '.' + fmt}


C['C_RAIN_LEN'] = round(SOUNDS['rain_loop'][2] / SOUNDS['rain_loop'][1], 3)
C['C_WIND_LEN'] = round(SOUNDS['wind_loop'][2] / SOUNDS['wind_loop'][1], 3)

# ------------------------------------------------------------------ targets
FX = common.FX
CL = common.CLONES
EN = common.ENEMY


def sprite(name, costumes, src, sounds=(), visible=False, x=0, y=0):
    t = target(name)
    t.costumes = costumes
    t.sounds = [sound_entry(s) for s in sounds]
    t.visible = visible
    t.x, t.y = x, y
    try:
        scratchc.compile_sprite(t, src, C)
    except scratchc.CompileError as e:
        raise SystemExit('Compile error in %s: %s' % (name, e))
    return t


def anim_info_src(folder):
    meta = json.load(open(assets.asset_path('characters', folder, 'animations.json')))
    out = ['@proc', 'def anim_info(name):']
    first = True
    for k, v in meta.items():
        out.append('    %s name == "%s":' % ('if' if first else 'elif', k))
        out.append('        a_n = %d' % v['frames'])
        out.append('        a_fps = %d' % (0 if k == 'jump' else v['fps']))
        out.append('        a_loop = %d' % (1 if v['loop'] else 0))
        first = False
    return '\n'.join(out) + '\n'


ATTACKS = {
    'attack1': (1, 1, 1, 3, 'slash1', 0, 'slash1'),
    'attack2': (1, 1, 1, 3, 'slash2', 0, 'slash2'),
    'attack3': (1, 1, 1, 3, 'thrust', 0, 'slash3'),
    'attack4': (2, 2, 1, 9, 'finisher', 1, 'finisher'),
    'air_attack': (1, 1, 1, 3, 'air', 0, 'slash2'),
    'launcher': (1, 1, 1, 0, 'launcher', 0, 'launcher'),
    'heavy': (2, 3, 3, 10, 'heavy', 2, 'heavy'),
    'severance': (1, 0, 0, 0, '', 0, 'sever_draw'),
}


def atk_info_src():
    out = ['@proc', 'def atk_info(a):']
    first = True
    for k, (conn, dmg, integ, kb, fx, fxoff, snd) in ATTACKS.items():
        out.append('    %s a == "%s":' % ('if' if first else 'elif', k))
        for var, val in (('atk_conn', conn), ('atk_dmg', dmg), ('atk_int', integ), ('atk_kb', kb)):
            out.append('        %s = %s' % (var, val))
        out.append('        atk_fx = "%s"' % fx)
        out.append('        atk_fxoff = %d' % fxoff)
        out.append('        atk_snd = "%s"' % snd)
        first = False
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------ sprites
# made from data, slotted into a costume folder where its costumes.json says "generated"
GENERATED = {
    'rooms': ROOM_COSTUMES, 'splash': splash(), 'portraits': sheet_portraits(), 'dialogue_pages': DLG_COSTUMES,
    'hints': HINT_COSTUMES, 'option_labels': OPTION_LABELS, 'option_values': OPTION_VALUES, 'pages': PAGES,
}


def art(folder):
    return CostumeSet(folder).costumes(FILES, GENERATED)


stage = target('Stage', stage=True)
stage.costumes = art('backgrounds/stage')
stage.sounds = []
stage.current_costume = [c['name'] for c in stage.costumes].index('black')
scratchc.compile_sprite(stage, read_logic('stage.py'), C)

BLACK = art('fx/fade')   # the shared costume of the sprites that only play sounds
SLASHFX_SRC = '''
@flag
def s_init():
    hide()


@on("t_draw")
def draw():
    sfr = floor(pfr) - slash_off
    if ingame == 1 and pst == "atk" and slash_fx != "" and sfr >= 0 and sfr < 4:
        costume(join(slash_fx, "_", sfr))
        goto(px + shx, py + shy)
        if pface == 1:
            point(90)
        else:
            point(-90)
        show()
    else:
        hide()
'''

# in layer order, back to front
sprite('Warmup', art('fx/warmup'), visuals.WARMUP)
sprite('Splash', GENERATED['splash'], visuals.SPLASH)
sprite('Sky', art('backgrounds/sky'), visuals.SKY)
sprite('Parallax_far', art('backgrounds/parallax_far'), visuals.parallax(0.05, 1))
sprite('Parallax_mid', art('backgrounds/parallax_mid'), visuals.parallax(0.12, 9))
sprite('Ranks', art('backgrounds/ranks'), visuals.RANKS)
sprite('GlitchBG', art('fx/glitch_bg'), visuals.GLITCHBG)
sprite('Level', ROOM_COSTUMES, visuals.LEVEL)
sprite('Props', art('objects/props'), CL + objects.PROPS)
sprite('PhaseBlock', art('objects/phase_block'), CL + objects.PHASEBLOCK)
sprite('Mist', art('objects/mist'), CL + objects.MIST)
sprite('SlotMachine', art('objects/slot_machine'), CL + enemies.SLOT_MACHINE)
sprite('Reels', art('objects/reels'), CL + enemies.REELS)
sprite('Breakable', art('objects/breakable'), CL + FX + objects.BREAKABLE)
sprite('LaserBarrier', art('objects/laser_barrier'), CL + objects.LASER)
sprite('SecurityDoor', art('objects/security_door'), CL + EN + objects.DOOR)
sprite('ShrineTerminal', art('objects/shrine_terminal'), CL + FX + objects.SHRINE)
sprite('Pickup', art('objects/pickup'), CL + FX + objects.PICKUP)
sprite('MemoryShard', art('objects/memory_shard'), CL + FX + EN + objects.SHARD)
sprite('ShockPuddle', art('objects/shock_puddle'), CL + objects.PUDDLE)
sprite('MovingPlatform', art('objects/moving_platform'), CL + objects.LIFT)
sprite('Crate', art('objects/crate'), CL + EN + objects.CRATE)
sprite('Tetsu', art('characters/tetsu'), CL + objects.TETSU)
sprite('DaiCam', art('characters/daicam'), CL + EN + objects.DAICAM)
sprite('Cage', art('objects/cage'), CL + FX + EN + objects.CAGE)
sprite('CamDrone', art('characters/cam_drone'), CL + objects.CAMDRONE)
sprite('Turret', art('characters/turret'), CL + FX + EN + enemies.TURRET)
sprite('SlotTurret', art('characters/slot_turret'), CL + FX + EN + enemies.SLOT_TURRET)
sprite('Croupier', art('characters/croupier'), CL + FX + EN + enemies.CROUPIER)
sprite('HannyaBoy', art('characters/hannya_boy'), CL + FX + EN + enemies.HANNYA)
sprite('BigOni', art('characters/big_oni'), CL + FX + EN + enemies.ONI)
sprite('ScavDrone', art('characters/scav_drone'), CL + FX + EN + enemies.DRONE)
sprite('LadyLuck', art('characters/lady_luck'), CL + FX + EN + enemies.LUCK)
sprite('Warden', art('characters/warden'), CL + FX + EN + enemies.WARDEN)
sprite('KuroBoss', art('characters/kuro_boss'), CL + FX + EN + enemies.KUROBOSS)
sprite('Daimyo', art('characters/daimyo'), CL + FX + EN + enemies.DAIMYO)
sprite('Dobunushi', art('characters/dobunushi'), CL + FX + EN + enemies.DOBU)
sprite('Harmacist', art('characters/harmacist'), CL + FX + EN + enemies.HARM)
sprite('Mukuro', art('characters/mukuro'), CL + FX + EN + enemies.MUKURO)
sprite('Raijin', art('characters/raijin'), CL + FX + EN + enemies.RAIJIN)
sprite('TrackPost', art('objects/track_post'), CL + EN + enemies.TRACKPOST)
sprite('SweepLaser', art('objects/sweep_laser'), CL + EN + enemies.SWEEP)
sprite('Kuro', art('characters/kuro'), visuals.KURO)
sprite('Hotaru', art('characters/hotaru'), read_logic('hotaru.py') + FX + anim_info_src('hotaru') + atk_info_src())
sprite('SlashFX', art('fx/slash_fx'), SLASHFX_SRC)
# the sludge tide draws over the fighters (they wade in it), under the effects and HUD
sprite('Sludge', art('objects/sludge'), objects.SLUDGE)
sprite('Projectiles', art('fx/projectiles'), CL + FX + EN + objects.PROJECTILES)
sprite('MoveFX', art('fx/move_fx'), CL + visuals.fx_sprite('mq', visuals.MOVE_FX))
sprite('CombatFX', art('fx/combat_fx'), CL + visuals.fx_sprite('cq', visuals.COMBAT_FX))
sprite('Rain', art('fx/rain'), visuals.RAIN)
sprite('Flash', art('fx/flash'), visuals.FLASH)
sprite('EnemyUI', art('ui/enemy_ui'), CL + visuals.ENEMY_UI)
sprite('HUD', art('ui/hud'), visuals.HUD)
sprite('Hints', art('ui/hints'), visuals.HINTS)
sprite('Banners', art('ui/banners'), visuals.BANNERS)
sprite('Dialogue', art('ui/dialogue'), visuals.DIALOGUE)
sprite('Menu', art('ui/menu'), menu.MENU)
sprite('TextFX', art('fonts/regular'), menu.TEXTFX)
sprite('Fade', BLACK, visuals.FADE)
sprite('SFX', BLACK, visuals.SFX, sounds=audio.SFX_NAMES)

for track, length in audio.MUSIC.items():
    sprite('Music_' + track, BLACK, visuals.music(track, length), sounds=[track])
sprite('Music_drums', BLACK, visuals.music('boss_drums', audio.MUSIC['boss'], drums=True),
       sounds=['boss_drums'])
sprite('Music_luck_drums', BLACK, visuals.music('luck_drums', audio.MUSIC['luck'], drums=True, drums_for='luck'),
       sounds=['luck_drums'])
sprite('Music_mukuro_drums', BLACK, visuals.music('mukuro_drums', audio.MUSIC['mukuro'], drums=True, drums_for='mukuro'),
       sounds=['mukuro_drums'])
sprite('Music_raijin_drums', BLACK, visuals.music('raijin_drums', audio.MUSIC['raijin'], drums=True, drums_for='raijin'),
       sounds=['raijin_drums'])
for tr in ('kuro', 'daimyo', 'dobu', 'harm'):
    sprite('Music_%s_drums' % tr, BLACK, visuals.music(tr + '_drums', audio.MUSIC[tr], drums=True, drums_for=tr),
           sounds=[tr + '_drums'])
sprite('Ambience', BLACK, visuals.AMBIENCE, sounds=['rain_loop', 'wind_loop'])

# make sure the HUD/Hotaru-local name 'pfr' is shared: Hotaru writes it as a global
for t in TARGETS:
    for n in list(t.vars):
        if n in proj.gvars:
            raise SystemExit('variable %s is both local (%s) and global' % (n, t.name))

# ------------------------------------------------------------------ write
pj = proj.to_json()
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('project.json', json.dumps(pj, separators=(',', ':')))
    for name, data in FILES.items():
        z.writestr(name, data)
size = os.path.getsize(OUT)
nblocks = sum(len(t['blocks']) for t in pj['targets'])
print('wrote %s: %.2f MB, %d targets, %d blocks, %d assets' % (OUT, size / 1e6, len(pj['targets']), nblocks, len(FILES)))