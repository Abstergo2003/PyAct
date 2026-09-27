from pyact_cli.pamd_helpers.unit import Unit

ALUMINIUM_CONSTANTS = {
    "E": Unit(70, "[GPa]"), # Modulus of Elasticity [GPa] (70,000 MPa)
    "G": Unit(27, "[GPa]"),     # Shear Modulus [GPa] (27,000 MPa)
    "nu": Unit(0.3, "[]"),    # Poisson's ratio in elastic stage
    "rho": Unit(2700, "[kg/m^3]"),  # Density [kg/m^3]
    "alpha": Unit(23e-6, "[1/K]")      # Coefficient of linear thermal expansion [1/K]
}


EN_AW_6060_T66 = {
    **ALUMINIUM_CONSTANTS,
    "fo": Unit(160, "[MPa]"),      # 0.2% Proof Strength [MPa]
    "fu": Unit(215, "[MPa]"),   # Ultimate Tensile Strength [MPa]
    "fo_haz": Unit(75, "[MPa]"),     # Proof Strength in Heat Affected Zone [MPa]
    "fu_haz": Unit(115, "[MPa]"),    # Ultimate Strength in Heat Affected Zone [MPa]
    }
EN_AW_6061_T6 = {
    **ALUMINIUM_CONSTANTS,
    "fo": Unit(240, "[MPa]"),
    "fu": Unit(260, "[MPa]"),
    "fo_haz": Unit(115, "[MPa]"),
    "fu_haz": Unit(165, "[MPa]"),
    }
EN_AW_6082_T6 = {
    **ALUMINIUM_CONSTANTS,
    "fo": Unit(250, "[MPa]"),
    "fu": Unit(290, "[MPa]"),
    "fo_haz": Unit(125, "[MPa]"),
    "fu_haz": Unit(185, "[MPa]"),
    }

def help():
    print(f"""
    (E, Modulus of Elasticity) [GPa]
    (G, Shear Modulus) [GPa]
    (nu, Poisson's ratio) []
    (rho, Density) [kg/m^3]
    (alpha, Coefficient of linear thermal expansion) [1/K]
    (fo, 0.2% Proof Strength) [MPa]
    (fu, Ultimate Tensile Strength) [MPa]
    (fo_haz, Proof Strength in Heat Affected Zone) [MPa]
    (fu_haz, Ultimate Strength in Heat Affected Zone) [MPa]
    """)