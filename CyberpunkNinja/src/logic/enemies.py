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
    skin = ""
    if chapter == 6:
        skin = "p_"
    elif chapter == 5:
        # memories of drones: a violet cast
        skin = "h_"
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
                    ehp -= dmg_out
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
        costume(join(skin, join("charge_", min(3, floor(fr)))))
    elif st == "dive":
        costume(join(skin, "charge_3"))
    else:
        costume(join(skin, join("hover_", floor(fr) % 4)))
    goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "dive" and hitdone == 0 and (sqrt((px - x) * (px - x) + (py + 18 - y) * (py + 18 - y)) - 19) / 8 < 9:
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
if not (oi in dead_objs) and not (O_A[oi] == "desk" and recep == 2):
    x = O_X[oi]
    y = O_Y[oi]
    brk_ok = O_A[oi]
    myobj = oi
    skin = ""
    pkind = "card"
    dr = 0
    ehp = 6
    imax = 8
    if O_TYPE[oi] == "drainling":
        dr = 1
        skin = "d_"
        ehp = 5
        imax = 6
    elif room == C_ROOM_E2:
        # the Slums memory: a Hannya Boy, not one of Kanshi's suits
        skin = "mg_"
    elif chapter == 5:
        skin = "m_"
    elif chapter >= 2:
        # from the casino floor on, the gang grunts wear suits
        skin = "u_"
        if chapter == 4:
            pkind = "bolt"
    add_ent("hannya", x, y, 10, 38, ehp, imax, 1)
    # the Spire Lobby's receptionist (brk_ok "desk") waits behind his desk, out of the fight,
    # until the lobby scene sends him over the counter
    waiting = 0
    if brk_ok == "desk" and recep == 0:
        waiting = 1
        # 2: not in the fight yet (his Stance bar waits with him)
        ent_alive[slot] = 2
    find_bounds()
    st = "idle"
    t = 0
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
    if brk_ok == "desk":
        recep = 2
        broadcast("ev_recep_dead")


@proc
def h_update():
    if waiting == 1:
        if recep == 0:
            return
        # over the counter
        waiting = 0
        ent_alive[slot] = 1
        face = -1
        acd = 30
        cfx("hit", x, y + 24, 0)
        sfxq.append("windup")
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
            x = min(max(x + face * (1.8 - 0.5 * dr), xmin), xmax)
        if dr == 1 and acd == 0 and pst != "dead" and (abs(dx) >= 70 or abs(py - y) >= 40):
            # Drainlings leap at mid range and spit sludge from afar
            t = 0
            hitdone = 0
            if abs(dx) < 150 and abs(py - y) < 40:
                st = "crouch"
                sfxq.append("windup")
            elif abs(dx) < 280:
                st = "spitw"
                sfxq.append("windup")
        elif abs(dx) < 54 and acd == 0 and abs(py - y) < 60 and pst != "dead":
            start_wind()
    elif st == "crouch":
        if t > 16:
            st = "leap"
            t = 0
            vz = 7
            sfxq.append("dash")
    elif st == "leap":
        x = min(max(x + face * 6, xmin), xmax)
        z += vz
        vz -= 1
        if hitdone == 0:
            p_overlap(x - 14, x + 14, y + z, y + z + 34)
            if ov == 1:
                hitdone = 1
                hit_player(2, 0, x)
                if res == "deflect":
                    integ = min(imax, integ + 2)
                    int_t = 0
                    vz = min(vz, 0)
                    x = min(max(x - face * 10, xmin), xmax)
        if z <= 0:
            z = 0
            st = "recover"
            t = 0
    elif st == "spitw":
        if t == 18:
            pq_t.append("spit")
            pq_x.append(x + face * 10)
            pq_y.append(y + 28)
            pq_vx.append(face * min(7, max(3, abs(dx) / 32)))
            pq_vy.append(min(8, max(2, 4 + (py - y) / 30)))
            sfxq.append("throw")
        if t >= 26:
            st = "recover"
            t = 0
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
            acd = rand(15, 40) + 20 * dr
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
    if waiting == 1:
        hide()
        return
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
    elif st == "crouch" or st == "spitw":
        if t < 10:
            costume(join(skin, "attack_1"))
        else:
            costume(join(skin, "attack_2"))
    elif st == "leap":
        costume(join(skin, "attack_3"))
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
    if (st == "wind" and t >= 15) or (st == "swing" and t == 0) or (st == "spitw" and t >= 9 and t <= 17):
        tell = 1
    if (st == "crouch" or st == "leap") and hitdone == 0:
        tth = max(0, abs(px - x) - 21) / 6
        if st == "crouch":
            tth += 17 - t
        if tth < 9:
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

HANNYA = HANNYA.replace('if O_TYPE[oi] == "hannya":', 'if O_TYPE[oi] == "hannya" or O_TYPE[oi] == "drainling":', 1)


