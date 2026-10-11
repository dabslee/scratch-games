# Hotaru: the player. Movement, Phase Step, combat, deflect / Heat, healing.
# Positions are stage units; (px, py) is the point between her feet.

@flag
def init():
    hide()
    rotation_style("left-right")
    pst = "move"
    panim = ""


@on("t_player")
def t_player():
    p_update()


@on("t_draw")
def t_draw():
    p_draw()


@on("clear")
def on_clear():
    if mode != "play" and mode != "trans" and mode != "dead":
        ingame = 0


# ------------------------------------------------------------ room entry
@on("spawn")
def on_spawn():
    p_enter()


@proc
def p_enter():
    ingame = 1
    onplat = 0
    drop_t = 0
    if enter_dir == "L":
        px = -236
    elif enter_dir == "R":
        px = 236
    elif enter_dir == "B":
        if lift_ride == 1:
            py = C_LIFT_LOW
            pvy = 0
            onplat = 1
        else:
            py = -200
            pvy = C_BOOST
            jumping = 0
    elif enter_dir == "T":
        py = 152
    else:
        if enter_dir == "C":
            px = cp_x
            py = cp_y
        else:
            o1 = O_FIRST[room]
            for oi in range(o1, o1 + O_NUM[room]):
                if O_TYPE[oi] == "start":
                    px = O_X[oi]
                    py = O_Y[oi]
            cp_room = room
            cp_x = px
            cp_y = py
        pst = "move"
        pvx = 0
        pvy = 0
        pface = 1
        pinv = 0
        pparry = 0
        pblock = 0
        pdash = 0
        heat = 0
        cling = 0
        jbuf = 0
        combo = 0
        anim_force("idle")
        if room == C_ROOM_P1 and not ("boot" in seen):
            pst = "cut"
            anim_force("death")
            pfr = 5.5
    # a lift ride carries over so the arriving lift can bring Hotaru up
    if enter_dir != "B":
        lift_ride = 0
    safe_x = px
    safe_y = py
    if enter_dir == "L" or enter_dir == "R":
        safe_ok = 1
    p_ground = grounded


# ------------------------------------------------------------ update
@proc
def p_update():
    if pst == "cut":
        if p_cmd == "reboot":
            p_cmd = ""
            pst = "reboot"
            pfr = 5.9
            sfxq.append("reboot")
        physics()
        return
    if pst == "reboot":
        pfr -= 0.27
        if pfr <= 0:
            pfr = 0
            pst = "move"
            anim_force("idle")
        physics()
        return
    proc_hits()
    if pst == "dead":
        st_dead()
        return
    timers()
    down_tap()
    if pst == "move":
        st_move()
    elif pst == "dash":
        st_dash()
    elif pst == "atk":
        st_atk()
    elif pst == "deflect":
        st_deflect()
    elif pst == "block":
        st_block()
    elif pst == "hurt":
        st_hurt()
    elif pst == "overheat":
        st_overheat()
    elif pst == "heal":
        st_heal()
    elif pst == "held":
        st_held()
    if pst != "dead" and pst != "held":
        physics()
        post()
    pt += 1
    anim_step()
    p_ground = grounded
    p_onplat = onplat


@proc
def timers():
    if pinv > 0:
        pinv -= 1
    if pparry > 0:
        pparry -= 1
    if jbuf > 0:
        jbuf -= 1
    if pU == 1:
        jbuf = C_JBUF
    if coyote > 0:
        coyote -= 1
    if combo_t > 0:
        combo_t -= 1
    elif pst != "atk":
        combo = 0
    if heavy_buf > 0:
        heavy_buf -= 1
    if dash_end_buf > 0:
        dash_end_buf -= 1
    if drop_t > 0:
        drop_t -= 1
    if dtap_t > 0:
        dtap_t -= 1
    if land_t > 0:
        land_t -= 1
    air_t += 1
    heat_idle += 1
    # Stance only recovers with her guard down: never while blocking. The more hurt
    # she is the slower it settles, down to half speed near empty
    if heat_idle > 30 and heat > 0 and pst != "overheat" and pst != "block" and pst != "deflect" and frame % 6 == 0:
        heat -= 0.5 + hp / 20
        if heat < 0:
            heat = 0


