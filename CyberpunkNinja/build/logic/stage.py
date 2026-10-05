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
    luck_dead = 0
    muk_dead = 0
    muk_exit = 0
    daicam_done = 0
    daicam3_done = 0
    daicam4_done = 0
    daicam5_done = 0
    raijin_dead = 0
    wind = 0
    moving = 0
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
def read_input():
    kL = key("left arrow") or key("a")
    kR = key("right arrow") or key("d")
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
    if chapter == 0:
        backdrop("sky_sump")
        music_want = "sump"
    elif chapter == 1:
        backdrop("sky_neon_alley")
        music_want = "alley"
    elif chapter == 2:
        backdrop("sky_vaults")
        music_want = "vaults"
    elif chapter == 3:
        backdrop("sky_server_gardens")
        music_want = "gardens"
    else:
        backdrop("sky_rail")
        music_want = "monorail"
    if (R_BOSS[r] == 1 and boss_dead == 0) or (R_BOSS[r] == 2 and luck_dead == 0) or (R_BOSS[r] == 3 and muk_dead == 0) or (R_BOSS[r] == 4 and raijin_dead == 0):
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


@on("start_ch2")
def start_ch2():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    reset_run()
    has_gourd = 1
    gmax = 4
    gourd = 4
    boss_dead = 1
    daicam_done = 1
    seen.append("tetsu")
    enter_dir = "S"
    load_room(C_ROOM_B1)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("start_ch3")
def start_ch3():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    reset_run()
    has_gourd = 1
    gmax = 4
    gourd = 4
    boss_dead = 1
    luck_dead = 1
    daicam_done = 1
    daicam3_done = 1
    seen.append("tetsu")
    enter_dir = "S"
    load_room(C_ROOM_C1)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("start_ch4")
def start_ch4():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    reset_run()
    has_gourd = 1
    gmax = 4
    gourd = 4
    boss_dead = 1
    luck_dead = 1
    muk_dead = 1
    daicam_done = 1
    daicam3_done = 1
    daicam4_done = 1
    seen.append("tetsu")
    enter_dir = "S"
    load_room(C_ROOM_D1)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


@on("start_ch1")
def start_ch1():
    mode = "trans"
    broadcast("menu_close")
    fade_to = 100
    wait_until(fade > 99)
    reset_run()
    has_gourd = 1
    gourd = 3
    seen.append("tetsu")
    enter_dir = "S"
    load_room(C_ROOM_A1)
    wait(0)
    fade_to = 0
    wait_until(fade < 50)
    mode = "play"


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
    once("drones")
    if first == 1:
        say("drones")
        wait_until(mode == "play")
    hint = "attack"


@on("ev_hint_deflect")
def ev_hint_deflect():
    once("turret")
    if first == 1:
        say("turret")
        wait_until(mode == "play")
    hint = "deflect"


@on("ev_hint_dash")
def ev_hint_dash():
    once("barrier")
    if first == 1:
        say("barrier")
        wait_until(mode == "play")
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


@on("ev_lift_talk")
def ev_lift_talk():
    once("lift")
    if first == 1:
        say("lift")


@on("ev_ch1_start")
def ev_ch1_start():
    cp_room = room
    cp_x = C_A1_X
    cp_y = C_A1_Y
    once("ch1")
    if first == 1:
        card = "ch1"
        wait(2.5)
        say("ch1")


@on("ev_hint_integrity")
def ev_hint_integrity():
    once("integrity")
    if first == 1:
        say("integrity")
        wait_until(mode == "play")
    hint = "integrity"


@on("ev_daicam_start")
def ev_daicam_start():
    if daicam_done == 0:
        once("daicam1")
        if first == 1:
            say("daicam1")
            wait_until(mode == "play")
        hint = "heavy"


@on("ev_daicam_end")
def ev_daicam_end():
    hint = ""
    say("daicam2")
    wait_until(mode == "play")
    daicam_done = 1


@on("ev_hint_breach")
def ev_hint_breach():
    once("breach")
    if first == 1:
        say("breach")
        wait_until(mode == "play")
    hint = "breach"


