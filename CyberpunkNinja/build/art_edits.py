"""Hand edits to pack characters, carried from one edited idle frame to every frame.

The art in art/src/edits is a single edited idle_0 per character. Each animation
frame gets the edit by:
  1. finding where the original idle head sits in that frame (best pixel match) and
     pasting the edited pixels there;
  2. optionally doing the same for a second patch (Lady Luck's waist);
  3. recoloring the rest of the body with the color changes the edit made below
     the head.
Frames where the head can't be found (smears, dissolves, odd poses) fall back to
recoloring the head by color too.
"""
import os
from collections import Counter, defaultdict

from PIL import Image

import art_ch2
from assets import PALETTE as P

EDITS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'src', 'edits')


def _rgba(name):
    return P[name] + (255,)


def patch(old, new, box):
    """(reference pixels of the original, pixels the edit changed), relative to box."""
    x0, y0, x1, y1 = box
    po, pn = old.load(), new.load()
    ref = {(x - x0, y - y0): po[x, y] for y in range(y0, y1) for x in range(x0, x1) if po[x, y][3]}
    diff = {(x - x0, y - y0): (po[x, y], pn[x, y]) for y in range(y0, y1) for x in range(x0, x1) if po[x, y] != pn[x, y]}
    return ref, diff


def find(fr, ref, box, rng=14):
    """Best match of a reference patch in a frame: (fraction matched, top-left)."""
    pf = fr.load()
    W, H = fr.size
    best = (0, (box[0], box[1]))
    for dy in range(-rng, rng + 1):
        for dx in range(-rng, rng + 1):
            ox, oy = box[0] + dx, box[1] + dy
            hit = 0
            for (x, y), c in ref.items():
                X, Y = x + ox, y + oy
                if 0 <= X < W and 0 <= Y < H and pf[X, Y] == c:
                    hit += 1
            if hit > best[0]:
                best = (hit, (ox, oy))
    return best[0] / max(1, len(ref)), best[1]


def color_map(old, new, inside=None, outside=None, keep=()):
    """Majority color change between the original and the edit, counted inside or
    outside a box."""
    po, pn = old.load(), new.load()
    m = defaultdict(Counter)
    for y in range(old.height):
        for x in range(old.width):
            inb = lambda b: b[0] <= x < b[2] and b[1] <= y < b[3]
            if inside and not inb(inside):
                continue
            if outside and inb(outside):
                continue
            if po[x, y][3] and pn[x, y][3]:
                m[po[x, y]][pn[x, y]] += 1
    out = {}
    for k, v in m.items():
        c, n = v.most_common(1)[0]
        if c != k and k[:3] not in keep and n / sum(v.values()) >= 0.5:
            out[k] = c
    return out


class Edit:
    def __init__(self, old, new, head, thr=0.6, keep=(), body=None, head_colors=None, patches=()):
        self.new = new
        self.head = head
        self.thr = thr
        self.patches = [(patch(old, new, head), head, thr)] + [(patch(old, new, b), b, t) for b, t in patches]
        self.body = color_map(old, new, outside=head, keep=keep)
        self.headmap = color_map(old, new, inside=head, keep=keep)
        self.body.update(body or {})
        self.headmap.update(head_colors or {})
        self._all = {**self.headmap, **self.body}
        self._keys = list(self._all)

    def apply(self, fr, hooks=None):
        out = fr.copy()
        po = out.load()
        touched = set()
        hits = []
        for (ref, diff), box, thr in self.patches:
            sc, off = find(fr, ref, box)
            hits.append((sc >= thr, off))
            if sc < thr:
                continue
            for (x, y), (o, nw) in diff.items():
                X, Y = x + off[0], y + off[1]
                if (X, Y) in touched or not (0 <= X < fr.width and 0 <= Y < fr.height):
                    continue
                if po[X, Y] == o or (not o[3] and not po[X, Y][3]):
                    po[X, Y] = nw
                    touched.add((X, Y))
        if hooks:
            hooks(out, touched, hits)
        head_ok = hits[0][0]
        for y in range(fr.height):
            for x in range(fr.width):
                if (x, y) in touched or not po[x, y][3]:
                    continue
                if po[x, y] in self.body:
                    po[x, y] = self.body[po[x, y]]
                elif not head_ok and po[x, y] in self.headmap:
                    po[x, y] = self.headmap[po[x, y]]
                elif not head_ok:
                    # glitch smears and dissolves: off-palette, part-transparent pixels
                    # take the change of the nearest color, keeping their alpha
                    c = po[x, y]
                    k = min(self._keys, key=lambda k: sum((a - b) ** 2 for a, b in zip(k[:3], c[:3])))
                    if sum((a - b) ** 2 for a, b in zip(k[:3], c[:3])) < 48 ** 2:
                        po[x, y] = self._all[k][:3] + (c[3],)
        return out


