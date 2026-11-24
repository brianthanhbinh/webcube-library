#!/usr/bin/env python3
"""Generate a pcubes figure file (XML) for a dodecahedron (megaminx body).

Usage:  python gen_megaminx_figure.py [output.xml]

- The 8 cube vertices of the dodecahedron sit at (+-W, +-W, +-W), like the
  tetrahedron example; the other 12 are at 0, +-W/phi, +-W*phi.
- Faces are listed counter-clockwise seen from outside (same winding as the
  tetrahedron example).
- Face i and face i+6 are opposite each other.
"""
import itertools
import math
import sys

PHI = (1 + 5 ** 0.5) / 2
INV = 1 / PHI

# 12 face colours, hex RRGGBB. Index i and i+6 are opposite faces.
COLORS = [
    "FFFFFF", "C80000", "0000C8", "800080", "FF96C8", "00C8C8",   # 0..5
    "FFFF00", "FF8000", "009600", "80FF00", "D2B48C", "8B4513",   # 6..11 (opposites)
]


# Face normals (icosahedron directions). Face i and face i+6 are opposite.
_BASE = [(0, PHI, 1), (0, PHI, -1), (1, 0, PHI), (-1, 0, PHI), (PHI, 1, 0), (PHI, -1, 0)]
NORMALS = _BASE + [tuple(-c for c in n) for n in _BASE]


def build():
    # --- vertices -----------------------------------------------------
    verts = [(sx, sy, sz) for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]
    for a, b in itertools.product((1, -1), repeat=2):
        verts.append((0, a * INV, b * PHI))
        verts.append((a * INV, b * PHI, 0))
        verts.append((b * PHI, 0, a * INV))
    assert len(verts) == 20

    normals = NORMALS

    def dot(p, q):
        return sum(x * y for x, y in zip(p, q))

    def cross(p, q):
        return (p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0])

    def unit(p):
        l = math.sqrt(dot(p, p))
        return tuple(c / l for c in p)

    faces = []
    for n in normals:
        nu = unit(n)
        ds = [dot(v, nu) for v in verts]
        top = max(ds)
        idx = [i for i, d in enumerate(ds) if abs(d - top) < 1e-9]
        assert len(idx) == 5, "face should have 5 vertices"
        # build basis (u, w) with u x w = nu  ->  CCW seen from outside
        ref = (1, 0, 0) if abs(nu[0]) < 0.9 else (0, 1, 0)
        u = unit(cross(nu, ref))
        w = cross(nu, u)
        c = tuple(sum(verts[i][k] for i in idx) / 5 for k in range(3))
        idx.sort(key=lambda i: math.atan2(dot([verts[i][k] - c[k] for k in range(3)], w),
                                          dot([verts[i][k] - c[k] for k in range(3)], u)))
        faces.append(idx)
    return verts, faces


def fmt(c):
    """Coordinate -> pcubes script expression in terms of W."""
    if abs(c) < 1e-12:
        return "0"
    s = "-" if c < 0 else ""
    a = abs(c)
    if abs(a - 1) < 1e-12:
        return f"{s}W"
    return f"{s}{a:.9f} * W"


def write(path):
    verts, faces = build()
    out = []
    out.append('<?xml version = "1.0" encoding = "UTF-8"?>')
    out.append("<xml>")
    out.append("    <Script>")
    out.append("        if not VarExists('Colors[0]') then begin")
    for i, c in enumerate(COLORS):
        out.append(f"            Colors[{i}] := '{c}';")
    out.append("        end;")
    out.append("")
    for i, (x, y, z) in enumerate(verts):
        out.append(f"        Vx[{i}] := {fmt(x)}; Vy[{i}] := {fmt(y)}; Vz[{i}] := {fmt(z)};")
    out.append("    </Script>")
    out.append("")
    out.append("    <Part>")
    out.append('        <Vertices Vectors = "Vx; Vy; Vz" />')
    out.append("")
    out.append("        <Faces>")
    for i, f in enumerate(faces):
        out.append(f'            <Face Color = "Colors[{i}]" VertexIndexes = "{";".join(map(str, f))}" />')
    out.append("        </Faces>")
    out.append("    </Part>")
    out.append("</xml>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else "megaminx_figure.xml")