# ------------------------------------------------------------ states
@proc
def down_tap():
    # Double-tapping Down while standing on a thin platform drops through it.
    # The first tap is still a normal deflect.
    if pS == 0:
        return
    if dtap_t > 0 and grounded == 1 and on_oneway == 1 and on_solid == 0 and (pst == "move" or pst == "deflect" or pst == "block"):
        dtap_t = 0
        pS = 0
        pblock = 0
        pparry = 0
        pst = "move"
        drop_t = 6
        pvy = -3
        jumping = 0
    else:
        dtap_t = 10


@proc
def st_move():
    dirx = kR - kL
    crouch = 0
    if wjlock > 0:
        wjlock -= 1
    else:
        tgt = dirx * C_RUN
        if grounded == 1 and kD == 1:
            tgt = 0
            crouch = 1
        if grounded == 1:
            acc = 1.6
        else:
            acc = 0.9
        if pvx < tgt:
            pvx = min(pvx + acc, tgt)
        elif pvx > tgt:
            pvx = max(pvx - acc, tgt)
        if dirx != 0:
            pface = dirx
    if jbuf > 0:
        if grounded == 1 or coyote > 0:
            do_jump()
        else:
            near_wall()
            if nw != 0:
                wall_jump(nw)
    if jumping == 1 and kU == 0 and pvy > 4:
        pvy = 4
        jumping = 0
    if pvy <= 0:
        jumping = 0
    if pZ == 1:
        try_dash()
        return
    if pA == 1:
        try_attack()
        return
    if pS == 1:
        start_deflect()
        return
    if pH == 1:
        try_heal()
        return
    if grounded == 1:
        if land_t > 0:
            anim("land")
        elif crouch == 1:
            anim("land")
            pfr = 1
        elif abs(pvx) > 0.8:
            anim("run")
            step_t += 1
            if step_t % 8 == 1:
                mfx("run_dust", px - pface * 6, py, pface)
                sfxq.append("step")
        else:
            anim("idle")
    elif cling != 0:
        anim("wall_cling")
        pface = cling
        if pt % 5 == 0:
            mfx("wall_spark", px + cling * 8, py + 30, cling)
    else:
        anim("jump")
        if pvy > 7:
            pfr = 0
        elif pvy > 2:
            pfr = 1
        elif pvy > -3:
            pfr = 2
        elif pvy > -8:
            pfr = 3
        else:
            pfr = 4


@proc
def do_jump():
    pvy = C_JUMP
    grounded = 0
    coyote = 0
    jbuf = 0
    jumping = 1
    air_t = 0
    onplat = 0
    sfxq.append("jump")
    mfx("run_dust", px, py, pface)


@proc
def near_wall():
    nw = 0
    cell(px + C_HW + 4, py + 18)
    if cc == "#" or cc == "B" or cc == "D":
        nw = 1
    cell(px - C_HW - 4, py + 18)
    if cc == "#" or cc == "B" or cc == "D":
        nw = -1
    if cling != 0:
        nw = cling


@proc
def wall_jump(side):
    pvy = C_WALLJUMP
    pvx = 0 - side * 7
    pface = 0 - side
    wjlock = 7
    cling = 0
    jbuf = 0
    jumping = 1
    air_t = 0
    sfxq.append("jump")
    mfx("wall_spark", px + side * 8, py + 20, side)


