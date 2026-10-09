"""The Daimyo's mech (phase 1), animated from the user's parts by a small 2D rig.

art/src/daimyo_mech holds the parts (helmet, upper arm, forearm, fist, sword,
torso with the waist plates and scabbard, upper leg, lower leg) cut from the
user's sheet, and the assembled pose they come from. Each pose places the hips,
the feet and the sword's grip; the knees and elbows are solved to reach them
(two-bone IK). The far arm and leg are the same parts, darker, behind the body.
Parts are rotated the RotSprite way: upscaled 8x with Scale2x, turned, then
sampled back at 1x, so the pixel art stays crisp.
"""
import math
import os

from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'src', 'daimyo_mech')
UP = 8

# where the parts sit in the user's assembled pose (top-left corners)
ASSEMBLED = {'torso': (0, 27), 'helmet': (10, 12), 'uarm': (9, 23), 'forearm': (11, 38),
             'sword': (25, 0), 'uleg': (12, 42), 'lleg': (10, 57)}
GROUND = 83          # the assembled pose's feet, in its own pixels

# joints, in each part's own pixels
PIV = {
    'helmet': (8, 14),       # neck
    'uarm': (6, 1),          # shoulder
    'forearm': (3, 3),       # elbow
    'fist': (3, 3),
    'uleg': (6, 1),          # hip
    'lleg': (7, 3),          # knee
    'sword': (4, 47),        # where the front hand grips
}


def _a2p(part, pt):
    """An assembled-pose point in a part's own pixels."""
    ox, oy = ASSEMBLED[part]
    return (pt[0] - ox, pt[1] - oy)


def _p2a(part, pt):
    ox, oy = ASSEMBLED[part]
    return (pt[0] + ox, pt[1] + oy)


# the torso's anchor is the hip; its children hang off points worked out from the assembly
HIP_A = _p2a('uleg', PIV['uleg'])
TORSO_PIV = _a2p('torso', HIP_A)
NECK_T = _a2p('torso', _p2a('helmet', PIV['helmet']))
SHOULDER_T = _a2p('torso', _p2a('uarm', PIV['uarm']))
ELBOW_U = _a2p('uarm', _p2a('forearm', PIV['forearm']))
HAND_F = (18, 9)                                      # palm, in the forearm
HAND_FIST = (17, 10)
KNEE_U = _a2p('uleg', _p2a('lleg', PIV['lleg']))
FOOT_L = (8, 26)                                      # sole, in the lower leg
GRIP2_S = (2, 52)                                     # the far hand, lower on the grip
BACK_SHOULDER = (-4, 2)                              # far shoulder and hip, relative to the near ones
BACK_HIP = (-5, 0)


JOINT, JOINT_HI, JOINT_LO = (92, 92, 116, 255), (178, 184, 201, 255), (33, 35, 61, 255)


def _load(name):
    im = Image.open(os.path.join(SRC, 'part_%s.png' % name)).convert('RGBA')
    if name == 'torso':
        # the shoulder socket (hidden under the arm in the drawing) shows when the arm
        # swings up: fill it with the armor's dark red, as a shaded plate
        px = im.load()
        BLK = (0, 0, 0, 255)
        inner = [(x, y) for y in range(1, 9) for x in range(8, 26)
                 if px[x, y] == BLK and all(px[x + dx, y + dy] == BLK for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        ys = [y for _, y in inner]
        xs = [x for x, _ in inner]
        for x, y in inner:
            c = (118, 13, 38, 255)
            if y == max(ys):
                c = (177, 29, 33, 255)
            px[x, y] = c
    return im


def scale2x(im):
    """EPX / Scale2x: doubles pixel art without blurring its edges."""
    W, H = im.size
    src = im.load()
    out = Image.new('RGBA', (W * 2, H * 2))
    dst = out.load()
    g = lambda x, y: src[min(max(x, 0), W - 1), min(max(y, 0), H - 1)]
    for y in range(H):
        for x in range(W):
            P = src[x, y]
            A, B, C, D = g(x, y - 1), g(x + 1, y), g(x - 1, y), g(x, y + 1)
            e0 = e1 = e2 = e3 = P
            if C == A and C != D and A != B:
                e0 = A
            if A == B and A != C and B != D:
                e1 = B
            if D == C and D != B and C != A:
                e2 = C
            if B == D and B != A and D != C:
                e3 = D
            dst[2 * x, 2 * y], dst[2 * x + 1, 2 * y], dst[2 * x, 2 * y + 1], dst[2 * x + 1, 2 * y + 1] = e0, e1, e2, e3
    return out


_UP = {}


def _up(name):
    if name not in _UP:
        im = _load(name)
        for _ in range(3):
            im = scale2x(im)
        _UP[name] = im
    return _UP[name]


def _dark(c, k=0.62):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k), c[3])


