import re
import json

def css_to_dict(css_string: str) -> dict:
    """
    Parses a raw CSS string into a nested Python dictionary.
    
    Why it is needed:
    CSS is text-based and formatted with selectors, curly braces, and semicolons.
    To programmatically apply these styles to python-docx elements, we need to 
    convert the syntax into a highly structured, queryable dictionary map.
    
    Inputs:
        css_string (str): The raw contents of a CSS file as a string.
        
    Outputs:
        dict: A dictionary where keys are CSS selectors (e.g., 'p', 'h1') and 
              values are dictionaries of style properties (e.g., {'color': '#000'}).
    """
    # Remove CSS comments
    css_string = re.sub(r'/\*[\s\S]*?\*/', '', css_string)
    
    # Match selectors and their corresponding blocks
    pattern = r'([^{]+)\{([^}]+)\}'
    matches = re.findall(pattern, css_string)
    
    css_dict = {}
    for selector, block in matches:
        selector = selector.strip()
        
        # Parse individual CSS properties
        rules = {}
        for line in block.split(';'):
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                key, val = line.split(':', 1)
                rules[key.strip()] = val.strip()
        
        # Handle comma-separated selectors (e.g., 'h1, h2, h3')
        for sel in selector.split(','):
            sel = sel.strip()
            if sel:
                if sel not in css_dict:
                    css_dict[sel] = {}
                css_dict[sel].update(rules)
                
    return css_dict

def parse_css_file(file_path: str, as_json_string: bool = False):
    """
    Reads a CSS file from disk and parses it into a dictionary or JSON string.
    
    Why it is needed:
    Provides a clean interface for reading a physical file from the OS, extracting 
    its contents, and piping it into the core `css_to_dict` parser.
    
    Inputs:
        file_path (str): The path to the `.css` file on disk.
        as_json_string (bool): If True, returns the output as a serialized JSON string 
                               instead of a Python dictionary. Defaults to False.
                               
    Outputs:
        dict or str: The parsed CSS dictionary, or a JSON-formatted string if requested.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        css_string = f.read()
    
    css_dict = css_to_dict(css_string)
    
    if as_json_string:
        return json.dumps(css_dict, indent=4)
    return css_dict

if __name__ == "__main__":
    # Example usage:
    # print(parse_css_file("style.css", as_json_string=True))
    pass