@proc
def try_dash():
    if dash_ch > 0:
        dash_ch -= 1
        dash_cd = 30
        ddx = kR - kL
        ddy = kU - kD
        if grounded == 1 and ddy < 0 and not (on_oneway == 1 and on_solid == 0):
            ddy = 0
        if ddx == 0 and ddy == 0:
            ddx = pface
        if ddx != 0 and ddy != 0:
            ddx = ddx * 0.7071
            ddy = ddy * 0.7071
        if ddx > 0:
            pface = 1
        if ddx < 0:
            pface = -1
        pst = "dash"
        pt = 0
        pdash = 1
        jumping = 0
        cling = 0
        onplat = 0
        anim_force("dash")
        sfxq.append("dash")
        mfx("afterimage", px, py, pface)
    else:
        heavy_buf = 6
        sfxq.append("nodash")


@proc
def st_dash():
    if pA == 1:
        pdash = 0
        start_heavy(1)
        return
    pvx = ddx * C_DASHV
    pvy = ddy * C_DASHV
    if pt % 2 == 1:
        mfx("afterimage", px, py, pface)
    if pt >= C_DASHF - 1:
        cell(px, py + 17)
        inl = 0
        if cc == "L":
            inl = 1
        cell(px + pface * 6, py + 17)
        if cc == "L":
            inl = 1
        if inl == 0 or pt > 20:
            pdash = 0
            pst = "move"
            pvx = ddx * C_RUN
            if ddy > 0:
                pvy = ddy * 7
            else:
                pvy = 0
            if ddy < 0:
                drop_t = 3
            dash_end_buf = 5


@proc
def try_attack():
    find_sever()
    if sev_slot > 0:
        start_atk("severance")
        return
    if heavy_buf > 0 or dash_end_buf > 0:
        heavy_buf = 0
        start_heavy(0)
        return
    if grounded == 0:
        if kU == 1 and air_t < 8:
            start_atk("launcher")
            return
        if airatk < 3:
            airatk += 1
            start_atk("air_attack")
        return
    if kU == 1:
        start_atk("launcher")
        return
    if combo_t > 0 and combo < 4:
        combo += 1
    else:
        combo = 1
    start_atk(join("attack", combo))


@proc
def start_heavy(lunge):
    start_atk("heavy")
    lunge_on = lunge
    if dash_end_buf > 0:
        lunge_on = 1
    dash_end_buf = 0


@proc
def start_atk(a):
    pst = "atk"
    p_atk = a
    pt = 0
    hitdone = 0
    queued = 0
    lunge_on = 0
    anim_force(a)
    atk_info(a)
    slash_fx = atk_fx
    slash_off = atk_fxoff
    sfxq.append(atk_snd)
    if a == "attack1" or a == "attack2" or a == "attack3" or a == "attack4":
        if grounded == 1:
            pvx = pface * 2.5
    if a == "launcher":
        pvy = max(pvy, 8)
        grounded = 0
        onplat = 0
    if a == "air_attack":
        if pvy < 0:
            pvy = 0
    if a == "severance":
        pinv = 24
        if ent_x[sev_slot] > px:
            pface = 1
        else:
            pface = -1
        ox = px
        px = ent_x[sev_slot] - pface * 26
        # never snap into a wall (an enemy standing against one)
        cell(px - C_HW, py + 10)
        if cc == "#":
            px = ox
        cell(px + C_HW, py + 10)
        if cc == "#":
            px = ox
        pvx = 0


@proc
def st_atk():
    fr = floor(pfr)
    if p_atk == "heavy":
        if fr < 3 and lunge_on == 1:
            pvx = pface * 8
        else:
            pvx = pvx * 0.7
    elif grounded == 1:
        pvx = pvx * 0.75
    if hitdone == 0 and fr >= atk_conn:
        hitdone = 1
        if p_atk == "severance":
            do_sever()
        else:
            do_hit()
    if pA == 1 and fr >= atk_conn:
        if p_atk == "attack1" or p_atk == "attack2" or p_atk == "attack3":
            queued = 1
    if fr > atk_conn and p_atk != "heavy" and p_atk != "severance":
        if pZ == 1:
            pst = "move"
            try_dash()
            return
        if pS == 1:
            start_deflect()
            return
    if pfr >= a_n:
        if queued == 1 and grounded == 1:
            find_sever()
            if sev_slot > 0:
                start_atk("severance")
                return
            combo += 1
            start_atk(join("attack", combo))
            return
        pst = "move"
        if p_atk == "attack1" or p_atk == "attack2" or p_atk == "attack3":
            combo_t = C_COMBO
        if p_atk == "attack4":
            combo = 0


