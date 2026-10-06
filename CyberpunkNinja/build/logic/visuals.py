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
        if dash_ch >= 1:
            costume("afterimage_0")
        else:
            costume("afterimage_1")
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
        if ent_alive[slot] != 1:
            delete_clone()
        ex = ent_x[slot]
        ey = ent_y[slot]
        eh = ent_h[slot]
        if role == "bar":
            if ent_int[slot] > 0 or ent_stag[slot] == 1:
                costume(join("enemy_int_", round(ent_int[slot] * 8 / ent_imax[slot])))
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
        if hp >= 10:
            costume("hp_10")
        else:
            costume(join("hp_0", max(0, hp)))
        goto(-232, 172)
        show()
    elif role == "dash":
        costume(join("dash_", dash_ch))
        goto(-230, 147)
        show()
    elif role == "gourd":
        if has_gourd == 1:
            if opt_gourd == 1:
                costume("gourd_3")
            else:
                costume(join("gourd_", gourd))
            goto(-192, 151)
            show()
        else:
            hide()
    elif role == "heat":
        if pst == "overheat":
            if frame % 6 < 3:
                costume("heat_max_flash")
            else:
                costume("heat_16")
        elif heat < 10:
            costume(join("heat_0", max(0, round(heat))))
        else:
            costume(join("heat_", min(16, round(heat))))
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
            if boss_hp < 10:
                costume(join("boss_0", max(0, boss_hp)))
            else:
                costume(join("boss_", boss_hp))
            goto(0, 124)
            show()
        else:
            hide()
    elif role == "bint":
        if boss_on == 1:
            if boss_int < 10:
                costume(join("integrity_0", round(boss_int)))
            else:
                costume(join("integrity_", round(boss_int)))
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
        else:
            costume(join("hint_", shown))
            if boss_on == 1 and boss_hp > 0:
                goto(0, 64)
            else:
                goto(0, 104)
            effect("ghost", 100 - alpha)
            show()
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
            elif ct < 80:
                goto(0, 40)
            else:
                goto((ct - 80) * 42, 40)
            show()
            if ct > 94:
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
        for k in range(1, 6):
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
        if dlg_t > 8 and (p_ok == 1 or p_click == 1 or pA == 1):
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
    if dlg_spk == "kuro":
        sfxq.append("kuro")
    else:
        sfxq.append("blip")


@proc
def d_draw():
    if dlg_on == 0:
        hide()
        return
    if role == "box":
        costume("box")
        goto(0, -124)
    elif role == "port":
        costume(dlg_port)
        goto(-190, -123)
        if dlg_spk == "kuro":
            effect("ghost", rand(0, 25))
        else:
            effect("ghost", 0)
    elif role == "name":
        costume(dlg_nm)
        goto(-140, -64)
    elif role == "text":
        costume(dlg_txt)
        goto(-136, -88)
        effect("ghost", max(0, 80 - dlg_t * 20))
    elif role == "arrow":
        costume(join("next_", floor(frame / 8) % 2))
        goto(220, -160)
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
    elif live == 1 and (chapter < 2 or chapter == 8):
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
        if chapter == 0:
            costume("sump")
        elif chapter == 1:
            costume("neon_alley")
        elif chapter == 2:
            costume("vaults")
        elif chapter == 3:
            costume("server_gardens")
        elif chapter == 4:
            costume("rail")
        elif chapter == 5:
            costume("hollow")
        elif chapter == 6:
            costume("academy")
        elif chapter == 7:
            costume("tenshu")
        else:
            costume("sump")
        po = (0 - px * %s - frame * %s * moving) %% 480
        if is_clone == 1:
            goto(po - 480, 0)
        else:
            goto(po, 0)
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
        costume(R_LEVEL[room])
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
    if ingame == 1 and mode != "menu" and (chapter < 2 or chapter == 8):
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