@on("ev_ambush")
def ev_ambush():
    if len(ent_type) > 0:
        ambush_on = 1
        once("ambush")
        if first == 1:
            say("ambush")
            wait_until(mode == "play")
        hint = "launch"


@on("ev_boss_gate")
def ev_boss_gate():
    if boss_dead == 0:
        once("boss_gate")
        if first == 1:
            say("boss_gate")
            wait_until(mode == "play")
        hint = "heavy"


@on("ev_boss_start")
def ev_boss_start():
    if boss_dead == 0:
        ambush_on = 1
        boss_on = 1
        boss_phase = 1
        boss_name = "big_oni"
        music_want = "boss"
        once("oni")
        if first == 1:
            say("oni")


@on("ev_oni_phase2")
def ev_oni_phase2():
    boss_phase = 2
    broadcast("drums")
    once("oni2")
    if first == 1:
        say("oni2")


@on("ev_oni_dead")
def ev_oni_dead():
    boss_dead = 1
    music_want = "none"
    wait(1.4)
    banner = "victory"
    sfxq.append("victory")
    wait(3)
    banner = ""
    boss_on = 0
    gmax = 4
    gourd = gmax
    hint = "upgrade"
    sfxq.append("pickup")
    wait(2.5)
    say("oni_dead")
    wait_until(mode == "play")
    hint = ""
    music_want = "alley"


@on("ev_shard")
def ev_shard():
    banner = "shard"
    sfxq.append("shard")
    wait(2)
    banner = ""
    say(join("shard", shard_id))


# ------------------------------------------------------------ chapter 2
@on("ev_ch2_start")
def ev_ch2_start():
    cp_room = room
    cp_x = C_B1_X
    cp_y = C_B1_Y
    once("ch2")
    if first == 1:
        card = "ch2"
        wait(2.5)
        say("ch2")


@on("ev_lasers")
def ev_lasers():
    once("lasers")
    if first == 1:
        say("lasers")
        wait_until(mode == "play")
    hint = "lasergrid"


@on("ev_slots")
def ev_slots():
    once("slots")
    if first == 1:
        say("slots")
        wait_until(mode == "play")
    hint = "cards"


@on("ev_rollers")
def ev_rollers():
    once("rollers")
    if first == 1:
        say("rollers")


@on("ev_daicam3")
def ev_daicam3():
    if daicam3_done == 0:
        once("daicam3")
        if first == 1:
            say("daicam3")
            wait_until(mode == "play")
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
        once("luck_gate")
        if first == 1:
            say("luck_gate")
            wait_until(mode == "play")
        hint = "reels"


@on("ev_luck_start")
def ev_luck_start():
    if luck_dead == 0:
        hint = ""
        ambush_on = 1
        boss_on = 1
        boss_phase = 1
        boss_name = "lady_luck"
        music_want = "luck"
        once("luck")
        if first == 1:
            say("luck")


@on("ev_luck_phase2")
def ev_luck_phase2():
    boss_phase = 2
    broadcast("drums")
    once("luck2")
    if first == 1:
        say("luck2")


@on("ev_luck_dead")
def ev_luck_dead():
    luck_dead = 1
    music_want = "none"
    wait(1.4)
    banner = "victory"
    sfxq.append("victory")
    wait(3)
    banner = ""
    boss_on = 0
    say("luck_dead")
    wait_until(mode == "play")
    if chapter == 2:
        music_want = "vaults"


# ------------------------------------------------------------ chapter 3
@on("ev_ch3_start")
def ev_ch3_start():
    cp_room = room
    cp_x = C_C1_X
    cp_y = C_C1_Y
    once("ch3")
    if first == 1:
        card = "ch3"
        wait(2.5)
        say("ch3")


@on("ev_mist")
def ev_mist():
    once("mist")
    if first == 1:
        say("mist")
        wait_until(mode == "play")
    hint = "mist"