@proc
def hb_box():
    ha = -6
    hb = 40
    ay1 = py + 2
    ay2 = py + 42
    if p_atk == "attack4":
        hb = 48
    elif p_atk == "heavy":
        hb = 52
        ay2 = py + 46
    elif p_atk == "launcher":
        ha = -12
        hb = 34
        ay2 = py + 70
    elif p_atk == "air_attack":
        hb = 40
        ay1 = py - 8
        ay2 = py + 50
    if pface == 1:
        ax1 = px + ha
        ax2 = px + hb
    else:
        ax1 = px - hb
        ax2 = px - ha


@proc
def do_hit():
    hb_box()
    nh = 0
    for ei in range(1, len(ent_type) + 1):
        if ent_alive[ei] == 1 and ent_x[ei] + ent_w[ei] > ax1 and ent_x[ei] - ent_w[ei] < ax2:
            if ent_y[ei] + ent_h[ei] > ay1 and ent_y[ei] < ay2:
                ent_dmg[ei] = ent_dmg[ei] + atk_dmg
                ent_idmg[ei] = ent_idmg[ei] + atk_int
                ent_kb[ei] = pface * atk_kb
                ent_hk[ei] = p_atk
                nh += 1
                cfx("hit_enemy", ent_x[ei] - pface * 4, ent_y[ei] + min(ent_h[ei] * 0.55, 40), pface)
    if nh > 0:
        sfxq.append("hit")
        if p_atk == "attack4" or p_atk == "heavy":
            hitstop = 5
            shake = 6
            shake_amp = 4
            sfxq.append("hit_heavy")
        else:
            hitstop = 2
    brk_check()


@proc
def brk_check():
    bc1 = max(0, floor((ax1 + 240) / 16))
    bc2 = min(29, floor((ax2 + 240) / 16))
    br1 = max(0, floor((180 - ay2) / 16))
    br2 = min(22, floor((180 - ay1) / 16))
    for brr in range(br1, br2 + 1):
        for bcc in range(bc1, bc2 + 1):
            if grid[brr * 30 + bcc + 1] == "B":
                brk_hits.append(brr * 30 + bcc + 1)


@proc
def find_sever():
    sev_slot = 0
    for ei in range(1, len(ent_type) + 1):
        if ent_alive[ei] == 1 and ent_stag[ei] == 1:
            if abs(ent_x[ei] - px) < 70 and abs(ent_y[ei] - py) < 60:
                sev_slot = ei


@proc
def do_sever():
    ent_sev[sev_slot] = 1
    hitstop = 8
    shake = 10
    shake_amp = 6
    sfxq.append("severance")
    banner_flash("execution")
    # an Execution steadies Hotaru and refills a gourd charge
    heat = 0
    if has_gourd == 1:
        gourd = min(gmax, gourd + 1)
    cfx("hit_enemy", ent_x[sev_slot], ent_y[sev_slot] + 30, pface)
    cfx("explosion", ent_x[sev_slot], ent_y[sev_slot] + 30, pface)


@proc
def banner_flash(b):
    banner = b
    banner_t = 40


@proc
def start_deflect():
    pst = "deflect"
    pt = 0
    if opt_wide == 1:
        pparry = C_PARRY_WIDE
    else:
        pparry = C_PARRY
    pblock = 0
    anim_force("deflect")
    sfxq.append("swish")


@proc
def st_deflect():
    if grounded == 1:
        pvx = pvx * 0.6
    guard_cancel()
    if pst != "deflect":
        return
    if pfr >= a_n:
        if kS == 1:
            pst = "block"
            pblock = 1
            anim("block")
        else:
            pst = "move"


