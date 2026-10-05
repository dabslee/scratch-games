# Interactive objects, NPCs and projectiles (Scratch DSL).
from common import spawner

PROJECTILES = '''
@on("t_world")
def tick():
    if is_clone == 1:
        pr_update()
    else:
        pr_spawn()


@on("t_draw")
def draw():
    if is_clone == 1:
        pr_draw()


@proc
def pr_spawn():
    for qi in range(1, len(pq_t) + 1):
        kind = pq_t[qi]
        x = pq_x[qi]
        y = pq_y[qi]
        vx = pq_vx[qi]
        vy = pq_vy[qi]
        t = 0
        if kind == "bullet":
            owner = "e"
        elif kind == "wave":
            owner = "w"
        else:
            owner = "p"
        is_clone = 1
        clone()
        is_clone = 0
    pq_t.clear()
    pq_x.clear()
    pq_y.clear()
    pq_vx.clear()
    pq_vy.clear()


@proc
def pr_update():
    t += 1
    x += vx
    y += vy
    if t > 100 or x < -260 or x > 260 or y < -200 or y > 200:
        delete_clone()
    if kind == "wave":
        cell(x + vx * 2, y + 8)
        if cc == "#" or cc == "D":
            cfx("hit", x, y + 10, 0)
            delete_clone()
        if px + 7 > x - 10 and px - 7 < x + 10 and py < y + 22 and py + 34 > y:
            if vx > 0:
                hit_player(3, 1, x - 30)
            else:
                hit_player(3, 1, x + 30)
            if res == "hit":
                delete_clone()
        return
    cell(x, y)
    if cc == "#" or cc == "B" or cc == "D":
        cfx("hit", x - vx, y - vy, 0)
        delete_clone()
    if owner == "e":
        if px + 7 > x - 4 and px - 7 < x + 4 and py + 36 > y - 4 and py < y + 4:
            hit_player(1, 0, x - vx * 3)
            if res == "deflect":
                vx = 0 - vx * 1.6
                vy = 0 - vy * 1.6
                owner = "p"
                t = 0
            elif res != "miss":
                delete_clone()
    else:
        for ei in range(1, len(ent_type) + 1):
            if ent_alive[ei] == 1 and ent_x[ei] + ent_w[ei] + 4 > x and ent_x[ei] - ent_w[ei] - 4 < x:
                if ent_y[ei] + ent_h[ei] + 4 > y and ent_y[ei] - 4 < y:
                    if kind == "bullet":
                        ent_dmg[ei] = ent_dmg[ei] + 2
                    else:
                        ent_dmg[ei] = ent_dmg[ei] + 1
                    ent_hk[ei] = "projectile"
                    if vx > 0:
                        ent_kb[ei] = 2
                    else:
                        ent_kb[ei] = -2
                    cfx("hit_enemy", x, y, 0)
                    sfxq.append("hit")
                    delete_clone()


@proc
def pr_draw():
    # enemy shots flash white in the last 0.1 s (3 frames) before reaching Hotaru
    tell = 0
    if owner != "p" and vx != 0 and (px - x) * vx > 0:
        eta = (abs(px - x) - 11) / abs(vx)
        if eta > 0 and eta <= 3 and abs((py + 18) - y) < 40:
            tell = 1
    if tell == 1:
        effect("brightness", 100)
    else:
        effect("brightness", 0)
    if kind == "wave":
        costume(join("wave_", floor(t / 3) % 2))
    else:
        costume(join("bullet_", floor(t / 4) % 2))
    goto(x + shx, y + shy)
    if vx < 0:
        point(-90)
    else:
        point(90)
    show()
'''


