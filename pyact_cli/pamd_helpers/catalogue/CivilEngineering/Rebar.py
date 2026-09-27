from pyact_cli.pamd_helpers.unit import Unit


phi6 = {"d": Unit(6, "[mm]"), "As": Unit(28.3, "[mm^2]"), "u": Unit(18.8, "[mm]"), "weight": Unit(0.222, "[kg/m]")}
phi8 = {"d": Unit(8, "[mm]"), "As": Unit(50.3, "[mm^2]"), "u": Unit(25.1, "[mm]"), "weight": Unit(0.395, "[kg/m]")}
phi10 = {"d": Unit(10, "[mm]"), "As": Unit(78.5, "[mm^2]"), "u": Unit(31.4, "[mm]"), "weight": Unit(0.617, "[kg/m]")}
phi12 = {"d": Unit(12, "[mm]"), "As": Unit(113.1, "[mm^2]"), "u": Unit(37.7, "[mm]"), "weight": Unit(0.888, "[kg/m]")}
phi14 = {"d": Unit(14, "[mm]"), "As": Unit(153.9, "[mm^2]"), "u": Unit(44.0, "[mm]"), "weight": Unit(1.21, "[kg/m]")}
phi16 = {"d": Unit(16, "[mm]"), "As": Unit(201.1, "[mm^2]"), "u": Unit(50.3, "[mm]"), "weight": Unit(1.58, "[kg/m]")}
phi20 = {"d": Unit(20, "[mm]"), "As": Unit(314.2, "[mm^2]"), "u": Unit(62.8, "[mm]"), "weight": Unit(2.47, "[kg/m]")}
phi25 = {"d": Unit(25, "[mm]"), "As": Unit(490.9, "[mm^2]"), "u": Unit(78.5, "[mm]"), "weight": Unit(3.85, "[kg/m]")}
phi32 = {"d": Unit(32, "[mm]"), "As": Unit(804.2, "[mm^2]"), "u": Unit(100.5, "[mm]"), "weight": Unit(6.31, "[kg/m]")}
        
def help():
    print(f"""
        (d, Nominal diameter) [mm]
        (As, Cross-sectional area) [mm^2]
        (u, Perimeter) [mm]
        (weight, Nominal weight per meter) [kg/m]
    """)