import inspect
import ast
import textwrap
from typing import Callable, List, Any
from enum import Enum
from pyact.py2tex import py2tex


def _extract_lambda_parts(func: Callable) -> tuple[str, list[str], str]:
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    lambda_node = next(
        (node for node in ast.walk(tree) if isinstance(node, ast.Lambda)),
        None,
    )
    if lambda_node is None:
        raise ValueError("Expected a lambda function.")

    expression = ast.get_source_segment(source, lambda_node.body)
    if expression is None:
        raise ValueError("Could not read the lambda expression.")

    name = getattr(func, "__name__", "calculation")
    assignment = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) for target in node.targets)
            and lambda_node in ast.walk(node.value)
        ),
        None,
    )
    if assignment is not None:
        name = next(
            target.id
            for target in assignment.targets
            if isinstance(target, ast.Name)
        )

    variables = [argument.arg for argument in lambda_node.args.args]
    return name, variables, expression

def equation(func: Callable, values: List[Any]) -> str:
    """
    Converts a Python lambda or simple function into a LaTeX math equation string.
    
    Why it is needed:
    To allow users to define equations in Python syntax and automatically render them 
    as mathematical formulas in the final document, without needing to hand-write LaTeX.
    
    Inputs:
        func (Callable): A simple Python function (e.g., `lambda x: x**2`).
        values (List[Any]): The arguments to pass to the function to compute the result.
        
    Outputs:
        str: A Markdown math string formatted as `$$ Name = Equation = Value $$`.
    """
    print("Function 'equation()' is deprecated and will be removed, please use Calculation() class.")
    value = func(*values)
    name, _, equ = _extract_lambda_parts(func)
    
    name = name.strip()
    if "_" in name:
        parts = name.split("_", 1)
        name = f"{parts[0]}_{{{parts[1]}}}"
        
    import re
    greek_pattern = r'(?<![a-zA-Z])(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Alpha|Beta|Gamma|Delta|Epsilon|Zeta|Eta|Theta|Iota|Kappa|Lambda|Mu|Nu|Xi|Omicron|Pi|Rho|Sigma|Tau|Upsilon|Phi|Chi|Psi|Omega)(?![a-zA-Z])'
    name = re.sub(greek_pattern, r'\\\1', name)
    
    return f"$$ {name} = {py2tex(equ.replace(chr(10), ''))} = {value} $$"

def image(link: str, caption: str) -> str:
    """
    Generates a Markdown image string with an embedded HTML caption.
    
    Why it is needed:
    Standard Markdown images `![caption](url)` don't display visible captions below the image.
    This helper injects a styled HTML `<span>` below the image to force a visual caption.
    
    Inputs:
        link (str): The URL or local path to the image.
        caption (str): The text to display as the caption.
        
    Outputs:
        str: A formatted string containing the Markdown image and HTML span caption.
    """
    image_link = f"![{caption}]({link})"
    caption_html = f"<span style='text-align: center; display: block; font-style: italic;'>{caption}</span>"
    return f"{image_link} \n {caption_html}"

def plot(fig_or_plt: Any, caption: str = "", filename: str = None, dpi: int = 300, output_dir: str = "images") -> str:
    """
    Saves a Matplotlib/Seaborn figure or pyplot module to an image file and returns a styled Markdown image string.
    
    Why it is needed:
    Allows data analysts and engineers to generate plots directly in Python code cells and 
    seamlessly embed them into both Markdown and Word (DOCX) documents without manual file saving.
    
    Inputs:
        fig_or_plt: A matplotlib Figure object or the matplotlib.pyplot module.
        caption (str): Caption text to display below the plot.
        filename (str): Optional file name (e.g. 'beam_deflection.png'). If omitted, a name is automatically generated.
        dpi (int): Resolution of the exported image (default 300 dpi for sharp printing).
        output_dir (str): Directory where the image should be saved (default 'images').
        
    Outputs:
        str: A Markdown image tag with an italicized caption span, ready for injection into the document.
    """
    import os
    import time
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    if not filename:
        if caption:
            import re
            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', caption.strip().lower())[:30].strip('_')
            filename = f"{clean_name}.png" if clean_name else f"plot_{int(time.time()*1000)}.png"
        else:
            filename = f"plot_{int(time.time()*1000)}.png"
            
    if not filename.endswith(('.png', '.jpg', '.jpeg', '.svg')):
        filename += '.png'
        
    filepath = os.path.join(output_dir, filename)
    norm_path = filepath.replace('\\', '/')
    
    if hasattr(fig_or_plt, 'savefig'):
        fig_or_plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    elif hasattr(fig_or_plt, 'figure') and hasattr(fig_or_plt.figure, 'savefig'):
        fig_or_plt.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
    elif hasattr(fig_or_plt, 'save'):
        fig_or_plt.save(filepath)
    else:
        raise TypeError(f"Expected a matplotlib Figure or image object with a 'savefig' or 'save' method, got {type(fig_or_plt)}")
        
    return image(norm_path, caption)

