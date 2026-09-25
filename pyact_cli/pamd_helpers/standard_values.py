"""
Engineering Data Library for PyAct

Provides standard dictionaries of physics values, material characteristics characteristics, and beam profiles
to be easily imported and injected into .pamd documents.
"""

from unit import Unit

# Physical Constants
class PHYSICAL_CONSTANTS:
    def __init__(self):
        self.R_K= Unit(25812.80745, "[Omega]"),
        self.R_inf = Unit(10973731.568157, "[1/m]"),
        self.K_J = Unit(483597.848484e9, "[Hz/V]"),
        self.alpha = Unit(0.0072973525643, "[]"),
        self.m_e = Unit(9.1093837139e-31, "[kg]"),
        self.mi_0 = Unit(1.25663706127e-6, "[N/A^2]"),
        self.epsilon_0 = Unit(8.8541878188e-12, "[F/m]"),
        self.h = Unit(6.62607015e-34, "[J/Hz]"),
        self.e = Unit(1.602176634e-19, "[C]"),
        self.g = Unit(9.80665, "[m/s^2]"),           # Acceleration due to gravity
        self.G = Unit(6.67430e-11, "[m^3/kg/s^2]"),        # Gravitational constant
        self.c = Unit(299792458, "[m/s]"),          # Speed of light
        self.R = Unit(8.314462618, "[J/(mol*K)]"),        # Ideal gas constant
        self.atm = Unit(101325, "[Pa]"),           # Standard atmosphere

    def help(self):
        print(f"""
        (R_K, von Klitzing constant) [Omega]
        (R_inf, Rydberg constant) [1/m]
        (K_J, Josephson constant) [Hz/V]
        (alpha, Fine-structure constant) []
        (m_e, Electron mass) [kg]
        (mi_0, Vacuum magnetic permeability) [N/A^2]
        (epsilon_0, Vacuum electric permittivity) [F/m]
        (h, Planck constant) [J/Hz]
        (e, Elementary charge) [C]
        (g, Acceleration due to gravity) [m/s^2]
        (G, Gravitational constant) [m^3/kg/s^2]
        (c, Speed of light) [m/s]
        (R, Ideal gas constant) [J/(mol*K)]
        (atm, Standard atmosphere) [Pa]
        """)


STEEL_CONSTANTS = {
    "E": Unit(210, "[GPa]"),           # Modulus of Elasticity [GPa] (210,000 MPa)
    "G": Unit(81, "[GPa]"),            # Shear Modulus [GPa] (81,000 MPa)
    "nu": Unit(0.3, "[]"),          # Poisson's ratio in elastic stage
    "rho": Unit(7850, "[kg/m^3]"),        # Density [kg/m^3]
    "alpha": Unit(12e-6, "[1/K]")      # Coefficient of linear thermal expansion [1/K]
}
# Material Properties (Standard values)
# Values typically given for Young's Modulus (E) in GPa, Yield Strength (Fy) in MPa, Density in kg/m^3
class Steel:
    def __init__(self):
        self.S235 = {
            **STEEL_CONSTANTS,
            "fy": Unit(235, "[MPa]"),      # Yield strength [MPa]
            "fu": Unit(360, "[MPa]")       # Ultimate tensile strength [MPa]
        }
        self.S275 = {
            **STEEL_CONSTANTS,
            "fy": Unit(275, "[MPa]"),
            "fu": Unit(430, "[MPa]")
        }
        self.S355 = {
            **STEEL_CONSTANTS,
            "fy": Unit(355, "[MPa]"),
            "fu": Unit(470, "[MPa]")
        }
        self.S420 = {
            **STEEL_CONSTANTS,
            "fy": Unit(420, "[MPa]"),
            "fu": Unit(520, "[MPa]")
        }
        self.S460 = {
            **STEEL_CONSTANTS,
            "fy": Unit(460, "[MPa]"),
            "fu": Unit(540, "[MPa]")
        }   

    def help(self):
        print(f"""
        (E, Modulus of Elasticity) [GPa]
        (G, Shear Modulus) [GPa]
        (nu, Poisson's ratio) []
        (rho, Density) [kg/m^3]
        (alpha, Coefficient of linear thermal expansion) [1/K]
        (fy, Yield strength) [MPa]
        (fu, Ultimate tensile strength) [MPa]
        """)


