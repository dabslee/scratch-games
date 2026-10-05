"""
Room layouts for the vertical slice (Prologue + Chapter 1).

Every room is one 480x360 screen: 30 columns x 23 rows of 16-unit tiles
(8x8 art pixels). Row 22 is only half visible. Cell (c, r) has its centre
at stage (-232 + 16c, 172 - 16r).

Collision characters stored in the room grid string:
  .  empty            #  solid           =  one-way platform
  ^  spikes (floor)   v  spikes (ceiling)
  B  breakable block (solid until broken)
Doors and laser barriers write their own cells at runtime.
"""

W, H = 30, 23


def cx(c):
    return -232 + 16 * c


def left(c):
    return -240 + 16 * c


def top(r):
    return 180 - 16 * r


def bottom(r):
    return 164 - 16 * r


DECOR = {
    'l': 'ladder', 'i': 'pipe_v', '-': 'pipe_h', 'g': 'grate', 'z': 'hazard',
    'o': 'window_lit', 'u': 'window_lit2', 'x': 'window_dark', 'c': 'trim_cyan',
    'm': 'trim_mag', 'y': 'trim_gold', 'r': 'trim_red', 'v': 'vent',
}


class Room:
    def __init__(self, key, chapter, title):
        self.key = key
        self.chapter = chapter          # 0 = Prologue (Sump), 1 = Neon Alley
        self.title = title
        self.g = [['.'] * W for _ in range(H)]
        self.decor = {}                 # (c, r) -> tile name (drawn only)
        self.objs = []
        self.exits = {}
        self.flags = []

    # --- terrain -------------------------------------------------------
    def solid(self, c1, r1, c2, r2, ch='#'):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.g[r][c] = ch
        return self

    def clear(self, c1, r1, c2, r2):
        return self.solid(c1, r1, c2, r2, '.')

    def plat(self, c1, c2, r):
        for c in range(c1, c2 + 1):
            self.g[r][c] = '='
        return self

    def spikes(self, c1, c2, r):
        for c in range(c1, c2 + 1):
            self.g[r][c] = '^'
        return self

    def breakable(self, c1, r1, c2, r2):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.g[r][c] = 'B'
                self.obj('block', cx(c), top(r) - 8, a=c, b=r)
        return self

    def deco(self, ch, c1, r1, c2=None, r2=None):
        c2 = c1 if c2 is None else c2
        r2 = r1 if r2 is None else r2
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.decor[(c, r)] = DECOR[ch]
        return self

    # --- objects -------------------------------------------------------
    def obj(self, kind, x, y, a='', b='', c=''):
        self.objs.append({'type': kind, 'x': x, 'y': y, 'a': a, 'b': b, 'c': c})
        return self

    def grid_string(self):
        return ''.join(''.join(row) for row in self.g)

    def is_solid(self, c, r):
        if c < 0 or c >= W or r < 0 or r >= H:
            return None
        return self.g[r][c] in '#B'


ROOMS = []


def room(key, chapter, title):
    r = Room(key, chapter, title)
    ROOMS.append(r)
    return r


def link(a, direction, b):
    opposite = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}
    a.exits[direction] = b.key
    b.exits[opposite[direction]] = a.key


# =====================================================================
# PROLOGUE: THE SUMP
# =====================================================================

# P1 Reboot -----------------------------------------------------------
p1 = room('p1', 0, 'Reboot')
p1.solid(0, 19, 29, 22)
p1.solid(0, 12, 1, 18).solid(2, 15, 2, 18)
p1.deco('g', 0, 14, 1, 14).deco('v', 0, 16, 1, 16)
p1.solid(13, 17, 19, 18).solid(14, 16, 18, 16).solid(15, 15, 17, 15)      # scrap heap
p1.deco('x', 15, 17, 17, 17)
p1.plat(20, 24, 13)
p1.solid(25, 15, 29, 18)                                                  # container
p1.deco('x', 26, 16, 28, 16).deco('c', 25, 15, 29, 15)
p1.solid(6, 18, 8, 18).deco('z', 6, 18, 8, 18)                            # crate pile
p1.obj('start', cx(4), bottom(18))
p1.obj('trig', -999, 0, a='boot')
p1.obj('trig', cx(11), 0, a='hint_jump')
p1.obj('sign', cx(27) + 8, top(11), a='NeonSign_Danger')

