import inspect
from typing import Callable, List, Any
from pyact.py2tex import py2tex

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
    source = inspect.getsource(func)
    value = func(*values)
    name, sep, tail = source.rpartition("=")
    head, sep, equ = tail.rpartition(":")
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