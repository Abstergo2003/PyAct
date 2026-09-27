from pyact_cli.pamd_helpers.unit import Unit


Water = {"A": Unit(5.40221, "[-]"), "B": Unit(1838.675, "[K]"), "C": Unit(-31.737, "[K]")}
Ethanol = {"A": Unit(5.24677, "[-]"), "B": Unit(1598.673, "[K]"), "C": Unit(-46.424, "[K]")}
Methanol = {"A": Unit(5.20409, "[-]"), "B": Unit(1581.341, "[K]"), "C": Unit(-33.50, "[K]")}
Acetone = {"A": Unit(4.42448, "[-]"), "B": Unit(1312.253, "[K]"), "C": Unit(-32.445, "[K]")}
Benzene = {"A": Unit(4.72583, "[-]"), "B": Unit(1660.652, "[K]"), "C": Unit(-1.461, "[K]")}

def help():
    print("""
        Antoine Equation Constants: log10(P) = A - (B / (T + C))
        where P is in bar, and T is in Kelvin.
        (A, Antoine A constant) [-]
        (B, Antoine B constant) [K]
        (C, Antoine C constant) [K]
        Use with: log10(P[bar]) = A - (B / (T[K] + C))
    """)