# P2 Climb ------------------------------------------------------------
p2 = room('p2', 0, 'Climb')
p2.solid(0, 19, 29, 22)
p2.solid(1, 0, 16, 1)                                                     # overhang
p2.solid(0, 15, 2, 18).deco('x', 0, 16, 1, 16).deco('c', 0, 15, 2, 15)      # container (matches P1)
p2.solid(21, 0, 29, 18)                                                   # right wall
p2.solid(12, 5, 16, 14)                                                   # container stack
p2.deco('x', 13, 6, 15, 6).deco('x', 13, 9, 15, 9).deco('x', 13, 12, 15, 12)
p2.deco('i', 12, 15, 12, 18).deco('i', 16, 15, 16, 18)                    # stilts
p2.solid(4, 17, 7, 18).deco('x', 5, 18, 6, 18)
p2.plat(17, 20, 14)
p2.plat(7, 10, 9)
p2.deco('l', 22, 3, 22, 17).deco('c', 21, 4, 21, 4).deco('m', 21, 11, 21, 11)
p2.obj('trig', cx(9), 0, a='hint_cling')

# P3 First blood ------------------------------------------------------
p3 = room('p3', 0, 'First Blood')
p3.solid(0, 19, 16, 22).solid(21, 19, 29, 22)
p3.plat(17, 20, 19)
p3.solid(0, 0, 29, 2).solid(0, 0, 1, 18)
p3.solid(28, 0, 29, 13)
p3.plat(4, 9, 14).plat(21, 25, 13)
p3.deco('g', 2, 3, 27, 3).deco('i', 10, 4, 10, 18).deco('o', 3, 16, 4, 16)
p3.obj('drone', cx(8), top(11))
p3.obj('drone', cx(22), top(10))
p3.obj('door', left(29), bottom(18), a='lock')
p3.obj('trig', cx(18), 0, a='hint_attack')

# P4 Return fire ------------------------------------------------------
p4 = room('p4', 0, 'Return Fire')
p4.solid(0, 0, 29, 3)
p4.solid(0, 4, 0, 13)
p4.solid(0, 19, 9, 22)
p4.solid(10, 21, 17, 22).spikes(10, 17, 20)
p4.solid(18, 19, 29, 22)
p4.solid(25, 9, 29, 18)
p4.plat(19, 22, 15).plat(20, 23, 11)
p4.deco('z', 25, 9, 29, 9).deco('g', 26, 12, 28, 12).deco('i', 10, 4, 10, 19)
p4.obj('turret', left(25), top(16) - 8, a=-90)
p4.obj('trig', cx(3), 0, a='hint_deflect')

# P5 The barrier ------------------------------------------------------
p5 = room('p5', 0, 'The Barrier')
p5.solid(0, 0, 29, 3)
p5.solid(0, 9, 8, 22)
p5.solid(9, 19, 29, 22)
p5.solid(12, 4, 29, 12)
p5.deco('g', 13, 12, 28, 12).deco('c', 12, 12, 12, 12).deco('i', 3, 10, 3, 18)
p5.deco('x', 16, 6, 18, 6).deco('o', 22, 7, 24, 7).deco('x', 26, 9, 28, 9)
p5.obj('laser', cx(19), bottom(18))
p5.obj('trig', cx(13), 0, a='hint_dash')

# P6 Tetsu's cart -----------------------------------------------------
p6 = room('p6', 0, "Tetsu's Cart")
p6.solid(0, 19, 29, 22)
p6.solid(0, 0, 3, 12)
p6.solid(27, 0, 29, 12).deco('o', 27, 3, 29, 3).deco('u', 27, 7, 29, 7).deco('m', 27, 12, 29, 12)
p6.solid(8, 10, 14, 10)                                                    # awning
p6.deco('r', 8, 10, 14, 10)
p6.deco('i', 8, 11, 8, 18)
p6.obj('cart', cx(12), bottom(18))
p6.obj('tetsu', cx(15) + 4, bottom(18))
p6.obj('sign', cx(10), bottom(10), a='NeonSign_Ramen')
p6.obj('lantern', cx(13), bottom(10))
p6.obj('lantern', cx(9) + 6, bottom(10))
p6.obj('shrine', cx(22), bottom(18))
p6.obj('trig', cx(5), 0, a='tetsu_seen')

