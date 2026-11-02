import os
from .core import (
    find_globals,
    find_imports,
    find_templates,
    get_globals,
    get_imports,
    map_content,
    read_pamd_cells,
)

def run_linter(main_filename: str, directory: str):
    """
    Runs the linter on a PyAct project.
    
    Checks for unused and missing context values, globals, and templates.
    """
    print(f"--- PyAct Linter ---")
    print(f"Analyzing project starting from: {main_filename}.pamd\n")
    
    try:
        build_tree = map_content(main_filename, directory)
    except Exception as e:
        print(f"[ERROR] Could not map {main_filename}.pamd: {e}")
        return False
        
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
    has_errors = False
    if unused_files:
        print("[WARNING] Unused .pamd files found in project directory:")
        for uf in unused_files:
            print(f"   - {os.path.relpath(uf, directory)}")
    else:
        print("[OK] No unused .pamd files found.")
        
    try:
        global_values = get_globals(directory)
    except Exception as error:
        print(f"[ERROR] {error}")
        global_values = {}
        has_errors = True

    requested_global_keys = set()
    for used_file in used_files:
        try:
            _, markdown = read_pamd_cells(used_file)
            requested_global_keys.update(find_globals(markdown))
        except Exception:
            continue

    print("\n--- Context and Global Check ---")
    
    # Check context in each used file
    for used_file in used_files:
        rel_path = os.path.relpath(used_file, directory)
        try:
            code_text, md_text = read_pamd_cells(used_file)
        except Exception as error:
            print(f"\n[ERROR] {rel_path}: {error}")
            has_errors = True
            continue
            
        try:
            # Need to pass base name for error reporting in core.py
            base_name = os.path.splitext(os.path.basename(used_file))[0]
            context_dict = get_imports(base_name, code_text)
            exported_keys = set(context_dict.keys())
        except Exception as error:
            print(f"\n[ERROR] {rel_path}: {error}")
            exported_keys = set()
            has_errors = True
            
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
                has_errors = True
                print(f"  [ERROR] Missing context exports (used in markdown, missing in python):")
                for k in missing_exports:
                    print(f"     - {k}")

    unused_globals = set(global_values.keys()) - requested_global_keys
    missing_globals = requested_global_keys - set(global_values.keys())
    if unused_globals or missing_globals:
        print("\n--- Global Check ---")
        if unused_globals:
            print("[WARNING] Unused global exports:")
            for key in sorted(unused_globals):
                print(f"   - {key}")
        if missing_globals:
            has_errors = True
            print("[ERROR] Missing global exports:")
            for key in sorted(missing_globals):
                print(f"   - {key}")

    print("\n--- Template Check ---")
    print("[OK] Template references resolved during project mapping.")

    print("\nLinting complete!")
    return not has_errors
