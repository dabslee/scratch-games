# Enemy sprite sources (Scratch DSL). Each is combined with common.CLONES,
# common.ENEMY and common.FX by build.py.
from common import spawner

DRONE = spawner('drone', '''
if not (oi in dead_objs):
    hx = O_X[oi]
    hy = O_Y[oi]
    x = hx
    y = hy
    myobj = oi
    add_ent("drone", x, y - 12, 13, 22, 2, 0, 1)
    st = "hover"
    t = rand(0, 80)
    cd = 30
    ehp = 2
    fr = 0
    face = -1
    flash_t = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        d_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        d_draw()


@proc
def d_update():
    t += 1
    if st == "explode":
        fr += 0.47
        return
    if ent_dmg[slot] > 0:
        ehp -= ent_dmg[slot]
        kbv = ent_kb[slot]
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        flash_t = 4
        if ehp <= 0:
            explode()
            return
        st = "stun"
        t = 0
        if kbv == 0:
            if px < x:
                kbv = 3
            else:
                kbv = -3
        vx = kbv * 1.3
        vy = 2
        if ent_hk[slot] == "launcher":
            vy = 7
    dx = px - x
    dy = (py + 18) - y
    if st == "hover":
        x = hx + sin(t * 4) * 26
        y = hy + sin(t * 9) * 5
        fr += 0.34
        if dx > 0:
            face = 1
        else:
            face = -1
        if cd > 0:
            cd -= 1
        elif abs(dx) < 170 and abs(dy) < 210 and pst != "dead":
            st = "charge"
            t = 0
            fr = 0
            sfxq.append("drone_charge")
    elif st == "charge":
        fr += 0.4
        if fr >= 4:
            dd = sqrt(dx * dx + dy * dy)
            if dd < 1:
                dd = 1
            vx = dx / dd * 8
            vy = dy / dd * 8
            st = "dive"
            t = 0
            hitdone = 0
            sfxq.append("drone_dive")
    elif st == "dive":
        x += vx
        y += vy
        if hitdone == 0:
            p_overlap(x - 12, x + 12, y - 10, y + 10)
            if ov == 1:
                hitdone = 1
                hit_player(1, 0, x)
                if res == "deflect":
                    ehp -= 1
                    flash_t = 4
                    if ehp <= 0:
                        explode()
                        return
                    st = "stun"
                    t = 0
                    vx = 0 - vx * 0.9
                    vy = 3
                elif res == "block":
                    st = "stun"
                    t = 0
                    vx = 0 - vx * 0.6
                    vy = 2
                elif res == "hit":
                    st = "back"
                    t = 0
        cell(x + vx, y + vy)
        if cc == "#" or cc == "B" or cc == "D":
            st = "stun"
            t = 0
            vx = 0 - vx * 0.3
            vy = 1
        if t > 30:
            st = "back"
            t = 0
    elif st == "stun":
        x += vx
        y += vy
        vx = vx * 0.85
        vy = vy * 0.85
        fr = 0
        if t > 16:
            st = "back"
            t = 0
    elif st == "back":
        bx = hx - x
        by = hy - y
        dd = sqrt(bx * bx + by * by)
        fr += 0.34
        if dd < 4:
            x = hx
            y = hy
            st = "hover"
            t = 0
            cd = 40
        else:
            x += bx / dd * 3
            y += by / dd * 3
    ent_x[slot] = x
    ent_y[slot] = y - 11


@proc
def explode():
    st = "explode"
    fr = 0
    ent_alive[slot] = 0
    dead_objs.append(myobj)
    cfx("explosion", x, y, 0)
    sfxq.append("explode")
    shake = max(shake, 4)
    shake_amp = 3


@proc
def d_draw():
    if st == "explode":
        if fr >= 6:
            delete_clone()
        costume(join("explode_", floor(fr)))
    elif st == "charge":
        costume(join("charge_", min(3, floor(fr))))
    elif st == "dive":
        costume("charge_3")
    else:
        costume(join("hover_", floor(fr) % 4))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "dive" and hitdone == 0 and sqrt((px - x) * (px - x) + (py + 18 - y) * (py + 18 - y)) < 100:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    else:
        effect("brightness", 0)
    show()
'''


TURRET = spawner('turret', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    if O_A[oi] > 0:
        face = 1
    else:
        face = -1
    myobj = oi
    add_ent("turret", x + face * 18, y - 12, 18, 24, 4, 0, 1)
    st = "idle"
    t = rand(0, 30)
    ehp = 4
    fr = 0
    flash_t = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        t_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        t_draw()


@proc
def t_update():
    t += 1
    if st == "dead":
        return
    if ent_dmg[slot] > 0:
        ehp -= ent_dmg[slot]
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        flash_t = 4
        sfxq.append("metal_hit")
        if ehp <= 0:
            st = "dead"
            ent_alive[slot] = 0
            dead_objs.append(myobj)
            cfx("explosion", x + face * 16, y, 0)
            sfxq.append("explode")
            shake = max(shake, 5)
            shake_amp = 3
            return
    dx = px - x
    dy = (py + 18) - y
    if st == "idle":
        fr += 0.14
        if fr >= 4:
            fr = 0
        if t > 50 and dx * face > 30 and abs(dx) < 420 and abs(dy) < 150 and pst != "dead":
            st = "charge"
            fr = 0
            sfxq.append("turret_charge")
    elif st == "charge":
        fr += 0.34
        if fr >= 3:
            st = "fire"
            fr = 0
            fire()
    elif st == "fire":
        fr += 0.47
        if fr >= 2:
            st = "idle"
            fr = 0
            t = 0


@proc
def fire():
    mx = x + face * 34
    my = y
    ax = px - mx
    ay = (py + 20) - my
    dd = sqrt(ax * ax + ay * ay)
    if dd < 1:
        dd = 1
    pq_t.append("bullet")
    pq_x.append(mx)
    pq_y.append(my)
    pq_vx.append(ax / dd * 5)
    pq_vy.append(ay / dd * 5)
    sfxq.append("turret_fire")


@proc
def t_draw():
    if st == "dead":
        delete_clone()
    costume(join(st, "_", floor(fr)))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    else:
        effect("brightness", 0)
    show()
'''


SLOT_TURRET = spawner('slotturret', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    if O_A[oi] > 0:
        face = 1
    else:
        face = -1
    myobj = oi
    add_ent("turret", x + face * 18, y - 12, 18, 24, 4, 0, 1)
    st = "idle"
    t = rand(0, 30)
    ehp = 4
    fr = 0
    flash_t = 0
    is_clone = 1
    clone()
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        t_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        t_draw()


@proc
def t_update():
    t += 1
    if st == "dead":
        return
    if ent_dmg[slot] > 0:
        ehp -= ent_dmg[slot]
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        flash_t = 4
        sfxq.append("metal_hit")
        if ehp <= 0:
            st = "dead"
            ent_alive[slot] = 0
            dead_objs.append(myobj)
            cfx("explosion", x + face * 16, y, 0)
            sfxq.append("explode")
            shake = max(shake, 5)
            shake_amp = 3
            return
    dx = px - x
    dy = (py + 18) - y
    if st == "idle":
        fr += 0.14
        if fr >= 4:
            fr = 0
        if t > 50 and dx * face > 30 and abs(dx) < 420 and abs(dy) < 150 and pst != "dead":
            st = "charge"
            fr = 0
            sfxq.append("turret_charge")
    elif st == "charge":
        fr += 0.34
        if fr >= 3:
            st = "fire"
            fr = 0
            fire()
    elif st == "fire":
        fr += 0.47
        if fr >= 2:
            st = "idle"
            fr = 0
            t = 0


@proc
def fire():
    # slot turret: a fan of three card-blades
    mx = x + face * 34
    my = y
    ax = px - mx
    ay = (py + 20) - my
    base = atan(ay / (abs(ax) + 0.01))
    for k in range(3):
        ang = base + (k - 1) * 14
        pq_t.append("card")
        pq_x.append(mx)
        pq_y.append(my)
        pq_vx.append(face * cos(ang) * 4.5)
        pq_vy.append(sin(ang) * 4.5)
    sfxq.append("card_throw")


@proc
def t_draw():
    if st == "dead":
        delete_clone()
    costume(join(st, "_", floor(fr)))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    else:
        effect("brightness", 0)
    show()
'''


HANNYA = spawner('hannya', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    brk_ok = O_A[oi]
    myobj = oi
    skin = ""
    pkind = "card"
    if chapter == 4:
        skin = "g_"
        pkind = "bolt"
    elif chapter == 5:
        skin = "m_"
    add_ent("hannya", x, y, 10, 38, 6, 8, 1)
    find_bounds()
    st = "idle"
    t = 0
    ehp = 6
    imax = 8
    integ = 0
    int_t = 0
    z = 0
    vz = 0
    fr = 0
    face = -1
    acd = 20
    hitrow = 0
    hit_t = 0
    breach = 0
    flash_t = 0
    is_clone = 1
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("bar")
    clone("EnemyUI")
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        h_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        h_draw()


@proc
def find_bounds():
    bc = floor((x + 240) / 16)
    frow = floor((180 - (y - 4)) / 16)
    lc = bc
    scanning = 1
    while scanning == 1 and lc > 0:
        cl = grid[(frow - 1) * 30 + lc]
        fl = grid[frow * 30 + lc]
        if cl == "#" or not (fl == "#" or fl == "="):
            scanning = 0
        else:
            lc -= 1
    rc = bc
    scanning = 1
    while scanning == 1 and rc < 29:
        cl = grid[(frow - 1) * 30 + rc + 2]
        fl = grid[frow * 30 + rc + 2]
        if cl == "#" or not (fl == "#" or fl == "="):
            scanning = 0
        else:
            rc += 1
    xmin = lc * 16 - 240 + 10
    xmax = (rc + 1) * 16 - 240 - 10


@proc
def start_wind():
    st = "wind"
    t = 0
    hitdone = 0
    breach = 0
    if px > x:
        face = 1
    else:
        face = -1
    if brk_ok == 1 and rand(1, 100) <= 40:
        breach = 1
        sfxq.append("breach")
    else:
        sfxq.append("windup")


@proc
def h_die():
    st = "dead"
    t = 0
    fr = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    dead_objs.append(myobj)
    sfxq.append("thug_die")


@proc
def h_update():
    t += 1
    if st == "dead":
        fr += 0.27
        return
    if ent_sev[slot] == 1:
        h_die()
        return
    if ent_dmg[slot] > 0:
        ehp -= ent_dmg[slot]
        if st != "stagger":
            integ = min(imax, integ + ent_idmg[slot])
        int_t = 0
        hk = ent_hk[slot]
        x = min(max(x + ent_kb[slot], xmin), xmax)
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        flash_t = 3
        sfxq.append("thug_hurt")
        if ehp <= 0:
            h_die()
            return
        if st != "stagger":
            if hk == "launcher":
                st = "air"
                vz = 10
                t = 0
            elif st == "idle" or st == "walk" or st == "recover" or st == "hurt" or st == "recoil":
                hitrow += 1
                hit_t = 0
                if hitrow >= 3 and hk != "heavy":
                    hitrow = 0
                    start_wind()
                    t = 6
                else:
                    st = "hurt"
                    t = 0
            elif st == "wind" and hk == "heavy":
                hitrow = 0
                st = "hurt"
                t = 0
    if integ >= imax and st != "stagger" and st != "air":
        st = "stagger"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        sfxq.append("stagger")
    dx = px - x
    if st == "idle":
        fr += 0.17
        if abs(dx) < 260 and abs(py - y) < 100:
            st = "walk"
    elif st == "walk":
        fr += 0.27
        if dx > 0:
            face = 1
        else:
            face = -1
        if acd > 0:
            acd -= 1
        if abs(dx) > 42:
            x = min(max(x + face * 1.8, xmin), xmax)
        if abs(dx) < 54 and acd == 0 and abs(py - y) < 60 and pst != "dead":
            start_wind()
    elif st == "wind":
        if t == 1 and breach == 0:
            pass
        if t > 22:
            st = "swing"
            t = 0
            sfxq.append("swing")
    elif st == "swing":
        if hitdone == 0 and t <= 4:
            if face == 1:
                p_overlap(x, x + 48, y + 4, y + 40)
            else:
                p_overlap(x - 48, x, y + 4, y + 40)
            if ov == 1:
                hitdone = 1
                hit_player(2, breach, x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
                    st = "recoil"
                    t = 0
                    x = min(max(x - face * 6, xmin), xmax)
        if t >= 6 and st == "swing":
            st = "recover"
            t = 0
    elif st == "recover":
        if t >= 14:
            st = "walk"
            acd = rand(15, 40)
    elif st == "recoil":
        if t >= 18:
            st = "walk"
            acd = 12
    elif st == "hurt":
        if t >= 10:
            if hitrow >= 2:
                hitrow = 0
                start_wind()
            else:
                st = "walk"
                acd = max(acd, 8)
    elif st == "stagger":
        if t >= 80:
            st = "walk"
            integ = imax / 2
            ent_stag[slot] = 0
            acd = 10
    elif st == "air":
        z += vz
        vz -= 1.1
        if z <= 0:
            z = 0
            st = "hurt"
            t = 0
            hitrow = 0
    int_t += 1
    if int_t > 60 and integ > 0 and st != "stagger" and t % 15 == 0:
        integ -= 1
    hit_t += 1
    if hit_t > 30:
        hitrow = 0
    ent_x[slot] = x
    ent_y[slot] = y + z
    ent_int[slot] = integ
    if st == "wind" and breach == 1:
        ent_brk[slot] = 1
    else:
        ent_brk[slot] = 0


@proc
def h_draw():
    if st == "dead":
        if fr >= 7:
            delete_clone()
        costume(join(join(skin, "death_"), min(4, floor(fr))))
        if fr > 5:
            effect("ghost", (fr - 5) * 50)
    elif st == "idle":
        costume(join(join(skin, "idle_"), floor(fr) % 4))
    elif st == "walk":
        costume(join(join(skin, "walk_"), floor(fr) % 6))
    elif st == "wind":
        if t < 9:
            costume(join(skin, "attack_1"))
        else:
            costume(join(skin, "attack_2"))
    elif st == "swing":
        if t < 3:
            costume(join(skin, "attack_3"))
        else:
            costume(join(skin, "attack_4"))
    elif st == "recover":
        costume(join(skin, "attack_5"))
    elif st == "stagger":
        costume(join(skin, "hurt_1"))
    else:
        costume(join(join(skin, "hurt_"), min(1, floor(t / 4))))
    if st == "stagger":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + z + shy)
    else:
        goto(x + shx, y + z + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if (st == "wind" and t >= 15) or (st == "swing" and t <= 1):
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    elif st != "dead":
        effect("brightness", 0)
    show()
'''


ONI = spawner('oni', '''
if boss_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("oni", x, y, 26, 128, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    fr = 0
    face = -1
    acd = 40
    phase = 1
    flash_t = 0
    boss_hp = 20
    boss_int = 0
    is_clone = 1
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        o_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        o_draw()


@proc
def o_update():
    t += 1
    if st == "dead":
        fr += 0.2
        return
    if st == "wait":
        fr += 0.17
        if boss_on == 1:
            st = "roar"
            t = 0
            sfxq.append("oni_roar")
            shake = 24
            shake_amp = 5
        return
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        st = "stagger2"
        t = 0
        flash_t = 6
        sfxq.append("oni_hurt")
        if ehp <= 0:
            o_die()
            return
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        vuln = 0
        if st == "stagger" or st == "stagger2" or st == "recoil" or st == "broken":
            vuln = 1
        if (st == "swing" and t >= 20) or (st == "slam" and t >= 44):
            vuln = 1
        if vuln == 1 or hk == "heavy":
            ehp -= ent_dmg[slot]
            flash_t = 3
        else:
            sfxq.append("clang")
            cfx("deflect", x + face * 20, y + 70, 0 - face)
        gain = ent_idmg[slot]
        if vuln == 0 and hk != "heavy":
            gain = gain * 0.5
        if st != "broken":
            integ = min(imax, integ + gain)
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            ehp = 0
            o_die()
            return
        if hk == "heavy" and (st == "walk" or st == "swing" or st == "recover"):
            st = "stagger"
            t = 0
            sfxq.append("oni_hurt")
    if ehp <= 10 and phase == 1:
        phase = 2
        broadcast("ev_oni_phase2")
    if integ >= imax and st != "broken" and st != "stagger2":
        st = "broken"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        ent_brk[slot] = 0
        sfxq.append("stagger")
    dx = px - x
    adx = abs(dx)
    ent_brk[slot] = 0
    if st == "roar":
        fr += 0.17
        if t > 40:
            st = "walk"
    elif st == "walk":
        fr += 0.2
        if dx > 0:
            face = 1
        else:
            face = -1
        if adx > 70:
            x = min(max(x + face * 1.4, -190), 190)
        if acd > 0:
            acd -= 1
        elif pst != "dead":
            if adx < 125:
                if phase == 2 and rand(1, 100) <= 55:
                    start_slam()
                else:
                    st = "swing"
                    t = 0
                    hitdone = 0
                    sfxq.append("oni_grunt")
            elif phase == 2 and adx > 170 and rand(1, 100) <= 3:
                start_slam()
    elif st == "swing":
        if t == 15:
            sfxq.append("oni_swing")
        if t >= 15 and t <= 19 and hitdone == 0:
            if face == 1:
                p_overlap(x, x + 128, y + 20, y + 115)
            else:
                p_overlap(x - 128, x, y + 20, y + 115)
            if ov == 1:
                hitdone = 1
                hit_player(3, 0, x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
                    st = "recoil"
                    t = 0
                    sfxq.append("clang")
        if t >= 32 and st == "swing":
            st = "walk"
            acd = rand(25, 50)
    elif st == "slam":
        if t < 36:
            ent_brk[slot] = 1
        if t == 40:
            slam_hit()
        if t >= 62:
            st = "walk"
            acd = rand(30, 55)
    elif st == "stagger":
        if t >= 18:
            st = "walk"
            acd = 10
    elif st == "recoil":
        if t >= 14:
            st = "walk"
            acd = 16
    elif st == "broken":
        if t >= 110:
            st = "walk"
            integ = 8
            ent_stag[slot] = 0
            acd = 10
    elif st == "stagger2":
        if t >= 36:
            st = "walk"
            acd = 20
    int_t += 1
    if int_t > 75 and integ > 0 and st != "broken" and t % 20 == 0:
        integ -= 1
    ent_x[slot] = x
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ


@proc
def start_slam():
    st = "slam"
    t = 0
    hitdone = 0
    sfxq.append("breach")
    sfxq.append("oni_grunt")


@proc
def slam_hit():
    ix = x + face * 110
    if face == 1:
        p_overlap(x + 10, x + 150, y, y + 70)
    else:
        p_overlap(x - 150, x - 10, y, y + 70)
    if ov == 1:
        hit_player(4, 1, x)
    pq_t.append("wave")
    pq_x.append(ix)
    pq_y.append(y)
    pq_vx.append(7)
    pq_vy.append(0)
    pq_t.append("wave")
    pq_x.append(ix)
    pq_y.append(y)
    pq_vx.append(-7)
    pq_vy.append(0)
    cfx("shockwave", ix, y, 0)
    sfxq.append("oni_slam")
    shake = 16
    shake_amp = 7


@proc
def o_die():
    st = "dead"
    t = 0
    fr = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("oni_die")
    shake = 30
    shake_amp = 8
    hitstop = 12
    broadcast("ev_oni_dead")


@proc
def o_draw():
    if st == "dead":
        costume(join("death_", min(5, floor(fr))))
    elif st == "wait" or st == "roar":
        costume(join("idle_", floor(fr) % 4))
    elif st == "walk":
        costume(join("walk_", floor(fr) % 6))
    elif st == "swing":
        if t < 15:
            costume("slam_0")
        elif t < 20:
            costume("slam_4")
        else:
            costume("slam_7")
    elif st == "slam":
        if t < 8:
            costume("slam_0")
        elif t < 36:
            costume(join("slam_", 1 + floor((t - 8) / 10)))
        elif t < 40:
            costume("slam_4")
        elif t < 48:
            costume("slam_5")
        elif t < 55:
            costume("slam_6")
        else:
            costume("slam_7")
    else:
        costume(join("stagger_", floor(t / 5) % 3))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if (st == "swing" and t >= 6 and t <= 15) or (st == "slam" and t >= 31 and t <= 40):
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    else:
        effect("brightness", 0)
    show()
'''


def _extract(src, name):
    i = src.index('@proc\ndef %s(' % name)
    j = src.index('\n\n\n', i)
    return src[i:j] + '\n\n\n'


CROUPIER = spawner('croupier', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    skin = ""
    pkind = "card"
    if chapter == 4:
        skin = "g_"
        pkind = "bolt"
    add_ent("croupier", x, y, 10, 38, 5, 6, 1)
    find_bounds()
    st = "idle"
    t = 0
    ehp = 5
    imax = 6
    integ = 0
    int_t = 0
    z = 0
    vz = 0
    fr = 0
    face = -1
    acd = 30 + rand(0, 30)
    hitrow = 0
    hit_t = 0
    flash_t = 0
    is_clone = 1
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("bar")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        c_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        c_draw()


''' + _extract(HANNYA, 'find_bounds') + '''@proc
def c_die():
    st = "dead"
    t = 0
    fr = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    dead_objs.append(myobj)
    sfxq.append("thug_die")


@proc
def throw_card(spread):
    mx = x + face * 16
    my = y + 30
    ax = px - mx
    ay = (py + 20) - my
    dd = sqrt(ax * ax + ay * ay)
    if dd < 1:
        dd = 1
    pq_t.append(pkind)
    pq_x.append(mx)
    pq_y.append(my)
    pq_vx.append(ax / dd * 5.5)
    pq_vy.append(ay / dd * 5.5 + spread)
    if pkind == "bolt":
        sfxq.append("turret_fire")
    else:
        sfxq.append("card_throw")


@proc
def c_update():
    t += 1
    if st == "dead":
        fr += 0.27
        return
    if ent_sev[slot] == 1:
        c_die()
        return
    if ent_dmg[slot] > 0:
        ehp -= ent_dmg[slot]
        if st != "stagger":
            integ = min(imax, integ + ent_idmg[slot])
        int_t = 0
        hk = ent_hk[slot]
        x = min(max(x + ent_kb[slot], xmin), xmax)
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        flash_t = 3
        sfxq.append("thug_hurt")
        if ehp <= 0:
            c_die()
            return
        if st != "stagger":
            if hk == "launcher":
                st = "air"
                vz = 10
                t = 0
            elif st != "swing":
                st = "hurt"
                t = 0
    if integ >= imax and st != "stagger" and st != "air":
        st = "stagger"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        sfxq.append("stagger")
    dx = px - x
    if st == "idle":
        fr += 0.17
        if abs(dx) < 300 and abs(py - y) < 140:
            st = "walk"
    elif st == "walk":
        fr += 0.27
        if dx > 0:
            face = 1
        else:
            face = -1
        if acd > 0:
            acd -= 1
        if abs(dx) < 56 and abs(py - y) < 50:
            if acd < 20:
                st = "wind"
                t = 0
                hitdone = 0
                sfxq.append("windup")
        elif abs(dx) < 110:
            x = min(max(x - face * 1.4, xmin), xmax)
        elif abs(dx) > 190:
            x = min(max(x + face * 1.4, xmin), xmax)
        if st == "walk" and acd == 0 and abs(dx) >= 56 and pst != "dead":
            st = "aim"
            t = 0
    elif st == "aim":
        if t == 18:
            throw_card(0)
        if t == 28:
            throw_card(0)
        if t >= 40:
            st = "walk"
            acd = rand(45, 80)
    elif st == "wind":
        if t > 22:
            st = "swing"
            t = 0
            sfxq.append("swing")
    elif st == "swing":
        if hitdone == 0 and t <= 4:
            if face == 1:
                p_overlap(x, x + 46, y + 4, y + 40)
            else:
                p_overlap(x - 46, x, y + 4, y + 40)
            if ov == 1:
                hitdone = 1
                hit_player(2, 0, x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
                    st = "hurt"
                    t = 0
        if t >= 8 and st == "swing":
            st = "walk"
            acd = 30
    elif st == "hurt":
        if t >= 12:
            st = "walk"
            acd = max(acd, 10)
    elif st == "stagger":
        if t >= 80:
            st = "walk"
            integ = imax / 2
            ent_stag[slot] = 0
            acd = 20
    elif st == "air":
        z += vz
        vz -= 1.1
        if z <= 0:
            z = 0
            st = "hurt"
            t = 0
    int_t += 1
    if int_t > 60 and integ > 0 and st != "stagger" and t % 15 == 0:
        integ -= 1
    ent_x[slot] = x
    ent_y[slot] = y + z
    ent_int[slot] = integ


@proc
def c_draw():
    if st == "dead":
        if fr >= 7:
            delete_clone()
        costume(join(join(skin, "death_"), min(4, floor(fr))))
        if fr > 5:
            effect("ghost", (fr - 5) * 50)
    elif st == "idle":
        costume(join(join(skin, "idle_"), floor(fr) % 4))
    elif st == "walk":
        costume(join(join(skin, "walk_"), floor(fr) % 6))
    elif st == "aim":
        if t < 10 or (t >= 20 and t < 26):
            costume(join(skin, "attack_1"))
        elif t < 18 or (t >= 26 and t < 28):
            costume(join(skin, "attack_2"))
        else:
            costume(join(skin, "attack_4"))
    elif st == "wind":
        if t < 9:
            costume(join(skin, "attack_1"))
        else:
            costume(join(skin, "attack_2"))
    elif st == "swing":
        if t < 3:
            costume(join(skin, "attack_3"))
        else:
            costume(join(skin, "attack_4"))
    elif st == "stagger":
        costume(join(skin, "hurt_1"))
    else:
        costume(join(join(skin, "hurt_"), min(1, floor(t / 4))))
    goto(x + shx, y + z + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if (st == "wind" and t >= 15) or (st == "swing" and t <= 1):
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    elif st != "dead":
        effect("brightness", 0)
    show()
'''


LUCK = spawner('luck', '''
if luck_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("luck", x, y, 10, 40, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    fr = 0
    face = -1
    phase = 1
    flash_t = 0
    guard_t = 0
    tx = x
    boss_hp = 20
    boss_int = 0
    slot_state = "idle"
    slot_sym = "seven"
    is_clone = 1
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        l_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        l_draw()


@proc
def throw_card(ang_off, spd):
    mx = x + face * 16
    my = y + 30
    ax = px - mx
    ay = (py + 20) - my
    base = atan(ay / (abs(ax) + 0.01))
    if ax < 0:
        dirx = -1
    else:
        dirx = 1
    ang = base + ang_off
    pq_t.append("card")
    pq_x.append(mx)
    pq_y.append(my)
    pq_vx.append(dirx * cos(ang) * spd)
    pq_vy.append(sin(ang) * spd)
    sfxq.append("card_throw")


@proc
def vulnerable():
    vuln = 0
    if st == "recover" or st == "recoil" or st == "stagger" or st == "broken" or st == "stagger2":
        vuln = 1


@proc
def pick_symbol():
    roll = rand(1, 100)
    if phase == 2 and roll <= 22:
        slot_sym = "jackpot"
    elif roll <= 40:
        slot_sym = "spade"
    elif roll <= 62:
        slot_sym = "seven"
    elif roll <= 84:
        slot_sym = "cherry"
    else:
        slot_sym = "skull"


@proc
def l_die():
    st = "dead"
    t = 0
    fr = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    slot_state = "idle"
    sfxq.append("oni_die")
    shake = 24
    shake_amp = 6
    hitstop = 12
    broadcast("ev_luck_dead")


@proc
def l_update():
    t += 1
    if st == "dead":
        fr += 0.27
        return
    if st == "wait":
        fr += 0.2
        if boss_on == 1:
            st = "move"
            t = 0
            tx = 140
            if px > 0:
                tx = -140
        return
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        st = "stagger2"
        t = 0
        flash_t = 6
        slot_state = "idle"
        sfxq.append("oni_hurt")
        if ehp <= 0:
            l_die()
            return
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        vulnerable()
        if vuln == 1 or hk == "projectile" or (hk == "heavy" and st != "jackpot"):
            ehp -= ent_dmg[slot]
            flash_t = 3
            if hk == "heavy" and vuln == 0:
                st = "stagger"
                t = 0
                slot_state = "idle"
                sfxq.append("oni_hurt")
        else:
            sfxq.append("clang")
            cfx("deflect", x + face * 12, y + 26, 0 - face)
            guard_t = 8
        gain = ent_idmg[slot]
        if vuln == 0 and hk != "projectile" and hk != "heavy":
            gain = gain * 0.4
        if st != "broken":
            integ = min(imax, integ + gain)
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            ehp = 0
            l_die()
            return
    if ehp <= 10 and phase == 1:
        phase = 2
        broadcast("ev_luck_phase2")
    if integ >= imax and st != "broken" and st != "stagger2":
        st = "broken"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        ent_brk[slot] = 0
        slot_state = "idle"
        sfxq.append("stagger")
    if guard_t > 0:
        guard_t -= 1
    dx = px - x
    ent_brk[slot] = 0
    if st == "move":
        fr += 0.53
        if tx > x:
            face = 1
        else:
            face = -1
        if abs(tx - x) < 10:
            st = "spin"
            t = 0
            pick_symbol()
            slot_state = "spin"
            slot_t = 0
            sfxq.append("reels")
        else:
            x += face * 7
    elif st == "spin":
        slot_t = t
        fr += 0.2
        if dx > 0:
            face = 1
        else:
            face = -1
        if t == 33 or t == 43 or t == 53:
            sfxq.append("reel_stop")
        if t >= 68:
            slot_state = "show"
            st = slot_sym
            t = 0
            hitdone = 0
            if slot_sym == "skull":
                sfxq.append("breach")
            if slot_sym == "jackpot":
                sfxq.append("jackpot")
                sl_q.append(-220)
                sl_q.append(220)
    elif st == "spade":
        if dx > 0:
            face = 1
        else:
            face = -1
        if t == 8 or t == 30:
            throw_card(-14, 5)
            throw_card(0, 5)
            throw_card(14, 5)
        if t >= 44:
            to_recover(32)
    elif st == "seven":
        if dx > 0:
            face = 1
        else:
            face = -1
        if t >= 8 and t <= 40 and (t - 8) % 8 == 0:
            throw_card(0, 6.5)
        if t >= 48:
            to_recover(32)
    elif st == "cherry":
        if t < 45 and abs(dx) > 44:
            if dx > 0:
                face = 1
            else:
                face = -1
            x = min(max(x + face * 8, -200), 200)
            fr += 0.53
        else:
            st = "slash"
            t = 0
            hitdone = 0
            sfxq.append("swing")
    elif st == "slash":
        if (t == 12 or t == 30) and hitdone < 2:
            if face == 1:
                p_overlap(x, x + 50, y + 4, y + 42)
            else:
                p_overlap(x - 50, x, y + 4, y + 42)
            if ov == 1:
                hit_player(2, 0, x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
                    st = "recoil"
                    t = 0
                    sfxq.append("clang")
            hitdone += 1
            if t == 12 and st == "slash":
                sfxq.append("swing")
        if t >= 42 and st == "slash":
            to_recover(30)
    elif st == "skull":
        if t < 30:
            ent_brk[slot] = 1
        if t == 30:
            pq_t.append("wave")
            pq_x.append(x)
            pq_y.append(y)
            pq_vx.append(6.5)
            pq_vy.append(0)
            pq_t.append("wave")
            pq_x.append(x)
            pq_y.append(y)
            pq_vx.append(-6.5)
            pq_vy.append(0)
            cfx("shockwave", x, y, 0)
            sfxq.append("oni_slam")
            shake = 10
            shake_amp = 5
        if t >= 50:
            to_recover(36)
    elif st == "jackpot":
        if dx > 0:
            face = 1
        else:
            face = -1
        if t % 24 == 12:
            throw_card(0, 5)
        if t >= 150:
            to_recover(40)
    elif st == "recover":
        if t >= rec_len:
            st = "move"
            t = 0
            slot_state = "idle"
            if x > 0:
                tx = -140
            else:
                tx = 140
            if rand(1, 3) == 1:
                tx = 0 - tx
    elif st == "recoil":
        if t >= 22:
            to_recover(30)
    elif st == "stagger":
        if t >= 20:
            to_recover(20)
    elif st == "broken":
        if t >= 110:
            st = "move"
            t = 0
            integ = 8
            ent_stag[slot] = 0
            tx = 0 - x
    elif st == "stagger2":
        if t >= 36:
            to_recover(20)
    if slot_state == "show":
        slot_t += 1
    int_t += 1
    if int_t > 75 and integ > 0 and st != "broken" and t % 20 == 0:
        integ -= 1
    if x < -200:
        x = -200
    if x > 200:
        x = 200
    ent_x[slot] = x
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ


@proc
def to_recover(n):
    st = "recover"
    t = 0
    rec_len = n
    slot_state = "idle"


@proc
def l_draw():
    if st == "dead":
        costume(join("death_", min(5, floor(fr))))
    elif guard_t > 0:
        costume(join("deflect_", min(2, floor((8 - guard_t) / 3))))
    elif st == "wait" or st == "spin" or st == "jackpot":
        costume(join("idle_", floor(fr) % 4))
    elif st == "move" or st == "cherry":
        costume(join("dash_", 1 + floor(fr) % 2))
    elif st == "spade" or st == "seven":
        costume(join("attack2_", min(3, floor(t / 4) % 4)))
    elif st == "slash":
        if t < 30:
            costume(join("attack1_", min(3, floor(t / 4))))
        else:
            costume(join("attack3_", min(3, floor((t - 30) / 4))))
    elif st == "skull":
        costume(join("heavy_", min(5, floor(t / 6))))
    elif st == "broken":
        costume(join("overheat_", floor(t / 5) % 4))
    elif st == "recover":
        costume(join("block_0", ""))
        if t > 6:
            costume(join("idle_", floor(t / 5) % 4))
    else:
        costume(join("hurt_", floor(t / 5) % 2))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "slash" and ((t >= 3 and t <= 12) or (t >= 21 and t <= 30)):
        tell = 1
    if st == "skull" and t >= 21 and t <= 30:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    else:
        effect("brightness", 0)
    show()
'''


SWEEP = '''
@on("t_world")
def tick():
    if is_clone == 1:
        t += 1
        if t < 75:
            x += vx
        else:
            x -= vx
        if t > 150 or ent_alive[boss_slot] != 1:
            delete_clone()
        if abs(px - x) < 12 and py < y + 90:
            hit_player(2, 1, x - vx * 4)
    else:
        for qi in range(1, len(sl_q) + 1):
            x = sl_q[qi]
            y = -124
            if x < 0:
                vx = 2.6
            else:
                vx = -2.6
            t = 0
            is_clone = 1
            clone()
            is_clone = 0
        sl_q.clear()


@on("t_draw")
def draw():
    if is_clone == 1:
        costume(join("on_", floor(frame / 2) % 4))
        goto(x + shx, y + shy)
        size(100)
        show()
'''


SLOT_MACHINE = spawner('slot', '''
x = O_X[oi]
y = O_Y[oi]
is_clone = 1
clone()
is_clone = 0
for k in range(1, 5):
    reel_q.append(k)
    clone("Reels")
''') + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        if slot_state == "spin":
            costume(join("slot_", floor(frame / 2) % 2))
        else:
            costume(join("slot_", floor(frame / 12) % 2))
        goto(x + shx, y + shy)
        show()
'''


REELS = '''
@clone
def reel_start():
    is_clone = 1
    rk = reel_q[1]
    reel_q.delete(1)


@on("clear")
def reel_clear():
    if is_clone == 1:
        delete_clone()


@on("t_draw")
def draw():
    if is_clone == 1 and rk == 4:
        # Outcome callout on the machine's payout panel, from the last reel
        # stop until the attack is under way.
        if (slot_state == "spin" and slot_t >= 53) or (slot_state == "show" and slot_t < 110):
            costume(join("call_", slot_sym))
            if slot_t < 57:
                size(100 + (57 - slot_t) * 8)
            else:
                size(100)
            goto(shx, 22 + shy)
            show()
        else:
            hide()
    elif is_clone == 1:
        if slot_state == "spin" and slot_t < 22 + 10 * rk:
            costume(join("blur_", (floor(slot_t / 2) + rk) % 2))
        elif slot_state == "idle":
            costume("sym_seven")
        else:
            costume(join("sym_", slot_sym))
        goto(-82 + 40 * rk + shx, 65 + shy)
        show()
'''


def _proc(src, name):
    """Copy one @proc definition out of another sprite's source."""
    i = src.index('@proc\ndef %s(' % name)
    j = src.index('\n\n\n', i)
    return src[i:j] + '\n\n\n'


# Garden Warden: a Kanshi duelist that guards in neutral. Deflect its strikes
# (or land a Heavy Strike) to break its guard; it takes damage only while
# recovering, recoiling or staggered, and counters anyone who mashes.
WARDEN = spawner('warden', '''
if not (oi in dead_objs):
    x = O_X[oi]
    y = O_Y[oi]
    brk_ok = O_A[oi]
    myobj = oi
    add_ent("warden", x, y, 10, 38, 6, 6, 1)
    find_bounds()
    st = "idle"
    t = 0
    ehp = 6
    imax = 6
    integ = 0
    int_t = 0
    z = 0
    vz = 0
    fr = 0
    face = -1
    acd = 25
    guard_t = 0
    guard_n = 0
    hitrow = 0
    hit_t = 0
    nh = 1
    flash_t = 0
    elite = 0
    skin = ""
    if O_TYPE[oi] == "shell":
        elite = 1
        skin = "s_"
        ehp = 8
        imax = 7
    elif chapter == 5:
        skin = "m_"
    is_clone = 1
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("bar")
    clone("EnemyUI")
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        w_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        w_draw()


''' + _proc(HANNYA, 'find_bounds') + '''
@proc
def w_face():
    if px > x:
        face = 1
    else:
        face = -1


@proc
def w_combo(n):
    w_face()
    t = 0
    hitdone = 0
    nh = n
    if brk_ok == 1 and rand(1, 100) <= 35:
        st = "heavy"
        sfxq.append("breach")
    else:
        st = "combo"
        sfxq.append("windup")


@proc
def w_die():
    st = "dead"
    t = 0
    fr = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    dead_objs.append(myobj)
    sfxq.append("thug_die")


@proc
def w_strike(reach, dmg, brk, last):
    if face == 1:
        p_overlap(x, x + reach, y + 4, y + 40)
    else:
        p_overlap(x - reach, x, y + 4, y + 40)
    if ov == 1:
        hit_player(dmg, brk, x)
        if res == "deflect":
            integ = min(imax, integ + 2)
            int_t = 0
            x = min(max(x - face * 5, xmin), xmax)
            if last == 1:
                st = "recoil"
                t = 0


@proc
def w_update():
    t += 1
    if st == "dead":
        fr += 0.27
        return
    if ent_sev[slot] == 1:
        w_die()
        return
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        if st == "recover" or st == "recoil" or st == "hurt" or st == "stagger" or st == "air" or hk == "projectile":
            ehp -= ent_dmg[slot]
            if st != "stagger":
                integ = min(imax, integ + ent_idmg[slot])
            x = min(max(x + ent_kb[slot], xmin), xmax)
            flash_t = 3
            sfxq.append("thug_hurt")
            if ehp <= 0:
                w_die()
                return
            if st != "stagger":
                hitrow += 1
                if hk == "launcher":
                    st = "air"
                    vz = 10
                    t = 0
                elif st != "air":
                    if hitrow >= 3:
                        hitrow = 0
                        st = "walk"
                        acd = 4
                    else:
                        st = "hurt"
                        t = 0
        else:
            sfxq.append("muk_guard")
            cfx("deflect", x + face * 12, y + 26, 0 - face)
            if st != "combo" and st != "heavy":
                guard_t = 8
                w_face()
            if hk == "heavy":
                integ = min(imax, integ + ent_idmg[slot])
            else:
                integ = min(imax, integ + ent_idmg[slot] * 0.5)
            guard_n += 1
            hit_t = 0
            if guard_n >= 3 and st != "combo" and st != "heavy":
                guard_n = 0
                st = "combo"
                w_face()
                hitdone = 0
                nh = 1
                t = 7
                sfxq.append("windup")
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
    if integ >= imax and st != "stagger" and st != "air":
        st = "stagger"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        sfxq.append("stagger")
    dx = px - x
    if guard_t > 0:
        guard_t -= 1
    if st == "idle":
        fr += 0.17
        if abs(dx) < 240 and abs(py - y) < 90:
            st = "walk"
    elif st == "walk":
        w_face()
        if acd > 0:
            acd -= 1
        if elite == 1 and acd == 0 and abs(dx) > 100 and abs(py - y) < 60:
            t = 0
            if rand(1, 2) == 1:
                st = "dashin"
                sfxq.append("dash")
            else:
                st = "throw"
                sfxq.append("windup")
        elif abs(dx) > 40:
            fr += 0.3
            x = min(max(x + face * 1.8, xmin), xmax)
        if abs(dx) < 56 and acd == 0 and abs(py - y) < 60 and pst != "dead":
            w_combo(rand(1, 2))
    elif st == "combo":
        if t == 16 or (nh == 2 and t == 30):
            sfxq.append("muk_slash")
            w_strike(46, 2, 0, (t == 30 or nh == 1) + 0)
        if st == "combo" and ((nh == 1 and t >= 22) or t >= 36):
            st = "recover"
            t = 0
    elif st == "dashin":
        x = min(max(x + face * 9, xmin), xmax)
        if t % 2 == 0:
            mfx("afterimage", x, y, face)
        if t >= 10 or abs(dx) < 44:
            w_combo(1)
    elif st == "throw":
        if t == 12:
            pq_t.append("bolt")
            pq_x.append(x + face * 14)
            pq_y.append(y + 22)
            pq_vx.append(face * 7)
            pq_vy.append(0)
            sfxq.append("throw")
        if t >= 24:
            st = "walk"
            acd = rand(16, 36)
    elif st == "heavy":
        if t == 24:
            sfxq.append("swing")
            w_strike(56, 3, 1, 1)
        if t >= 32:
            st = "recover"
            t = 0
    elif st == "recover":
        if t >= 22 - 6 * elite:
            st = "walk"
            acd = rand(12, 36) - 8 * elite
            hitrow = 0
    elif st == "recoil":
        if t >= 22:
            st = "walk"
            acd = 10
            hitrow = 0
    elif st == "hurt":
        if t >= 12:
            st = "walk"
            acd = max(acd, 6)
    elif st == "stagger":
        if t >= 80:
            st = "walk"
            integ = imax / 2
            ent_stag[slot] = 0
            acd = 10
    elif st == "air":
        z += vz
        vz -= 1.1
        if z <= 0:
            z = 0
            st = "hurt"
            t = 0
    int_t += 1
    if int_t > 60 and integ > 0 and st != "stagger" and t % 15 == 0:
        integ -= 1
    hit_t += 1
    if hit_t > 40:
        guard_n = 0
    ent_x[slot] = x
    ent_y[slot] = y + z
    ent_int[slot] = integ
    if st == "heavy" and t < 24:
        ent_brk[slot] = 1
    else:
        ent_brk[slot] = 0


@proc
def w_draw():
    if st == "dead":
        if fr >= 8:
            delete_clone()
        costume(join(join(skin, "death_"), min(5, floor(fr))))
        if fr > 6:
            effect("ghost", (fr - 6) * 50)
    elif guard_t > 0:
        costume(join(join(skin, "deflect_"), min(2, floor((8 - guard_t) / 3))))
    elif st == "idle":
        costume(join(join(skin, "idle_"), floor(fr) % 4))
    elif st == "walk":
        if abs(px - x) <= 60:
            costume(join(skin, "block_0"))
        else:
            costume(join(join(skin, "run_"), floor(fr) % 8))
    elif st == "combo":
        if t < 23:
            hf = t - 16
            an = "attack1_"
        else:
            hf = t - 30
            an = "attack2_"
        if hf < -6:
            costume(join(an, 0))
        elif hf < 0:
            costume(join(an, 1))
        elif hf < 3:
            costume(join(an, 2))
        else:
            costume(join(an, 3))
    elif st == "dashin":
        costume(join(join(skin, "dash_"), min(3, floor(t / 3))))
    elif st == "throw":
        costume(join(join(skin, "attack2_"), min(3, floor(t / 4))))
    elif st == "heavy":
        if t < 8:
            costume(join(skin, "heavy_0"))
        elif t < 15:
            costume(join(skin, "heavy_1"))
        elif t < 21:
            costume(join(skin, "heavy_2"))
        elif t < 24:
            costume(join(skin, "heavy_3"))
        else:
            costume(join(join(skin, "heavy_"), min(5, 4 + floor((t - 24) / 4))))
    elif st == "stagger":
        costume(join(join(skin, "overheat_"), floor(t / 5) % 4))
    elif st == "recover":
        costume(join(join(skin, "idle_"), floor(t / 5) % 4))
    else:
        costume(join(join(skin, "hurt_"), min(1, floor(t / 5))))
    if st == "stagger":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + z + shy)
    else:
        goto(x + shx, y + z + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "combo" and ((t >= 7 and t <= 16) or (nh == 2 and t >= 21 and t <= 30)):
        tell = 1
    if st == "heavy" and t >= 15 and t <= 24:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 70)
    elif st != "dead":
        effect("brightness", 0)
    show()
'''


# Mukuro I: a pure deflect duel. He guards every blow outside his openings,
# so the way through is deflecting his strings to fill his Integrity, then
# punishing the recoveries. Mashing into his guard earns a counter, and so
# does staying greedy in an opening.
MUKURO = spawner('mukuro', '''
mk2 = 0
if O_A[oi] == 2:
    mk2 = 1
if (mk2 == 0 and muk_dead == 0) or (mk2 == 1 and muk2_dead == 0):
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("mukuro", x, y, 10, 38, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    fr = 0
    face = -1
    phase = 1
    flash_t = 0
    guard_t = 0
    guard_n = 0
    hitrow = 0
    hit_t = 0
    acd = 30
    rec_len = 30
    boss_hp = 20
    boss_int = 0
    fy = y
    sh_x = 999
    if mk2 == 1:
        muk_exit = 0
    is_clone = 1
    role = "body"
    clone()
    if mk2 == 1:
        role = "shadow"
        clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1 and role == "body":
        m_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        if role == "shadow":
            sh_draw()
        else:
            m_draw()


@proc
def m2_pick(roll):
    # Mukuro II: new tricks on top of his old strings
    if phase == 1:
        if roll <= 32:
            set_combo("c3")
        elif roll <= 52:
            set_combo("c2h")
        elif roll <= 76:
            set_combo("kunai")
        else:
            set_combo("dive")
    else:
        if roll <= 18:
            set_combo("c4")
        elif roll <= 34:
            set_combo("delay")
        elif roll <= 52:
            set_combo("kunai")
        elif roll <= 72:
            set_combo("dive")
        else:
            set_combo("shadow")


@proc
def m_kunai():
    mx = x + face * 14
    my = y + 24
    ax = px - mx
    ay = py + 18 - my
    base = atan(ay / (abs(ax) + 0.01))
    for k in range(3):
        ang = base + (k - 1) * 12
        pq_t.append("bolt")
        pq_x.append(mx)
        pq_y.append(my)
        pq_vx.append(face * cos(ang) * 7)
        pq_vy.append(sin(ang) * 7)
    sfxq.append("throw")


@proc
def m_rec(n):
    st = "recover"
    t = 0
    rec_len = n
    hitrow = 0
    sh_x = 999


@proc
def sh_draw():
    if sh_x < 900:
        hf = sh_t - 18
        if hf < -6:
            costume("attack1_0")
        elif hf < 0:
            costume("attack1_1")
        elif hf < 3:
            costume("attack1_2")
        else:
            costume("attack1_3")
        effect("ghost", 40)
        if sh_t >= 9 and sh_t <= 18:
            effect("brightness", 100)
        else:
            effect("brightness", -40)
        if sh_f == 1:
            point(90)
        else:
            point(-90)
        goto(sh_x + shx, fy + shy)
        show()
    else:
        hide()


@proc
def m_face():
    if px > x:
        face = 1
    else:
        face = -1


@proc
def set_combo(kind):
    st = "combo"
    ck = kind
    t = 0
    hitdone = 0
    n = 3
    h1 = 14
    h2 = 28
    h3 = 44
    h4 = 0
    k1 = "attack1"
    k2 = "attack2"
    k3 = "attack3"
    k4 = "heavy"
    b3 = 0
    b4 = 0
    if kind == "c2h":
        h3 = 60
        k3 = "heavy"
        b3 = 1
    elif kind == "c4":
        h1 = 12
        h2 = 24
        h3 = 36
        h4 = 66
        n = 4
        b4 = 1
    elif kind == "delay":
        h2 = 44
        h3 = 56
    elif kind == "lunge":
        n = 1
        h1 = 18
        k1 = "attack3"
        sfxq.append("dash")
    elif kind == "counter":
        n = 1
        h1 = 8
        k1 = "attack2"
        if phase == 2:
            n = 2
            h2 = 20
            k2 = "attack1"
    m_face()
    if kind != "lunge":
        sfxq.append("windup")
    if kind == "kunai" or kind == "dive" or kind == "shadow":
        st = kind
        if kind == "dive":
            sfxq.append("breach")
        if kind == "shadow":
            if x < px:
                sh_x = min(px + 46, 215)
                sh_f = -1
            else:
                sh_x = max(px - 46, -215)
                sh_f = 1
            sh_t = 0
            sfxq.append("muk_warp")


@proc
def get_hit():
    # current strike of the string: ci, its time ht, animation kk, breach bb
    ci = 0
    if t <= h1 + 4:
        ci = 1
        ht = h1
        kk = k1
        bb = 0
    elif n >= 2 and t <= h2 + 4:
        ci = 2
        ht = h2
        kk = k2
        bb = 0
    elif n >= 3 and t <= h3 + 4:
        ci = 3
        ht = h3
        kk = k3
        bb = b3
    elif n >= 4 and t <= h4 + 4:
        ci = 4
        ht = h4
        kk = k4
        bb = b4


@proc
def m_strike():
    reach = 48
    dmg = 2
    if kk == "attack3":
        reach = 64
    if kk == "heavy":
        reach = 58
        dmg = 3
    if face == 1:
        p_overlap(x - 6, x + reach, y + 2, y + 40)
    else:
        p_overlap(x - reach, x + 6, y + 2, y + 40)
    if kk == "heavy":
        sfxq.append("swing")
        cfx("shockwave", x + face * 30, y, 0)
        shake = 6
        shake_amp = 3
    else:
        sfxq.append("muk_slash")
    if ov == 1:
        hit_player(dmg, bb, x)
        if res == "deflect":
            integ = min(imax, integ + 2)
            int_t = 0
            x = min(max(x - face * 4, -205), 205)
            if ci == n:
                st = "recoil"
                t = 0


@proc
def m_beaten():
    if mk2 == 1 and st != "kneel":
        # the last segment: Hotaru chooses to destroy him or free him
        st = "kneel"
        t = 0
        ehp = 0
        integ = 0
        sh_x = 999
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        ent_sev[slot] = 0
        ent_stag[slot] = 0
        ent_brk[slot] = 0
        boss_hp = 0
        boss_int = 0
        sfxq.append("stagger")
        shake = 12
        shake_amp = 4
        hitstop = 10
        broadcast("ev_muk2_choice")
        return
    st = "beaten"
    t = 0
    ehp = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("stagger")
    shake = 16
    shake_amp = 5
    hitstop = 12
    if mk2 == 0:
        broadcast("ev_muk_dead")


@proc
def m_open():
    mo = 0
    if st == "recover" or st == "recoil" or st == "broken":
        mo = 1


@proc
def m_update():
    t += 1
    if st == "kneel":
        ent_x[slot] = x
        if ent_dmg[slot] > 0 and t < 20:
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
        elif ent_dmg[slot] > 0 and mode == "play":
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
            muk_freed = 0
            st = "dead"
            t = 0
            ent_alive[slot] = 0
            sfxq.append("oni_die")
            shake = 12
            shake_amp = 5
            broadcast("ev_muk2_dead")
        elif abs(px - x) < 54 and p_ground == 1 and mode == "play":
            prompt_on = 1
            prompt_x = x
            prompt_y = y + 84
            if pE == 1:
                muk_freed = 1
                st = "beaten"
                t = 0
                ent_alive[slot] = 0
                sfxq.append("sync")
                broadcast("ev_muk2_dead")
        return
    if st == "dead":
        return
    if st == "beaten":
        if muk_exit == 1:
            st = "exit"
            t = 0
        return
    if st == "exit":
        return
    if st == "wait":
        fr += 0.2
        if boss_on == 1:
            st = "move"
            t = 0
            acd = 40
        return
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        st = "stagger2"
        t = 0
        flash_t = 6
        sfxq.append("oni_hurt")
        if ehp <= 0:
            m_beaten()
            return
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        m_open()
        if mo == 1:
            ehp -= ent_dmg[slot]
            flash_t = 3
            sfxq.append("thug_hurt")
            if st != "broken":
                integ = min(imax, integ + ent_idmg[slot])
            if st == "recover" or st == "recoil":
                hitrow += 1
                if hitrow >= 4 - phase:
                    hitrow = 0
                    set_combo("counter")
        else:
            sfxq.append("muk_guard")
            cfx("deflect", x + face * 12, y + 26, 0 - face)
            if hk == "heavy":
                integ = min(imax, integ + ent_idmg[slot] * 0.5)
            else:
                integ = min(imax, integ + ent_idmg[slot] * 0.1)
            if st != "combo":
                guard_t = 8
                m_face()
                guard_n += 1
                hit_t = 0
                if guard_n >= 3:
                    guard_n = 0
                    set_combo("counter")
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            m_beaten()
            return
    if ehp <= 10 and phase == 1:
        phase = 2
        broadcast("ev_muk_phase2")
    if integ >= imax and st != "broken" and st != "stagger2":
        st = "broken"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        ent_brk[slot] = 0
        sfxq.append("stagger")
    if guard_t > 0:
        guard_t -= 1
    dx = px - x
    ent_brk[slot] = 0
    if st == "move":
        m_face()
        if acd > 0:
            acd -= 1
        ad = abs(dx)
        if ad > 150 and acd == 0:
            if mk2 == 1 and rand(1, 2) == 1:
                set_combo("kunai")
            else:
                set_combo("lunge")
        elif ad > 62:
            fr += 0.4
            x += face * (2 + 2 * (ad > 120))
        elif acd == 0 and pst != "dead":
            roll = rand(1, 100)
            if mk2 == 1:
                m2_pick(roll)
            elif phase == 1:
                if roll <= 58:
                    set_combo("c3")
                else:
                    set_combo("c2h")
            else:
                if roll <= 28:
                    set_combo("c3")
                elif roll <= 54:
                    set_combo("delay")
                elif roll <= 80:
                    set_combo("c4")
                else:
                    set_combo("c2h")
        elif ad < 36:
            x -= face * 1.5
    elif st == "combo":
        get_hit()
        if ci == 0:
            st = "recover"
            t = 0
            rec_len = 26 - 8 * (phase - 1)
            hitrow = 0
        else:
            if t == ht - 10:
                m_face()
                if bb == 1:
                    sfxq.append("breach")
            if ck == "lunge" and t < 12:
                if abs(dx) > 46:
                    x += face * 11
            elif t >= ht - 8 and t < ht and abs(dx) > 40:
                x += face * 3
            if bb == 1 and t >= ht - 20 and t < ht:
                ent_brk[slot] = 1
            if t == ht:
                m_strike()
    elif st == "kunai":
        if t == 14 or (phase == 2 and t == 30):
            m_kunai()
        if t >= 40 + 16 * (phase - 1):
            m_rec(22 - 6 * (phase - 1))
    elif st == "dive":
        if t < 16:
            y += 10 - t * 0.5
        elif t < 36:
            x += min(8, max(-8, px - x))
            ent_brk[slot] = 1
        else:
            y -= 18
            if y <= fy:
                y = fy
                sfxq.append("oni_slam")
                cfx("shockwave", x, y, 0)
                shake = 10
                shake_amp = 5
                for k in range(2):
                    pq_t.append("wave")
                    pq_x.append(x)
                    pq_y.append(y)
                    pq_vx.append(6 - 12 * k)
                    pq_vy.append(0)
                if abs(px - x) < 30 and py < y + 40:
                    hit_player(3, 1, x)
                m_rec(34)
    elif st == "shadow":
        sh_t = t
        if t == 18:
            sfxq.append("muk_slash")
            if sh_f == 1:
                p_overlap(sh_x - 6, sh_x + 48, y + 2, y + 40)
            else:
                p_overlap(sh_x - 48, sh_x + 6, y + 2, y + 40)
            if ov == 1:
                hit_player(2, 0, sh_x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
        elif t == 21:
            m_face()
        elif t == 30:
            kk = "attack2"
            bb = 0
            ci = 1
            n = 1
            m_strike()
        if t >= 40 and st == "shadow":
            m_rec(22 - 6 * (phase - 1))
    elif st == "recover":
        if t >= rec_len:
            st = "move"
            t = 0
            hitrow = 0
            acd = rand(10, 30) - 8 * (phase - 1)
    elif st == "recoil":
        if t >= 26 - 10 * mk2:
            st = "recover"
            t = 0
            rec_len = 10
    elif st == "broken":
        if t >= 110:
            st = "move"
            t = 0
            integ = 8
            ent_stag[slot] = 0
            acd = 6
    elif st == "stagger2":
        if t >= 36:
            st = "move"
            t = 0
            acd = 20
            if abs(dx) < 80:
                x = min(max(x - face * 30, -205), 205)
    int_t += 1
    if int_t > 75 and integ > 0 and st != "broken" and t % 20 == 0:
        integ = max(0, integ - 1)
    hit_t += 1
    if hit_t > 40:
        guard_n = 0
    x = min(max(x, -205), 205)
    ent_x[slot] = x
    ent_y[slot] = y
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ


@proc
def m_draw():
    effect("ghost", 0)
    if st == "beaten":
        costume(join("overheat_", floor(t / 6) % 4))
    elif st == "exit":
        costume("dash_1")
        effect("ghost", min(100, t * 5))
        if t > 22:
            hide()
            return
    elif guard_t > 0:
        costume(join("deflect_", min(2, floor((8 - guard_t) / 3))))
    elif st == "wait":
        costume(join("idle_", floor(fr) % 4))
    elif st == "move":
        if abs(px - x) > 62:
            costume(join("run_", floor(fr) % 8))
        else:
            costume("block_0")
    elif st == "combo":
        get_hit()
        if ck == "lunge" and t < 12:
            costume(join("dash_", min(3, floor(t / 3))))
        elif kk == "heavy":
            hf = t - ht
            if hf < -16:
                costume("heavy_0")
            elif hf < -8:
                costume("heavy_1")
            elif hf < -3:
                costume("heavy_2")
            elif hf < 0:
                costume("heavy_3")
            else:
                costume(join("heavy_", min(5, 4 + floor(hf / 4))))
        else:
            hf = t - ht
            if hf < -6:
                costume(join(kk, "_0"))
            elif hf < 0:
                costume(join(kk, "_1"))
            elif hf < 3:
                costume(join(kk, "_2"))
            else:
                costume(join(kk, "_3"))
    elif st == "kunai":
        kt = t % 16
        costume(join("attack2_", min(3, floor(kt / 4))))
    elif st == "dive":
        if t < 16:
            costume(join("jump_", min(4, floor(t / 4))))
        elif t < 36:
            costume("jump_4")
        else:
            costume("heavy_4")
    elif st == "shadow":
        if t < 21:
            costume("block_0")
        else:
            hf = t - 30
            if hf < -6:
                costume("attack2_0")
            elif hf < 0:
                costume("attack2_1")
            elif hf < 3:
                costume("attack2_2")
            else:
                costume("attack2_3")
    elif st == "kneel":
        costume(join("overheat_", floor(t / 6) % 4))
    elif st == "dead":
        costume(join("death_", min(5, floor(t / 5))))
    elif st == "broken":
        costume(join("overheat_", floor(t / 5) % 4))
    elif st == "recover":
        costume(join("idle_", floor(t / 5) % 4))
    else:
        costume(join("hurt_", floor(t / 5) % 2))
    if st == "broken" or st == "exit":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + shy)
    else:
        goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "combo":
        if t >= ht - 9 and t <= ht and ci > 0:
            tell = 1
    if st == "kunai" and (t % 16) >= 5 and (t % 16) <= 14 and t < 32:
        tell = 1
    if st == "shadow" and t >= 21 and t <= 30:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    else:
        effect("brightness", 0)
    show()
'''


# Raijin: the armored locomotive racing alongside on the parallel track.
# One sprite, several clone roles: the body (which owns the reactor core's
# hitbox and the brain), the pantograph arm, the ram plow, and four roof
# sections that it electrifies. The core is shuttered except while venting.
RAIJIN = spawner('raijin', '''
if raijin_dead == 0:
    roof_y = O_Y[oi]
    x = O_X[oi]
    y = roof_y + 22
    rest_x = x
    myobj = oi
    rj_bx = 420
    rj_arm = 999
    rj_plow = 999
    rj_open = 0
    RZ.clear()
    for k in range(4):
        RZ.append(0)
    add_ent("raijin", 420, y - 14, 12, 28, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    phase = 1
    flash_t = 0
    fire_t = 0
    step = 0
    last = 0
    idle_len = 40
    boss_hp = 20
    boss_int = 0
    is_clone = 1
    role = "body"
    clone()
    role = "arm"
    clone()
    role = "plow"
    clone()
    role = "zone"
    for k in range(1, 5):
        zi = k
        clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1 and role == "body":
        rj_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        rj_draw()


@proc
def zones_off():
    for k in range(1, 5):
        RZ[k] = 0


@proc
def to_vent():
    st = "vent"
    t = 0
    rj_open = 1
    sfxq.append("vent")


@proc
def rj_die():
    st = "dead"
    t = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    rj_arm = 999
    rj_plow = 999
    rj_open = 1
    zones_off()
    sfxq.append("rj_die")
    shake = 30
    shake_amp = 7
    hitstop = 14
    broadcast("ev_raijin_dead")


@proc
def pick_attack():
    t = 0
    hitdone = 0
    if phase == 1:
        step += 1
        roll = step % 3 + 1
    else:
        roll = rand(1, 4)
        if roll == last:
            roll = roll % 4 + 1
    last = roll
    if roll == 1:
        st = "cannon"
        nshot = 0
        nshots = 3 + 2 * (phase - 1)
        gap = 15 - 4 * (phase - 1)
    elif roll == 2:
        st = "zap"
        nw = phase
    elif roll == 3:
        st = "arm"
        sweeps = phase
        sfxq.append("arm")
    else:
        st = "ram"


@proc
def fire_shell():
    mx = rj_bx + 36
    my = y + 106
    tx = px + (nshot % 3 - 1) * 34
    ft = 34
    pq_t.append("shell")
    pq_x.append(mx)
    pq_y.append(my)
    pq_vx.append((tx - mx) / ft)
    pq_vy.append((py + 16 - my) / ft + 0.175 * ft)
    sfxq.append("cannon")
    fire_t = 5
    shake = 3
    shake_amp = 2


@proc
def zap_wave():
    # phase 1: alternate halves; phase 2: three live sections, one safe
    safe = rand(1, 4)
    pat = rand(0, 1)
    for k in range(1, 5):
        if phase == 1:
            if k % 2 == pat:
                RZ[k] = 1
            else:
                RZ[k] = 0
        elif k == safe:
            RZ[k] = 0
        else:
            RZ[k] = 1
    sfxq.append("zap_warn")


@proc
def rj_update():
    t += 1
    if fire_t > 0:
        fire_t -= 1
    if st == "dead":
        rj_bx += 2.5
        if t % 9 == 1 and t < 90:
            cfx("explosion", rj_bx + rand(-30, 120), y + rand(-10, 90), 0)
            sfxq.append("explode")
        return
    if st == "wait":
        if boss_on == 1:
            st = "enter"
            t = 0
            sfxq.append("horn")
        return
    if st == "enter":
        rj_bx = max(rest_x, rj_bx - 8)
        ent_x[slot] = rj_bx
        if rj_bx <= rest_x:
            st = "idle"
            t = 0
            idle_len = 30
        return
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        rj_open = 0
        st = "stagger"
        t = 0
        flash_t = 6
        sfxq.append("rj_hurt")
        shake = 12
        shake_amp = 5
        if ehp <= 0:
            rj_die()
            return
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        if hk == "projectile":
            ehp -= ent_dmg[slot]
            flash_t = 3
            sfxq.append("rj_hurt")
            if st != "overload":
                integ = min(imax, integ + ent_idmg[slot])
        elif rj_open == 1:
            # armor plating: melee on the open core does half damage
            ehp -= ent_dmg[slot] * 0.5
            flash_t = 3
            sfxq.append("rj_hurt")
            if st != "overload":
                integ = min(imax, integ + ent_idmg[slot])
        else:
            sfxq.append("clang")
            cfx("deflect", rj_bx - 10, y, 0)
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            rj_die()
            return
    if ehp <= 10 and phase == 1:
        phase = 2
        broadcast("ev_raijin_phase2")
    if integ >= imax and st != "overload" and st != "stagger" and st != "ram":
        st = "overload"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        rj_open = 1
        rj_arm = 999
        zones_off()
        sfxq.append("stagger")
    # live roof sections
    for k in range(1, 5):
        if RZ[k] == 2 and p_ground == 1 and px >= -360 + k * 120 and px < -240 + k * 120:
            hit_player(2, 1, px - pface)
    if st == "idle":
        if t >= idle_len:
            pick_attack()
    elif st == "cannon":
        if t % gap == 8 and nshot < nshots:
            fire_shell()
            nshot += 1
        if t >= nshots * gap + 34:
            to_vent()
    elif st == "zap":
        wt = t % 80
        if wt == 1:
            zap_wave()
        elif wt == 34:
            for k in range(1, 5):
                if RZ[k] == 1:
                    RZ[k] = 2
            sfxq.append("zap")
            shake = 4
            shake_amp = 2
        elif wt == 74:
            zones_off()
        if t >= nw * 80:
            to_vent()
    elif st == "arm":
        if rj_arm > 900:
            if t >= 24:
                rj_arm = rj_bx - 24
                hitdone = 0
        else:
            rj_arm -= 11
            if hitdone == 0 and abs(rj_arm - px) < 12 and py < -30 + roof_y + 60 and py + 34 > -38 + roof_y + 60:
                hitdone = 1
                hit_player(2, 0, rj_arm - 20)
                if res == "deflect":
                    integ = min(imax, integ + 3)
                    int_t = 0
                    sfxq.append("clang")
                    cfx("deflect", rj_arm, py + 20, 0)
                    rj_arm = -999
            if rj_arm < -270:
                rj_arm = 999
                sweeps -= 1
                t = 0
                if sweeps <= 0:
                    to_vent()
                else:
                    sfxq.append("arm")
    elif st == "ram":
        if t < 30:
            rj_bx += 10
        elif t == 30:
            sfxq.append("horn")
            rj_bx = 560
            hitdone = 0
        elif t > 52:
            rj_bx -= 15
            rj_plow = rj_bx - 70
            if hitdone == 0 and abs(rj_plow - px) < 46 and py < roof_y + 22:
                hitdone = 1
                hit_player(3, 1, rj_plow - 40)
            if rj_bx < -620:
                rj_plow = 999
                rj_bx = 520
                st = "enter"
                t = 0
    elif st == "vent":
        if t >= 60 - 8 * (phase - 1):
            rj_open = 0
            st = "idle"
            t = 0
            idle_len = 24
    elif st == "overload":
        if t >= 130:
            st = "idle"
            t = 0
            idle_len = 20
            integ = 8
            ent_stag[slot] = 0
            rj_open = 0
    elif st == "stagger":
        if t >= 40:
            st = "idle"
            t = 0
            idle_len = 16
    int_t += 1
    if int_t > 90 and integ > 0 and st != "overload" and t % 20 == 0:
        integ -= 1
    ent_x[slot] = rj_bx
    ent_int[slot] = integ
    boss_hp = ceil(ehp)
    boss_int = integ


@proc
def rj_draw():
    effect("ghost", 0)
    effect("brightness", 0)
    if role == "body":
        if st == "wait":
            hide()
            return
        if st == "dead":
            costume("rj_dead")
            effect("ghost", min(100, t * 1.2))
        elif rj_open == 1:
            costume(join("rj_vent_", floor(frame / 4) % 2))
        elif fire_t > 0:
            costume("rj_fire")
        else:
            costume(join("rj_idle_", floor(frame / 6) % 2))
        if flash_t > 0:
            flash_t -= 1
            effect("brightness", 60)
        if st == "overload" or st == "dead":
            goto(rj_bx + shx + (frame % 4 < 2) * 2 - 1, y + shy)
        else:
            goto(rj_bx + shx, y + shy)
        show()
    elif role == "arm":
        if rj_arm > -300 and rj_arm < 900:
            costume(join("arm_", frame % 2))
            if rj_arm > px and (rj_arm - px - 12) / 11 <= 9:
                effect("brightness", 100)
            goto(rj_arm + shx, roof_y + 26 + shy)
            show()
        else:
            hide()
    elif role == "plow":
        if rj_plow < 900:
            costume(join("plow_", frame % 2))
            goto(rj_plow + shx, roof_y + shy)
            show()
        else:
            hide()
    else:
        if RZ[zi] == 1:
            costume(join("zapw_", floor(frame / 3) % 2))
            goto(-300 + zi * 120 + shx, roof_y + shy)
            show()
        elif RZ[zi] == 2:
            costume(join("zapl_", frame % 3))
            goto(-300 + zi * 120 + shx, roof_y + shy)
            show()
        else:
            hide()
'''


TRACKPOST = spawner('post', '''
y = O_Y[oi]
period = O_A[oi]
offs = O_B[oi]
x = 999
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        ph = (frame + offs) % period
        if ph < 30:
            x = 999
        else:
            if ph == 30:
                sfxq.append("post")
            x = 262 - (ph - 30) * 14
            if x < -262:
                x = 999
            elif abs(x - px) < 12 and py < y + 42 and py + 34 > y:
                hit_player(2, 1, x + 30)


@on("t_draw")
def draw():
    if is_clone == 1:
        ph = (frame + offs) % period
        if ph < 30 and mode == "play":
            costume(join("warn_", floor(frame / 4) % 2))
            goto(222, y + 64)
            show()
        elif x < 900 and ph >= 30:
            costume("post")
            goto(x + shx, y + shy)
            show()
        else:
            hide()
'''

WARDEN = WARDEN.replace('if O_TYPE[oi] == "warden":', 'if O_TYPE[oi] == "warden" or O_TYPE[oi] == "shell":')


# Kuro, fought inside Hotaru's head. He mirrors her: her own 4-hit string,
# blink strikes from behind, and a Breach Phase Cut that she can answer
# with a Phase Step of her own (a Clash). In phase 2 he takes her controls
# and sends echoes of himself rushing along the floor.
KUROBOSS = spawner('kuro', '''
if kuro_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("kuro", x, y, 10, 38, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    fr = 0
    face = -1
    phase = 1
    flash_t = 0
    guard_t = 0
    guard_n = 0
    hit_t = 0
    acd = 30
    vis = 1
    last = 0
    flip_t = 0
    ke1 = 999
    ke2 = 999
    boss_hp = 20
    boss_int = 0
    is_clone = 1
    role = "body"
    clone()
    role = "echo1"
    clone()
    role = "echo2"
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1 and role == "body":
        kr_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        kr_draw()


@proc
def kr_face():
    if px > x:
        face = 1
    else:
        face = -1


@proc
def kr_go(kind):
    st = kind
    t = 0
    hitdone = 0
    nb = 0
    kr_face()
    if kind == "combo":
        sfxq.append("windup")
    elif kind == "cut":
        sfxq.append("breach")
    elif kind == "blink":
        sfxq.append("dash")
        mfx("afterimage", x, y, face)
    elif kind == "possess":
        sfxq.append("kuro")
        flip = 1
        flip_t = 150
        st = "combo"
    elif kind == "echo":
        ke1 = -228
        ke2 = 228
        e1hit = 0
        e2hit = 0
        sfxq.append("kuro")


@proc
def kr_strike(reach, dmg, last_hit):
    if face == 1:
        p_overlap(x - 6, x + reach, y + 2, y + 40)
    else:
        p_overlap(x - reach, x + 6, y + 2, y + 40)
    sfxq.append("muk_slash")
    if ov == 1:
        hit_player(dmg, 0, x)
        if res == "deflect":
            integ = min(imax, integ + 2)
            int_t = 0
            x = min(max(x - face * 4, -205), 205)
            if last_hit == 1:
                st = "recoil"
                t = 0


@proc
def kr_open():
    ko = 0
    if st == "recover" or st == "recoil" or st == "clashed" or st == "broken":
        ko = 1


@proc
def kr_update():
    t += 1
    if flip_t > 0:
        flip_t -= 1
        if flip_t == 0:
            flip = 0
    if st == "beaten":
        return
    if st == "wait":
        fr += 0.2
        if boss_on == 1:
            st = "move"
            t = 0
            acd = 40
        return
    # echoes rush along the floor (Breach: jump them or Phase Step through)
    if ke1 < 900:
        if st != "echo" or t >= 30:
            ke1 += 15
        if e1hit == 0 and abs(ke1 - px) < 14 and py < y + 30 and (st != "echo" or t >= 30):
            e1hit = 1
            hit_player(2, 1, ke1 - 20)
        if ke1 > 270:
            ke1 = 999
    if ke2 < 900:
        if st != "echo" or t >= 50:
            ke2 -= 15
        if e2hit == 0 and abs(ke2 - px) < 14 and py < y + 30 and (st != "echo" or t >= 50):
            e2hit = 1
            hit_player(2, 1, ke2 + 20)
        if ke2 < -270:
            ke2 = 999
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        st = "stagger2"
        t = 0
        vis = 1
        flash_t = 6
        sfxq.append("oni_hurt")
        if ehp <= 0:
            kr_beaten()
            return
    if ent_dmg[slot] > 0:
        kr_open()
        if ko == 1:
            ehp -= ent_dmg[slot]
            flash_t = 3
            sfxq.append("thug_hurt")
            if st != "broken":
                integ = min(imax, integ + ent_idmg[slot])
        elif vis == 1:
            sfxq.append("muk_guard")
            cfx("deflect", x + face * 12, y + 26, 0 - face)
            if ent_hk[slot] == "heavy":
                integ = min(imax, integ + ent_idmg[slot] * 0.5)
            if st == "move":
                guard_t = 8
                kr_face()
                guard_n += 1
                hit_t = 0
                if guard_n >= 4:
                    guard_n = 0
                    kr_go("blink")
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            kr_beaten()
            return
    if ehp <= 10 and phase == 1:
        phase = 2
        broadcast("ev_kuro_phase2")
    if integ >= imax and st != "broken" and st != "stagger2":
        st = "broken"
        t = 0
        vis = 1
        integ = imax
        ent_stag[slot] = 1
        flip = 0
        flip_t = 0
        sfxq.append("stagger")
    if guard_t > 0:
        guard_t -= 1
    dx = px - x
    ent_brk[slot] = 0
    if st == "move":
        kr_face()
        if acd > 0:
            acd -= 1
        ad = abs(dx)
        if acd == 0 and pst != "dead":
            roll = rand(1, 3 + 2 * (phase - 1))
            if roll == last:
                roll = roll % (3 + 2 * (phase - 1)) + 1
            if roll == 1 and ad > 70:
                roll = 2
            if roll == 4 and flip == 1:
                roll = 2
            last = roll
            if roll == 1:
                kr_go("combo")
            elif roll == 2:
                kr_go("blink")
            elif roll == 3:
                kr_go("cut")
            elif roll == 4:
                kr_go("possess")
            else:
                kr_go("echo")
        elif ad > 64:
            fr += 0.45
            x += face * 3.5
        elif ad < 34:
            x -= face * 1.5
    elif st == "combo":
        # her own string: slash, slash, thrust, heavy
        if t <= 16:
            ht = 12
            kk = "attack1"
        elif t <= 28:
            ht = 24
            kk = "attack2"
        elif t <= 40:
            ht = 36
            kk = "attack3"
        else:
            ht = 56
            kk = "heavy"
        if t == ht - 10:
            kr_face()
        if t >= ht - 8 and t < ht and abs(dx) > 40:
            x += face * 3
        if t == 12 or t == 24:
            kr_strike(50, 2, 0)
        elif t == 36:
            kr_strike(64, 2, 0)
        elif t == 56:
            kr_strike(58, 3, 1)
        if t >= 64 and st == "combo":
            kr_recover()
    elif st == "blink":
        if t < 14:
            vis = 0
        elif t == 14:
            vis = 1
            x = min(max(px - pface * 44, -205), 205)
            kr_face()
            sfxq.append("dash")
            mfx("afterimage", x, y, face)
        elif t == 26:
            kr_strike(50, 2, 1)
        if t >= 34 and st == "blink":
            if phase == 2 and nb == 0:
                nb = 1
                t = 0
                mfx("afterimage", x, y, face)
            else:
                kr_recover()
    elif st == "cut":
        if t < 30:
            ent_brk[slot] = 1
            kr_face()
            prel = px - x
        else:
            x += face * 16
            mfx("afterimage", x, y, face)
            rel = px - x
            if hitdone == 0 and rel * prel <= 0 and abs(py - y) < 40:
                hitdone = 1
                if pdash == 1:
                    # Clash: both Phase Step through each other
                    st = "clashed"
                    t = 0
                    integ = min(imax, integ + 6)
                    int_t = 0
                    sfxq.append("deflect")
                    sfxq.append("stagger")
                    cfx("deflect", (x + px) / 2, y + 20, 0)
                    hitstop = 8
                    shake = 10
                    shake_amp = 4
                else:
                    hit_player(3, 1, x - face * 10)
            prel = rel
            if (x <= -205 or x >= 205) and st == "cut":
                x = min(max(x, -205), 205)
                kr_recover()
    elif st == "echo":
        if t >= 100:
            kr_recover()
    elif st == "recover":
        if t >= rec_len:
            st = "move"
            t = 0
            acd = rand(10, 25) - 6 * (phase - 1)
    elif st == "recoil":
        if t >= 24:
            st = "recover"
            t = 0
            rec_len = 8
    elif st == "clashed":
        if t >= 60:
            st = "move"
            t = 0
            acd = 10
    elif st == "broken":
        if t >= 110:
            st = "move"
            t = 0
            integ = 8
            ent_stag[slot] = 0
            acd = 6
    elif st == "stagger2":
        if t >= 36:
            st = "move"
            t = 0
            acd = 16
    int_t += 1
    if int_t > 75 and integ > 0 and st != "broken" and t % 20 == 0:
        integ = max(0, integ - 1)
    hit_t += 1
    if hit_t > 40:
        guard_n = 0
    x = min(max(x, -205), 205)
    ent_x[slot] = x
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ


@proc
def kr_recover():
    st = "recover"
    t = 0
    vis = 1
    rec_len = 28 - 6 * (phase - 1)


@proc
def kr_beaten():
    st = "beaten"
    t = 0
    vis = 1
    ehp = 0
    flip = 0
    flip_t = 0
    ke1 = 999
    ke2 = 999
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("stagger")
    shake = 16
    shake_amp = 5
    hitstop = 12
    broadcast("ev_kuro_dead")


@proc
def kr_draw():
    effect("ghost", 0)
    effect("brightness", 0)
    if role == "echo1" or role == "echo2":
        if role == "echo1":
            ex = ke1
            point(90)
        else:
            ex = ke2
            point(-90)
        if ex < 900:
            costume(join("dash_", 1 + floor(frame / 2) % 2))
            effect("ghost", 45)
            if st == "echo" and ((role == "echo1" and t < 30) or (role == "echo2" and t < 50)) and frame % 6 < 3:
                effect("brightness", 100)
            goto(ex + shx, y + shy)
            show()
        else:
            hide()
        return
    if vis == 0:
        hide()
        return
    if st == "beaten":
        costume(join("overheat_", floor(t / 6) % 4))
    elif guard_t > 0:
        costume(join("deflect_", min(2, floor((8 - guard_t) / 3))))
    elif st == "wait":
        costume(join("idle_", floor(fr) % 4))
    elif st == "move":
        if abs(px - x) > 64:
            costume(join("run_", floor(fr) % 8))
        else:
            costume("block_0")
    elif st == "combo" or st == "blink":
        if st == "blink":
            ht = 26
            kk = "attack2"
        hf = t - ht
        if kk == "heavy":
            costume(join("heavy_", max(0, min(5, 3 + floor(hf / 4)))))
        elif hf < -6:
            costume(join(kk, "_0"))
        elif hf < 0:
            costume(join(kk, "_1"))
        elif hf < 3:
            costume(join(kk, "_2"))
        else:
            costume(join(kk, "_3"))
    elif st == "cut":
        if t < 30:
            costume("dash_0")
        else:
            costume(join("dash_", 1 + floor(t / 2) % 3))
    elif st == "echo":
        costume("block_0")
    elif st == "broken" or st == "clashed":
        costume(join("overheat_", floor(t / 5) % 4))
    elif st == "recover":
        costume(join("idle_", floor(t / 5) % 4))
    else:
        costume(join("hurt_", floor(t / 5) % 2))
    if st == "broken" or st == "clashed":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + shy)
    else:
        goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if (st == "combo" or st == "blink") and t >= ht - 9 and t <= ht:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    if st == "beaten" or vis == 1:
        show()
'''
