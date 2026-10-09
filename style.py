"""Console UI — Professional Gradient Dashboard Style."""

import os, sys, re, shutil

if sys.platform == "win32":
    os.system("")

def _tw():
    return min(shutil.get_terminal_size((90, 24)).columns, 110)

def _plain(s):
    return re.sub(r'\033\[[^m]*m', '', str(s))

def _len(s):
    return len(_plain(s))

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    WHITE  = "\033[97m"
    SILVER = "\033[37m"
    GRAY   = "\033[90m"
    TEAL   = rgb(0,   230, 200)
    AMBER  = rgb(255, 185, 40)
    ROSE   = rgb(255, 75,  105)
    SAGE   = rgb(80,  220, 130)
    STEEL  = rgb(90,  175, 255)
    GOLD   = rgb(255, 210, 60)
    MINT   = rgb(60,  240, 180)
    GREEN  = rgb(80,  220, 130)
    YELLOW = rgb(255, 200, 50)
    RED    = rgb(255, 70,  95)
    CYAN   = rgb(0,   230, 200)

class Box:
    X="╬"; tl="╭"; tr="╮"; bl="╰"; br="╯"; h="─"; v="│"
    lt="├"; rt="┤"; tt="┬"; bt="┴"

try:
    from pyfiglet import figlet_format as _figlet
    _HAS_FIGLET = True
except ImportError:
    _HAS_FIGLET = False

def _grad_text(text, r1, g1, b1, r2, g2, b2):
    n = max(len(text) - 1, 1)
    out = ""
    for i, ch in enumerate(text):
        t = i / n
        out += rgb(int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t)) + ch
    return out + C.RESET

def _grad_line_bg(char, w, fr1,fg1,fb1, fr2,fg2,fb2, br1,bg1,bb1, br2,bg2,bb2):
    n, out = max(w-1, 1), ""
    for i in range(w):
        t = i / n
        out += (bg_rgb(int(br1+(br2-br1)*t), int(bg1+(bg2-bg1)*t), int(bb1+(bb2-bb1)*t)) +
                rgb(int(fr1+(fr2-fr1)*t), int(fg1+(fg2-fg1)*t), int(fb1+(fb2-fb1)*t)) + char)
    print(out + C.RESET)

def _grad_line_str_bg(s, fr1,fg1,fb1, fr2,fg2,fb2, br1,bg1,bb1, br2,bg2,bb2):
    n, out = max(len(s)-1, 1), ""
    for i, ch in enumerate(s):
        t = i / n
        out += (bg_rgb(int(br1+(br2-br1)*t), int(bg1+(bg2-bg1)*t), int(bb1+(bb2-bb1)*t)) +
                rgb(int(fr1+(fr2-fr1)*t), int(fg1+(fg2-fg1)*t), int(fb1+(fb2-fb1)*t)) + ch)
    print(out + C.RESET)

def _print_big(text, r1, g1, b1, r2, g2, b2, center_w=0, font="standard"):
    raw   = _figlet(text, font=font) if _HAS_FIGLET else "  " + "  ".join(text.upper()) + "\n"
    lines = [l.rstrip() for l in raw.split("\n")]
    while lines and not lines[0].strip():  lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop()
    if not lines: return
    max_w = max(len(l) for l in lines)
    pad   = max(0, (center_w - max_w) // 2) if center_w else 2
    for line in lines:
        out = ""
        for i, ch in enumerate(line):
            t = i / max(max_w-1, 1)
            out += rgb(int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t)) + ch
        print(" " * pad + C.BOLD + out + C.RESET)

def login_screen():
    w = _tw()
    print()
    _grad_line_bg("▄", w, 0,230,200, 120,80,255, 10,10,22, 25,15,55)
    print()
    _print_big("ATTENDANCE", 0,230,200,  80,160,255, center_w=w)
    _print_big("MANAGEMENT", 80,160,255, 160,80,255, center_w=w)
    _print_big("SYSTEM",    160,80,255,  210,60,180, center_w=w)
    print()
    sub  = "v2.0  ·  Smart Tracker  ·  2026"
    pad  = (w - len(sub)) // 2
    line = " " * pad + sub + " " * max(0, w - pad - len(sub))
    print(f"{bg_rgb(20,18,50)}{C.DIM}{C.SILVER}{line}{C.RESET}")
    _grad_line_bg("▀", w, 210,60,180, 0,230,200, 25,15,55, 10,10,22)
    print()

