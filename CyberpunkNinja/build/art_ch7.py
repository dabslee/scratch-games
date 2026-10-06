"""
Chapter 7 (The Tenshu) art: the Daimyo in all three forms. The castle
itself (tiles, sky, fake moon) comes straight from the pack.

All functions return 1x art-pixel images unless noted.
"""
import math
import random

from PIL import Image, ImageDraw

from assets import PALETTE as P


def C(name, a=255):
    return P[name] + (a,)


# ------------------------------------------------------------------ the exoskeleton
EXO_W, EXO_H = 84, 92
EXO_ANCHOR = (42, 91)       # feet centre

POSES = {
    # hands (x, y), sword angle in degrees (0 = forward, 90 = up), body dy, front knee raised, flame, kneel
    'idle': ((54, 52), -55, 0, False, False, False),
    'walk': ((54, 52), -50, 1, False, False, False),
    'wind': ((40, 26), 150, 0, False, False, False),
    'slash': ((66, 44), 0, 2, False, False, False),
    'low': ((60, 54), -20, 3, False, False, False),
    'stomp': ((52, 40), 100, -4, True, False, False),
    'dash': ((46, 38), 200, 2, False, True, False),
    'hurt': ((50, 54), -70, 2, False, False, False),
    'broken': ((58, 74), -80, 16, False, False, True),
}


def exo(pose='idle', frame=0):
    """The Daimyo's samurai exoskeleton, facing right."""
    hands, ang, dy, knee, flame, kneel = POSES[pose]
    dy += frame % 2 if pose in ('idle', 'walk') else 0
    im = Image.new('RGBA', (EXO_W, EXO_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lac, red, gold, steel = C('night1'), C('red2'), C('gold'), C('slate3')
    # legs
    if kneel:
        d.rectangle([28, 78, 40, 90], fill=lac, outline=C('ink'))
        d.rectangle([44, 82, 62, 90], fill=lac, outline=C('ink'))
    else:
        d.rectangle([30, 62 + dy, 38, 88], fill=lac, outline=C('ink'))
        if knee:
            d.rectangle([44, 56, 54, 66], fill=lac, outline=C('ink'))
            d.rectangle([50, 66, 58, 76], fill=lac, outline=C('ink'))
        else:
            d.rectangle([46, 62 + dy, 54, 88], fill=lac, outline=C('ink'))
        for x0 in (29, 45):
            if knee and x0 == 45:
                continue
            d.line([x0 + 1, 72, x0 + 1, 86], fill=gold)
        d.rectangle([27, 87, 40, 91], fill=steel)
        if not knee:
            d.rectangle([43, 87, 57, 91], fill=steel)
    # skirt plates (kusazuri)
    for i in range(4):
        y = 50 + dy + i * 4
        d.rectangle([22 + i, y, 60 - i, y + 3], fill=lac, outline=C('ink'))
        d.line([24 + i, y + 1, 58 - i, y + 1], fill=red if i % 2 == 0 else gold)
    # back thruster
    d.rectangle([16, 30 + dy, 22, 44 + dy], fill=steel, outline=C('ink'))
    if flame:
        for k, col in enumerate(('white', 'cyan3', 'cyan2')):
            d.polygon([(16, 32 + dy + k), (4 - k * 3, 37 + dy), (16, 42 + dy - k)], fill=C(col))
    # torso (do) with lacing
    d.rectangle([26, 28 + dy, 56, 52 + dy], fill=lac, outline=C('ink'))
    for y in range(31 + dy, 50 + dy, 3):
        d.line([28, y, 54, y], fill=red)
    d.line([26, 28 + dy, 56, 28 + dy], fill=gold)
    if kneel:
        # cracked open: the core shows through
        d.polygon([(38, 30 + dy), (44, 38 + dy), (40, 46 + dy), (46, 52 + dy)], outline=C('cyan3'))
        d.ellipse([36, 36 + dy, 46, 46 + dy], fill=C('cyan3'))
        d.ellipse([39, 39 + dy, 43, 43 + dy], fill=C('white'))
    # back shoulder guard
    d.rectangle([16, 26 + dy, 28, 44 + dy], fill=red, outline=C('ink'))
    for y in range(29 + dy, 44 + dy, 4):
        d.line([17, y, 27, y], fill=gold)
    # helmet, crest and mask
    hy = 10 + dy
    d.pieslice([28, hy, 54, hy + 26], 180, 360, fill=lac, outline=C('ink'))
    d.rectangle([28, hy + 12, 54, hy + 15], fill=lac)
    d.polygon([(26, hy + 12), (30, hy + 6), (32, hy + 14)], fill=red)
    d.polygon([(56, hy + 12), (52, hy + 6), (50, hy + 14)], fill=red)
    d.arc([26, hy - 8, 56, hy + 8], 200, 340, fill=gold, width=2)
    d.polygon([(40, hy - 2), (44, hy - 2), (42, hy + 2)], fill=gold)
    d.rectangle([36, hy + 15, 50, hy + 25], fill=C('red1'), outline=C('ink'))
    eye = C('yellow') if not kneel else C('slate3')
    d.line([39, hy + 18, 42, hy + 18], fill=eye)
    d.line([45, hy + 18, 48, hy + 18], fill=eye)
    d.line([38, hy + 22, 48, hy + 22], fill=C('white'))
    # sword (nodachi) and front arm
    hx, hyy = hands
    hyy += dy if not kneel else 0
    a = math.radians(ang)
    tip = (hx + math.cos(a) * 48, hyy - math.sin(a) * 48)
    pommel = (hx - math.cos(a) * 9, hyy + math.sin(a) * 9)
    d.line([pommel, (hx, hyy)], fill=C('red1'), width=3)
    d.line([(hx, hyy), tip], fill=C('white'), width=2)
    d.line([(hx + math.cos(a) * 3, hyy - math.sin(a) * 3), tip], fill=C('steel'))
    d.line([(52, 34 + dy), (hx, hyy)], fill=lac, width=6)
    d.ellipse([hx - 3, hyy - 3, hx + 3, hyy + 3], fill=steel)
    # front shoulder guard
    d.rectangle([48, 26 + dy, 60, 42 + dy], fill=red, outline=C('ink'))
    for y in range(29 + dy, 42 + dy, 4):
        d.line([49, y, 59, y], fill=gold)
    return im


# ------------------------------------------------------------------ the castle defense AI
def eye(state='idle', frame=0):
    """A floating crest (mon) with a single eye, 48x48."""
    im = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 45, 45], fill=C('night1'), outline=C('gold'))
    d.ellipse([5, 5, 42, 42], outline=C('gold'))
    for k in range(8):
        a = math.radians(k * 45 + frame * 11)
        d.line([24 + math.cos(a) * 12, 24 + math.sin(a) * 12, 24 + math.cos(a) * 19, 24 + math.sin(a) * 19],
               fill=C('gold'), width=2)
    if state == 'open':
        for k in range(4):
            a = math.radians(k * 90 + 45)
            d.pieslice([4, 4, 43, 43], k * 90 + 20, k * 90 + 70, fill=C('night2'))
        d.ellipse([13, 13, 34, 34], fill=C('cyan3'), outline=C('white'))
        d.ellipse([20, 20, 27, 27], fill=C('white'))
    elif state == 'dead':
        d.ellipse([14, 14, 33, 33], fill=C('slate2'))
        d.line([10, 12, 36, 38], fill=C('ink'), width=2)
    else:
        iris = {'idle': 'red2', 'charge': 'yellow'}.get(state, 'red2')
        d.ellipse([12, 16, 35, 31], fill=C('white'))
        d.ellipse([18, 17, 29, 30], fill=C(iris))
        d.ellipse([22, 21, 25, 26], fill=C('ink'))
    return im


