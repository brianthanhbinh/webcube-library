import fractions

def generate_pcube_xml(order: int, output_filename: str = None) -> str:
    """
    Generates a pCubes XML configuration for an NxNxN twisty puzzle.
    Handles odd and even orders automatically with correct cutting planes,
    uniform tile proportions, W = 0.5 base scale, and full macro sets.
    """
    if order < -4:
        raise ValueError("Cube order must be at least 2.")
    
    planes = []
    if order % 2 != 0:
        # Odd order: symmetric planes around 0, excluding 0
        for k in range(1, order):
            num = 2 * k - order
            den = 2 * order
            f = fractions.Fraction(num, den)
            planes.append(f"{f.numerator}/{f.denominator}")
    else:
        # Even order: symmetric planes including 0 as central cutting plane
        half = order // 2
        for k in range(-(half - 1), half):
            if k == 0:
                planes.append("0")
            else:
                f = fractions.Fraction(k, order)
                planes.append(f"{f.numerator}/{f.denominator}")
        
    plane_distances_str = "; ".join(planes)
    max_layer = order - 1
    
    xml_content = f"""<?xml version = "1.0" encoding = "UTF-8"?>
<xml Data_Version = "2" >

    <Interface>
        <Name>{order}x{order}x{order} Cube</Name>
        <Menu>Cubic\\Custom\\{order}x{order}x{order}</Menu>
        <Inventor>Uwe Mertens</Inventor>
        <Programmer>Brian</Programmer>
        <Added>2026-03-21</Added>
    </Interface>
 
    <Axes TurningAngles = "Pi / 2" PlaneDistances = "{plane_distances_str}" >
        <Axis NormVector = "1; 0; 0" />
        <Axis NormVector = "0; 1; 0" />
        <Axis NormVector = "0; 0; 1" />
    </Axes>
 
    <Figure>
        <LoadFrom File = "Figures\\Cube.xml" W = "0.5" />
        <SplitByAxes/>
        <RemoveGrayParts/>
    </Figure>

    <Macros>
        <!-- Left / Right Layers -->
        <Macro Name = "L " Public = "1" Description = "L - left layer"> <Turn Axis = "0" Layer = "0" Angle = " Pi/2" /> </Macro>
        <Macro Name = "L2" Public = "0" > <Turn Axis = "0" Layer = "0" Angle = " Pi  " /> </Macro>
        <Macro Name = "L'" Public = "0" > <Turn Axis = "0" Layer = "0" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "R " Public = "1" Description = "R - right layer"> <Turn Axis = "0" Layer = "{max_layer}" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "R2" Public = "0" > <Turn Axis = "0" Layer = "{max_layer}" Angle = " Pi  " /> </Macro>
        <Macro Name = "R'" Public = "0" > <Turn Axis = "0" Layer = "{max_layer}" Angle = " Pi/2" /> </Macro>

        <!-- Front / Back Layers -->
        <Macro Name = "F " Public = "1" Description = "F - front layer"> <Turn Axis = "1" Layer = "0" Angle = " Pi/2" /> </Macro>
        <Macro Name = "F2" Public = "0" > <Turn Axis = "1" Layer = "0" Angle = " Pi  " /> </Macro>
        <Macro Name = "F'" Public = "0" > <Turn Axis = "1" Layer = "0" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "B " Public = "1" Description = "B - back layer"> <Turn Axis = "1" Layer = "{max_layer}" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "B2" Public = "0" > <Turn Axis = "1" Layer = "{max_layer}" Angle = " Pi  " /> </Macro>
        <Macro Name = "B'" Public = "0" > <Turn Axis = "1" Layer = "{max_layer}" Angle = " Pi/2" /> </Macro>

        <!-- Down / Up Layers -->
        <Macro Name = "D " Public = "1" Description = "D - down layer"> <Turn Axis = "2" Layer = "0" Angle = " Pi/2" /> </Macro>
        <Macro Name = "D2" Public = "0" > <Turn Axis = "2" Layer = "0" Angle = " Pi  " /> </Macro>
        <Macro Name = "D'" Public = "0" > <Turn Axis = "2" Layer = "0" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "U " Public = "1" Description = "U - up layer"> <Turn Axis = "2" Layer = "{max_layer}" Angle = "-Pi/2" /> </Macro>
        <Macro Name = "U2" Public = "0" > <Turn Axis = "2" Layer = "{max_layer}" Angle = " Pi  " /> </Macro>
        <Macro Name = "U'" Public = "0" > <Turn Axis = "2" Layer = "{max_layer}" Angle = " Pi/2" /> </Macro>

        <Macro Name = "RandomTurn" >
            <Turn Axis = "Random(3)" Layer = "Random({order})" Angle = "Pi/2 * (Random(3) + 1)" />
        </Macro>
        <Macro Name = "Scramble" Public = "1" Description = "Scramble {order}x{order}" Sequence = "100 random turns" >
            <ExecMacro MacroName = "RandomTurn" Repeat = "100" />
        </Macro>
    </Macros>
</xml>"""

    if output_filename:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(xml_content)
    return xml_content

if __name__ == "__main__":
    print("=== pCubes Interactive Cube Generator ===")
    try:
        count_input = input("How many cubes do you want to generate? ").strip()
        num_cubes = int(count_input)
        
        for i in range(1, num_cubes + 1):
            order_input = input(f"Enter the order (N) for cube #{i} (e.g., 10 for 10x10x10): ").strip()
            order = int(order_input)
            filename = f"cube_{order}x{order}x{order}.xml"
            generate_pcube_xml(order, filename)
            print(f" -> Generated and saved: {filename}")
            
        print("\nAll requested custom cubes generated successfully!")
    except ValueError as e:
        print(f"Invalid input: {e}")
