# Shared helpers, pasted into the sprites that need them.

FX = '''
@proc
def cfx(t, x, y, d):
    cq_t.append(t)
    cq_x.append(x)
    cq_y.append(y)
    cq_d.append(d)


@proc
def mfx(t, x, y, d):
    mq_t.append(t)
    mq_x.append(x)
    mq_y.append(y)
    mq_d.append(d)
'''

# Clone bookkeeping for sprites whose original spawns per-room clones.
CLONES = '''
@flag
def init_clone_flag():
    is_clone = 0
    hide()


@on("clear")
def clear_clones():
    if is_clone == 1:
        delete_clone()
'''

ENEMY = '''
@proc
def add_ent(t, x, y, w, h, hpv, imax, foe):
    ent_type.append(t)
    ent_x.append(x)
    ent_y.append(y)
    ent_w.append(w)
    ent_h.append(h)
    ent_hp.append(hpv)
    ent_int.append(0)
    ent_imax.append(imax)
    ent_alive.append(1)
    ent_stag.append(0)
    ent_dmg.append(0)
    ent_idmg.append(0)
    ent_kb.append(0)
    ent_hk.append("")
    ent_foe.append(foe)
    ent_obj.append(oi)
    ent_brk.append(0)
    ent_sev.append(0)
    slot = len(ent_type)


@proc
def hit_player(dmg, breach, sx):
    res = "hit"
    if pinv > 0 or pdash == 1 or pst == "dead" or pst == "cut" or pst == "reboot":
        res = "miss"
        return
    if breach == 0:
        if pparry > 0:
            res = "deflect"
        elif pblock == 1 and (sx - px) * pface >= 0:
            res = "block"
    if res == "hit":
        pinv = 3
    hq_t.append(res)
    hq_d.append(dmg)
    hq_x.append(sx)


@proc
def p_overlap(x1, x2, y1, y2):
    ov = 0
    if px + 7 > x1 and px - 7 < x2 and py + 34 > y1 and py < y2:
        ov = 1


@proc
def cell(x, y):
    ccx = floor((x + 240) / 16)
    ccy = floor((180 - y) / 16)
    if ccx < 0 or ccx > 29 or ccy < 0 or ccy > 22:
        cc = "."
    else:
        cc = grid[ccy * 30 + ccx + 1]


@proc
def count_foes():
    foes = 0
    for fi in range(1, len(ent_type) + 1):
        if ent_alive[fi] == 1 and ent_foe[fi] == 1:
            foes += 1
'''


def spawner(obj_type, body):
    """Original-only loop over the room's objects of one type."""
    return '''
@on("spawn")
def on_spawn():
    if is_clone == 0:
        spawn_all()


@proc
def spawn_all():
    o1 = O_FIRST[room]
    for oi in range(o1, o1 + O_NUM[room]):
        if O_TYPE[oi] == "%s":
%s
''' % (obj_type, '\n'.join('            ' + line for line in body.strip('\n').split('\n')))