SHRINE = spawner('shrine', '''
x = O_X[oi]
y = O_Y[oi]
fr = 0
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if abs(px - x) < 28 and abs(py - y) < 24 and p_ground == 1 and pst == "move":
            prompt_on = 1
            prompt_x = x
            prompt_y = y + 74
            if pE == 1:
                sync()


@proc
def sync():
    cp_room = room
    cp_x = x
    cp_y = y
    hp = 10
    heat = 0
    if has_gourd == 1:
        gourd = gmax
    dash_ch = 2
    dead_objs.clear()
    has_save = 1
    cfx("sync", x, y + 30, 0)
    banner = "synced"
    banner_t = 50
    sfxq.append("sync")


@on("t_draw")
def draw():
    if is_clone == 1:
        fr += 0.25
        if cp_room == room and abs(cp_x - x) < 2:
            costume(join("active_", floor(fr) % 4))
        else:
            costume(join("idle_", floor(fr * 0.6) % 4))
        goto(x + shx, y + shy)
        show()
'''


TETSU = spawner('tetsu', '''
x = O_X[oi]
y = O_Y[oi]
fr = 0
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if abs(px - x) < 44 and abs(py - y) < 24 and p_ground == 1 and pst == "move":
            prompt_on = 1
            prompt_x = x
            prompt_y = y + 84
            if pE == 1:
                if has_gourd == 0:
                    dlg_req = "tetsu"
                else:
                    dlg_req = "tetsu2"
                mode = "dlg"


@on("t_draw")
def draw():
    if is_clone == 1:
        if dlg_spk == "tetsu":
            fr += 0.2
            costume(join("talk_", floor(fr) % 4))
        else:
            fr += 0.17
            costume(join("idle_", floor(fr) % 4))
        goto(x + shx, y + shy)
        point(-90)
        show()
'''


DAICAM = spawner('daicam', '''
if daicam_done == 0:
    x = O_X[oi]
    y = O_Y[oi]
    fr = 0
    st = "panic"
    t = 0
    cam_x = x
    cam_y = y + 70
    is_clone = 1
    clone()
    is_clone = 0
    clone("CamDrone")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        dc_update()


@proc
def dc_update():
    t += 1
    if st == "panic":
        fr += 0.34
        count_foes()
        if foes == 0:
            st = "wait"
            t = 0
    elif st == "wait":
        fr += 0.2
        if t > 25:
            st = "talk"
            broadcast("ev_daicam_end")
    elif st == "talk":
        fr += 0.27
        if daicam_done == 1:
            st = "run"
            t = 0
            sfxq.append("cam_beep")
    elif st == "run":
        fr += 0.34
        x += 5
        if x > 270:
            cam_x = 999
            delete_clone()
    cam_x = x - 26
    cam_y = y + 72 + sin(frame * 8) * 4


@on("t_draw")
def draw():
    if is_clone == 1:
        if st == "talk" or st == "wait":
            if dlg_spk == "daicam" or st == "wait":
                costume(join("wave_", floor(fr) % 4))
            else:
                costume(join("idle_", floor(fr) % 4))
        else:
            costume(join("panic_", floor(fr) % 4))
        goto(x + shx, y + shy)
        if st == "run":
            point(90)
        else:
            point(-90)
        show()
'''


CAMDRONE = '''
@clone
def cam_start():
    is_clone = 1


@on("t_draw")
def draw():
    if is_clone == 1:
        if cam_x > 900:
            delete_clone()
        costume(join("hover_", floor(frame / 3) % 4))
        goto(cam_x + shx, cam_y + shy)
        show()
'''


LASER = spawner('laser', '''
x = O_X[oi]
y = O_Y[oi]
lc = floor((x + 240) / 16)
lr = floor((180 - (y + 1)) / 16)
for k in range(6):
    grid[(lr - k) * 30 + lc + 1] = "L"
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        costume(join("on_", floor(frame / 3) % 4))
        goto(x + shx, y + shy)
        show()
        if abs(px - x) < 70 and frame % 20 == 0 and ingame == 1:
            sfxq.append("laser_hum")
'''


CRATE = spawner('crate', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    drop = O_A[oi]
    myobj = oi
    add_ent("crate", x, y, 13, 26, 2, 0, 0)
    ehp = 2
    st = "intact"
    fr = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if st == "break":
            fr += 0.4
        elif ent_dmg[slot] > 0:
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
            ehp -= 1
            if ehp <= 0:
                st = "break"
                fr = 0
                ent_alive[slot] = 0
                dead_objs.append(myobj)
                sfxq.append("crate_break")
                if drop == 1:
                    pk_x.append(x)
                    pk_y.append(y + 14)
            else:
                st = "cracked"
                sfxq.append("crate_hit")


@on("t_draw")
def draw():
    if is_clone == 1:
        if st == "break":
            if fr >= 3:
                delete_clone()
            costume(join("break_", floor(fr)))
        else:
            costume(join(st, "_0"))
        goto(x + shx, y + shy)
        show()
'''


PICKUP = '''
@on("t_world")
def tick():
    if is_clone == 1:
        t += 1
        if abs(px - x) < 16 and py < y + 10 and py + 36 > y - 10:
            gourd = min(gmax, gourd + 1)
            has_gourd = 1
            sfxq.append("pickup")
            cfx("heal", x, y - 12, 0)
            delete_clone()
    else:
        for qi in range(1, len(pk_x) + 1):
            x = pk_x[qi]
            y = pk_y[qi]
            t = 0
            is_clone = 1
            clone()
            is_clone = 0
        pk_x.clear()
        pk_y.clear()


@on("t_draw")
def draw():
    if is_clone == 1:
        costume("gourd_pickup")
        goto(x + shx, y + shy + sin(t * 8) * 3)
        if t % 30 < 15:
            effect("brightness", 25)
        else:
            effect("brightness", 0)
        show()
'''


PUDDLE = spawner('puddle', '''
x = O_X[oi]
y = O_Y[oi]
pz_x.append(x)
pz_y.append(y)
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if p_ground == 1 and abs(px - x) < 22 and abs(py - y) < 6 and pinv == 0 and pdash == 0:
            hq_t.append("hazard")
            hq_d.append(2)
            hq_x.append(x)


@on("t_draw")
def draw():
    if is_clone == 1:
        costume(join("spark_", floor(frame / 2.5) % 4))
        goto(x + shx, y + shy)
        show()
'''


LIFT = spawner('lift', '''
x = O_X[oi]
y = O_Y[oi]
lmode = O_A[oi]
st = "rest"
t = 0
if lmode == "arrive" and enter_dir == "B" and lift_ride == 1:
    y = C_LIFT_LOW
    st = "in"
mp_on = 1
mp_x = x
mp_y = y
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        t += 1
        if st == "rest" and lmode == "up":
            if p_onplat == 1:
                ride_t += 1
                if ride_t > 12:
                    st = "up"
                    sfxq.append("lift")
            else:
                ride_t = 0
        elif st == "up":
            y += 2.6
            if t % 25 == 0:
                sfxq.append("lift")
        elif st == "in":
            y += 2.6
            if y >= C_LIFT_TOP:
                y = C_LIFT_TOP
                st = "done"
                sfxq.append("land")
        mp_on = 1
        mp_x = x
        mp_y = y


@on("t_draw")
def draw():
    if is_clone == 1:
        costume(join("hover_", floor(frame / 3) % 2))
        goto(x + shx, y + shy)
        show()
'''


DOOR = spawner('door', '''
x = O_X[oi]
y = O_Y[oi]
dmode = O_A[oi]
dc = floor((x + 240) / 16)
dr = floor((180 - (y + 1)) / 16)
fr = 0
if dmode == "lock":
    st = "closed"
    if dc >= 15 and enter_dir == "R":
        st = "open"
    if dc < 15 and enter_dir == "L":
        st = "open"
else:
    st = "open"
if boss_dead == 1 and dmode == "ambush":
    st = "open"
if st == "closed":
    set_cells("D")
fr = 4
is_clone = 1
clone()
is_clone = 0
''') + '''
@proc
def set_cells(v):
    for k in range(5):
        grid[(dr - k) * 30 + dc + 1] = v


@on("t_world")
def tick():
    if is_clone == 1:
        count_foes()
        if st == "closed":
            if foes == 0:
                st = "opening"
                fr = 0
                set_cells(".")
                sfxq.append("door_open")
        elif st == "open":
            if dmode == "ambush" and ambush_on == 1 and foes > 0:
                if abs(px - x) > 30:
                    st = "closed"
                    set_cells("D")
                    sfxq.append("door_close")
                    shake = 4
                    shake_amp = 2
        elif st == "opening":
            fr += 0.47
            if fr >= 4:
                fr = 4
                st = "open"


@on("t_draw")
def draw():
    if is_clone == 1:
        if st == "closed":
            costume("closed_0")
        else:
            costume(join("open_", floor(fr)))
        goto(x + shx, y + shy)
        show()
'''


SHARD = spawner('shard', '''
if not (oi in got_shards):
    x = O_X[oi]
    y = O_Y[oi]
    sid = O_A[oi]
    myobj = oi
    t = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        count_foes()
        if foes == 0:
            t += 1
            if t == 1:
                sfxq.append("shard_appear")
            if abs(px - x) < 18 and py < y + 14 and py + 36 > y - 14:
                got_shards.append(myobj)
                shards += 1
                shard_id = sid
                cfx("sync", x, y, 0)
                broadcast("ev_shard")
                delete_clone()


@on("t_draw")
def draw():
    if is_clone == 1:
        if t > 0:
            costume(join("spin_", floor(frame / 3) % 6))
            goto(x + shx, y + shy + sin(frame * 6) * 4)
            effect("ghost", max(0, 100 - t * 8))
            show()
        else:
            hide()
'''


BREAKABLE = spawner('block', '''
bi = O_B[oi] * 30 + O_A[oi] + 1
bkey = join(room, "_", bi)
if bkey in broken:
    grid[bi] = "."
else:
    x = O_X[oi]
    y = O_Y[oi]
    hits = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if bi in brk_hits:
            hits += 1
            if hits >= 2:
                grid[bi] = "."
                broken.append(bkey)
                sfxq.append("block_break")
                cfx("hit_enemy", x, y, 0)
                mfx("land_dust", x, y - 8, 1)
                delete_clone()
            else:
                sfxq.append("crate_hit")


@on("t_draw")
def draw():
    if is_clone == 1:
        if hits == 0:
            costume("breakable")
        else:
            costume("breakable_cracked")
        goto(x + shx, y + shy)
        show()
    else:
        brk_hits.clear()
'''


PROPS = spawner('sign', '''
x = O_X[oi]
y = O_Y[oi]
kind = O_A[oi]
fl_t = rand(30, 200)
fr = 0
is_clone = 1
clone()
is_clone = 0
''').replace('if O_TYPE[oi] == "sign":', 'if O_TYPE[oi] == "sign" or O_TYPE[oi] == "lantern" or O_TYPE[oi] == "cart":').replace(
    'kind = O_A[oi]', 'kind = O_A[oi]\n            if O_TYPE[oi] != "sign":\n                kind = O_TYPE[oi]') + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        if kind == "lantern":
            costume(join("lantern_sway_", floor(frame / 7.5) % 4))
        elif kind == "cart":
            costume(join("cart_idle_", floor(frame / 5) % 4))
        else:
            fl_t -= 1
            if fl_t < 0:
                fr += 0.27
                costume(join(kind, "_flicker_", floor(fr) % 8))
                if fr >= 8:
                    fl_t = rand(60, 260)
                    fr = 0
            else:
                costume(join(kind, "_on_0"))
        goto(x + shx, y + shy)
        show()
'''