def draw(canvas, name, piv, at, ang, dark=False):
    """Draw a part with its pivot `piv` on canvas point `at`, turned by `ang` degrees
    (clockwise on screen)."""
    up = _up(name)
    upx = up.load()
    W, H = up.size
    cx = canvas.load()
    th = math.radians(ang)
    c, s = math.cos(th), math.sin(th)
    # the part's corners on the canvas, to bound the work
    pw, ph = W / UP, H / UP
    pts = []
    for lx, ly in ((0, 0), (pw, 0), (0, ph), (pw, ph)):
        dx, dy = lx - piv[0], ly - piv[1]
        pts.append((at[0] + dx * c - dy * s, at[1] + dx * s + dy * c))
    x0 = max(0, int(min(p[0] for p in pts)) - 1)
    x1 = min(canvas.width, int(max(p[0] for p in pts)) + 2)
    y0 = max(0, int(min(p[1] for p in pts)) - 1)
    y1 = min(canvas.height, int(max(p[1] for p in pts)) + 2)
    for Y in range(y0, y1):
        for X in range(x0, x1):
            dx, dy = X + 0.5 - at[0], Y + 0.5 - at[1]
            lx = dx * c + dy * s + piv[0]
            ly = -dx * s + dy * c + piv[1]
            ux, uy = int(lx * UP), int(ly * UP)
            if 0 <= ux < W and 0 <= uy < H:
                p = upx[ux, uy]
                if p[3]:
                    cx[X, Y] = _dark(p) if dark else p


def _ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _rot(v, ang):
    th = math.radians(ang)
    return (v[0] * math.cos(th) - v[1] * math.sin(th), v[0] * math.sin(th) + v[1] * math.cos(th))


def ik(root, target, u_vec, l_vec, bend):
    """Two-bone IK. u_vec / l_vec: each bone's rest vector (pivot to its end). Returns
    the turn (degrees) for the upper and lower part, and the middle joint."""
    L1, L2 = math.hypot(*u_vec), math.hypot(*l_vec)
    d = _sub(target, root)
    dist = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, math.hypot(*d)))
    base = math.atan2(d[1], d[0])
    a = math.acos(max(-1, min(1, (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist))))
    up_abs = base + bend * a
    joint = (root[0] + L1 * math.cos(up_abs), root[1] + L1 * math.sin(up_abs))
    lo_abs = math.atan2(target[1] - joint[1], target[0] - joint[0])
    return math.degrees(up_abs) - _ang(u_vec), math.degrees(lo_abs) - _ang(l_vec), joint


REST = None


def rest_pose():
    """The assembled pose's own numbers, measured from the hip (feet at y=0 under it)."""
    hip = HIP_A
    foot = _p2a('lleg', FOOT_L)
    grip = _p2a('sword', PIV['sword'])
    rel = lambda p: (p[0] - hip[0], p[1] - GROUND)
    return {'hip': (0, hip[1] - GROUND), 'lean': 0, 'head': 0,
            'foot': rel(foot), 'bfoot': (rel(foot)[0] - 7, 0),
            'grip': rel(grip), 'sword': 0, 'fist': False, 'z': 0}


def render(pose, W=150, H=150, gx=None, gy=None):
    """One frame: {hip, lean, head, foot, bfoot, grip, sword, ...} in pixels from the
    ground point under the rest hip (y up is negative). Returns the frame and its anchor
    (the ground point)."""
    P = dict(rest_pose())
    P.update(pose)
    gx = W // 2 if gx is None else gx
    gy = H - 6 if gy is None else gy
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    z = P.get('z', 0)
    w = lambda p: (gx + p[0], gy + p[1] - z)
    hip = w(P['hip'])
    lean = P['lean']
    tp = lambda v: (hip[0] + _rot(_sub(v, TORSO_PIV), lean)[0], hip[1] + _rot(_sub(v, TORSO_PIV), lean)[1])
    neck, shoulder = tp(NECK_T), tp(SHOULDER_T)
    b_sh = (shoulder[0] + BACK_SHOULDER[0], shoulder[1] + BACK_SHOULDER[1])
    b_hip = (hip[0] + BACK_HIP[0], hip[1] + BACK_HIP[1])
    # sword: the near hand holds its grip point; the far hand a little lower
    s_ang = P['sword']
    grip = w(P['grip'])
    grip2 = (grip[0] + _rot(_sub(GRIP2_S, PIV['sword']), s_ang)[0], grip[1] + _rot(_sub(GRIP2_S, PIV['sword']), s_ang)[1])
    u_arm, l_arm = _sub(ELBOW_U, PIV['uarm']), _sub(HAND_F, PIV['forearm'])
    u_leg, l_leg = _sub(KNEE_U, PIV['uleg']), _sub(FOOT_L, PIV['lleg'])
    fore = 'fist' if P.get('fist') else 'forearm'
    # the far side first, darker
    bu, bl, bj = ik(b_hip, w(P['bfoot']), u_leg, l_leg, -1)
    draw(cv, 'uleg', PIV['uleg'], b_hip, bu, True)
    draw(cv, 'lleg', PIV['lleg'], bj, bl, True)
    au, al, aj = ik(b_sh, grip2, u_arm, l_arm, 1)
    draw(cv, 'uarm', PIV['uarm'], b_sh, au, True)
    draw(cv, fore, PIV['forearm'], aj, al, True)
    fu, fl, fj = ik(hip, w(P['foot']), u_leg, l_leg, -1)
    draw(cv, 'uleg', PIV['uleg'], hip, fu)
    draw(cv, 'lleg', PIV['lleg'], fj, fl)
    draw(cv, 'torso', TORSO_PIV, hip, lean)
    eu, el, ej = ik(shoulder, grip, u_arm, l_arm, 1)
    draw(cv, 'uarm', PIV['uarm'], shoulder, eu)
    # the head in front of the upper arm, so a raised arm never hides it
    draw(cv, 'helmet', PIV['helmet'], neck, lean + P['head'])
    draw(cv, 'sword', PIV['sword'], grip, s_ang)
    draw(cv, fore, PIV['forearm'], ej, el)
    return cv, (gx, gy)


