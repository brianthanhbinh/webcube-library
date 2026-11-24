#!/usr/bin/env python3
"""Generate pcubes dodecahedron puzzles (Megaminx, Gigaminx, ...) with N layers.

Run it (IDLE: F5) and type the number of layers when asked, or type  m  to make
several puzzles at once (it asks for start, step and end).  From a terminal:

    python gen_megaminx_puzzle.py 5          one puzzle
    python gen_megaminx_puzzle.py 3 2 9      start, step, end  (3, 5, 7, 9)

Files are named like "Megaminx 3x3.xml" / "Gigaminx 5x5.xml" and are written,
together with Figures\\Dodecahedron.xml, next to this script.  Needs
gen_megaminx_figure.py in the same folder.

How N works: N = number of layers along each axis (like a cube).  Cut planes
sit symmetrically on both sides of every axis, so
  odd N  (3, 5, 7, 9): Megaminx, Gigaminx, Teraminx, Petaminx - the middle slab
                       is not a normal move,
  even N (4, 6, 8 ...): same cuts as N-1 plus one plane through the centre, like
                       the 4x4 cube.  These are new puzzles (not real-world
                       ones) where the two middle slabs can also turn.
  N = 2 has no cap planes at all, only the 6 planes through the centre: every
        face turns half of the dodecahedron by 72 degrees (NOT a Kilominx).

Faces are lettered A..L.  A..F are the "positive" side of axes 0..5 and
G..L are their opposites (A-G, B-H, C-I, D-J, E-K, F-L).
"""
import os
import sys
from datetime import date

import gen_megaminx_figure as fig

# ---------------------------------------------------------------- settings
W = 0.5                       # same W you pass to <LoadFrom>; 0.5 matches Cube.xml
FIGURE_FILE = "Figures\\Dodecahedron.xml"
MENU_FOLDER = "Dodecahedral"
PROGRAMMER = ""               # put your name here (omitted when empty)
FACE_NAMES = "ABCDEFGHIJKL"   # macro letters; edit if you prefer other names
MIN_LAYERS = -10                # no upper limit (very high values give huge, slow puzzles)
# -------------------------------------------------------------------------

KNOWN = {3: "Megaminx", 5: "Gigaminx", 7: "Teraminx", 9: "Petaminx"}
HERE = os.path.dirname(os.path.abspath(__file__))


def unit(v):
    l = sum(c * c for c in v) ** 0.5
    return tuple(c / l for c in v)


def plane_distances(n):
    """Cut depths d_1 > d_2 > ... > d_K (K = n // 2), in units of W.

    Along an edge that leaves a face (from height r down to height h1) the
    face's planes cut at 1/n, 2/n, ...; the opposite end of the edge is cut by
    the neighbouring faces' planes.  Even n has one plane fewer per side
    (K = n/2 - 1) because the centre plane is added separately.
    """
    verts, _ = fig.build()
    n0 = unit(fig.NORMALS[0])
    heights = sorted({round(sum(a * b for a, b in zip(v, n0)), 9) for v in verts})
    r, h1 = heights[-1], heights[-2]
    length = r - h1
    k = n // 2 if n % 2 else n // 2 - 1
    return [r - m * length / n for m in range(1, k + 1)]


