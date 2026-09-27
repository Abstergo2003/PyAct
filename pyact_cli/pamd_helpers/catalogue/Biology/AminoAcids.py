from pyact_cli.pamd_helpers.unit import Unit

# Alanine (Ala, A)
Alanine = {"MW_Da": Unit(89.09, "[Da]"), "pI": Unit(6.01, "[-]"), "Hydropathy": Unit(1.8, "[-]")}
# Arginine (Arg, R)
Arginine = {"MW_Da": Unit(174.20, "[Da]"), "pI": Unit(10.76, "[-]"), "Hydropathy": Unit(-4.5, "[-]")}
# Asparagine (Asn, N)
Asparagine = {"MW_Da": Unit(132.12, "[Da]"), "pI": Unit(5.41, "[-]"), "Hydropathy": Unit(-3.5, "[-]")}
# Aspartic Acid (Asp, D)
AsparticAcid = {"MW_Da": Unit(133.10, "[Da]"), "pI": Unit(2.77, "[-]"), "Hydropathy": Unit(-3.5, "[-]")}
# Cysteine (Cys, C)
Cysteine = {"MW_Da": Unit(121.16, "[Da]"), "pI": Unit(5.02, "[-]"), "Hydropathy": Unit(2.5, "[-]")}
# Glutamic Acid (Glu, E)
GlutamicAcid = {"MW_Da": Unit(147.13, "[Da]"), "pI": Unit(3.22, "[-]"), "Hydropathy": Unit(-3.5, "[-]")}
# Glutamine (Gln, Q)
Glutamine = {"MW_Da": Unit(146.15, "[Da]"), "pI": Unit(5.65, "[-]"), "Hydropathy": Unit(-3.5, "[-]")}
# Glycine (Gly, G)
Glycine = {"MW_Da": Unit(75.07, "[Da]"), "pI": Unit(5.97, "[-]"), "Hydropathy": Unit(-0.4, "[-]")}
# Histidine (His, H)
Histidine = {"MW_Da": Unit(155.15, "[Da]"), "pI": Unit(7.59, "[-]"), "Hydropathy": Unit(-3.2, "[-]")}
# Isoleucine (Ile, I)
Isoleucine = {"MW_Da": Unit(131.17, "[Da]"), "pI": Unit(6.02, "[-]"), "Hydropathy": Unit(4.5, "[-]")}
# Leucine (Leu, L)
Leucine = {"MW_Da": Unit(131.17, "[Da]"), "pI": Unit(5.98, "[-]"), "Hydropathy": Unit(3.8, "[-]")}
# Lysine (Lys, K)
Lysine = {"MW_Da": Unit(146.19, "[Da]"), "pI": Unit(9.74, "[-]"), "Hydropathy": Unit(-3.9, "[-]")}
# Methionine (Met, M)
Methionine = {"MW_Da": Unit(149.21, "[Da]"), "pI": Unit(5.74, "[-]"), "Hydropathy": Unit(1.9, "[-]")}
# Phenylalanine (Phe, F)
Phenylalanine = {"MW_Da": Unit(165.19, "[Da]"), "pI": Unit(5.48, "[-]"), "Hydropathy": Unit(2.8, "[-]")}
# Proline (Pro, P)
Proline = {"MW_Da": Unit(115.13, "[Da]"), "pI": Unit(6.30, "[-]"), "Hydropathy": Unit(-1.6, "[-]")}
# Serine (Ser, S)
Serine = {"MW_Da": Unit(105.09, "[Da]"), "pI": Unit(5.68, "[-]"), "Hydropathy": Unit(-0.8, "[-]")}
# Threonine (Thr, T)
Threonine = {"MW_Da": Unit(119.12, "[Da]"), "pI": Unit(5.60, "[-]"), "Hydropathy": Unit(-0.7, "[-]")}
# Tryptophan (Trp, W)
Tryptophan = {"MW_Da": Unit(204.23, "[Da]"), "pI": Unit(5.89, "[-]"), "Hydropathy": Unit(-0.9, "[-]")}
# Tyrosine (Tyr, Y)
Tyrosine = {"MW_Da": Unit(181.19, "[Da]"), "pI": Unit(5.66, "[-]"), "Hydropathy": Unit(-1.3, "[-]")}
# Valine (Val, V)
Valine = {"MW_Da": Unit(117.15, "[Da]"), "pI": Unit(5.96, "[-]"), "Hydropathy": Unit(4.2, "[-]")}

def help():
    print("""
        (MW_Da, Molecular Weight) [Da] or [g/mol]
        (pI, Isoelectric Point) [-]
        (Hydropathy, Kyte-Doolittle Hydropathy Index) [-]
    """)
