"""Hand edits to pack characters, carried from one edited idle frame to every frame.

The art in art/src/edits is a single edited idle_0 per character. Every other
animation frame gets the edit in three passes:
  1. Pose frames: the original idle head is found in the frame (best pixel match;
     some frames give the spot by hand) and the edited head is pasted there. Only
     pixels that match the original are replaced, so a blade or an arm passing in
     front of the face stays in front. Leftover pieces in head-only colors (a hood
     tail flapping somewhere else) take the edit's color change, and the rest of
     the body is recolored by the edit's color changes.
  2. Glitch frames (the dash smears and death dissolves): rebuilt from the edited
     clean frame they were made from. Each row of a glitch frame is a sideways-
     shifted row of that frame, so the same shift picks the edited pixels.
  3. Hand fixes for the frames that still need them (FIXES below).
"""
import math
import os
from collections import Counter, defaultdict

from PIL import Image

import art_ch2
from assets import PALETTE as P

EDITS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'src', 'edits')
CLEAR = (0, 0, 0, 0)


def _rgba(name):
    return P[name] + (255,)


def _load(name):
    return Image.open(os.path.join(EDITS, name)).convert('RGBA')


def _4x(im):
    return im.resize((im.width * 4, im.height * 4), Image.NEAREST)


def _1x(im):
    return im.resize((im.width // 4, im.height // 4), Image.NEAREST)


def _colors(im, box=None, outside=None):
    px = im.load()
    out = set()
    for y in range(im.height):
        for x in range(im.width):
            inb = lambda b: b[0] <= x < b[2] and b[1] <= y < b[3]
            if (box and not inb(box)) or (outside and inb(outside)) or not px[x, y][3]:
                continue
            out.add(px[x, y])
    return out


def color_map(old, new, inside=None, outside=None, keep=()):
    """Majority color change between the original and the edit, counted inside or
    outside a box."""
    po, pn = old.load(), new.load()
    m = defaultdict(Counter)
    for y in range(old.height):
        for x in range(old.width):
            inb = lambda b: b[0] <= x < b[2] and b[1] <= y < b[3]
            if (inside and not inb(inside)) or (outside and inb(outside)):
                continue
            if po[x, y][3] and pn[x, y][3]:
                m[po[x, y]][pn[x, y]] += 1
    out = {}
    for k, v in m.items():
        c, n = v.most_common(1)[0]
        if c != k and k[:3] not in keep and n / sum(v.values()) >= 0.5:
            out[k] = c
    return out


class Head:
    """The original and edited head, cut out of the idle frame (optionally rotated)."""

    def __init__(self, old, new, box, rotate=None):
        o, n = old.crop(box), new.crop(box)
        if rotate is not None:
            o, n = o.transpose(rotate), n.transpose(rotate)
        self.size = o.size
        po, pn = o.load(), n.load()
        self.ref = {(x, y): po[x, y] for y in range(o.height) for x in range(o.width) if po[x, y][3]}
        self.diff = {(x, y): (po[x, y], pn[x, y]) for y in range(o.height) for x in range(o.width) if po[x, y] != pn[x, y]}
        self.home = box[:2]
        self.replaceable = set(self.ref.values())

    def find(self, fr, near=None, rng=14):
        """Best match in a frame: (fraction of the head matched, top-left corner)."""
        pf = fr.load()
        W, H = fr.size
        cx, cy = near or self.home
        best = (0, (cx, cy))
        for oy in range(cy - rng, cy + rng + 1):
            for ox in range(cx - rng, cx + rng + 1):
                hit = 0
                for (x, y), c in self.ref.items():
                    X, Y = x + ox, y + oy
                    if 0 <= X < W and 0 <= Y < H and pf[X, Y] == c:
                        hit += 1
                if hit > best[0]:
                    best = (hit, (ox, oy))
        return best[0] / max(1, len(self.ref)), best[1]

    def paste(self, out, off, touched, force=False):
        """Paste the edited pixels where the frame still shows the original. With
        force, the edited head also goes over pixels of the original head that are
        shaded differently in this frame (but never over other colors)."""
        po = out.load()
        W, H = out.size
        for (x, y), (o, nw) in self.diff.items():
            X, Y = x + off[0], y + off[1]
            if not (0 <= X < W and 0 <= Y < H) or (X, Y) in touched:
                continue
            f = po[X, Y]
            if f == o or (not o[3] and not f[3]) or (force and o[3] and f in self.replaceable):
                po[X, Y] = nw
                touched.add((X, Y))


class Edit:
    def __init__(self, old, new, head, thr=0.6, keep=(), body=None, head_colors=None):
        self.old, self.new = old, new
        self.box = head
        self.thr = thr
        self.head = Head(old, new, head)
        self.body = color_map(old, new, outside=head, keep=keep)
        self.headmap = color_map(old, new, inside=head, keep=keep)
        self.body.update(body or {})
        self.always = dict(head_colors or {})
        self.headmap.update(self.always)
        # colors only the head uses (a hood, a mask): these change wherever they turn up
        self.head_only = _colors(old, head) - _colors(old, outside=head)
        self.head.replaceable = set(self.head_only)

    def apply(self, fr, place=None, hook=None):
        """place: (x, y) to paste the head at, chosen by hand, or None to search."""
        out = fr.copy()
        po = out.load()
        touched = set()
        if place is not None:
            self.head.paste(out, place, touched, force=True)
        else:
            sc, off = self.head.find(fr)
            if sc >= self.thr:
                # where the pose matches only in part, the edited head also goes over
                # leftover pixels in the head's own colors (never over anything else)
                self.head.paste(out, off, touched, force=sc < 0.97)
        if hook:
            hook(out, touched)
        for y in range(fr.height):
            for x in range(fr.width):
                c = po[x, y]
                if (x, y) in touched or not c[3]:
                    continue
                if c in self.body:
                    po[x, y] = self.body[c]
                elif c in self.always or (c in self.head_only and c in self.headmap):
                    po[x, y] = self.headmap[c]
        return out


# ---------------------------------------------------------------- glitch frames
def _row_shift(G, S, y, rng=12):
    pg, ps = G.load(), S.load()
    W = G.width
    best = (0, 0)
    for dx in range(-rng, rng + 1):
        hit = 0
        for x in range(W):
            g = pg[x, y]
            sx = x - dx
            if g[3] and 0 <= sx < W:
                s = ps[sx, y]
                if s[3] and s[:3] == g[:3]:
                    hit += 1
        if hit > best[0]:
            best = (hit, dx)
    return best


def rebuild_glitch(G, olds, news):
    """A glitch frame rebuilt from the edited clean frame it was made from."""
    best = None
    for n, S in olds.items():
        rows = [_row_shift(G, S, y) for y in range(G.height)]
        sc = sum(h for h, _ in rows)
        if best is None or sc > best[0]:
            best = (sc, n, rows)
    _, n, rows = best
    So, Sn, pg = olds[n].load(), news[n].load(), G.load()
    out = G.copy()
    po = out.load()
    for y, (hits, dx) in enumerate(rows):
        alphas = [pg[x, y][3] for x in range(G.width) if pg[x, y][3] and 0 <= x - dx < G.width
                  and So[x - dx, y][3] and So[x - dx, y][:3] == pg[x, y][:3]]
        a_row = max(set(alphas), key=alphas.count) if alphas else 255
        for x in range(G.width):
            sx = x - dx
            if not 0 <= sx < G.width:
                continue
            g, o, nw = pg[x, y], So[sx, y], Sn[sx, y]
            if g[3] and o[3] and g[:3] == o[:3]:
                po[x, y] = (nw[:3] + (g[3],)) if nw[3] else CLEAR
            elif not g[3] and not o[3] and nw[3] and hits >= 3:
                po[x, y] = nw[:3] + (a_row,)
    return out


def _fix(im, fixes):
    """Hand fixes: {(x, y): color or None}."""
    px = im.load()
    for (x, y), c in fixes.items():
        px[x, y] = CLEAR if c is None else (c + (255,) if len(c) == 3 else c)
    return im


def carry(frames, edit, glitch=(), places=None, hooks=None, fixes=None, idle='idle_0'):
    """{name: 1x frame} with the edit carried to every frame."""
    out = {}
    for n, fr in frames.items():
        if n == idle:
            out[n] = edit.new.copy()
        elif n.split('_')[0] + '_' + n.split('_')[1] not in glitch:
            out[n] = edit.apply(fr, (places or {}).get(n.rsplit('_', 1)[0] if n.endswith(('_m', '_g')) else n),
                                hooks(n) if hooks else None)
    for n, fr in frames.items():
        if n in out:
            continue
        suffix = n[len(n.split('_')[0] + '_' + n.split('_')[1]):]
        clean = {k: frames[k] for k in out if k[len(k.split('_')[0] + '_' + k.split('_')[1]):] == suffix}
        out[n] = rebuild_glitch(fr, clean, {k: out[k] for k in clean})
    for n, f in (fixes or {}).items():
        if n in out:
            _fix(out[n], f)
    return out


def costumes(st, sprite, frames, prefix=''):
    return [(prefix + c['name'], _4x(frames[c['name']]), c['rotationCenterX'], c['rotationCenterY'])
            for c in st.costumes(sprite)]


GLITCH = ('dash_1', 'dash_2', 'death_3', 'death_4', 'death_5')


# ---------------------------------------------------------------- Hotaru
HOTARU_FIXES = {}


def hotaru_frames(st):
    frames = {c['name']: st.image_1x('Hotaru', c['name']) for c in st.costumes('Hotaru')}
    ed = Edit(frames['idle_0'], _load('hotaru_idle_0.png'), head=(16, 13, 30, 24))
    return carry(frames, ed, glitch=GLITCH, places=HOTARU_PLACES, fixes=HOTARU_FIXES)


HOTARU_PLACES = {}


def hotaru_costumes(st):
    return costumes(st, 'Hotaru', hotaru_frames(st))


# ---------------------------------------------------------------- Lady Luck
LUCK_DARK = (39, 19, 81, 255)
LUCK_GOLD = (224, 176, 64, 255)
LUCK_PLACES = {}
LUCK_FIXES = {}


def _sash(muk):
    """Lady Luck's gold sash (red in Mukuro's colors). Red2 is only ever sash; red3 is
    shared with the blade, so each red3 pixel goes with whichever is nearer, red2
    (sash) or yellow (the blade's tip). The waist belt, a run of four or more red2 below the
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
        for r in nxt:  # a tie goes to the blade
            if label[r] == 's' and any(label.get((r[0] + dx, r[1] + dy)) == 'b' and (r[0] + dx, r[1] + dy) in nxt
                                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                label[r] = 'b'
        frontier = nxt
    # red3 pieces cut off from both (a sash tip flying free) are sash: the blade
    # always ends in yellow
    for y in range(H):
        for x in range(W):
            if col((x, y)) == R3 and (x, y) not in label:
                label[(x, y)] = 's'
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
            belt = x1 - x0 >= 3
        out[(x, y)] = LUCK_GOLD if belt else LUCK_DARK
    return out


def luck_frames(st):
    frames = {n: _1x(im) for n, im, _, _ in art_ch2.recolor_costumes('Mukuro', art_ch2.LUCK_MAP)}
    head, waist = (13, 11, 33, 24), (15, 24, 31, 34)
    new = _load('luck_idle_0.png')
    ed = Edit(frames['idle_0'], new, head=head, head_colors={_rgba('mag3'): LUCK_DARK, _rgba('mag2'): LUCK_DARK})
    waist_head = Head(frames['idle_0'], new, waist)

    def hooks(name):
        muk = st.image_1x('Mukuro', name)

        def run(out, touched):
            sc, off = waist_head.find(out)
            if sc >= 0.85:
                waist_head.paste(out, off, touched)
            po = out.load()
            for q, c in _sash(muk).items():
                if q not in touched and po[q][3]:
                    po[q] = c
                    touched.add(q)
        return run
    return carry(frames, ed, glitch=GLITCH, places=LUCK_PLACES, hooks=hooks, fixes=LUCK_FIXES)


def luck_costumes(st):
    return costumes(st, 'Mukuro', luck_frames(st))


# ---------------------------------------------------------------- Mukuro
MUKURO_PLACES = {}
MUKURO_FIXES = {}
_MUK = {}


def mukuro_frames(st):
    if not _MUK:
        frames = {c['name']: st.image_1x('Mukuro', c['name']) for c in st.costumes('Mukuro')}
        ed = Edit(frames['idle_0'], _load('mukuro_idle_0.png'), head=(15, 11, 31, 25))
        _MUK.update(carry(frames, ed, glitch=GLITCH, places=MUKURO_PLACES, fixes=MUKURO_FIXES))
    return _MUK


def mukuro_image(st, name):
    """Mukuro's pack frame (4x) with the edit (his eyes showing under the hood)."""
    return _4x(mukuro_frames(st)[name])


def mukuro_costumes(st, prefix='', names=None):
    fr = mukuro_frames(st)
    return [(prefix + c['name'], _4x(fr[c['name']]), c['rotationCenterX'], c['rotationCenterY'])
            for c in st.costumes('Mukuro') if names is None or any(c['name'].startswith(k) for k in names)]


# ---------------------------------------------------------------- the suited grunt
STEEL = (P['steel'], P['slate3'])
SUIT = (24, 24, 24, 255)
BLADE, BLADE_DK, GUARD, OUTLINE, BLACK = (154, 163, 194, 255), (98, 108, 145, 255), (129, 101, 31, 255), _rgba('ink'), (0, 0, 0, 255)
# the overhead swing: his raised arms cover his face, so the head goes in by hand
GRUNT_PLACES = {'attack_0': (16, 9), 'attack_1': (16, 11), 'attack_2': (16, 11)}
# lying dead, his head turned on its side: {name: (rotation, top-left)}
GRUNT_ROTATED = {'death_2': (Image.ROTATE_90, (8, 22)), 'death_3': (Image.ROTATE_90, (8, 22))}
# the glint on the raised blade (the pipe's old orange spark) as a white star
_GLINT = {(21, 7): (154, 163, 194), (21, 8): (238, 242, 255), (21, 9): (238, 242, 255), (21, 10): (238, 242, 255),
          (21, 11): (154, 163, 194), (20, 9): (238, 242, 255), (22, 9): (238, 242, 255), (19, 9): None, (23, 9): None}
GRUNT_FIXES = {'attack_1': _GLINT, 'attack_2': _GLINT}


def _katana(orig, out):
    """Swap the Hannya Boy's lead pipe for the edit's katana: a one-pixel steel blade
    along the pipe's line, a brown guard at his hands and a short dark grip below."""
    po, pg = out.load(), orig.load()
    W, H = orig.size
    steel = {P['steel'], P['slate3']}
    pipe = [(x, y) for y in range(H) for x in range(W) if pg[x, y][3] and pg[x, y][:3] in steel]
    if len(pipe) < 4:
        return
    pset = set(pipe)
    # its outline: ink touching the pipe and nothing else
    edge = set()
    for (x, y) in pipe:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q in pset or not (0 <= q[0] < W and 0 <= q[1] < H) or pg[q][:3] != P['ink'] or not pg[q][3]:
                    continue
                if all(not pg[r][3] or pg[r][:3] == P['ink'] or r in pset
                       for r in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1))
                       if 0 <= r[0] < W and 0 <= r[1] < H):
                    edge.add(q)
    hand = [(x, y) for y in range(H) for x in range(W) if pg[x, y][3] and pg[x, y][:3] == P['skin2']
            and min(abs(x - a) + abs(y - b) for a, b in pipe) <= 3]
    # the pipe's axis
    mx = sum(x for x, _ in pipe) / len(pipe)
    my = sum(y for _, y in pipe) / len(pipe)
    sxx = sum((x - mx) ** 2 for x, _ in pipe)
    syy = sum((y - my) ** 2 for _, y in pipe)
    sxy = sum((x - mx) * (y - my) for x, y in pipe)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ux, uy = math.cos(ang), math.sin(ang)
    proj = [(x - mx) * ux + (y - my) * uy for x, y in pipe]
    t0, t1 = min(proj), max(proj)
    if hand:
        hx = sum(x for x, _ in hand) / len(hand)
        hy = sum(y for _, y in hand) / len(hand)
        th = (hx - mx) * ux + (hy - my) * uy
    else:
        th = t0
    if abs(th - t1) < abs(th - t0):  # point the axis from the hands to the tip
        ux, uy, t0, t1, th = -ux, -uy, -t1, -t0, -th
    for q in pset | edge:
        po[q] = CLEAR
    # holes the pipe leaves in his body fill with suit
    for q in pset | edge:
        x, y = q
        n = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        solid = [r for r in n if 0 <= r[0] < W and 0 <= r[1] < H and po[r][3]]
        if len(solid) >= 3:
            po[q] = SUIT
    pt = lambda t: (int(round(mx + ux * t)), int(round(my + uy * t)))

    def line(p, q):
        # a one-pixel line (Bresenham), like a hand-drawn blade
        (x0, y0), (x1, y1) = p, q
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
        err, out = dx + dy, []
        while True:
            out.append((x0, y0))
            if (x0, y0) == (x1, y1):
                return out
            e2 = 2 * err
            step_x, step_y = e2 >= dy, e2 <= dx
            if step_x:
                err += dy
                x0 += sx
            if step_x and step_y:
                out.append((x0, y0))  # no corner-only joins: the blade stays one solid strip
            if step_y:
                err += dx
                y0 += sy

    def put(q, c, only_clear=False):
        if 0 <= q[0] < W and 0 <= q[1] < H and (not only_clear or not po[q][3]):
            po[q] = c

    guard = pt(max(t0, th) + 1)
    tip = pt(t1 + 2)
    blade = line(guard, tip)[1:]
    steep = abs(tip[1] - guard[1]) >= abs(tip[0] - guard[0])
    # the blade: darker steel for its first stretch out of the guard, as in the edit
    for i, q in enumerate(blade):
        put(q, BLADE_DK if i < 3 else BLADE)
    # outlined one pixel to each side, ink on one side and black on the other
    for q in blade:
        a, b = ((q[0] - 1, q[1]), (q[0] + 1, q[1])) if steep else ((q[0], q[1] - 1), (q[0], q[1] + 1))
        put(a, OUTLINE, True)
        put(b, BLACK, True)
    put((tip[0] + int(round(ux)), tip[1] + int(round(uy))), OUTLINE, True)
    # a three-pixel guard across the blade, a short black grip and a brown pommel
    for s_ in (-1, 0, 1):
        put((guard[0] + s_, guard[1]) if steep else (guard[0], guard[1] + s_), GUARD)
    grip = line(guard, pt(max(t0, th) + 1 - 4))[1:]
    for i, q in enumerate(grip):
        put(q, GUARD if i == len(grip) - 1 else BLACK)