def callout(text: str, callout_type: str = "note", title: str = None) -> str:
    """
    Generates a GitHub-flavored Markdown alert/callout box.
    
    Inputs:
        text (str): The body text of the alert.
        callout_type (str): 'note', 'tip', 'important', 'warning', or 'caution'.
        title (str): Optional title overriding the default alert header.
        
    Outputs:
        str: A blockquote formatted alert.
    """
    c_type = callout_type.upper()
    lines = text.strip().split('\n')
    header = f"> [!{c_type}]"
    if title:
        header += f" {title}"
    body = "\n".join(f"> {line}" for line in lines)
    return f"{header}\n{body}\n"

def table(headers: List[str], values: List[List[Any]], caption: str, add_no: bool = False, starting_number: int = 1) -> str:
    """
    Generates a Markdown table from Python lists, including a caption.
    
    Why it is needed:
    Writing Markdown tables by hand is tedious. This function allows users to programmatically 
    build tables from 2D data arrays, inject automatic numbering, and append a styled caption.
    
    Inputs:
        headers (List[str]): List of column header names.
        values (List[List[Any]]): A 2D list containing the row data.
        caption (str): The text to display above the table.
        add_no (bool): If True, adds an auto-incrementing "No." column to the left.
        starting_number (int): The starting index for the "No." column.
        
    Outputs:
        str: A formatted Markdown string containing the caption and the table.
    """
    print("Function 'table()' is deprecated and will be removed, please use Table() class.")
    if add_no:
        headers_string = f"|No.|"
        breaker_line = "|---|"
    else:
        headers_string = f"|"
        breaker_line = "|"

    for i in headers:
        headers_string += f"{i}|"
        breaker_line += "-"*len(i)+"|"

    table_content = ""
    for i, row in enumerate(values):
        if add_no:
            table_content += f"|{i+starting_number}|"
        else:
            table_content += "|"
        for value in row:
            table_content += f"{value}|"
        table_content += "\n"

    caption_html = f"<span style='text-align: center; display: block; font-style: italic;'>{caption}</span>"
    return f"{caption_html} \n {headers_string}\n{breaker_line}\n{table_content}"

def hyperlink(caption: str, link: str) -> str:
    """
    Generates a simple Markdown hyperlink.
    
    Why it is needed:
    Provides a standardized helper method in the PyAct ecosystem for injecting links.
    
    Inputs:
        caption (str): The clickable text to display.
        link (str): The URL destination.
        
    Outputs:
        str: The Markdown hyperlink string `[caption](link)`.
    """
    return f"[{caption}]({link})"

def unordered_list(items: List[str]) -> str:
    """
    Generates a Markdown unordered (bullet) list from a Python list.
    
    Why it is needed:
    Allows programmatic generation of bullet points from array data.
    
    Inputs:
        items (List[str]): A list of string items.
        
    Outputs:
        str: A Markdown string where each item is prefixed with `* `.
    """
    print("Function 'unordered_list()' is deprecated and will be removed, please use CList() class.")
    list_string = ""
    for i in items:
        list_string += f"* {i}\n"
    return list_string

def ordered_list(items: List[str]) -> str:
    """
    Generates a Markdown ordered (numbered) list from a Python list.
    
    Why it is needed:
    Allows programmatic generation of numbered lists from array data.
    
    Inputs:
        items (List[str]): A list of string items.
        
    Outputs:
        str: A Markdown string where each item is numbered sequentially (1. 2. 3.).
    """
    print("Function 'ordered_list()' is deprecated and will be removed, please use CList() class.")
    list_string = ""
    for i, item in enumerate(items):
        list_string += f"{i+1}. {item}\n"
    return list_string

def checklist(items: List[str]) -> str:
    """
    Generates a Markdown task checklist from a Python list.
    
    Why it is needed:
    Allows programmatic generation of checkable task items.
    
    Inputs:
        items (List[str]): A list of string items.
        
    Outputs:
        str: A Markdown string where each item is prefixed with `- [ ] `.
    """
    print("Function 'checklist()' is deprecated and will be removed, please use CList() class.")
    list_string = ""
    for i in items:
        list_string += f"- [ ] {i}\n"
    return list_string

