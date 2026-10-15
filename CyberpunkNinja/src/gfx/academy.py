"""
Chapter 7 (The Academy) art: the Tenshu tileset re-toned into red lacquer, the
training-hall backdrops, the practice dummy and the trainees' palette swap.
The training holograms are hollow_floor.phase_block(..., holo=True).


All functions return 1x art-pixel images unless noted.
"""
import random

from PIL import Image, ImageDraw

import assets
from gfx.hollow_floor import tone
from gfx.util import C, gradient


ACADEMY_RAMP = ['ink', 'night1', 'brown', 'red1', 'red2', 'orange', 'yellow']


# ------------------------------------------------------------------ tiles and backdrops
SHELL_MAP = {'cyan1': 'red1', 'cyan2': 'red2', 'cyan3': 'red3', 'cyan4': 'orange'}


def academy_atlas():
    atlas = Image.open(assets.pack_path('tilesets', 'tenshu_atlas_8x8.png')).convert('RGBA')
    return tone(atlas, ['night1', 'brown', 'red1', 'red2', 'orange', 'yellow'], keep=('gold',), stretch=True)


def academy_sky():
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 80, 'ink', 'night1')
    gradient(im, 80, 180, 'night1', 'red1')
    d = ImageDraw.Draw(im)
    for x in (20, 80, 140, 200):
        d.line([x, 0, x, 10], fill=C('brown'))
        d.ellipse([x - 5, 10, x + 5, 22], fill=C('red2'), outline=C('red1'))
        d.line([x - 4, 16, x + 4, 16], fill=C('orange'))
    return im


def academy_far():
    """A shoji screen wall with trainee silhouettes behind the paper."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 70, 239, 160], fill=C('brown'))
    for x in range(0, 240, 30):
        d.rectangle([x + 2, 74, x + 27, 156], fill=C('orange', 60))
        for gx in range(x + 2, x + 28, 8):
            d.line([gx, 74, gx, 156], fill=C('brown'))
        for gy in range(74, 157, 12):
            d.line([x + 2, gy, x + 27, gy], fill=C('brown'))
    rng = random.Random(14)
    for x in range(15, 240, 60):
        h = rng.randint(30, 38)
        top = 150 - h
        d.ellipse([x - 3, top, x + 3, top + 6], fill=C('red1', 200))
        d.rectangle([x - 3, top + 6, x + 3, 150], fill=C('red1', 200))
        d.line([x + 3, top + 10, x + 14, top + 2], fill=C('red1', 200))
    d.rectangle([0, 160, 239, 179], fill=C('night1'))
    return im


def academy_mid():
    """Lacquered pillars with hanging banners, every 120 px."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (30, 150):
        d.rectangle([x, 0, x + 8, 179], fill=C('red1'))
        d.line([x + 1, 0, x + 1, 179], fill=C('red2'))
        d.rectangle([x - 2, 40, x + 10, 44], fill=C('gold'))
        bx = x + 30
        d.rectangle([bx, 6, bx + 16, 70], fill=C('night2'), outline=C('gold'))
        d.line([bx + 8, 14, bx + 8, 40], fill=C('white'), width=2)
        d.line([bx + 3, 24, bx + 13, 24], fill=C('white'))
        d.line([bx + 4, 48, bx + 12, 58], fill=C('red3'), width=2)
        d.line([bx + 12, 48, bx + 4, 58], fill=C('red3'), width=2)
        d.polygon([(bx, 70), (bx + 8, 64), (bx + 16, 70)], fill=C('ink'))
    return im


def dummy():
    """Training dummy, 14x26."""
    im = Image.new('RGBA', (14, 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 8, 7, 25], fill=C('brown'))
    d.rectangle([1, 10, 12, 12], fill=C('brown'))
    d.ellipse([3, 0, 10, 8], fill=C('gold'), outline=C('brown'))
    d.rectangle([4, 13, 9, 20], fill=C('gold'), outline=C('brown'))
    d.line([4, 16, 9, 16], fill=C('red2'))
    d.rectangle([3, 24, 10, 25], fill=C('slate2'))
    return im


# ------------------------------------------------------------------ hollowed trainees (Mukuro's rig)
# Kuro's former students in their training gi, eyes blank white.
TRAINEE_MAP = {'night1': 'slate1', 'night2': 'slate2', 'night3': 'slate3', 'indigo': 'steel',
               'red2': 'white', 'red3': 'red2', 'slate2': 'steel', 'slate3': 'white'}
