from pyact_cli.pamd_helpers.unit import Unit


ATP_to_ADP = {"dG0_kJ_mol": Unit(-30.5, "[kJ/mol]")}
ATP_to_AMP = {"dG0_kJ_mol": Unit(-45.6, "[kJ/mol]")}
ADP_to_AMP = {"dG0_kJ_mol": Unit(-32.8, "[kJ/mol]")}
Phosphoenolpyruvate = {"dG0_kJ_mol": Unit(-61.9, "[kJ/mol]")}
Creatine_phosphate = {"dG0_kJ_mol": Unit(-43.1, "[kJ/mol]")}
Glucose_6_phosphate = {"dG0_kJ_mol": Unit(-13.8, "[kJ/mol]")}

def help():
    print("""
        (dG0_kJ_mol, Standard free energy of hydrolysis at pH 7.0) [kJ/mol]
    """)