def _load(name):
    im = Image.open(os.path.join(EDITS, name)).convert('RGBA')
    return im


def _4x(im):
    return im.resize((im.width * 4, im.height * 4), Image.NEAREST)


def _1x(im):
    return im.resize((im.width // 4, im.height // 4), Image.NEAREST)


def edited_costumes(st, sprite, frames, edit, idle_name='idle_0', hooks=None, prefix=''):
    """[(name, 4x image, rcx, rcy)] for every frame, with the edit carried over."""
    out = []
    for c in st.costumes(sprite):
        n = c['name']
        im = edit.new if n == idle_name else edit.apply(frames[n], hooks(n) if hooks else None)
        out.append((prefix + n, _4x(im), c['rotationCenterX'], c['rotationCenterY']))
    return out


# ---------------------------------------------------------------- Hotaru
def hotaru_costumes(st):
    frames = {c['name']: st.image_1x('Hotaru', c['name']) for c in st.costumes('Hotaru')}
    ed = Edit(frames['idle_0'], _load('hotaru_idle_0.png'), head=(16, 13, 30, 24))
    out = []
    for c in st.costumes('Hotaru'):
        n = c['name']
        # the dash-charge variants (_m, _g) share her head, so the same edit applies
        im = ed.new if n == 'idle_0' else ed.apply(frames[n])
        out.append((n, _4x(im), c['rotationCenterX'], c['rotationCenterY']))
    return out


# ---------------------------------------------------------------- Lady Luck
LUCK_DARK = (39, 19, 81, 255)
LUCK_GOLD = (224, 176, 64, 255)


def _sash(muk):
    """Lady Luck's gold sash (red in Mukuro's colors). Red2 is only ever sash; red3 is
    shared with the blade, so each red3 pixel goes with whichever is nearer, red2
    (sash) or yellow (the blade's tip). The waist belt, a run of red2 well below the
    top of her head, stays gold; the rest of the sash goes dark purple, as in the edit."""
    R2, R3, Y = P['red2'], P['red3'], P['yellow']
    px = muk.load()
    W, H = muk.size
    col = lambda q: px[q][:3] if px[q][3] else None
    label, frontier = {}, []
    for y in range(H):
        for x in range(W):
            if col((x, y)) == R2:
                label[(x, y)] = 's'
                frontier.append((x, y))
            elif col((x, y)) == Y:
                label[(x, y)] = 'b'
                frontier.append((x, y))
    while frontier:
        nxt = []
        for q in frontier:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    r = (q[0] + dx, q[1] + dy)
                    if 0 <= r[0] < W and 0 <= r[1] < H and r not in label and col(r) == R3:
                        label[r] = label[q]
                        nxt.append(r)
        # a tie goes to the blade
        for r in nxt:
            if label[r] == 's' and any(label.get((r[0] + dx, r[1] + dy)) == 'b' and (r[0] + dx, r[1] + dy) in nxt
                                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                label[r] = 'b'
        frontier = nxt
    top = muk.getbbox()[1]
    out = {}
    for (x, y), lab in label.items():
        if lab != 's':
            continue
        belt = False
        if col((x, y)) == R2 and y >= top + 12:
            x0 = x
            while x0 - 1 >= 0 and col((x0 - 1, y)) == R2:
                x0 -= 1
            x1 = x
            while x1 + 1 < W and col((x1 + 1, y)) == R2:
                x1 += 1
            belt = x1 - x0 >= 2
        out[(x, y)] = LUCK_GOLD if belt else LUCK_DARK
    return out


def luck_costumes(st):
    frames = {n: _1x(im) for n, im, _, _ in art_ch2.recolor_costumes('Mukuro', art_ch2.LUCK_MAP)}
    head, waist = (13, 11, 33, 24), (15, 24, 31, 34)
    ed = Edit(frames['idle_0'], _load('luck_idle_0.png'), head=head, patches=[(waist, 0.85)],
              head_colors={_rgba('mag3'): LUCK_DARK, _rgba('mag2'): LUCK_DARK})

    def hooks(name):
        muk = st.image_1x('Mukuro', name)

        def run(out, touched, hits):
            (head_ok, (hx, hy)), (waist_ok, _) = hits
            if waist_ok:
                return
            po = out.load()
            hb = (hx, hy, hx + head[2] - head[0], hy + head[3] - head[1])
            for q, c in _sash(muk).items():
                if head_ok and hb[0] <= q[0] < hb[2] and hb[1] <= q[1] < hb[3]:
                    continue  # her visor, handled by the head edit
                if q not in touched and po[q][3]:
                    po[q] = c
                    touched.add(q)
        return run
    return edited_costumes(st, 'Mukuro', frames, ed, hooks=hooks)


# ---------------------------------------------------------------- the suited grunt
STEEL = (P['steel'], P['slate3'])


def suit_frames(st):
    """{name: 1x image} of the Hannya Boy redrawn as a man in a black suit."""
    frames = {c['name']: st.image_1x('HannyaBoy', c['name']) for c in st.costumes('HannyaBoy')}
    ed = Edit(frames['idle_0'], _load('grunt_suit_idle_0.png'), head=(18, 9, 34, 22), keep=STEEL,
              body={_rgba('mag3'): (79, 79, 79, 255)},
              head_colors={_rgba('red3'): (249, 212, 156, 255), _rgba('red2'): (249, 212, 156, 255),
                           _rgba('red1'): (237, 163, 118, 255), _rgba('white'): (24, 24, 24, 255),
                           _rgba('yellow'): (11, 8, 20, 255)})
    return {n: (ed.new if n == 'idle_0' else ed.apply(im)) for n, im in frames.items()}


def suit_costumes(st, prefix):
    fr = suit_frames(st)
    return [(prefix + c['name'], _4x(fr[c['name']]), c['rotationCenterX'], c['rotationCenterY']) for c in st.costumes('HannyaBoy')]


# ---------------------------------------------------------------- Mukuro
_MUK = {}


def mukuro_image(st, name):
    """Mukuro's pack frame (4x) with the edit (his eyes showing under the hood)."""
    if not _MUK:
        frames = {c['name']: st.image_1x('Mukuro', c['name']) for c in st.costumes('Mukuro')}
        ed = Edit(frames['idle_0'], _load('mukuro_idle_0.png'), head=(15, 11, 31, 25))
        for n, im in frames.items():
            _MUK[n] = _4x(ed.new if n == 'idle_0' else ed.apply(im))
    return _MUK[name].copy()


def mukuro_costumes(st, prefix='', names=None):
    out = []
    for c in st.costumes('Mukuro'):
        n = c['name']
        if names is not None and not any(n.startswith(k) for k in names):
            continue
        out.append((prefix + n, mukuro_image(st, n), c['rotationCenterX'], c['rotationCenterY']))
    return out
