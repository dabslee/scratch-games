"""
Asset helpers: load costume folders from assets/, autotile and render rooms, and
set text in the Shinobi Mono glyphs.

Every costume uses Scratch's bitmapResolution 2: one art pixel = 4 PNG pixels =
2 stage units. The PNGs in assets/ are drawn at 1x and scaled up here.
"""
import hashlib
import io
import json
import os
import random

from PIL import Image

import levels

HERE = os.path.dirname(os.path.abspath(__file__))
# all of the game's art, next to src/ (assets/README.md maps it)
ASSETS = os.path.join(HERE, '..', 'assets')


def asset_path(*p):
    return os.path.join(ASSETS, *p)


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


class CostumeSet:
    """A costume folder: its PNGs and costumes.json, which lists the costumes in order.
    Each entry has a name, a file, an anchor (the rotation centre, in the file's pixels)
    and an optional scale (PNG pixels per file pixel; 4 when left out). An entry
    {"generated": kind} marks where the build puts costumes it makes from data."""

    def __init__(self, folder):
        self.folder = folder
        self.entries = json.load(open(asset_path(folder, 'costumes.json')))['costumes']
        self.by_name = {e['name']: e for e in self.entries if 'name' in e}

    def names(self):
        return [e['name'] for e in self.entries if 'name' in e]

    def image(self, name):
        """A costume's PNG as drawn (1x for scale 4)."""
        im = Image.open(asset_path(self.folder, self.by_name[name]['file']))
        im.load()
        return im

    def costumes(self, store, generated=None):
        out = []
        for e in self.entries:
            if 'generated' in e:
                out += generated[e['generated']]
                continue
            s = e.get('scale', 4)
            im = self.image(e['name'])
            if s > 1:
                im = im.resize((im.width * s, im.height * s), Image.NEAREST)
            out.append(make_costume(e['name'], im, round(e['anchor'][0] * s), round(e['anchor'][1] * s), store))
        return out


# ---------------------------------------------------------------- tiles
MATERIAL = {0: 'sump', 1: 'alley', 2: 'vaults', 3: 'sewer', 4: 'rail', 5: 'memory', 6: 'gardens', 7: 'academy', 8: 'tenshu', 9: 'sump'}


def tile_images(material):
    layout = json.load(open(asset_path('tilesets', 'layout.json')))
    atlas = Image.open(asset_path('tilesets', '%s_atlas_8x8.png' % material)).convert('RGBA')
    tiles = {}
    for r, row in enumerate(layout['rows']):
        for c, name in enumerate(row):
            tiles[name] = atlas.crop((c * 8, r * 8, c * 8 + 8, r * 8 + 8))
    return tiles


def toxic_tile(surface, frame, col):
    """8x8 cell of the Sewers' toxic runoff (toxic_8x8.png): a row per bubbling frame;
    the first column is below the surface, the next six the surface (every sixth
    column alike)."""
    atlas = Image.open(asset_path('tilesets', 'toxic_8x8.png')).convert('RGBA')
    x = 8 + 8 * (col % 6) if surface else 0
    return atlas.crop((x, 8 * frame, x + 8, 8 * frame + 8))


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
                im.alpha_composite(toxic_tile(r == 0 or room.g[r - 1][c] != 'w', frame, c), (c * 8, r * 8))
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


# ---------------------------------------------------------------- font
class Font:
    """Shinobi Mono glyphs (1x) from assets/fonts/regular or assets/fonts/bold; each
    costume is named ch_<character>."""

    def __init__(self, bold=False):
        glyphs = CostumeSet('fonts/bold' if bold else 'fonts/regular')
        self.order = [n[3:] for n in glyphs.names()]
        self.glyphs = {n[3:]: glyphs.image(n) for n in glyphs.names()}

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
           for k, v in json.load(open(asset_path('palette', 'palette.json'))).items()}
