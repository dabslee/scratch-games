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
        if kind == "bullet" or kind == "card" or kind == "bolt" or kind == "shell":
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
    if kind == "shell":
        vy -= 0.35
    x += vx
    y += vy
    if t > 100 or x < -260 or x > 260 or y < -200 or y > 260:
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
        if kind == "shell":
            cfx("explosion", x, y, 0)
            sfxq.append("explode")
            if abs(px - x) < 24 and py < y + 10 and py + 34 > y - 10:
                hit_player(2, 0, x)
        else:
            cfx("hit", x - vx, y - vy, 0)
        delete_clone()
    if owner == "e":
        if px + 7 > x - 4 and px - 7 < x + 4 and py + 36 > y - 4 and py < y + 4:
            if kind == "shell":
                hit_player(2, 0, x - vx * 3)
            else:
                hit_player(1, 0, x - vx * 3)
            if res == "deflect":
                if kind == "shell":
                    # a deflected shell flies straight back into Raijin's core
                    kind = "rshell"
                    ddx = ent_x[boss_slot] - x
                    ddy = ent_y[boss_slot] + 14 - y
                    dd = sqrt(ddx * ddx + ddy * ddy) + 0.01
                    vx = ddx / dd * 11
                    vy = ddy / dd * 11
                else:
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
                    if kind == "bullet" or kind == "rshell":
                        ent_dmg[ei] = ent_dmg[ei] + 2
                    else:
                        ent_dmg[ei] = ent_dmg[ei] + 1
                    if kind == "rshell":
                        ent_idmg[ei] = ent_idmg[ei] + 3
                    else:
                        ent_idmg[ei] = ent_idmg[ei] + 2
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
    # enemy shots flash white for the last 0.3 s (9 frames) before reaching Hotaru
    tell = 0
    if kind == "shell":
        sd = sqrt((px - x) * (px - x) + (py + 18 - y) * (py + 18 - y))
        if (sd - 14) / (sqrt(vx * vx + vy * vy) + 0.01) <= 9:
            tell = 1
    elif owner != "p" and vx != 0 and (px - x) * vx > 0:
        eta = (abs(px - x) - 11) / abs(vx)
        if eta <= 9 and abs((py + 18) - y) < 40:
            tell = 1
    if tell == 1:
        effect("brightness", 100)
    else:
        effect("brightness", 0)
    if kind == "wave":
        costume(join("wave_", floor(t / 3) % 2))
    elif kind == "card":
        costume(join("card_", floor(t / 3) % 4))
    elif kind == "shell":
        costume(join("shell_", floor(t / 3) % 2))
    elif kind == "rshell":
        costume(join("rshell_", floor(t / 3) % 2))
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
tmode = O_A[oi]
fr = 0
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1 and tmode != "mem":
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
        if tmode == "mem":
            effect("ghost", 25 + (frame % 40 < 3) * 40)
        goto(x + shx, y + shy)
        point(-90)
        show()
'''


DAICAM = spawner('daicam', '''
dmode = O_A[oi]
dc_done()
if ddone == 0:
    x = O_X[oi]
    y = O_Y[oi]
    by = y
    fy = O_B[oi]
    fr = 0
    st = "panic"
    if dmode == "cage":
        st = "caged"
    if dmode == "echo" or dmode == "trainee":
        st = "idle"
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
def dc_done():
    ddone = daicam_done
    if dmode == "cage":
        ddone = daicam3_done
    elif dmode == "float":
        ddone = daicam4_done
    elif dmode == "dine":
        ddone = daicam5_done
    elif dmode == "echo":
        ddone = daicam6_done
    elif dmode == "trainee":
        ddone = daicam7_done


@proc
def dc_update():
    t += 1
    if dmode == "float" and (st == "panic" or st == "wait"):
        if st == "panic":
            y = by + sin(frame * 6) * 6
        elif y > fy:
            y = max(fy, y - 7)
            t = 14
    if st == "idle":
        fr += 0.2
        dc_done()
        if ddone == 1:
            st = "run"
            t = 0
            sfxq.append("cam_beep")
    elif st == "caged":
        fr += 0.34
        if cage_broken == 1:
            st = "wait"
            t = 0
    elif st == "panic":
        fr += 0.34
        count_foes()
        if foes == 0:
            st = "wait"
            t = 0
    elif st == "wait":
        fr += 0.2
        if t > 25:
            st = "talk"
            if dmode == "cage":
                broadcast("ev_daicam3_free")
            elif dmode == "float":
                broadcast("ev_daicam4_end")
            elif dmode == "dine":
                broadcast("ev_daicam5_end")
            else:
                broadcast("ev_daicam_end")
    elif st == "talk":
        fr += 0.27
        dc_done()
        if ddone == 1:
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
        if dmode == "echo":
            effect("ghost", 35 + (frame % 30 < 4) * 40)
        if st == "idle":
            if dlg_spk == "daicam":
                costume(join("wave_", floor(fr) % 4))
            else:
                costume(join("idle_", floor(fr) % 4))
        elif st == "talk" or st == "wait":
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
pulse = 0
phase = 0
if O_B[oi] != "":
    pulse = 1
    phase = O_B[oi]
