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
import levels  # noqa: E402
import scratchc  # noqa: E402
from assets import PALETTE as P, make_costume, up4  # noqa: E402
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
tool_n tool_max dash_ch hitstop shake shake_amp shx shy flash fade fade_to
kL kR kU kD kA kZ kS kH kQ kE kN kP pU pD pL pR pA pZ pS pH pQ pE p_ok p_click p_pause p_any
opt_wide opt_slow opt_heat opt_gourd opt_god opt_music opt_sfx opt_shake
banner banner_t card hint prompt_on prompt_x prompt_y dlg_req dlg_on dlg_spk dlg_port dlg_txt dlg_nm dlg_name
boss_on boss_hp boss_int boss_slot boss_phase boss_dead ambush_on mp_on mp_x mp_y lift_ride
cp_room cp_x cp_y has_save shards shard_id deaths play_time daicam_done cam_x cam_y music_cur music_want
first tstr pfr slash_fx slash_off dlg_t msel press_t chap_i
'''.split()

GLOBAL_LISTS = '''
grid R_GRID R_LEVEL R_CH R_L R_R R_U R_D R_BOSS O_FIRST O_NUM O_TYPE O_X O_Y O_A O_B
ent_type ent_x ent_y ent_w ent_h ent_hp ent_int ent_imax ent_alive ent_stag ent_dmg ent_idmg ent_kb ent_hk
ent_foe ent_obj ent_brk ent_sev hq_t hq_d hq_x cq_t cq_x cq_y cq_d mq_t mq_x mq_y mq_d
pq_t pq_x pq_y pq_vx pq_vy pk_x pk_y pz_x pz_y brk_hits sfxq ui_slot ui_role
trig_x trig_ev trig_on dead_objs seen got_shards broken
CONV_NAME CONV_START CONV_LEN DL_SPK DL_PORT DL_TEXT DL_NAME
MI_KEY MI_X MI_Y MI_KIND HUD_ROLES DLG_ROLES FONT_W
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
set_list('R_CH', [r.chapter for r in ROOMS])
for d in 'LRUD':
    set_list('R_' + d, [RI[r.exits[d]] if d in r.exits else 0 for r in ROOMS])
set_list('R_BOSS', [1 if 'boss' in r.flags else 0 for r in ROOMS])
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
C.update({
    'C_ROOM_P1': RI['p1'], 'C_ROOM_A1': RI['a1'], 'C_A1_X': a1_start['x'], 'C_A1_Y': a1_start['y'],
    'C_LIFT_LOW': -200, 'C_LIFT_TOP': levels.top(19),
    'C_G': 1.5, 'C_JUMP': 16.5, 'C_WALLJUMP': 15, 'C_BOOST': 18, 'C_RUN': 6, 'C_MAXFALL': 13,
    'C_SLIDE': 3, 'C_DASHV': 21.3, 'C_DASHF': 6, 'C_HW': 7, 'C_PH': 34, 'C_COYOTE': 3,
    'C_JBUF': 4, 'C_PARRY': 6, 'C_PARRY_WIDE': 12, 'C_OVERHEAT': 36, 'C_IFRAMES': 30,
    'C_HEAL': 4, 'C_COMBO': 11,
})