@proc
def st_block():
    pvx = pvx * 0.6
    if kL == 1:
        pface = -1
    if kR == 1:
        pface = 1
    anim("block")
    guard_cancel()
    if pst != "block":
        return
    if kS == 0:
        pst = "move"
        pblock = 0


@proc
def guard_cancel():
    # Deflect / block live on the Down key: Phase Step (aimable, including
    # down through thin platforms) cancels them, and Up jumps out of a block.
    if pZ == 1:
        pblock = 0
        pst = "move"
        try_dash()
        return
    if jbuf > 0 and (grounded == 1 or coyote > 0):
        pblock = 0
        pst = "move"
        do_jump()


@proc
def try_heal():
    if grounded == 1 and hp < 10:
        if gourd > 0 or (opt_gourd == 1 and has_gourd == 1):
            pst = "heal"
            pt = 0
            healed = 0
            anim_force("heal")
            sfxq.append("uncork")
        else:
            sfxq.append("empty")


@proc
def st_heal():
    pvx = pvx * 0.5
    if healed == 0 and pfr >= 3:
        healed = 1
        hp = min(10, hp + C_HEAL)
        if opt_gourd == 0:
            gourd -= 1
        cfx("heal", px, py, pface)
        sfxq.append("heal")
    if pfr >= a_n:
        pst = "move"


@proc
def overheat():
    pst = "overheat"
    pt = 0
    pblock = 0
    pparry = 0
    heat = 16
    anim_force("overheat")
    sfxq.append("overheat")
    cfx("steam", px, py + 30, pface)


@proc
def st_overheat():
    pvx = pvx * 0.7
    if pt >= C_OVERHEAT:
        heat = 0
        pst = "move"


@proc
def st_hurt():
    if grounded == 1 and pt > 3:
        pvx = pvx * 0.7
    if pt >= 10:
        pst = "move"


@proc
def st_dead():
    pt += 1
    if pfr < a_n:
        pfr += 0.27
    pvx = pvx * 0.8
    physics()
    if pt == 50:
        want_respawn = 1


# ------------------------------------------------------------ incoming hits
@proc
def proc_hits():
    hn = len(hq_t)
    for hi in range(1, hn + 1):
        ht = hq_t[hi]
        if ht == "deflect":
            got_deflect(hq_x[hi])
        elif ht == "block":
            got_block(hq_x[hi])
        elif ht == "hit":
            take_hit(hq_d[hi], hq_x[hi])
        elif ht == "hazard":
            hazard(hq_d[hi])
        elif ht == "sting":
            sting(hq_d[hi])
        elif ht == "guardbreak":
            guard_break()
        elif ht == "held":
            got_held()
        elif ht == "squeeze":
            squeeze(hq_d[hi])
        elif ht == "thrown":
            thrown(hq_x[hi])
    hq_t.clear()
    hq_d.clear()
    hq_x.clear()


@proc
def got_deflect(sx):
    heat = max(0, heat - 2)
    dash_ch = 1
    hitstop = max(hitstop, 4)
    if sx > px:
        cfx("deflect", px + 14, py + 24, 1)
    else:
        cfx("deflect", px - 14, py + 24, -1)
    sfxq.append("deflect")
    shake = 3
    shake_amp = 2


@proc
def got_block(sx):
    if opt_heat == 1:
        heat += 1.5
    else:
        heat += 3
    heat_idle = 0
    if sx > px:
        pvx = -3
        cfx("hit", px + 12, py + 24, 1)
    else:
        pvx = 3
        cfx("hit", px - 12, py + 24, -1)
    sfxq.append("block")
    hitstop = max(hitstop, 2)
    if heat >= 16:
        overheat()


@proc
def take_hit(dmg, sx):
    if pst == "dead":
        return
    if opt_god == 0:
        hp -= dmg
    pinv = C_IFRAMES
    if px > sx:
        pvx = 5
    else:
        pvx = -5
    pvy = 5
    grounded = 0
    onplat = 0
    pst = "hurt"
    pt = 0
    pblock = 0
    pparry = 0
    pdash = 0
    cling = 0
    anim_force("hurt")
    sfxq.append("hurt")
    cfx("hit", px, py + 20, 0)
    shake = 6
    shake_amp = 4
    hitstop = 3
    if hp <= 0:
        die()