lon = 1
set_cells("L")
is_clone = 1
clone()
is_clone = 0
''') + '''
@proc
def set_cells(v):
    for k in range(6):
        grid[(lr - k) * 30 + lc + 1] = v


@on("t_world")
def tick():
    if is_clone == 1 and pulse == 1:
        # laser grids pulse: on for 60 frames, off for 40 (warning flicker in the last 15)
        ph = (frame + phase) % 100
        if ph < 60:
            want = 1
        else:
            want = 0
        if want != lon:
            lon = want
            if lon == 1:
                set_cells("L")
                sfxq.append("laser_hum")
                if abs(px - x) < 14 and pdash == 0 and pinv == 0 and pst != "dead":
                    hq_t.append("hit")
                    hq_d.append(1)
                    hq_x.append(x)
            else:
                set_cells(".")


@on("t_draw")
def draw():
    if is_clone == 1:
        if lon == 1:
            costume(join("on_", floor(frame / 3) % 4))
            effect("ghost", 0)
        elif (frame + phase) % 100 >= 85 and frame % 4 < 2:
            costume("on_0")
            effect("ghost", 70)
        else:
            costume("off_0")
            effect("ghost", 0)
        goto(x + shx, y + shy)
        show()
        if lon == 1 and abs(px - x) < 70 and frame % 20 == 0 and ingame == 1:
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
''').replace('if O_TYPE[oi] == "sign":', 'if O_TYPE[oi] == "sign" or O_TYPE[oi] == "lantern" or O_TYPE[oi] == "cart" or O_TYPE[oi] == "pachinko" or O_TYPE[oi] == "rack" or O_TYPE[oi] == "pod" or O_TYPE[oi] == "toro" or O_TYPE[oi] == "bonsai" or O_TYPE[oi] == "seat" or O_TYPE[oi] == "dummy":').replace(
    'kind = O_A[oi]', 'kind = O_A[oi]\n            if O_TYPE[oi] != "sign":\n                kind = O_TYPE[oi]') + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        if kind == "lantern":
            costume(join("lantern_sway_", floor(frame / 7.5) % 4))
        elif kind == "cart":
            costume(join("cart_idle_", floor(frame / 5) % 4))
        elif kind == "pachinko":
            costume(join("pachinko_", (floor(frame / 8) + floor(x / 16)) % 2))
        elif kind == "rack":
            costume(join("rack_blink_", (floor(frame / 9) + floor(x / 16)) % 4))
        elif kind == "pod":
            costume(join("pod_", (floor(frame / 18) + floor(x / 16)) % 2))
        elif kind == "toro":
            if (floor(frame / 5) + floor(x / 16)) % 9 == 0:
                costume("toro_1")
            else:
                costume("toro_0")
        elif kind == "bonsai":
            costume("bonsai")
        elif kind == "seat":
            costume("seat")
        elif kind == "dummy":
            costume("dummy")
        if chapter == 5:
            effect("ghost", 35)
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


CAGE = spawner('daicam', '''
if O_A[oi] == "cage" and daicam3_done == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("crate", x, y, 14, 40, 3, 0, 0)
    ehp = 3
    cage_broken = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1 and ehp > 0:
        if ent_dmg[slot] > 0:
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
            ehp -= 1
            sfxq.append("metal_hit")
            cfx("hit", x, y + 30, 0)
            if ehp <= 0:
                ent_alive[slot] = 0
                cage_broken = 1
                sfxq.append("block_break")
                shake = 4
                shake_amp = 3


@on("t_draw")
def draw():
    if is_clone == 1:
        if ehp <= 0:
            costume("cage_2")
        elif ehp < 3:
            costume("cage_1")
        else:
            costume("cage_0")
        goto(x + shx, y + shy)
        show()
'''


MIST = spawner('mist', '''
x = O_X[oi]
pulse = O_B[oi]
for k in range(floor((O_A[oi] + 1) / 2)):
    y = O_Y[oi] + 16 + k * 32
    seg = k
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        if pulse == 1:
            ph = frame % 110
            if ph < 70:
                effect("ghost", 25)
            elif ph < 80:
                effect("ghost", 25 + (ph - 70) * 7)
            else:
                effect("ghost", 100)
        else:
            effect("ghost", 25)
        costume(join("mist_", (floor(frame / 2) + seg * 3) % 8))
        goto(x + shx, y + shy)
        show()
'''


PHASEBLOCK = '''
@on("spawn")
def on_spawn():
    if is_clone == 0:
        for k in range(1, len(GL_I) + 1):
            gi = GL_I[k]
            x = -232 + 16 * ((gi - 1) % 30)
            y = 172 - 16 * floor((gi - 1) / 30)
            is_clone = 1
            clone()
            is_clone = 0


@on("t_draw")
def draw():
    if is_clone == 1:
        if chapter == 6:
            pre = "hb_"
        else:
            pre = "gb_"
        if grid[gi] == "#":
            if frame % 100 >= 80 and frame % 6 < 3:
                costume(join(pre, "warn"))
            else:
                costume(join(pre, "on"))
        else:
            costume(join(pre, "off"))
        goto(x + shx, y + shy)
        show()
'''
