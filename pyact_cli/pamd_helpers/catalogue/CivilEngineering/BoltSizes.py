from pyact_cli.pamd_helpers.unit import Unit

M4 = {"d": Unit(4, "[mm]"), "A": Unit(12.6, "[mm^2]"), "As": Unit(8.78, "[mm^2]")}
M5 = {"d": Unit(5, "[mm]"), "A": Unit(19.6, "[mm^2]"), "As": Unit(14.2, "[mm^2]")}
M6 = {"d": Unit(6, "[mm]"), "A": Unit(28.3, "[mm^2]"), "As": Unit(20.1, "[mm^2]")}
M8 = {"d": Unit(8, "[mm]"), "A": Unit(50.3, "[mm^2]"), "As": Unit(36.6, "[mm^2]")}
M10 = {"d": Unit(10, "[mm]"), "A": Unit(78.5, "[mm^2]"), "As": Unit(58.0, "[mm^2]")}
M12 = {"d": Unit(12, "[mm]"), "A": Unit(113.1, "[mm^2]"), "As": Unit(84.3, "[mm^2]")}
M14 = {"d": Unit(14, "[mm]"), "A": Unit(153.9, "[mm^2]"), "As": Unit(115.0, "[mm^2]")}
M16 = {"d": Unit(16, "[mm]"), "A": Unit(201.1, "[mm^2]"), "As": Unit(157.0, "[mm^2]")}
M18 = {"d": Unit(18, "[mm]"), "A": Unit(254.5, "[mm^2]"), "As": Unit(192.0, "[mm^2]")}
M20 = {"d": Unit(20, "[mm]"), "A": Unit(314.2, "[mm^2]"), "As": Unit(245.0, "[mm^2]")}
M22 = {"d": Unit(22, "[mm]"), "A": Unit(380.1, "[mm^2]"), "As": Unit(303.0, "[mm^2]")}
M24 = {"d": Unit(24, "[mm]"), "A": Unit(452.4, "[mm^2]"), "As": Unit(353.0, "[mm^2]")}
M27 = {"d": Unit(27, "[mm]"), "A": Unit(572.6, "[mm^2]"), "As": Unit(459.0, "[mm^2]")}
M30 = {"d": Unit(30, "[mm]"), "A": Unit(706.9, "[mm^2]"), "As": Unit(561.0, "[mm^2]")}
M33 = {"d": Unit(33, "[mm]"), "A": Unit(855.3, "[mm^2]"), "As": Unit(694.0, "[mm^2]")}
M36 = {"d": Unit(36, "[mm]"), "A": Unit(1017.9, "[mm^2]"), "As": Unit(817.0, "[mm^2]")}


def help():
    print(f"""
    (d, Nominal diameter) [mm]
    (A, Nominal cross-sectional area) [mm^2]
    (As, Tensile stress area) [mm^2]
    """)