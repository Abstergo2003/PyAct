from pyact_cli.pamd_helpers.unit import Unit

STEEL_CONSTANTS = {
    "E": Unit(210, "[GPa]"),           # Modulus of Elasticity [GPa] (210,000 MPa)
    "G": Unit(81, "[GPa]"), # Shear Modulus [GPa] (81,000 MPa)
    "nu": Unit(0.3, "[]"),          # Poisson's ratio in elastic stage
    "rho": Unit(7850, "[kg/m^3]"),        # Density [kg/m^3]
    "alpha": Unit(12e-6, "[1/K]")      # Coefficient of linear thermal expansion [1/K]
}
# Material Properties (Standard values)
# Values typically given for Young's Modulus (E) in GPa, Yield Strength (Fy) in MPa, Density in kg/m^3

S235 = {
    **STEEL_CONSTANTS,
    "fy": Unit(235, "[MPa]"),      # Yield strength [MPa]
    "fu": Unit(360, "[MPa]")       # Ultimate tensile strength [MPa]
    }
S275 = {
    **STEEL_CONSTANTS,
    "fy": Unit(275, "[MPa]"),
    "fu": Unit(430, "[MPa]")
    }
S355 = {
    **STEEL_CONSTANTS,
    "fy": Unit(355, "[MPa]"),
    "fu": Unit(470, "[MPa]")
    }
S420 = {
    **STEEL_CONSTANTS,
    "fy": Unit(420, "[MPa]"),
    "fu": Unit(520, "[MPa]")
    }
S460 = {
    **STEEL_CONSTANTS,
    "fy": Unit(460, "[MPa]"),
    "fu": Unit(540, "[MPa]")
    }   

def help():
    print(f"""
    (E, Modulus of Elasticity) [GPa]
    (G, Shear Modulus) [GPa]
    (nu, Poisson's ratio) []
    (rho, Density) [kg/m^3]
    (alpha, Coefficient of linear thermal expansion) [1/K]
    (fy, Yield strength) [MPa]
    (fu, Ultimate tensile strength) [MPa]
    """)