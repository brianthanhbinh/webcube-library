#!/usr/bin/env python3
"""Generate pcubes cuboid puzzles (a x b x c layers) like 3x3x2, 2x3x4, 5x5x1 ...

Run it (IDLE: F5) and type sizes when asked.  Accepted forms:

    3            -> 3x3x3 cube
    5x3          -> 5x3x3   (5 layers long, 3x3 square ends, like a 5x3 cube)
    2x3x4        -> 2x3x4
    3x3x2, 2x3x4 -> several puzzles at once (comma separated)

From a terminal:  python gen_cuboid_puzzle.py 3x3x2 2x3x4

The three numbers are the layers along x (left-right), y (front-back) and
z (down-up), the same axes as the L/R, F/B, D/U macros of the 3x3x3 cube.

Writes "Cuboid AxBxC.xml" ("Cube NxNxN.xml" when all three are equal) and
Figures\\Cuboid.xml next to this script.

Turning rules: a layer turn rotates the cross-section of the other two
directions.  If that cross-section is square the layer turns by 90 degrees and
keeps the cuboid shape.  If it is a rectangle, the layer can still be turned by
90 degrees (QUARTER_TURNS_ON_RECTANGLES = True; the cuboid becomes shape-shifted
and pcubes blocks turns that would cut through pieces) and by 180 degrees (which
keeps the shape, as on a real 3x3x2).  Scrambling only uses shape-keeping turns.
Directions that have only 1 layer get no turns.
"""
import math
import os
import re
import sys
from datetime import date

# ---------------------------------------------------------------- settings
DENOM = 6                     # layer thickness = 2/DENOM = 1/3 (the 3x3x3 cube has W = 0.5)
QUARTER_TURNS_ON_RECTANGLES = True   # also allow 90-degree turns where the cross-section is a rectangle
                              # (the cuboid then changes shape until you turn it back); False = 180 only
FIGURE_FILE = "Figures\\Cuboid.xml"
MENU_FOLDER = "Cubic\\Cuboids"
PROGRAMMER = ""               # put your name here (omitted when empty)
# -------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))

# physical axes: (macro letter for layer 0, macro letter for last layer, normal vector)
AXES = [("L", "R", (1, 0, 0)), ("F", "B", (0, 1, 0)), ("D", "U", (0, 0, 1))]

# face colours: +x, -x, +y, -y, +z, -z   (R, L, B, F, U, D)
COLORS = ["C80000", "FF8000", "0000C8", "009600", "FFFFFF", "FFFF00"]


# ------------------------------------------------------------------ figure
def figure_xml():
    verts = [(sx, sy, sz) for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]
    normals = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

    def dot(p, q):
        return sum(x * y for x, y in zip(p, q))

    def cross(p, q):
        return (p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0])

    faces = []
    for n in normals:
        idx = [i for i, v in enumerate(verts) if dot(v, n) == 1]
        ref = (0, 0, 1) if abs(n[2]) == 0 else (1, 0, 0)
        u = cross(n, ref)
        w = cross(n, u)
        idx.sort(key=lambda i: math.atan2(dot(verts[i], w), dot(verts[i], u)))   # CCW seen from outside
        faces.append(idx)

    def c(v, name):
        return ("-" if v < 0 else "") + name

    o = ['<?xml version = "1.0" encoding = "UTF-8"?>', "<xml>", "    <Script>",
         "        if not VarExists('Colors[0]') then begin"]
    for i, col in enumerate(COLORS):
        o.append(f"            Colors[{i}] := '{col}';")
    o.append("        end;")
    o.append("")
    for i, (x, y, z) in enumerate(verts):
        o.append(f"        Vx[{i}] := {c(x, 'Wx')}; Vy[{i}] := {c(y, 'Wy')}; Vz[{i}] := {c(z, 'Wz')};")
    o += ["    </Script>", "", "    <Part>", '        <Vertices Vectors = "Vx; Vy; Vz" />', "", "        <Faces>"]
    for i, f in enumerate(faces):
        o.append(f'            <Face Color = "Colors[{i}]" VertexIndexes = "{";".join(map(str, f))}" />')
    o += ["        </Faces>", "    </Part>", "</xml>"]
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ puzzle
def plane_list(n):
    """Cut positions for n layers, ascending, as exact fractions like '-1/6'."""
    return [f"{(2 * j - n)}/{DENOM}" if (2 * j - n) != 0 else "0" for j in range(1, n)]