@proc
def guard_break():
    # she tried to guard a Breach: the hit lands, and her Stance takes a block's worth
    if pst == "dead":
        return
    if opt_heat == 1:
        heat += 1.5
    else:
        heat += 3
    heat_idle = 0
    if heat >= 16:
        overheat()


@proc
def got_held():
    # caught in the Daimyo's soul grab: lifted and held until he throws her
    if pst == "dead":
        return
    pst = "held"
    pt = 0
    pvx = 0
    pvy = 0
    pblock = 0
    pparry = 0
    pdash = 0
    cling = 0
    anim_force("hurt")
    sfxq.append("hurt")
    cfx("hit", px, py + 20, 0)
    shake = 6
    shake_amp = 4
    hitstop = 4


@proc
def st_held():
    px = hold_x
    py = hold_y
    pvx = 0
    pvy = 0
    grounded = 0
    if mk_x > px:
        pface = 1
    else:
        pface = -1
    if pt > 60:
        pst = "move"


@proc
def squeeze(dmg):
    if pst != "held":
        return
    if opt_god == 0:
        hp -= dmg
    heat = min(16, heat + 3)
    heat_idle = 0
    sfxq.append("zap")
    cfx("hit", px, py + 20, 0)
    shake = 3
    shake_amp = 2
    if hp <= 0:
        die()


@proc
def thrown(sx):
    if pst != "held":
        return
    pinv = C_IFRAMES
    if px > sx:
        pvx = 8
    else:
        pvx = -8
    pvy = 8
    grounded = 0
    onplat = 0
    pst = "hurt"
    pt = 0
    anim_force("hurt")
    sfxq.append("hurt")
    shake = 6
    shake_amp = 4
    hitstop = 3


@proc
def sting(dmg):
    if pst == "dead" or pinv > 0:
        return
    if opt_god == 0:
        hp -= dmg
    pinv = 12
    sfxq.append("zap")
    cfx("hit", px, py + 18, 0)
    shake = 3
    shake_amp = 2
    if hp <= 0:
        die()


@proc
def hazard(dmg):
    if pst == "dead":
        return
    if opt_god == 0:
        hp -= dmg
    px = safe_x
    py = safe_y
    pvx = 0
    pvy = 0
    pinv = C_IFRAMES
    pst = "hurt"
    pt = 0
    pdash = 0
    pblock = 0
    onplat = 0
    anim_force("hurt")
    sfxq.append("zap")
    flash = 40
    shake = 6
    shake_amp = 4
    if hp <= 0:
        die()


@proc
def tide_hit():
    # the sludge tide: a burn and a bounce back up, no teleport
    if opt_god == 0:
        hp -= 1
    pvy = 17
    py = tide_y - 4
    pinv = 24
    pdash = 0
    pblock = 0
    anim_force("hurt")
    sfxq.append("zap")
    cfx("hit", px, py + 10, 0)
    shake = 4
    shake_amp = 3
    if hp <= 0:
        die()


@proc
def die():
    hp = 0
    pst = "dead"
    pt = 0
    anim_force("death")
    deaths += 1
    pdash = 0
    pblock = 0
    pparry = 0
    hint = ""
    sfxq.append("flatline")


