#!/usr/bin/env python3
"""Generate pcubes cylinder puzzles: a round "can" cut like a cube.

The cylinder is cut by a G x G grid across the circle (planes along x and y)
and by L layers along its height (planes along z).  Like the 3x3x3 cube, but the
outline is round, so you get rounded corner and edge pieces.

Run it (IDLE: F5) and type sizes when asked.  Accepted forms:

    3          -> grid 3x3, 3 layers   (Cylinder 3x3x3)
    3x4        -> grid 3x3, 4 layers   (Cylinder 3x3x4)
    3x3x4      -> same as 3x4  (the first two numbers must be equal)
    3x3x2, 5x1 -> several puzzles at once (comma separated)

From a terminal:  python gen_cylinder_puzzle.py 3x3x3 4x2

Writes "Cylinder GxGxL.xml" and Figures\\Cylinder.xml next to this script.

Turning rules: the layers along the height turn by 90 degrees; the layers across
the circle (L/R and F/B) turn by 180 degrees only, because a can lying on its
side is not the same shape.  A direction with only 1 layer gets no turns.
"""
import math
import os
import re
import sys
from datetime import date

# ---------------------------------------------------------------- settings
DENOM = 6                     # layer thickness = 2/DENOM = 1/3 (the 3x3x3 cube has W = 0.5)
N_SIDES = 32                  # polygon sides that approximate the circle (multiple of 4)
FIGURE_FILE = "Figures\\Cylinder.xml"
MENU_FOLDER = "Cubic\\Cylinders"
PROGRAMMER = ""               # put your name here (omitted when empty)
# -------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))

# physical axes: (macro letter for layer 0, macro letter for last layer, normal vector)
AXES = [("L", "R", (1, 0, 0)), ("F", "B", (0, 1, 0)), ("D", "U", (0, 0, 1))]

# colours: wall +x, +y, -x, -y, then top, bottom
COLORS = ["C80000", "0000C8", "FF8000", "009600", "FFFFFF", "FFFF00"]


# ------------------------------------------------------------------ figure
def figure_xml():
    n = N_SIDES
    assert n % 4 == 0 and n >= 8, "N_SIDES must be a multiple of 4"
    ang = [-math.pi / 4 + 2 * math.pi * i / n for i in range(n)]
    o = ['<?xml version = "1.0" encoding = "UTF-8"?>', "<xml>", "    <Script>",
         "        if not VarExists('Colors[0]') then begin"]
    for i, col in enumerate(COLORS):
        o.append(f"            Colors[{i}] := '{col}';")
    o.append("        end;")
    o.append("")
    # bottom ring 0..n-1 (z = -Wh), top ring n..2n-1 (z = +Wh); Wr = radius
    for i, a in enumerate(ang):
        c, s = math.cos(a), math.sin(a)
        o.append(f"        Vx[{i}] := {c:.6f} * Wr; Vy[{i}] := {s:.6f} * Wr; Vz[{i}] := -Wh;")
        o.append(f"        Vx[{n + i}] := {c:.6f} * Wr; Vy[{n + i}] := {s:.6f} * Wr; Vz[{n + i}] := Wh;")
    o += ["    </Script>", "", "    <Part>", '        <Vertices Vectors = "Vx; Vy; Vz" />', "", "        <Faces>"]
    q = n // 4
    for i in range(n):                                   # wall quads, CCW seen from outside
        j = (i + 1) % n
        o.append(f'            <Face Color = "Colors[{i // q}]" VertexIndexes = "{i};{j};{n + j};{n + i}" />')
    top = ";".join(str(n + i) for i in range(n))
    bottom = ";".join(str(i) for i in reversed(range(n)))
    o.append(f'            <Face Color = "Colors[4]" VertexIndexes = "{top}" />')
    o.append(f'            <Face Color = "Colors[5]" VertexIndexes = "{bottom}" />')
    o += ["        </Faces>", "    </Part>", "</xml>"]
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ puzzle
def plane_list(n):
    """Cut positions for n layers, ascending, as exact fractions like '-1/6'."""
    return [f"{(2 * j - n)}/{DENOM}" if (2 * j - n) != 0 else "0" for j in range(1, n)]


