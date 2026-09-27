from pyact_cli.pamd_helpers.unit import Unit


Li_plus_to_Li = {"E_V": Unit(-3.04, "[V]")}
K_plus_to_K = {"E_V": Unit(-2.93, "[V]")}
Ca_2plus_to_Ca = {"E_V": Unit(-2.87, "[V]")}
Na_plus_to_Na = {"E_V": Unit(-2.71, "[V]")}
Mg_2plus_to_Mg = {"E_V": Unit(-2.37, "[V]")}
Al_3plus_to_Al = {"E_V": Unit(-1.66, "[V]")}
Zn_2plus_to_Zn = {"E_V": Unit(-0.76, "[V]")}
Fe_2plus_to_Fe = {"E_V": Unit(-0.44, "[V]")}
Pb_2plus_to_Pb = {"E_V": Unit(-0.13, "[V]")}
H_plus_to_H2 = {"E_V": Unit(0.00, "[V]")}
Cu_2plus_to_Cu = {"E_V": Unit(0.34, "[V]")}
Ag_plus_to_Ag = {"E_V": Unit(0.80, "[V]")}
Cl2_to_Cl_minus = {"E_V": Unit(1.36, "[V]")}
F2_to_F_minus = {"E_V": Unit(2.87, "[V]")}

def help():
    print("""
        (E_V, Standard Reduction Potential at 25C) [V]
    """)
