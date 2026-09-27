from pyact_cli.pamd_helpers.unit import Unit

AceticAcid = {"pKa": Unit(4.76, "[-]")}
FormicAcid = {"pKa": Unit(3.75, "[-]")}
HydrofluoricAcid = {"pKa": Unit(3.17, "[-]")}
NitrousAcid = {"pKa": Unit(3.39, "[-]")}
CarbonicAcid_1 = {"pKa": Unit(6.35, "[-]")}
CarbonicAcid_2 = {"pKa": Unit(10.33, "[-]")}
PhosphoricAcid_1 = {"pKa": Unit(2.15, "[-]")}
PhosphoricAcid_2 = {"pKa": Unit(7.20, "[-]")}
PhosphoricAcid_3 = {"pKa": Unit(12.35, "[-]")}
AmmoniumIon = {"pKa": Unit(9.25, "[-]")}

def help():
    print("""
        (pKa, Acid dissociation constant) [-]
    """)