def _belt(im):
    """The Hannya Boy's gold belt: the stretch of a row from its first gold pixel to its
    last, where the row holds three or more (in some poses the pants show through)."""
    px = im.load()
    W, H = im.size
    out = set()
    for y in range(H):
        xs = [x for x in range(W) if px[x, y][3] and px[x, y][:3] == P['gold']]
        if len(xs) >= 3 and xs[-1] - xs[0] <= 8:
            out.update((x, y) for x in range(xs[0], xs[-1] + 1))
    return out


def _drop_strays(im):
    """Lone pixels with nothing around them (the old mask's horn tips)."""
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            if px[x, y][3] and not any(px[x + dx, y + dy][3] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                       if (dx or dy) and 0 <= x + dx < W and 0 <= y + dy < H):
                px[x, y] = CLEAR


_SUITS = {}


def suit_frames(st, edit='grunt_suit_idle_0.png'):
    """{name: 1x image} of the Hannya Boy redrawn as a man in a suit: the black-suited
    grunt, or (with croupier_idle_0.png) the casino croupier in plum."""
    if edit not in _SUITS:
        _SUITS[edit] = _suit_frames(st, edit)
    return {k: v.copy() for k, v in _SUITS[edit].items()}


def _suit_frames(st, edit):
    frames = {c['name']: st.image_1x('HannyaBoy', c['name']) for c in st.costumes('HannyaBoy')}
    new = _load(edit)
    box = (18, 9, 34, 22)
    ed = Edit(frames['idle_0'], new, head=box, keep=STEEL,
              body={_rgba('mag3'): (79, 79, 79, 255)},
              head_colors={_rgba('red3'): (249, 212, 156, 255), _rgba('red2'): (249, 212, 156, 255),
                           _rgba('red1'): (237, 163, 118, 255), _rgba('white'): SUIT,
                           _rgba('yellow'): (11, 8, 20, 255)})
    rot = {k: Head(frames['idle_0'], new, box, rotate=r) for k, (r, _) in GRUNT_ROTATED.items()}
    for h in rot.values():
        h.replaceable = set(ed.head_only)
    # the shadow under the jacket: the edit's colors in the two rows below the old belt
    pants = {P['slate1'], P['slate2'], P['night1'], P['skin1']}
    po0, pn0 = frames['idle_0'].load(), new.load()
    shade = {}
    for k in (1, 2):
        cs = Counter(pn0[x, y + k] for x, y in _belt(frames['idle_0'])
                     if po0[x, y + k][3] and po0[x, y + k][:3] in pants and pn0[x, y + k][3])
        shade[k] = cs.most_common(1)[0][0] if cs else None

    def hooks(name):
        def run(out, touched):
            if name in rot:
                rot[name].paste(out, GRUNT_ROTATED[name][1], touched, force=True)
            _katana(frames[name], out)
            po = out.load()
            orig = frames[name].load()
            belt = _belt(frames[name])
            for x, y in belt:
                for k in (1, 2):
                    q = (x, y + k)
                    if (shade[k] and q not in touched and q not in belt and y + k < out.height
                            and orig[q][3] and orig[q][:3] in pants and po[q][3]):
                        po[q] = shade[k]
                        touched.add(q)
            # the katana is drawn now; keep it out of the recolor
            for y in range(out.height):
                for x in range(out.width):
                    if po[x, y] in (BLADE, BLADE_DK, GUARD, BLACK):
                        touched.add((x, y))
        return run
    out = carry(frames, ed, glitch=('death_4',), places=GRUNT_PLACES, hooks=hooks, fixes=GRUNT_FIXES)
    for n, im in out.items():
        if n != 'idle_0':
            _drop_strays(im)
    return out


def suit_costumes(st, prefix):
    return costumes(st, 'HannyaBoy', suit_frames(st), prefix)


def croupier_costumes(st, prefix=''):
    """The casino croupier: the suited man in plum with purple shades."""
    return costumes(st, 'HannyaBoy', suit_frames(st, 'croupier_idle_0.png'), prefix)


# the Chapter 5 gunner: the croupier's suit (and shades) in blue instead of plum
PLUM = ((66, 25, 60), (128, 44, 116), (147, 70, 135))


def _to_blue(c, hue=222):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c])
    return tuple(int(round(v * 255)) for v in colorsys.hls_to_rgb(hue / 360, l, s))


def gunner_costumes(st, prefix='g_'):
    blue = {c: _to_blue(c) for c in PLUM}
    frames = suit_frames(st, 'croupier_idle_0.png')
    for im in frames.values():
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                p = px[x, y]
                if p[3] and p[:3] in blue:
                    px[x, y] = blue[p[:3]] + (p[3],)
    return costumes(st, 'HannyaBoy', frames, prefix)