# P7 Gauntlet ---------------------------------------------------------
p7 = room('p7', 0, 'Gauntlet')
p7.solid(0, 0, 12, 2).solid(16, 0, 29, 2)
p7.solid(0, 3, 2, 12)
p7.solid(0, 19, 6, 22)
p7.solid(7, 21, 11, 22).spikes(7, 11, 20)
p7.solid(12, 19, 16, 22)
p7.solid(17, 21, 21, 22).spikes(17, 21, 20)
p7.solid(22, 19, 29, 22)
p7.plat(8, 10, 15).plat(18, 20, 15)
p7.plat(12, 16, 11).plat(13, 15, 6)
p7.solid(26, 3, 29, 10)
p7.deco('z', 0, 12, 2, 12).deco('g', 26, 10, 29, 10).deco('o', 4, 4, 9, 4)
p7.obj('turret', left(3), top(10) - 8, a=90)
p7.obj('drone', cx(9), top(12))
p7.obj('drone', cx(19), top(12))
p7.obj('sign', cx(24), bottom(2), a='NeonSign_Danger')

# P7s Shard room (challenge) -------------------------------------------
p7s = room('p7s', 0, 'Scrap Vault')
p7s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
p7s.solid(0, 19, 12, 22).solid(16, 19, 29, 22)
p7s.plat(13, 15, 19)
p7s.plat(4, 9, 14).plat(20, 25, 14).plat(11, 18, 9)
p7s.deco('g', 2, 3, 27, 3).deco('x', 3, 17, 5, 17).deco('x', 23, 17, 25, 17)
p7s.obj('drone', cx(6), top(11))
p7s.obj('drone', cx(23), top(11))
p7s.obj('drone', cx(14), top(6))
p7s.obj('shard', cx(14) + 8, top(6), a=1)
p7s.flags.append('challenge')

# P8 The lift ---------------------------------------------------------
p8 = room('p8', 0, 'The Lift')
p8.solid(0, 0, 19, 10)
p8.solid(0, 19, 19, 22).solid(24, 19, 29, 22)
p8.solid(24, 0, 29, 18)
p8.solid(20, 21, 23, 22)
p8.deco('z', 19, 11, 19, 18).deco('z', 24, 0, 24, 18).deco('l', 18, 9, 18, 18)
p8.deco('g', 2, 10, 17, 10).deco('o', 3, 4, 7, 4).deco('u', 10, 5, 13, 5)
p8.obj('lift', left(22), top(19), a='up')
p8.obj('trig', cx(6), 0, a='lift_talk')

# =====================================================================
# CHAPTER 1: NEON ALLEY
# =====================================================================

# A1 Arrival ----------------------------------------------------------
a1 = room('a1', 1, 'Neon Alley')
a1.solid(0, 19, 19, 22).solid(24, 19, 29, 22)
a1.solid(0, 0, 3, 13)
a1.solid(26, 0, 29, 8)
a1.deco('o', 0, 3, 3, 3).deco('u', 0, 6, 3, 6).deco('x', 0, 9, 3, 9).deco('m', 0, 12, 3, 12)
a1.deco('o', 26, 2, 29, 2).deco('u', 26, 5, 29, 5).deco('c', 26, 8, 29, 8)
a1.obj('lift', left(22), top(19), a='arrive')
a1.obj('sign', cx(5), bottom(5), a='NeonSign_Ninja')
a1.obj('sign', cx(24), bottom(4), a='NeonSign_Bar')
a1.obj('lantern', cx(9), top(0))
a1.obj('lantern', cx(14), top(0))
a1.obj('start', cx(21) + 8, bottom(18))
a1.obj('trig', -999, 0, a='ch1_start')

# A2 Market street ----------------------------------------------------
a2 = room('a2', 1, 'Market Street')
a2.solid(0, 19, 29, 22)
a2.solid(0, 0, 1, 8).deco('o', 0, 3, 1, 3).deco('x', 0, 6, 1, 6)
a2.solid(28, 0, 29, 13)
a2.solid(5, 11, 11, 11).deco('m', 5, 11, 11, 11)                           # awning
a2.solid(17, 11, 23, 11).deco('c', 17, 11, 23, 11)
a2.deco('i', 5, 12, 5, 18).deco('i', 23, 12, 23, 18)
a2.obj('sign', cx(8), bottom(11), a='NeonSign_Ramen')
a2.obj('lantern', cx(19), bottom(11))
a2.obj('lantern', cx(22), bottom(11))
a2.obj('sign', cx(28) + 8, bottom(13), a='NeonSign_Bar')
a2.obj('hannya', cx(18), bottom(18), a=0)
a2.obj('door', left(29), bottom(18), a='lock')
a2.obj('trig', cx(6), 0, a='hint_integrity')

