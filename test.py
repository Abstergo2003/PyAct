import pyact_cli.pamd_helpers as pamd_helpers

def context():
    headers = ["Part", "Quantity", "Material"]
    data = [
        ["Bolt M8", 120, "Steel"],
        ["Bracket", 45, "Aluminum"]
    ]

        # This will generate a CAD file named 'bom_table.dxf' in your project folder!
    dxf_link = pamd_helpers.table_to_dxf(headers, data, "bom_table.dxf")

    return {
        "dxf_download": dxf_link
    }

context()