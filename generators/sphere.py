#!/usr/bin/env python3
"""Generate pcubes sphere puzzles: a ball cut by planes like a cube.

The ball is cut by layers along x, y and z (like the 3x3x3 cube), so you get
rounded corner, edge and centre pieces.  A sphere looks the same after any
rotation, so every layer turns by 90 degrees and the ball always stays round.

Run it (IDLE: F5) and type sizes when asked.  Accepted forms:

    3            -> 3x3x3 ball
    5x3          -> 5x3x3   (5 layers along x, 3 along y and z)
    2x3x4        -> 2x3x4
    3, 4x4x4     -> several balls at once (comma separated)

From a terminal:  python gen_sphere_puzzle.py 3 4x4x4

The three numbers are the layers along x (left-right), y (front-back) and
z (down-up), the same axes as the L/R, F/B, D/U macros of the 3x3x3 cube.

Writes "Sphere AxBxC.xml" and Figures\\Sphere mesh N.xml next to this script.

The ball is a mesh of flat triangles (DETAIL controls how fine; it keeps the
mesh identical after every 90 degree turn).  The surface is coloured in six big
patches like a cube (red/orange = +x/-x, blue/green = +y/-y, white/yellow = +z/-z).
"""
import math
import os
import re
import sys
from datetime import date
from fractions import Fraction

# ---------------------------------------------------------------- settings
W = 0.5                       # radius of the ball (0.5 = same size as the normal 3x3x3 cube)
DETAIL = 8                    # mesh: each of the 6 sides is DETAIL x DETAIL quads, each quad = 4 triangles
TURN_STEP = "Pi / 2"          # keep 90 degrees: only these turns map the mesh exactly onto itself
MENU_FOLDER = "Cubic\\Spheres"
PROGRAMMER = ""               # put your name here (omitted when empty)
# -------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))

# physical axes: (macro letter for layer 0, mid slice letter, macro letter for last layer, normal vector)
AXES = [("L", "M", "R", (1, 0, 0)), ("F", "S", "B", (0, 1, 0)), ("D", "E", "U", (0, 0, 1))]

# patch colours: +x, -x, +y, -y, +z, -z
COLORS = {(0, 1): "C80000", (0, -1): "FF8000", (1, 1): "0000C8", (1, -1): "009600", (2, 1): "FFFFFF", (2, -1): "FFFF00"}

# (axis, sign): (right vector, up vector) seen from outside, so triangles come out counter-clockwise
SIDES = {
    (2, 1): ((1, 0, 0), (0, 1, 0)),
    (2, -1): ((1, 0, 0), (0, -1, 0)),
    (1, -1): ((1, 0, 0), (0, 0, 1)),
    (1, 1): ((-1, 0, 0), (0, 0, 1)),
    (0, -1): ((0, -1, 0), (0, 0, 1)),
    (0, 1): ((0, 1, 0), (0, 0, 1)),
}


# ------------------------------------------------------------------ figure
def mesh(m):
    """Cube-sphere mesh: returns (vertices as unit vectors, triangles as index triples, colour key per triangle)."""
    verts, index = [], {}

    def vid(p):
        if p not in index:
            index[p] = len(verts)
            length = math.sqrt(sum(c * c for c in p))
            verts.append(tuple(c / length for c in p))
        return index[p]

    tris, keys = [], []
    for key, (right, up) in SIDES.items():
        ax, sign = key
        normal = [0, 0, 0]
        normal[ax] = sign
        for r in range(m):
            for c in range(m):
                def pt(uu, vv):                      # integer cube-surface coordinates
                    return tuple(m * normal[k] + uu * right[k] + vv * up[k] for k in range(3))
                tl, tr = pt(2 * c - m, m - 2 * r), pt(2 * c + 2 - m, m - 2 * r)
                bl, br = pt(2 * c - m, m - 2 * r - 2), pt(2 * c + 2 - m, m - 2 * r - 2)
                ce = pt(2 * c + 1 - m, m - 2 * r - 1)
                a, b, d, e, z = vid(tl), vid(bl), vid(br), vid(tr), vid(ce)
                for tri in ((a, b, z), (b, d, z), (d, e, z), (e, a, z)):   # counter-clockwise seen from outside
                    tris.append(tri)
                    keys.append(key)
    return verts, tris, keys


