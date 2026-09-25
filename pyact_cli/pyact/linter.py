import os
from .core import read_pamd_cells, get_imports, find_imports, map_content

def run_linter(main_filename: str, directory: str):
    """
    Runs the linter on a PyAct project.
    
    Checks for:
    1. Unused .pamd files in the directory.
    2. Context keys exported but not used in the markdown.
    3. Context tags requested in the markdown but missing from the context dictionary.
    """
    print(f"--- PyAct Linter ---")
    print(f"Analyzing project starting from: {main_filename}.pamd\n")
    
    try:
        build_tree = map_content(main_filename, directory)
    except Exception as e:
        print(f"Error mapping project: {e}")
        return
        
    used_files = set()
    
    def collect_used_files(tree):
        file_path = os.path.join(tree['path'], tree['name'])
        used_files.add(os.path.abspath(file_path + ".pamd"))
        for child in tree.get("templates", []):
            collect_used_files(child)
            
    collect_used_files(build_tree)
    
    # Check for unused .pamd files in the base directory
    all_pamd_files = set()
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".pamd"):
                all_pamd_files.add(os.path.abspath(os.path.join(root, f)))
                
    unused_files = all_pamd_files - used_files
    if unused_files:
        print(f"[WARNING] Unused .pamd files found in project directory:")
        for uf in unused_files:
            print(f"   - {os.path.relpath(uf, directory)}")
    else:
        print("[OK] No unused .pamd files found.")
        
    print("\n--- Context Check ---")
    
    # Check context in each used file
    for used_file in used_files:
        rel_path = os.path.relpath(used_file, directory)
        try:
            code_text, md_text = read_pamd_cells(used_file)
        except Exception:
            continue
            
        try:
            # Need to pass base name for error reporting in core.py
            base_name = os.path.splitext(os.path.basename(used_file))[0]
            context_dict = get_imports(base_name, code_text)
            exported_keys = set(context_dict.keys())
        except Exception:
            # If a file has no code cell or no context(), it returns an empty dict effectively, 
            # or throws ValueError in get_imports. Let's just treat as empty if error.
            exported_keys = set()
            
        requested_keys = set(find_imports(md_text))
        
        unused_exports = exported_keys - requested_keys
        missing_exports = requested_keys - exported_keys
        
        if unused_exports or missing_exports:
            print(f"\nFile: {rel_path}")
            if unused_exports:
                print(f"  [WARNING] Unused context exports (defined in python, not used in markdown):")
                for k in unused_exports:
                    print(f"     - {k}")
            if missing_exports:
                print(f"  [ERROR] Missing context exports (used in markdown, missing in python):")
                for k in missing_exports:
                    print(f"     - {k}")
        else:
            pass

    print("\nLinting complete!")
