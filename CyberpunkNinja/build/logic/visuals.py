# Effects, HUD, banners, hints, dialogue and screen layers (Scratch DSL).

# FX tables: name -> (frames, fps). Used to generate fx_info procs.
COMBAT_FX = {'deflect': (5, 16), 'hit': (4, 16), 'hit_enemy': (4, 16), 'explosion': (5, 14),
             'shockwave': (5, 12), 'heal': (6, 10), 'steam': (4, 8), 'sync': (6, 12)}
MOVE_FX = {'run_dust': (4, 12), 'land_dust': (4, 12), 'wall_spark': (3, 12),
           'afterimage': (1, 4), 'rain_splash': (3, 12)}


def fx_info(table):
    out = ['@proc', 'def fx_info(t):', '    nfr = 4', '    fps = 12']
    first = True
    for k, (n, f) in table.items():
        out.append('    %s t == "%s":' % ('if' if first else 'elif', k))
        out.append('        nfr = %d' % n)
        out.append('        fps = %d' % f)
        first = False
    return '\n'.join(out) + '\n'


def fx_sprite(queue, table):
    q = queue
    return fx_info(table) + '''
@on("t_draw")
def draw():
    if is_clone == 1:
        fx_draw()
    else:
        for qi in range(1, len(%(q)s_t) + 1):
            kind = %(q)s_t[qi]
            x = %(q)s_x[qi]
            y = %(q)s_y[qi]
            d = %(q)s_d[qi]
            fx_info(kind)
            fr = 0
            life = 0
            is_clone = 1
            clone()
            is_clone = 0
        %(q)s_t.clear()
        %(q)s_x.clear()
        %(q)s_y.clear()
        %(q)s_d.clear()


@proc
def fx_draw():
    life += 1
    if kind == "steam":
        if pst != "overheat":
            delete_clone()
        x = px
        y = py + 30
        costume(join("steam_", floor(fr) %% 4))
        fr += fps / 30
    elif kind == "afterimage":
        if life > 8:
            delete_clone()
        costume("afterimage_0")
        effect("ghost", 30 + life * 8)
    else:
        if fr >= nfr:
            delete_clone()
        costume(join(kind, "_", floor(fr)))
        fr += fps / 30
    goto(x + shx, y + shy)
    if d < 0:
        point(-90)
    else:
        point(90)
    show()
''' % {'q': q}


ENEMY_UI = '''
@clone
def ui_start():
    is_clone = 1
    slot = ui_slot[1]
    role = ui_role[1]
    ui_slot.delete(1)
    ui_role.delete(1)


@on("t_draw")
def draw():
    if is_clone == 1:
        if ent_alive[slot] == 0:
            delete_clone()
        if ent_alive[slot] != 1:
            hide()
            return
        ex = ent_x[slot]
        ey = ent_y[slot]
        eh = ent_h[slot]
        if role == "bar":
            if ent_int[slot] > 0 or ent_stag[slot] == 1:
                # Stance fills gold under pressure; full means broken
                costume(join("enemy_int_", min(8, round(ent_int[slot] * 8 / ent_imax[slot]))))
                goto(ex + shx, ey + eh + 12 + shy)
                show()
            else:
                hide()
        else:
            if ent_stag[slot] == 1:
                costume(join("severance_", floor(frame / 8) % 2))
                goto(ex + shx, ey + eh * 0.5 + shy)
                show()
            elif ent_brk[slot] == 1:
                costume(join("breach_", floor(frame / 4) % 4))
                goto(ex + shx, ey + eh + 26 + shy)
                show()
            else:
                hide()
'''


