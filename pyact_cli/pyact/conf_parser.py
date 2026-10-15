import os

def conf_parser(conf_path: str) -> dict:
    """
    Parses a pamd.conf configuration file into a dictionary of sections and settings.
    
    Why it is needed:
    Allows PyAct projects to define global Word export settings such as Headers, Footers, 
    Page margins/orientations, and document Metadata without cluttering Markdown templates 
    or Python code cells.
    
    Inputs:
        conf_path (str): Path to the pamd.conf file.
        
    Outputs:
        dict: A nested dictionary of sections and their key-value options.
              Example: {'Header': {'left': 'PyAct'}, 'Metadata': {'author': 'Radek'}}
    """
    if not conf_path or not os.path.exists(conf_path):
        return {}
        
    parsed_dict = {}
    current_header = "General"
    
    with open(conf_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            # Skip empty lines and comment lines starting with # or ;
            if not stripped or stripped.startswith(('#', ';')):
                continue
                
            if stripped.startswith('[') and stripped.endswith(']'):
                current_header = stripped[1:-1].strip()
                if current_header not in parsed_dict:
                    parsed_dict[current_header] = {}
            elif '=' in stripped:
                head, tail = stripped.split('=', 1)
                key = head.strip()
                val = tail.strip()
                if current_header not in parsed_dict:
                    parsed_dict[current_header] = {}
                parsed_dict[current_header][key] = val
                
    return parsed_dict