# A3 Rooftops ---------------------------------------------------------
a3 = room('a3', 1, 'Rooftops')
a3.solid(0, 19, 29, 22)
a3.solid(7, 0, 29, 1).solid(0, 0, 1, 1)
a3.solid(20, 15, 29, 18)
a3.solid(10, 11, 17, 12)
a3.solid(0, 6, 6, 8)
a3.solid(0, 2, 0, 13)
a3.deco('o', 21, 17, 28, 17).deco('x', 11, 12, 16, 12).deco('u', 1, 8, 5, 8)
a3.deco('m', 20, 15, 29, 15).deco('c', 10, 11, 17, 11)
a3.obj('puddle', cx(11) + 8, bottom(18))
a3.obj('puddle', cx(25), bottom(14))
a3.obj('puddle', cx(13) + 8, bottom(10))
a3.obj('drone', cx(13), top(7))
a3.obj('drone', cx(23), top(11))
a3.obj('sign', cx(18), bottom(1), a='NeonSign_Danger')

# A4 DaiCam -----------------------------------------------------------
a4 = room('a4', 1, 'Cornered')
a4.solid(0, 19, 1, 22).solid(7, 19, 29, 22)
a4.plat(2, 6, 19)
a4.solid(0, 0, 1, 18)
a4.solid(28, 0, 29, 13)
a4.solid(10, 9, 16, 9).deco('r', 10, 9, 16, 9)
a4.deco('o', 0, 4, 1, 4).deco('x', 0, 10, 1, 10)
a4.obj('sign', cx(13), bottom(9), a='NeonSign_Bar')
a4.obj('lantern', cx(11), bottom(9))
a4.obj('daicam', cx(25), bottom(18))
a4.obj('hannya', cx(16), bottom(18), a=0)
a4.obj('hannya', cx(21), bottom(18), a=0)
a4.obj('door', left(29), bottom(18), a='lock')
a4.obj('trig', cx(4), 0, a='daicam_start')

# A5 Crate alley ------------------------------------------------------
a5 = room('a5', 1, 'Crate Alley')
a5.solid(0, 19, 29, 22)
a5.solid(0, 0, 29, 2)
a5.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
a5.plat(6, 11, 14).plat(18, 23, 14)
a5.deco('g', 1, 3, 28, 3).deco('i', 14, 4, 14, 18)
a5.obj('crate', cx(4), bottom(18), a=1)
a5.obj('crate', cx(5) + 6, bottom(18), a=0)
a5.obj('crate', cx(21), bottom(13), a=1)
a5.obj('crate', cx(26), bottom(18), a=0)
a5.obj('hannya', cx(16), bottom(18), a=1)
a5.obj('lantern', cx(9), top(3))
a5.obj('lantern', cx(20), top(3))
a5.obj('trig', cx(7), 0, a='hint_breach')

# A6 Shrine -----------------------------------------------------------
a6 = room('a6', 1, 'Vending Shrine')
a6.solid(0, 19, 29, 22)
a6.solid(0, 0, 29, 2)
a6.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
a6.solid(9, 12, 20, 12).deco('c', 9, 12, 20, 12)
a6.deco('o', 2, 5, 6, 5).deco('u', 23, 5, 27, 5).deco('x', 11, 6, 18, 6)
a6.obj('shrine', cx(15), bottom(18))
a6.obj('sign', cx(4), bottom(2), a='NeonSign_Ninja')
a6.obj('lantern', cx(12), bottom(12))
a6.obj('lantern', cx(17), bottom(12))

# A7 Three-thug ambush ------------------------------------------------
a7 = room('a7', 1, 'Ambush')
a7.solid(0, 19, 29, 22)
a7.solid(0, 0, 12, 4).solid(16, 0, 29, 4)
a7.breakable(13, 3, 15, 4)
a7.solid(0, 5, 0, 13).solid(29, 5, 29, 13)
a7.plat(3, 8, 14).plat(21, 26, 14).plat(11, 17, 10)
a7.deco('g', 1, 5, 12, 5).deco('g', 16, 5, 28, 5).deco('o', 2, 8, 5, 8).deco('u', 24, 8, 27, 8)
a7.obj('door', left(0) + 8, bottom(18), a='ambush')
a7.obj('door', left(29), bottom(18), a='lock')
a7.obj('hannya', cx(14), bottom(18), a=0)
a7.obj('hannya', cx(23), bottom(13), a=0)
a7.obj('hannya', cx(6), bottom(13), a=1)
a7.obj('trig', cx(4), 0, a='ambush')

