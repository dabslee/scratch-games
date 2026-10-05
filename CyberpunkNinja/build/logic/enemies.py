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
    if flash_t > 0:
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
    if flash_t > 0:
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
            elif st == "wind" and (hk == "heavy" or hk == "shuriken"):
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
        costume(join("death_", min(4, floor(fr))))
        if fr > 5:
            effect("ghost", (fr - 5) * 50)
    elif st == "idle":
        costume(join("idle_", floor(fr) % 4))
    elif st == "walk":
        costume(join("walk_", floor(fr) % 6))
    elif st == "wind":
        if t < 9:
            costume("attack_1")
        else:
            costume("attack_2")
    elif st == "swing":
        if t < 3:
            costume("attack_3")
        else:
            costume("attack_4")
    elif st == "recover":
        costume("attack_5")
    elif st == "stagger":
        costume("hurt_1")
    else:
        costume(join("hurt_", min(1, floor(t / 4))))
    if st == "stagger":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + z + shy)
    else:
        goto(x + shx, y + z + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    if flash_t > 0:
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
        if st != "broken":
            integ = min(imax, integ + ent_idmg[slot])
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
    if flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    else:
        effect("brightness", 0)
    show()
'''
