import inspect
from pyact.py2tex import py2tex

def equation(func: function, values: list) -> str:
    source = inspect.getsource(func)
    value = func(*values)
    name, sep, tail = source.rpartition("=")
    head, sep, equ = tail.rpartition(":")
    return f"$$ {name} = {py2tex(equ.replace("\n", ""))} = {value} $$"


def image(link: str, caption: str) -> str:
    image_link = f"![{caption}]({link})"
    caption = f"<span style='text-align: center; display: block; font-style: italic;'>{caption}</span>"
    return f"{image_link} \n {caption}"

def table(headers: list, values: list, caption: str, add_no: bool = False, starting_number: int = 1) -> str:
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

    caption = f"<span style='text-align: center; display: block; font-style: italic;'>{caption}</span>"
    return f"{caption} \n {headers_string}\n{breaker_line}\n{table_content}"


def hyperlink(caption: str, link: str) -> str:
    return f"[{caption}]({link})"

def unordered_list(items: list) -> str:
    list_string = ""
    for i in items:
        list_string += f"* {i}\n"
    return list_string

def ordered_list(items: list) -> str:
    list_string = ""
    for i, item in enumerate(items):
        list_string += f"{i+1}. {item}\n"
    return list_string

def checklist(items: list) -> str:
    list_string = ""
    for i in items:
        list_string += f"- [ ] {i}\n"
    return list_string

class Footnote:
    def __init__(self, number, text):
        self.number = number
        self.text = text

    def define_string(self) -> str:
        return f"[^{self.number}]: {self.text}"

    def adnotation(self) -> str:
        return f"[^{self.number}]\n"