import os
import glob
import json
import re

def sanitize_name(name):
    """
    Converts an arbitrary string into a valid Python identifier.
    E.g. 'Advance UKB (BS 4-1:2005)' -> 'Advance_UKB_BS_4_1_2005'
    """
    s = re.sub(r'[\s\-/,.:;()[\]{}]', '_', name)
    s = re.sub(r'[^a-zA-Z0-9_]', '', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    
    if s and s[0].isdigit():
        s = '_' + s
        
    return s

def get_unit_from_key(key):
    """
    Extracts the unit string assuming the key was formatted like 'h_mm' or 'A_cm2'
    """
    parts = key.rsplit('_', 1)
    if len(parts) == 2:
        unit = parts[1]
        if unit in ['mm', 'cm', 'm', 'cm2', 'cm3', 'cm4', 'cm6', 'kg_m', 'kg']:
            return f"[{unit}]"
    return "[-]"

def generate_python_classes():
    directory = os.path.dirname(os.path.abspath(__file__))
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    print("Starting JSON to Python classes conversion...")
    
    for file_path in json_files:
        print(f"Processing: {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {file_path} - Invalid JSON")
                continue
                
        # 1. Sanitize Data
        sanitized_data = {}
        for series_name, beams in data.items():
            clean_series_name = sanitize_name(series_name)
            new_beams = {}
            for beam_name, beam_props in beams.items():
                clean_beam_name = sanitize_name(beam_name)
                clean_props = {}
                for prop, val in beam_props.items():
                    clean_prop = sanitize_name(prop)
                    clean_props[clean_prop] = val
                new_beams[clean_beam_name] = clean_props
            sanitized_data[clean_series_name] = new_beams
            
        # 2. Generate Python File
        base_name = os.path.basename(file_path).replace('.json', '')
        py_module_name = sanitize_name(base_name)
        py_file_path = os.path.join(directory, py_module_name + ".py")
        
        lines = []
        lines.append("from pamd_helpers.standard_values import Unit\n")
        
        for series_name, beams in sanitized_data.items():
            lines.append(f"class {series_name}:")
            lines.append("    def __init__(self):")
            
            all_props = set()
            if not beams:
                lines.append("        pass\n")
                continue
                
            for beam_name, props in beams.items():
                dict_entries = []
                for prop_k, prop_v in props.items():
                    all_props.add(prop_k)
                    unit_str = get_unit_from_key(prop_k)
                    if isinstance(prop_v, (int, float)):
                        dict_entries.append(f'"{prop_k}": Unit({prop_v}, "{unit_str}")')
                    else:
                        dict_entries.append(f'"{prop_k}": "{prop_v}"')
                        
                dict_str = "{" + ", ".join(dict_entries) + "}"
                lines.append(f"        self.{beam_name} = {dict_str}")
                
            lines.append("")
            lines.append("    def help(self):")
            lines.append("        print(f\"\"\"")
            for prop in sorted(all_props):
                unit_str = get_unit_from_key(prop)
                lines.append(f"        ({prop}) {unit_str}")
            lines.append("        \"\"\")\n")
            
        # 3. Add Master Class
        lines.append(f"class {py_module_name}:")
        lines.append("    def __init__(self):")
        if sanitized_data.keys():
            for series_name in sanitized_data.keys():
                lines.append(f"        self.{series_name} = {series_name}()")
        else:
            lines.append("        pass")
        lines.append("")
            
        with open(py_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        print(f"✅ Generated {py_module_name}.py successfully!")

if __name__ == "__main__":
    generate_python_classes()
