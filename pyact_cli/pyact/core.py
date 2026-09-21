import re
import json

def get_directory(path: str) -> list:
    # Splits path into: ('./main', '/', 'retro.pamd')
    head, sep, tail = path.rpartition('/')
    # Recombine the first part and the slash
    return [head + sep, tail]

def read_pamd_cells(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    code_content = ""
    markdown_content = ""
    
    for cell in data.get("cells", []):
        cell_type = cell.get("cell_type", "")
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
            
        if cell_type == "code":
            code_content += source + "\n"
        elif cell_type == "markdown":
            markdown_content += source + "\n"
            
    return code_content, markdown_content

def get_imports(file: str, code_text: str):
    file_namespace = {"__file__": f"{file}.pamd"}
    if not code_text.strip():
        raise ValueError(f"The file {file}.pamd needs a 'context()' function but has no code cell.")
        
    try:
        exec(code_text, file_namespace)
    except Exception as e:
        raise RuntimeError(f"Error executing code in {file}.pamd: {e}")

    if "context" not in file_namespace:
        raise ValueError(f"The file {file}.pamd is missing the required 'context()' function.")

    context_func = file_namespace["context"]

    if not callable(context_func):
        raise TypeError(f"In {file}.pamd, 'context' was found but it is not a function!")

    result_dict = context_func()

    if not isinstance(result_dict, dict):
        raise TypeError(f"The 'context()' function in {file}.pamd must return a dictionary.")

    return result_dict

def find_imports(text: str):
    # <ctx></ctx>
    pattern = r"<ctx>(.*?)</ctx>"
    return re.findall(pattern, text)


def find_templates(text: str):
    # <tmp></tmp>
    pattern = r"<tmp>(.*?)</tmp>"
    return re.findall(pattern, text)

def map_content(file: str, path: str):
    if path and not path.endswith('/'):
        full_path = f"{path}/{file}"
    elif path.endswith('/'):
        full_path = f"{path}{file}"
    else:
        full_path = file
        
    code_text, main_file = read_pamd_cells(f"{full_path}.pamd")
    templates = find_templates(main_file)
    imports = find_imports(main_file)
    meta = get_directory(full_path)
    
    ready_t = []
    for i in templates:
        ready_t.append(map_content(i, meta[0]))

    return {
        "tag_name": file,
        "name": meta[1],
        "path": meta[0],
        "imports": imports,
        "templates": ready_t
    }

def process_content(build_tree: dict):
    file_path_base = build_tree.get("path", "") + build_tree.get("name", "")
    code_text, file_text = read_pamd_cells(file_path_base + ".pamd")
    
    needed_imports = build_tree.get("imports", [])
    if needed_imports:
        imports = get_imports(file_path_base, code_text)
        for i in needed_imports:
            file_text = file_text.replace(f"<ctx>{i}</ctx>", str(imports.get(i, '')))

    for i in build_tree.get("templates", []):
        file_text = file_text.replace(f"<tmp>{i.get('tag_name')}</tmp>", process_content(i))
    return file_text