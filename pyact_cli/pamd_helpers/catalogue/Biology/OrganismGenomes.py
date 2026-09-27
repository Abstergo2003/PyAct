from pyact_cli.pamd_helpers.unit import Unit

Escherichia_coli = {"GenomeSize_bp": Unit(4.6e6, "[bp]"), "EstimatedGenes": Unit(4300, "[-]"), "Chromosomes": Unit(1, "[-]")}
Saccharomyces_cerevisiae = {"GenomeSize_bp": Unit(1.2e7, "[bp]"), "EstimatedGenes": Unit(6000, "[-]"), "Chromosomes": Unit(16, "[-]")}
Caenorhabditis_elegans = {"GenomeSize_bp": Unit(1.0e8, "[bp]"), "EstimatedGenes": Unit(20000, "[-]"), "Chromosomes": Unit(6, "[-]")}
Drosophila_melanogaster = {"GenomeSize_bp": Unit(1.4e8, "[bp]"), "EstimatedGenes": Unit(14000, "[-]"), "Chromosomes": Unit(4, "[-]")}
Homo_sapiens = {"GenomeSize_bp": Unit(3.2e9, "[bp]"), "EstimatedGenes": Unit(20000, "[-]"), "Chromosomes": Unit(46, "[-]")}

def help():
    print("""
        (GenomeSize_bp, Size of haploid genome in base pairs) [bp]
        (EstimatedGenes, Number of protein-coding genes) [-]
        (Chromosomes, Typical diploid/haploid depending on species standard) [-]
    """)
