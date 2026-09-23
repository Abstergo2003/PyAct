# Getting Started

## 1. Installation

The PyAct CLI is distributed via pip and works on any standard Python environment.

```bash
pip install pyact-cli
```

## 2. Your First Document

PyAct uses a custom file format called `.pamd`. A `.pamd` file is essentially a JSON notebook containing exactly two cells:
1. **A Markdown Cell** (where you write your text).
2. **A Python Cell** (where you define your dynamic variables).

*(Note: If you use the **PAMD File Support** extension for VS Code, creating a new `.pamd` file automatically generates this structure for you!)*

### The Python Cell
In the Python cell, you must define a `context()` function that returns a dictionary. These are the variables you want to inject into your Markdown.

```python
def context():
    greeting = "Hello, World!"
    calc = 10 * 25
    return {
        "msg": greeting,
        "math_result": calc
    }
```

### The Markdown Cell
In the Markdown cell, you use the `<ctx>` tag to call your variables.

```markdown
# My First PyAct Doc
The python script says: <ctx>msg</ctx>
And the calculation is: <ctx>math_result</ctx>
```

## 3. Compiling

Once you've saved your file (e.g., `document.pamd`), open your terminal and run:

```bash
pyact document.pamd -o document.md
```

PyAct will execute the Python code, extract the context variables, replace the `<ctx>` tags, and output a clean `document.md` file!