def make_xml(n):
    name = f"{KNOWN.get(n, 'Megaminx')} {n}x{n}"
    ds = [d * W for d in plane_distances(n)]
    k = len(ds)
    even = n % 2 == 0
    planes = [-d for d in ds] + ([0.0] if even else []) + list(reversed(ds))   # ascending
    axes = [unit(v) for v in fig.NORMALS[:6]]
    turns = max(100, 30 * n)

    o = []
    a = o.append
    a('<?xml version = "1.0" encoding = "UTF-8"?>')
    a('<xml Data_Version = "2" >')
    a("")
    a("    <Interface>")
    a(f"        <Name>{name}</Name>")
    a(f"        <Menu>{MENU_FOLDER}\\{name}</Menu>")
    if PROGRAMMER:
        a(f"        <Programmer>{PROGRAMMER}</Programmer>")
    a(f"        <Added>{date.today().isoformat()}</Added>")
    a("    </Interface>")
    a("")
    a(f'    <Axes TurningAngles = "2 * Pi / 5" PlaneDistances = "{"; ".join(f"{p:.6f}" for p in planes)}" >')
    for v in axes:
        a(f'        <Axis NormVector = "{v[0]:.9f}; {v[1]:.9f}; {v[2]:.9f}" />')
    a("    </Axes>")
    a("")
    a("    <Figure>")
    a(f'        <LoadFrom File = "{FIGURE_FILE}" W = "{W}" />')
    a("        <SplitByAxes/>")
    a("        <RemoveGrayParts/>")
    a("    </Figure>")
    a("")
    a("    <!-- Macros turn the outer layer of each face. Layers per axis: 0..%d (outer = 0 and %d) -->" % (n - 1, n - 1))
    a("    <Macros>")
    for i in range(12):
        axis, layer = (i, n - 1) if i < 6 else (i - 6, 0)
        s = -1 if layer else 1                              # clockwise seen from outside
        nm = FACE_NAMES[i]
        desc = f' Description = "{nm} - face {nm} clockwise, {nm}\' - counter-clockwise, {nm}2 - two steps"'
        def turn(steps):
            return f'<Turn Axis = "{axis}" Layer = "{layer}" Angle = "{s * steps}*2*Pi/5" />'
        a(f'        <Macro Name = "{nm} " Public = "1"{desc} > {turn(1)} </Macro>')
        a(f'        <Macro Name = "{nm}\'" Public = "0" > {turn(-1)} </Macro>')
        a(f'        <Macro Name = "{nm}2" Public = "0" > {turn(2)} </Macro>')
        a(f'        <Macro Name = "{nm}2\'" Public = "0" > {turn(-2)} </Macro>')
    a("")
    a('        <Macro Name = "RandomTurn" >')
    layer_expr = f"Random({n})" if even else f"Random({k}) + Random(2) * {k + 1}"
    a(f'            <Turn Axis = "Random(6)" Layer = "{layer_expr}" Angle = "2 * Pi / 5 * (Random(4) + 1)" />')
    a("        </Macro>")
    a(f'        <Macro Name = "Scramble" Public = "1" Description = "Replacing of standard scrambling" Sequence = "{turns} random turns" >')
    a(f'            <ExecMacro MacroName = "RandomTurn" Repeat = "{turns}" />')
    a("        </Macro>")
    a("    </Macros>")
    a("</xml>")
    return name, "\n".join(o) + "\n", ds


def write(n):
    os.makedirs(os.path.join(HERE, "Figures"), exist_ok=True)
    figures_dir = os.path.join(HERE, "Figures")
    os.makedirs(figures_dir, exist_ok=True)
    # Prefer the exact uploaded reference figure, using the conventional
    # filename expected by existing puzzle files and loaders.
    reference = os.path.join(HERE, "..", "figures", "Dodecahedron.xml")
    if os.path.isfile(reference):
        import shutil
        shutil.copyfile(reference, os.path.join(figures_dir, "Dodecahedron.xml"))
    else:
        # Fallback for standalone copies of this generator without the library.
        fig.write(os.path.join(figures_dir, "Dodecahedron.xml"))
    name, text, ds = make_xml(n)
    path = os.path.join(HERE, f"{name}.xml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"{name}: {n} layers -> {path}")


def ask_int(prompt, default, minimum):
    while True:
        s = input(f"{prompt} [{default}]: ").strip()
        if not s:
            return default
        try:
            v = int(s)
        except ValueError:
            print("  please type a whole number")
            continue
        if v < minimum:
            print(f"  choose {minimum} or more")
            continue
        return v


def write_range(start, step, end):
    layers = list(range(start, end + 1, step))
    for n in layers:
        write(n)
    print(f"Done: {len(layers)} puzzle(s) ({', '.join(str(n) for n in layers)} layers).")


def ask():
    while True:
        s = input(f"Number of layers ({MIN_LAYERS} or more, 3 = Megaminx, 5 = Gigaminx), "
                  "m = make several, blank = quit: ").strip().lower()
        if not s:
            return
        if s == "m":
            start = ask_int("  Start layers", MIN_LAYERS, MIN_LAYERS)
            step = ask_int("  Step", 2, 1)
            end = ask_int("  End layers", max(start, 9), start)
            write_range(start, step, end)
            continue
        try:
            n = int(s)
        except ValueError:
            print("  please type a whole number or m")
            continue
        if n < MIN_LAYERS:
            print(f"  choose {MIN_LAYERS} or more")
            continue
        write(n)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        write_range(*(int(a) for a in sys.argv[1:4]))
    elif len(sys.argv) > 1:
        write(int(sys.argv[1]))
    else:
        ask()
