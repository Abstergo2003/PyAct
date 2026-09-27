from pyact_cli.pamd_helpers.unit import Unit

# Clay Bricks (Group 1 - Solid, Group 2 - Perforated)
Clay_Solid = {"fb": Unit(15.0, "[MPa]"), "k": Unit(0.55, "[-]")}
Clay_Perforated = {"fb": Unit(10.0, "[MPa]"), "k": Unit(0.45, "[-]")}
        
# Calcium Silicate Blocks
CalciumSilicate_Solid = {"fb": Unit(15.0, "[MPa]"), "k": Unit(0.55, "[-]")}
CalciumSilicate_Perforated = {"fb": Unit(10.0, "[MPa]"), "k": Unit(0.45, "[-]")}
        
# Autoclaved Aerated Concrete (AAC)
AAC_Block = {"fb": Unit(4.0, "[MPa]"), "k": Unit(0.55, "[-]")}
        
# Aggregate Concrete Blocks
AggregateConcrete_Solid = {"fb": Unit(10.0, "[MPa]"), "k": Unit(0.55, "[-]")}
        
def help(self):
    print(f"""
        Typical normalized compressive strengths for masonry units (fb)
        Note: These are typical/assumed values. Actual values depend on the manufacturer.
        (fb, Normalized mean compressive strength of masonry unit) [MPa]
        (K, Constant for characteristic compressive strength equation) [-]
    """)