from pyact_cli.pamd_helpers.unit import Unit

Adenine = {"MW_Da": Unit(135.13, "[Da]")}
Guanine = {"MW_Da": Unit(151.13, "[Da]")}
Cytosine = {"MW_Da": Unit(111.10, "[Da]")}
Thymine = {"MW_Da": Unit(126.11, "[Da]")}
Uracil = {"MW_Da": Unit(112.09, "[Da]")}
        
def help():
    print("""
        (MW_Da, Molecular Weight of the free base) [Da]
    """)
