from datetime import date

def generate_mirror_xml(n: int, w: float = 0.5, author: str = "Brian"):
    if n < -10:
        raise ValueError("Layer count N must be at least 2.")

    # Cube_Coordinates.inc spans [-W, +W], so total width is 2*W
    step = (2 * w) / n
    cuts = list()
    for k in range(1, n):
        cuts.append(round(-w + k * step, 6))
    plane_distances = "; ".join(f"{c:g}" for c in cuts)

    scramble_turns = max(45, n * 15)
    macro_lines = list()

    face_defs = [
        ("R", 0, True,  "2*Pi/4",  "-2*Pi/4"),
        ("L", 0, False, "-2*Pi/4", "2*Pi/4"),
        ("U", 1, True,  "2*Pi/4",  "-2*Pi/4"),
        ("D", 1, False, "-2*Pi/4", "2*Pi/4"),
        ("F", 2, True,  "2*Pi/4",  "-2*Pi/4"),
        ("B", 2, False, "-2*Pi/4", "2*Pi/4"),
    ]

    for face_name, axis_idx, is_pos, cw_angle, ccw_angle in face_defs:
        outer_layer = (n - 1) if is_pos else 0
        macro_lines.append(
            f'        <Macro Name = "{face_name} " Public = "1" Description = "{face_name} face turn"> '
            f'<Turn Axis = "{axis_idx}" Layer = "{outer_layer}" Angle = "{cw_angle}" /> </Macro>'
        )
        macro_lines.append(
            f'        <Macro Name = "{face_name}\'" Public = "0"> '
            f'<Turn Axis = "{axis_idx}" Layer = "{outer_layer}" Angle = "{ccw_angle}" /> </Macro>'
        )

        for depth in range(2, (n // 2) + 1):
            layer_idx = (n - depth) if is_pos else (depth - 1)
            prefix = f"{depth}{face_name}"
            macro_lines.append(
                f'        <Macro Name = "{prefix} " Public = "1" Description = "{prefix} slice turn"> '
                f'<Turn Axis = "{axis_idx}" Layer = "{layer_idx}" Angle = "{cw_angle}" /> </Macro>'
            )
            macro_lines.append(
                f'        <Macro Name = "{prefix}\'" Public = "0"> '
                f'<Turn Axis = "{axis_idx}" Layer = "{layer_idx}" Angle = "{ccw_angle}" /> </Macro>'
            )

    macros_block = "\n".join(macro_lines)

    puzzle_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<xml Data_Version="2">

    <Interface>
        <Name>Mirror Cube {n}x{n}x{n}</Name>
        <Menu>Cubic\\Mirror\\{n}x{n}x{n}</Menu>
        <Inventor>Hidetoshi Takeji</Inventor>
        <Programmer>{author}</Programmer>
        <Added>{date.today().isoformat()}</Added>
    </Interface>

    <Axes
        TurningAngles="2*Pi/4"
        PlaneDistances="{plane_distances}">

        <Axis NormVector="1;0;0"/>
        <Axis NormVector="0;1;0"/>
        <Axis NormVector="0;0;1"/>

    </Axes>

    <Figure>
        <LoadFrom File="Figures\\Mirror.xml" W="{w}"/>
        <SplitByAxes/>
        <RemoveGrayParts/>
    </Figure>

    <Macros>
{macros_block}

        <Macro Name = "RandomTurn" >
            <Turn Axis = "Random(3)" Layer = "Random({n})" Angle = "2*Pi/4 * (Random(3) + 1)" />
        </Macro>
        <Macro Name = "Scramble" Public = "1" Description = "Scramble Mirror {n}x{n}x{n}" Sequence = "{scramble_turns} random turns" >
            <ExecMacro MacroName = "RandomTurn" Repeat = "{scramble_turns}" />
        </Macro>
    </Macros>
</xml>
"""
    filename = f"Mirror_{n}x{n}x{n}.xml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(puzzle_xml)
    print(f"Generated {filename} (PlaneDistances=\"{plane_distances}\")")

if __name__ == "__main__":
    layers = int(input("Enter N (e.g. 3 for 3x3x3 Mirror): "))
    generate_mirror_xml(layers, 0.5)
