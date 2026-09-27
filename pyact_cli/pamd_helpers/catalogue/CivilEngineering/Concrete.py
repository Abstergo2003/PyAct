from pyact_cli.pamd_helpers.unit import Unit

CONCRETE_CONSTANTS = {
    "nu_uncracked": Unit(0.2, "[]"),    # Poisson's ratio for uncracked concrete
    "nu_cracked": Unit(0.0, "[]"),      # Poisson's ratio for cracked concrete
    "rho_plain": Unit(2400, "[kg/m^3]"),      # Density of plain concrete [kg/m^3]
    "rho_reinforced": Unit(2500, "[kg/m^3]"), # Density of reinforced concrete [kg/m^3]
    "alpha": Unit(10e-6, "[1/K]")          # Coefficient of linear thermal expansion [1/K]
}

C20_25 = {
    **CONCRETE_CONSTANTS,
    "fck": Unit(20, "[MPa]"),
    "fck_cube": Unit(25, "[MPa]"),
    "fcm": Unit(28, "[MPa]"),        # fck + 8
    "fctm": Unit(2.2, "[MPa]"),        # 0.3 * fck^(2/3)
    "Ecm": Unit(30, "[MPa]"),           # 22 * (fcm/10)^0.3
}
C25_30 = {
    **CONCRETE_CONSTANTS,
    "fck": Unit(25, "[MPa]"),
    "fck_cube": Unit(30, "[MPa]"),
    "fcm": Unit(33, "[MPa]"),
    "fctm": Unit(2.6, "[MPa]"),
    "Ecm": Unit(31, "[MPa]"),
}
C30_37 = {
    **CONCRETE_CONSTANTS,
    "fck": Unit(30, "[MPa]"),
    "fck_cube": Unit(37, "[MPa]"),
    "fcm": Unit(38, "[MPa]"),
    "fctm": Unit(2.9, "[MPa]"),
    "Ecm": Unit(33, "[MPa]"),
}
C35_45 = {
    **CONCRETE_CONSTANTS,
    "fck": Unit(35, "[MPa]"),
    "fck_cube": Unit(45, "[MPa]"),
    "fcm": Unit(43, "[MPa]"),
    "fctm": Unit(3.2, "[MPa]"),
    "Ecm": Unit(34, "[MPa]"),
}

def help():
    print(f"""
    (nu_uncracked, Poisson's ratio for uncracked concrete) []
    (nu_cracked, Poisson's ratio for cracked concrete) []
    (rho_plain, Density of plain concrete) [kg/m^3]
    (rho_reinforced, Density of reinforced concrete) [kg/m^3]
    (alpha, Coefficient of linear thermal expansion) [1/K]
    (fck, Characteristic compressive cylinder strength at 28 days) [MPa]
    (fck_cube, Characteristic compressive cube strength) [MPa]
    (fcm, Mean compressive strength) [MPa]
    (fctm, Mean tensile strength) [MPa]
    (Ecm, Secant modulus of elasticity) [MPa]
    """)