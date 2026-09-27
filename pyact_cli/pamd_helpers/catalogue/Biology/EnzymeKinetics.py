from pyact_cli.pamd_helpers.unit import Unit

# Catalase (one of the fastest enzymes)
Catalase = {"kcat_1_s": Unit(4.0e7, "[1/s]"), "Km_M": Unit(1.1, "[M]")}
# Acetylcholinesterase
Acetylcholinesterase = {"kcat_1_s": Unit(1.4e4, "[1/s]"), "Km_M": Unit(9.0e-5, "[M]")}
# Carbonic Anhydrase
CarbonicAnhydrase = {"kcat_1_s": Unit(1.0e6, "[1/s]"), "Km_M": Unit(1.2e-2, "[M]")}
# Hexokinase
Hexokinase = {"kcat_1_s": Unit(4.0e2, "[1/s]"), "Km_M": Unit(4.0e-4, "[M]")}

def help():
    print("""
        Typical Michaelis-Menten kinetic parameters for reference enzymes.
        Values can vary heavily based on conditions and substrate.
        (kcat_1_s, Turnover number / kcat) [1/s]
        (Km_M, Michaelis constant) [M] -> Moles per Liter
    """)