@on("ev_racks")
def ev_racks():
    once("racks")
    if first == 1:
        say("racks")


@on("ev_warden")
def ev_warden():
    if len(ent_type) > 0:
        once("warden")
        if first == 1:
            say("warden")
            wait_until(mode == "play")
        hint = "warden"


@on("ev_pulse")
def ev_pulse():
    hint = "pulse"


@on("ev_daicam4")
def ev_daicam4():
    if daicam4_done == 0:
        once("daicam4")
        if first == 1:
            say("daicam4")


@on("ev_daicam4_end")
def ev_daicam4_end():
    say("daicam4b")
    wait_until(mode == "play")
    daicam4_done = 1


@on("ev_muk_gate")
def ev_muk_gate():
    if muk_dead == 0:
        once("muk_gate")
        if first == 1:
            say("muk_gate")
            wait_until(mode == "play")
        hint = "duel"


@on("ev_muk_start")
def ev_muk_start():
    if muk_dead == 0:
        hint = ""
        ambush_on = 1
        boss_on = 1
        boss_phase = 1
        boss_name = "mukuro"
        music_want = "mukuro"
        once("mukuro")
        if first == 1:
            say("mukuro")


@on("ev_muk_phase2")
def ev_muk_phase2():
    boss_phase = 2
    broadcast("drums")
    once("mukuro2")
    if first == 1:
        say("mukuro2")


@on("ev_muk_dead")
def ev_muk_dead():
    muk_dead = 1
    music_want = "none"
    wait(1.4)
    banner = "victory"
    sfxq.append("victory")
    wait(3)
    banner = ""
    boss_on = 0
    say("muk_dead")
    wait_until(mode == "play")
    muk_exit = 1
    sfxq.append("muk_warp")
    wait(1.2)
    say("muk_gone")
    wait_until(mode == "play")
    if chapter == 3:
        music_want = "gardens"


# ------------------------------------------------------------ chapter 4
@on("ev_ch4_start")
def ev_ch4_start():
    cp_room = room
    cp_x = C_D1_X
    cp_y = C_D1_Y
    once("ch4")
    if first == 1:
        card = "ch4"
        wait(2.5)
        say("ch4")


@on("ev_wind")
def ev_wind():
    once("wind")
    if first == 1:
        say("wind")
        wait_until(mode == "play")
    hint = "wind"


@on("ev_posts")
def ev_posts():
    once("posts")
    if first == 1:
        say("posts")
        wait_until(mode == "play")
    hint = "posts"


@on("ev_junction")
def ev_junction():
    once("junction")
    if first == 1:
        say("junction")


@on("ev_daicam5")
def ev_daicam5():
    if daicam5_done == 0:
        once("daicam5")
        if first == 1:
            say("daicam5")


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
            sfxq.append("horn")
            say("raijin_gate")
            wait_until(mode == "play")
        hint = "raijin"


@on("ev_raijin_start")
def ev_raijin_start():
    if raijin_dead == 0:
        hint = ""
        ambush_on = 1
        boss_on = 1
        boss_phase = 1
        boss_name = "raijin"
        music_want = "raijin"
        once("raijin")
        if first == 1:
            wait(1.2)
            say("raijin")


@on("ev_raijin_phase2")
def ev_raijin_phase2():
    boss_phase = 2
    broadcast("drums")
    once("raijin2")
    if first == 1:
        say("raijin2")


@on("ev_raijin_dead")
def ev_raijin_dead():
    raijin_dead = 1
    music_want = "none"
    wait(2.4)
    banner = "victory"
    sfxq.append("victory")
    wait(3)
    banner = ""
    boss_on = 0
    say("raijin_dead")
    wait_until(mode == "play")
    wait(0.6)
    sfxq.append("reboot")
    flash = 60
    say("record")
    wait_until(mode == "play")
    wait(0.5)
    mode = "trans"
    fade_to = 100
    wait_until(fade > 99)
    ingame = 0
    broadcast("clear")
    music_want = "title"
    backdrop("black")
    open_menu("end")
    fade_to = 0
