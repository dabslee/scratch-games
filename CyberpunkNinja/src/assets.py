"""
Asset helpers: read the starter project from the asset pack, autotile and
render rooms, and render text with the Shinobi Mono glyphs.

All generated costumes use Scratch's bitmapResolution 2 at 4x art scale,
exactly like the asset pack: one art pixel = 4 PNG pixels = 2 stage units.
"""
import hashlib
import io
import json
import os
import random
import zipfile

from PIL import Image

import levels

HERE = os.path.dirname(os.path.abspath(__file__))
# the asset pack ships in the repo next to src/; CN_PACK points the build at another copy
PACK = os.environ.get('CN_PACK', os.path.join(HERE, '..', 'CyberpunkNinja_AssetPack'))
# this project's own hand-drawn source art
ART = os.path.join(HERE, '..', 'art')


def pack_path(*p):
    return os.path.join(PACK, *p)


def art_path(*p):
    return os.path.join(ART, *p)


class Starter:
    """The asset pack's starter .sb3, indexed by sprite and costume name."""

    def __init__(self):
        self.zip = zipfile.ZipFile(pack_path('scratch', 'CyberpunkNinja_Starter.sb3'))
        self.project = json.loads(self.zip.read('project.json'))
        self.targets = {t['name']: t for t in self.project['targets']}

    def costumes(self, sprite):
        return self.targets[sprite]['costumes']

    def costume(self, sprite, name):
        for c in self.targets[sprite]['costumes']:
            if c['name'] == name:
                return c
        raise KeyError((sprite, name))

    def data(self, md5ext):
        return self.zip.read(md5ext)

    def image(self, sprite, name):
        c = self.costume(sprite, name)
        return Image.open(io.BytesIO(self.data(c['md5ext']))).convert('RGBA')

    def image_1x(self, sprite, name):
        im = self.image(sprite, name)
        return im.resize((im.width // 4, im.height // 4), Image.NEAREST)


STARTER = None


def starter():
    global STARTER
    if STARTER is None:
        STARTER = Starter()
    return STARTER


# ---------------------------------------------------------------- costumes
def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def make_costume(name, im_4x, cx, cy, store):
    """Register a 4x PNG costume; (cx, cy) is the rotation centre in PNG pixels."""
    data = png_bytes(im_4x)
    md5 = hashlib.md5(data).hexdigest()
    store[md5 + '.png'] = data
    return {'name': name, 'bitmapResolution': 2, 'dataFormat': 'png', 'assetId': md5,
            'md5ext': md5 + '.png', 'rotationCenterX': cx, 'rotationCenterY': cy}


def up4(im):
    return im.resize((im.width * 4, im.height * 4), Image.NEAREST)


# ---------------------------------------------------------------- tiles
MATERIAL = {0: 'sump', 1: 'alley', 2: 'vaults', 3: 'sewer', 4: 'rail', 5: 'memory', 6: 'gardens', 7: 'academy', 8: 'tenshu', 9: 'sump'}


def tile_images(material):
    layout = json.load(open(pack_path('tilesets', 'layout.json')))
    if material == 'sewer':
        from gfx import sewers
        atlas = sewers.sewer_atlas()
    elif material == 'vaults':
        from gfx import vaults
        atlas = vaults.vaults_atlas()
    elif material == 'rail':
        from gfx import monorail
        atlas = monorail.rail_atlas()
    elif material == 'memory':
        from gfx import hollow_floor
        atlas = hollow_floor.memory_atlas()
    elif material == 'academy':
        from gfx import academy
        atlas = academy.academy_atlas()
    else:
        atlas = Image.open(pack_path('tilesets', '%s_atlas_8x8.png' % material)).convert('RGBA')
    tiles = {}
    for r, row in enumerate(layout['rows']):
        for c, name in enumerate(row):
            tiles[name] = atlas.crop((c * 8, r * 8, c * 8 + 8, r * 8 + 8))
    return tiles


def autotile(room, c, r, rng):
    def s(cc, rr):
        v = room.is_solid(cc, rr)
        if v is None:  # outside the room: continue the edge cell
            cc = min(max(cc, 0), levels.W - 1)
            rr = min(max(rr, 0), levels.H - 1)
            return room.g[rr][cc] in '#B'
        return v
    up, dn, lf, rt = s(c, r - 1), s(c, r + 1), s(c - 1, r), s(c + 1, r)
    if not up and not dn:
        if lf and rt:
            return 'row_m'
        if lf:
            return 'row_r'
        if rt:
            return 'row_l'
        return 'single'
    if not lf and not rt:
        if up and dn:
            return 'col_mid'
        return 'col_top' if dn else 'col_bottom'
    if not up:
        return 'top' if (lf and rt) else ('top_left' if rt else 'top_right')
    if not dn:
        return 'bottom' if (lf and rt) else ('bottom_left' if rt else 'bottom_right')
    if lf and rt:
        if not s(c - 1, r - 1):
            return 'inner_tl'
        if not s(c + 1, r - 1):
            return 'inner_tr'
        if not s(c - 1, r + 1):
            return 'inner_bl'
        if not s(c + 1, r + 1):
            return 'inner_br'
        x = rng.random()
        if x < 0.08:
            return 'vent'
        if x < 0.22:
            return 'center_b'
        if x < 0.32:
            return 'center_c'
        return 'center'
    return 'left' if rt else 'right'


def render_room(room, frame=0):
    """Render the static tile layer of a room as a 1x RGBA image (240x184). `frame` picks
    the toxic runoff's bubbling frame (0 or 1)."""
    tiles = tile_images(MATERIAL[room.chapter])
    rng = random.Random(room.key)
    im = Image.new('RGBA', (levels.W * 8, levels.H * 8), (0, 0, 0, 0))
    for r in range(levels.H):
        for c in range(levels.W):
            ch = room.g[r][c]
            name = None
            if ch == '#':
                name = autotile(room, c, r, rng)
            elif ch == '=':
                lf = c > 0 and room.g[r][c - 1] == '='
                rt = c < levels.W - 1 and room.g[r][c + 1] == '='
                name = 'plat_m' if lf and rt else 'plat_r' if lf else 'plat_l' if rt else 'plat_single'
            elif ch == '^':
                name = 'spikes_up'
            elif ch == 'v':
                name = 'spikes_down'
            elif ch == 'w':
                from gfx import sewers
                im.alpha_composite(sewers.toxic_tile(r == 0 or room.g[r - 1][c] != 'w', frame, c), (c * 8, r * 8))
                continue
            deco = room.decor.get((c, r))
            if deco and ch in '.#':
                if ch == '#' and deco in ('ladder', 'pipe_v', 'pipe_h', 'grate'):
                    pass  # see-through decor on walls looks wrong; keep the wall tile
                else:
                    if name and deco in ('window_lit', 'window_lit2', 'window_dark', 'vent'):
                        name = deco
                    elif name:
                        im.alpha_composite(tiles[name], (c * 8, r * 8))
                        name = deco
                    else:
                        name = deco
            if name:
                im.alpha_composite(tiles[name], (c * 8, r * 8))
    return im


# ---------------------------------------------------------------- previews
OBJ_PREVIEW = {
    'drone': ('ScavDrone', 'hover_0'), 'turret': ('Turret', 'idle_0'), 'hannya': ('HannyaBoy', 'idle_0'),
    'oni': ('BigOni', 'idle_0'), 'shrine': ('ShrineTerminal', 'idle_0'), 'cart': ('RamenCart', 'idle_0'),
    'tetsu': ('Tetsu', 'idle_0'), 'daicam': ('DaiCam', 'panic_0'), 'laser': ('LaserBarrier', 'on_0'),
    'crate': ('Crate', 'intact_0'), 'puddle': ('ShockPuddle', 'spark_0'), 'lift': ('MovingPlatform', 'hover_0'),
    'shard': ('MemoryShard', 'spin_0'), 'lantern': ('Lantern', 'sway_0'), 'door': ('SecurityDoor', 'closed_0'),
    'start': ('Hotaru', 'idle_0'), 'rack': ('ServerRack', 'blink_0'), 'mukuro': ('Mukuro', 'idle_0'),
    'kuro': ('Kuro', 'idle_0'), 'shell': ('Hotaru', 'idle_0_g'), 'mknpc': ('Mukuro', 'idle_0'),
}


CH2_PREVIEW = {'croupier': ('HannyaBoy', 'vaults.CROUPIER_MAP', 'idle_0'), 'slotturret': ('Turret', 'vaults.SLOT_TURRET_MAP', 'idle_0'),
               'luck': ('Mukuro', 'vaults.LUCK_MAP', 'idle_0'), 'warden': ('Mukuro', 'gardens.WARDEN_MAP', 'idle_0')}


def preview_room(room, scale=2):
    st = starter()
    if room.chapter == 3:
        from gfx import sewers
        bg = sewers.sewer_sky()
        bg.alpha_composite(sewers.sewer_far())
        bg.alpha_composite(sewers.sewer_mid())
    elif room.chapter == 2:
        from gfx import vaults
        bg = vaults.sky()
        bg.alpha_composite(vaults.far())
        bg.alpha_composite(vaults.mid())
    elif room.chapter == 4:
        from gfx import monorail
        bg = monorail.sky()
        bg.alpha_composite(monorail.far())
        bg.alpha_composite(monorail.mid())
    elif room.chapter == 5:
        from gfx import hollow_floor
        bg = hollow_floor.hollow_sky()
        bg.alpha_composite(hollow_floor.hollow_far())
        bg.alpha_composite(hollow_floor.hollow_mid())
    elif room.chapter == 7:
        from gfx import academy
        bg = academy.academy_sky()
        bg.alpha_composite(academy.academy_far())
        bg.alpha_composite(academy.academy_mid())
    else:
        ch = {0: 'sump', 1: 'neon_alley', 6: 'server_gardens', 8: 'tenshu', 9: 'sump'}[room.chapter]
        bg = Image.open(pack_path('backgrounds', ch, 'sky.png')).convert('RGBA')
        for l in ('far', 'mid'):
            bg.alpha_composite(Image.open(pack_path('backgrounds', ch, l + '.png')).convert('RGBA'))
    im = Image.new('RGBA', (240, 184), (0, 0, 0, 255))
    im.paste(bg, (0, 0))
    im.alpha_composite(render_room(room))
    if room.chapter in (5, 7, 8):
        from gfx import hollow_floor
        for r in range(levels.H):
            for c in range(levels.W):
                if room.g[r][c] in 'GH':
                    on = 'on' if room.g[r][c] == 'G' else 'off'
                    im.alpha_composite(hollow_floor.phase_block(on, room.chapter == 7), (c * 8, r * 8))
    from gfx import academy, gardens, monorail, npcs, tenshu, vaults
    from gfx.util import recolor
    for o in room.objs:
        extra = {'pachinko': (vaults.pachinko_prop(0), 8, 30), 'slot': (vaults.slot_machine(0), 40, 38),
                 'jackpot': (vaults.jackpot_sign(True), 26, 0), 'pod': (gardens.pod(0), 7, 30),
                 'toro': (gardens.toro(0), 6, 22), 'bonsai': (gardens.bonsai(), 7, 18),
                 'seat': (monorail.seat(), 9, 12), 'post': (monorail.post(), 5, 22),
                 'desk': (npcs.desk(), 36, 30), 'directory': (npcs.directory(), 38, 0),
                 'dummy': (academy.dummy(), 7, 26),
                 'daimyo': (tenshu.exo('idle', 0), 42, 91),
                 'raijin': (monorail.raijin('idle', 0).crop((0, 0, monorail.RJ_W, monorail.RJ_CUT)),
                            monorail.RJ_CORE[0], monorail.RJ_CUT)}
        key = 'jackpot' if o['type'] == 'sign' and o['a'] == 'NeonSign_Jackpot' else o['type']
        if key == 'mist':
            for k in range(o['a']):
                _paste_clip(im, gardens.mist(k % 8), int((o['x'] + 240) / 2) - 8, int((180 - o['y']) / 2) - 8 * (k + 1))
            continue
        if key in extra:
            sp, ax, ay = extra[key]
            _paste_clip(im, sp, int((o['x'] + 240) / 2) - ax, int((180 - o['y']) / 2) - ay)
            continue
        if o['type'] in CH2_PREVIEW or (room.chapter == 4 and o['type'] in ('hannya', 'croupier')):
            if room.chapter == 4 and o['type'] in ('hannya', 'croupier'):
                spr, mp, cos = 'HannyaBoy', 'monorail.' + ('GUARD_MAP' if o['type'] == 'hannya' else 'GUNNER_MAP'), 'idle_0'
            else:
                spr, mp, cos = CH2_PREVIEW[o['type']]
            c = st.costume(spr, cos)
            mod = {'vaults': vaults, 'gardens': gardens, 'monorail': monorail}[mp.split('.')[0]]
            sp = recolor(st.image_1x(spr, cos), getattr(mod, mp.split('.')[1]))
            if o['a'] == -90:
                sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
                ax = sp.width - c['rotationCenterX'] // 4
            else:
                ax = c['rotationCenterX'] // 4
            _paste_clip(im, sp, int((o['x'] + 240) / 2) - ax, int((180 - o['y']) / 2) - c['rotationCenterY'] // 4)
            continue
        if o['type'] == 'sign':
            spr, cos = o['a'], 'on_0'
        elif o['type'] in OBJ_PREVIEW:
            spr, cos = OBJ_PREVIEW[o['type']]
        else:
            continue
        c = st.costume(spr, cos)
        sp = st.image_1x(spr, cos)
        if o['type'] == 'turret' and o['a'] == -90:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            ax = sp.width - c['rotationCenterX'] // 4
        else:
            ax = c['rotationCenterX'] // 4
        ay = c['rotationCenterY'] // 4
        px = int((o['x'] + 240) / 2) - ax
        py = int((180 - o['y']) / 2) - ay
        _paste_clip(im, sp, px, py)
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def _paste_clip(dst, src, x, y):
    tmp = Image.new('RGBA', dst.size, (0, 0, 0, 0))
    tmp.paste(src, (x, y))
    dst.alpha_composite(tmp)


# ---------------------------------------------------------------- font
class Font:
    """Shinobi Mono glyphs taken from the Font / FontBold sprites (1x)."""

    def __init__(self, bold=False):
        st = starter()
        spr = 'FontBold' if bold else 'Font'
        self.glyphs = {}
        for c in st.costumes(spr):
            ch = c['name'][3:]
            self.glyphs[ch] = st.image_1x(spr, c['name'])

    def width(self, text):
        w = 0
        for ch in text:
            g = self.glyphs.get(ch) or self.glyphs['?']
            w += g.width + 1
        return max(0, w - 1)

    def draw(self, im, x, y, text, color=(238, 242, 255), shadow=None):
        for ch in text:
            g = self.glyphs.get(ch) or self.glyphs['?']
            if shadow:
                tinted = Image.new('RGBA', g.size, shadow + (255,))
                tinted.putalpha(g.getchannel('A'))
                im.alpha_composite(tinted, (x + 1, y + 1))
            tinted = Image.new('RGBA', g.size, color + (255,))
            tinted.putalpha(g.getchannel('A'))
            im.alpha_composite(tinted, (x, y))
            x += g.width + 1
        return x

    def wrap(self, text, width):
        lines = []
        for para in text.split('\n'):
            line = ''
            for word in para.split(' '):
                cand = word if not line else line + ' ' + word
                if self.width(cand) <= width:
                    line = cand
                else:
                    if line:
                        lines.append(line)
                    line = word
            lines.append(line)
        return lines


PALETTE = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
           for k, v in json.load(open(pack_path('palette', 'palette.json'))).items()}
