import re
import json
import time
import linecache
from pathlib import Path
from typing import Any, Mapping

build_logs = []


def validate_pamd_document(data: Any, file_path: str | Path) -> list[dict]:
    """Validate the structural contract of a PAMD notebook document."""
    path = Path(file_path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid PAMD file {path}: the root must be a JSON object.")

    cells = data.get("cells")
    if not isinstance(cells, list):
        raise ValueError(f"Invalid PAMD file {path}: 'cells' must be a JSON array.")

    validated_cells = []
    markdown_count = 0
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            raise ValueError(
                f"Invalid PAMD file {path}: cell {index} must be a JSON object."
            )

        cell_type = cell.get("cell_type")
        if cell_type not in {"code", "markdown"}:
            raise ValueError(
                f"Invalid PAMD file {path}: cell {index} has unsupported "
                f"cell_type {cell_type!r}; expected 'code' or 'markdown'."
            )

        source = cell.get("source")
        if isinstance(source, str):
            normalized_source = source
        elif isinstance(source, list) and all(isinstance(line, str) for line in source):
            normalized_source = "".join(source)
        else:
            raise ValueError(
                f"Invalid PAMD file {path}: cell {index} 'source' must be "
                "a string or an array of strings."
            )

        if cell_type == "markdown":
            markdown_count += 1
        validated_cells.append(
            {"cell_type": cell_type, "source": normalized_source}
        )

    if markdown_count != 1:
        raise ValueError(
            f"Invalid PAMD file {path}: expected exactly one markdown cell, "
            f"found {markdown_count}."
        )

    return validated_cells


def get_directory(path: str | Path) -> list:
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
    path = Path(path)
    return [path.parent, path.name]

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
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid PAMD file {path}: malformed JSON at line "
            f"{error.lineno}, column {error.colno}: {error.msg}."
        ) from error
    except OSError as error:
        raise OSError(f"Could not read PAMD file {path}: {error}") from error

    cells = validate_pamd_document(data, path)
    
    code_content = ""
    markdown_content = ""
    
    for cell in cells:
        cell_type = cell["cell_type"]
        source = cell["source"]

        if cell_type == "code":
            code_content += source
            if source and not source.endswith("\n"):
                code_content += "\n"
        elif cell_type == "markdown":
            markdown_content += source
            if source and not source.endswith("\n"):
                markdown_content += "\n"
            
    return code_content, markdown_content

def get_imports(file: str | Path, code_text: str):
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
    filename = str(Path(file).with_suffix(".pamd"))
    file_namespace = {"__file__": filename}
    if not code_text.strip():
        raise ValueError(f"The file {filename} needs a 'context()' function but has no code cell.")
        
    try:
        # Mock linecache so inspect.getsource works on dynamically executed code
        linecache.cache[filename] = (
            len(code_text),
            None,
            [line + '\n' for line in code_text.splitlines()],
            filename
        )
        compiled_code = compile(code_text, filename, "exec")
        exec(compiled_code, file_namespace)
    except Exception as e:
        raise RuntimeError(f"Error executing code in {filename}: {e}")

    if "context" not in file_namespace:
        raise ValueError(f"The file {file}.pamd is missing the required 'context()' function.")

    context_func = file_namespace["context"]

    if not callable(context_func):
        raise TypeError(f"In {file}.pamd, 'context' was found but it is not a function!")

    result_dict = context_func()

    if not isinstance(result_dict, dict):
        raise TypeError(f"The 'context()' function in {file}.pamd must return a dictionary.")

    return result_dict

def get_globals(directory: str | Path):
    """
    Reads global.py and executes its global_context() function to get global variables.
    """
    global_path = Path(directory) / "global.py"
    if not global_path.exists():
        return {}
        
    with global_path.open("r", encoding="utf-8") as f:
        code_text = f.read()
        
    file_namespace = {"__file__": str(global_path)}
    try:
        compiled_code = compile(code_text, str(global_path), "exec")
        exec(compiled_code, file_namespace)
    except Exception as e:
        raise RuntimeError(f"Error executing global.py: {e}")
        
    if "global_context" in file_namespace:
        func = file_namespace["global_context"]
    else:
        raise ValueError("The global.py file must define a 'global_context()' function. (Note: 'global' is a reserved Python keyword!)")
        
    res = func()
    if not isinstance(res, dict):
        raise TypeError("'global_context()' in global.py must return a dictionary.")
        
    return res

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


def find_globals(text: str):
    """
    Finds all `<glb>var_name</glb>` tags in a markdown string.
    """
    pattern = r"<glb>(.*?)</glb>"
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

def _template_path(template: str | Path, directory: str | Path) -> Path:
    template_path = Path(template)
    if template_path.suffix != ".pamd":
        template_path = template_path.with_suffix(".pamd")
    if not template_path.is_absolute():
        template_path = Path(directory) / template_path
    return template_path


