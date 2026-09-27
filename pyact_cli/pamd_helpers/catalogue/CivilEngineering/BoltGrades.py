from pyact_cli.pamd_helpers.unit import Unit

G3_6 = {"fyb": Unit(180, "[MPa]"), "fub": Unit(300, "[MPa]")}
G4_6 = {"fyb": Unit(240, "[MPa]"), "fub": Unit(400, "[MPa]")}
G4_8 = {"fyb": Unit(320, "[MPa]"), "fub": Unit(400, "[MPa]")}
G5_6 = {"fyb": Unit(300, "[MPa]"), "fub": Unit(500, "[MPa]")}
G5_8 = {"fyb": Unit(400, "[MPa]"), "fub": Unit(500, "[MPa]")}
G6_8 = {"fyb": Unit(480, "[MPa]"), "fub": Unit(600, "[MPa]")}
G8_8 = {"fyb": Unit(640, "[MPa]"), "fub": Unit(800, "[MPa]")}
G9_8 = {"fyb": Unit(720, "[MPa]"), "fub": Unit(900, "[MPa]")}
G10_9 = {"fyb": Unit(900, "[MPa]"), "fub": Unit(1000, "[MPa]")}
G12_9 = {"fyb": Unit(1080, "[MPa]"), "fub": Unit(1200, "[MPa]")}
        
def help():
    print(f"""
    (fyb, Yield strength of bolt) [MPa]
    (fub, Ultimate tensile strength of bolt) [MPa]
    """)