HUD = '''
@flag
def hud_init():
    hide()
    is_clone = 0
    role = ""


@on("boot")
def hud_boot():
    if is_clone == 0:
        for k in range(1, len(HUD_ROLES) + 1):
            role = HUD_ROLES[k]
            is_clone = 1
            clone()
            is_clone = 0
        role = ""


@on("t_draw")
def draw():
    if is_clone == 1:
        if ingame == 1 and (mode == "play" or mode == "dlg" or mode == "trans" or mode == "dead" or menu == "pause" or menu == "pause_options"):
            hud_draw()
        else:
            hide()


@proc
def hud_draw():
    if role == "hp":
        # a hit can take part of a segment (damage options, some bosses): a started segment shows
        hv = ceil(hp)
        if hv >= 10:
            costume("hp_10")
        else:
            costume(join("hp_0", max(0, hv)))
        goto(-232, 172)
        show()
        # the run's stopwatch, as the end screen counts it
        secs = floor(play_time / 30)
        if secs % 60 < 10:
            clk_s = join(floor(secs / 60), ":0", secs % 60)
        else:
            clk_s = join(floor(secs / 60), ":", secs % 60)
    elif role == "dash":
        # the Phase Step dot and the gourd sit in line with the health bar, to its right
        costume(join("dash_", dash_ch))
        goto(-118, 170)
        show()
    elif role == "gourd":
        if has_gourd == 1:
            costume(join("gourd_", gourd))
            goto(-96, 175)
            show()
        else:
            hide()
    elif "clk" in role:
        # one digit of the stopwatch, counted from the right
        ck = letter(4, role)
        if ck > strlen(clk_s):
            hide()
        else:
            costume(join("clk_", letter(strlen(clk_s) + 1 - ck, clk_s)))
            goto(234 - ck * 12, 172)
            show()
    elif role == "heat":
        # Hotaru's Stance works like everyone else's: it fills gold as she blocks, breaks when full
        pv = min(16, max(0, round(heat)))
        if pst == "overheat":
            if frame % 6 < 3:
                costume("heat_max_flash")
            else:
                costume("integrity_16")
        elif pv < 10:
            costume(join("integrity_0", pv))
        else:
            costume(join("integrity_", pv))
        goto(0, -154)
        show()
    elif role == "bplate":
        if boss_on == 1:
            costume(join("boss_", boss_name))
            goto(-164, 148)
            show()
        else:
            hide()
    elif role == "bbar":
        if boss_on == 1:
            bh = ceil(boss_hp)
            if bh < 10:
                costume(join("boss_0", max(0, bh)))
            else:
                costume(join("boss_", bh))
            goto(0, 124)
            show()
        else:
            hide()
    elif role == "bint":
        if boss_on == 1:
            bv = min(16, max(0, round(boss_int)))
            if bv < 10:
                costume(join("integrity_0", bv))
            else:
                costume(join("integrity_", bv))
            goto(0, 106)
            show()
        else:
            hide()
'''


HINTS = '''
@flag
def h_init():
    hide()
    is_clone = 0
    shown = ""
    alpha = 0


@on("boot")
def h_boot():
    if is_clone == 0:
        is_clone = 1
        clone()
        is_clone = 0


@on("t_draw")
def draw():
    if is_clone == 1:
        if prompt_on == 1 and mode == "play":
            if frame % 30 < 15:
                costume("key_e")
            else:
                costume("key_e_pressed")
            goto(prompt_x, prompt_y + sin(frame * 6) * 2)
            show()
        else:
            hide()
        prompt_on = 0
    else:
        want = hint
        if ingame == 0 or (mode != "play" and mode != "trans" and mode != "dead"):
            want = ""
        if want != shown:
            alpha -= 20
            if alpha <= 0:
                alpha = 0
                shown = want
        elif shown != "":
            alpha = min(100, alpha + 12)
        if shown == "" or alpha <= 0:
            hide()
            hint_hover = 0
        else:
            costume(join("hint_", shown))
            if boss_on == 1 and boss_hp > 0:
                goto(0, 64)
            else:
                goto(0, 104)
            effect("ghost", 100 - alpha)
            show()
            # a click on the card puts it away (and isn't an attack)
            hint_hover = touching_mouse()
            if hint_hover == 1 and p_click == 1 and want == shown:
                hint = ""
                sfxq.append("menu_back")
'''


BANNERS = '''
@flag
def b_init():
    hide()
    is_clone = 0
    role = "main"
    shown = ""


@on("boot")
def b_boot():
    if is_clone == 0:
        role = "kanji"
        is_clone = 1
        clone()
        role = "card"
        clone()
        is_clone = 0
        role = "main"


@on("t_draw")
def draw():
    if role == "main":
        if banner_t > 0:
            banner_t -= 1
            if banner_t == 0:
                banner = ""
        if banner != shown:
            shown = banner
            bt = 0
            if shown != "":
                sfxq.append("banner")
        bt += 1
        if shown == "":
            hide()
        else:
            costume(shown)
            size(100 + max(0, 30 - bt * 6))
            goto(0, 20)
            effect("ghost", max(0, 60 - bt * 15))
            show()
    elif role == "kanji":
        if banner == "flatlined":
            costume("kanji_death")
            goto(0, 100)
            effect("ghost", rand(0, 30))
            show()
        else:
            hide()
    elif role == "card":
        if card != "":
            if card != cshown:
                cshown = card
                ct = 0
                sfxq.append("card")
            ct += 1
            costume(card)
            if ct < 12:
                goto(-500 + ct * 42, 40)
            elif ct < 62:
                goto(0, 40)
            else:
                goto((ct - 62) * 42, 40)
            show()
            if ct > 75:
                card = ""
                cshown = ""
        else:
            hide()
'''