class Footnote:
    """
    A helper class for managing Markdown footnotes.
    
    Why it is needed:
    Footnotes require two separate parts in Markdown: the annotation mark in the text `[^1]`, 
    and the definition at the bottom of the document `[^1]: The text`. This class links 
    the two together to prevent numbering mismatches.
    """
    def __init__(self, number: int, text: str):
        """
        Inputs:
            number (int): The footnote reference number.
            text (str): The expanded text definition of the footnote.
        """
        self.number = number
        self.text = text

    def __repr__(self) -> str:
        return self.define_string()

    def define_string(self) -> str:
        """
        Outputs (str): The full footnote definition block to place at the bottom of the document.
        """
        return f"[^{self.number}]: {self.text}"

    def adnotation(self) -> str:
        """
        Outputs (str): The short inline reference marker to place in the paragraph text.
        """
        return f"[^{self.number}]\n"

def table_to_dxf(headers: List[str], values: List[List[Any]], filename: str, cell_width: float = 50.0, cell_height: float = 10.0) -> str:
    """
    Exports a table (headers + values) to a 2D CAD DXF file.
    
    Why it is needed:
    Engineers and designers often need to embed tabulated data (e.g. Bill of Materials, 
    coordinate tables, parts lists) directly into AutoCAD drawings. This helper converts 
    a Python table directly into DXF geometry (lines and text) that can be opened in any CAD software.
    
    Inputs:
        headers (List[str]): List of column header names.
        values (List[List[Any]]): A 2D list containing the row data.
        filename (str): The output filename (e.g., 'table.dxf').
        cell_width (float): The width of each cell in drawing units.
        cell_height (float): The height of each cell in drawing units.
        
    Outputs:
        str: A string confirming the export, formatted as a Markdown link.
    """
    print("Function 'table_to_dfx()' is deprecated and will be removed, please use Table() class.")
    try:
        import ezdxf
    except ImportError:
        return f"*(Error: ezdxf library is not installed. Cannot generate {filename})*"
        
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Construct full grid data
    rows = [headers] + values
    num_rows = len(rows)
    num_cols = len(headers)
    
    # Draw horizontal grid lines
    for i in range(num_rows + 1):
        y = -i * cell_height
        msp.add_line((0, y), (num_cols * cell_width, y))
        
    # Draw vertical grid lines
    for j in range(num_cols + 1):
        x = j * cell_width
        msp.add_line((x, 0), (x, -num_rows * cell_height))
        
    # Draw text centered in each cell
    for i, row in enumerate(rows):
        y = -i * cell_height - (cell_height / 2)
        for j, cell_val in enumerate(row):
            if j >= num_cols: continue # Safety bounds
            x = j * cell_width + (cell_width / 2)
            msp.add_text(
                str(cell_val),
                dxfattribs={
                    'height': cell_height * 0.4,
                }
            ).set_placement((x, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
            
    doc.saveas(filename)
    return f"*[Successfully exported table to {filename}]({filename})*"

class Calculation:
    def __init__(self, func: Callable, values: List[float|int], repl: bool = False, precision: int = 3):
        self.func = func
        self.values = values
        self.replace = repl
        self.precision = precision
        self.value = round(func(*values), self.precision)
        self.name = None
        self.vars = None
        self.repr = self.get_representation()

    def __repr__(self):
        return self.repr

    def recalculate(self, values, precision: int = None):
        if precision is None:
            return Calculation(self.func, values, self.replace, self.precision)
        else:
            return Calculation(self.func, values, self.replace, precision)

    def get_representation(self):
        name, self.vars, equ = _extract_lambda_parts(self.func)
        
        name = name.strip()
        self.name = f"$ {py2tex(name)} $"
        if "_" in name:
            parts = name.split("_", 1)
            name = f"{parts[0]}_{{{parts[1]}}}"
            
        import re
        greek_pattern = r'(?<![a-zA-Z])(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Alpha|Beta|Gamma|Delta|Epsilon|Zeta|Eta|Theta|Iota|Kappa|Lambda|Mu|Nu|Xi|Omicron|Pi|Rho|Sigma|Tau|Upsilon|Phi|Chi|Psi|Omega)(?![a-zA-Z])'
        name = re.sub(greek_pattern, r'\\\1', name)
        texified = py2tex(equ.replace(chr(10), ''))
        replaced = texified
        for i, vr in enumerate(self.vars):
            replaced = replaced.replace(py2tex(vr.replace(",", "")), f"{self.values[i]}")

        if self.replace:
            return f"$$ {name} = {texified} = {replaced} = {self.value} $$"
        else:
            return f"$$ {name} = {texified} = {self.value} $$"

    def _extract(self, other) -> float:
        return float(other.value) if isinstance(other, Calculation) else float(other)

    def __add__(self, other):
        return float(self.value) + self._extract(other)

    def __radd__(self, other):
        return self._extract(other) + float(self.value)

    def __sub__(self, other):
        return float(self.value) - self._extract(other)

    def __rsub__(self, other):
        return self._extract(other) - float(self.value)

    def __mul__(self, other):
        return float(self.value) * self._extract(other)

    def __rmul__(self, other):
        return self._extract(other) * float(self.value)

    def __truediv__(self, other):
        return float(self.value) / self._extract(other)

    def __rtruediv__(self, other):
        return self._extract(other) / float(self.value)

    def __pow__(self, power):
        return float(self.value) ** self._extract(power)

    def __neg__(self):
        return -float(self.value)
        
    def __abs__(self):
        return abs(float(self.value))

class Table():
    def __init__(self, headers: List[str], values: List[List[Any]], caption: str, add_no: bool = False, starting_number: int = 1):
        self.headers = headers
        self.values = values
        self.caption = caption
        self.add_no = add_no
        self.starting_number = starting_number
        self.repr = self.get_representation()

    def __repr__(self):
        return self.repr

    def get_representation(self):
        if self.add_no:
            headers_string = f"|No.|"
            breaker_line = "|---|"
        else:
            headers_string = f"|"
            breaker_line = "|"
    
        for i in self.headers:
            headers_string += f"{i}|"
            breaker_line += "-"*len(i)+"|"
    
        table_content = ""
        for i, row in enumerate(self.values):
            if self.add_no:
                table_content += f"|{i+self.starting_number}|"
            else:
                table_content += "|"
            for value in row:
                table_content += f"{value}|"
            table_content += "\n"
    
        caption_html = f"<span style='text-align: center; display: block; font-style: italic;'>{self.caption}</span>"
        return f"{caption_html} \n {headers_string}\n{breaker_line}\n{table_content}"

    def toDXF(self, filename: str, cell_width: float = 50.0, cell_height: float = 10.0):
        try:
            import ezdxf
        except ImportError:
            return f"*(Error: ezdxf library is not installed. Cannot generate {filename})*"
            
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Construct full grid data
        rows = [self.headers] + self.values
        num_rows = len(rows)
        num_cols = len(self.headers)
        
        # Draw horizontal grid lines
        for i in range(num_rows + 1):
            y = -i * cell_height
            msp.add_line((0, y), (num_cols * cell_width, y))
            
        # Draw vertical grid lines
        for j in range(num_cols + 1):
            x = j * cell_width
            msp.add_line((x, 0), (x, -num_rows * cell_height))
            
        # Draw text centered in each cell
        for i, row in enumerate(rows):
            y = -i * cell_height - (cell_height / 2)
            for j, cell_val in enumerate(row):
                if j >= num_cols: continue # Safety bounds
                x = j * cell_width + (cell_width / 2)
                msp.add_text(
                    str(cell_val),
                    dxfattribs={
                        'height': cell_height * 0.4,
                    }
                ).set_placement((x, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
                
        doc.saveas(filename)
        return f"*[Successfully exported table to {filename}]({filename})*"

class ListType(Enum):
    ORDERED = 1
    UNORDERED = 2
    CHECKLIST = 3

class CList():
    def __init__(self, items: List[Any], type: ListType):
        self.items = items
        self.type = type
        self.repr = self.get_representation()

    def __repr__(self):
        return self.repr

    def get_representation(self):
        if self.type == ListType.ORDERED:
            return self.get_ordered()
        elif self.type == ListType.UNORDERED:
            return self.get_unordered()
        elif self.type == ListType.CHECKLIST:
            return self.get_checklist()

    def get_ordered(self):
        list_string = ""
        for i, item in enumerate(self.items):
            list_string += f"{i+1}. {item}\n"
        return list_string
    def get_unordered(self):
        list_string = ""
        for i in self.items:
            list_string += f"* {i}\n"
        return list_string
    def get_checklist(self):
        list_string = ""
        for i in self.items:
            list_string += f"- [ ] {i}\n"
        return list_string

# feat:: footnote list
# class FootnoteList():
#     def __init__(self, footnotes: List[Footnote]):
#         self.footnotes = footnotes
#         self.repr = self.get_adnotations()

#     def __repr__(self):
#         return self.repr
    
#     def append(self, footnote: Footnote|List[Footnote]):
#         if isinstance(footnote, List):
#             self.footnotes = self.footnotes + footnote
#         else:
#             self.footnotes = self.footnotes.append(footnote)
#     def get_adnotations(self):
#         adnots = ""
#         for fn in self.footnotes:
#             adnots = adnots + f"{fn.adnotation}\n"

if __name__ == "__main__":
    # func_w = lambda x_1, y, z: x_1+y+z
    # func_eq = Calculation(func_w, [1,2,3], True)
    # print(func_eq.vars)


    
    print(["lol4", "lol5"][-1])