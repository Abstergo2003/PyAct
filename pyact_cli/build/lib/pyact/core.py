import re
import json

def get_directory(path: str) -> list:
    """
    Splits a full file path into its directory component and its filename component.
    
    Why it is needed:
    When resolving nested templates or generating output files, the engine needs to 
    know the base directory of the current `.pamd` file so it can correctly locate 
    sibling template files.
    
    Inputs:
        path (str): The full path to a file (e.g., './main/retro.pamd').
        
    Outputs:
        list: A two-element list `[directory_path, filename]`.
    """
    head, sep, tail = path.rpartition('/')
    return [head + sep, tail]

def read_pamd_cells(file_path: str):
    """
    Reads a .pamd (JSON Notebook) file and extracts the Markdown and Python code.
    
    Why it is needed:
    `.pamd` files are stored exactly like Jupyter Notebooks (a list of cell objects). 
    This function parses the JSON structure and concatenates all 'code' cells into a 
    single executable Python script, and all 'markdown' cells into a single Markdown document.
    
    Inputs:
        file_path (str): Path to the `.pamd` file to read.
        
    Outputs:
        tuple (str, str): A tuple containing `(code_content, markdown_content)`.
    """
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
    """
    Executes the Python code from a .pamd file and retrieves the context variables.
    
    Why it is needed:
    To inject dynamic data into the Markdown document, PyAct executes the user's Python 
    script. The user must define a `context()` function that returns a dictionary mapping 
    variable names (like 'title') to their computed values. This function safely executes 
    that code and extracts the resulting dictionary.
    
    Inputs:
        file (str): The name of the file being executed (for error reporting).
        code_text (str): The raw Python code extracted from the `.pamd` file.
        
    Outputs:
        dict: The dictionary of variables returned by the user's `context()` function.
    """
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
    """
    Finds all `<ctx>var_name</ctx>` tags in a markdown string.
    
    Why it is needed:
    Identifies which variables the Markdown document is requesting from the Python context.
    
    Inputs:
        text (str): The raw Markdown text.
        
    Outputs:
        list: A list of variable names extracted from the tags.
    """
    pattern = r"<ctx>(.*?)</ctx>"
    return re.findall(pattern, text)


def find_templates(text: str):
    """
    Finds all `<tmp>file_name</tmp>` tags in a markdown string.
    
    Why it is needed:
    Identifies nested `.pamd` template files that need to be recursively compiled 
    and injected into the current document.
    
    Inputs:
        text (str): The raw Markdown text.
        
    Outputs:
        list: A list of template file names extracted from the tags.
    """
    pattern = r"<tmp>(.*?)</tmp>"
    return re.findall(pattern, text)

def map_content(file: str, path: str):
    """
    Recursively maps the dependency tree of a `.pamd` file.
    
    Why it is needed:
    Before compiling, PyAct needs to build an Abstract Syntax Tree (AST) of the document, 
    mapping out all required context variables and any nested child templates that need 
    to be resolved. This allows for deep, nested project structures.
    
    Inputs:
        file (str): The target `.pamd` file name (without extension).
        path (str): The directory where the file is located.
        
    Outputs:
        dict: A recursive "build tree" dictionary containing metadata, required imports, 
              and the build trees of all nested templates.
    """
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
    """
    Compiles a mapped build tree into a final flat Markdown string.
    
    Why it is needed:
    This is the core renderer. It reads the `.pamd` files, executes their Python code 
    to fetch the context dictionary, replaces all `<ctx>` tags with dynamic data, 
    and recursively replaces all `<tmp>` tags with their fully compiled child documents.
    
    Inputs:
        build_tree (dict): The AST mapping generated by `map_content()`.
        
    Outputs:
        str: The final, fully compiled Markdown text string ready for export.
    """
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