def section(title: str):
    w, label = _tw(), f"  {title}  "
    print()
    print(f"{C.TEAL}{Box.lt}{Box.h}{C.RESET}"
          f"{C.BOLD}{_grad_text(label, 0,230,200, 190,100,255)}{C.RESET}"
          f"{_grad_text(Box.h * (w - 2 - len(label)), 190,100,255, 25,20,60)}"
          f"{C.TEAL}{Box.rt}{C.RESET}")
    print()

def menu(title: str, items: list):
    w = _tw()
    print()
    _grad_line_bg("═", w, 0,230,200, 190,100,255, 10,10,22, 22,15,50)
    print()
    _print_big(title, 0,230,200, 190,100,255, center_w=w)
    print()
    _grad_line_bg("─", w, 190,100,255, 0,230,200, 22,15,50, 10,10,22)
    mid, col_w, row_bg = (len(items)+1)//2, (w-4)//2, bg_rgb(14,13,30)
    for i in range(mid):
        lkey, llabel = items[i]
        right  = items[i+mid] if (i+mid) < len(items) else None
        l_text = f"{C.BOLD}{_grad_text(f' {lkey:>2}', 255,185,40, 255,110,80)}{C.RESET}  {C.SILVER}{llabel}{C.RESET}"
        l_pad  = max(0, col_w - len(f" {lkey:>2}  {llabel}"))
        r_text = (f"{C.BOLD}{_grad_text(f' {right[0]:>2}', 255,185,40, 255,110,80)}{C.RESET}  {C.SILVER}{right[1]}{C.RESET}"
                  if right else "")
        print(f"{row_bg}  {l_text}{' '*l_pad}  {r_text}{C.RESET}")
    _grad_line_bg("═", w, 0,230,200, 190,100,255, 10,10,22, 22,15,50)
    print()

_HDR_S  = (0,230,200);  _HDR_E  = (190,100,255)
_HDR_BS = (18,16,45);   _HDR_BE = (28,14,55)
_ROW_GRADS = [((0,200,180),(150,80,240)), ((0,160,150),(110,60,200))]
_ROW_BG    = [(14,13,28), (20,18,38)]