def map_content(
    file: str | Path,
    path: str | Path,
    _active_paths: tuple[Path, ...] = (),
):
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
    source_path = _template_path(file, path).resolve()
    if source_path in _active_paths:
        cycle_start = _active_paths.index(source_path)
        cycle = (*_active_paths[cycle_start:], source_path)
        cycle_display = " -> ".join(str(item) for item in cycle)
        raise ValueError(f"Recursive <tmp> template cycle detected: {cycle_display}")

    code_text, main_file = read_pamd_cells(str(source_path))
    templates = find_templates(main_file)
    imports = find_imports(main_file)
    globals_req = find_globals(main_file)
    meta = get_directory(source_path.with_suffix(""))
    
    ready_t = []
    for i in templates:
        ready_t.append(map_content(i, meta[0], (*_active_paths, source_path)))

    return {
        "tag_name": str(file),
        "name": str(meta[1]),
        "path": meta[0],
        "source_path": source_path,
        "imports": imports,
        "globals": globals_req,
        "templates": ready_t
    }

def _resolve_value(values: Mapping[str, Any], key: str) -> Any:
    current: Any = values
    for part in key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(key)
        current = current[part]
    return current


def process_content(build_tree: dict, globals_dict: dict = None):
    """
    Compiles a mapped build tree into a final flat Markdown string.
    """
    start_time = time.perf_counter()
    
    if globals_dict is None:
        globals_dict = get_globals(build_tree.get("path", ""))
        
    source_path = build_tree.get("source_path")
    if source_path is None:
        source_path = _template_path(
            build_tree.get("name", ""),
            build_tree.get("path", ""),
        )
    source_path = Path(source_path)
    code_text, file_text = read_pamd_cells(str(source_path))
    
    needed_imports = build_tree.get("imports", [])
    if needed_imports:
        imports = get_imports(source_path, code_text)
        for i in needed_imports:
            try:
                value = _resolve_value(imports, i)
            except KeyError:
                raise ValueError(
                    f"Context variable '{i}' requested in {source_path.name} "
                    "but not returned by context()."
                ) from None
            file_text = file_text.replace(f"<ctx>{i}</ctx>", str(value))
            
    needed_globals = build_tree.get("globals", [])
    for g in needed_globals:
        try:
            value = _resolve_value(globals_dict, g)
        except KeyError:
            raise ValueError(
                f"Global variable '{g}' requested via <glb> but not found "
                "in global.py's global_context()."
            ) from None
        file_text = file_text.replace(f"<glb>{g}</glb>", str(value))

    for i in build_tree.get("templates", []):
        file_text = file_text.replace(f"<tmp>{i.get('tag_name')}</tmp>", process_content(i, globals_dict))
        
    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    
    build_logs.append({
        "file": source_path.name,
        "time_ms": elapsed_ms
    })
        
    return file_text

def make_github_slug(heading: str) -> str:
    """Creates a GitHub-compatible anchor slug from heading text."""
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', heading)
    clean = re.sub(r'[*_`]', '', clean)
    clean = clean.lower().strip()
    clean = re.sub(r'[^\w\s-]', '', clean, flags=re.UNICODE)
    clean = re.sub(r'\s', '-', clean)
    return clean

def generate_markdown_toc(text: str) -> str:
    """
    Replaces `<toc/>`, `<toc>`, `[toc]`, or `<toc title="..."/>` with a GitHub-compatible
    Markdown Table of Contents.
    """
    toc_pattern = r'<(?:toc|TOC)(?:\s+title=["\'](.*?)["\'])?\s*/?>|\[toc\]|\[TOC\]'
    m = re.search(toc_pattern, text)
    if not m:
        return text
        
    toc_pos = m.start()
    title_override = m.group(1)
    
    # Scan headings after the TOC tag
    text_after = text[toc_pos:]
    lines = text_after.split('\n')
    
    in_code = False
    headings = []
    for line in lines:
        ls = line.strip()
        if ls.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        h_match = re.match(r'^(#{1,6})\s+(.*)$', ls)
        if h_match:
            level = len(h_match.group(1))
            h_text = h_match.group(2).strip()
            headings.append((level, h_text))
            
    if not headings:
        # Fallback to scanning whole document if no headings were found after TOC tag
        lines = text.split('\n')
        in_code = False
        for line in lines:
            ls = line.strip()
            if ls.startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                continue
            h_match = re.match(r'^(#{1,6})\s+(.*)$', ls)
            if h_match:
                level = len(h_match.group(1))
                h_text = h_match.group(2).strip()
                headings.append((level, h_text))
                
    if not headings:
        return re.sub(toc_pattern, '', text, count=1)
        
    base_level = min(h[0] for h in headings)
    toc_lines = []
    for level, h_text in headings:
        indent = "  " * (level - base_level)
        clean_title = re.sub(r'[*_`]', '', h_text).strip()
        slug = make_github_slug(h_text)
        toc_lines.append(f"{indent}- [{clean_title}](#{slug})")
        
    toc_header = ""
    if title_override:
        if title_override.lower() not in ('none', 'false', 'no'):
            toc_header = f"## {title_override}\n"
    else:
        toc_header = "## Table of Contents\n"
        
    full_toc = toc_header + "\n".join(toc_lines) + "\n"
    return re.sub(toc_pattern, lambda _: full_toc, text, count=1)