def make_xml(g, layers):
    dims = (g, g, layers)
    name = f"Cylinder {g}x{g}x{layers}"

    info = []
    for k in range(3):
        n = dims[k]
        if n < 2:
            continue
        angle = "Pi / 2" if k == 2 else "Pi"          # height turns 90, across-the-circle turns 180
        info.append({"k": k, "n": n, "angle": angle, "planes": "; ".join(plane_list(n))})
    if not info:
        raise ValueError("need a grid of 2 or more, or 2 or more layers")

    groups = []
    for a in info:
        for gr in groups:
            if gr[0]["angle"] == a["angle"] and gr[0]["planes"] == a["planes"]:
                gr.append(a)
                break
        else:
            groups.append([a])
    order = [a for gr in groups for a in gr]
    for index, a in enumerate(order):
        a["index"] = index

    o = []
    ap = o.append
    ap('<?xml version = "1.0" encoding = "UTF-8"?>')
    ap('<xml Data_Version = "2" >')
    ap("")
    ap("    <Interface>")
    ap(f"        <Name>{name}</Name>")
    ap(f"        <Menu>{MENU_FOLDER}\\{name}</Menu>")
    if PROGRAMMER:
        ap(f"        <Programmer>{PROGRAMMER}</Programmer>")
    ap(f"        <Added>{date.today().isoformat()}</Added>")
    ap("    </Interface>")
    ap("")
    for gr in groups:
        ap(f'    <Axes TurningAngles = "{gr[0]["angle"]}" PlaneDistances = "{gr[0]["planes"]}" >')
        for a in gr:
            v = AXES[a["k"]][2]
            ap(f'        <Axis NormVector = "{v[0]}; {v[1]}; {v[2]}" />')
        ap("    </Axes>")
        ap("")
    radius = g / DENOM
    half_h = layers / DENOM
    ap("    <Figure>")
    ap(f'        <LoadFrom File = "{FIGURE_FILE}" Wr = "{radius:.6f}" Wh = "{half_h:.6f}" />')
    ap("        <SplitByAxes/>")
    ap("        <RemoveGrayParts/>")
    ap("    </Figure>")
    ap("")
    ap("    <Macros>")
    for a in info:
        lo, hi, _ = AXES[a["k"]]
        n, idx = a["n"], a["index"]
        quarter = a["angle"] == "Pi / 2"
        for letter, layer, sign in ((lo, 0, +1), (hi, n - 1, -1)):
            side = "first" if layer == 0 else "last"
            def ang(mult):
                if mult == 2:
                    return "Pi"
                return "Pi/2" if (mult == 1) == (sign > 0) else "-Pi/2"
            t = lambda mult: f'<Turn Axis = "{idx}" Layer = "{layer}" Angle = "{ang(mult)}" />'
            if quarter:
                ap(f'        <Macro Name = "{letter} " Public = "1" Description = "{letter} - {side} layer along the height clockwise, {letter}2 - double, {letter}\' - counter-clockwise" > {t(1)} </Macro>')
                ap(f'        <Macro Name = "{letter}2" Public = "0" > {t(2)} </Macro>')
                ap(f'        <Macro Name = "{letter}\'" Public = "0" > {t(-1)} </Macro>')
            else:
                ap(f'        <Macro Name = "{letter}2" Public = "1" Description = "{letter}2 - half turn of the {side} layer across the circle" > {t(2)} </Macro>')
    ap("")

    def rand_turn(a):
        return a["index"], a["n"], ("Pi/2 * (Random(3) + 1)" if a["angle"] == "Pi / 2" else "Pi")

    total = sum(a["n"] for a in info)
    turns = max(100, 10 * total)
    same = len({(a["n"], a["angle"]) for a in info}) == 1
    if same:
        a = info[0]
        ap('        <Macro Name = "RandomTurn" >')
        ap(f'            <Turn Axis = "Random({len(info)})" Layer = "Random({a["n"]})" Angle = "{rand_turn(a)[2]}" />')
        ap("        </Macro>")
        rep, mac = turns, "RandomTurn"
    else:
        ap('        <Macro Name = "RandomRound" >')
        for a in info:
            i, n, angle = rand_turn(a)
            ap(f'            <Turn Axis = "{i}" Layer = "Random({n})" Angle = "{angle}" />')
        ap("        </Macro>")
        rep, mac = max(1, turns // len(info)), "RandomRound"
    ap(f'        <Macro Name = "Scramble" Public = "1" Description = "Replacing of standard scrambling" Sequence = "{turns} random turns" >')
    ap(f'            <ExecMacro MacroName = "{mac}" Repeat = "{rep}" />')
    ap("        </Macro>")
    ap("    </Macros>")
    ap("</xml>")
    return name, "\n".join(o) + "\n"


# ------------------------------------------------------------------ I/O
def parse(spec):
    nums = [int(x) for x in re.split(r"[x*\s]+", spec.strip().lower()) if x]
    if len(nums) == 1:
        nums = nums * 3
    elif len(nums) == 2:
        nums = [nums[0], nums[0], nums[1]]
    if len(nums) != 3 or min(nums) < 1:
        raise ValueError("type 1, 2 or 3 positive numbers, like 3 or 3x4")
    if nums[0] != nums[1]:
        raise ValueError("the grid across the circle must be square (first two numbers equal)")
    return nums[0], nums[2]


def write(g, layers):
    os.makedirs(os.path.join(HERE, "Figures"), exist_ok=True)
    with open(os.path.join(HERE, "Figures", "Cylinder.xml"), "w", encoding="utf-8") as fh:
        fh.write(figure_xml())
    name, text = make_xml(g, layers)
    path = os.path.join(HERE, f"{name}.xml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"{name} -> {path}")


def write_many(specs):
    for s in specs:
        try:
            write(*parse(s))
        except ValueError as e:
            print(f"  skipped '{s}': {e}")


def ask():
    while True:
        s = input("Size (3 = 3x3x3, 3x4 = grid 3x3 with 4 layers, several with commas), blank = quit: ").strip()
        if not s:
            return
        write_many([x for x in s.split(",") if x.strip()])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        write_many(sys.argv[1:])
    else:
        ask()