def _col_widths(headers, rows):
    w = [_len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(w): w[i] = max(w[i], _len(str(cell)))
    return w

def _colorize_cell(val: str, header: str) -> str:
    h, v = header.lower(), val.strip()
    if v.endswith("%"):
        try:
            p = float(v.rstrip("%"))
            if p >= 75: return f"{C.BOLD}{C.SAGE}{v}{C.RESET}"
            if p >= 50: return f"{C.BOLD}{C.AMBER}{v}{C.RESET}"
            return f"{C.BOLD}{C.ROSE}{v}{C.RESET}"
        except ValueError: pass
    status_map = {"P":(C.SAGE,"● Present"),"L":(C.AMBER,"◐ Late   "),"A":(C.ROSE,"○ Absent "),"PR":(C.STEEL,"◑ Permit ")}
    if v in status_map and "status" in h:
        col, lbl = status_map[v]; return f"{C.BOLD}{col}{lbl}{C.RESET}"
    if h == "present":    return f"{C.SAGE}{v}{C.RESET}"
    if h == "absent":     return f"{C.ROSE}{v}{C.RESET}"
    if h == "late":       return f"{C.AMBER}{v}{C.RESET}"
    if h == "permission": return f"{C.STEEL}{v}{C.RESET}"
    if v in ("🥇","🥈","🥉"): return f"{C.BOLD}{C.GOLD}{v}{C.RESET}"
    if v.startswith("#"): return f"{C.GRAY}{v}{C.RESET}"
    if "⚠" in v:          return f"{C.AMBER}{v}{C.RESET}"
    if h in ("id","sid","course id","course_id"): return f"{C.MINT}{v}{C.RESET}"
    return f"{C.SILVER}{v}{C.RESET}"

def styled_table(headers: list, rows: list, title: str = ""):
    if not rows: return warn("No records found")
    if title: title_line(title)
    widths = [w+2 for w in _col_widths(headers, rows)]

    _grad_line_str_bg(Box.tl + Box.tt.join(Box.h*w for w in widths) + Box.tr, *_HDR_S,*_HDR_E,*_HDR_BS,*_HDR_BE)

    n, cells = max(len(headers)-1, 1), []
    for i, h in enumerate(headers):
        t   = i/n
        r,g,b   = int(_HDR_S[0]+(_HDR_E[0]-_HDR_S[0])*t), int(_HDR_S[1]+(_HDR_E[1]-_HDR_S[1])*t), int(_HDR_S[2]+(_HDR_E[2]-_HDR_S[2])*t)
        br,bg_,bb = int(_HDR_BS[0]+(_HDR_BE[0]-_HDR_BS[0])*t), int(_HDR_BS[1]+(_HDR_BE[1]-_HDR_BS[1])*t), int(_HDR_BS[2]+(_HDR_BE[2]-_HDR_BS[2])*t)
        pad = widths[i]-_len(h); lp = pad//2
        cells.append(f"{bg_rgb(br,bg_,bb)}{C.BOLD}{rgb(r,g,b)}{' '*lp}{h}{' '*(pad-lp)}{C.RESET}")
    bc, bbc = rgb(*_HDR_S), bg_rgb(*_HDR_BS)
    print(f"{bbc}{bc}{Box.v}{C.RESET}" + f"{bbc}{bc}{Box.v}{C.RESET}".join(cells) + f"{bbc}{bc}{Box.v}{C.RESET}")

    _grad_line_str_bg(Box.lt + Box.X.join(Box.h*w for w in widths) + Box.rt, *_HDR_S,*_HDR_E,*_HDR_BS,*_HDR_BE)

    for ri, row in enumerate(rows):
        rs, re_ = _ROW_GRADS[ri%2]; rbc = _ROW_BG[ri%2]
        n2, cells = max(len(row)-1, 1), []
        for ci, cell in enumerate(row):
            t  = ci/n2
            r_ = int(rs[0]+(re_[0]-rs[0])*t); g_ = int(rs[1]+(re_[1]-rs[1])*t); b_ = int(rs[2]+(re_[2]-rs[2])*t)
            val = _colorize_cell(str(cell), headers[ci] if ci < len(headers) else "")
            pad = widths[ci]-_len(str(cell))
            cells.append(f"{bg_rgb(*rbc)}{rgb(r_,g_,b_)} {C.RESET}{bg_rgb(*rbc)}{val}{' '*(pad-1)}{C.RESET}")
        rb, rbb = rgb(55,50,100), bg_rgb(*rbc)
        print(f"{rbb}{rb}{Box.v}{C.RESET}" + f"{rbb}{rb}{Box.v}{C.RESET}".join(cells) + f"{rbb}{rb}{Box.v}{C.RESET}")
        if ri < len(rows)-1:
            _grad_line_str_bg(Box.lt + Box.X.join(Box.h*w for w in widths) + Box.rt, 35,30,80,55,45,110,12,11,24,18,16,34)

    _grad_line_str_bg(Box.bl + Box.bt.join(Box.h*w for w in widths) + Box.br, *_HDR_E,*_HDR_S,*_HDR_BE,*_HDR_BS)
    print()

def success(msg: str):
    w = _tw(); text = f"  ✓  {msg}  "
    print(f"\n{C.BOLD}{bg_rgb(10,60,45)}{_grad_text(text + ' '*max(0,w-len(text)), 0,230,200, 80,220,130)}{C.RESET}\n")

def error(msg: str):
    print(f"\n{C.BOLD}{bg_rgb(70,15,25)}{C.ROSE}  ✗  {msg}  {C.RESET}\n")

def warn(msg: str):
    print(f"{C.BOLD}{bg_rgb(55,38,8)}{C.AMBER}  ▲  {msg}  {C.RESET}")

def info(msg: str):
    print(f"  {C.GRAY}·{C.RESET}  {C.SILVER}{msg}{C.RESET}")

def title_line(msg: str):
    w = _tw()
    print()
    print(f"{C.TEAL}{Box.lt}{Box.h*2}{C.RESET}"
          f"{C.BOLD}{_grad_text(f'  {msg}  ', 0,230,200, 190,100,255)}{C.RESET}"
          f"{C.GRAY}{Box.h*max(0,w-len(msg)-6)}{Box.rt}{C.RESET}")
    print()

def prompt(label: str) -> str:
    return input(f"  {_grad_text('❯', 0,230,200, 190,100,255)}  {C.SILVER}{label}{C.GRAY}:{C.RESET} ")

def pct_bar(pct: float, width: int = 20) -> str:
    filled = int(pct/100*width); empty = "▒"*(width-filled)
    if pct >= 75:   color, bar = rgb(80,220,130), _grad_text("█"*filled, 0,230,200, 80,220,130)
    elif pct >= 50: color, bar = rgb(255,185,40), _grad_text("█"*filled, 255,220,80, 255,140,30)
    else:           color, bar = rgb(255,70,95),  _grad_text("█"*filled, 255,120,80, 255,50,90)
    return f"{C.DIM}{C.GRAY}[{C.RESET}{bar}{C.DIM}{C.GRAY}{empty}]{C.RESET} {C.BOLD}{color}{pct:.1f}%{C.RESET}"
    if h == "late":       return f"{C.AMBER}{v}{C.RESET}"
    if h == "permission": return f"{C.STEEL}{v}{C.RESET}"
    if v in ("🥇","🥈","🥉"): return f"{C.BOLD}{C.GOLD}{v}{C.RESET}"
    if v.startswith("#"): return f"{C.GRAY}{v}{C.RESET}"
    if "⚠" in v:          return f"{C.AMBER}{v}{C.RESET}"
    if h in ("id","sid","course id","course_id"): return f"{C.MINT}{v}{C.RESET}"
    return f"{C.SILVER}{v}{C.RESET}"

# ── Notifications ─────────────────────────────────────────────────────────────
def success(msg: str):
    w    = _tw()
    text = f"  ✓  {msg}  "
    line = text + " " * max(0, w - len(text))
    print(f"\n{C.BOLD}{bg_rgb(10,60,45)}{_grad_text(line, 0,230,200, 80,220,130)}{C.RESET}\n")

def error(msg: str):
    print(f"\n{C.BOLD}{bg_rgb(70,15,25)}{C.ROSE}  ✗  {msg}  {C.RESET}\n")

def warn(msg: str):
    print(f"{C.BOLD}{bg_rgb(55,38,8)}{C.AMBER}  ▲  {msg}  {C.RESET}")

def info(msg: str):
    print(f"  {C.GRAY}·{C.RESET}  {C.SILVER}{msg}{C.RESET}")

def title_line(msg: str):
    w    = _tw()
    rest = max(0, w - len(msg) - 6)
    print()
    print(f"{C.TEAL}{Box.lt}{Box.h*2}{C.RESET}"
          f"{C.BOLD}{_grad_text(f'  {msg}  ', 0,230,200, 190,100,255)}{C.RESET}"
          f"{C.GRAY}{Box.h*rest}{Box.rt}{C.RESET}")
    print()

def prompt(label: str) -> str:
    return input(f"  {_grad_text('❯', 0,230,200, 190,100,255)}  {C.SILVER}{label}{C.GRAY}:{C.RESET} ")

def pct_bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    empty  = "▒" * (width - filled)
    if pct >= 75:
        color = rgb(80,220,130);  bar = _grad_text("█"*filled, 0,230,200, 80,220,130)
    elif pct >= 50:
        color = rgb(255,185,40);  bar = _grad_text("█"*filled, 255,220,80, 255,140,30)
    else:
        color = rgb(255,70,95);   bar = _grad_text("█"*filled, 255,120,80, 255,50,90)
    return f"{C.DIM}{C.GRAY}[{C.RESET}{bar}{C.DIM}{C.GRAY}{empty}]{C.RESET} {C.BOLD}{color}{pct:.1f}%{C.RESET}"

def status_badge(status: str) -> str:
    m = {"P":(C.SAGE,"PRESENT"),"L":(C.AMBER,"LATE"),"A":(C.ROSE,"ABSENT"),"PR":(C.STEEL,"PERMIT")}
    col, lbl = m.get(status, (C.GRAY, status))
    return f"{C.BOLD}{col}[{lbl}]{C.RESET}"
