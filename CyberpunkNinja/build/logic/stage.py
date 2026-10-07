# Stage: master game loop, input, rooms, transitions and story events.
# (Scratch DSL: compiled by scratchc.py, not run as Python.)

@flag
def boot():
    mode = "boot"
    frame = 0
    menu = ""
    init_options()
    reset_run()
    has_save = 0
    music_cur = "-"
    music_want = ""
    fade = 100
    fade_to = 100
    hitstop = 0
    shake = 0
    flash = 0
    want_room = 0
    want_respawn = 0
    walk_to = 999
    muk_carry = 0
    dlg_req = ""
    banner = ""
    card = ""
    hint = ""
    prompt_on = 0
    boss_on = 0
    backdrop("black")
    clear_queues()
    broadcast("boot")
    go_title()
    while True:
        frame_step()


@proc
def init_options():
    opt_wide = 0
    opt_slow = 0
    opt_heat = 0
    opt_gourd = 0
    opt_god = 0
    opt_music = 4
    opt_sfx = 4
    opt_shake = 1


@proc
def reset_run():
    hp = 10
    heat = 0
    gourd = 0
    gmax = 3
    has_gourd = 0
    dash_ch = 2
    shards = 0
    deaths = 0
    play_time = 0
    boss_dead = 0
    dobu_dead = 0
    luck_dead = 0
    harm_dead = 0
    muk_dead = 0
    muk_exit = 0
    daicam_done = 0
    daicam2_done = 0
    daicam3_done = 0
    daicam4_done = 0
    daicam5_done = 0
    raijin_dead = 0
    kuro_dead = 0
    kbranch = 0
    kuro_in = 0
    daicam6_done = 0
    daicam7_done = 0
    daicam8_done = 0
    daimyo_dead = 0
    wind = 0
    moving = 0
    flip = 0
    boss_name = "big_oni"
    lift_ride = 0
    cp_room = 1
    cp_x = 0
    cp_y = 0
    dead_objs.clear()
    seen.clear()
    got_shards.clear()
    broken.clear()


@proc
def respawn_state():
    hp = 10
    heat = 0
    if has_gourd == 1:
        gourd = gmax
    dash_ch = 2
    dead_objs.clear()


@proc
def clear_queues():
    hq_t.clear()
    hq_d.clear()
    hq_x.clear()
    cq_t.clear()
    cq_x.clear()
    cq_y.clear()
    cq_d.clear()
    mq_t.clear()
    mq_x.clear()
    mq_y.clear()
    mq_d.clear()
    pq_t.clear()
    pq_x.clear()
    pq_y.clear()
    pq_vx.clear()
    pq_vy.clear()
    brk_hits.clear()
    sfxq.clear()
    ui_slot.clear()
    ui_role.clear()