ALUMINIUM_CONSTANTS = {
    "E": Unit(70, "[GPa]"),            # Modulus of Elasticity [GPa] (70,000 MPa)
    "G": Unit(27, "[GPa]"),            # Shear Modulus [GPa] (27,000 MPa)
    "nu": Unit(0.3, "[]"),          # Poisson's ratio in elastic stage
    "rho": Unit(2700, "[kg/m^3]"),        # Density [kg/m^3]
    "alpha": Unit(23e-6, "[1/K]")      # Coefficient of linear thermal expansion [1/K]
}

class Aluminium:
    def __init__(self):
        self.EN_AW_6060_T66 = {
            **ALUMINIUM_CONSTANTS,
            "fo": Unit(160, "[MPa]"),      # 0.2% Proof Strength [MPa]
            "fu": Unit(215, "[MPa]"),            # Ultimate Tensile Strength [MPa]
            "fo_haz": Unit(75, "[MPa]"),         # Proof Strength in Heat Affected Zone [MPa]
            "fu_haz": Unit(115, "[MPa]"),         # Ultimate Strength in Heat Affected Zone [MPa]
        }
        self.EN_AW_6061_T6 = {
            **ALUMINIUM_CONSTANTS,
            "fo": Unit(240, "[MPa]"),
            "fu": Unit(260, "[MPa]"),
            "fo_haz": Unit(115, "[MPa]"),
            "fu_haz": Unit(165, "[MPa]"),
        }
        self.EN_AW_6082_T6 = {
            **ALUMINIUM_CONSTANTS,
            "fo": Unit(250, "[MPa]"),
            "fu": Unit(290, "[MPa]"),
            "fo_haz": Unit(125, "[MPa]"),
            "fu_haz": Unit(185, "[MPa]"),
        }

    def help(self):
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

