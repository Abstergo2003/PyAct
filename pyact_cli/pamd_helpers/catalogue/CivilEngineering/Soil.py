from pyact_cli.pamd_helpers.unit import Unit
# ==========================================
# COARSE-GRAINED SOILS (Non-Cohesive)
# ==========================================

# GRAVEL
Gravel_Dense = {
    "gamma": Unit(20.0, "[kN/m3]"), 
    "gamma_sat": Unit(22.0, "[kN/m3]"),
    "phi": Unit(38.0, "[deg]"), 
    "c": Unit(0.0, "[kPa]"), 
    "E": Unit(150.0, "[MPa]"), 
    "nu": Unit(0.3, "[-]"),
    "qa": Unit(600.0, "[kPa]")
}
Gravel_Loose = {
    "gamma": Unit(18.0, "[kN/m3]"), 
    "gamma_sat": Unit(20.0, "[kN/m3]"),
    "phi": Unit(32.0, "[deg]"), 
    "c": Unit(0.0, "[kPa]"), 
    "E": Unit(80.0, "[MPa]"), 
    "nu": Unit(0.3, "[-]"),
    "qa": Unit(400.0, "[kPa]")
}

# SAND
Sand_Dense = {
    "gamma": Unit(19.0, "[kN/m3]"), 
    "gamma_sat": Unit(21.0, "[kN/m3]"),
    "phi": Unit(35.0, "[deg]"), 
    "c": Unit(0.0, "[kPa]"), 
    "E": Unit(75.0, "[MPa]"), 
    "nu": Unit(0.3, "[-]"),
    "qa": Unit(300.0, "[kPa]")
}
Sand_Medium = {
    "gamma": Unit(18.0, "[kN/m3]"), 
    "gamma_sat": Unit(20.0, "[kN/m3]"),
    "phi": Unit(32.0, "[deg]"), 
    "c": Unit(0.0, "[kPa]"), 
    "E": Unit(40.0, "[MPa]"), 
    "nu": Unit(0.3, "[-]"),
    "qa": Unit(200.0, "[kPa]")
}
Sand_Loose = {
    "gamma": Unit(17.0, "[kN/m3]"), 
    "gamma_sat": Unit(19.0, "[kN/m3]"),
    "phi": Unit(29.0, "[deg]"), 
    "c": Unit(0.0, "[kPa]"), 
    "E": Unit(20.0, "[MPa]"), 
    "nu": Unit(0.3, "[-]"),
    "qa": Unit(100.0, "[kPa]")
}

# ==========================================
# FINE-GRAINED SOILS (Cohesive)
# ==========================================

# SILT
Silt = {
    "gamma": Unit(18.0, "[kN/m3]"), 
    "gamma_sat": Unit(19.5, "[kN/m3]"),
    "phi": Unit(28.0, "[deg]"), 
    "c": Unit(10.0, "[kPa]"), 
    "cu": Unit(40.0, "[kPa]"),
    "E": Unit(15.0, "[MPa]"), 
    "nu": Unit(0.35, "[-]"),
}

# CLAY
Clay_Stiff = {
    "gamma": Unit(20.0, "[kN/m3]"), 
    "gamma_sat": Unit(20.5, "[kN/m3]"),
    "phi": Unit(22.0, "[deg]"), 
    "c": Unit(50.0, "[kPa]"), 
    "cu": Unit(150.0, "[kPa]"),
    "E": Unit(35.0, "[MPa]"), 
    "nu": Unit(0.4, "[-]"),
    "qa": Unit(200.0, "[kPa]")
}
Clay_Firm = {
    "gamma": Unit(18.0, "[kN/m3]"), 
    "gamma_sat": Unit(18.5, "[kN/m3]"),
    "phi": Unit(20.0, "[deg]"), 
    "c": Unit(20.0, "[kPa]"), 
    "cu": Unit(50.0, "[kPa]"),
    "E": Unit(15.0, "[MPa]"), 
    "nu": Unit(0.45, "[-]"),
    "qa": Unit(100.0, "[kPa]")
}
Clay_Soft = {
    "gamma": Unit(16.0, "[kN/m3]"), 
    "gamma_sat": Unit(16.5, "[kN/m3]"),
    "phi": Unit(18.0, "[deg]"), 
    "c": Unit(10.0, "[kPa]"), 
    "cu": Unit(20.0, "[kPa]"),
    "E": Unit(5.0, "[MPa]"), 
    "nu": Unit(0.45, "[-]"),
    "qa": Unit(50.0, "[kPa]")
}

# PEAT (Highly organic)
Peat = {
    "gamma": Unit(11.0, "[kN/m3]"), 
    "gamma_sat": Unit(12.0, "[kN/m3]"),
    "phi": Unit(15.0, "[deg]"), 
    "c": Unit(5.0, "[kPa]"), 
    "cu": Unit(10.0, "[kPa]"),
    "E": Unit(1.0, "[MPa]"), 
    "nu": Unit(0.45, "[-]"),
    "qa": Unit(600.0, "[kPa]")
}

def help():
    print(f"""
        Comprehensive dictionary of typical geotechnical properties for various soil classifications.
        Values are representative averages meant for preliminary structural/geotechnical design.
        (gamma, Bulk unit weight) [kN/m3]
        (gamma_sat, Saturated unit weight) [kN/m3]
        (phi, Effective angle of internal friction) [deg]
        (c, Effective cohesion) [kPa]
        (cu, Undrained shear strength) [kPa]  <-- Specific to cohesive soils!
        (E, Modulus of elasticity / Young's modulus) [MPa]
        (nu, Poisson's ratio) [-]
        (qa, Presumed allowable bearing pressure) [kPa]
    """)