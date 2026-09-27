from pyact_cli.pamd_helpers.unit import Unit


AgCl = {"Ksp": Unit(1.77e-10, "[-]")}
AgBr = {"Ksp": Unit(5.35e-13, "[-]")}
AgI = {"Ksp": Unit(8.3e-17, "[-]")}
BaSO4 = {"Ksp": Unit(1.08e-10, "[-]")}
CaCO3 = {"Ksp": Unit(3.3e-9, "[-]")}
CaF2 = {"Ksp": Unit(3.9e-11, "[-]")}
PbCl2 = {"Ksp": Unit(1.7e-5, "[-]")}
MgOH2 = {"Ksp": Unit(5.61e-12, "[-]")}
ZnS = {"Ksp": Unit(2e-25, "[-]")}

def help():
    print("""
        (Ksp, Solubility product constant at 25C) [-]
    """)