# ------------------------------------------------------------ physics
@proc
def physics():
    fallv = pvy
    was_g = grounded
    if onplat == 1:
        if mp_on == 1 and abs(px - mp_x) < 32 + C_HW:
            py = mp_y
        else:
            onplat = 0
    # Cooling-mist updrafts ("~" always on, "%" pulsing) lift Hotaru.
    updraft = 0
    cell(px, py + 12)
    if cc == "~" or (cc == "%" and frame % 110 < 70):
        updraft = 1
        jumping = 0
    # headwind on the monorail roofs
    if wind != 0 and pst != "dash" and pst != "dead" and px > -226:
        if grounded == 1:
            move_x(wind * 0.5)
        else:
            move_x(wind)
    if pst != "dash":
        if updraft == 1:
            if pvy < 0:
                pvy = pvy * 0.8
            pvy = min(pvy + 1.2, 8)
        elif cling != 0 and pvy < 0:
            pvy = max(pvy - C_G, 0 - C_SLIDE)
        elif pst == "atk" and (p_atk == "air_attack" or p_atk == "launcher") and pvy < 0:
            pvy = max(pvy - C_G * 0.35, -3)
        else:
            pvy = max(pvy - C_G, 0 - C_MAXFALL)
    grounded = 0
    on_oneway = 0
    on_solid = 0
    steps = ceil(max(abs(pvx), abs(pvy)) / 7)
    if steps < 1:
        steps = 1
    stx = pvx / steps
    sty = pvy / steps
    for _ in range(steps):
        move_x(stx)
        move_y(sty)
    if was_g == 1 and grounded == 0 and pvy <= 0 and jumping == 0:
        coyote = C_COYOTE
    # the Phase Step charge comes back a second after it's spent, once she's on the ground
    if dash_cd > 0:
        dash_cd -= 1
    if grounded == 1:
        air_t = 0
        if dash_cd == 0 and dash_ch < 1:
            dash_ch = 1
        if was_g == 0:
            airatk = 0
            if fallv < -9 and pst == "move":
                land_t = 5
                anim_force("land")
                mfx("land_dust", px, py, pface)
                sfxq.append("land")
    cling = 0
    if grounded == 0 and pst == "move" and pvy < 3:
        if kR == 1:
            cell(px + C_HW + 2, py + 20)
            if cc == "#" or cc == "B" or cc == "D":
                cling = 1
        elif kL == 1:
            cell(px - C_HW - 2, py + 20)
            if cc == "#" or cc == "B" or cc == "D":
                cling = -1


@proc
def cell(x, y):
    ccx = floor((x + 240) / 16)
    ccy = floor((180 - y) / 16)
    if ccx < 0:
        if exL > 0 and ccy >= 0 and ccy <= 22:
            cc = grid[ccy * 30 + 1]
            if cc != "#":
                cc = "."
        else:
            cc = "#"
    elif ccx > 29:
        if exR > 0 and ccy >= 0 and ccy <= 22:
            cc = grid[ccy * 30 + 30]
            if cc != "#":
                cc = "."
        else:
            cc = "#"
    elif ccy < 0:
        if exU > 0:
            cc = "."
        else:
            cc = "#"
    elif ccy > 22:
        cc = grid[661 + ccx]
        if cc != "#":
            cc = "."
    else:
        cc = grid[ccy * 30 + ccx + 1]


@proc
def move_x(dx):
    if dx == 0:
        return
    px += dx
    if dx > 0:
        edge = px + C_HW
    else:
        edge = px - C_HW
    blocked = 0
    for k in range(3):
        cell(edge, py + 2 + k * 15)
        if cc == "#" or cc == "B" or cc == "D" or (cc == "L" and pdash == 0):
            blocked = 1
    if blocked == 1:
        col = floor((edge + 240) / 16)
        if dx > 0:
            px = col * 16 - 240 - C_HW - 0.01
        else:
            px = col * 16 - 224 + C_HW + 0.01
        pvx = 0
        if pst == "dash" and ddy == 0:
            pvx = 0


@proc
def move_y(dy):
    if dy == 0:
        return
    oldy = py
    py += dy
    if dy < 0:
        blocked = 0
        land_top = -99999
        foot(px - 5, oldy)
        foot(px + 5, oldy)
        if blocked == 0 and mp_on == 1:
            if abs(px - mp_x) < 32 + 4 and oldy >= mp_y - 0.01 and py <= mp_y:
                blocked = 1
                land_top = mp_y
                onplat = 1
        if blocked == 1:
            py = land_top
            pvy = 0
            grounded = 1
    else:
        hy = py + C_PH
        blocked = 0
        for k in range(2):
            cell(px - 5 + k * 10, hy)
            if cc == "#" or cc == "B" or cc == "D" or (cc == "L" and pdash == 0):
                blocked = 1
        if blocked == 1:
            py = (180 - (ccy + 1) * 16) - C_PH - 0.01
            pvy = 0
            jumping = 0