@proc
def frame_step():
    frame += 1
    read_input()
    if mode == "title":
        backdrop(join("title_", (frame // 4) % 8))
        if p_any == 1:
            sfxq.append("menu_select")
            open_menu("main")
    elif mode == "menu":
        if menu == "end":
            backdrop("black")
        elif menu != "pause" and menu != "pause_options":
            backdrop(join("title_menu_", (frame // 4) % 8))
    elif mode == "play":
        play_time += 1
        if p_pause == 1:
            mode = "menu"
            sfxq.append("pause")
            open_menu("pause")
        elif hitstop > 0:
            hitstop -= 1
        elif opt_slow == 1 and frame % 4 == 0:
            pass
        else:
            broadcast("t_player")
            broadcast("t_world")
            check_triggers()
            weather()
            phase_step()
        if mode == "play":
            if want_respawn == 1:
                want_respawn = 0
                mode = "dead"
                broadcast("do_respawn")
            elif want_room > 0:
                mode = "trans"
                broadcast("do_trans")
    shake_step()
    if music_want != music_cur:
        music_cur = music_want
        broadcast("music")
    broadcast("t_draw")


@proc
def phase_step():
    # phasing blocks swap every 100 frames; the incoming set turns solid 15 frames
    # before the outgoing set vanishes (gph = 2 * set + overlap)
    if len(GL_I) > 0 and floor(frame / 100) % 2 * 2 + (frame % 100 >= 85) != gph:
        gph = floor(frame / 100) % 2 * 2 + (frame % 100 >= 85)
        apply_phase()
        if gph % 2 == 1:
            sfxq.append("phase")
    # the sludge tide: low, rising, high, falling (a boss can drive tide_lvl itself)
    if R_TIDE[room] != 0:
        tide_hi = R_TIDE[room]
        tide_warn = 0
        if tide_force == 0:
            # each visit starts at low tide
            tide_t += 1
            tcyc = tide_t % 300
            if tcyc >= 95 and tcyc < 150:
                tide_warn = 1
            if tcyc < 150:
                tide_lvl = 0
            elif tcyc < 200:
                tide_lvl = (tcyc - 150) / 50
            elif tcyc < 260:
                tide_lvl = 1
            else:
                tide_lvl = 1 - (tcyc - 260) / 40
            if tcyc == 95 and mode == "play":
                sfxq.append("gurgle")
                shake = 20
                shake_amp = 2
        tide_y = -200 + (tide_hi + 200) * tide_lvl
        if tide_y == 0:
            tide_y = 1
    else:
        tide_y = 0
    # Kuro periodically takes the controls in possessed rooms
    if R_FLIP[room] == 1:
        cyc = frame % 330
        if cyc >= 210 and cyc < 240:
            flip_warn = 1
        else:
            flip_warn = 0
        if cyc == 240:
            sfxq.append("kvoice")
        if cyc >= 240:
            flip = 1
        else:
            flip = 0


@proc
def apply_phase():
    for gi in range(1, len(GL_I) + 1):
        if gph % 2 == 1 or (GL_T[gi] == "G" and gph < 2) or (GL_T[gi] == "H" and gph >= 2):
            grid[GL_I[gi]] = "#"
        else:
            grid[GL_I[gi]] = "."


@proc
def read_input():
    kL = key("left arrow") or key("a")
    kR = key("right arrow") or key("d")
    if flip == 1:
        tmp = kL
        kL = kR
        kR = tmp
    kU = key("up arrow") or key("w")
    kD = key("down arrow") or key("s")
    kA = mouse_down() or key("x") or key("j")
    kZ = key("space") or key("z") or key("k")
    kS = key("down arrow") or key("s") or key("l")
    kH = key("r")
    kE = key("e")
    kN = key("enter")
    kP = key("p")
    kAny = key("any") or mouse_down()
    if walk_to != 999:
        # a scripted walk: Hotaru crosses to walk_to on her own
        kL = px > walk_to + 3
        kR = px < walk_to - 3
        kU = 0
        kD = 0
        kA = 0
        kZ = 0
        kS = 0
        kH = 0
    pU = 0
    pD = 0
    pL = 0
    pR = 0
    pA = 0
    pZ = 0
    pS = 0
    pH = 0
    pE = 0
    p_pause = 0
    p_any = 0
    p_click = 0
    if kU == 1 and oU == 0:
        pU = 1
    if kD == 1 and oD == 0:
        pD = 1
    if kL == 1 and oL == 0:
        pL = 1
    if kR == 1 and oR == 0:
        pR = 1
    if kA == 1 and oA == 0:
        pA = 1
    if kZ == 1 and oZ == 0:
        pZ = 1
    if kS == 1 and oS == 0:
        pS = 1
    if kH == 1 and oH == 0:
        pH = 1
    if kE == 1 and oE == 0:
        pE = 1
    if kP == 1 and oP == 0:
        p_pause = 1
    if kAny == 1 and oAny == 0:
        p_any = 1
    mdown = mouse_down()
    if mdown == 1 and oM == 0:
        p_click = 1
    p_ok = 0
    if (kN == 1 and oN == 0) or pE == 1 or pZ == 1 or (pA == 1 and mdown == 0):
        p_ok = 1
    oU = kU
    oD = kD
    oL = kL
    oR = kR
    oA = kA
    oZ = kZ
    oS = kS
    oH = kH
    oE = kE
    oN = kN
    oP = kP
    oAny = kAny
    oM = mdown


@proc
def shake_step():
    if shake > 0 and opt_shake == 1:
        shake -= 1
        shx = rand(0 - shake_amp, shake_amp)
        shy = rand(0 - shake_amp, shake_amp)
        if shake_amp > 1:
            shake_amp = shake_amp * 0.85
    else:
        shake = 0
        shx = 0
        shy = 0


@proc
def weather():
    if chapter == 0:
        if frame > next_flash:
            next_flash = frame + rand(240, 520)
            flash = 70
            thunder_at = frame + rand(8, 30)
        if frame == thunder_at:
            sfxq.append("thunder")


@proc
def open_menu(m):
    menu = m
    mode = "menu"
    broadcast("menu_build")


@proc
def go_title():
    mode = "title"
    ingame = 0
    menu = ""
    hint = ""
    boss_on = 0
    music_want = "title"
    fade_to = 0
    broadcast("clear")
    broadcast("menu_close")


@proc
def check_triggers():
    for ti in range(1, len(trig_x) + 1):
        if trig_on[ti] == 1 and px > trig_x[ti]:
            trig_on[ti] = 0
            broadcast(join("ev_", trig_ev[ti]))


@proc
def load_room(r):
    room = r
    rs = R_GRID[r]
    grid.clear()
    gi = 1
    for _ in range(690):
        grid.append(letter(gi, rs))
        gi += 1
    chapter = R_CH[r]
    wind = R_WIND[r]
    moving = R_MOVE[r]
    flip = 0
    flip_warn = 0
    tide_force = 0
    tide_lvl = 0
    tide_y = 0
    tide_t = 0
    tide_warn = 0
    GL_I.clear()
    GL_T.clear()
    if chapter == 6 or chapter == 7:
        for gi in range(1, 691):
            if grid[gi] == "G" or grid[gi] == "H":
                GL_I.append(gi)
                GL_T.append(grid[gi])
        gph = floor(frame / 100) % 2 * 2 + (frame % 100 >= 85)
        apply_phase()
    exL = R_L[r]
    exR = R_R[r]
    exU = R_U[r]
    exD = R_D[r]
    ent_type.clear()
    ent_x.clear()
    ent_y.clear()
    ent_w.clear()
    ent_h.clear()
    ent_hp.clear()
    ent_int.clear()
    ent_imax.clear()
    ent_alive.clear()
    ent_stag.clear()
    ent_dmg.clear()
    ent_idmg.clear()
    ent_kb.clear()
    ent_hk.clear()
    ent_foe.clear()
    ent_obj.clear()
    ent_brk.clear()
    ent_sev.clear()
    clear_queues()
    trig_x.clear()
    trig_ev.clear()
    trig_on.clear()
    o1 = O_FIRST[r]
    for oi in range(o1, o1 + O_NUM[r]):
        if O_TYPE[oi] == "trig":
            trig_x.append(O_X[oi])
            trig_ev.append(O_A[oi])
            trig_on.append(1)
    boss_on = 0
    ambush_on = 0
    mp_on = 0
    hint = ""
    prompt_on = 0
    hitstop = 0
    cage_broken = 0
    slot_state = "idle"
    backdrop(join("sky_", chapter))
    music_want = CH_MUSIC[chapter + 1]
    bk = R_BOSS[r]
    if (bk == 1 and boss_dead == 0) or (bk == 2 and dobu_dead == 0) or (bk == 3 and luck_dead == 0) or (bk == 4 and harm_dead == 0) or (bk == 5 and raijin_dead == 0) or (bk == 6 and kuro_dead == 0) or (bk == 7 and muk_dead == 0) or (bk == 8 and daimyo_dead == 0):
        music_want = "none"
    broadcast("clear")
    broadcast("spawn")


@proc
def say(name):
    dlg_req = name
    mode = "dlg"


@proc
def once(name):
    first = 0
    if not (name in seen):
        seen.append(name)
        first = 1


# ------------------------------------------------------------ sequences
@on("do_trans")
def do_trans():
    fade_to = 100
    wait_until(fade > 99)
    nr = want_room
    want_room = 0
    load_room(nr)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("do_respawn")
def do_respawn():
    music_want = "none"
    banner = "flatlined"
    wait(2.4)
    fade_to = 100
    wait_until(fade > 99)
    banner = ""
    respawn_state()
    enter_dir = "C"
    load_room(cp_room)
    wait(0)
    fade_to = 0
    sfxq.append("respawn")
    wait_until(fade < 50)
    mode = "play"


@on("new_game")
def new_game():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    reset_run()
    enter_dir = "S"
    load_room(C_ROOM_P1)
    wait(0)
    card = "ch0"
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@proc
def late_run(c):
    # state for starting at a later chapter from the chapter select
    reset_run()
    has_gourd = 1
    gourd = 3
    seen.append("tetsu")
    if c >= 2:
        gmax = 4
        gourd = 4
        boss_dead = 1
        daicam_done = 1
    if c >= 3:
        dobu_dead = 1
        daicam2_done = 1
    if c >= 4:
        luck_dead = 1
        daicam3_done = 1
    if c >= 5:
        harm_dead = 1
        daicam4_done = 1
    if c >= 6:
        raijin_dead = 1
        daicam5_done = 1
    if c >= 7:
        kuro_dead = 1
        daicam6_done = 1
        kbranch = kb_last
        if kbranch == 0:
            kbranch = 1
    if c >= 8:
        muk_dead = 1
        daicam7_done = 1


@proc_yield
def start_at(c):
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    late_run(c)
    enter_dir = "S"
    load_room(CH_ROOM[c + 1])
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("start_ch1")
def start_ch1():
    start_at(1)


@on("start_ch2")
def start_ch2():
    start_at(2)


@on("start_ch3")
def start_ch3():
    start_at(3)


@on("start_ch4")
def start_ch4():
    start_at(4)


@on("start_ch5")
def start_ch5():
    start_at(5)


@on("start_ch6")
def start_ch6():
    start_at(6)


@on("start_ch7")
def start_ch7():
    start_at(7)


@on("start_ch8")
def start_ch8():
    start_at(8)


@on("continue_game")
def continue_game():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    respawn_state()
    enter_dir = "C"
    load_room(cp_room)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("quit_to_title")
def quit_to_title():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    backdrop("black")
    go_title()


# ------------------------------------------------------------ story events
# Scene names are scene ids in story.json. kbranch: 0 undecided, 1 Kuro spared, 2 Kuro destroyed.
@proc
def say_b(name):
    # the branch variant of a scene ("<name>_alone" when Kuro was destroyed)
    if kbranch == 2:
        say(join(name, "_alone"))
    else:
        say(name)


@proc_yield
def say_once(name):
    once(name)
    if first == 1:
        say(name)
        wait_until(mode == "play")


@proc_yield
def chapter_open(c, x, y, scene):
    cp_room = room
    cp_x = x
    cp_y = y
    once(join("ch", c))
    if first == 1:
        card = join("ch", c)
        # hold Hotaru still under the chapter card, then go straight into the scene
        mode = "dlg"
        wait_until(card == "")
        say(scene)


@proc_yield
def boss_open(name, track, scene):
    hint = ""
    ambush_on = 1
    boss_on = 1
    boss_phase = 1
    boss_name = name
    music_want = track
    once(scene)
    if first == 1:
        say(scene)


@proc_yield
def boss_phase2(scene):
    boss_phase = 2
    broadcast("drums")
    once(scene)
    if first == 1:
        say(scene)


@proc_yield
def boss_down(delay):
    music_want = "none"
    wait(delay)
    banner = "victory"
    sfxq.append("victory")
    wait(3)
    banner = ""
    boss_on = 0


@proc
def chapter_jump(r):
    # scripted fall into the next chapter's first room
    mode = "trans"
    fade_to = 100
    wait_until(fade > 99)
    boss_on = 0
    enter_dir = "S"
    load_room(r)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


# ------------------------------------------------------------ prologue
@on("ev_boot")
def ev_boot():
    once("boot")
    if first == 1:
        wait(1.0)
        say("boot0")
        wait_until(mode == "play")
        p_cmd = "reboot"
        wait(1.6)
        say("boot")
        wait_until(mode == "play")
    hint = "move"


@on("ev_hint_jump")
def ev_hint_jump():
    hint = "jump"


@on("ev_hint_cling")
def ev_hint_cling():
    hint = "cling"


@on("ev_hint_attack")
def ev_hint_attack():
    say_once("drones")
    hint = "attack"


@on("ev_hint_deflect")
def ev_hint_deflect():
    say_once("turret")
    hint = "deflect"


@on("ev_hint_dash")
def ev_hint_dash():
    say_once("barrier")
    hint = "dash"


@on("ev_tetsu_seen")
def ev_tetsu_seen():
    if has_gourd == 0:
        hint = "talk"


@on("end_tetsu")
def ev_tetsu_done():
    has_gourd = 1
    gourd = gmax
    sfxq.append("pickup")
    hint = "heal"


@on("ev_edge")
def ev_edge():
    say_once("edge")


@on("ev_shard")
def ev_shard():
    banner = "shard"
    sfxq.append("shard")
    wait(2)
    banner = ""
    if shard_id >= 8:
        say_b(join("shard", shard_id))
    else:
        say(join("shard", shard_id))


# ------------------------------------------------------------ chapter 1: neon alley
@on("ev_ch1_start")
def ev_ch1_start():
    chapter_open(1, C_A1_X, C_A1_Y, "ch1")


@on("ev_hint_integrity")
def ev_hint_integrity():
    say_once("integrity")
    hint = "integrity"


@on("ev_daicam_start")
def ev_daicam_start():
    if daicam_done == 0:
        say_once("daicam1")
        hint = "heavy"


@on("ev_daicam_end")
def ev_daicam_end():
    hint = ""
    say("daicam2")
    wait_until(mode == "play")
    daicam_done = 1


@on("ev_hint_breach")
def ev_hint_breach():
    say_once("breach")
    hint = "breach"


@on("ev_ambush")
def ev_ambush():
    if len(ent_type) > 0:
        ambush_on = 1
        say_once("ambush")
        hint = "launch"


@on("ev_boss_gate")
def ev_boss_gate():
    if boss_dead == 0:
        say_once("boss_gate")
        hint = "gate_oni"


@on("ev_boss_start")
def ev_boss_start():
    if boss_dead == 0:
        boss_open("big_oni", "boss", "oni")


@on("ev_oni_phase2")
def ev_oni_phase2():
    boss_phase2("oni2")


@on("ev_oni_dead")
def ev_oni_dead():
    boss_dead = 1
    boss_down(1.4)
    gmax = 4
    gourd = gmax
    hint = "upgrade"
    sfxq.append("pickup")
    wait(2.5)
    say("oni_dead")
    wait_until(mode == "play")
    hint = ""
    music_want = "alley"


# ------------------------------------------------------------ chapter 2: the sewers
@on("ev_ch2_start")
def ev_ch2_start():
    chapter_open(2, C_W1_X, C_W1_Y, "ch2")


@on("ev_toxic")
def ev_toxic():
    say_once("toxic")
    hint = "toxic"


@on("ev_drainling")
def ev_drainling():
    if len(ent_type) > 0:
        say_once("drainling")
        hint = "drainling"


@on("ev_tide")
def ev_tide():
    say_once("tide")
    hint = "tide"


@on("ev_daicam_sewer")
def ev_daicam_sewer():
    if daicam2_done == 0 and len(ent_type) > 0:
        ambush_on = 1
        say_once("daicam_sewer")


@on("ev_daicam2_end")
def ev_daicam2_end():
    say("daicam_sewer2")
    wait_until(mode == "play")
    daicam2_done = 1


@on("ev_dobu_gate")
def ev_dobu_gate():
    if dobu_dead == 0:
        say_once("dobu_gate")
        hint = "gate_dobu"


@on("ev_dobu_start")
def ev_dobu_start():
    if dobu_dead == 0:
        boss_open("dobunushi", "dobu", "dobu")


@on("ev_dobu_phase2")
def ev_dobu_phase2():
    boss_phase2("dobu2")


@on("ev_dobu_dead")
def ev_dobu_dead():
    dobu_dead = 1
    boss_down(2.0)
    say("dobu_dead")
    wait_until(mode == "play")
    if chapter == 2:
        music_want = "sewers"


# ------------------------------------------------------------ chapter 3: the pachinko vaults
@on("ev_ch3_start")
def ev_ch3_start():
    chapter_open(3, C_B1_X, C_B1_Y, "ch3")


@on("ev_lasers")
def ev_lasers():
    say_once("lasers")
    hint = "lasergrid"


@on("ev_slots")
def ev_slots():
    say_once("slots")
    hint = "cards"


@on("ev_debtors")
def ev_debtors():
    say_once("debtors")


@on("ev_rollers")
def ev_rollers():
    say_once("rollers")


@on("ev_daicam3")
def ev_daicam3():
    if daicam3_done == 0:
        say_once("daicam3")
        hint = "cage"


@on("ev_daicam3_free")
def ev_daicam3_free():
    hint = ""
    say("daicam3b")
    wait_until(mode == "play")
    daicam3_done = 1


@on("ev_luck_gate")
def ev_luck_gate():
    if luck_dead == 0:
        say_once("luck_gate")
        hint = "gate_luck"


@on("ev_luck_start")
def ev_luck_start():
    if luck_dead == 0:
        boss_open("lady_luck", "luck", "luck")


@on("ev_luck_phase2")
def ev_luck_phase2():
    boss_phase2("luck2")


@on("ev_luck_dead")
def ev_luck_dead():
    luck_dead = 1
    boss_down(1.4)
    say("luck_dead")
    wait_until(mode == "play")
    if chapter == 3:
        music_want = "vaults"


# ------------------------------------------------------------ chapter 4: the physic gardens
@on("ev_ch4_start")
def ev_ch4_start():
    chapter_open(4, C_C1_X, C_C1_Y, "ch4")


@on("ev_vents")
def ev_vents():
    say_once("vents")
    hint = "mist"


@on("ev_warden")
def ev_warden():
    if len(ent_type) > 0:
        say_once("warden")
        hint = "warden"


@on("ev_pulse")
def ev_pulse():
    hint = "pulse"


@on("ev_daicam4")
def ev_daicam4():
    if daicam4_done == 0:
        say_once("daicam4")


@on("ev_daicam4_end")
def ev_daicam4_end():
    say("daicam4b")
    wait_until(mode == "play")
    daicam4_done = 1


@on("ev_pricing")
def ev_pricing():
    say_once("pricing")


@on("ev_harm_gate")
def ev_harm_gate():
    if harm_dead == 0:
        say_once("harm_gate")
        hint = "gate_harm"


@on("ev_harm_start")
def ev_harm_start():
    if harm_dead == 0:
        boss_open("the_harmacist", "harm", "harm")


@on("ev_harm_phase2")
def ev_harm_phase2():
    boss_phase2("harm2")


@on("ev_harm_dead")
def ev_harm_dead():
    harm_dead = 1
    music_want = "none"
    wait(0.9)
    say("harm_dead")
    wait_until(mode == "play")
    harm_dead = 2
    wait(2.6)
    boss_down(0)
    say("harm_dead2")
    wait_until(mode == "play")
    if chapter == 4:
        music_want = "gardens"


# ------------------------------------------------------------ chapter 5: monorail ascent
@on("ev_ch5_start")
def ev_ch5_start():
    chapter_open(5, C_D1_X, C_D1_Y, "ch5")


@on("ev_wind")
def ev_wind():
    say_once("wind")
    hint = "wind"


@on("ev_posts")
def ev_posts():
    say_once("posts")
    hint = "posts"


@on("ev_junction")
def ev_junction():
    say_once("junction")


@on("ev_daicam5")
def ev_daicam5():
    if daicam5_done == 0:
        say_once("daicam5")


@on("ev_daicam5_end")
def ev_daicam5_end():
    say("daicam5b")
    wait_until(mode == "play")
    daicam5_done = 1


@on("ev_raijin_gate")
def ev_raijin_gate():
    if raijin_dead == 0:
        once("raijin_gate")
        if first == 1:
            sfxq.append("cam_beep")
            flash = 30
            say("raijin_gate")
            wait_until(mode == "play")
            sfxq.append("horn")
        hint = "gate_raijin"


@on("ev_raijin_start")
def ev_raijin_start():
    if raijin_dead == 0:
        wait(1.2)
        boss_open("raijin", "raijin", "raijin")


@on("ev_raijin_phase2")
def ev_raijin_phase2():
    boss_phase2("raijin2")


@on("ev_raijin_dead")
def ev_raijin_dead():
    raijin_dead = 1
    boss_down(2.4)
    say("raijin_dead")
    wait_until(mode == "play")
    wait(0.6)
    sfxq.append("reboot")
    flash = 60
    say("record")
    wait_until(mode == "play")
    sfxq.append("flatline")
    flash = 90
    chapter_jump(C_ROOM_E1)


# ------------------------------------------------------------ chapter 6: hollow floor
@on("ev_ch6_start")
def ev_ch6_start():
    chapter_open(6, C_E1_X, C_E1_Y, "ch6")


@on("ev_glitch")
def ev_glitch():
    say_once("glitch")
    hint = "glitch"


@on("ev_sump_mem")
def ev_sump_mem():
    say_once("sump_mem")


@on("ev_tetsu_mem")
def ev_tetsu_mem():
    say_once("tetsu_mem")


@on("ev_academy_mem")
def ev_academy_mem():
    say_once("academy_mem")


@on("ev_possess")
def ev_possess():
    say_once("possess")
    hint = "possess"


@on("ev_white_room")
def ev_white_room():
    say_once("white_room")


@on("ev_daicam6")
def ev_daicam6():
    if daicam6_done == 0:
        say("daicam6")
        wait_until(mode == "play")
        daicam6_done = 1


@on("ev_kuro_gate")
def ev_kuro_gate():
    if kuro_dead == 0:
        say_once("kuro_gate")
        hint = "gate_kuro"


@on("ev_kuro_start")
def ev_kuro_start():
    if kuro_dead == 0:
        boss_open("kuro", "kuro", "kuro_fight")


@on("ev_kuro_phase2")
def ev_kuro_phase2():
    boss_phase2("kuro2")


@on("ev_kuro_choice")
def ev_kuro_choice():
    music_want = "none"
    flip = 0
    hint = "choice"
    say("kuro_choice")


@on("ev_kuro_dead")
def ev_kuro_dead():
    kuro_dead = 1
    hint = ""
    kb_last = kbranch
    wait(1.0)
    boss_on = 0
    if kbranch == 1:
        say("kuro_spared")
        wait_until(mode == "play")
        sfxq.append("respawn")
    else:
        say("kuro_destroyed")
        wait_until(mode == "play")
        sfxq.append("flatline")
    flash = 90
    chapter_jump(C_ROOM_F1)


# ------------------------------------------------------------ chapter 7: the academy
@on("ev_ch7_start")
def ev_ch7_start():
    if kbranch == 2:
        chapter_open(7, C_F1_X, C_F1_Y, "ch7_alone")
    else:
        chapter_open(7, C_F1_X, C_F1_Y, "ch7")


@on("ev_trainee")
def ev_trainee():
    if len(ent_type) > 0:
        once("trainee")
        if first == 1:
            say_b("trainee")
            wait_until(mode == "play")
        hint = "shell"


@on("ev_holo")
def ev_holo():
    if kbranch != 2:
        say_once("holo")


@on("ev_spar")
def ev_spar():
    if kbranch != 2:
        say_once("spar")


@on("ev_intake")
def ev_intake():
    if daicam7_done == 0 and len(ent_type) > 0:
        ambush_on = 1
        say_once("intake")


@on("ev_daicam7_end")
def ev_daicam7_end():
    say("intake2")
    wait_until(mode == "play")
    daicam7_done = 1


@on("ev_extraction")
def ev_extraction():
    if muk_dead == 0:
        once("extraction")
        if first == 1:
            say_b("extraction")
            wait_until(mode == "play")
        hint = "gate_muk"


@on("ev_muk_start")
def ev_muk_start():
    if muk_dead == 0:
        if kbranch == 2:
            boss_open("mukuro", "mukuro", "mukuro_alone")
        else:
            boss_open("mukuro", "mukuro", "mukuro")


@on("ev_muk_phase2")
def ev_muk_phase2():
    if kbranch == 2:
        boss_phase2("mukuro2_alone")
    else:
        boss_phase2("mukuro2")
    hint = "muk2"


@on("ev_muk_dead")
def ev_muk_dead():
    muk_dead = 1
    hint = ""
    muk_carry = 0
    boss_down(1.4)
    say_b("muk_dead")
    wait_until(mode == "play")
    if kbranch == 1:
        # Hotaru shoulders the body: Kuro will need it at the top
        walk_to = muk_bx - 14
        wtt = 0
        while abs(px - walk_to) > 5 and wtt < 120:
            wtt += 1
            wait(0)
        walk_to = 999
        sfxq.append("pickup")
        muk_carry = 1
        wait(0.6)
    wait(0.5)
    chapter_jump(C_ROOM_F9)


# ------------------------------------------------------------ chapter 8: the tenshu
@on("ev_ch8_start")
def ev_ch8_start():
    # riding up from the Spire Lift: let it arrive before the chapter card
    wait_until(py > C_LIFT_TOP - 4 or lift_ride == 0)
    if kbranch == 2:
        chapter_open(8, C_G1_X, C_G1_Y, "ch8_alone")
    else:
        chapter_open(8, C_G1_X, C_G1_Y, "ch8")


@on("ev_bailey")
def ev_bailey():
    if kbranch != 2:
        say_once("bailey")


@on("ev_grid")
def ev_grid():
    if kbranch != 2:
        say_once("grid")


@on("ev_muster")
def ev_muster():
    if daicam8_done == 0:
        say("muster")
        wait_until(mode == "play")
        daicam8_done = 1


@on("ev_transfer")
def ev_transfer():
    if kbranch == 1 and kuro_in == 0:
        say("transfer")
        wait(0.2)
        wait_until(dlg_spk == "system" or mode == "play")
        sfxq.append("sync")
        flash = 60
        kuro_in = 1
        wait_until(mode == "play")


@on("ev_throne")
def ev_throne():
    if daimyo_dead == 0:
        once("throne")
        if first == 1:
            say_b("throne")
            wait_until(mode == "play")
        hint = "gate_dm"


@on("ev_daimyo_start")
def ev_daimyo_start():
    if daimyo_dead == 0:
        boss_open("the_daimyo", "daimyo", "daimyo_fight")
        wait_until(mode == "play")
        if kbranch == 1:
            say_once("dm_ally")


@on("ev_dm_phase2")
def ev_dm_phase2():
    hint = "eye"
    wait(1.2)
    if kbranch == 2:
        boss_phase2("dm2_alone")
    else:
        boss_phase2("dm2")


@on("ev_kuro_falls")
def ev_kuro_falls():
    say_once("kuro_falls")


@on("ev_dm_phase3")
def ev_dm_phase3():
    music_want = "engram"
    hint = "duel3"
    wait(1.2)
    say_once("dm3")


@on("ev_dm_dead")
def ev_dm_dead():
    daimyo_dead = 1
    hint = ""
    boss_down(1.6)
    say("dm_dead")
    wait_until(mode == "play")
    if kbranch == 2:
        say("ending_alone")
        wait_until(mode == "play")
        flash = 60
    else:
        say("ending")
        wait(0.2)
        wait_until(dlg_spk == "system" or mode == "play")
        sfxq.append("sync")
        for k in range(6):
            cq_t.append("sync")
            cq_x.append(rand(-200, 200))
            cq_y.append(rand(-100, 120))
            cq_d.append(0)
            wait(0.25)
        flash = 100
        kuro_in = 2
        wait_until(mode == "play")
    wait(0.6)
    chapter_jump(C_ROOM_EP)


# ------------------------------------------------------------ epilogue
@on("ev_epilogue")
def ev_epilogue():
    cp_room = room
    card = "epi"
    wait(3)
    say("epilogue")
    wait_until(mode == "play")
    say("ep_hollowed")
    wait_until(mode == "play")
    if kbranch == 2:
        wait(0.6)
        sfxq.append("blip")
        wait(0.3)
        sfxq.append("blip")
        wait(0.6)
        say("ep_destroyed")
        wait_until(mode == "play")
    else:
        say("ep_spared")
        wait_until(mode == "play")
        wait(0.8)
        # the scarf flickers once in Kuro's color
        dash_ch = 1
        sfxq.append("kvoice")
        wait(0.35)
        dash_ch = 2
        wait(0.8)
        say("ep_spared2")
        wait_until(mode == "play")
    wait(1.5)
    mode = "trans"
    fade_to = 100
    wait_until(fade > 99)
    ingame = 0
    broadcast("clear")
    music_want = "title"
    backdrop("black")
    open_menu("end")
    fade_to = 0
