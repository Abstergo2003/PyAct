from pyact_cli.pamd_helpers.unit import Unit

Water = {"dH_fus_kJ_mol": Unit(6.01, "[kJ/mol]"), "dH_vap_kJ_mol": Unit(40.65, "[kJ/mol]")}
Ethanol = {"dH_fus_kJ_mol": Unit(4.9, "[kJ/mol]"), "dH_vap_kJ_mol": Unit(38.56, "[kJ/mol]")}
Methanol = {"dH_fus_kJ_mol": Unit(3.22, "[kJ/mol]"), "dH_vap_kJ_mol": Unit(35.2, "[kJ/mol]")}
Ammonia = {"dH_fus_kJ_mol": Unit(5.66, "[kJ/mol]"), "dH_vap_kJ_mol": Unit(23.33, "[kJ/mol]")}
Benzene = {"dH_fus_kJ_mol": Unit(9.87, "[kJ/mol]"), "dH_vap_kJ_mol": Unit(30.72, "[kJ/mol]")}

def help():
    print("""
        (dH_fus_kJ_mol, Enthalpy of Fusion) [kJ/mol]
        (dH_vap_kJ_mol, Enthalpy of Vaporization) [kJ/mol]
    """)