DIALOGUE = '''
@flag
def d_init():
    hide()
    is_clone = 0
    role = "ctl"
    dlg_on = 0
    dlg_spk = ""


@on("boot")
def d_boot():
    if is_clone == 0:
        for k in range(1, len(DLG_ROLES) + 1):
            role = DLG_ROLES[k]
            is_clone = 1
            clone()
            is_clone = 0
        role = "ctl"


@on("t_draw")
def draw():
    if is_clone == 0:
        d_ctl()
    else:
        d_draw()


@proc
def d_ctl():
    if dlg_req != "":
        ci = CONV_NAME.index(dlg_req)
        dlg_name = dlg_req
        dlg_req = ""
        if ci == 0:
            mode = "play"
        else:
            di = CONV_START[ci]
            dend = di + CONV_LEN[ci] - 1
            dlg_on = 1
            mode = "dlg"
            show_page()
    elif dlg_on == 1:
        dlg_t += 1
        # the page types out at 60 characters a second, ticking as it goes
        if dlg_c < dlg_n:
            dlg_c += 2
            if dlg_t % 2 == 1:
                if dlg_spk == "kuro":
                    sfxq.append("type_k")
                else:
                    sfxq.append("type")
        if dlg_t > 3 and (p_ok == 1 or p_click == 1 or pA == 1):
            if dlg_c < dlg_n:
                # a press while it types finishes the page
                dlg_c = dlg_n
            else:
                di += 1
                if di > dend:
                    dlg_on = 0
                    dlg_spk = ""
                    mode = "play"
                    broadcast(join("end_", dlg_name))
                else:
                    show_page()


@proc
def show_page():
    dlg_spk = DL_SPK[di]
    dlg_port = DL_PORT[di]
    dlg_txt = DL_TEXT[di]
    dlg_nm = DL_NAME[di]
    dlg_t = 0
    dlg_c = 0
    dlg_pg = di
    dlg_n = DLL_N[di * 3 - 2] + DLL_N[di * 3 - 1] + DLL_N[di * 3]
    if dlg_spk == "kuro":
        sfxq.append("kvoice")


@proc
def d_draw():
    if dlg_on == 0:
        hide()
        return
    if role == "box":
        costume("box")
        goto(0, 128)
    elif role == "port":
        costume(dlg_port)
        goto(-190, 129)
        if dlg_spk == "kuro":
            # a ghost in the machine: now and then his portrait tears and fills with static
            if gl_t > 0:
                gl_t -= 1
                costume(join(dlg_port, join("_g", 1 + floor(gl_t / 2) % 2)))
            elif rand(1, 45) == 1:
                gl_t = rand(3, 7)
            effect("ghost", rand(0, 25))
        else:
            gl_t = 0
            effect("ghost", 0)
    elif role == "name":
        costume(dlg_nm)
        goto(-136, 170)
    elif role == "text":
        costume(dlg_txt)
        goto(-136, 145)
    elif role == "arrow":
        if dlg_c < dlg_n:
            hide()
            return
        costume(join("next_", floor(frame / 8) % 2))
        goto(218, 92)
    else:
        # m1-m3: a strip of the box's own background over the part of each line not yet typed
        ml = letter(2, role)
        mi = dlg_pg * 3 - 3 + ml
        mc = dlg_c
        if ml > 1:
            mc -= DLL_N[dlg_pg * 3 - 2]
        if ml > 2:
            mc -= DLL_N[dlg_pg * 3 - 1]
        if mc >= DLL_N[mi]:
            hide()
            return
        if mc < 0:
            mc = 0
        # the strip reaches from the typed edge to the right margin, in steps of 4 stage px
        # (2 box pixels); each line sits 8 box rows below the last, so one set fits all three
        costume(join("mask_", ceil((176 - DLL_W[mi] * mc / DLL_N[mi] * 0.75) / 2)))
        goto(0, 128 - (ml - 1) * 16)
    show()
'''


