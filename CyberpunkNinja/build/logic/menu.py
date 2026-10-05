# Menus: main menu, options (assist mode), chapters, credits, controls, pause, end.

MENU = '''
@flag
def m_init():
    hide()
    is_clone = 0
    ckind = ""
    msel = 1
    press_t = 0
    pend = ""
    chap_i = 0


@on("menu_close")
def m_close():
    if is_clone == 1:
        delete_clone()
    else:
        hide()
        broadcast("text_clear")


@on("menu_build")
def m_build():
    if is_clone == 1:
        delete_clone()
    else:
        build()


@proc
def build():
    MI_KEY.clear()
    MI_X.clear()
    MI_Y.clear()
    MI_KIND.clear()
    msel = 1
    press_t = 0
    pend = ""
    menu_t = 0
    broadcast("text_clear")
    if menu == "main":
        add_btn("new_game", 0, 22)
        add_btn("continue", 0, -12)
        add_btn("chapters", 0, -46)
        add_btn("options", 0, -80)
        add_btn("credits", 0, -114)
        add_btn("quit", 0, -148)
        if has_save == 1:
            msel = 2
    elif menu == "pause":
        add_deco("pause", 0, 20)
        add_btn("resume", 0, 44)
        add_btn("options", 0, 8)
        add_btn("quit", 0, -28)
    elif menu == "options" or menu == "pause_options":
        add_deco("panel", 0, 0)
        add_deco("ttl_options", 0, 158)
        add_deco("ttl_assist", -150, 134)
        add_opt("wide", 110)
        add_opt("slow", 86)
        add_opt("heat", 62)
        add_opt("gourd", 38)
        add_opt("god", 14)
        add_opt("music", -18)
        add_opt("sfx", -42)
        add_opt("shake", -66)
        add_opt("controls", -96)
        add_btn("back", 0, -142)
    elif menu == "chapters":
        add_deco("panel", 0, 0)
        add_deco("ttl_chapters", 0, 150)
        add_item("prev", "arrow", -208, 50)
        add_item("card", "card", 0, 50)
        add_item("next", "arrow", 208, 50)
        add_deco("chap_label", 0, -20)
        add_btn("back", 0, -142)
        msel = 2
    elif menu == "credits" or menu == "credits_end":
        add_deco("panel", 0, 0)
        add_deco("credits_page", 0, 18)
        add_btn("back", 0, -142)
    elif menu == "controls":
        add_deco("panel", 0, 0)
        add_deco("controls_page", 0, 22)
        add_btn("back", 0, -146)
    elif menu == "end":
        add_deco("end_page", 0, 60)
        add_deco("press_any_key", 0, -150)
        end_stats()
    if len(MI_KEY) > 0:
        ckind = "cursor"
        cidx = 0
        is_clone = 1
        clone()
        is_clone = 0


@proc
def end_stats():
    secs = floor(play_time / 30)
    mins = floor(secs / 60)
    secs = secs % 60
    if secs < 10:
        tstr = join(mins, ":0", secs)
    else:
        tstr = join(mins, ":", secs)
    broadcast("text_write")


@proc
def add_btn(k, x, y):
    add_item(k, "btn", x, y)


@proc
def add_item(k, kind, x, y):
    MI_KEY.append(k)
    MI_X.append(x)
    MI_Y.append(y)
    MI_KIND.append(kind)
    ckind = kind
    ckey = k
    cx = x
    cy = y
    cidx = len(MI_KEY)
    is_clone = 1
    clone()
    is_clone = 0


@proc
def add_opt(k, y):
    add_deco(join("lbl_", k), -212, y)
    add_item(k, "opt", 148, y)


@proc
def add_deco(c, x, y):
    ckind = "deco"
    ccos = c
    cx = x
    cy = y
    cidx = 0
    is_clone = 1
    clone()
    is_clone = 0


@on("t_draw")
def draw():
    if is_clone == 1:
        m_draw()
    elif mode == "menu":
        m_ctl()


@proc
def m_ctl():
    n = len(MI_KEY)
    menu_t += 1
    if menu_t < 4:
        omx = mouse_x()
        omy = mouse_y()
        return
    if menu == "end":
        if p_any == 1:
            sfxq.append("menu_select")
            menu = "credits_end"
            broadcast("menu_build")
        return
    if n == 0:
        return
    if press_t > 0:
        press_t -= 1
        if press_t == 0:
            activate(pend)
        return
    old = msel
    if pU == 1:
        step_sel(-1)
    if pD == 1:
        step_sel(1)
    mx = mouse_x()
    my = mouse_y()
    if mx != omx or my != omy:
        for k in range(1, n + 1):
            item_w(k)
            if abs(mx - MI_X[k]) < iw and abs(my - MI_Y[k]) < 15:
                if not (MI_KEY[k] == "continue" and has_save == 0):
                    msel = k
    omx = mx
    omy = my
    if msel != old:
        sfxq.append("menu_move")
    sk = MI_KEY[msel]
    if pL == 1 or pR == 1:
        if MI_KIND[msel] == "opt":
            change_opt(sk, pR - pL)
        elif sk == "card":
            change_chap(pR - pL)
    clicked = 0
    if p_click == 1:
        item_w(msel)
        if abs(mx - MI_X[msel]) < iw and abs(my - MI_Y[msel]) < 15:
            clicked = 1
    if p_ok == 1 or clicked == 1:
        if MI_KIND[msel] == "opt":
            change_opt(sk, 1)
        elif MI_KIND[msel] == "arrow":
            if sk == "prev":
                change_chap(-1)
            else:
                change_chap(1)
        elif not (sk == "continue" and has_save == 0):
            sfxq.append("menu_select")
            pend = sk
            press_t = 4


@proc
def item_w(k):
    if MI_KIND[k] == "card":
        iw = 170
    elif MI_KIND[k] == "arrow":
        iw = 16
    elif MI_KIND[k] == "opt":
        iw = 70
    else:
        iw = 78


@proc
def step_sel(dv):
    msel += dv
    if msel < 1:
        msel = len(MI_KEY)
    if msel > len(MI_KEY):
        msel = 1
    if MI_KEY[msel] == "continue" and has_save == 0:
        msel += dv


@proc
def change_opt(k, dv):
    sfxq.append("menu_move")
    if k == "wide":
        opt_wide = 1 - opt_wide
    elif k == "slow":
        opt_slow = 1 - opt_slow
    elif k == "heat":
        opt_heat = 1 - opt_heat
    elif k == "gourd":
        opt_gourd = 1 - opt_gourd
    elif k == "god":
        opt_god = 1 - opt_god
    elif k == "shake":
        opt_shake = 1 - opt_shake
    elif k == "music":
        opt_music = (opt_music + dv) % 6
        broadcast("music_vol")
    elif k == "sfx":
        opt_sfx = (opt_sfx + dv) % 6
        broadcast("sfx_vol")
    elif k == "controls":
        sfxq.append("menu_select")
        if menu == "pause_options":
            ctl_from = "pause_options"
        else:
            ctl_from = "options"
        menu = "controls"
        broadcast("menu_build")


@proc
def change_chap(dv):
    chap_i = (chap_i + dv) % 8
    sfxq.append("menu_move")


@proc
def activate(k):
    if k == "new_game":
        broadcast("new_game")
    elif k == "continue":
        broadcast("continue_game")
    elif k == "chapters":
        menu = "chapters"
        broadcast("menu_build")
    elif k == "options":
        if menu == "pause":
            menu = "pause_options"
        else:
            menu = "options"
        broadcast("menu_build")
    elif k == "credits":
        menu = "credits"
        broadcast("menu_build")
    elif k == "quit":
        broadcast("quit_to_title")
    elif k == "resume":
        menu = ""
        mode = "play"
        broadcast("menu_close")
    elif k == "card":
        if chap_i == 0:
            broadcast("new_game")
        elif chap_i == 1:
            broadcast("start_ch1")
        else:
            sfxq.append("empty")
    elif k == "back":
        sfxq.append("menu_back")
        if menu == "pause_options":
            menu = "pause"
        elif menu == "credits_end":
            menu = "main"
            music_want = "title"
        elif menu == "controls":
            menu = ctl_from
        else:
            menu = "main"
        broadcast("menu_build")


@proc
def m_draw():
    if ckind == "cursor":
        k = msel
        if MI_KIND[k] == "opt":
            goto(MI_X[k] - 92, MI_Y[k] - 2)
        elif MI_KIND[k] == "card":
            hide()
            return
        elif MI_KIND[k] == "arrow":
            goto(MI_X[k], MI_Y[k] - 34)
        else:
            goto(MI_X[k] - 98, MI_Y[k] - 2)
        costume(join("spin_", floor(frame / 3) % 4))
        show()
        return
    st = "normal"
    if msel == cidx:
        st = "hover"
        if press_t > 0:
            st = "pressed"
    if ckind == "btn":
        if ckey == "continue" and has_save == 0:
            st = "disabled"
        costume(join(ckey, "_", st))
    elif ckind == "opt":
        if ckey == "music":
            vv = join("vol", opt_music)
        elif ckey == "sfx":
            vv = join("vol", opt_sfx)
        elif ckey == "controls":
            vv = "view"
        else:
            if ckey == "wide":
                ov = opt_wide
            elif ckey == "slow":
                ov = opt_slow
            elif ckey == "heat":
                ov = opt_heat
            elif ckey == "gourd":
                ov = opt_gourd
            elif ckey == "god":
                ov = opt_god
            else:
                ov = opt_shake
            if ov == 1:
                vv = "on"
            else:
                vv = "off"
        if st == "pressed":
            st = "hover"
        costume(join("val_", vv, "_", st))
    elif ckind == "arrow":
        if ckey == "prev":
            costume("key_left")
        else:
            costume("key_right")
        if st == "hover":
            effect("brightness", 30)
        else:
            effect("brightness", 0)
    elif ckind == "card":
        costume(join("ch", chap_i))
        size(88)
        if chap_i > 1:
            effect("brightness", -55)
        elif msel == cidx and frame % 30 < 15:
            effect("brightness", 15)
        else:
            effect("brightness", 0)
    elif ccos == "chap_label":
        if chap_i < 2:
            costume("lbl_play")
        else:
            costume("lbl_locked")
    elif ccos == "press_any_key":
        costume(ccos)
        if frame % 40 < 20:
            effect("ghost", 0)
        else:
            effect("ghost", 70)
    else:
        costume(ccos)
    goto(cx, cy)
    show()
'''


TEXTFX = '''
@flag
def t_init():
    hide()
    is_clone = 0


@on("text_clear")
def t_clear():
    if is_clone == 1:
        delete_clone()


@on("text_write")
def t_write():
    if is_clone == 0:
        write_line(join("TIME   ", tstr), -70, -6)
        write_line(join("DEATHS   ", deaths), -70, -30)
        write_line(join("MEMORY SHARDS   ", shards, " / 2"), -70, -54)


@proc
def write_line(s, x, y):
    tx = x
    for i in range(1, strlen(s) + 1):
        costume(join("ch_", letter(i, s)))
        gw = FONT_W[costume_num()]
        goto(tx, y)
        is_clone = 1
        clone()
        is_clone = 0
        tx += gw * 2 + 2


@clone
def t_show():
    show()
'''