class Softwood:
    def __init__(self):
        self.C14 = {
            "f_m": Unit(14, "[N/mm^2]"),
            "f_t0": Unit(8, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(16, "[N/mm^2]"),
            "f_c90": Unit(2.0, "[N/mm^2]"),
            "f_v": Unit(3.0, "[N/mm^2]"),
            "E_0mean": Unit(7, "[kN/mm^2]"),
            "E_005": Unit(4.7, "[kN/mm^2]"),
            "E_90mean": Unit(0.23, "[kN/mm^2]"),
            "G_mean": Unit(0.44, "[kN/mm^2]"),
            "rho": Unit(290, "[kg/m^3]"),
            "rho_mean": Unit(350, "[kg/m^3]"),
        }
        self.C16 = {
            "f_m": Unit(16, "[N/mm^2]"),
            "f_t0": Unit(10, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(17, "[N/mm^2]"),
            "f_c90": Unit(2.2, "[N/mm^2]"),
            "f_v": Unit(3.2, "[N/mm^2]"),
            "E_0mean": Unit(8, "[kN/mm^2]"),
            "E_005": Unit(5.4, "[kN/mm^2]"),
            "E_90mean": Unit(0.27, "[kN/mm^2]"),
            "G_mean": Unit(0.50, "[kN/mm^2]"),
            "rho": Unit(310, "[kg/m^3]"),
            "rho_mean": Unit(370, "[kg/m^3]"),
        }
        self.C18 = {
            "f_m": Unit(18, "[N/mm^2]"),
            "f_t0": Unit(11, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(18, "[N/mm^2]"),
            "f_c90": Unit(2.2, "[N/mm^2]"),
            "f_v": Unit(3.4, "[N/mm^2]"),
            "E_0mean": Unit(9, "[kN/mm^2]"),
            "E_005": Unit(6.0, "[kN/mm^2]"),
            "E_90mean": Unit(0.30, "[kN/mm^2]"),
            "G_mean": Unit(0.56, "[kN/mm^2]"),
            "rho": Unit(320, "[kg/m^3]"),
            "rho_mean": Unit(380, "[kg/m^3]"),
        }
        self.C20 = {
            "f_m": Unit(20, "[N/mm^2]"),
            "f_t0": Unit(12, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(19, "[N/mm^2]"),
            "f_c90": Unit(2.3, "[N/mm^2]"),
            "f_v": Unit(3.6, "[N/mm^2]"),
            "E_0mean": Unit(9.5, "[kN/mm^2]"),
            "E_005": Unit(6.4, "[kN/mm^2]"),
            "E_90mean": Unit(0.32, "[kN/mm^2]"),
            "G_mean": Unit(0.59, "[kN/mm^2]"),
            "rho": Unit(330, "[kg/m^3]"),
            "rho_mean": Unit(390, "[kg/m^3]"),
        }
        self.C22 = {
            "f_m": Unit(22, "[N/mm^2]"),
            "f_t0": Unit(13, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(20, "[N/mm^2]"),
            "f_c90": Unit(2.4, "[N/mm^2]"),
            "f_v": Unit(3.8, "[N/mm^2]"),
            "E_0mean": Unit(10, "[kN/mm^2]"),
            "E_005": Unit(6.7, "[kN/mm^2]"),
            "E_90mean": Unit(0.33, "[kN/mm^2]"),
            "G_mean": Unit(0.63, "[kN/mm^2]"),
            "rho": Unit(340, "[kg/m^3]"),
            "rho_mean": Unit(410, "[kg/m^3]"),
        }
        self.C24 = {
            "f_m": Unit(24, "[N/mm^2]"),
            "f_t0": Unit(14, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(21, "[N/mm^2]"),
            "f_c90": Unit(2.5, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(11, "[kN/mm^2]"),
            "E_005": Unit(7.4, "[kN/mm^2]"),
            "E_90mean": Unit(0.37, "[kN/mm^2]"),
            "G_mean": Unit(0.69, "[kN/mm^2]"),
            "rho": Unit(350, "[kg/m^3]"),
            "rho_mean": Unit(420, "[kg/m^3]"),
        }
        self.C27 = {
            "f_m": Unit(27, "[N/mm^2]"),
            "f_t0": Unit(16, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(22, "[N/mm^2]"),
            "f_c90": Unit(2.6, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(11.5, "[kN/mm^2]"),
            "E_005": Unit(7.7, "[kN/mm^2]"),
            "E_90mean": Unit(0.38, "[kN/mm^2]"),
            "G_mean": Unit(0.72, "[kN/mm^2]"),
            "rho": Unit(370, "[kg/m^3]"),
            "rho_mean": Unit(450, "[kg/m^3]"),
        }
        self.C30 = {
            "f_m": Unit(30, "[N/mm^2]"),
            "f_t0": Unit(18, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(23, "[N/mm^2]"),
            "f_c90": Unit(2.7, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(12, "[kN/mm^2]"),
            "E_005": Unit(8.0, "[kN/mm^2]"),
            "E_90mean": Unit(0.40, "[kN/mm^2]"),
            "G_mean": Unit(0.75, "[kN/mm^2]"),
            "rho": Unit(380, "[kg/m^3]"),
            "rho_mean": Unit(470, "[kg/m^3]"),
        }
        self.C35 = {
            "f_m": Unit(35, "[N/mm^2]"),
            "f_t0": Unit(21, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(25, "[N/mm^2]"),
            "f_c90": Unit(2.8, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(13, "[kN/mm^2]"),
            "E_005": Unit(8.7, "[kN/mm^2]"),
            "E_90mean": Unit(0.43, "[kN/mm^2]"),
            "G_mean": Unit(0.81, "[kN/mm^2]"),
            "rho": Unit(400, "[kg/m^3]"),
            "rho_mean": Unit(480, "[kg/m^3]"),
        }
        self.C40 = {
            "f_m": Unit(40, "[N/mm^2]"),
            "f_t0": Unit(24, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(26, "[N/mm^2]"),
            "f_c90": Unit(2.9, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(14, "[kN/mm^2]"),
            "E_005": Unit(9.4, "[kN/mm^2]"),
            "E_90mean": Unit(0.47, "[kN/mm^2]"),
            "G_mean": Unit(0.88, "[kN/mm^2]"),
            "rho": Unit(420, "[kg/m^3]"),
            "rho_mean": Unit(500, "[kg/m^3]"),
        }
        self.C45 = {
            "f_m": Unit(45, "[N/mm^2]"),
            "f_t0": Unit(27, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(27, "[N/mm^2]"),
            "f_c90": Unit(3.1, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(15, "[kN/mm^2]"),
            "E_005": Unit(10.0, "[kN/mm^2]"),
            "E_90mean": Unit(0.50, "[kN/mm^2]"),
            "G_mean": Unit(0.94, "[kN/mm^2]"),
            "rho": Unit(440, "[kg/m^3]"),
            "rho_mean": Unit(520, "[kg/m^3]"),
        }
        self.C50 = {
            "f_m": Unit(50, "[N/mm^2]"),
            "f_t0": Unit(30, "[N/mm^2]"),
            "f_t90": Unit(0.4, "[N/mm^2]"),
            "f_c0": Unit(29, "[N/mm^2]"),
            "f_c90": Unit(3.2, "[N/mm^2]"),
            "f_v": Unit(4.0, "[N/mm^2]"),
            "E_0mean": Unit(16, "[kN/mm^2]"),
            "E_005": Unit(10.7, "[kN/mm^2]"),
            "E_90mean": Unit(0.53, "[kN/mm^2]"),
            "G_mean": Unit(1.0, "[kN/mm^2]"),
            "rho": Unit(460, "[kg/m^3]"),
            "rho_mean": Unit(550, "[kg/m^3]"),
        }

    def help(self):
        print(f"""
        (f_m, Bending strength) [N/mm^2]
        (f_t0, Tensile strength parallel to grain) [N/mm^2]
        (f_t90, Tensile strength perpendicular to grain) [N/mm^2]
        (f_c0, Compressive strength parallel to grain) [N/mm^2]
        (f_c90, Compressive strength perpendicular to grain) [N/mm^2]
        (f_v, Shear strength) [N/mm^2]
        (E_0mean, Mean modulus of elasticity parallel to grain) [kN/mm^2]
        (E_005, 5% percentile modulus of elasticity parallel to grain) [kN/mm^2]
        (E_90mean, Mean modulus of elasticity perpendicular to grain) [kN/mm^2]
        (G_mean, Mean shear modulus) [kN/mm^2]
        (rho, Characteristic density) [kg/m^3]
        (rho_mean, Mean density) [kg/m^3]
        """)

CONCRETE_CONSTANTS = {
    "nu_uncracked": Unit(0.2, "[]"),    # Poisson's ratio for uncracked concrete
    "nu_cracked": Unit(0.0, "[]"),      # Poisson's ratio for cracked concrete
    "rho_plain": Unit(2400, "[kg/m^3]"),      # Density of plain concrete [kg/m^3]
    "rho_reinforced": Unit(2500, "[kg/m^3]"), # Density of reinforced concrete [kg/m^3]
    "alpha": Unit(10e-6, "[1/K]")          # Coefficient of linear thermal expansion [1/K]
}

class Concrete:
    def __init__(self):
        self.C20_25 = {
            **CONCRETE_CONSTANTS,
            "fck": Unit(20, "[MPa]"),
            "fck_cube": Unit(25, "[MPa]"),
            "fcm": Unit(28, "[MPa]"),        # fck + 8
            "fctm": Unit(2.2, "[MPa]"),        # 0.3 * fck^(2/3)
            "Ecm": Unit(30, "[MPa]"),           # 22 * (fcm/10)^0.3
        }
        self.C25_30 = {
            **CONCRETE_CONSTANTS,
            "fck": Unit(25, "[MPa]"),
            "fck_cube": Unit(30, "[MPa]"),
            "fcm": Unit(33, "[MPa]"),
            "fctm": Unit(2.6, "[MPa]"),
            "Ecm": Unit(31, "[MPa]"),
        }
        self.C30_37 = {
            **CONCRETE_CONSTANTS,
            "fck": Unit(30, "[MPa]"),
            "fck_cube": Unit(37, "[MPa]"),
            "fcm": Unit(38, "[MPa]"),
            "fctm": Unit(2.9, "[MPa]"),
            "Ecm": Unit(33, "[MPa]"),
        }
        self.C35_45 = {
            **CONCRETE_CONSTANTS,
            "fck": Unit(35, "[MPa]"),
            "fck_cube": Unit(45, "[MPa]"),
            "fcm": Unit(43, "[MPa]"),
            "fctm": Unit(3.2, "[MPa]"),
            "Ecm": Unit(34, "[MPa]"),
        }

    def help(self):
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


class BoltGrades:
    def __init__(self):
        self.G3_6 = {"fyb": Unit(180, "[MPa]"), "fub": Unit(300, "[MPa]")}
        self.G4_6 = {"fyb": Unit(240, "[MPa]"), "fub": Unit(400, "[MPa]")}
        self.G4_8 = {"fyb": Unit(320, "[MPa]"), "fub": Unit(400, "[MPa]")}
        self.G5_6 = {"fyb": Unit(300, "[MPa]"), "fub": Unit(500, "[MPa]")}
        self.G5_8 = {"fyb": Unit(400, "[MPa]"), "fub": Unit(500, "[MPa]")}
        self.G6_8 = {"fyb": Unit(480, "[MPa]"), "fub": Unit(600, "[MPa]")}
        self.G8_8 = {"fyb": Unit(640, "[MPa]"), "fub": Unit(800, "[MPa]")}
        self.G9_8 = {"fyb": Unit(720, "[MPa]"), "fub": Unit(900, "[MPa]")}
        self.G10_9 = {"fyb": Unit(900, "[MPa]"), "fub": Unit(1000, "[MPa]")}
        self.G12_9 = {"fyb": Unit(1080, "[MPa]"), "fub": Unit(1200, "[MPa]")}
        
    def help(self):
        print(f"""
        (fyb, Yield strength of bolt) [MPa]
        (fub, Ultimate tensile strength of bolt) [MPa]
        """)


class BoltSizes:
    def __init__(self):
        self.M4 = {"d": Unit(4, "[mm]"), "A": Unit(12.6, "[mm^2]"), "As": Unit(8.78, "[mm^2]")}
        self.M5 = {"d": Unit(5, "[mm]"), "A": Unit(19.6, "[mm^2]"), "As": Unit(14.2, "[mm^2]")}
        self.M6 = {"d": Unit(6, "[mm]"), "A": Unit(28.3, "[mm^2]"), "As": Unit(20.1, "[mm^2]")}
        self.M8 = {"d": Unit(8, "[mm]"), "A": Unit(50.3, "[mm^2]"), "As": Unit(36.6, "[mm^2]")}
        self.M10 = {"d": Unit(10, "[mm]"), "A": Unit(78.5, "[mm^2]"), "As": Unit(58.0, "[mm^2]")}
        self.M12 = {"d": Unit(12, "[mm]"), "A": Unit(113.1, "[mm^2]"), "As": Unit(84.3, "[mm^2]")}
        self.M14 = {"d": Unit(14, "[mm]"), "A": Unit(153.9, "[mm^2]"), "As": Unit(115.0, "[mm^2]")}
        self.M16 = {"d": Unit(16, "[mm]"), "A": Unit(201.1, "[mm^2]"), "As": Unit(157.0, "[mm^2]")}
        self.M18 = {"d": Unit(18, "[mm]"), "A": Unit(254.5, "[mm^2]"), "As": Unit(192.0, "[mm^2]")}
        self.M20 = {"d": Unit(20, "[mm]"), "A": Unit(314.2, "[mm^2]"), "As": Unit(245.0, "[mm^2]")}
        self.M22 = {"d": Unit(22, "[mm]"), "A": Unit(380.1, "[mm^2]"), "As": Unit(303.0, "[mm^2]")}
        self.M24 = {"d": Unit(24, "[mm]"), "A": Unit(452.4, "[mm^2]"), "As": Unit(353.0, "[mm^2]")}
        self.M27 = {"d": Unit(27, "[mm]"), "A": Unit(572.6, "[mm^2]"), "As": Unit(459.0, "[mm^2]")}
        self.M30 = {"d": Unit(30, "[mm]"), "A": Unit(706.9, "[mm^2]"), "As": Unit(561.0, "[mm^2]")}
        self.M33 = {"d": Unit(33, "[mm]"), "A": Unit(855.3, "[mm^2]"), "As": Unit(694.0, "[mm^2]")}
        self.M36 = {"d": Unit(36, "[mm]"), "A": Unit(1017.9, "[mm^2]"), "As": Unit(817.0, "[mm^2]")}
        
    def help(self):
        print(f"""
        (d, Nominal diameter) [mm]
        (A, Nominal cross-sectional area) [mm^2]
        (As, Tensile stress area) [mm^2]
        """)


class Rebar:
    def __init__(self):
        self.phi6 = {"d": Unit(6, "[mm]"), "As": Unit(28.3, "[mm^2]"), "u": Unit(18.8, "[mm]"), "weight": Unit(0.222, "[kg/m]")}
        self.phi8 = {"d": Unit(8, "[mm]"), "As": Unit(50.3, "[mm^2]"), "u": Unit(25.1, "[mm]"), "weight": Unit(0.395, "[kg/m]")}
        self.phi10 = {"d": Unit(10, "[mm]"), "As": Unit(78.5, "[mm^2]"), "u": Unit(31.4, "[mm]"), "weight": Unit(0.617, "[kg/m]")}
        self.phi12 = {"d": Unit(12, "[mm]"), "As": Unit(113.1, "[mm^2]"), "u": Unit(37.7, "[mm]"), "weight": Unit(0.888, "[kg/m]")}
        self.phi14 = {"d": Unit(14, "[mm]"), "As": Unit(153.9, "[mm^2]"), "u": Unit(44.0, "[mm]"), "weight": Unit(1.21, "[kg/m]")}
        self.phi16 = {"d": Unit(16, "[mm]"), "As": Unit(201.1, "[mm^2]"), "u": Unit(50.3, "[mm]"), "weight": Unit(1.58, "[kg/m]")}
        self.phi20 = {"d": Unit(20, "[mm]"), "As": Unit(314.2, "[mm^2]"), "u": Unit(62.8, "[mm]"), "weight": Unit(2.47, "[kg/m]")}
        self.phi25 = {"d": Unit(25, "[mm]"), "As": Unit(490.9, "[mm^2]"), "u": Unit(78.5, "[mm]"), "weight": Unit(3.85, "[kg/m]")}
        self.phi32 = {"d": Unit(32, "[mm]"), "As": Unit(804.2, "[mm^2]"), "u": Unit(100.5, "[mm]"), "weight": Unit(6.31, "[kg/m]")}
        
    def help(self):
        print(f"""
        (d, Nominal diameter) [mm]
        (As, Cross-sectional area) [mm^2]
        (u, Perimeter) [mm]
        (weight, Nominal weight per meter) [kg/m]
        """)

