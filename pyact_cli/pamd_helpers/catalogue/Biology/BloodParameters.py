from pyact_cli.pamd_helpers.unit import Unit

pH = {"NormalRange_min": Unit(7.35, "[-]"), "NormalRange_max": Unit(7.45, "[-]")}
Osmolarity = {"Value_mOsm_L": Unit(290.0, "[mOsm/L]")}
Hemoglobin_Male = {"Value_g_dL": Unit(15.5, "[g/dL]")}
Hemoglobin_Female = {"Value_g_dL": Unit(14.0, "[g/dL]")}
TotalProtein = {"Value_g_dL": Unit(7.0, "[g/dL]")}
FastingGlucose = {"Value_mg_dL": Unit(90.0, "[mg/dL]")}

def help():
    print("""
        Various clinical parameters for adult humans.
    """)
