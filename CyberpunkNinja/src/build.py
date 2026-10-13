"""
Build CyberpunkNinja.sb3 from the asset pack, the room layouts, the dialogue
script, generated audio and the Scratch-DSL game logic in logic/.

    CN_PACK=/path/to/CyberpunkNinja_AssetPack python3 build.py
"""
import copy
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
import export_portraits  # noqa: E402
import levels  # noqa: E402
import scratchc  # noqa: E402
from assets import PALETTE as P, make_costume, up4  # noqa: E402
from gfx import academy, edits, gardens, hollow_floor, mech, monorail, npcs, sewers, tenshu, ui, util, vaults  # noqa: E402
from logic import common, enemies, menu, objects, visuals  # noqa: E402

OUT = os.path.join(HERE, '..', 'CyberpunkNinja.sb3')
FILES = {}          # md5ext -> bytes
ST = assets.starter()
REG = assets.Font(False)
BOLD = assets.Font(True)


def read_logic(name):
    return open(os.path.join(HERE, 'logic', name)).read()


# ------------------------------------------------------------------ helpers
def copy_costumes(sprite, prefix='', names=None, rename=None):
    out = []
    for c in ST.costumes(sprite):
        if names is not None and not any(c['name'] == n or c['name'].startswith(n) for n in names):
            continue
        c2 = copy.deepcopy(c)
        if rename:
            c2['name'] = rename(c2['name'])
        else:
            c2['name'] = prefix + c2['name']
        FILES[c2['md5ext']] = ST.data(c['md5ext'])
        out.append(c2)
    return out


def costume_from(im_1x, name, cx1, cy1):
    """Register a 1x art image; (cx1, cy1) is the anchor in art pixels."""
    return make_costume(name, up4(im_1x), int(cx1 * 4), int(cy1 * 4), FILES)


def costume_small(im_1x, name, cx1, cy1):
    """Like costume_from, but drawn at 1.5 stage pixels per art pixel so a figure
    stands as tall as Hotaru."""
    return make_costume(name, im_1x.resize((im_1x.width * 3, im_1x.height * 3), Image.NEAREST), int(cx1 * 3), int(cy1 * 3), FILES)


def costume_crop(im_1x, name, cx1, cy1):
    """costume_small, trimmed to the drawn pixels (big animation cells are mostly empty)."""
    box = im_1x.getbbox() or (0, 0, 1, 1)
    return costume_small(im_1x.crop(box), name, cx1 - box[0], cy1 - box[1])


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


# ------------------------------------------------------------------ new key caps
KEY_GLYPHS = {
    'z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
    'x': ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
    'p': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
}


def make_keycap(letter, pressed):
    base = ST.image_1x('KeyPrompts', 'key_e_pressed' if pressed else 'key_e')
    face = None
    px = base.load()
    white = P['white'] + (255,)
    xs, ys = [], []
    for y in range(base.height):
        for x in range(base.width):
            if px[x, y] == white:
                xs.append(x)
                ys.append(y)
    ox, oy = min(xs), min(ys)
    face = px[ox - 1, oy]
    for x, y in zip(xs, ys):
        px[x, y] = face
    for r, row in enumerate(KEY_GLYPHS[letter]):
        for c, ch in enumerate(row):
            if ch == '1':
                px[ox + c, oy + r] = white
    return base


def keycap(name):
    """1x image for a key prompt costume name (existing or generated)."""
    if name[4:5] in KEY_GLYPHS and name.startswith('key_') and len(name.split('_')[1]) == 1:
        return make_keycap(name[4], name.endswith('_pressed'))
    return ST.image_1x('KeyPrompts', name)


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
set_list('FONT_W', [REG.glyphs[c['name'][3:]].width for c in ST.costumes('Font')])


# ------------------------------------------------------------------ hint images
def hint_image(segs):
    rows = [[]]
    for s in segs:
        if s[0] == 'n':
            rows.append([])
        elif s[0] == 'k':
            rows[-1].append(('img', keycap(s[1])))
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
    ui.tiny_text(im, w - ui.tiny_width(HINT_NOTE) - 4, h - 8, HINT_NOTE, rgba('slate3'))
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


HINT_NOTE = 'click to hide'
HINT_COSTUMES = []
for k, v in dialogue.HINTS.items():
    him = hint_image(v)
    HINT_COSTUMES.append(costume_from(him, 'hint_' + k, him.width / 2, him.height / 2))

# ------------------------------------------------------------------ menu images
MENU_COSTUMES = []
MENU_COSTUMES += copy_costumes('Buttons')