# ---------------------------------------------------------------- animations (12 fps)
def _lerp(a, b, t):
    if isinstance(a, tuple):
        return tuple(_lerp(x, y, t) for x, y in zip(a, b))
    if isinstance(a, bool):
        return a if t < 0.5 else b
    return a + (b - a) * t


def _tween(a, b, t):
    return {k: _lerp(a.get(k, REST_P[k]), b.get(k, REST_P[k]), t) for k in set(REST_P) | set(a) | set(b)}


REST_P = rest_pose()
STAND = {}
OVERHEAD = {'hip': (-1, -41), 'lean': -4, 'head': -2, 'grip': (12, -82), 'sword': -70, 'foot': (4, 0), 'bfoot': (-10, 0)}
CUT_END = {'hip': (3, -36), 'lean': 14, 'head': 6, 'grip': (24, -26), 'sword': 105, 'foot': (10, 0), 'bfoot': (-12, 0)}
CUT_MID = {'hip': (2, -38), 'lean': 8, 'head': 3, 'grip': (18, -50), 'sword': 30, 'foot': (8, 0), 'bfoot': (-11, 0)}
LOW = {'hip': (0, -34), 'lean': 10, 'head': 4, 'grip': (16, -28), 'sword': 70, 'foot': (9, 0), 'bfoot': (-12, 0)}
CROUCH = {'hip': (0, -32), 'lean': 6, 'head': 2, 'grip': (10, -30), 'sword': -20, 'foot': (8, 0), 'bfoot': (-10, 0)}
THRUST_READY = {'hip': (-3, -37), 'lean': -10, 'head': -4, 'grip': (-8, -36), 'sword': 72, 'foot': (8, 0), 'bfoot': (-12, 0)}
DASH = {'hip': (2, -36), 'lean': 22, 'head': 8, 'grip': (24, -36), 'sword': 72, 'foot': (14, 0), 'bfoot': (-14, -4)}
HURT = {'hip': (-3, -39), 'lean': -14, 'head': -10, 'grip': (6, -30), 'sword': 40, 'foot': (6, 0), 'bfoot': (-9, 0)}
KNEEL = {'hip': (-2, -24), 'lean': 10, 'head': 20, 'grip': (16, -30), 'sword': 100, 'foot': (12, 0), 'bfoot': (-20, 0)}


def anim_frames():
    """{anim: [pose, ...]}, 12 frames a second."""
    A = {}
    A['idle'] = [{'hip': (0, -40 + d), 'grip': (11, -36 + d)} for d in (0, 1, 1, 0)]
    walk = []
    for i in range(8):
        ph = i / 8 * 2 * math.pi
        s = math.sin(ph)
        lift = lambda v: min(0, v)
        walk.append({'hip': (0, -40 + abs(math.sin(ph)) * 1.5), 'lean': 4, 'grip': (12, -37 + abs(s) * 1.5),
                     'foot': (10 * s, lift(-5 * math.cos(ph))), 'bfoot': (-10 * s - 4, lift(5 * math.cos(ph)))})
    A['walk'] = walk
    A['windup'] = [_tween(STAND, OVERHEAD, t) for t in (0.4, 0.8, 1.0)]
    A['slash'] = [_tween(OVERHEAD, CUT_MID, 0.6), CUT_MID, _tween(CUT_MID, CUT_END, 0.6), CUT_END]
    A['low'] = [LOW]
    A['stomp'] = [CROUCH, dict(CROUCH, hip=(0, -30)), dict(OVERHEAD, z=12, foot=(6, -10), bfoot=(-8, -6)),
                  dict(OVERHEAD, z=26, foot=(6, -14), bfoot=(-8, -10)), dict(OVERHEAD, z=18, foot=(6, -8), bfoot=(-8, -6)),
                  dict(LOW, sword=110, grip=(18, -22))]
    A['charge'] = [_tween(STAND, THRUST_READY, 0.6), THRUST_READY]
    A['dash'] = [DASH, dict(DASH, foot=(4, -6), bfoot=(-16, 0))]
    A['hurt'] = [HURT]
    A['kneel'] = [KNEEL]
    return A


def frames():
    """{costume name: (1x image, anchor)}"""
    out = {}
    for anim, poses in anim_frames().items():
        for i, p in enumerate(poses):
            im, anc = render(p, W=160, H=170)
            out['mech_%s_%d' % (anim, i)] = (im, anc)
    return out
