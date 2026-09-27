from pyact_cli.pamd_helpers.unit import Unit

M1 = {"fm": Unit(1.0, "[MPa]")}
M2_5 = {"fm": Unit(2.5, "[MPa]")}
M5 = {"fm": Unit(5.0, "[MPa]")}
M10 = {"fm": Unit(10.0, "[MPa]")}
M15 = {"fm": Unit(15.0, "[MPa]")}
M20 = {"fm": Unit(20.0, "[MPa]")}

def help():
    print(f"""
        Standard mortar classes according to Eurocode 6 (EN 1996-1-1)
        (fm, Compressive strength of mortar) [MPa]
    """)