ONI = spawner('oni', '''
if boss_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("oni", x, y, 26, 128, 20, 16, 1)
    boss_slot = slot
    boss_dmul = 0.5
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
    ha = 0
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
        if vuln == 1:
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
    if (st == "swing" and t >= 6 and t <= 14) or (st == "slam" and t >= 31 and t <= 39):
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
        # the throw (or shot) always faces Hotaru, windup included
        if dx > 0:
            face = 1
        else:
            face = -1
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
    if (st == "wind" and t >= 15) or (st == "swing" and t == 0):
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
    boss_dmul = 1.5
    p2_first = 0
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
    if phase == 2 and p2_first == 1:
        # phase 2 always opens on a Jackpot
        p2_first = 0
        slot_sym = "jackpot"
    elif phase == 2 and roll <= 22:
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
            to_spin()
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
        if vuln == 1 or hk == "projectile":
            # 20% more health
            ehp -= ent_dmg[slot] / 1.2
            flash_t = 3
        else:
            sfxq.append("clang")
            cfx("deflect", x + face * 12, y + 26, 0 - face)
            if hk == "heavy" and st != "jackpot":
                # a Heavy Strike doesn't cut through her guard, but it rocks her back
                st = "stagger"
                t = 0
                slot_state = "idle"
                sfxq.append("oni_hurt")
            else:
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
        p2_first = 1
        if st == "spin":
            # the reels are still turning: they land on the Jackpot
            slot_sym = "jackpot"
            p2_first = 0
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
    if st == "spin":
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
            to_spin()
    elif st == "recoil":
        if t >= 22:
            to_recover(30)
    elif st == "stagger":
        if t >= 20:
            to_recover(20)
    elif st == "broken":
        if t >= 110:
            to_spin()
            integ = 8
            ent_stag[slot] = 0
    elif st == "stagger2":
        if t >= 36:
            to_recover(20)
    if slot_state == "show":
        slot_t += 1
    int_t += 1
    if int_t > 75 and integ > 0 and st != "broken" and t % 20 == 0:
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
    if x < -200:
        x = -200
    if x > 200:
        x = 200
    ent_x[slot] = x
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ


@proc
def to_spin():
    st = "spin"
    t = 0
    pick_symbol()
    slot_state = "spin"
    slot_t = 0
    sfxq.append("reels")


@proc
def to_recover(n):
    st = "recover"
    t = 0
    rec_len = n
    slot_state = "idle"


@proc
def l_draw():
    effect("ghost", 0)
    if st == "dead":
        costume(join("death_", min(2, floor(fr))))
        effect("ghost", min(35, fr * 10))
    elif guard_t > 0:
        costume(join("deflect_", min(2, floor((8 - guard_t) / 3))))
    elif st == "wait" or st == "spin" or st == "jackpot":
        costume(join("idle_", floor(fr) % 4))
    elif st == "cherry":
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
    if st == "slash" and ((t >= 3 and t <= 11) or (t >= 21 and t <= 29)):
        tell = 1
    if st == "skull" and t >= 21 and t <= 29:
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
        if t < turn:
            x += vx
        else:
            x -= vx
        if t > turn * 2 or ent_alive[boss_slot] != 1:
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
            # Lady Luck's pair turns back short of the middle; the Daimyo's meet there
            turn = 75
            if chapter == 8:
                turn = abs(x) / 2.6
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
        # hollowed trainees in the Academy, hollowed soldiers in the Tenshu
        elite = 1
        skin = "s_"
        if chapter == 8:
            skin = "h_"
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / (6 + 2 * elite) / 2
        if integ < 0:
            integ = 0
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
    if st == "combo" and ((t >= 7 and t <= 15) or (nh == 2 and t >= 21 and t <= 29)):
        tell = 1
    if st == "heavy" and t >= 15 and t <= 23:
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


# Mukuro: Kuro's hollowed body. A pure deflect duel: he guards every blow
# outside his openings, so the way through is deflecting his strings to drain
# his Integrity, then punishing the recoveries. Mashing into his guard earns a
# counter, and so does staying greedy in an opening. Phase 1 baits early
# deflects with held strikes; phase 2 adds kunai, a diving slam and a shadow.
MUKURO = spawner('mukuro', '''
if muk_dead == 0:
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
    is_clone = 1
    role = "body"
    clone()
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
def m_pick(roll):
    if phase == 1:
        if roll <= 45:
            set_combo("c3")
        elif roll <= 72:
            set_combo("c2h")
        else:
            set_combo("delay")
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
        if sh_t >= 9 and sh_t <= 17:
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
    st = "beaten"
    t = 0
    muk_bx = x
    ehp = 0
    sh_x = 999
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("stagger")
    shake = 16
    shake_amp = 5
    hitstop = 12
    broadcast("ev_muk_dead")


@proc
def m_open():
    mo = 0
    if st == "recover" or st == "recoil" or st == "broken":
        mo = 1


@proc
def m_update():
    t += 1
    if st == "beaten":
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
            # twice the health
            ehp -= ent_dmg[slot] / 2
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
            if phase == 2 and rand(1, 2) == 1:
                set_combo("kunai")
            else:
                set_combo("lunge")
        elif ad > 62:
            fr += 0.4
            x += face * (2 + 2 * (ad > 120))
        elif acd == 0 and pst != "dead":
            m_pick(rand(1, 100))
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
        if t >= 26 - 10 * (phase - 1):
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
        # he slumps and stays down, unless Hotaru carries him off
        if muk_carry == 1:
            hide()
            return
        if t < 18:
            costume(join("death_", floor(t / 6)))
        else:
            costume("slump")
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
    elif st == "broken":
        costume(join("overheat_", floor(t / 5) % 4))
    elif st == "recover":
        costume(join("idle_", floor(t / 5) % 4))
    else:
        costume(join("hurt_", floor(t / 5) % 2))
    if st == "broken":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + shy)
    else:
        goto(x + shx, y + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if st == "combo" and ci > 0:
        if (h1 - t >= 1 and h1 - t <= 9) or (n >= 2 and h2 - t >= 1 and h2 - t <= 9) or (n >= 3 and h3 - t >= 1 and h3 - t <= 9) or (n >= 4 and h4 - t >= 1 and h4 - t <= 9):
            tell = 1
    if st == "kunai" and ((t >= 5 and t <= 13) or (phase == 2 and t >= 21 and t <= 29)):
        tell = 1
    if st == "shadow" and t >= 21 and t <= 29:
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
        # 60% more health
        if hk == "projectile":
            ehp -= ent_dmg[slot] / 1.6
            flash_t = 3
            sfxq.append("rj_hurt")
            if st != "overload":
                integ = min(imax, integ + ent_idmg[slot])
        elif rj_open == 1:
            # armor plating: melee on the open core does half damage
            ehp -= ent_dmg[slot] * 0.5 / 1.6
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
            if rj_arm - px >= 12 and (rj_arm - px - 12) / 11 < 9:
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
lt = 0
# in the Tenshu the crow holds off for 3 s after Hotaru comes in
hold = 90 * (chapter == 8)
ph = 0
is_clone = 1
clone()
is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        lt += 1
        if lt <= hold:
            ph = -1
            x = 999
            return
        if hold > 0:
            # after the hold its first pass starts with the warning
            ph = (lt - hold - 1) % period
        else:
            ph = (frame + offs) % period
        if ph < 30:
            x = 999
        else:
            if ph == 30:
                sfxq.append("post")
            x = 262 - (ph - 30) * 14
            if x < -262:
                x = 999
            elif abs(x - px) < 14 and py < y + 21 and py + 30 > y + 7:
                # a Kanshi crow skimming the roof: jump it or Phase Step through
                hit_player(2, 1, x + 30)


@on("t_draw")
def draw():
    if is_clone == 1:
        if ph >= 0 and ph < 30 and mode == "play":
            costume(join("warn_", floor(frame / 4) % 2))
            goto(222, y + 64)
            show()
        elif x < 900 and ph >= 30:
            costume(join("crow_", floor(frame / 3) % 2))
            goto(x + shx, y + 14 + shy + sin(frame * 40) * 2)
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
        sfxq.append("kvoice")
        flip = 1
        flip_t = 150
        st = "combo"
    elif kind == "echo":
        ke1 = -228
        ke2 = 228
        e1hit = 0
        e2hit = 0
        sfxq.append("kvoice")


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
    if st == "beaten" or st == "gone":
        return
    if st == "kneel":
        if ent_dmg[slot] > 0 and t < 24:
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
        elif ent_dmg[slot] > 0 and mode == "play":
            ent_dmg[slot] = 0
            ent_idmg[slot] = 0
            kbranch = 2
            st = "gone"
            t = 0
            ent_alive[slot] = 0
            sfxq.append("flatline")
            shake = 12
            shake_amp = 5
            broadcast("ev_kuro_dead")
        elif abs(px - x) < 54 and p_ground == 1 and mode == "play":
            prompt_on = 1
            prompt_x = x
            prompt_y = y + 64
            if pE == 1:
                kbranch = 1
                st = "beaten"
                t = 0
                ent_alive[slot] = 0
                sfxq.append("sync")
                broadcast("ev_kuro_dead")
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
    # each echo flashes for the 0.3 s before it reaches Hotaru (15/frame, 14 px)
    ke1_tell = 0
    ke2_tell = 0
    if ke1 < 900 and e1hit == 0 and px - ke1 >= 14:
        tth = 1 + floor((px - ke1 - 14) / 15)
        if st == "echo":
            tth = max(1, 30 - t) + floor((px - ke1 - 14) / 15)
        if tth <= 9:
            ke1_tell = 1
    if ke2 < 900 and e2hit == 0 and ke2 - px >= 14:
        tth = 1 + floor((ke2 - px - 14) / 15)
        if st == "echo":
            tth = max(1, 50 - t) + floor((ke2 - px - 14) / 15)
        if tth <= 9:
            ke2_tell = 1
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
            # 40% more health
            ehp -= ent_dmg[slot] / 1.4
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
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
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
    # Kuro kneels: Hotaru chooses (E to reach out, attack to destroy his mind)
    st = "kneel"
    t = 0
    vis = 1
    ehp = 0
    integ = 0
    flip = 0
    flip_t = 0
    ke1 = 999
    ke2 = 999
    ent_dmg[slot] = 0
    ent_idmg[slot] = 0
    ent_sev[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("stagger")
    shake = 16
    shake_amp = 5
    hitstop = 12
    broadcast("ev_kuro_choice")


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
            if (role == "echo1" and ke1_tell == 1) or (role == "echo2" and ke2_tell == 1):
                effect("brightness", 100)
            goto(ex + shx, y + shy)
            show()
        else:
            hide()
        return
    if vis == 0:
        hide()
        return
    if st == "beaten" or st == "kneel":
        costume(join("overheat_", floor(t / 6) % 4))
    elif st == "gone":
        # his mind comes apart in static
        costume(join("hurt_", floor(t / 2) % 2))
        effect("ghost", min(100, t * 3))
        if frame % 4 < 2:
            effect("brightness", 60)
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
    if st == "combo" and ((t >= 3 and t <= 11) or (t >= 15 and t <= 23) or (t >= 27 and t <= 35) or (t >= 47 and t <= 55)):
        tell = 1
    if st == "blink" and t >= 17 and t <= 25:
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    if st == "beaten" or vis == 1:
        show()
'''


# The Daimyo, in three forms. One sprite, several clone roles: the samurai
# exoskeleton (which also runs the brain for every phase), two castle turrets
# and the cables for phase 2, the Daimyo himself for phase 3, and Kuro in
# Mukuro's body, who fights beside Hotaru through the first two phases when he
# was spared. The boss hitbox follows whichever form is live.
DAIMYO = spawner('daimyo', '''
if daimyo_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    fy = y
    myobj = oi
    add_ent("daimyo", x, y, 16, 80, 20, 16, 1)
    boss_slot = slot
    boss_dmul = 1.3
    st = "wait"
    t = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    face = -1
    flash_t = 0
    guard_t = 0
    acd = 30
    cnt = 0
    dm_ph = 1
    dm_vul = 0
    eye_x = 0
    eye_y = fy
    mk_x = x
    mk_y = fy
    mk_st = "hidden"
    ally_x = 999
    ally_st = "fight"
    ally_hp = 1
    ally_lives = shards
    ally_rev = 0
    ally_inv = 0
    ally_def = 0
    ally_dash = 0
    exo_x = x
    exo_dark = 0
    jz = 0
    pat = 0
    dm_stage = 1
    dm_z = 0
    dm_hi = 1
    dm_lh = -99
    ally_shot = 0
    fy_floor = fy
    dm_st = "wait"
    dm_t = 0
    dm_fc = -1
    dm_tell = 0
    dm_fl = 0
    if kbranch == 1 and kuro_in == 1:
        ally_x = -230
    boss_hp = 20
    boss_int = 0
    is_clone = 1
    role = "body"
    clone()
    role = "tl"
    clone()
    role = "tr"
    clone()
    role = "cable"
    clone()
    role = "man"
    clone()
    role = "ally"
    at = 0
    ast = ""
    act_t = 0
    acool = 30
    aface = 1
    clone()
    role = "shard"
    clone()
    is_clone = 0
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if role == "body":
            dm_update()
        elif role == "ally":
            al_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        dm_draw()


@proc
def dm_face():
    if px > x:
        face = 1
    else:
        face = -1


@proc
def dm_go(kind):
    st = kind
    t = 0
    hitdone = 0
    nshot = 0
    prel = px - x
    dm_face()
    if kind == "stomp" or kind == "charge" or kind == "grab":
        sfxq.append("breach")
    elif kind == "iaido" or kind == "combo" or kind == "draw" or kind == "tempest":
        sfxq.append("windup")
    elif kind == "lasers":
        sl_q.append(-230)
        sl_q.append(230)
        sfxq.append("zap_warn")


@proc
def dm_rec(n):
    st = "recover"
    t = 0
    rec_len = n


@proc
def dm_slash(reach, dmg, last_hit, gain):
    if face == 1:
        p_overlap(x - 10, x + reach, y, y + 70)
    else:
        p_overlap(x - reach, x + 10, y, y + 70)
    sfxq.append("oni_swing")
    if ov == 1:
        hit_player(dmg, 0, x)
        if res == "deflect":
            integ = min(imax, integ + gain)
            int_t = 0
            if last_hit == 1:
                st = "recoil"
                t = 0
    elif ally_x < 900 and abs(ally_x - x) < reach + 10 and (ally_x - x) * face > 0:
        ally_hit(0)


@proc
def ally_hit(breach):
    # Kuro fights like Hotaru: he deflects most cuts and Phase Steps most Breaches
    if ally_inv > 0 or ally_dash > 0 or ally_st == "down" or ally_st == "fall" or ally_x > 900:
        return
    if breach == 0 and rand(1, 10) <= 6:
        sfxq.append("deflect")
        cfx("deflect", ally_x, fy + 30, 0 - face)
        integ = min(imax, integ + 1)
        int_t = 0
        ally_def = 9
        return
    if breach == 1 and rand(1, 10) <= 5:
        ally_dash = 8
        sfxq.append("dash")
        return
    ally_hurt()


@proc
def ally_hurt():
    if ally_inv > 0 or ally_st == "down" or ally_st == "fall":
        return
    ally_hp -= 1
    ally_inv = 30
    sfxq.append("thug_hurt")
    cfx("hit", ally_x, fy + 30, 0)
    if ally_hp <= 0:
        if ally_lives > 0:
            # a Memory Shard burns to put him back on his feet
            ally_lives -= 1
            ally_hp = 1
            ally_rev = 50
            broadcast("ev_kuro_revive")
            ally_inv = 50
            sfxq.append("sync")
            cfx("sync", ally_x, fy + 30, 0)
        else:
            ally_st = "down"
            sfxq.append("stagger")


@proc
def dm_hurt():
    # damage, guard and Stance for whichever form is live
    hk = ent_hk[slot]
    if dm_ph == 3 and st == "counter" and t >= 6 and hk != "projectile":
        # he was waiting for that: Tamakiri turns the blow and answers at once
        sfxq.append("deflect")
        cfx("deflect", x + face * 12, fy + 40, 0 - face)
        heat = min(16, heat + 6)
        hitstop = max(hitstop, 6)
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        dm_combo("riposte")
        return
    if dm_vul == 1 or hk == "projectile":
        ehp -= ent_dmg[slot]
        flash_t = 3
        if dm_ph == 3:
            sfxq.append("thug_hurt")
        else:
            sfxq.append("rj_hurt")
        if st != "broken":
            integ = min(imax, integ + ent_idmg[slot])
    else:
        sfxq.append("muk_guard")
        cfx("deflect", ent_x[slot] + face * 14, ent_y[slot] + 30, 0 - face)
        if hk == "heavy":
            integ = min(imax, integ + ent_idmg[slot] * 0.5)
        guard_t = 8
    int_t = 0
    ent_dmg[slot] = 0
    ent_idmg[slot] = 0


@proc
def dm_next_phase():
    integ = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    t = 0
    ehp = 20
    sfxq.append("rj_die")
    shake = 24
    shake_amp = 6
    hitstop = 14
    if dm_ph == 1:
        dm_ph = 2
        st = "rise"
        broadcast("ev_dm_phase2")
    elif dm_ph == 2:
        dm_ph = 3
        st = "emerge"
        exo_x = min(max(eye_x, -170), 170)
        mk_x = exo_x
        mk_st = "man"
        x = exo_x
        if ally_x < 900:
            ally_st = "fall"
            ally_rev = 0
            ally_inv = 0
            broadcast("ev_kuro_falls")
        broadcast("ev_dm_phase3")
    else:
        # beaten: he kneels through his last words; the stage sends him off (mk_st "dying")
        st = "end"
        ehp = 0
        mk_st = "kneel"
        ent_alive[slot] = 0
        boss_hp = 0
        boss_int = 0
        broadcast("ev_dm_dead")


@proc
def dm_update():
    t += 1
    if st == "end":
        if mk_st == "dying":
            mk_st = "dead"
            t = 0
        dm_publish()
        return
    if st == "wait":
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
        flash_t = 6
        sfxq.append("oni_hurt")
        if dm_ph == 2:
            st = "climb"
            t = 0
        else:
            dm_rec(30)
    if ally_shot > 0:
        ally_shot = 0
        ally_hurt()
    dm_vul = 0
    if st == "recover" or st == "recoil" or st == "broken" or st == "descend":
        dm_vul = 1
    if ent_dmg[slot] > 0:
        dm_hurt()
    if ehp <= 0 and st != "rise" and st != "emerge":
        dm_next_phase()
        return
    if integ >= imax and st != "broken":
        st = "broken"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        sfxq.append("stagger")
    if guard_t > 0:
        guard_t -= 1
    dx = px - x
    ent_brk[slot] = 0
    if dm_ph == 1:
        dm_exo()
    elif dm_ph == 2:
        dm_plug()
    else:
        dm_man()
    int_t += 1
    if int_t > 80 and integ > 0 and st != "broken" and t % 20 == 0:
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
    x = min(max(x, -200), 200)
    # hitboxes cover the whole figure: the mech stands about 150 tall, the eye is about 60 across, the man about 64
    if dm_ph == 1:
        ent_x[slot] = x
        ent_y[slot] = y
        ent_w[slot] = 26
        ent_h[slot] = 150
    elif dm_ph == 2:
        ent_x[slot] = eye_x
        ent_y[slot] = eye_y
        ent_w[slot] = 28
        ent_h[slot] = 58
    else:
        ent_x[slot] = x
        ent_y[slot] = fy + jz
        ent_w[slot] = 12
        ent_h[slot] = 52
        if flash_t > 0:
            flash_t -= 1
    ent_int[slot] = integ
    dm_publish()
    boss_hp = ceil(ehp)
    boss_int = integ


@proc
def dm_publish():
    # the man, the turrets and the cable are other clones: they draw from these
    dm_st = st
    dm_t = t
    dm_fc = face
    dm_fl = flash_t
    dm_z = jz
    dm_hi = hi
    dm_tell = 0
    if dm_ph == 3:
        if st == "draw" and hitdone == 0 and t < 34 and (t < 26 or (px - x) * face > 0):
            # frames to the hit: the dash moves 13 px a frame from t 26 and connects inside 30 px
            tth = max(1, 26 - t) + floor(max(0, abs(px - x) - 30) / 13)
            if tth <= 9:
                dm_tell = 1
        if (st == "cut3" or st == "storm" or st == "rend" or st == "riposte") and hi <= len(dm_hits):
            if dm_hits[hi] - t >= 1 and dm_hits[hi] - t <= 9:
                dm_tell = 1


@proc
def dm_combo(kind):
    # a string of cuts to deflect in rhythm; the last is heavy and, deflected, staggers him
    dm_go(kind)
    sfxq.append("windup")
    hi = 1
    dm_lh = -99
    dm_hits.clear()
    if kind == "cut3":
        # a 0.9 s windup, then da-da ... DA
        dm_hits.append(26)
        dm_hits.append(38)
        dm_hits.append(58)
    elif kind == "riposte":
        dm_hits.append(9)
    else:
        dm_hits.append(26)
        dm_hits.append(50)
        dm_hits.append(74)
        dm_hits.append(86)
        dm_hits.append(110)


@proc
def dm_hold():
    hold_x = min(max(x + face * 22, -210), 210)
    hold_y = fy + 8


@proc
def dm_pick():
    # his moves come in a set order with a little variation, so the duel has a rhythm
    ad = abs(px - x)
    pat += 1
    if rand(1, 4) == 1:
        pat += 1
    if dm_stage == 1:
        k = pat % 6
        if ad > 150 and k != 4:
            k = 1
        if k == 0 or k == 3:
            dm_combo("cut3")
        elif k == 1 or k == 5:
            dm_go("draw")
        elif k == 2:
            dm_go("counter")
            sfxq.append("muk_guard")
        else:
            dm_go("grab")
    else:
        k = pat % 7
        if ad > 160 and (k == 0 or k == 4):
            k = 1
        if k == 0:
            dm_combo("cut3")
        elif k == 1 or k == 6:
            dm_go("tempest")
        elif k == 2:
            dm_go("draw")
        elif k == 3:
            dm_go("counter")
            sfxq.append("muk_guard")
        elif k == 4:
            dm_combo("rend")
        else:
            dm_go("grab")


@proc
def dm_exo():
    # phase 1: the samurai mech
    if st == "move":
        dm_face()
        if acd > 0:
            acd -= 1
        ad = abs(dx)
        if acd == 0 and pst != "dead" and ally_x < 900 and ally_st != "fall" and ally_st != "down" and rand(1, 3) == 1:
            # he turns on Kuro: his swings land on the other side, an opening for Hotaru
            dm_go("iaido")
            if ally_x > x:
                face = 1
            else:
                face = -1
        elif acd == 0 and pst != "dead":
            roll = rand(1, 4)
            if roll == last:
                roll = roll % 4 + 1
            last = roll
            if ad > 120 and roll == 2:
                roll = 1
            if roll == 1:
                dm_go("iaido")
            elif roll == 2:
                dm_go("combo")
            elif roll == 3:
                dm_go("stomp")
            else:
                dm_go("charge")
        elif ad > 90:
            x += face * 1.6
    elif st == "iaido":
        if t == 26:
            dm_slash(130, 3, 1, 3)
        if t >= 40 and st == "iaido":
            dm_rec(30)
    elif st == "combo":
        # a 0.9 s windup like the iaido, then three cuts half a second apart (t 26, 42, 58)
        if t == 17 or t == 33 or t == 49:
            dm_face()
        if (t > 17 and t < 26) or (t > 33 and t < 42) or (t > 49 and t < 58):
            if abs(dx) > 50:
                x += face * 2.5
        if t == 26 or t == 42:
            dm_slash(84, 2, 0, 2)
        elif t == 58:
            dm_slash(84, 2, 1, 2)
        if t >= 68 and st == "combo":
            dm_rec(24)
    elif st == "stomp":
        if t < 30:
            ent_brk[slot] = 1
        if t == 30:
            sfxq.append("oni_slam")
            cfx("shockwave", x, fy, 0)
            shake = 12
            shake_amp = 5
            for k in range(2):
                pq_t.append("wave")
                pq_x.append(x)
                pq_y.append(fy)
                pq_vx.append(7 - 14 * k)
                pq_vy.append(0)
            if abs(dx) < 54 and py < fy + 30:
                hit_player(3, 1, x)
            if abs(ally_x - x) < 70:
                ally_hit(1)
        if t >= 46:
            dm_rec(30)
    elif st == "charge":
        if t < 30:
            # facing is fixed when the warning starts (dm_go): he dashes that way
            ent_brk[slot] = 1
            prel = px - x
        else:
            x += face * 14
            if t % 2 == 0:
                mfx("afterimage", x, y + 30, face)
            rel = px - x
            if hitdone == 0 and rel * prel <= 0 and py < y + 70:
                hitdone = 1
                hit_player(3, 1, x - face * 10)
            prel = rel
            if ally_x < 900 and abs(ally_x - x) < 16:
                ally_hit(1)
            if (x <= -200 or x >= 200) and st == "charge":
                shake = 8
                shake_amp = 4
                sfxq.append("oni_slam")
                dm_rec(34)
    elif st == "recover":
        if t >= rec_len:
            st = "move"
            t = 0
            acd = rand(8, 24)
    elif st == "recoil":
        if t >= 28:
            dm_rec(8)
    elif st == "broken":
        if t >= 110:
            st = "move"
            t = 0
            integ = 8
            ent_stag[slot] = 0
            acd = 8


@proc
def dm_plug():
    # phase 2: the mech's eye wires itself into the Tenshu; the castle's turrets do the fighting
    if st == "rise":
        eye_y = min(-40, eye_y + 5)
        if eye_y >= -40 and t > 50:
            st = "float"
            t = 0
            cnt = 0
        return
    if st == "float" or st == "barrage" or st == "lasers":
        eye_x = sin(frame * 1.6) * 120
        eye_y = -40 + sin(frame * 5) * 5
    if st == "float":
        if t >= 40:
            cnt += 1
            if cnt % 4 == 0:
                st = "descend"
                t = 0
                sfxq.append("vent")
            elif cnt % 4 == 2:
                dm_go("lasers")
            else:
                dm_go("barrage")
    elif st == "barrage":
        # the wall turrets fire in turn; deflected rounds fly back into the eye
        if t % 14 == 8 and nshot < 4:
            nshot += 1
            tsx = 224
            if nshot % 2 == 1:
                tsx = -224
            # every other volley goes for Kuro while he stands
            tgx = px
            tgy = py + 18
            if nshot % 2 == 0 and ally_x < 900 and ally_st != "down" and ally_st != "fall":
                tgx = ally_x
                tgy = fy + 30
            for k in range(3):
                ax = tgx - tsx
                ay = tgy - 30
                dd = sqrt(ax * ax + ay * ay) + 0.01
                ang = (k - 1) * 8
                vx0 = ax / dd * 6
                vy0 = ay / dd * 6
                pq_t.append("bullet")
                pq_x.append(tsx)
                pq_y.append(30)
                pq_vx.append(vx0 * cos(ang) - vy0 * sin(ang))
                pq_vy.append(vx0 * sin(ang) + vy0 * cos(ang))
            sfxq.append("turret_fire")
        if t >= 70:
            st = "float"
            t = 0
    elif st == "lasers":
        if t >= 150:
            st = "float"
            t = 0
    elif st == "descend":
        # it drops to the floor to recharge: the opening
        eye_y = max(fy, eye_y - 7)
        if t >= 130:
            st = "climb"
            t = 0
    elif st == "broken":
        eye_y = max(fy, eye_y - 7)
        if t >= 120:
            ent_stag[slot] = 0
            integ = 6
            st = "climb"
            t = 0
    elif st == "climb":
        eye_y = min(-40, eye_y + 5)
        if eye_y >= -40:
            st = "float"
            t = 0


@proc
def dm_man():
    # phase 3: the Daimyo in person, with Tamakiri
    if st == "emerge":
        # the eye crashes to the floor where it hung, and he steps out of it
        eye_y = max(fy, eye_y - 8)
        if t == 30:
            x = exo_x + 26
            sfxq.append("vent")
        mk_x = x
        if t >= 60:
            st = "move"
            t = 0
            acd = 30
        return
    eye_y = fy
    exo_dark = min(45, exo_dark + 1)
    if dm_stage == 1 and ehp <= 10 and st == "move":
        # halfway down he plants his feet and stops holding back
        dm_stage = 2
        dm_go("kiai")
    if st == "move":
        dm_face()
        if acd > 0:
            acd -= 1
        if acd == 0 and pst != "dead":
            dm_pick()
        elif abs(dx) > 80:
            x += face * (2.6 + 0.8 * (dm_stage == 2))
    elif st == "kiai":
        if t == 2:
            sfxq.append("breach")
            flash = 24
            shake = 16
            shake_amp = 4
        if t >= 40:
            st = "move"
            t = 0
            acd = 10
    elif st == "cut3" or st == "storm" or st == "rend" or st == "riposte":
        if hi <= len(dm_hits):
            nh = dm_hits[hi]
            if nh - t > 7:
                dm_face()
                if abs(px - x) > 46:
                    x += face * 3.2
            if st == "rend" and hi > 1 and nh - t == 12:
                # he blinks to Hotaru's other side between cuts
                mfx("afterimage", x, fy + 30, face)
                x = min(max(px + face * 40, -200), 200)
                sfxq.append("dash")
                dm_face()
            if t == nh:
                lh = 0
                dd = 2
                if hi == len(dm_hits):
                    lh = 1
                    dd = 3
                dm_lh = t
                dm_slash(66, dd, lh, 2)
                hi += 1
        elif t >= dm_hits[len(dm_hits)] + 14:
            if st == "riposte":
                dm_rec(24)
            else:
                dm_rec(34)
    elif st == "draw":
        # iaido: a 0.9 s draw, then a dash-cut along the floor
        if t < 26:
            dm_face()
            prel = px - x
        elif t < 34:
            x += face * 13
            if t % 2 == 0:
                mfx("afterimage", x, fy + 30, face)
            rel = px - x
            if hitdone == 0 and (rel * prel <= 0 or abs(rel) < 30) and py < fy + 40:
                hitdone = 1
                hit_player(3, 0, x - face * 10)
                if res == "deflect":
                    integ = min(imax, integ + 3)
                    # a short stagger: 9 frames, then 8 open (half the old 34)
                    st = "recoil"
                    t = 17
            prel = rel
        elif t >= 52 and st == "draw":
            dm_rec(13)
    elif st == "counter":
        # Tamakiri raised and waiting; hold off and he lowers it, open
        if t >= 46:
            dm_rec(7)
    elif st == "grab":
        # the soul grab: a Breach; if it connects it fills Hotaru's Stance
        if t < 24:
            ent_brk[slot] = 1
            dm_face()
        elif t < 34:
            x += face * 12
            if hitdone == 0 and abs(px - x) < 24 and py < fy + 40:
                hitdone = 1
                if pinv == 0 and pdash == 0 and pst != "dead" and pst != "cut" and pst != "reboot":
                    # caught: he holds her up for a second, draining her, then throws her
                    st = "hold"
                    t = 0
                    dm_hold()
                    if pparry > 0 or (pblock == 1 and (x - px) * pface >= 0):
                        hq_t.append("guardbreak")
                        hq_d.append(0)
                        hq_x.append(x)
                    hq_t.append("held")
                    hq_d.append(0)
                    hq_x.append(x)
                    sfxq.append("kvoice")
        elif t >= 52:
            dm_rec(15)
    elif st == "hold":
        dm_hold()
        if pst != "held":
            dm_rec(15)
        elif t == 5 or t == 15 or t == 25:
            # 3 damage and 9 Stance over the second, and every point of it heals him
            hq_t.append("squeeze")
            hq_d.append(boss_dmul)
            hq_x.append(x)
            ehp = min(20, ehp + 1)
            cfx("heal", x, fy + 40, face)
            sfxq.append("heal")
        elif t >= 30:
            hq_t.append("thrown")
            hq_d.append(0)
            hq_x.append(x)
            sfxq.append("oni_swing")
            st = "throw"
            t = 0
    elif st == "throw":
        if t >= 10:
            dm_rec(15)
    elif st == "tempest":
        # he leaps, spins in the air and throws three slash waves at Hotaru, then lands open
        if t < 12:
            dm_face()
        elif t < 30:
            jz = min(84, jz + 8)
            x += (0 - x) * 0.04
        elif t < 72:
            jz = 84
            dm_face()
            if t == 32:
                sfxq.append("oni_swing")
            if t == 38 or t == 50 or t == 62:
                ax = px - x
                ay = py + 18 - (fy + jz + 30)
                dd = sqrt(ax * ax + ay * ay) + 0.01
                pq_t.append("crescent")
                pq_x.append(x + face * 10)
                pq_y.append(fy + jz + 30)
                pq_vx.append(ax / dd * 5.5)
                pq_vy.append(ay / dd * 5.5)
                sfxq.append("muk_slash")
        elif t < 88:
            jz = max(0, jz - 10)
        else:
            jz = 0
            if t == 88:
                sfxq.append("oni_slam")
                shake = 10
                shake_amp = 4
            if t >= 92:
                dm_rec(46)
    elif st == "recover":
        if t >= rec_len:
            st = "move"
            t = 0
            if dm_stage == 1:
                acd = rand(16, 28)
            else:
                acd = rand(8, 16)
    elif st == "recoil":
        if t >= 26:
            dm_rec(8)
    elif st == "broken":
        jz = 0
        if t >= 100:
            st = "move"
            t = 0
            integ = 8
            ent_stag[slot] = 0
            acd = 8
    mk_x = x


@proc
def al_update():
    # Kuro, wearing his own body again, fights the armor the way Hotaru does
    at += 1
    if ally_x > 900:
        return
    if dm_ph >= 3:
        ally_st = "fall"
    if ally_st == "fall" or ally_st == "down":
        # down for good: no shard burning over him, no flashing
        ally_rev = 0
        ally_inv = 0
        ally_dash = 0
        return
    if boss_on == 0:
        return
    if ally_inv > 0:
        ally_inv -= 1
    if ally_rev > 0:
        ally_rev -= 1
    if ally_def > 0:
        ally_def -= 1
    if ally_dash > 0:
        ally_dash -= 1
        ally_x = min(max(ally_x + aface * 7, -205), 205)
        if ally_dash % 2 == 0:
            mfx("afterimage", ally_x, fy + 30, aface)
        return
    bx2 = ent_x[boss_slot]
    reach_ok = abs(ent_y[boss_slot] - fy) < 40
    if ast == "atk":
        # a three-cut string into an opening
        act_t += 1
        if act_t == 6 or act_t == 18:
            sfxq.append("muk_slash")
            if abs(bx2 - ally_x) < 64 and reach_ok:
                ent_dmg[boss_slot] = ent_dmg[boss_slot] + 0.25
                ent_idmg[boss_slot] = ent_idmg[boss_slot] + 0.5
                ent_hk[boss_slot] = "ally"
                cfx("hit_enemy", bx2 - aface * 6, fy + 50, aface)
        if act_t >= 28:
            ast = ""
            acool = 30
        return
    if ast == "heavy":
        # Phase Step in, then a Heavy Strike into the guard to build Stance
        act_t += 1
        if act_t < 8:
            ally_x = min(max(ally_x + aface * 6, -205), 205)
            if act_t % 2 == 0:
                mfx("afterimage", ally_x, fy + 30, aface)
        if act_t == 12:
            sfxq.append("muk_slash")
            if abs(bx2 - ally_x) < 70 and reach_ok:
                ent_dmg[boss_slot] = ent_dmg[boss_slot] + 0.25
                ent_idmg[boss_slot] = ent_idmg[boss_slot] + 1.5
                ent_hk[boss_slot] = "heavy"
                cfx("hit_enemy", bx2 - aface * 6, fy + 50, aface)
        if act_t >= 26:
            ast = ""
            acool = 40
        return
    # flank: take the side away from Hotaru so the armor has to split its attention
    if px < bx2:
        want = bx2 + 50
    else:
        want = bx2 - 50
    if want > 200 or want < -200:
        want = bx2 * 2 - want
    if abs(want - ally_x) > 6:
        if want > ally_x:
            ally_x += 3
            aface = 1
        else:
            ally_x -= 3
            aface = -1
        ally_st = "run"
    else:
        ally_st = "fight"
        if bx2 > ally_x:
            aface = 1
        else:
            aface = -1
        if acool > 0:
            acool -= 1
        elif reach_ok and dm_vul == 1:
            ast = "atk"
            act_t = 0
        elif reach_ok and rand(1, 150) == 1:
            ast = "heavy"
            act_t = 0


@proc
def dm_draw():
    effect("ghost", 0)
    effect("brightness", 0)
    if role == "body":
        # phase 1: the mech's frames run at 12 a second (2.5 game frames each)
        if dm_ph == 2:
            # the eye wired into the castle: shut while it floats and the castle fires,
            # open while it lies on the floor recharging, so it's the eye Hotaru hits
            if st == "descend":
                if t < 8 or t > 116:
                    costume("eye_half")
                else:
                    costume("eye_open")
            elif st == "broken":
                costume("eye_open")
            elif st == "rise" or st == "climb":
                costume("eye_half")
            else:
                costume("eye_shut")
        elif dm_ph == 3:
            # the dead eye stays where it fell, going dark behind the duel
            costume("eye_shut")
            effect("brightness", -20 - exo_dark)
        elif st == "wait" and boss_on == 0:
            costume("mech_idle_0")
        elif st == "iaido":
            if t < 23:
                costume(join("mech_windup_", min(2, floor(t / 2.5))))
            else:
                costume(join("mech_slash_", min(3, floor((t - 23) / 2.5))))
        elif st == "combo":
            # the windup (sword raised), then three cuts landing at t 26, 42 and 58
            if t < 17:
                costume(join("mech_windup_", min(2, floor(t / 2.5))))
            else:
                u = t - 17 - min(2, floor((t - 17) / 16)) * 16
                if u < 6:
                    costume("mech_windup_2")
                else:
                    costume(join("mech_slash_", min(3, floor((u - 6) / 2.5))))
        elif st == "stomp":
            # crouch, leap, and come down on the shockwave at t 30
            if t < 30:
                costume(join("mech_stomp_", min(4, floor(t / 6))))
            else:
                costume("mech_stomp_5")
        elif st == "charge":
            if t < 30:
                costume(join("mech_charge_", min(1, floor(t / 10))))
            else:
                costume(join("mech_dash_", floor(t / 2.5) % 2))
        elif st == "broken":
            costume("mech_kneel_0")
        elif st == "recoil":
            costume("mech_hurt_0")
        elif guard_t > 0:
            costume("mech_low_0")
        elif st == "move" and abs(px - x) > 90:
            costume(join("mech_walk_", floor(frame / 2.5) % 8))
        else:
            costume(join("mech_idle_", floor(frame / 7.5) % 4))
        tell = 0
        if dm_ph == 1:
            if st == "iaido" and t >= 17 and t <= 25:
                tell = 1
            if st == "combo" and ((t >= 17 and t <= 25) or (t >= 33 and t <= 41) or (t >= 49 and t <= 57)):
                tell = 1
        if tell == 1:
            effect("brightness", 100)
        elif flash_t > 0 and dm_ph <= 2:
            flash_t -= 1
            effect("brightness", 60)
        elif dm_ph == 2 and st == "descend":
            effect("brightness", 25 * (frame % 10 < 5))
        if face == 1:
            point(90)
        else:
            point(-90)
        if dm_ph == 2:
            if px > eye_x:
                point(90)
            else:
                point(-90)
            goto(eye_x + shx, eye_y + shy)
        elif dm_ph == 3:
            point(90)
            goto(exo_x + shx, eye_y + shy)
        elif st == "broken":
            goto(x + shx + (frame % 4 < 2) * 2 - 1, y + shy)
        else:
            goto(x + shx, y + shy)
        show()
    elif role == "tl" or role == "tr":
        if dm_ph == 2:
            costume("turret")
            if role == "tl":
                point(90)
                goto(-226 + shx, 30 + shy)
            else:
                point(-90)
                goto(226 + shx, 30 + shy)
            if st == "barrage":
                effect("brightness", 40 * (t % 14 > 4))
            show()
        else:
            hide()
    elif role == "cable":
        if dm_ph == 2:
            costume("cable")
            goto(eye_x + shx, eye_y + 58 + shy)
            show()
        else:
            hide()
    elif role == "man":
        if mk_st == "man" or mk_st == "dead" or mk_st == "kneel" or mk_st == "dying":
            if mk_st == "dead":
                # up off his knees only to let Tamakiri fall; he crumbles to ash, then he's gone
                if dm_t >= 66:
                    hide()
                    return
                costume(join("dmf_death_", min(27, 13 + floor(dm_t / 3))))
                effect("ghost", max(0, (dm_t - 44) * 5))
            elif mk_st == "kneel" or mk_st == "dying":
                if dm_t < 8:
                    costume(join("dmf_kneel_stunned_", floor(dm_t / 4)))
                else:
                    costume(join("dmf_kneel_stunned_", 2 + floor(dm_t / 5) % 6))
            elif dm_st == "emerge":
                if dm_t < 30:
                    hide()
                    return
                costume("dmf_idle_0")
                effect("ghost", max(0, 100 - (dm_t - 30) * 5))
            elif dm_st == "draw":
                if dm_t < 26:
                    costume("dmf_dash_0")
                elif dm_t < 34:
                    costume(join("dmf_dash_", 1 + floor((dm_t - 26) / 3) % 3))
                elif dm_t < 42:
                    costume("dmf_dash_4")
                else:
                    costume("dmf_dash_5")
            elif dm_st == "riposte" and dm_t < 6:
                costume(join("dmf_parry_", 2 + floor(dm_t / 3)))
            elif dm_st == "cut3" or dm_st == "storm" or dm_st == "rend" or dm_st == "riposte":
                if dm_t - dm_lh < 9:
                    costume(join("dmf_slash_", 2 + floor((dm_t - dm_lh) / 3)))
                elif dm_hi <= len(dm_hits) and dm_hits[dm_hi] - dm_t <= 6:
                    costume("dmf_slash_1")
                elif dm_hi <= len(dm_hits) and dm_hits[dm_hi] - dm_t <= 12:
                    costume("dmf_slash_0")
                else:
                    costume("dmf_slash_5")
            elif dm_st == "counter":
                if dm_t < 6:
                    costume("dmf_parry_0")
                elif dm_t < 40:
                    costume("dmf_parry_1")
                else:
                    costume(join("dmf_parry_", min(5, 4 + floor((dm_t - 40) / 4))))
            elif dm_st == "kiai":
                costume("dmf_parry_1")
            elif dm_st == "grab":
                if dm_t < 12:
                    costume("dmf_grab_0")
                elif dm_t < 24:
                    costume("dmf_grab_1")
                elif dm_t < 29:
                    costume("dmf_grab_2")
                elif dm_t < 34:
                    costume("dmf_grab_3")
                elif dm_t < 44:
                    costume("dmf_grab_4")
                else:
                    costume("dmf_grab_5")
            elif dm_st == "hold":
                costume(join("dmf_grab_", 2 + floor(dm_t / 4) % 2))
            elif dm_st == "throw":
                costume(join("dmf_grab_", 4 + (dm_t >= 5)))
            elif dm_st == "tempest":
                if dm_t < 12:
                    costume(join("dmf_jump_", floor(dm_t / 6)))
                elif dm_t < 30:
                    costume(join("dmf_jump_", min(4, 2 + floor((dm_t - 12) / 6))))
                elif dm_t < 72:
                    costume(join("dmf_whirlwind_", 1 + floor(dm_t / 3) % 4))
                elif dm_t < 88:
                    costume(join("dmf_jump_", 5 + floor((dm_t - 72) / 8)))
                else:
                    costume("dmf_jump_7")
            elif dm_st == "broken":
                if dm_t < 8:
                    costume(join("dmf_kneel_stunned_", floor(dm_t / 4)))
                else:
                    costume(join("dmf_kneel_stunned_", 2 + floor(dm_t / 5) % 6))
            elif dm_st == "recoil":
                costume(join("dmf_hurt_", 2 + floor(dm_t / 6) % 2))
            elif dm_st == "move" and abs(px - mk_x) > 80:
                costume(join("dmf_run_", floor(frame / 3) % 8))
            else:
                costume(join("dmf_idle_", floor(frame / 5) % 12))
            if mk_st != "man":
                effect("brightness", 0)
            elif dm_tell == 1:
                effect("brightness", 100)
            elif dm_fl > 0:
                effect("brightness", 60)
            elif dm_st == "grab" and dm_t < 24:
                effect("brightness", 40 * (frame % 6 < 3))
            elif dm_st == "kiai":
                effect("brightness", 50 * (frame % 4 < 2))
            if dm_fc == 1:
                point(90)
            else:
                point(-90)
            if dm_st == "broken" and dm_t > 8:
                goto(mk_x + shx + (frame % 4 < 2) * 2 - 1, fy + shy)
            else:
                goto(mk_x + shx, fy + dm_z + shy)
            show()
        else:
            hide()
    elif role == "shard":
        # a Memory Shard burning away over Kuro as it puts him back on his feet
        if ally_rev > 0 and ally_x < 900 and kuro_in == 1 and ally_st != "fall" and ally_st != "down":
            costume(join("shard_", floor(frame / 3) % 6))
            goto(ally_x + shx, fy + 76 + (50 - ally_rev) * 1.2 + shy)
            effect("ghost", max(0, 60 - ally_rev * 2))
            effect("brightness", 30)
            show()
        else:
            hide()
    else:
        # Kuro, in Mukuro's body
        if ally_x < 900 and kuro_in == 1:
            if ally_st == "fall" or ally_st == "down":
                costume("mk_lie")
            elif ally_dash > 0 or (ast == "heavy" and act_t < 8):
                costume(join("mk_dash_", min(3, floor(frame / 2) % 4)))
            elif ast == "heavy":
                costume(join("mk_heavy_", min(5, floor((act_t - 8) / 3))))
            elif ast == "atk":
                costume(join(join("mk_attack", min(3, floor(act_t / 10) + 1)), join("_", min(3, floor((act_t % 10) / 3)))))
            elif ally_def > 0:
                costume(join("mk_deflect_", min(2, floor((9 - ally_def) / 3))))
            elif ally_inv > 20 and ally_rev == 0:
                costume(join("mk_hurt_", floor(frame / 4) % 2))
            elif ally_st == "run":
                costume(join("mk_run_", floor(frame / 3) % 8))
            else:
                costume(join("mk_idle_", floor(frame / 8) % 4))
            effect("color", 160)
            if ally_rev > 0:
                effect("brightness", 50 * (frame % 6 < 3))
            elif ally_inv > 0:
                effect("ghost", 40 * (frame % 4 < 2))
            if aface == 1:
                point(90)
            else:
                point(-90)
            goto(ally_x + shx, fy + shy)
            show()
        else:
            hide()
'''


# Dobunushi: a mass of Drainlings fused around a broken Kanshi outflow pipe.
# The body never moves; its two arms do the fighting. An arm rears up over
# Hotaru, then slams down: deflect the slam and the arm is pinned, open to
# cuts until its Stance breaks and it can be cut off. With both arms gone the
# core opens until the arms regrow. The body raises the sludge tide in waves,
# and in phase 2 it spews a Breach wave along the floor.
DOBU = spawner('dobu', '''
if dobu_dead == 0:
    bx = O_X[oi]
    by = O_Y[oi]
    x = bx
    y = by
    myobj = oi
    add_ent("dobu", bx, by + 30, 24, 60, 20, 10, 1)
    boss_slot = slot
    cslot = slot
    st = "wait"
    t = 0
    ehp = 20
    imax = 10
    integ = 0
    int_t = 0
    flash_t = 0
    guard_t = 0
    tcyc = 0
    boss_hp = 20
    boss_int = 0
    dobu_cut = 0
    dobu_gen = 0
    dobu_ph = 1
    dobu_open = 0
    dobu_turn = 0
    spew_first = 0
    tide_force = 1
    tide_lvl = 0
    is_clone = 1
    role = "body"
    clone()
    ui_slot.append(slot)
    ui_role.append("mark")
    clone("EnemyUI")
    st = ""
    t = 0
    for k in range(2):
        role = "arm"
        side = k * 2 - 1
        add_ent("dobu_arm", bx + side * 120, -999, 14, 20, 6, 6, 1)
        aslot = slot
        clone()
        ui_slot.append(slot)
        ui_role.append("bar")
        clone("EnemyUI")
        ui_slot.append(slot)
        ui_role.append("mark")
        clone("EnemyUI")
    is_clone = 0
''') + '''
@on("t_world")
def tick():
    if is_clone == 1:
        if role == "body":
            db_update()
        else:
            da_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        if role == "body":
            db_draw()
        else:
            da_draw()


# ---------------------------------------------------------------- the body and core
@proc
def db_update():
    t += 1
    if st == "beaten":
        tide_lvl = max(0, tide_lvl - 0.02)
        return
    if st == "wait":
        if boss_on == 1:
            st = "closed"
            t = 0
        return
    # the tide: every few seconds the sludge comes up over the floor
    tcyc += 1
    tper = 420 - 90 * (dobu_ph - 1)
    tc = tcyc % tper
    # the same warning as the Sewers' pump rooms: the plate flashes and the pumps gurgle
    tide_warn = 0
    if tc >= tper - 255 and tc < tper - 200:
        tide_warn = 1
    if tc == tper - 255:
        sfxq.append("gurgle")
        shake = 20
        shake_amp = 2
    if tc < tper - 200:
        tide_lvl = max(0, tide_lvl - 0.025)
    elif tc < tper - 140:
        tide_lvl = min(1, tide_lvl + 1 / 60)
    elif tc < tper - 50:
        tide_lvl = 1
    else:
        tide_lvl = max(0, tide_lvl - 1 / 50)
    if ent_sev[cslot] == 1:
        ent_sev[cslot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[cslot] = 0
        flash_t = 8
        sfxq.append("oni_hurt")
        shake = 10
        shake_amp = 5
        if ehp <= 0:
            db_beaten()
            return
        db_close()
    if ent_dmg[cslot] > 0 or ent_idmg[cslot] > 0:
        if st == "open":
            # 20% more health
            ehp -= ent_dmg[cslot] / 1.2
            integ = min(imax, integ + ent_idmg[cslot])
            flash_t = 3
            sfxq.append("thug_hurt")
            int_t = 0
        else:
            # the closed mass shrugs blows off, but they still wear on its Stance
            # (as do cuts to its arms, which arrive here as Stance alone)
            integ = min(imax, integ + ent_idmg[cslot] * 0.5)
            int_t = 0
            if ent_dmg[cslot] > 0:
                guard_t = 6
                sfxq.append("muk_guard")
                cfx("deflect", px + pface * 12, py + 24, 0 - pface)
        ent_dmg[cslot] = 0
        ent_idmg[cslot] = 0
        if ehp <= 0:
            db_beaten()
            return
    if ehp <= 10 and dobu_ph == 1:
        dobu_ph = 2
        # the shorter phase 2 cycle starts over, so the tide doesn't jump to high
        tcyc = 0
        # phase 2 opens with the spew: the arms hold off until it's out
        spew_first = 1
        dobu_turn = 9
        broadcast("ev_dobu_phase2")
    if integ >= imax and ent_stag[cslot] == 0:
        integ = imax
        ent_stag[cslot] = 1
        sfxq.append("stagger")
    ent_brk[cslot] = 0
    if st == "closed":
        dobu_open = 0
        if dobu_cut >= 2:
            st = "open"
            t = 0
            dobu_open = 1
            sfxq.append("block_break")
            shake = 8
            shake_amp = 4
        elif dobu_ph == 2 and (spew_first == 1 or t > 200):
            st = "spew"
            t = 0
            spew_first = 0
            sfxq.append("breach")
    elif st == "spew":
        ent_brk[cslot] = 1
        if t == 41:
            sfxq.append("oni_slam")
            shake = 8
            shake_amp = 4
            # a tall green wall of sludge, up to the thin platforms: jump it from up there,
            # Phase Step through it from the floor
            for k in range(2):
                pq_t.append("gwave")
                pq_x.append(bx + 30 - 60 * k)
                pq_y.append(by)
                pq_vx.append(6 - 12 * k)
                pq_vy.append(0)
        if t >= 65:
            st = "closed"
            t = 0
            if dobu_turn == 9:
                dobu_turn = 0
    elif st == "open":
        if ent_stag[cslot] == 0 and t >= 170 - 40 * (dobu_ph - 1):
            db_close()
    int_t += 1
    if int_t > 75 and integ > 0 and ent_stag[cslot] == 0 and t % 20 == 0:
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[cslot] / 2
        if integ < 0:
            integ = 0
    ent_int[cslot] = integ
    boss_hp = ehp
    boss_int = integ * 16 / imax


@proc
def db_close():
    # the core seals and the arms grow back
    st = "closed"
    t = 0
    dobu_open = 0
    dobu_cut = 0
    dobu_gen += 1
    integ = 0
    ent_stag[cslot] = 0
    sfxq.append("gurgle")


@proc
def db_beaten():
    st = "beaten"
    t = 0
    ehp = 0
    dobu_open = 0
    ent_alive[cslot] = 0
    ent_stag[cslot] = 0
    ent_brk[cslot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("oni_die")
    shake = 16
    shake_amp = 6
    hitstop = 12
    broadcast("ev_dobu_dead")


@proc
def db_draw():
    effect("ghost", 0)
    if st == "beaten":
        costume(join("dobu_dead_", min(3, floor(t / 12))))
        effect("ghost", min(100, max(0, t - 40) * 2))
    elif st == "open":
        costume(join("dobu_open_", floor(t / 8) % 2))
    elif st == "spew":
        costume("dobu_spew")
    else:
        costume(join("dobu_idle_", floor(t / 15) % 2))
    goto(bx + shx, by - 8 + shy)
    if st == "spew" and t >= 32 and t <= 40:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    elif guard_t > 0:
        guard_t -= 1
        effect("brightness", 25)
    else:
        effect("brightness", 0)
    show()


# ---------------------------------------------------------------- the arms
@proc
def aim(ax, ay):
    # Scratch direction from the shoulder to (ax, ay), and the size that reaches it
    ddx = ax - sx
    ddy = ay - sy
    if ddy == 0:
        ddy = 0.01
    dir = atan(ddx / ddy)
    if ddy < 0:
        dir += 180
    asz = min(150, max(60, sqrt(ddx * ddx + ddy * ddy) / 1.52))


@proc
def da_reset():
    st = "idle"
    t = 0
    ahp = 6
    aint = 0
    acd = 40 + 50 * (side == 1)
    gen = dobu_gen
    ent_alive[aslot] = 1
    ent_stag[aslot] = 0
    ent_int[aslot] = 0
    ent_y[aslot] = -999


@proc
def da_update():
    if t == 0 and st == "":
        sx = bx + side * 36
        sy = by + 66
        da_reset()
        st = "grow"
    t += 1
    if dobu_dead == 1 or boss_hp <= 0:
        st = "dead"
        ent_alive[aslot] = 0
        return
    if st == "cut":
        if gen != dobu_gen:
            da_reset()
            st = "grow"
            sfxq.append("gurgle")
        return
    if st == "grow":
        aim(sx + side * 60, sy - 70)
        asz = min(asz, t * 4)
        if t > 30:
            st = "idle"
            t = 0
        return
    if boss_on == 0:
        aim(sx + side * 60, sy - 80)
        return
    # the arms never guard: every cut lands, and wears on the body's Stance too
    if ent_sev[aslot] == 1:
        ent_sev[aslot] = 0
        da_cut()
        return
    if ent_dmg[aslot] > 0:
        ahp -= ent_dmg[aslot]
        if st == "pinned":
            aint = min(6, aint + ent_idmg[aslot])
        else:
            aint = min(6, aint + ent_idmg[aslot] * 0.5)
        ent_idmg[cslot] = ent_idmg[cslot] + ent_idmg[aslot] * 0.5
        flash_t = 3
        sfxq.append("thug_hurt")
        ent_dmg[aslot] = 0
        ent_idmg[aslot] = 0
        if ahp <= 0:
            da_cut()
            return
    if aint >= 6 and ent_stag[aslot] == 0:
        ent_stag[aslot] = 1
        st = "pinned"
        t = 0
        sfxq.append("stagger")
    if st == "idle":
        aim(sx + side * (70 + sin(frame * 3 + side * 40) * 10), sy - 60 + cos(frame * 4) * 8)
        if acd > 0:
            acd -= 1
        elif dobu_turn == 0 and pst != "dead" and mode == "play" and (px - bx) * side > -40:
            dobu_turn = side
            st = "rear"
            t = 0
            sfxq.append("windup")
    elif st == "rear":
        if t <= 22:
            tx = min(max(px, -215), 215)
            if p_ground == 1:
                ty = py
            else:
                ty = -124
        aim(tx - side * 10, ty + 120)
        if t >= 32 - 6 * (dobu_ph - 1):
            st = "slam"
            t = 0
    elif st == "slam":
        aim(tx, ty)
        if t == 2:
            sfxq.append("oni_slam")
            cfx("shockwave", hx, ty, 0)
            shake = 6
            shake_amp = 4
            p_overlap(tx - 26, tx + 26, ty - 4, ty + 30)
            if ov == 1:
                hit_player(2, 0, tx)
                if res == "deflect":
                    st = "pinned"
                    t = 0
                    sfxq.append("stagger")
            if st == "slam":
                st = "down"
                t = 0
    elif st == "down" or st == "pinned":
        aim(tx, ty)
        dlen = 34
        if st == "pinned":
            dlen = 110 - 20 * (dobu_ph - 1)
        if ent_stag[aslot] == 1:
            dlen = 150
        if t >= dlen:
            st = "lift"
            t = 0
            ent_stag[aslot] = 0
            aint = max(0, aint - 2)
    elif st == "lift":
        aim(sx + side * 70, sy - 60)
        if t >= 12:
            st = "idle"
            t = 0
            acd = rand(30, 60) - 18 * (dobu_ph - 1)
            if dobu_turn == side:
                dobu_turn = 0
    hx = sx + asz * 1.52 * sin(dir)
    hy = sy + asz * 1.52 * cos(dir)
    ent_x[aslot] = hx
    ent_y[aslot] = hy - 6
    ent_int[aslot] = aint


@proc
def da_cut():
    st = "cut"
    t = 0
    ent_alive[aslot] = 0
    ent_stag[aslot] = 0
    dobu_cut += 1
    if dobu_turn == side:
        dobu_turn = 0
    sfxq.append("block_break")
    cfx("hit", hx, hy, 0)
    shake = 8
    shake_amp = 4


@proc
def da_draw():
    if st == "dead" or st == "":
        hide()
        return
    rotation_style("all around")
    if st == "cut":
        costume("dobu_stump")
        point(90 + side * 60)
        size(100)
    else:
        costume(join("dobu_arm_", floor(frame / 6) % 2))
        point(dir)
        size(asz)
    goto(sx + shx, sy + shy)
    if (st == "rear" and t >= 25 - 6 * (dobu_ph - 1)) or (st == "slam" and t <= 1):
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    elif st == "pinned":
        effect("brightness", 20 * (frame % 8 < 4))
    else:
        effect("brightness", 0)
    show()
'''


# The Harmacist: keeps her distance and lobs vials in arcs (deflect them back;
# where they break, poison clouds linger). Up close she slashes with a scalpel.
# When hurt she pulls out a stim and heals until a Heavy Strike interrupts her.
# Phase 2: she injects her best formula (faster, red goggles), throws three
# vials at a time and bursts a poison cloud around herself as a Breach.
HARM = spawner('harm', '''
if harm_dead == 0:
    x = O_X[oi]
    y = O_Y[oi]
    myobj = oi
    add_ent("harm", x, y, 9, 48, 20, 16, 1)
    boss_slot = slot
    st = "wait"
    t = 0
    z = 0
    ehp = 20
    imax = 16
    integ = 0
    int_t = 0
    fr = 0
    face = -1
    acd = 40
    phase = 1
    juiced = 0
    stim_cd = 300
    hitrow = 0
    guard_n = 0
    mo = 0
    hdir = 0
    hit_t = 0
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
        hm_update()


@on("t_draw")
def draw():
    if is_clone == 1:
        hm_draw()


@proc
def hm_face():
    if px > x:
        face = 1
    else:
        face = -1


@proc
def hm_go(s2):
    st = s2
    t = 0
    ha = 0
    hm_face()


@proc
def hm_vial(tt):
    # an arc that lands on Hotaru in about tt frames
    vx = (px - x) / tt
    vy = (py + 14 - (y + 24) + 0.15 * tt * tt) / tt
    pq_t.append("vial")
    pq_x.append(x + face * 6)
    pq_y.append(y + 24)
    pq_vx.append(vx)
    pq_vy.append(vy)


@proc
def hm_beaten():
    st = "beaten"
    t = 0
    ehp = 0
    ent_alive[slot] = 0
    ent_stag[slot] = 0
    ent_brk[slot] = 0
    boss_hp = 0
    boss_int = 0
    sfxq.append("stagger")
    shake = 14
    shake_amp = 5
    hitstop = 12
    broadcast("ev_harm_dead")


@proc
def hm_update():
    t += 1
    ha += 1
    if st == "beaten":
        if harm_dead == 2:
            # she gets up and limps off, away from Hotaru
            st = "limp"
            t = 0
            if px > x:
                face = -1
            else:
                face = 1
        return
    if st == "limp":
        fr += 0.07
        x += face * 0.9
        if abs(x) > 280:
            st = "gone"
        return
    if st == "gone":
        return
    if st == "wait":
        fr += 0.15
        if boss_on == 1:
            hm_go("move")
            acd = 30
        return
    if ent_sev[slot] == 1:
        ent_sev[slot] = 0
        seg = ceil(ehp / 5)
        ehp = (seg - 1) * 5
        integ = 0
        ent_stag[slot] = 0
        flash_t = 8
        sfxq.append("oni_hurt")
        if ehp <= 0:
            hm_beaten()
            return
        hm_go("hurt")
        t = -20
    if ent_dmg[slot] > 0:
        hk = ent_hk[slot]
        mo = 0
        if st == "recover" or st == "hurt" or st == "stim" or st == "broken" or hk == "projectile":
            mo = 1
    if ent_dmg[slot] > 0 and mo == 0:
        # outside her openings she fends blows off with her vial case
        sfxq.append("muk_guard")
        cfx("deflect", x + face * 10, y + 22, 0 - face)
        if hk == "heavy":
            integ = min(imax, integ + ent_idmg[slot] * 0.4)
        else:
            integ = min(imax, integ + ent_idmg[slot] * 0.15)
        int_t = 0
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        guard_n += 1
        if st == "move" and guard_n >= 2:
            guard_n = 0
            hm_go("hop")
            sfxq.append("dash")
    if ent_dmg[slot] > 0:
        # twice the health
        ehp -= ent_dmg[slot] / 2
        if st != "broken":
            integ = min(imax, integ + ent_idmg[slot])
        int_t = 0
        flash_t = 3
        sfxq.append("thug_hurt")
        x = min(max(x + ent_kb[slot], -205), 205)
        ent_dmg[slot] = 0
        ent_idmg[slot] = 0
        if ehp <= 0:
            hm_beaten()
            return
        if st == "stim":
            if hk == "heavy":
                # a Heavy Strike knocks the stim out of her hand
                integ = min(imax, integ + 4)
                stim_cd = 420
                sfxq.append("glass")
                hm_go("hurt")
                t = -16
        elif st == "recover" or st == "hurt":
            # an opening is worth a couple of cuts; then she's gone
            hitrow += 1
            hit_t = 0
            if hitrow >= 2:
                hitrow = 0
                hm_go("hop")
                sfxq.append("dash")
    if ehp <= 10 and phase == 1:
        phase = 2
        hm_go("juice")
        broadcast("ev_harm_phase2")
    if integ >= imax and st != "broken":
        st = "broken"
        t = 0
        integ = imax
        ent_stag[slot] = 1
        sfxq.append("stagger")
    if stim_cd > 0:
        stim_cd -= 1
    dx = px - x
    ad = abs(dx)
    sp = 1.5 + juiced
    ent_brk[slot] = 0
    if st == "move":
        hm_face()
        fr += 0.2
        if acd > 0:
            acd -= 1
        if ad < 100:
            x -= face * sp
        elif ad > 170:
            x += face * sp
        if acd == 0 and pst != "dead":
            seg_top = ceil(ehp / 5) * 5
            if stim_cd == 0 and seg_top - ehp >= 2:
                hm_go("stim")
                sfxq.append("pickup")
            elif ad < 70:
                hm_go("slash")
                sfxq.append("windup")
            elif phase == 2 and ad < 110 and rand(1, 3) == 1:
                hm_go("burst")
                sfxq.append("breach")
            else:
                hm_go("throw")
                sfxq.append("windup")
    elif st == "throw":
        if t == 18:
            sfxq.append("throw")
            tt = max(22, ad / 5)
            hm_vial(tt)
            if phase == 2:
                hm_vial(tt * 0.75)
                hm_vial(tt * 1.3)
        if t >= 30:
            st = "recover"
            t = 0
    elif st == "slash":
        # the sword: a 0.6 s windup, then a cut with twice the old scalpel's reach
        if t == 18:
            sfxq.append("muk_slash")
            if face == 1:
                p_overlap(x, x + 68, y + 2, y + 40)
            else:
                p_overlap(x - 68, x, y + 2, y + 40)
            if ov == 1:
                hit_player(2, 0, x)
                if res == "deflect":
                    integ = min(imax, integ + 3)
                    int_t = 0
                    hm_go("hurt")
                    t = -10
        if t >= 28 and st == "slash":
            st = "recover"
            t = 0
    elif st == "stim":
        if t > 20 and t % 10 == 0 and ehp < ceil(ehp / 5) * 5:
            ehp = min(ceil(ehp / 5) * 5, ehp + 0.5)
            cfx("sync", x, y + 30, 0)
        if t >= 70:
            stim_cd = 360
            st = "recover"
            t = 0
    elif st == "juice":
        if t == 20:
            juiced = 1
            sfxq.append("sync")
            flash = 30
        if t >= 44:
            st = "recover"
            t = 0
    elif st == "burst":
        ent_brk[slot] = 1
        if t >= 12 and t < 24 and ad > 26:
            x += face * 3
        if t == 24:
            pq_t.append("burst")
            pq_x.append(x)
            pq_y.append(y)
            pq_vx.append(0)
            pq_vy.append(0)
        if t >= 40:
            st = "recover"
            t = 0
    elif st == "hop":
        if t == 1:
            # backed into a wall, she vaults over Hotaru instead
            hdir = 0 - face
            if (hdir == 1 and x > 150) or (hdir == -1 and x < -150):
                hdir = face
        x = min(max(x + hdir * (5 + 2 * (hdir == face)), -205), 205)
        z = max(0, sin(t * 10) * 34)
        if t >= 18:
            z = 0
            st = "recover"
            t = 0
    elif st == "recover":
        if t >= 22 - 8 * juiced:
            hm_go("move")
            acd = rand(30, 60) - 15 * juiced
    elif st == "hurt":
        if t >= 12:
            hm_go("move")
            acd = max(acd, 10)
    elif st == "broken":
        if t >= 100:
            st = "move"
            t = 0
            integ = imax / 2
            ent_stag[slot] = 0
            acd = 10
    int_t += 1
    if int_t > 150 and integ > 0 and st != "broken" and t % 45 == 0:
        # hurt fighters settle slower, down to half speed
        integ -= 0.5 + ehp / ent_hp[slot] / 2
        if integ < 0:
            integ = 0
    hit_t += 1
    if hit_t > 40:
        hitrow = 0
        guard_n = 0
    x = min(max(x, -205), 205)
    ent_x[slot] = x
    ent_y[slot] = y + z
    ent_int[slot] = integ
    boss_hp = ehp
    boss_int = integ * 16 / imax


@proc
def hm_draw():
    # hand-drawn frames at 12 fps (2.5 game frames each); harmj_ is her juiced look
    pre = "harm_"
    if juiced == 1:
        pre = "harmj_"
    if st == "gone":
        hide()
        return
    if st == "beaten":
        costume(join("harm_death_", min(11, floor(t / 2.5))))
    elif st == "limp":
        costume(join("harm_run_", floor(fr * 4) % 8))
    elif st == "throw":
        # 0 takes a vial, 1-2 wind up, 3 lets go (the vial spawns at t 18), 4-7 follow through
        if t < 18:
            costume(join(pre, join("throw_", floor(t / 6))))
        else:
            costume(join(pre, join("throw_", min(7, 3 + floor((t - 18) / 3)))))
    elif st == "slash":
        # 0-1 wind up, 2 is the cut (t 18), 3-5 follow through
        if t < 18:
            costume(join(pre, join("slash_", floor(t / 9))))
        else:
            costume(join(pre, join("slash_", min(5, 2 + floor((t - 18) / 3)))))
    elif st == "stim" or st == "juice":
        if t < 20:
            costume(join(pre, "burst_0"))
        else:
            costume(join(pre, "burst_1"))
    elif st == "burst":
        if t < 12:
            costume(join(pre, join("burst_", floor(t / 6))))
        elif t < 24:
            costume(join(pre, join("burst_", 2 + floor((t - 12) / 3) % 3)))
        else:
            costume(join(pre, join("burst_", min(7, 5 + floor((t - 24) / 5)))))
    elif st == "hurt":
        costume(join(pre, join("hurt_", min(3, floor(ha / 3)))))
    elif st == "broken":
        costume(join(pre, "hurt_3"))
    elif (st == "move" and abs(px - x) > 6) or st == "hop":
        costume(join(pre, join("run_", floor(fr * 2) % 8)))
    else:
        costume(join(pre, join("idle_", floor(frame / 2.5) % 12)))
    if st == "broken":
        goto(x + shx + (frame % 4 < 2) * 2 - 1, y + z + shy)
    else:
        goto(x + shx, y + z + shy)
    if face == 1:
        point(90)
    else:
        point(-90)
    tell = 0
    if (st == "throw" and t >= 9 and t < 18) or (st == "slash" and t >= 9 and t < 18):
        tell = 1
    if tell == 1:
        effect("brightness", 100)
    elif flash_t > 0:
        flash_t -= 1
        effect("brightness", 60)
    elif st == "stim" and t >= 20:
        effect("brightness", 30 * (frame % 6 < 3))
    else:
        effect("brightness", 0)
    show()
'''
