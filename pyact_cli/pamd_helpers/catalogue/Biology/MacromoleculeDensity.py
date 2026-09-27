from pyact_cli.pamd_helpers.unit import Unit


GlobularProteins = {"Density_g_cm3": Unit(1.37, "[g/cm3]"), "SpecVolume_cm3_g": Unit(0.73, "[cm3/g]")}
DNA = {"Density_g_cm3": Unit(1.70, "[g/cm3]"), "SpecVolume_cm3_g": Unit(0.55, "[cm3/g]")}
RNA = {"Density_g_cm3": Unit(1.90, "[g/cm3]"), "SpecVolume_cm3_g": Unit(0.53, "[cm3/g]")}
Carbohydrates = {"Density_g_cm3": Unit(1.60, "[g/cm3]"), "SpecVolume_cm3_g": Unit(0.63, "[cm3/g]")}
Lipids = {"Density_g_cm3": Unit(0.92, "[g/cm3]"), "SpecVolume_cm3_g": Unit(1.08, "[cm3/g]")}

def help():
    print("""
        Partial specific volumes and densities for ultracentrifugation.
        (Density_g_cm3, Average buoyant density) [g/cm3]
        (SpecVolume_cm3_g, Partial specific volume) [cm3/g]
    """)
