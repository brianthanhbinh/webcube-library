from pathlib import Path


def calc_even_cuts(
    layers: int,
    start: float = 0.1,
    end: float = 0.58,
    decimals: int = 4,
) -> list[float]:
  """Distribute (layers - 1) cuts evenly across [start, end] with no leading 0."""
  if layers < 2:
    raise ValueError("Number of layers must be at least 2.")

  num_cuts = layers - 1
  if num_cuts == 1:
    return [round(start, decimals)]

  step = (end - start) / (num_cuts - 1)
  return [round(start + i * step, decimals) for i in range(num_cuts)]


def format_distances(values: list[float]) -> str:
  return "; ".join(f"{v:g}" for v in values)


def build_pyraminx_xml(
    layers: int,
    distances_str: str,
    w: float = 0.5,
    programmer: str = "Brian",
    date_added: str = "2026-11-19",
) -> str:
  max_layer = layers - 1
  return f"""<?xml version="1.0" encoding="UTF-8"?>
<xml Data_Version="2">

    <Interface>
        <Name>Pyraminx {layers}x{layers}</Name>
        <Menu>Tetrahedron\\Pyraminx\\{layers}x{layers}</Menu>
        <Inventor>Uwe Meffert</Inventor>
        <Programmer>{programmer}</Programmer>
        <Added>{date_added}</Added>
    </Interface>

    <Axes
        TurningAngles="2*Pi/3"
        PlaneDistances="{distances_str}">

        <Axis NormVector="1;1;1"/>
        <Axis NormVector="-1;-1;1"/>
        <Axis NormVector="-1;1;-1"/>
        <Axis NormVector="1;-1;-1"/>

    </Axes>

    <Figure>
        <LoadFrom File="Figures\\Tetrahedron.xml" W="{w:g}"/>
        <SplitByAxes/>
        <RemoveGrayParts/>
    </Figure>

    <Macros>
        <!-- Face Turns -->
        <Macro Name = "U " Public = "1" Description = "U face turn"> <Turn Axis = "0" Layer = "{max_layer}" Angle = "2*Pi/3" /> </Macro>
        <Macro Name = "U'" Public = "0" > <Turn Axis = "0" Layer = "{max_layer}" Angle = "-2*Pi/3" /> </Macro>
        <Macro Name = "L " Public = "1" Description = "L face turn"> <Turn Axis = "1" Layer = "{max_layer}" Angle = "2*Pi/3" /> </Macro>
        <Macro Name = "L'" Public = "0" > <Turn Axis = "1" Layer = "{max_layer}" Angle = "-2*Pi/3" /> </Macro>
        <Macro Name = "R " Public = "1" Description = "R face turn"> <Turn Axis = "2" Layer = "{max_layer}" Angle = "2*Pi/3" /> </Macro>
        <Macro Name = "R'" Public = "0" > <Turn Axis = "2" Layer = "{max_layer}" Angle = "-2*Pi/3" /> </Macro>
        <Macro Name = "B " Public = "1" Description = "B face turn"> <Turn Axis = "3" Layer = "{max_layer}" Angle = "2*Pi/3" /> </Macro>
        <Macro Name = "B'" Public = "0" > <Turn Axis = "3" Layer = "{max_layer}" Angle = "-2*Pi/3" /> </Macro>

        <Macro Name = "RandomTurn" >
            <Turn Axis = "Random(4)" Layer = "Random({layers})" Angle = "2*Pi/3 * (Random(2) + 1)" />
        </Macro>
        <Macro Name = "Scramble" Public = "1" Description = "Scramble Pyraminx {layers}x{layers}" Sequence = "50 random turns" >
            <ExecMacro MacroName = "RandomTurn" Repeat = "50" />
        </Macro>
    </Macros>
</xml>
"""


def main() -> None:
  while True:
    raw = input("Enter number of layers: ").strip()
    try:
      layers = int(raw)
      if layers >= 2:
        break
      print("Enter an integer >= 2.")
    except ValueError:
      print("Enter a valid integer.")

  values = calc_even_cuts(layers=layers, start=0.1, end=0.58)
  distances_str = format_distances(values)
  xml_content = build_pyraminx_xml(layers=layers, distances_str=distances_str, w=0.5)

  out_path = Path(__file__).resolve().parent / f"Pyraminx_{layers}x{layers}.xml"
  out_path.write_text(xml_content, encoding="utf-8")

  print(f"Saved: {out_path}")
  print(f"PlaneDistances: {distances_str}")


if __name__ == "__main__":
  main()