def text_button(label):
    """A main-menu button for `label` in the pack's style, drawn over the pack's QUIT button:
    {state: 1x image}."""
    out = {}
    for state in ('normal', 'hover', 'pressed', 'disabled'):
        quit_im = ST.image_1x('Buttons', 'quit_' + state)
        blank = ST.image_1x('Buttons', 'blank_' + state)
        qa, ba = quit_im.load(), blank.load()
        # QUIT's lettering: where it differs from the blank button
        diff = [(x, y) for y in range(quit_im.height) for x in range(quit_im.width) if qa[x, y] != ba[x, y]]
        x0 = min(x for x, y in diff)
        y0 = min(y for x, y in diff)
        y1 = max(y for x, y in diff)
        # its colors, top to bottom: the face, and (hover) the shadow under it
        face = max((qa[x, y] for x, y in diff), key=lambda c: sum(c[:3]))
        bold = state == 'hover'
        font = BOLD if bold else REG
        im = blank.copy()
        t = text_image([label], font, face[:3], shadow=P['ink'] if bold else None)
        im.alpha_composite(t, ((im.width - t.width) // 2, y0 + (y1 - y0 + 1 - 8) // 2 - 1))
        out[state] = im
    return out


for _st, _im in text_button('CONTROLS').items():
    c = ST.costume('Buttons', 'quit_' + _st)
    MENU_COSTUMES.append(make_costume('controls_' + _st, up4(_im), c['rotationCenterX'], c['rotationCenterY'], FILES))
MENU_COSTUMES += copy_costumes('MenuCursor')
MENU_COSTUMES += copy_costumes('Panels')
MENU_COSTUMES += [costume_from(ui.chapter_card(i), 'ch%d' % i, 100, 22) for i in range(9)]
MENU_COSTUMES += copy_costumes('KeyPrompts', names=['key_left', 'key_right'])
MENU_COSTUMES += copy_costumes('Banners', names=['press_any_key'])
big = panel_image(232, 176)
MENU_COSTUMES.append(costume_from(big, 'panel', 116, 88))
for key, label, col in (('ttl_options', 'OPTIONS', 'cyan3'), ('ttl_chapters', 'CHAPTERS', 'cyan3')):
    im = text_image([label], BOLD, P[col], shadow=P['mag2'] if col == 'cyan3' else P['ink'])
    MENU_COSTUMES.append(costume_from(im, key, im.width / 2, 4.5))
for key, label in dialogue.OPTION_LABELS.items():
    im = text_image([label], REG, P['white'], shadow=P['ink'])
    assert im.width <= 128, ('option label too wide', label, im.width)
    MENU_COSTUMES.append(costume_from(im, 'lbl_' + key, 0, 5))
values = {'on': 'ON', 'off': 'OFF', 'view': 'VIEW'}
values.update(dialogue.VALUE_TEXT)
for i in range(6):
    values['vol%d' % i] = '%d%%' % (i * 20)
for vk, vt in values.items():
    for state in ('normal', 'hover'):
        base = ST.image_1x('Buttons', 'blank_' + state)
        tim = text_image([vt], BOLD, P['white'] if state == 'hover' else P['steel'])
        base.alpha_composite(tim, ((base.width - tim.width) // 2, 3))
        MENU_COSTUMES.append(costume_from(base, 'val_%s_%s' % (vk, state), 40, 7))
for key, label, col in (('lbl_play', 'ENTER / CLICK THE CARD TO PLAY', 'cyan3'),
                        ('lbl_locked', 'LOCKED: NOT IN THIS VERTICAL SLICE', 'red3')):
    im = text_image([label], REG, P[col], shadow=P['ink'])
    MENU_COSTUMES.append(costume_from(im, key, im.width / 2, 4.5))


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


for key, rows, w in (('controls_page', dialogue.CONTROLS, 222),
                     ('end_page', dialogue.END_PAGE, 236), ('end_next', dialogue.END_NEXT, 236),
                     ('end_next_alone', dialogue.END_NEXT_ALONE, 236)):
    im = page_image(rows, w)
    if im.width > 0 and key == 'controls_page':
        for r in rows:
            if r[0] == 't' and REG.width(r[1]) > w:
                print('WARNING controls line too wide', r)
    MENU_COSTUMES.append(costume_from(im, key, im.width / 2, im.height / 2))

# ------------------------------------------------------------------ misc images
black = Image.new('RGBA', (120, 90), (0, 0, 0, 255))
white = Image.new('RGBA', (120, 90), P['white'] + (255,))
FADE_COSTUMES = [make_costume('black', black.resize((960, 720), Image.NEAREST), 480, 360, FILES)]
FLASH_COSTUMES = [make_costume('white', white.resize((960, 720), Image.NEAREST), 480, 360, FILES)]


gourd_icon = ST.image_1x('HUD', 'gourd_1')
bbox = gourd_icon.getbbox()
icon = gourd_icon.crop((bbox[0], bbox[1], bbox[0] + 11, bbox[3]))
icon = icon.crop(icon.getbbox())
PICKUP_COSTUMES = [costume_from(icon, 'gourd_pickup', icon.width / 2, icon.height / 2)]


def wave_frame(n):
    im = Image.new('RGBA', (12, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, col in enumerate(['cyan1', 'cyan2', 'cyan3', 'cyan4']):
        hgt = [5, 9, 12, 13][i] - (n * (i % 2))
        x = 2 + i * 2
        d.line([x, 13 - hgt, x, 13], fill=rgba(col))
        d.line([x + 1, 13 - hgt + 2, x + 1, 13], fill=rgba(col, 180))
    d.line([0, 13, 11, 13], fill=rgba('cyan4'))
    return im


WAVE_COSTUMES = [costume_from(wave_frame(i), 'wave_%d' % i, 8, 13) for i in range(2)]


def sludge_wave(n):
    """Dobunushi's spew: a green wall of sludge 48 px tall (96 on stage), feet at the bottom."""
    im = Image.new('RGBA', (14, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, col in enumerate(['green1', 'green2', 'lime', 'green2', 'green1']):
        x = 2 + i * 2
        top = [14, 4, 0, 3, 12][i] + (n * (i % 2)) * 2
        d.line([x, top, x, 47], fill=rgba(col))
        d.line([x + 1, top + 2, x + 1, 47], fill=rgba(col, 200))
    for k in range(6):
        y = 8 + ((k * 7 + n * 4) % 38)
        im.putpixel((3 + (k * 5) % 9, y), rgba('white', 220))
    d.line([0, 47, 13, 47], fill=rgba('lime'))
    return im


WAVE_COSTUMES += [costume_from(sludge_wave(i), 'gwave_%d' % i, 7, 47) for i in range(2)]
tiles_alley = assets.tile_images('alley')
BREAK_COSTUMES = [costume_from(tiles_alley['breakable'], 'breakable', 4, 4),
                  costume_from(tiles_alley['breakable_cracked'], 'breakable_cracked', 4, 4)]
ROOM_COSTUMES = [make_costume('room_' + r.key, up4(assets.render_room(r)), 0, 0, FILES) for r in ROOMS]
ROOM_COSTUMES += [make_costume('room_' + r.key + '_b', up4(assets.render_room(r, 1)), 0, 0, FILES) for r in BUBBLING]

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


MEM_RAMP = ['night2', 'purple1', 'purple2', 'purple3', 'white']


def tinted(sprite_name, prefix, color, amount):
    """A sprite's pack costumes blended `amount` of the way toward `color` (a palette name)."""
    out = []
    tc = P[color]
    for c in ST.costumes(sprite_name):
        im = ST.image_1x(sprite_name, c['name'])
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (round(r + (tc[0] - r) * amount), round(g + (tc[1] - g) * amount),
                                round(b + (tc[2] - b) * amount), a)
        out.append(make_costume(prefix + c['name'], up4(im), c['rotationCenterX'], c['rotationCenterY'], FILES))
    return out


def toned(sprite_name, ramp, prefix, suffix='', recolor_map=None):
    out = []
    for n, im, cx, cy in hollow_floor.tone_costumes(sprite_name, ramp, prefix, suffix=suffix) if recolor_map is None else []:
        out.append(make_costume(n, im, cx, cy, FILES))
    return out


def recolored(sprite_name, mapping, prefix=''):
    return [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in util.recolor_costumes(sprite_name, mapping, prefix)]


def anim_info_src(sprite_name):
    meta = json.load(open(assets.pack_path('sprites', 'characters', sprite_name, sprite_name + '.json')))
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


# Stage
stage = target('Stage', stage=True)
stage.costumes = copy_costumes('Stage', names=['title_', 'black'])
# backdrops and parallax layers are named by chapter number (9 = the epilogue, back in the Sump)
PACK_BG = {0: 'sump', 1: 'neon_alley', 6: 'server_gardens', 8: 'tenshu', 9: 'sump'}
NEW_BG = {2: (vaults.sky, vaults.far, vaults.mid),
          3: (sewers.sewer_sky, sewers.sewer_far, sewers.sewer_mid),
          4: (monorail.sky, monorail.far, monorail.mid),
          5: (hollow_floor.hollow_sky, hollow_floor.hollow_far, hollow_floor.hollow_mid),
          7: (academy.academy_sky, academy.academy_far, academy.academy_mid)}
PAR = {0: [], 1: [], 2: []}


def tenshu_sky():
    """The Tenshu's night sky without its moon, and the moon on its own (it sets as Hotaru
    climbs; see visuals.SKY). Returns (sky, moon, (moon centre x, y)) in 1x art pixels."""
    sky = ST.image_1x('Stage', 'sky_tenshu')
    px = sky.load()
    # the moon: the biggest patch of bright pixels up there (stars are single pixels)
    bright = {(x, y) for y in range(0, 100) for x in range(120, 230) if sum(px[x, y][:3]) > 330}
    best = set()
    while bright:
        todo = [bright.pop()]
        comp = set(todo)
        while todo:
            x, y = todo.pop()
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)):
                if q in bright:
                    bright.discard(q)
                    comp.add(q)
                    todo.append(q)
        if len(comp) > len(best):
            best = comp
    x0, x1 = min(p[0] for p in best), max(p[0] for p in best)
    y0, y1 = min(p[1] for p in best), max(p[1] for p in best)
    mx, my, r = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + 0.5
    moon = Image.new('RGBA', (x1 - x0 + 3, y1 - y0 + 3), (0, 0, 0, 0))
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if (x - mx) ** 2 + (y - my) ** 2 <= r * r:
                moon.putpixel((x - x0 + 1, y - y0 + 1), px[x, y])
    # the sky behind it: the same rows from further left (it's a vertical gradient with stars)
    for y in range(y0 - 2, y1 + 3):
        for x in range(x0 - 2, x1 + 3):
            if (x - mx) ** 2 + (y - my) ** 2 <= (r + 1.5) ** 2:
                px[x, y] = px[x - int(2 * r + 8), y]
    return sky, moon, (mx - x0 + 1, my - y0 + 1)


def dawn_sky():
    """The sunrise behind the Tenshu's clouds: violet overhead to gold at the horizon."""
    stops = [(0, (44, 30, 96)), (70, (150, 64, 140)), (115, (240, 120, 96)), (150, (255, 186, 98)), (180, (255, 222, 140))]
    im = Image.new('RGBA', (240, 180))
    for y in range(180):
        for (ya, ca), (yb, cb) in zip(stops, stops[1:]):
            if ya <= y <= yb:
                f = (y - ya) / (yb - ya)
                col = tuple(round(a + (b - a) * f) for a, b in zip(ca, cb)) + (255,)
        for x in range(240):
            im.putpixel((x, y), col)
    return im


def sun_disc():
    im = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    for y in range(48):
        for x in range(48):
            d = ((x - 23.5) ** 2 + (y - 23.5) ** 2) ** 0.5
            if d <= 13:
                im.putpixel((x, y), (255, 248, 214, 255) if d < 9 else (255, 224, 120, 255))
            elif d <= 23:
                im.putpixel((x, y), (255, 214, 120, int(150 * (23 - d) / 10)))
    return im


SKY8, MOON, MOON_C = tenshu_sky()
for ch in range(10):
    if ch == 8:
        stage.costumes.append(make_costume('sky_8', up4(SKY8), 480, 360, FILES))
        for li, layer in ((1, 'Parallax_far'), (2, 'Parallax_mid')):
            PAR[li] += copy_costumes(layer, names=['tenshu'], rename=lambda n: 'ch8')
        continue
    if ch in PACK_BG:
        k = PACK_BG[ch]
        stage.costumes += copy_costumes('Stage', names=['sky_' + k], rename=lambda n, ch=ch: 'sky_%d' % ch)
        for li, layer in ((1, 'Parallax_far'), (2, 'Parallax_mid')):
            if ch == 6 and li == 2:
                # the gardens' front layer: a thick band of blossoming trees
                PAR[li].append(make_costume('ch6', up4(gardens.garden_trees(ST.image_1x(layer, k))), 480, 360, FILES))
                continue
            PAR[li] += copy_costumes(layer, names=[k], rename=lambda n, ch=ch: 'ch%d' % ch)
    else:
        sky, far, mid = NEW_BG[ch]
        stage.costumes.append(make_costume('sky_%d' % ch, up4(sky()), 480, 360, FILES))
        PAR[1].append(make_costume('ch%d' % ch, up4(far()), 480, 360, FILES))
        PAR[2].append(make_costume('ch%d' % ch, up4(mid()), 480, 360, FILES))
stage.sounds = []
stage.current_costume = [c['name'] for c in stage.costumes].index('black')
scratchc.compile_sprite(stage, read_logic('stage.py'), C)

# the splash logo (art/splash_logo.png, any size), on white, filling the screen's height
_logo = Image.open(assets.art_path('splash_logo.png')).convert('RGBA')
_sc = min(640 / _logo.height, 900 / _logo.width)
_logo = _logo.resize((round(_logo.width * _sc), round(_logo.height * _sc)), Image.LANCZOS)
_splash = Image.new('RGBA', (960, 720), (255, 255, 255, 255))
_splash.alpha_composite(_logo, ((960 - _logo.width) // 2, (720 - _logo.height) // 2))
sprite('Warmup', [costume_from(Image.new('RGBA', (8, 8), P['steel'] + (255,)), 'square', 4, 4)], visuals.WARMUP)
sprite('Splash', [make_costume('splash', _splash, 480, 360, FILES)], visuals.SPLASH)
# the Tenshu's moon, and the dawn (behind the clouds)
sprite('Sky', [costume_from(MOON, 'moon', *MOON_C), costume_from(sun_disc(), 'sun', 24, 24),
               make_costume('dawn', up4(dawn_sky()), 480, 360, FILES)], visuals.SKY)
PAR_FAR = sprite('Parallax_far', PAR[1], visuals.parallax(0.05, 1))
PAR_MID = sprite('Parallax_mid', PAR[2], visuals.parallax(0.12, 9))
def ranks_image():
    # rows of hollowed soldiers, blacked out: the army waiting in the dark behind the hall
    fig = ST.image_1x('Mukuro', 'idle_0')
    bb = fig.getbbox()
    fig = fig.crop(bb)
    W, H = 280, 40
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for row, (col, lift, off) in enumerate(((P['night2'], 7, 6), (P['night1'], 3, 0), (P['ink'], 0, 3))):
        sil = Image.new('RGBA', fig.size, col + (255,))
        sil.putalpha(fig.getchannel('A'))
        for x in range(-4 + off, W, 13):
            im.alpha_composite(sil, (x, H - fig.height - lift))
    return im


sprite('Ranks', [costume_from(ranks_image(), 'ranks', 140, 40)], visuals.RANKS)
sprite('GlitchBG', [costume_from(hollow_floor.glitch_piece(i), 'glitch_%d' % i, hollow_floor.glitch_piece(i).width / 2, hollow_floor.glitch_piece(i).height / 2) for i in range(12)], visuals.GLITCHBG)
sprite('Level', ROOM_COSTUMES, visuals.LEVEL)
def mk_slump(name='slump'):
    # the last kneeling frame of Mukuro's death, held solid, with his visor lights gone out
    c = ST.costume('Mukuro', 'death_2')
    im = edits.mukuro_image(ST, 'death_2')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and r > 150 and g < 100:  # the visor reds, not his skin
                px[x, y] = P['red1'] + (a,)
    return make_costume(name, im, c['rotationCenterX'], c['rotationCenterY'], FILES)


props = []
props += copy_costumes('RamenCart', rename=lambda n: 'cart_' + n)
props += copy_costumes('Lantern', rename=lambda n: 'lantern_' + n)
for s, k in (('NeonSign_Ramen', 'ramen'), ('NeonSign_Ninja', 'ninja'), ('NeonSign_Bar', 'bar'), ('NeonSign_Danger', 'danger')):
    props += copy_costumes(s, rename=lambda n, k=k: k + '_' + n)
for i in range(2):
    props.append(costume_from(vaults.pachinko_prop(i), 'pachinko_%d' % i, 8, 30))
jp_on, jp_off = vaults.jackpot_sign(True), vaults.jackpot_sign(False)
props.append(costume_from(jp_on, 'jackpot_on_0', jp_on.width / 2, 0))
for i in range(8):
    im = jp_on if i in (0, 2, 3, 6) else jp_off
    props.append(costume_from(im, 'jackpot_flicker_%d' % i, im.width / 2, 0))
props += copy_costumes('ServerRack', rename=lambda n: 'rack_' + n)
props += [costume_from(gardens.pod(i), 'pod_%d' % i, 7, 30) for i in range(2)]
props += [costume_from(gardens.toro(i), 'toro_%d' % i, 6, 22) for i in range(2)]
props.append(costume_from(gardens.bonsai(), 'bonsai', 7, 18))
props.append(costume_from(monorail.seat(), 'seat', 9, 12))
props.append(costume_from(academy.dummy(), 'dummy', 7, 26))
props += [costume_from(gardens.planter(i), 'planter_%d' % i, 8, 24) for i in range(2)]
props.append(costume_from(gardens.herbs(), 'herbs', 7, 30))
props += [costume_from(gardens.price_board(i), 'board_%d' % i, 38, 0) for i in range(2)]
props += [costume_from(npcs.civilian(i, f), 'debtor_%d_%d' % (i, f), 7, 28) for i in range(npcs.CIVILIANS) for f in range(2)]
# turned to face left (the Vaults' line, headed for its door), and running left
props += [costume_from(npcs.civilian(i, f).transpose(Image.FLIP_LEFT_RIGHT), 'debtorl_%d_%d' % (i, f), 7, 28)
          for i in range(npcs.CIVILIANS) for f in range(2)]
props += [costume_from(npcs.civilian_run(i, f).transpose(Image.FLIP_LEFT_RIGHT), 'debtorrun_%d_%d' % (i, f), 7, 28)
          for i in range(npcs.CIVILIANS) for f in range(4)]
# the Vaults debtors' minder: the suit grunt, facing left, standing and running
_suit = edits.suit_frames(ST)
props += [costume_from(_suit['idle_%d' % k].transpose(Image.FLIP_LEFT_RIGHT), 'escort_idle_%d' % k, 24, 37) for k in range(4)]
props += [costume_from(_suit['walk_%d' % k].transpose(Image.FLIP_LEFT_RIGHT), 'escort_run_%d' % k, 24, 37) for k in range(6)]
# the epilogue's hollowed soldier: a Tenshu trainee (the Muster Hall's look) idling, facing left
props += [make_costume('soldier_%s' % n[len('h_idle_'):], im.transpose(Image.FLIP_LEFT_RIGHT), im.width - cx, cy, FILES)
          for n, im, cx, cy in util.recolor_costumes('Mukuro', tenshu.SOLDIER_MAP, 'h_') if n.startswith('h_idle_')]
props += [costume_from(npcs.desk(f), 'desk_%d' % f, 36, 30) for f in range(2)]
props.append(costume_from(npcs.desk(staffed=False), 'desk_empty', 36, 30))
_dir = npcs.directory()
props.append(costume_from(_dir, 'directory', _dir.width / 2, 0))


for k in range(4):
    c = ST.costume('Mukuro', 'idle_%d' % k)
    im = edits.mukuro_image(ST, 'idle_%d' % k).transpose(Image.FLIP_LEFT_RIGHT)
    props.append(make_costume('mk_idle_%d' % k, im, im.width - c['rotationCenterX'], c['rotationCenterY'], FILES))
props.append(mk_slump('mk_lie'))
for k in range(4):
    c = ST.costume('Mukuro', 'idle_%d' % k)
    props.append(make_costume('mk_idr_%d' % k, edits.mukuro_image(ST, 'idle_%d' % k), c['rotationCenterX'], c['rotationCenterY'], FILES))
for k in range(8):
    c = ST.costume('Mukuro', 'run_%d' % k)
    im = edits.mukuro_image(ST, 'run_%d' % k)
    props.append(make_costume('mk_runr_%d' % k, im, c['rotationCenterX'], c['rotationCenterY'], FILES))
    props.append(make_costume('mk_runl_%d' % k, im.transpose(Image.FLIP_LEFT_RIGHT), im.width - c['rotationCenterX'], c['rotationCenterY'], FILES))
sprite('Props', props, CL + objects.PROPS)
pb = [costume_from(hollow_floor.phase_block(st_, h), '%s_%s' % ('hb' if h else 'gb', st_), 4, 4)
      for h in (False, True) for st_ in ('on', 'warn', 'soon', 'off')]
sprite('PhaseBlock', pb, CL + objects.PHASEBLOCK)
sprite('Mist', [costume_from(gardens.heat_vent(i), 'mist_%d' % i, 8, 8) for i in range(gardens.MIST_FRAMES)]
       + [costume_from(sewers.sludge_fall(i), 'falls_%d' % i, 8, 8) for i in range(8)], CL + objects.MIST)
slot_cos = [costume_from(vaults.slot_machine(i), 'slot_%d' % i, 40, 38) for i in range(2)]
sprite('SlotMachine', slot_cos, CL + enemies.SLOT_MACHINE)
reel_cos = [costume_from(vaults.symbol(n), 'sym_' + n, 6, 7) for n in vaults.SYMBOLS]
reel_cos += [costume_from(vaults.reel_blur(i), 'blur_%d' % i, 6, 7) for i in range(2)]
SLOT_CALLOUTS = {'spade': 'CARD FAN!', 'seven': 'RAPID FIRE!', 'cherry': 'DASH SLASH!',
                 'skull': 'SHOCKWAVE!', 'jackpot': 'LASERS!'}
for sym, text in SLOT_CALLOUTS.items():
    w = BOLD.width(text) + 12
    im = panel_image(w, 15, fill='ink', border='gold', accent='red2')
    BOLD.draw(im, 6, 3, text, P['red2'] if sym in ('skull', 'jackpot') else P['yellow'], P['ink'])
    reel_cos.append(costume_from(im, 'call_' + sym, w / 2, 7))
sprite('Reels', reel_cos, CL + enemies.REELS)
sprite('Breakable', BREAK_COSTUMES, CL + FX + objects.BREAKABLE)
sprite('LaserBarrier', copy_costumes('LaserBarrier'), CL + objects.LASER)
sprite('SecurityDoor', copy_costumes('SecurityDoor'), CL + EN + objects.DOOR)
sprite('ShrineTerminal', copy_costumes('ShrineTerminal'), CL + FX + objects.SHRINE)
sprite('Pickup', PICKUP_COSTUMES, CL + FX + objects.PICKUP)
sprite('MemoryShard', copy_costumes('MemoryShard'), CL + FX + EN + objects.SHARD)
sprite('ShockPuddle', copy_costumes('ShockPuddle'), CL + objects.PUDDLE)
sprite('MovingPlatform', copy_costumes('MovingPlatform'), CL + objects.LIFT)
sprite('Crate', copy_costumes('Crate'), CL + EN + objects.CRATE)
sprite('Tetsu', copy_costumes('Tetsu'), CL + objects.TETSU)
sprite('DaiCam', copy_costumes('DaiCam'), CL + EN + objects.DAICAM)
sprite('Cage', [costume_from(vaults.cage(i), 'cage_%d' % i, 14, 40) for i in range(3)], CL + FX + EN + objects.CAGE)
sprite('CamDrone', copy_costumes('CamDrone'), CL + objects.CAMDRONE)
sprite('Turret', copy_costumes('Turret'), CL + FX + EN + enemies.TURRET)
sprite('SlotTurret', recolored('Turret', vaults.SLOT_TURRET_MAP), CL + FX + EN + enemies.SLOT_TURRET)
sprite('Croupier', [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in edits.croupier_costumes(ST) + edits.gunner_costumes(ST)], CL + FX + EN + enemies.CROUPIER)
drain_cos = []
for i, c in enumerate(ST.costumes('HannyaBoy')):
    im = sewers.drainling_frame(ST.image_1x('HannyaBoy', c['name']), i)
    drain_cos.append(make_costume('d_' + c['name'], up4(im), c['rotationCenterX'], c['rotationCenterY'], FILES))
# from the Vaults on, the grunts are men in black suits (u_); in the Hollow Floor, a memory of one (m_)
suit = edits.suit_costumes(ST, 'u_')
suit_mem = [('m_' + n[2:], hollow_floor.tone(im, MEM_RAMP, stretch=True), cx, cy) for n, im, cx, cy in suit]
# the Slums memory's Hannya Boy, toned like the rest of Kuro's memories (mg_)
suit_mem += [('mg_' + c['name'], hollow_floor.tone(up4(ST.image_1x('HannyaBoy', c['name'])), MEM_RAMP, stretch=True),
              c['rotationCenterX'], c['rotationCenterY']) for c in ST.costumes('HannyaBoy')]
sprite('HannyaBoy', copy_costumes('HannyaBoy') + [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in suit + suit_mem]
       + drain_cos, CL + FX + EN + enemies.HANNYA)
sprite('BigOni', copy_costumes('BigOni'), CL + FX + EN + enemies.ONI)
SPRAYER_MAP = {'slate3': 'white', 'slate2': 'steel', 'steel': 'green2', 'slate1': 'green1', 'red3': 'lime'}
# Hollow Floor's drones (h_) are memories: a slight violet cast
sprite('ScavDrone', copy_costumes('ScavDrone') + recolored('ScavDrone', SPRAYER_MAP, 'p_') + tinted('ScavDrone', 'h_', 'purple2', 0.3),
       CL + FX + EN + enemies.DRONE)
sprite('LadyLuck', [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in edits.luck_costumes(ST)], CL + FX + EN + enemies.LUCK)
sprite('Warden', recolored('Mukuro', gardens.WARDEN_MAP) + toned('Mukuro', MEM_RAMP, 'm_') + recolored('Mukuro', academy.TRAINEE_MAP, 's_')
       + recolored('Mukuro', tenshu.SOLDIER_MAP, 'h_'), CL + FX + EN + enemies.WARDEN)
sprite('KuroBoss', copy_costumes('Kuro'), CL + FX + EN + enemies.KUROBOSS)
dm = []
# phase 1: the user's samurai mech, animated from its parts (mech.py), 2 screen px per art px
for _n, (_im, (_ax, _ay)) in mech.frames().items():
    _bb = _im.getbbox()
    dm.append(costume_from(_im.crop(_bb), _n, _ax - _bb[0], _ay - _bb[1]))
# phase 2: the mech's eye, wired into the castle (open, half-lidded, shut), 2 screen px per art px,
# turned to look right like every other sprite; feet (bottom centre) at its anchor
for _i, _n in enumerate(('eye_open', 'eye_half', 'eye_shut')):
    _im = Image.open(assets.art_path('characters', 'daimyo_mech', 'eye_sheet.png')).convert('RGBA')
    _im = _im.crop((1 + 32 * _i, 9, 31 + 32 * _i, 39)).transpose(Image.FLIP_LEFT_RIGHT)
    _px = _im.load()
    for _y in range(_im.height):
        for _x in range(_im.width):
            _px[_x, _y] = _px[_x, _y][:3] + (255,) if _px[_x, _y][3] >= 128 else (0, 0, 0, 0)
    dm.append(costume_from(_im, _n, _im.width / 2, _im.height - 1))
# the Daimyo in person: the user's 80x64 frames (art/characters/daimyo), feet at (40, 61),
# drawn at 1.5 screen pixels per art pixel so he stands as tall as Hotaru
_DMF = assets.art_path('characters', 'daimyo')
for _folder in sorted(os.listdir(_DMF)):
    _anim = _folder.split('_', 1)[1]
    for _f in sorted(os.listdir(os.path.join(_DMF, _folder))):
        _i = int(_f.rsplit('_', 1)[1].split('.')[0])
        dm.append(costume_small(Image.open(os.path.join(_DMF, _folder, _f)).convert('RGBA'),
                                'dmf_%s_%d' % (_anim, _i), 40, 61))
dm.append(costume_from(tenshu.cable(), 'cable', 3, 110))
dm += copy_costumes('Turret', names=['idle_0'], rename=lambda n: 'turret')
dm += [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in edits.mukuro_costumes(ST, 'mk_', ['idle_', 'run_', 'attack1_', 'attack2_', 'attack3_', 'heavy_', 'deflect_', 'dash_', 'hurt_'])]
dm += copy_costumes('MemoryShard', names=['spin_'], rename=lambda n: n.replace('spin_', 'shard_'))
dm.append(mk_slump('mk_lie'))
sprite('Daimyo', dm, CL + FX + EN + enemies.DAIMYO)
dobu_cos = [costume_from(sewers.dobu_body('idle', i), 'dobu_idle_%d' % i, sewers.DOBU_W / 2, sewers.DOBU_H) for i in range(2)]
dobu_cos += [costume_from(sewers.dobu_body('open', i), 'dobu_open_%d' % i, sewers.DOBU_W / 2, sewers.DOBU_H) for i in range(2)]
dobu_cos += [costume_from(sewers.dobu_body('spew', 0), 'dobu_spew', sewers.DOBU_W / 2, sewers.DOBU_H)]
dobu_cos += [costume_from(sewers.dobu_body('dead', i), 'dobu_dead_%d' % i, sewers.DOBU_W / 2, sewers.DOBU_H) for i in range(4)]
dobu_cos += [costume_from(sewers.dobu_arm(i), 'dobu_arm_%d' % i, 0, 11) for i in range(2)]
dobu_cos.append(costume_from(sewers.dobu_arm(0, True), 'dobu_stump', 0, 11))
sprite('Dobunushi', dobu_cos, CL + FX + EN + enemies.DOBU)
harm_cos = []
for _anim, _fs in gardens.harm_frames().items():
    for _i, _im in enumerate(_fs):
        harm_cos.append(costume_crop(_im, 'harm_%s_%d' % (_anim, _i), *gardens.HARM_ANCHOR))
        if _anim != 'death':
            harm_cos.append(costume_crop(gardens.harm_juiced(_im, _i), 'harmj_%s_%d' % (_anim, _i), *gardens.HARM_ANCHOR))
sprite('Harmacist', harm_cos, CL + FX + EN + enemies.HARM)
sprite('Mukuro', [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in edits.mukuro_costumes(ST)] + [mk_slump()], CL + FX + EN + enemies.MUKURO)
rj_cut = lambda im: im.crop((0, 0, monorail.RJ_W, monorail.RJ_CUT))
rj = [costume_from(rj_cut(monorail.raijin('idle', i)), 'rj_idle_%d' % i, *monorail.RJ_CORE) for i in range(2)]
rj += [costume_from(rj_cut(monorail.raijin('vent', i)), 'rj_vent_%d' % i, *monorail.RJ_CORE) for i in range(2)]
rj += [costume_from(rj_cut(monorail.raijin('fire', 0)), 'rj_fire', *monorail.RJ_CORE),
       costume_from(rj_cut(monorail.raijin('dead', 0)), 'rj_dead', *monorail.RJ_CORE)]
rj += [costume_from(monorail.arm(i), 'arm_%d' % i, 0, 7) for i in range(2)]
rj += [costume_from(monorail.plow(i), 'plow_%d' % i, 22, 14) for i in range(2)]
rj += [costume_from(monorail.zap(False, i), 'zapw_%d' % i, 30, 10) for i in range(2)]
rj += [costume_from(monorail.zap(True, i), 'zapl_%d' % i, 30, 10) for i in range(3)]
sprite('Raijin', rj, CL + FX + EN + enemies.RAIJIN)
sprite('TrackPost', [costume_from(monorail.robo_crow(i), 'crow_%d' % i, 12, 7) for i in range(2)] + [costume_from(monorail.warn(i), 'warn_%d' % i, 7, 7) for i in range(2)],
       CL + EN + enemies.TRACKPOST)
sprite('SweepLaser', copy_costumes('LaserBarrier', names=['on_']), CL + EN + enemies.SWEEP)
sprite('Kuro', copy_costumes('Kuro', names=['idle_']), visuals.KURO)
hotaru_src = read_logic('hotaru.py') + FX + anim_info_src('Hotaru') + atk_info_src()
sprite('Hotaru', [make_costume(n, im, cx, cy, FILES) for n, im, cx, cy in edits.hotaru_costumes(ST)], hotaru_src)
sprite('SlashFX', copy_costumes('SlashFX'), '''
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
''')
proj_costumes = copy_costumes('Projectiles', names=['bullet_']) + WAVE_COSTUMES
proj_costumes += [costume_from(tenshu.crescent(i), 'crescent_%d' % i, 7, 10) for i in range(2)]
proj_costumes += [costume_from(f, 'card_%d' % i, 4.5, 4.5) for i, f in enumerate(vaults.card_frames())]
proj_costumes += [costume_from(monorail.shell(i), 'shell_%d' % i, 4, 4) for i in range(2)]
proj_costumes += [costume_from(monorail.shell(i, True), 'rshell_%d' % i, 4, 4) for i in range(2)]
proj_costumes += [costume_from(tenshu.orb(i), 'orb_%d' % i, 4, 4) for i in range(2)]
proj_costumes += [costume_from(sewers.spit(i), 'spit_%d' % i, 4, 4) for i in range(2)]
proj_costumes += [costume_from(gardens.vial(i), 'vial_%d' % i, 4, 4) for i in range(2)]
proj_costumes += [costume_from(gardens.cloud(i), 'cloud_%d' % i, 16, 22) for i in range(2)]
proj_costumes += [costume_from(gardens.cloud(i, True), 'cloudb_%d' % i, 24, 28) for i in range(2)]
# the sludge tide draws over the fighters (they wade in it), under the effects and HUD
def tide_warn(on):
    # the visual half of the pump gurgle: a hazard plate with rising arrows
    tim = text_image(['TIDE RISING'], BOLD, P['yellow'] if on else P['orange'], shadow=P['ink'])
    w = tim.width + 36
    im = panel_image(w, 17, fill='ink', alpha=220, border='yellow' if on else 'orange', accent=None)
    im.alpha_composite(tim, (18, 3))
    d = ImageDraw.Draw(im)
    col = P['lime'] if on else P['green2']
    for x0 in (5, w - 14):
        for k, dy in enumerate((0, 5)):
            d.polygon([(x0 + 4, 3 + dy), (x0 + 8, 7 + dy), (x0, 7 + dy)], fill=col)
    return im


sprite('Sludge', [costume_from(sewers.tide_surface(i), 'tide_%d' % i, 122, 0) for i in range(4)]
       + [costume_from(tide_warn(k), 'tide_warn_%d' % k, tide_warn(k).width / 2, 8) for k in range(2)], objects.SLUDGE)
sprite('Projectiles', proj_costumes, CL + FX + EN + objects.PROJECTILES)
sprite('MoveFX', copy_costumes('MoveFX'), CL + visuals.fx_sprite('mq', visuals.MOVE_FX))
sprite('CombatFX', copy_costumes('CombatFX'), CL + visuals.fx_sprite('cq', visuals.COMBAT_FX))
sprite('Rain', copy_costumes('Rain') + [make_costume('wind_%d' % i, up4(monorail.wind(i)), 480, 360, FILES) for i in range(4)]
       + [make_costume('possess', up4(hollow_floor.possess()), 480, 360, FILES)], visuals.RAIN)
sprite('Flash', FLASH_COSTUMES, visuals.FLASH)
eui = copy_costumes('HUD', names=['enemy_int_']) + copy_costumes('CombatFX', names=['breach_', 'severance_'])
sprite('EnemyUI', eui, CL + visuals.ENEMY_UI)
def snug_hp(name):
    # the pack's bar has room for 12 segments; close it up around Hotaru's 10
    im = ST.image_1x('HUD', name)
    out = Image.new('RGBA', (im.width - 8, im.height), (0, 0, 0, 0))
    out.paste(im.crop((0, 0, 52, im.height)), (0, 0))
    out.paste(im.crop((60, 0, im.width, im.height)), (52, 0))
    return costume_from(out, name, 0, 0)


hud = [snug_hp('hp_%02d' % k) for k in range(11)]
hud += [costume_from(ST.image_1x('HUD', src).crop((0, 0, 8, 9)), 'dash_%d' % i, 0, 0) for i, src in enumerate(('dash_0', 'dash_2', 'dash_1'))]
hud += copy_costumes('HUD', names=['gourd_', 'heat_', 'integrity_', 'boss_']) + copy_costumes('NamePlates', names=['boss_big_oni', 'boss_lady_luck', 'boss_mukuro', 'boss_raijin', 'boss_kuro', 'boss_the_daimyo'])
hud += [costume_from(ui.boss_plate(t), 'boss_' + k, 0, 0) for k, t in (('dobunushi', 'DOBUNUSHI'), ('the_harmacist', 'THE HARMACIST'))]
# the stopwatch, top right: one costume per character, centred in a 6 px cell, top at the anchor,
# lettered like the flask's charge count (the regular face in white with a dark outline all round)
def outlined_char(ch):
    t = text_image([ch], REG, P['white'])
    a = t.split()[3]
    out = Image.new('RGBA', (t.width + 2, t.height + 2), (0, 0, 0, 0))
    ink = Image.new('RGBA', t.size, P['ink'] + (255,))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            out.paste(ink, (1 + dx, 1 + dy), a)
    out.alpha_composite(t, (1, 1))
    return out


for _ch in '0123456789:':
    _t = outlined_char(_ch)
    hud.append(costume_from(_t, 'clk_' + _ch, _t.width / 2 - 0.5, 0))
sprite('HUD', hud, visuals.HUD)
hint_cos = HINT_COSTUMES + copy_costumes('KeyPrompts', names=['key_e'])
sprite('Hints', hint_cos, visuals.HINTS)
_ex = ui.banner_word('EXECUTION')
# a boss's defeat reads ENEMY FELLED (the pack's banner said TARGET SEVERED)
_felled = ui.banner_word('ENEMY FELLED')
ban = ([c for c in copy_costumes('Banners') if c['name'] != 'victory']
       + [costume_from(_felled, 'victory', _felled.width / 2, _felled.height / 2)]
       + [costume_from(_ex, 'execution', _ex.width / 2, _ex.height / 2)]) + [costume_from(ui.chapter_card(i), 'ch%d' % i, 100, 22) for i in range(9)]
epi = panel_image(200, 44, border='mag3', accent='cyan3')
REG.draw(epi, 10, 6, 'THE END OF THE CLIMB', P['mag3'], P['ink'])
et = text_image(['EPILOGUE'], BOLD, P['cyan3'], shadow=P['mag2'])
epi.alpha_composite(et.resize((et.width * 2, et.height * 2), Image.NEAREST), (10, 18))
ban.append(costume_from(epi, 'epi', 100, 22))
sprite('Banners', ban, visuals.BANNERS)
def sheet_portraits():
    # every dialogue portrait comes from art/portraits.png (made by export_portraits.py);
    # edit that sheet to change them. Cell order is in art/portraits.json.
    path = assets.art_path('portraits', 'portraits.png')
    meta = json.load(open(assets.art_path('portraits', 'portraits.json')))
    sheet = Image.open(path).convert('RGBA')
    cell = meta['cell']
    out = []
    for p in meta['portraits']:
        im = sheet.crop((p['col'] * cell, p['row'] * cell, (p['col'] + 1) * cell, (p['row'] + 1) * cell))
        out.append(costume_from(im, p['name'], cell / 2, cell / 2))
        if p['name'].startswith('kuro_'):
            # Kuro's portrait glitches now and then while he talks
            for k in (1, 2):
                out.append(costume_from(export_portraits.kuro_glitch(im, k), '%s_g%d' % (p['name'], k), cell / 2, cell / 2))
    missing = set(dialogue.PORTRAIT.values()) - {p['name'] for p in meta['portraits']}
    assert not missing, 'portraits missing from art/portraits/portraits.png: %s' % missing
    return out


def dialogue_box():
    """The pack's dialogue box with its text panel made opaque, and the strips that hide
    the untyped part of each line: crops of that same panel, so they match it exactly.
    The box draws at (0, 128) with its centre at (116, 24) in box pixels (2 stage px each);
    a line's text spans 16.5 stage px, which 9 box rows cover, starting at rows 15, 23 and
    31 (all odd, so the panel's scanlines line up for one set of strips)."""
    c = ST.costume('Dialogue', 'box')
    box = ST.image_1x('Dialogue', 'box')
    px = box.load()
    for y in range(box.height):
        for x in range(box.width):
            if 200 <= px[x, y][3] < 255:
                px[x, y] = px[x, y][:3] + (255,)
    right, top, rows = 224, 15, 9
    for y in range(top, 31 + rows):
        for x in range(48, right):
            assert px[x, y] == px[100, top + (y - top) % 2], ('dialogue panel not plain at', x, y)
    out = [make_costume('box', up4(box), c['rotationCenterX'], c['rotationCenterY'], FILES)]
    for k in range(89):
        w = max(1, 2 * k)
        strip = box.crop((right - w, top, right, top + rows))
        if k == 0:
            strip = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        out.append(costume_from(strip, 'mask_%d' % k, 116 - (right - w), 24 - top))
    return out


_box = dialogue_box()
dlg = ([_box[0]] + copy_costumes('Dialogue', names=['next_']) + _box[1:] + sheet_portraits()
       + copy_costumes('NamePlates', names=['name_']) + DLG_COSTUMES)
dlg.append(costume_from(ui.nameplate('LADY LUCK'), 'name_lady_luck', 0, 0))
dlg.append(costume_from(ui.nameplate('SYSTEM', border='cyan2'), 'name_system', 0, 0))
dlg.append(costume_from(ui.nameplate('BIG ONI', border='red2'), 'name_big_oni', 0, 0))
dlg.append(costume_from(ui.nameplate('THE HARMACIST', border='green2'), 'name_the_harmacist', 0, 0))
dlg.append(costume_from(ui.nameplate('DEBTOR', border='steel'), 'name_debtor', 0, 0))
dlg.append(costume_from(ui.nameplate('RECEPTIONIST', border='cyan2'), 'name_receptionist', 0, 0))
dlg.append(costume_from(ui.nameplate('KANSHI ASSOCIATE', border='cyan2'), 'name_kanshi_associate', 0, 0))
sprite('Dialogue', dlg, visuals.DIALOGUE)
sprite('Menu', MENU_COSTUMES, menu.MENU)
sprite('TextFX', copy_costumes('Font'), menu.TEXTFX)
sprite('Fade', FADE_COSTUMES, visuals.FADE)
sprite('SFX', [FADE_COSTUMES[0]], visuals.SFX, sounds=audio.SFX_NAMES)
for track, length in audio.MUSIC.items():
    sprite('Music_' + track, [FADE_COSTUMES[0]], visuals.music(track, length), sounds=[track])
sprite('Music_drums', [FADE_COSTUMES[0]], visuals.music('boss_drums', audio.MUSIC['boss'], drums=True),
       sounds=['boss_drums'])
sprite('Music_luck_drums', [FADE_COSTUMES[0]], visuals.music('luck_drums', audio.MUSIC['luck'], drums=True, drums_for='luck'),
       sounds=['luck_drums'])
sprite('Music_mukuro_drums', [FADE_COSTUMES[0]], visuals.music('mukuro_drums', audio.MUSIC['mukuro'], drums=True, drums_for='mukuro'),
       sounds=['mukuro_drums'])
sprite('Music_raijin_drums', [FADE_COSTUMES[0]], visuals.music('raijin_drums', audio.MUSIC['raijin'], drums=True, drums_for='raijin'),
       sounds=['raijin_drums'])
for tr in ('kuro', 'daimyo', 'dobu', 'harm'):
    sprite('Music_%s_drums' % tr, [FADE_COSTUMES[0]], visuals.music(tr + '_drums', audio.MUSIC[tr], drums=True, drums_for=tr),
           sounds=[tr + '_drums'])
sprite('Ambience', [FADE_COSTUMES[0]], visuals.AMBIENCE, sounds=['rain_loop', 'wind_loop'])

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
