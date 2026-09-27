from pyact_cli.pamd_helpers.unit import Unit

R_K= Unit(25812.80745, "[Omega]"),
R_inf = Unit(10973731.568157, "[1/m]"),
K_J = Unit(483597.848484e9, "[Hz/V]"),
alpha = Unit(0.0072973525643, "[]"),
m_e = Unit(9.1093837139e-31, "[kg]"),
mi_0 = Unit(1.25663706127e-6, "[N/A^2]"),
epsilon_0 = Unit(8.8541878188e-12, "[F/m]"),
h = Unit(6.62607015e-34, "[J/Hz]"),
e = Unit(1.602176634e-19, "[C]"),
g = Unit(9.80665, "[m/s^2]"),           # Acceleration due to gravity
G = Unit(6.67430e-11, "[m^3/kg/s^2]"),        # Gravitational constant
c = Unit(299792458, "[m/s]"),          # Speed of light
R = Unit(8.314462618, "[J/(mol*K)]"),        # Ideal gas constant
atm = Unit(101325, "[Pa]"),           # Standard atmosphere
N_A = Unit(6.02214076e23, "[1/mol]"),        # Avogadro constant
F = Unit(96485.3321, "[C/mol]"),             # Faraday constant
k_B = Unit(1.380649e-23, "[J/K]"),           # Boltzmann constant

def help():
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
        (N_A, Avogadro constant) [1/mol]
        (F, Faraday constant) [C/mol]
        (k_B, Boltzmann constant) [J/K]
    """)