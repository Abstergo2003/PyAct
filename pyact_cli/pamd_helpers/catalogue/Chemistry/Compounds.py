from pyact_cli.pamd_helpers.unit import Unit


Water = {"M_g_mol": Unit(18.015, "[g/mol]"), "dH_f_kJ_mol": Unit(-285.8, "[kJ/mol]"), "S_J_mol_K": Unit(69.9, "[J/(mol*K)]"), "Cp_J_g_K": Unit(4.184, "[J/(g*K)]")}
CarbonDioxide = {"M_g_mol": Unit(44.01, "[g/mol]"), "dH_f_kJ_mol": Unit(-393.5, "[kJ/mol]"), "S_J_mol_K": Unit(213.8, "[J/(mol*K)]"), "Cp_J_g_K": Unit(0.839, "[J/(g*K)]")}
Methane = {"M_g_mol": Unit(16.04, "[g/mol]"), "dH_f_kJ_mol": Unit(-74.8, "[kJ/mol]"), "S_J_mol_K": Unit(186.3, "[J/(mol*K)]"), "Cp_J_g_K": Unit(2.22, "[J/(g*K)]")}
Ammonia = {"M_g_mol": Unit(17.03, "[g/mol]"), "dH_f_kJ_mol": Unit(-45.9, "[kJ/mol]"), "S_J_mol_K": Unit(192.8, "[J/(mol*K)]"), "Cp_J_g_K": Unit(2.09, "[J/(g*K)]")}
SulfuricAcid = {"M_g_mol": Unit(98.08, "[g/mol]"), "dH_f_kJ_mol": Unit(-814.0, "[kJ/mol]"), "S_J_mol_K": Unit(156.9, "[J/(mol*K)]"), "Cp_J_g_K": Unit(1.42, "[J/(g*K)]")}

def help():
    print("""
        (M_g_mol, Molar Mass) [g/mol]
        (dH_f_kJ_mol, Standard Enthalpy of Formation) [kJ/mol]
        (S_J_mol_K, Standard Entropy) [J/(mol*K)]
        (Cp_J_g_K, Specific Heat Capacity) [J/(g*K)]
    """)