KURO = '''
@flag
def k_init():
    hide()


@on("t_draw")
def draw():
    if dlg_on == 1 and dlg_spk == "kuro" and ingame == 1:
        costume(join("idle_", floor(frame / 5) % 4))
        kx = px - pface * 34
        if kx < -220:
            kx = px + 34
        if kx > 220:
            kx = px - 34
        goto(kx + rand(-1, 1) * (rand(1, 10) > 8) * 3, py + 6 + sin(frame * 5) * 3)
        if kx > px:
            point(-90)
        else:
            point(90)
        effect("ghost", rand(35, 55))
        show()
    else:
        hide()
'''


FADE = '''
@flag
def f_init():
    goto(0, 0)
    show()


@on("t_draw")
def draw():
    if fade < fade_to:
        fade = min(fade_to, fade + 34)
    elif fade > fade_to:
        fade = max(fade_to, fade - 34)
    if fade <= 0:
        hide()
    else:
        costume("black")
        goto(0, 0)
        effect("ghost", 100 - fade)
        show()
'''


FLASH = '''
@flag
def fl_init():
    hide()


@on("t_draw")
def draw():
    if flash > 0 and ingame == 1:
        costume("white")
        goto(0, 0)
        effect("ghost", 100 - flash)
        show()
        flash = max(0, flash - 12)
    else:
        hide()
'''


RAIN = '''
@flag
def r_init():
    hide()


@on("t_draw")
def draw():
    live = 0
    if ingame == 1 and (mode == "play" or mode == "dlg" or mode == "trans" or mode == "dead" or menu == "pause"):
        live = 1
    if live == 1 and (flip == 1 or flip_warn == 1):
        costume("possess")
        goto(0, 0)
        if flip == 1:
            effect("ghost", 20)
        else:
            effect("ghost", 30 + (frame % 6 < 3) * 50)
        show()
    elif live == 1 and (chapter < 2 or chapter == 9):
        costume(join("rain_", floor(frame / 3) % 4))
        goto(0, 0)
        effect("ghost", 15)
        show()
    elif live == 1 and wind != 0:
        costume(join("wind_", floor(frame / 2) % 4))
        goto(0, 0)
        effect("ghost", 20)
        show()
    else:
        hide()
'''


def parallax(k, auto=0):
    return '''
@flag
def p_init():
    hide()
    is_clone = 0


@on("boot")
def p_boot():
    if is_clone == 0:
        is_clone = 1
        clone()
        is_clone = 0


@on("t_draw")
def draw():
    if ingame == 1 and (mode != "menu" or menu == "pause"):
        costume(join("ch", chapter))
        po = (0 - px * %s - frame * %s * moving) %% 480
        gj = 0
        if chapter == 5 and frame %% 70 < 3:
            # Hollow Floor's memory skips like a bad tape
            gj = rand(-10, 10)
            effect("color", rand(-40, 40))
        else:
            effect("color", 0)
        # the clouds catch the sunrise
        effect("brightness", dawn * 0.12)
        if is_clone == 1:
            goto(po - 480 + gj, 0)
        else:
            goto(po + gj, 0)
        show()
    else:
        hide()
''' % (k, auto)


LEVEL = '''
@flag
def l_init():
    hide()


@on("t_draw")
def draw():
    if ingame == 1 and (mode != "menu" or menu == "pause"):
        if frame % 24 < 12:
            costume(R_LEVEL[room])
        else:
            costume(R_LEVEL2[room])
        goto(-240 + shx, 180 + shy)
        show()
    else:
        hide()
'''


SFX = '''
@flag
def s_init():
    hide()
    volume(80)


@on("t_draw")
def draw():
    for si in range(1, len(sfxq) + 1):
        play(sfxq[si])
    sfxq.clear()


@on("sfx_vol")
def vol():
    volume(opt_sfx * 20)
'''