# ------------------------------------------------------------------ dialogue pages
DLG_COSTUMES = []
CONV_NAME, CONV_START, CONV_LEN, DL_SPK, DL_PORT, DL_TEXT, DL_NAME = [], [], [], [], [], [], []
page_no = 0
for cname, lines in dialogue.CONVERSATIONS.items():
    CONV_NAME.append(cname)
    CONV_START.append(len(DL_SPK) + 1)
    n = 0
    for spk, port, text in lines:
        wrapped = REG.wrap(text, 178)
        for i in range(0, len(wrapped), 3):
            page = wrapped[i:i + 3]
            page_no += 1
            name = 'txt_%d' % page_no
            DLG_COSTUMES.append(costume_from(text_image(page, width=178), name, 0, 0))
            DL_SPK.append('kuro' if spk == 'unknown' else spk)
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
set_list('HUD_ROLES', ['hp', 'dash', 'gourd', 'tool', 'tcount', 'heat', 'bplate', 'bbar', 'bint'])
set_list('DLG_ROLES', ['box', 'port', 'name', 'text', 'arrow'])
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
        else:
            rows[-1].append(('gap', 6))
    widths = [sum(p[1].width if p[0] == 'img' else p[1] for p in r) + 3 * (len(r) - 1) for r in rows]
    w = 8 + max(widths)
    rh = 17
    h = 4 + rh * len(rows)
    im = panel_image(w, h, alpha=215, accent=None, border='slate3')
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


HINT_COSTUMES = []
for k, v in dialogue.HINTS.items():
    him = hint_image(v)
    HINT_COSTUMES.append(costume_from(him, 'hint_' + k, him.width / 2, him.height / 2))

# ------------------------------------------------------------------ menu images
MENU_COSTUMES = []
MENU_COSTUMES += copy_costumes('Buttons')
MENU_COSTUMES += copy_costumes('MenuCursor')
MENU_COSTUMES += copy_costumes('Panels')
MENU_COSTUMES += copy_costumes('ChapterCards')
MENU_COSTUMES += copy_costumes('KeyPrompts', names=['key_left', 'key_right'])
MENU_COSTUMES += copy_costumes('Banners', names=['press_any_key'])
big = panel_image(232, 176)
MENU_COSTUMES.append(costume_from(big, 'panel', 116, 88))
for key, label, col in (('ttl_options', 'OPTIONS', 'cyan3'), ('ttl_chapters', 'CHAPTERS', 'cyan3'), ('ttl_assist', 'ASSIST MODE', 'mag3')):
    im = text_image([label], BOLD, P[col], shadow=P['mag2'] if col == 'cyan3' else P['ink'])
    MENU_COSTUMES.append(costume_from(im, key, im.width / 2, 4.5))
for key, label in dialogue.OPTION_LABELS.items():
    im = text_image([label], REG, P['white'], shadow=P['ink'])
    assert im.width <= 128, ('option label too wide', label, im.width)
    MENU_COSTUMES.append(costume_from(im, 'lbl_' + key, 0, 5))
values = {'on': 'ON', 'off': 'OFF', 'view': 'VIEW'}
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


for key, rows, w in (('credits_page', dialogue.CREDITS, 220), ('controls_page', dialogue.CONTROLS, 222),
                     ('end_page', dialogue.END_PAGE, 236)):
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

tcount = []
for i in range(6):
    im = text_image(['x%d' % i], BOLD, P['white'], shadow=P['ink'])
    tcount.append(costume_from(im, 'tcount_%d' % i, 0, 0))

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
tiles_alley = assets.tile_images('alley')
BREAK_COSTUMES = [costume_from(tiles_alley['breakable'], 'breakable', 4, 4),
                  costume_from(tiles_alley['breakable_cracked'], 'breakable_cracked', 4, 4)]
ROOM_COSTUMES = [make_costume('room_' + r.key, up4(assets.render_room(r)), 0, 0, FILES) for r in ROOMS]

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
    'plunge': (1, 2, 1, 0, '', 0, 'plunge'),
    'heavy': (2, 3, 3, 10, 'heavy', 2, 'heavy'),
    'severance': (1, 0, 0, 0, '', 0, 'sever_draw'),
    'throw': (1, 0, 0, 0, '', 0, 'throw'),
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
stage.costumes = copy_costumes('Stage', names=['title_', 'sky_sump', 'sky_neon_alley', 'black'])
stage.sounds = []
scratchc.compile_sprite(stage, read_logic('stage.py'), C)

