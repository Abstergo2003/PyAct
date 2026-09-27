from pyact_cli.pamd_helpers.unit import Unit


# E. coli (bacterium)
Ecoli = {"Volume_um3": Unit(1.0, "[um3]"), "Mass_pg": Unit(1.0, "[pg]"), "Length_um": Unit(2.0, "[um]")}
# S. cerevisiae (yeast)
Yeast = {"Volume_um3": Unit(42.0, "[um3]"), "Mass_pg": Unit(42.0, "[pg]"), "Diameter_um": Unit(5.0, "[um]")}
# Human Erythrocyte (RBC)
RedBloodCell = {"Volume_um3": Unit(90.0, "[um3]"), "Diameter_um": Unit(8.0, "[um]")}
# HeLa Cell (human cancer cell line)
HeLa = {"Volume_um3": Unit(3000.0, "[um3]"), "Diameter_um": Unit(20.0, "[um]")}

def help():
    print("""
        (Volume_um3, Cell Volume) [um^3]
        (Mass_pg, Typical wet mass) [picograms]
        (Diameter_um, Typical diameter/length) [um]
    """)