def make_xml(dims):
    nx, ny, nz = dims
    if all(d == dims[0] for d in dims):
        name = f"Cube {nx}x{ny}x{nz}"
    else:
        name = f"Cuboid {nx}x{ny}x{nz}"

    # describe the axes that can turn (more than one layer)
    info = []
    for k in range(3):
        n = dims[k]
        if n < 2:
            continue
        p, q = [dims[j] for j in range(3) if j != k]
        square = p == q
        angle = "Pi / 2" if (square or QUARTER_TURNS_ON_RECTANGLES) else "Pi"
        info.append({"k": k, "n": n, "angle": angle, "square": square, "planes": "; ".join(plane_list(n))})
    if not info:
        raise ValueError("at least one direction needs 2 or more layers")

    # group axes with identical settings into one <Axes> block (indices follow block order)
    groups = []
    for a in info:
        for g in groups:
            if g[0]["angle"] == a["angle"] and g[0]["planes"] == a["planes"]:
                g.append(a)
                break
        else:
            groups.append([a])
    order = [a for g in groups for a in g]
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
    for g in groups:
        ap(f'    <Axes TurningAngles = "{g[0]["angle"]}" PlaneDistances = "{g[0]["planes"]}" >')
        for a in g:
            v = AXES[a["k"]][2]
            ap(f'        <Axis NormVector = "{v[0]}; {v[1]}; {v[2]}" />')
        ap("    </Axes>")
        ap("")
    half = [f"{d / DENOM:.6f}" for d in dims]
    ap("    <Figure>")
    ap(f'        <LoadFrom File = "{FIGURE_FILE}" Wx = "{half[0]}" Wy = "{half[1]}" Wz = "{half[2]}" />')
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
                v = {1: "Pi/2", 2: "Pi", -1: "-Pi/2"}[mult]
                return v if sign > 0 or mult == 2 else ({"Pi/2": "-Pi/2", "-Pi/2": "Pi/2"}[v])
            t = lambda mult: f'<Turn Axis = "{idx}" Layer = "{layer}" Angle = "{ang(mult)}" />'
            if quarter:
                ap(f'        <Macro Name = "{letter} " Public = "1" Description = "{letter} - {side} layer of direction {"xyz"[a["k"]]} clockwise, {letter}2 - double, {letter}\' - counter-clockwise" > {t(1)} </Macro>')
                ap(f'        <Macro Name = "{letter}2" Public = "0" > {t(2)} </Macro>')
                ap(f'        <Macro Name = "{letter}\'" Public = "0" > {t(-1)} </Macro>')
            else:
                ap(f'        <Macro Name = "{letter}2" Public = "1" Description = "{letter}2 - half turn of the {side} layer of direction {"xyz"[a["k"]]}" > {t(2)} </Macro>')
    ap("")

    def rand_turn(a):
        ang = "Pi/2 * (Random(3) + 1)" if a["square"] else "Pi"        # scramble keeps the cuboid shape
        return a["index"], a["n"], ang

    total = sum(a["n"] for a in info)
    turns = max(100, 10 * total)
    same = len({(a["n"], a["square"]) for a in info}) == 1
    if same:                                               # like the original cube file
        a = info[0]
        ap('        <Macro Name = "RandomTurn" >')
        ap(f'            <Turn Axis = "Random({len(info)})" Layer = "Random({a["n"]})" Angle = "{rand_turn(a)[2]}" />')
        ap("        </Macro>")
        rep, mac = turns, "RandomTurn"
    else:                                                  # one random turn per axis per round
        ap('        <Macro Name = "RandomRound" >')
        for a in info:
            i, n, ang = rand_turn(a)
            ap(f'            <Turn Axis = "{i}" Layer = "Random({n})" Angle = "{ang}" />')
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
        nums = [nums[0], nums[1], nums[1]]
    if len(nums) != 3 or min(nums) < 1:
        raise ValueError("type 1, 2 or 3 positive numbers, like 3 or 3x4 or 2x3x4")
    return tuple(nums)


def write(dims):
    os.makedirs(os.path.join(HERE, "Figures"), exist_ok=True)
    with open(os.path.join(HERE, "Figures", "Cuboid.xml"), "w", encoding="utf-8") as fh:
        fh.write(figure_xml())
    name, text = make_xml(dims)
    path = os.path.join(HERE, f"{name}.xml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"{name} -> {path}")


def write_many(specs):
    for s in specs:
        try:
            write(parse(s))
        except ValueError as e:
            print(f"  skipped '{s}': {e}")


def ask():
    while True:
        s = input("Size (3 = cube, 5x3 = 5x3x3, 2x3x4, several with commas), blank = quit: ").strip()
        if not s:
            return
        write_many([x for x in s.split(",") if x.strip()])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        write_many(sys.argv[1:])
    else:
        ask()