def music(track, length, drums=False, drums_for='boss'):
    cond = 'music_cur == "%s"' % (drums_for if drums else track)
    vol = '(boss_phase == 2) * opt_music * 20' if drums else 'opt_music * 20'
    return '''
@flag
def m_init():
    hide()
    volume(0)


@on("music")
def m_go():
    if %(cond)s:
        volume(%(vol)s)
        while %(cond)s:
            play("%(track)s")
            wait(%(len)s)
    else:
        volume(0)


@on("music_vol")
def m_vol():
    if %(cond)s:
        volume(%(vol)s)


@on("drums")
def m_drums():
    if %(cond)s:
        volume(%(vol)s)
''' % {'cond': cond, 'vol': vol, 'track': track, 'len': length}


AMBIENCE = '''
@flag
def a_init():
    hide()
    volume(0)
    amb = 0


@on("t_draw")
def draw():
    want = 0
    if ingame == 1 and mode != "menu" and (chapter < 2 or chapter == 9):
        want = 1
    if ingame == 1 and mode != "menu" and chapter == 4 and moving == 1:
        want = 2
    if want != amb:
        amb = want
        broadcast("amb")


@on("amb")
def amb_go():
    if amb == 1:
        volume(opt_sfx * 9)
        while amb == 1:
            play("rain_loop")
            wait(C_RAIN_LEN)
    elif amb == 2:
        volume(opt_sfx * 7)
        while amb == 2:
            play("wind_loop")
            wait(C_WIND_LEN)
    else:
        volume(0)
'''


# Hollow Floor is a memory coming apart: glitch pieces flicker behind the rooms.
GLITCHBG = '''
@flag
def g_init():
    hide()
    is_clone = 0


@on("boot")
def g_boot():
    if is_clone == 0:
        for k in range(5):
            is_clone = 1
            gt = k * 9
            clone()
        is_clone = 0


@on("t_draw")
def draw():
    if is_clone == 0:
        return
    if ingame == 1 and chapter == 5 and (mode != "menu" or menu == "pause"):
        gt -= 1
        if gt <= 0:
            gt = rand(4, 40)
            gon = rand(2, 7)
            costume(join("glitch_", rand(0, 11)))
            gx = rand(-220, 220)
            gy = rand(-60, 170)
        if gon > 0:
            gon -= 1
            goto(gx + rand(-3, 3), gy)
            effect("ghost", rand(10, 50))
            show()
        else:
            hide()
    else:
        hide()
'''


# The Extraction and Muster Halls: the hollowed army stands in silhouette behind the room.
RANKS = '''
@flag
def r_init():
    hide()


@on("t_draw")
def draw():
    if ingame == 1 and (room == C_ROOM_G5 or room == C_ROOM_F7) and (mode != "menu" or menu == "pause"):
        costume("ranks")
        goto(0 - px * 0.08, -124)
        show()
    else:
        hide()
'''


# The Tenshu's sky, between the backdrop and the clouds: the moon sets as Hotaru climbs
# (its height per room is R_MOON; 999 = down), and after the Daimyo the dawn comes up
# behind the clouds (dawn counts 0 to 150).
SKY = '''
@flag
def k_init():
    hide()
    is_clone = 0
    role = "orb"


@on("boot")
def k_boot():
    if is_clone == 0:
        # a clone sits just behind its parent: the dawn sky, under the moon and sun
        role = "dawn"
        is_clone = 1
        clone()
        is_clone = 0
        role = "orb"


@on("t_draw")
def draw():
    if ingame == 0 or chapter != 8 or (mode == "menu" and menu != "pause"):
        hide()
        return
    if role == "dawn":
        if dawn > 0:
            costume("dawn")
            goto(0, 0)
            effect("ghost", 100 - dawn * 100 / 150)
            show()
        else:
            hide()
    elif dawn > 0:
        costume("sun")
        goto(70 - px * 0.02, -150 + dawn * 1.3)
        show()
    elif R_MOON[room] < 900:
        costume("moon")
        goto(104 - px * 0.02, R_MOON[room])
        show()
    else:
        hide()
'''


SPLASH = '''
@flag
def sp_init():
    hide()


@on("t_draw")
def draw():
    if mode == "splash":
        costume("splash")
        goto(0, 0)
        if splash_t < 20:
            effect("ghost", 100 - splash_t * 5)
        elif splash_t < 100:
            effect("ghost", 0)
        else:
            effect("ghost", min(100, (splash_t - 100) * 5.6))
        show()
    else:
        hide()
'''