def figure_xml(m):
    verts, tris, keys = mesh(m)
    palette = list(COLORS)

    def expr(x):
        if abs(x) < 1e-12:
            return "0"
        if abs(x - 1) < 1e-12:
            return "W"
        if abs(x + 1) < 1e-12:
            return "-W"
        return f"{x:.9f} * W"

    o = ['<?xml version = "1.0" encoding = "UTF-8"?>', "<xml>", "    <Script>",
         "        if not VarExists('Colors[0]') then begin"]
    for i, key in enumerate(palette):
        o.append(f"            Colors[{i}] := '{COLORS[key]}';")
    o.append("        end;")
    o.append("")
    for i, (x, y, z) in enumerate(verts):
        o.append(f"        Vx[{i}] := {expr(x)}; Vy[{i}] := {expr(y)}; Vz[{i}] := {expr(z)};")
    o += ["    </Script>", "", "    <Part>", '        <Vertices Vectors = "Vx; Vy; Vz" />', "", "        <Faces>"]
    for t, key in zip(tris, keys):
        o.append(f'            <Face Color = "Colors[{palette.index(key)}]" VertexIndexes = "{t[0]};{t[1]};{t[2]}" />')
    o += ["        </Faces>", "    </Part>", "</xml>"]
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ puzzle
def plane_text(n):
    """Cuts between n equal layers across the ball, ascending, as exact fractions (W = 0.5)."""
    out = []
    for j in range(1, n):
        f = Fraction(2 * j - n, 2 * n)
        out.append("0" if f == 0 else f"{f.numerator}/{f.denominator}")
    return "; ".join(out)


def make_xml(dims, fig_file):
    name = f"Sphere {dims[0]}x{dims[1]}x{dims[2]}"
    info = [{"k": k, "n": dims[k], "planes": plane_text(dims[k])} for k in range(3) if dims[k] >= 2]
    if not info:
        raise ValueError("at least one direction needs 2 or more layers")

    groups = []
    for a in info:
        for g in groups:
            if g[0]["planes"] == a["planes"]:
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
        ap(f'    <Axes TurningAngles = "{TURN_STEP}" PlaneDistances = "{g[0]["planes"]}" >')
        for a in g:
            v = AXES[a["k"]][3]
            ap(f'        <Axis NormVector = "{v[0]}; {v[1]}; {v[2]}" />')
        ap("    </Axes>")
        ap("")
    ap("    <Figure>")
    ap(f'        <LoadFrom File = "{fig_file}" W = "{W}" />')
    ap("        <SplitByAxes/>")
    ap("        <RemoveGrayParts/>")
    ap("    </Figure>")
    ap("")
    ap("    <Macros>")
    for a in info:
        lo, mid, hi, _ = AXES[a["k"]]
        n, idx = a["n"], a["index"]
        turns = [(lo, 0, 1, 1), (hi, n - 1, -1, 1)]
        if n == 3:
            turns.insert(1, (mid, 1, 1, 0))
        for letter, layer, sign, public in turns:
            def t(mult):
                v = {1: "Pi/2", 2: "Pi", -1: "-Pi/2"}[mult]
                if sign < 0 and mult != 2:
                    v = "-Pi/2" if mult == 1 else "Pi/2"
                return f'<Turn Axis = "{idx}" Layer = "{layer}" Angle = "{v}" />'
            desc = f' Description = "{letter} - clockwise, {letter}2 - double, {letter}\' - counter-clockwise"' if public else ""
            ap(f'        <Macro Name = "{letter} " Public = "{public}"{desc} > {t(1)} </Macro>')
            ap(f'        <Macro Name = "{letter}2" Public = "0" > {t(2)} </Macro>')
            ap(f'        <Macro Name = "{letter}\'" Public = "0" > {t(-1)} </Macro>')
    ap("")
    total = sum(a["n"] for a in info)
    turns = max(100, 10 * total)
    if len({a["n"] for a in info}) == 1:
        ap('        <Macro Name = "RandomTurn" >')
        ap(f'            <Turn Axis = "Random({len(info)})" Layer = "Random({info[0]["n"]})" Angle = "Pi/2 * (Random(3) + 1)" />')
        ap("        </Macro>")
        rep, mac = turns, "RandomTurn"
    else:
        ap('        <Macro Name = "RandomRound" >')
        for a in info:
            ap(f'            <Turn Axis = "{a["index"]}" Layer = "Random({a["n"]})" Angle = "Pi/2 * (Random(3) + 1)" />')
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
        raise ValueError("type 1, 2 or 3 positive numbers, like 3 or 5x3 or 2x3x4")
    return tuple(nums)


def write(dims):
    os.makedirs(os.path.join(HERE, "Figures"), exist_ok=True)
    fig_name = f"Sphere mesh {DETAIL}.xml"
    with open(os.path.join(HERE, "Figures", fig_name), "w", encoding="utf-8") as fh:
        fh.write(figure_xml(DETAIL))
    name, text = make_xml(dims, f"Figures\\{fig_name}")
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
        s = input("Size (3 = 3x3x3, 5x3 = 5x3x3, 2x3x4, several with commas), blank = quit: ").strip()
        if not s:
            return
        write_many([x for x in s.split(",") if x.strip()])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        write_many(sys.argv[1:])
    else:
        ask()