@proc
def foot(fx, oy):
    cell(fx, py)
    ftop = 180 - ccy * 16
    if cc == "#" or cc == "B" or cc == "D" or (cc == "L" and pdash == 0):
        blocked = 1
        land_top = max(land_top, ftop)
        on_solid = 1
    elif cc == "=" and drop_t == 0 and oy >= ftop - 0.01 and not (pst == "dash" and ddy < 0):
        blocked = 1
        land_top = max(land_top, ftop)
        on_oneway = 1


@proc
def post():
    for _ in range(3):
        cell(px, py + 6)
        if cc == "#" and pst != "dash":
            py = 180 - ccy * 16
            pvy = 0
    cell(px, py + 5)
    if cc == "^" or cc == "v" or cc == "w":
        hazard(2)
        return
    cell(px, py + 28)
    if cc == "^" or cc == "v":
        hazard(2)
        return
    if tide_y != 0 and py < tide_y - 6 and pinv == 0 and pst != "dead":
        tide_hit()
    if py < -215 and exD == 0:
        hazard(2)
        return
    if px > 244 and exR > 0:
        want_room = exR
        enter_dir = "L"
    elif px < -244 and exL > 0:
        want_room = exL
        enter_dir = "R"
    elif py + 30 > 180 and exU > 0:
        want_room = exU
        enter_dir = "B"
        lift_ride = onplat
    elif py + 30 < -184 and exD > 0:
        want_room = exD
        enter_dir = "T"
    if grounded == 1 and onplat == 0 and on_oneway == 0 and pst == "move":
        cell(px - 6, py - 4)
        sa = cc
        oa = letter(ccy * 30 + ccx + 1, R_GRID[room])
        cell(px + 6, py - 4)
        ob = letter(ccy * 30 + ccx + 1, R_GRID[room])
        # phasing blocks come and go, so they never count as safe ground
        if sa == "#" and cc == "#" and oa == "#" and ob == "#":
            cell(px - 22, py + 5)
            sb = cc
            cell(px + 22, py + 5)
            if sb != "^" and cc != "^" and sb != "w" and cc != "w" and (tide_y == 0 or py > tide_hi + 8):
                safe_x = px
                safe_y = py


# ------------------------------------------------------------ animation
@proc
def anim(name):
    if panim != name:
        panim = name
        pfr = 0
        anim_info(name)


@proc
def anim_force(name):
    panim = name
    pfr = 0
    anim_info(name)


@proc
def anim_step():
    if pst == "reboot" or pst == "cut":
        return
    pfr += a_fps / 30
    if a_loop == 1:
        if pfr >= a_n:
            pfr = pfr - a_n


@proc
def p_draw():
    if ingame == 0:
        hide()
        return
    show()
    fi = floor(pfr)
    if fi > a_n - 1:
        fi = a_n - 1
    if fi < 0:
        fi = 0
    # one Phase Step charge: the scarf greys out while it's spent (2 = the epilogue's violet flicker)
    suf = ""
    if dash_ch == 2:
        suf = "_m"
    elif dash_ch < 1:
        suf = "_g"
    costume(join(panim, "_", fi, suf))
    if panim == "wall_cling":
        goto(px - pface * 5 + shx, py + shy)
    else:
        goto(px + shx, py + shy)
    if pface == 1:
        point(90)
    else:
        point(-90)
    if pinv > 0 and pst != "atk" and pst != "dead" and frame % 4 < 2:
        effect("ghost", 60)
    elif pst == "cut":
        effect("ghost", 100)
    elif pst == "reboot":
        effect("ghost", rand(0, 40))
    else:
        effect("ghost", 0)