# A8 Memory shard room ------------------------------------------------
a8 = room('a8', 1, 'Hidden Den')
a8.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
a8.solid(0, 19, 12, 22).solid(16, 19, 29, 22)
a8.plat(13, 15, 19)
a8.plat(4, 9, 14).plat(20, 25, 14)
a8.deco('g', 2, 3, 27, 3).deco('m', 2, 18, 12, 18).deco('c', 16, 18, 27, 18)
a8.obj('hannya', cx(6), bottom(18), a=0)
a8.obj('hannya', cx(23), bottom(18), a=1)
a8.obj('drone', cx(14), top(10))
a8.obj('shard', cx(14) + 8, top(10), a=2)
a8.obj('sign', cx(8), bottom(2), a='NeonSign_Bar')
a8.flags.append('challenge')

# A9 Boss gate --------------------------------------------------------
a9 = room('a9', 1, 'Boss Gate')
a9.solid(0, 19, 29, 22)
a9.solid(0, 0, 29, 2)
a9.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
a9.deco('z', 1, 3, 28, 3).deco('r', 24, 13, 28, 13).deco('x', 3, 7, 8, 7)
a9.obj('shrine', cx(8), bottom(18))
a9.obj('sign', cx(20), bottom(3), a='NeonSign_Danger')
a9.obj('lantern', cx(14), bottom(3))
a9.obj('trig', cx(16), 0, a='boss_gate')

# A10 Big Oni arena ---------------------------------------------------
a10 = room('a10', 1, 'Rooftop Arena')
a10.solid(0, 19, 29, 22)
a10.solid(29, 0, 29, 18)
a10.solid(0, 0, 0, 13)
a10.deco('z', 29, 0, 29, 18).deco('m', 0, 19, 29, 19)
a10.obj('puddle', cx(3), bottom(18))
a10.obj('puddle', cx(26), bottom(18))
a10.obj('door', left(0) + 8, bottom(18), a='ambush')
a10.obj('oni', cx(21), bottom(18))
a10.obj('sign', cx(6), top(2), a='NeonSign_Ninja')
a10.obj('sign', cx(23), top(1), a='NeonSign_Danger')
a10.obj('trig', cx(4), 0, a='boss_start')
a10.flags.append('boss')

# --- connections --------------------------------------------------------
link(p1, 'R', p2)
link(p2, 'U', p3)
link(p3, 'R', p4)
link(p4, 'R', p5)
link(p5, 'R', p6)
link(p6, 'R', p7)
link(p7, 'U', p7s)
link(p7, 'R', p8)
link(p8, 'U', a1)
link(a1, 'R', a2)
link(a2, 'R', a3)
link(a3, 'U', a4)
link(a4, 'R', a5)
link(a5, 'R', a6)
link(a6, 'R', a7)
link(a7, 'U', a8)
link(a7, 'R', a9)
link(a9, 'R', a10)

ROOM_INDEX = {r.key: i + 1 for i, r in enumerate(ROOMS)}


# edge cells that differ but that the player can never reach
UNREACHABLE = {('p2', 'U', 0)}


def validate():
    """Check that openings line up across every room connection."""
    problems = []
    for r in ROOMS:
        for d, k in r.exits.items():
            o = ROOMS[ROOM_INDEX[k] - 1]
            if d == 'R':
                a = [r.g[i][W - 1] in '#B' for i in range(H)]
                b = [o.g[i][0] in '#B' for i in range(H)]
            elif d == 'U':
                a = [r.g[0][i] in '#B' for i in range(W)]
                b = [o.g[H - 1][i] in '#B' for i in range(W)]
            else:
                continue
            for i, (x, y) in enumerate(zip(a, b)):
                if x != y and (r.key, d, i) not in UNREACHABLE:
                    problems.append('%s %s %s: index %d %s/%s' % (r.key, d, k, i, x, y))
    return problems


if __name__ == '__main__':
    for p in validate():
        print(p)
    for r in ROOMS:
        print(r.key, r.exits)
