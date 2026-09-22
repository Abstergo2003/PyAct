import re
import json

def css_to_dict(css_string: str) -> dict:
    """Parses a CSS string into a Python dictionary."""
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
    Reads a CSS file and converts it to a dictionary map. 
    If as_json_string is True, returns a formatted JSON string instead.
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
