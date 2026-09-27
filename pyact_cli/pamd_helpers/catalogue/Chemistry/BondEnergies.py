from pyact_cli.pamd_helpers.unit import Unit


C_H = {"E_kJ_mol": Unit(413, "[kJ/mol]")}
C_C = {"E_kJ_mol": Unit(348, "[kJ/mol]")}
C_double_C = {"E_kJ_mol": Unit(614, "[kJ/mol]")}
C_triple_C = {"E_kJ_mol": Unit(839, "[kJ/mol]")}
C_O = {"E_kJ_mol": Unit(358, "[kJ/mol]")}
C_double_O = {"E_kJ_mol": Unit(799, "[kJ/mol]")}
O_H = {"E_kJ_mol": Unit(463, "[kJ/mol]")}
O_double_O = {"E_kJ_mol": Unit(495, "[kJ/mol]")}
N_H = {"E_kJ_mol": Unit(391, "[kJ/mol]")}
N_triple_N = {"E_kJ_mol": Unit(941, "[kJ/mol]")}
H_H = {"E_kJ_mol": Unit(436, "[kJ/mol]")}
Cl_Cl = {"E_kJ_mol": Unit(242, "[kJ/mol]")}
H_Cl = {"E_kJ_mol": Unit(431, "[kJ/mol]")}

def help(self):
    print("""
        (E_kJ_mol, Average Bond Dissociation Energy) [kJ/mol]
    """)