# ------------------------------------------------------------------ the engram
def mask(state='idle', frame=0):
    """The Daimyo's ghost: a floating kabuto and menpo with trailing static, 48x48."""
    im = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(frame + (9 if state == 'pin' else 0))
    for k in range(10):
        x = 10 + k * 3 + rng.randint(-1, 1)
        ln = rng.randint(6, 14)
        d.line([x, 32, x + rng.randint(-3, 3), 32 + ln], fill=C('purple2', 160))
    d.pieslice([8, 4, 40, 34], 180, 360, fill=C('purple1', 220), outline=C('purple3'))
    d.arc([4, -10, 44, 12], 200, 340, fill=C('gold'), width=2)
    d.rectangle([14, 18, 34, 32], fill=C('red1', 230), outline=C('purple3'))
    eyes = C('slate3') if state == 'pin' else C(['red3', 'white'][frame % 2])
    d.line([17, 22, 22, 22], fill=eyes, width=2)
    d.line([26, 22, 31, 22], fill=eyes, width=2)
    d.line([17, 28, 31, 28], fill=C('white', 200))
    if state == 'pin':
        for (x0, y0, x1, y1) in ((2, 10, 14, 22), (46, 12, 34, 24), (6, 40, 16, 30)):
            d.line([x0, y0, x1, y1], fill=C('mag3'), width=2)
    return im


def orb(frame):
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 7, 7], fill=C('purple2'))
    d.ellipse([2, 2, 5, 5], fill=C('mag4' if frame % 2 else 'white'))
    return im