PAR_FAR = sprite('Parallax_far', copy_costumes('Parallax_far', names=['sump', 'neon_alley']), visuals.parallax(0.05))
PAR_MID = sprite('Parallax_mid', copy_costumes('Parallax_mid', names=['sump', 'neon_alley']), visuals.parallax(0.12))
sprite('Level', ROOM_COSTUMES, visuals.LEVEL)
props = []
props += copy_costumes('RamenCart', rename=lambda n: 'cart_' + n)
props += copy_costumes('Lantern', rename=lambda n: 'lantern_' + n)
for s, k in (('NeonSign_Ramen', 'ramen'), ('NeonSign_Ninja', 'ninja'), ('NeonSign_Bar', 'bar'), ('NeonSign_Danger', 'danger')):
    props += copy_costumes(s, rename=lambda n, k=k: k + '_' + n)
sprite('Props', props, CL + objects.PROPS)
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
sprite('CamDrone', copy_costumes('CamDrone'), CL + objects.CAMDRONE)
sprite('Turret', copy_costumes('Turret'), CL + FX + EN + enemies.TURRET)
sprite('HannyaBoy', copy_costumes('HannyaBoy'), CL + FX + EN + enemies.HANNYA)
sprite('BigOni', copy_costumes('BigOni'), CL + FX + EN + enemies.ONI)
sprite('ScavDrone', copy_costumes('ScavDrone'), CL + FX + EN + enemies.DRONE)
sprite('Kuro', copy_costumes('Kuro', names=['idle_']), visuals.KURO)
hotaru_src = read_logic('hotaru.py') + FX + anim_info_src('Hotaru') + atk_info_src()
sprite('Hotaru', copy_costumes('Hotaru'), hotaru_src)
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
proj_costumes = copy_costumes('Projectiles') + WAVE_COSTUMES
sprite('Projectiles', proj_costumes, CL + FX + EN + objects.PROJECTILES)
sprite('MoveFX', copy_costumes('MoveFX'), CL + visuals.fx_sprite('mq', visuals.MOVE_FX))
sprite('CombatFX', copy_costumes('CombatFX'), CL + visuals.fx_sprite('cq', visuals.COMBAT_FX))
sprite('Rain', copy_costumes('Rain'), visuals.RAIN)
sprite('Flash', FLASH_COSTUMES, visuals.FLASH)
eui = copy_costumes('HUD', names=['enemy_int_']) + copy_costumes('CombatFX', names=['breach_', 'severance_'])
sprite('EnemyUI', eui, CL + visuals.ENEMY_UI)
hud = copy_costumes('HUD') + tcount + copy_costumes('NamePlates', names=['boss_big_oni'])
sprite('HUD', hud, visuals.HUD)
hint_cos = HINT_COSTUMES + copy_costumes('KeyPrompts', names=['key_e'])
sprite('Hints', hint_cos, visuals.HINTS)
ban = copy_costumes('Banners') + copy_costumes('ChapterCards')
sprite('Banners', ban, visuals.BANNERS)
dlg = (copy_costumes('Dialogue') + copy_costumes('Portraits') + copy_costumes('NamePlates', names=['name_'])
       + DLG_COSTUMES)
sprite('Dialogue', dlg, visuals.DIALOGUE)
sprite('Menu', MENU_COSTUMES, menu.MENU)
sprite('TextFX', copy_costumes('Font'), menu.TEXTFX)
sprite('Fade', FADE_COSTUMES, visuals.FADE)
sprite('SFX', [FADE_COSTUMES[0]], visuals.SFX, sounds=audio.SFX_NAMES)
for track, length in audio.MUSIC.items():
    sprite('Music_' + track, [FADE_COSTUMES[0]], visuals.music(track, length), sounds=[track])
sprite('Music_drums', [FADE_COSTUMES[0]], visuals.music('boss_drums', audio.MUSIC['boss'], drums=True),
       sounds=['boss_drums'])
sprite('Ambience', [FADE_COSTUMES[0]], visuals.AMBIENCE, sounds=['rain_loop'])

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
