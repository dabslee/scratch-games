"""
Room layouts for the vertical slice (Prologue + Chapter 1).

Every room is one 480x360 screen: 30 columns x 23 rows of 16-unit tiles
(8x8 art pixels). Row 22 is only half visible. Cell (c, r) has its centre
at stage (-232 + 16c, 172 - 16r).

Collision characters stored in the room grid string:
  .  empty            #  solid           =  one-way platform
  ^  spikes (floor)   v  spikes (ceiling)
  B  breakable block (solid until broken)
  ~  cooling-mist updraft     %  pulsing updraft (on 70 of every 110 frames)
  G  phasing block, solid in phase A    H  phasing block, solid in phase B
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
        self.wind = 0                   # constant push on Hotaru (px per frame)
        self.moving = 0                 # 1 = the train is moving (background scrolls)
        self.flip = 0                   # 1 = Kuro periodically swaps left and right

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

    def mist(self, c1, r1, r2, pulse=False):
        """A two-cell-wide updraft column over rows r1..r2 (vent at the bottom)."""
        ch = '%' if pulse else '~'
        for r in range(r1, r2 + 1):
            for c in (c1, c1 + 1):
                if self.g[r][c] == '.':
                    self.g[r][c] = ch
        self.obj('mist', left(c1) + 16, bottom(r2), a=r2 - r1 + 1, b=1 if pulse else 0)
        return self

    def phase(self, c1, c2, r, ch='G'):
        """A row of phasing blocks (G: solid in phase A, H: solid in phase B)."""
        for c in range(c1, c2 + 1):
            self.g[r][c] = ch
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
p2.plat(17, 20, 15)
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
p4.solid(10, 21, 15, 22).spikes(10, 15, 20)
p4.solid(16, 19, 29, 22)
p4.solid(25, 9, 29, 18)
p4.plat(19, 22, 15).plat(20, 23, 11)
p4.deco('z', 25, 9, 29, 9).deco('g', 26, 12, 28, 12).deco('i', 10, 4, 10, 18)
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
p7.plat(12, 16, 11).plat(13, 15, 7).plat(13, 15, 4)
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
a3.solid(0, 7, 6, 8)
a3.plat(2, 5, 4)
a3.solid(0, 2, 0, 6).solid(0, 9, 0, 13)
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
a7.solid(0, 0, 12, 2).solid(16, 0, 29, 2)
a7.breakable(13, 1, 15, 2)
a7.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
a7.plat(3, 8, 14).plat(21, 26, 14).plat(11, 17, 10).plat(13, 15, 6)
a7.deco('g', 1, 3, 12, 3).deco('g', 16, 3, 28, 3).deco('o', 2, 8, 5, 8).deco('u', 24, 8, 27, 8)
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
a10.solid(28, 0, 29, 13)
a10.solid(0, 0, 0, 13)
a10.deco('z', 28, 0, 28, 13).deco('m', 0, 19, 29, 19)
a10.obj('door', left(29), bottom(18), a='lock')
a10.obj('puddle', cx(3), bottom(18))
a10.obj('puddle', cx(26), bottom(18))
a10.obj('door', left(0) + 8, bottom(18), a='ambush')
a10.obj('oni', cx(21), bottom(18))
a10.obj('sign', cx(6), top(2), a='NeonSign_Ninja')
a10.obj('sign', cx(23), top(1), a='NeonSign_Danger')
a10.obj('trig', cx(4), 0, a='boss_start')
a10.flags.append('boss')


# =====================================================================
# CHAPTER 2: THE PACHINKO VAULTS
# =====================================================================

# B1 Vault entrance ---------------------------------------------------
b1 = room('b1', 2, 'Vault Entrance')
b1.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13)
b1.solid(28, 3, 29, 13)
b1.solid(11, 16, 18, 18).deco('y', 11, 16, 18, 16)
b1.plat(3, 7, 14).plat(22, 26, 14)
b1.deco('g', 1, 3, 27, 3)
b1.obj('start', cx(3), bottom(18))
b1.obj('sign', cx(14) + 8, top(4), a='NeonSign_Jackpot')
for c in (2, 5, 21, 24):
    b1.obj('pachinko', cx(c), bottom(18))
b1.obj('lantern', cx(9), top(3))
b1.obj('lantern', cx(20), top(3))
b1.obj('trig', -999, 0, a='ch2_start')

# B2 Laser hall -------------------------------------------------------
b2 = room('b2', 2, 'Laser Hall')
b2.solid(0, 19, 29, 22).solid(0, 0, 29, 11)
b2.solid(0, 12, 0, 13).solid(28, 12, 29, 13)
b2.deco('u', 2, 9, 9, 9).deco('o', 12, 9, 17, 9).deco('u', 20, 9, 26, 9).deco('y', 1, 11, 28, 11)
b2.obj('laser', cx(9), bottom(18), b=1)
b2.obj('laser', cx(19), bottom(18), b=50)
b2.obj('hannya', cx(14), bottom(18), a=0)
b2.obj('croupier', cx(25), bottom(18), a=0)
b2.obj('door', left(29), bottom(18), a='lock')
b2.obj('trig', cx(3), 0, a='lasers')

# B3 Slot floor -------------------------------------------------------
b3 = room('b3', 2, 'Slot Floor')
b3.solid(0, 19, 29, 22).solid(0, 0, 23, 2).solid(28, 0, 29, 18)
b3.solid(0, 3, 0, 13)
b3.solid(12, 9, 13, 18).deco('y', 12, 9, 13, 9)
b3.plat(14, 18, 15).plat(19, 23, 11).plat(23, 27, 7).plat(24, 27, 3)
b3.plat(4, 9, 14)
b3.obj('shrine', cx(4), bottom(18))
b3.obj('slotturret', left(14), top(12) - 8, a=90)
b3.obj('slotturret', left(28), top(15) - 8, a=-90)
b3.obj('pachinko', cx(7), bottom(18))
b3.obj('pachinko', cx(9), bottom(18))
b3.obj('trig', cx(10), 0, a='slots')

# B4 Pachinko shaft (vertical) ----------------------------------------
b4 = room('b4', 2, 'Pachinko Shaft')
b4.solid(0, 0, 2, 1).solid(7, 0, 29, 1)
b4.solid(0, 2, 1, 22).solid(28, 2, 29, 22)
b4.solid(2, 19, 23, 22).plat(24, 27, 19)
b4.plat(17, 22, 15).plat(9, 14, 11).plat(16, 21, 7).plat(10, 13, 5).plat(3, 8, 3)
b4.deco('o', 2, 6, 4, 6).deco('u', 24, 10, 26, 10).deco('x', 3, 14, 6, 14)
b4.obj('drone', cx(12), top(9))
b4.obj('drone', cx(20), top(13))
b4.obj('slotturret', left(28), top(9) - 8, a=-90)
b4.obj('pachinko', cx(5), bottom(18))
b4.obj('pachinko', cx(8), bottom(18))

# B5 High rollers lounge ----------------------------------------------
b5 = room('b5', 2, 'High Rollers')
b5.solid(0, 0, 23, 2).solid(27, 0, 29, 2)
b5.solid(0, 3, 1, 22).solid(28, 3, 29, 13)
b5.solid(2, 19, 2, 22).solid(7, 19, 29, 22).plat(3, 6, 19)
b5.plat(8, 13, 14).plat(17, 22, 14).plat(22, 26, 10).plat(24, 26, 6)
b5.deco('y', 2, 3, 27, 3).deco('u', 9, 8, 13, 8)
b5.obj('croupier', cx(10), bottom(13), a=0)
b5.obj('croupier', cx(20), bottom(13), a=0)
b5.obj('hannya', cx(16), bottom(18), a=1)
b5.obj('door', left(29), bottom(18), a='lock')
b5.obj('sign', cx(15), top(3), a='NeonSign_Jackpot')
b5.obj('trig', cx(4), 0, a='rollers')

# B5s Shard room -------------------------------------------------------
b5s = room('b5s', 2, 'Back Room')
b5s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
b5s.solid(0, 19, 23, 22).solid(27, 19, 29, 22).plat(24, 26, 19)
b5s.plat(4, 9, 14).plat(13, 18, 11)
b5s.deco('y', 2, 3, 27, 3).deco('o', 3, 6, 8, 6)
b5s.obj('slotturret', left(2), top(10) - 8, a=90)
b5s.obj('croupier', cx(16), bottom(18), a=0)
b5s.obj('drone', cx(20), top(9))
b5s.obj('shard', cx(15) + 8, top(8), a=3)
b5s.flags.append('challenge')

# B6 Cashier's cage ---------------------------------------------------
b6 = room('b6', 2, "Cashier's Cage")
b6.solid(0, 19, 29, 22).solid(0, 0, 29, 2)
b6.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
b6.solid(14, 12, 26, 12).deco('y', 14, 12, 26, 12)
b6.deco('o', 2, 6, 6, 6).deco('u', 9, 6, 12, 6)
b6.obj('shrine', cx(5), bottom(18))
b6.obj('daicam', cx(20), bottom(18), a='cage')
b6.obj('lantern', cx(16), bottom(12))
b6.obj('lantern', cx(24), bottom(12))
b6.obj('trig', cx(12), 0, a='daicam3')

# B7 Boss gate --------------------------------------------------------
b7 = room('b7', 2, 'Velvet Rope')
b7.solid(0, 19, 29, 22).solid(0, 0, 29, 2)
b7.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
b7.deco('z', 1, 3, 28, 3).deco('r', 22, 12, 28, 12)
for c in (4, 8, 21, 25):
    b7.obj('pachinko', cx(c), bottom(18))
b7.obj('sign', cx(14) + 8, top(4), a='NeonSign_Jackpot')
b7.obj('trig', cx(12), 0, a='luck_gate')

# B8 Lady Luck's table ------------------------------------------------
b8 = room('b8', 2, "Lady Luck's Table")
b8.solid(0, 19, 29, 22).solid(0, 0, 29, 1)
b8.solid(0, 2, 0, 13).solid(29, 2, 29, 13)
b8.plat(3, 7, 14).plat(22, 26, 14)
b8.deco('y', 1, 19, 28, 19).deco('z', 29, 2, 29, 13)
b8.obj('slot', 0, 64)
b8.obj('door', left(29), bottom(18), a='lock')
b8.obj('door', left(0) + 8, bottom(18), a='ambush')
b8.obj('luck', cx(22), bottom(18))
b8.obj('trig', cx(4), 0, a='luck_start')
b8.flags.append('boss')


# =====================================================================
# CHAPTER 3: THE SERVER GARDENS
# =====================================================================

# C1 Garden gate ------------------------------------------------------
c1 = room('c1', 3, 'Garden Gate')
c1.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
c1.solid(12, 17, 17, 18).plat(20, 25, 14)
c1.deco('g', 1, 3, 28, 3)
c1.obj('start', cx(3), bottom(18))
c1.obj('toro', cx(7), bottom(18))
c1.obj('toro', cx(10), bottom(18))
c1.obj('bonsai', cx(14) + 8, bottom(16))
for c in (20, 22, 24, 26):
    c1.obj('rack', cx(c), bottom(18))
c1.obj('trig', -999, 0, a='ch3_start')

# C2 Mist steps (exit up on the hanging updraft) ----------------------
c2 = room('c2', 3, 'Mist Steps')
c2.solid(0, 19, 29, 22).solid(0, 0, 14, 1).solid(19, 0, 29, 1)
c2.solid(0, 2, 1, 13).solid(28, 2, 29, 18)
c2.mist(5, 7, 18).deco('v', 5, 19, 6, 19)
c2.plat(8, 13, 9)
c2.mist(16, 0, 12)
c2.solid(22, 14, 27, 18).deco('g', 22, 14, 27, 14)
c2.obj('drone', cx(20), top(10))
c2.obj('toro', cx(24), bottom(13))
c2.obj('bonsai', cx(10), bottom(8))
c2.obj('trig', cx(3), 0, a='mist')

# C3 Rack rows ------------------------------------------------------
c3 = room('c3', 3, 'Rack Rows')
c3.solid(0, 19, 14, 22).solid(19, 19, 29, 22).solid(0, 0, 29, 2)
c3.solid(0, 3, 0, 18).solid(29, 3, 29, 13)
c3.mist(16, 15, 22)
c3.deco('g', 1, 3, 28, 3)
c3.obj('shrine', cx(3), bottom(18))
for c in (6, 8, 10, 12):
    c3.obj('pod', cx(c), bottom(18))
for c in (21, 23, 25, 27):
    c3.obj('rack', cx(c), bottom(18))
c3.obj('warden', cx(24), bottom(18), a=0)
c3.obj('trig', cx(5), 0, a='racks')
c3.obj('trig', cx(19), 0, a='warden')

# C4 Koi terraces ---------------------------------------------------
c4 = room('c4', 3, 'Koi Terraces')
c4.solid(0, 19, 8, 22).solid(9, 21, 20, 22).solid(21, 13, 29, 22).solid(0, 0, 29, 2)
c4.solid(0, 3, 0, 13)
c4.spikes(9, 20, 20)
c4.mist(15, 6, 19, pulse=True).deco('v', 15, 20, 16, 20)
c4.plat(3, 7, 13).plat(10, 12, 16)
c4.deco('g', 21, 13, 29, 13)
c4.obj('turret', left(1), top(8) - 8, a=90)
c4.obj('drone', cx(10), top(11))
c4.obj('toro', cx(24), bottom(12))
c4.obj('bonsai', cx(27), bottom(12))
c4.obj('trig', cx(4), 0, a='pulse')

# C5 Cooling tower (down the shaft; updraft up to the root room) -----
c5 = room('c5', 3, 'Cooling Tower')
c5.solid(0, 0, 19, 2).solid(24, 0, 29, 2).solid(0, 13, 6, 22).solid(7, 19, 29, 22)
c5.solid(29, 3, 29, 13)
c5.plat(8, 12, 15).plat(13, 17, 11).plat(25, 28, 9)
c5.spikes(9, 15, 18)
c5.mist(21, 0, 18, pulse=True).deco('v', 21, 19, 22, 19)
c5.obj('drone', cx(12), top(8))
c5.obj('warden', cx(26), bottom(18), a=1)
c5.obj('pod', cx(17), bottom(18))
c5.obj('pod', cx(25), bottom(18))

# C5s Root directory (Memory Shard challenge) -----------------------
c5s = room('c5s', 3, 'Root Directory')
c5s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
c5s.solid(0, 19, 19, 22).solid(24, 19, 29, 22)
c5s.mist(21, 15, 22)
c5s.plat(4, 9, 13).plat(11, 16, 10)
c5s.deco('g', 2, 3, 27, 3)
c5s.obj('warden', cx(8), bottom(18), a=1)
c5s.obj('warden', cx(14), bottom(18), a=0)
c5s.obj('shard', cx(13) + 8, top(7), a=4)
for c in (3, 26):
    c5s.obj('pod', cx(c), bottom(18))
c5s.flags.append('challenge')

# C6 Zen court (DaiCam stuck in an updraft; ambush) -----------------
c6 = room('c6', 3, 'Zen Court')
c6.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
c6.mist(19, 6, 18).deco('v', 19, 19, 20, 19)
c6.plat(23, 27, 13)
c6.deco('g', 1, 3, 28, 3)
c6.obj('shrine', cx(4), bottom(18))
c6.obj('daicam', cx(20) - 8, bottom(10), a='float', b=bottom(18))
c6.obj('warden', cx(14), bottom(18), a=0)
c6.obj('warden', cx(25), bottom(18), a=1)
c6.obj('door', left(29), bottom(18), a='lock')
c6.obj('toro', cx(8), bottom(18))
c6.obj('bonsai', cx(25), bottom(12))
c6.obj('trig', cx(9), 0, a='daicam4')

# C7 Moon bridge ----------------------------------------------------
c7 = room('c7', 3, 'Moon Bridge')
c7.solid(0, 19, 6, 22).solid(23, 19, 29, 22).solid(7, 21, 22, 22).solid(0, 0, 29, 2)
c7.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
c7.plat(7, 22, 19)
c7.spikes(7, 22, 20)
for c in (3, 26):
    c7.obj('toro', cx(c), bottom(18))
c7.obj('trig', cx(10), 0, a='muk_gate')

# C8 Mukuro's dojo --------------------------------------------------
c8 = room('c8', 3, "Mukuro's Dojo")
c8.solid(0, 19, 29, 22).solid(0, 0, 29, 1)
c8.solid(0, 2, 0, 13).solid(29, 2, 29, 13)
c8.plat(3, 7, 14).plat(22, 26, 14)
c8.deco('g', 1, 19, 28, 19)
c8.obj('door', left(0) + 8, bottom(18), a='ambush')
c8.obj('door', left(29), bottom(18), a='lock')
c8.obj('toro', cx(11), bottom(18))
c8.obj('toro', cx(18), bottom(18))
c8.obj('mukuro', cx(22), bottom(18))
c8.obj('trig', cx(4), 0, a='muk_start')
c8.flags.append('boss')


# =====================================================================
# CHAPTER 4: MONORAIL ASCENT
# =====================================================================
ROOF = 15                               # car roofs: top edge at stage y = -60


def car(r, c1, c2, roof=ROOF):
    """A monorail car: a solid body from the roof down, with windows."""
    r.solid(c1, roof, c2, 22).deco('c', c1, roof, c2, roof)
    for c in range(c1 + 1, c2, 3):
        r.deco('o', c, roof + 2)
    return r


# D1 Platform 9 (station) ----------------------------------------------
d1 = room('d1', 4, 'Platform 9')
d1.solid(0, 19, 25, 22).solid(0, 0, 25, 2).solid(0, 3, 0, 13)
car(d1, 18, 29)
d1.deco('i', 8, 3, 8, 18).deco('i', 15, 3, 15, 18).deco('z', 1, 19, 17, 19)
d1.obj('start', cx(2), bottom(18))
d1.obj('shrine', cx(5), bottom(18))
d1.obj('sign', cx(11) + 8, top(4), a='NeonSign_Danger')
d1.obj('lantern', cx(4), top(3))
d1.obj('lantern', cx(12), top(3))
d1.obj('trig', -999, 0, a='ch4_start')

# D2 Roof run ----------------------------------------------------------
d2 = room('d2', 4, 'Roof Run')
car(d2, 0, 7)
car(d2, 12, 19)
car(d2, 25, 29)
d2.plat(8, 11, 19).plat(20, 24, 19)
d2.obj('drone', cx(10), top(9))
d2.obj('drone', cx(22), top(8))
d2.obj('hannya', cx(16), bottom(14), a=0)
d2.obj('trig', cx(2), 0, a='wind')
d2.wind, d2.moving = -1.3, 1

# D3 Signal line -------------------------------------------------------
d3 = room('d3', 4, 'Signal Line')
car(d3, 0, 9)
car(d3, 13, 21)
car(d3, 25, 29)
d3.solid(4, 12, 7, 14).solid(16, 12, 19, 14).deco('c', 4, 12, 7, 12).deco('c', 16, 12, 19, 12)
d3.plat(10, 12, 19).plat(22, 24, 19)
d3.obj('post', 0, top(ROOF), a=150, b=0)
d3.obj('hannya', cx(14), bottom(14), a=1)
d3.obj('croupier', cx(27), bottom(14), a=0)
d3.obj('trig', cx(2), 0, a='posts')
d3.wind, d3.moving = -1.3, 1

# D4 Spiral junction (climb to the upper line; side door to the bay) ----
d4 = room('d4', 4, 'Spiral Junction')
d4.solid(0, 15, 10, 22).solid(11, 19, 25, 22).solid(26, 0, 29, 22).solid(0, 0, 18, 1)
d4.clear(26, 16, 29, 18)
d4.deco('c', 0, 15, 10, 15).deco('c', 11, 19, 25, 19)
for r in range(3, 15, 3):
    d4.deco('o', 27, r).deco('o', 28, r)
d4.deco('l', 25, 4, 25, 18)
d4.plat(12, 16, 12).plat(18, 22, 9).plat(13, 17, 6).plat(20, 24, 3)
d4.obj('shrine', cx(14), bottom(18))
d4.obj('trig', cx(4), 0, a='junction')

# D5 Upper line --------------------------------------------------------
d5 = room('d5', 4, 'Upper Line')
car(d5, 0, 18)
car(d5, 26, 29)
d5.solid(8, 12, 11, 14).deco('c', 8, 12, 11, 12)
d5.plat(19, 25, 19)
d5.obj('post', 0, top(ROOF), a=190, b=60)
d5.obj('croupier', cx(4), bottom(14), a=0)
d5.obj('hannya', cx(15), bottom(14), a=1)
d5.obj('drone', cx(22), top(10))
d5.wind, d5.moving = -1.3, 1

# D5s Maintenance bay (Memory Shard challenge, inside the tower) ---------
d5s = room('d5s', 4, 'Maintenance Bay')
d5s.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 15).solid(28, 3, 29, 18)
d5s.plat(4, 9, 14).plat(12, 17, 10).plat(20, 25, 7)
for r in (5, 9, 13):
    d5s.deco('o', 2, r, 5, r).deco('o', 22, r, 25, r)
d5s.obj('croupier', cx(8), bottom(18), a=0)
d5s.obj('croupier', cx(22), bottom(18), a=0)
d5s.obj('hannya', cx(15), bottom(18), a=1)
d5s.obj('shard', cx(22) + 8, top(5), a=5)
d5s.flags.append('challenge')

# D6 Dining car --------------------------------------------------------
d6 = room('d6', 4, 'Dining Car')
d6.solid(0, 15, 29, 22).solid(2, 3, 29, 5).solid(29, 6, 29, 9)
d6.deco('x', 2, 6, 29, 14).deco('u', 3, 8, 28, 9).deco('c', 2, 5, 29, 5)
for c in (5, 9, 13, 17):
    d6.obj('seat', cx(c), bottom(14))
d6.obj('daicam', cx(21), bottom(14), a='dine')
d6.obj('hannya', cx(10), bottom(14), a=0)
d6.obj('hannya', cx(16), bottom(14), a=1)
d6.obj('croupier', cx(26), bottom(14), a=0)
d6.obj('door', left(29), bottom(14), a='lock')
d6.obj('trig', cx(6), 0, a='daicam5')
d6.moving = 1

# D7 Observation deck --------------------------------------------------
d7 = room('d7', 4, 'Observation Deck')
d7.solid(0, 15, 29, 22).solid(0, 3, 12, 5).solid(0, 6, 0, 9)
d7.deco('x', 0, 6, 12, 14).deco('u', 1, 8, 11, 9).deco('c', 0, 5, 12, 5).deco('c', 13, 15, 29, 15)
d7.obj('trig', cx(16), 0, a='raijin_gate')
d7.wind, d7.moving = -1.0, 1

# D8 Raijin -----------------------------------------------------------
d8 = room('d8', 4, 'Thunder Line')
d8.solid(0, 15, 29, 22).solid(29, 0, 29, 14)
d8.deco('c', 0, 15, 29, 15).deco('z', 29, 0, 29, 14)
for c in range(2, 29, 4):
    d8.deco('o', c, 17)
d8.obj('door', left(0) + 8, bottom(14), a='ambush')
d8.obj('raijin', 116, top(ROOF))
d8.obj('trig', cx(4), 0, a='raijin_start')
d8.flags.append('boss')
d8.moving = 1


# =====================================================================
# CHAPTER 5: HOLLOW FLOOR (inside Hotaru's head)
# =====================================================================

# E1 Static -----------------------------------------------------------
e1 = room('e1', 5, 'Static')
e1.solid(0, 19, 9, 22).solid(20, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 18).solid(29, 3, 29, 13)
e1.phase(10, 13, 18, 'G').phase(14, 16, 18, 'H').phase(17, 19, 18, 'G')
e1.obj('start', cx(3), bottom(18))
e1.obj('trig', -999, 0, a='ch5_start')
e1.obj('trig', cx(7), 0, a='glitch')

# E2 Memory: the Sump -------------------------------------------------
e2 = room('e2', 5, 'Memory: The Sump')
e2.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
e2.solid(9, 16, 13, 18).solid(10, 14, 12, 15).solid(20, 15, 25, 18)
e2.phase(15, 18, 12, 'G').plat(3, 6, 14)
e2.obj('laser', cx(17), bottom(18), b=1)
e2.obj('drone', cx(8), top(9))
e2.obj('hannya', cx(23), bottom(14), a=0)
e2.obj('trig', cx(3), 0, a='sump_mem')

# E3 Memory: Tetsu's roof ---------------------------------------------
e3 = room('e3', 5, "Memory: Tetsu's Roof")
e3.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
e3.solid(18, 17, 29, 18).deco('z', 18, 17, 29, 17)
e3.obj('shrine', cx(4), bottom(18))
e3.obj('cart', cx(22), bottom(16))
e3.obj('tetsu', cx(26), bottom(16), a='mem')
e3.obj('lantern', cx(21), top(3))
e3.obj('trig', cx(14), 0, a='tetsu_mem')

# E4 Memory: the Academy (climb on phasing blocks) --------------------
e4 = room('e4', 5, 'Memory: The Academy')
e4.solid(0, 19, 29, 22).solid(0, 0, 21, 1).solid(26, 0, 29, 1)
e4.solid(0, 2, 0, 13).solid(0, 17, 0, 18).solid(28, 2, 29, 18)
e4.phase(4, 8, 15, 'G').phase(10, 14, 12, 'H').phase(4, 8, 9, 'G').phase(10, 14, 6, 'H')
e4.plat(16, 19, 5).plat(22, 25, 3)
e4.obj('warden', cx(18), bottom(18), a=0)
e4.obj('drone', cx(22), top(10))

# E5 Possession -------------------------------------------------------
e5 = room('e5', 5, 'Possession')
e5.solid(0, 19, 7, 22).solid(8, 21, 21, 22).solid(26, 19, 29, 22).solid(0, 0, 3, 1).solid(8, 0, 29, 1)
e5.plat(22, 25, 19)
e5.solid(0, 2, 0, 18).solid(29, 2, 29, 13)
e5.spikes(8, 21, 20)
e5.plat(9, 12, 16).plat(16, 20, 16).plat(1, 3, 14).plat(4, 7, 10).plat(3, 6, 5)
e5.obj('drone', cx(14), top(10))
e5.obj('trig', cx(4), 0, a='possess')
e5.flip = 1

# E5s Locked memory (Memory Shard challenge) ---------------------------
e5s = room('e5s', 5, 'Locked Memory')
e5s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
e5s.solid(0, 19, 3, 22).solid(8, 19, 29, 22).plat(4, 7, 19)
e5s.phase(12, 16, 14, 'G').phase(18, 22, 10, 'H')
e5s.obj('warden', cx(12), bottom(18), a=1)
e5s.obj('warden', cx(22), bottom(18), a=0)
e5s.obj('shard', cx(20) + 8, top(7), a=6)
e5s.flags.append('challenge')

# E6 The white room ---------------------------------------------------
e6 = room('e6', 5, 'The White Room')
e6.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
e6.deco('g', 1, 3, 28, 3)
e6.obj('shrine', cx(4), bottom(18))
e6.obj('pod', cx(14), bottom(18))
e6.obj('pod', cx(16), bottom(18))
e6.obj('daicam', cx(23), bottom(18), a='echo')
e6.obj('hannya', cx(10), bottom(18), a=0)
e6.obj('warden', cx(20), bottom(18), a=0)
e6.obj('trig', cx(12), 0, a='white_room')
e6.obj('trig', cx(19), 0, a='daicam6')

# E7 Threshold --------------------------------------------------------
e7 = room('e7', 5, 'Threshold')
e7.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
e7.phase(9, 12, 15, 'G').phase(17, 20, 15, 'H')
e7.obj('trig', cx(12), 0, a='kuro_gate')

# E8 Hollow floor (Kuro) ------------------------------------------------
e8 = room('e8', 5, 'Hollow Floor')
e8.solid(0, 19, 29, 22).solid(0, 0, 29, 1).solid(0, 2, 0, 13).solid(29, 2, 29, 18)
e8.phase(4, 8, 14, 'G').phase(21, 25, 14, 'H')
e8.obj('door', left(0) + 8, bottom(18), a='ambush')
e8.obj('kuro', cx(22), bottom(18))
e8.obj('trig', cx(4), 0, a='kuro_start')
e8.flags.append('boss')


# =====================================================================
# CHAPTER 6: THE ACADEMY
# =====================================================================

# F1 Academy gate -----------------------------------------------------
f1 = room('f1', 6, 'Academy Gate')
f1.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 18).solid(29, 3, 29, 13)
f1.deco('y', 1, 19, 28, 19)
f1.obj('start', cx(3), bottom(18))
f1.obj('shrine', cx(6), bottom(18))
for c in (13, 17, 21):
    f1.obj('dummy', cx(c), bottom(18))
f1.obj('lantern', cx(10), top(3))
f1.obj('lantern', cx(24), top(3))
f1.obj('trig', -999, 0, a='ch6_start')

# F2 Kata hall --------------------------------------------------------
f2 = room('f2', 6, 'Kata Hall')
f2.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
f2.plat(4, 9, 14).plat(20, 25, 14).deco('y', 1, 19, 28, 19)
f2.obj('dummy', cx(5), bottom(18))
f2.obj('dummy', cx(8), bottom(18))
f2.obj('shell', cx(20), bottom(18), a=0)
f2.obj('trig', cx(10), 0, a='shell')

# F3 Laser drill ------------------------------------------------------
f3 = room('f3', 6, 'Laser Drill')
f3.solid(0, 19, 6, 22).solid(7, 21, 22, 22).solid(23, 19, 29, 22).solid(0, 0, 29, 2)
f3.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
f3.spikes(7, 22, 20)
f3.phase(8, 11, 17, 'G').phase(13, 16, 17, 'H').phase(18, 21, 17, 'G')
f3.obj('laser', cx(12), bottom(16), b=75)
f3.obj('laser', cx(17), bottom(16), b=75)
f3.obj('turret', left(29), top(9) - 8, a=-90)
f3.obj('trig', cx(3), 0, a='holo')

# F4 Climbing wall (exit up) ------------------------------------------
f4 = room('f4', 6, 'Climbing Wall')
f4.solid(0, 19, 29, 22).solid(0, 0, 19, 1).solid(25, 0, 29, 1)
f4.solid(0, 2, 0, 13).solid(28, 2, 29, 18)
f4.solid(13, 6, 14, 15).spikes(16, 20, 18)
f4.phase(2, 5, 15, 'G').phase(7, 10, 12, 'H').phase(2, 5, 9, 'G')
f4.plat(7, 11, 6).plat(16, 20, 5).plat(21, 24, 2)
f4.obj('drone', cx(22), top(12))
f4.obj('shell', cx(22), bottom(18), a=1)

# F5 Sparring ring (ambush; up to the loft) ---------------------------
f5 = room('f5', 6, 'Sparring Ring')
f5.solid(0, 19, 19, 22).solid(25, 19, 29, 22).plat(20, 24, 19).solid(0, 0, 3, 2).solid(8, 0, 29, 2)
f5.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
f5.plat(4, 7, 15).plat(4, 7, 10).plat(4, 7, 5).deco('r', 9, 19, 26, 19)
f5.obj('shell', cx(14), bottom(18), a=0)
f5.obj('shell', cx(23), bottom(18), a=1)
f5.obj('drone', cx(18), top(9))
f5.obj('door', left(29), bottom(18), a='lock')
f5.obj('trig', cx(9), 0, a='spar')

# F5s Instructor's loft (Memory Shard challenge) -----------------------
f5s = room('f5s', 6, "Instructor's Loft")
f5s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
f5s.solid(0, 19, 3, 22).solid(8, 19, 29, 22).plat(4, 7, 19)
f5s.plat(12, 17, 14).plat(20, 25, 10)
f5s.obj('shell', cx(15), bottom(18), a=1)
f5s.obj('turret', left(28), top(6) - 8, a=-90)
f5s.obj('shard', cx(22) + 8, top(8), a=7)
f5s.flags.append('challenge')

# F6 Barracks ---------------------------------------------------------
f6 = room('f6', 6, 'Barracks')
f6.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
f6.deco('y', 1, 19, 28, 19)
f6.obj('shrine', cx(4), bottom(18))
f6.obj('daicam', cx(18), bottom(18), a='trainee')
f6.obj('dummy', cx(22), bottom(18))
f6.obj('dummy', cx(25), bottom(18))
f6.obj('trig', cx(12), 0, a='daicam7')

# F7 Hall of instances ------------------------------------------------
f7 = room('f7', 6, 'Hall of Instances')
f7.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
for c in range(3, 28, 3):
    f7.obj('pod', cx(c), bottom(18))
f7.obj('post', 0, top(19), a=170, b=40)
f7.obj('shell', cx(24), bottom(18), a=1)
f7.obj('trig', cx(8), 0, a='instances')

# F8 Mukuro's ring (Mukuro II) ------------------------------------------
f8 = room('f8', 6, "Mukuro's Ring")
f8.solid(0, 19, 29, 22).solid(0, 0, 29, 1).solid(0, 2, 0, 13).solid(29, 2, 29, 18)
f8.plat(3, 7, 14).plat(22, 26, 14).deco('r', 1, 19, 28, 19)
f8.obj('door', left(0) + 8, bottom(18), a='ambush')
f8.obj('mukuro', cx(22), bottom(18), a=2)
f8.obj('trig', cx(4), 0, a='muk2_start')
f8.flags.append('boss')


# =====================================================================
# CHAPTER 7: THE TENSHU
# =====================================================================

# G1 Cloud gate -------------------------------------------------------
g1 = room('g1', 7, 'Cloud Gate')
g1.solid(0, 19, 29, 22).solid(0, 0, 0, 18).solid(29, 0, 29, 13)
g1.deco('y', 1, 19, 28, 19)
g1.obj('start', cx(3), bottom(18))
g1.obj('shrine', cx(6), bottom(18))
g1.obj('lantern', cx(12), top(4))
g1.obj('lantern', cx(20), top(4))
g1.obj('trig', -999, 0, a='ch7_start')
g1.obj('trig', cx(14), 0, a='mukuro_gate')

# G2 Outer bailey (rooftops above the clouds) ----------------------------
g2 = room('g2', 7, 'Outer Bailey')
g2.solid(0, 19, 7, 22).solid(11, 16, 18, 22).solid(22, 13, 29, 22).solid(29, 0, 29, 7).solid(0, 0, 0, 13)
g2.deco('y', 0, 19, 7, 19).deco('y', 11, 16, 18, 16).deco('y', 22, 13, 29, 13)
g2.plat(8, 10, 17).plat(19, 21, 17).plat(13, 16, 11)
g2.obj('shell', cx(15), bottom(15), a=1)
g2.obj('drone', cx(9), top(8))
g2.obj('drone', cx(21), top(7))
g2.obj('trig', cx(3), 0, a='bailey')
g2.wind = -1.0

# G3 Castle tiers (climb; exit up) --------------------------------------
g3 = room('g3', 7, 'Castle Tiers')
g3.solid(0, 19, 29, 22).solid(0, 0, 21, 1).solid(26, 0, 29, 1)
g3.solid(0, 2, 0, 7).solid(0, 13, 3, 18).solid(28, 2, 29, 18)
g3.solid(8, 15, 12, 18).solid(16, 11, 20, 18).spikes(13, 15, 18)
g3.plat(4, 7, 11).plat(10, 13, 8).plat(17, 20, 6).plat(22, 25, 3)
g3.phase(13, 15, 13, 'G')
g3.obj('turret', left(28), top(9) - 8, a=-90)
g3.obj('warden', cx(18), bottom(10), a=1)

# G4 Defense grid -----------------------------------------------------
g4 = room('g4', 7, 'Defense Grid')
g4.solid(0, 19, 21, 22).solid(26, 19, 29, 22).plat(22, 25, 19).solid(0, 0, 3, 2).solid(8, 0, 29, 2)
g4.solid(0, 3, 0, 13).solid(29, 3, 29, 13)
g4.plat(4, 7, 15).plat(4, 7, 10).plat(4, 7, 5)
g4.obj('laser', cx(11), bottom(18), b=1)
g4.obj('laser', cx(19), bottom(18), b=50)
g4.obj('post', 0, top(19), a=160, b=0)
g4.obj('shell', cx(15), bottom(18), a=0)
g4.obj('turret', left(29), top(8) - 8, a=-90)
g4.obj('trig', cx(9), 0, a='grid')

# G4s Daimyo's study (Memory Shard challenge) -------------------------
g4s = room('g4s', 7, "Daimyo's Study")
g4s.solid(0, 0, 29, 2).solid(0, 0, 1, 22).solid(28, 0, 29, 22)
g4s.solid(0, 19, 3, 22).solid(8, 19, 29, 22).plat(4, 7, 19)
g4s.plat(12, 17, 14).plat(20, 25, 10)
g4s.obj('shell', cx(14), bottom(18), a=1)
g4s.obj('warden', cx(22), bottom(18), a=1)
g4s.obj('shard', cx(22) + 8, top(8), a=8)
g4s.flags.append('challenge')

# G5 Harvest hall -----------------------------------------------------
g5 = room('g5', 7, 'Harvest Hall')
g5.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
for c in range(3, 28, 2):
    g5.obj('pod', cx(c), bottom(18))
g5.obj('shell', cx(14), bottom(18), a=0)
g5.obj('warden', cx(22), bottom(18), a=1)
g5.obj('door', left(29), bottom(18), a='lock')
g5.obj('trig', cx(6), 0, a='harvest')

# G6 Last shrine ------------------------------------------------------
g6 = room('g6', 7, 'Last Shrine')
g6.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
g6.deco('y', 1, 19, 28, 19)
g6.obj('shrine', cx(5), bottom(18))
g6.obj('daicam', cx(20), bottom(18), a='stream')
g6.obj('lantern', cx(10), top(3))
g6.obj('lantern', cx(16), top(3))
g6.obj('trig', cx(13), 0, a='daicam8')

# G7 Throne gate ------------------------------------------------------
g7 = room('g7', 7, 'Throne Gate')
g7.solid(0, 19, 29, 22).solid(0, 0, 29, 2).solid(0, 3, 0, 13).solid(29, 3, 29, 13)
g7.deco('y', 1, 19, 28, 19)
g7.obj('trig', cx(12), 0, a='throne')

# G8 Tenshu core (the Daimyo) --------------------------------------------
g8 = room('g8', 7, 'Tenshu Core')
g8.solid(0, 19, 29, 22).solid(0, 0, 29, 1).solid(0, 2, 0, 13).solid(29, 2, 29, 18)
g8.plat(3, 7, 14).plat(22, 26, 14).deco('y', 1, 19, 28, 19)
g8.obj('door', left(0) + 8, bottom(18), a='ambush')
g8.obj('daimyo', cx(21), bottom(18))
g8.obj('trig', cx(4), 0, a='daimyo_start')
g8.flags.append('boss')


# =====================================================================
# EPILOGUE: RAMEN IN THE RAIN
# =====================================================================
ep = room('ep', 8, "Tetsu's Cart")
ep.solid(0, 19, 29, 22).solid(0, 0, 0, 18).solid(29, 0, 29, 18)
ep.deco('g', 1, 19, 28, 19)
ep.obj('start', cx(4), bottom(18))
ep.obj('cart', cx(15), bottom(18))
ep.obj('tetsu', cx(19), bottom(18), a='mem')
ep.obj('daicam', cx(10), bottom(18), a='ep')
ep.obj('mknpc', cx(23), bottom(18))
ep.obj('sign', cx(15), top(5), a='NeonSign_Ramen')
ep.obj('trig', -999, 0, a='epilogue')

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
link(a10, 'R', b1)
link(b1, 'R', b2)
link(b2, 'R', b3)
link(b3, 'U', b4)
link(b4, 'U', b5)
link(b5, 'U', b5s)
link(b5, 'R', b6)
link(b6, 'R', b7)
link(b7, 'R', b8)
link(b8, 'R', c1)
link(c1, 'R', c2)
link(c2, 'U', c3)
link(c3, 'R', c4)
link(c4, 'R', c5)
link(c5, 'U', c5s)
link(c5, 'R', c6)
link(c6, 'R', c7)
link(c7, 'R', c8)
link(c8, 'R', d1)
link(d1, 'R', d2)
link(d2, 'R', d3)
link(d3, 'R', d4)
link(d4, 'U', d5)
link(d4, 'R', d5s)
link(d5, 'R', d6)
link(d6, 'R', d7)
link(d7, 'R', d8)
link(e1, 'R', e2)
link(e2, 'R', e3)
link(e3, 'R', e4)
link(e4, 'U', e5)
link(e5, 'U', e5s)
link(e5, 'R', e6)
link(e6, 'R', e7)
link(e7, 'R', e8)
link(f1, 'R', f2)
link(f2, 'R', f3)
link(f3, 'R', f4)
link(f4, 'U', f5)
link(f5, 'U', f5s)
link(f5, 'R', f6)
link(f6, 'R', f7)
link(f7, 'R', f8)
link(g1, 'R', g2)
link(g2, 'R', g3)
link(g3, 'U', g4)
link(g4, 'U', g4s)
link(g4, 'R', g5)
link(g5, 'R', g6)
link(g6, 'R', g7)
link(g7, 'R', g8)

ROOM_INDEX = {r.key: i + 1 for i, r in enumerate(ROOMS)}


# edge cells that differ but that the player can never reach
UNREACHABLE = {('p2', 'U', 0), ('d3', 'R', 0), ('d3', 'R', 1)}


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
