<div align="center">
  <h1>⚡ PyAct CLI</h1>
  <p><b>The engine behind dynamic Markdown.</b></p>
</div>

The **PyAct CLI** allows you to compile `.pamd` files into standard Markdown (`.md`). It evaluates your Python logic, injects your variables, and builds complex markdown elements effortlessly.

## 🚀 Installation

Install it directly from PyPI:
```bash
pip install pyact-cli
```

## 📖 How it works

A `.pamd` file is split into a **Python cell** and a **Markdown cell**. 

### 1. Write your Python logic
Define a `context()` function that returns the variables you want to inject. You can even use the built-in `pamd_helpers` to do heavy lifting!

```python
import pamd_helpers

def context():
    # Automatically converts the lambda to LaTeX!
    equation = pamd_helpers.equation(lambda x: x**2, [5])
    
    return {
        "title": "My PyAct Document",
        "math": equation
    }
```

### 2. Write your Markdown
Use `<ctx>` tags to inject your Python variables anywhere in your text.

```markdown
# <ctx>title</ctx>

Here is my dynamically generated equation:
<ctx>math</ctx>

You can also include other pamd files as templates!
<tmp>path/to/another_file</tmp>
```

### 3. Use Global Variables `<glb>`
If you have data you want to access everywhere across multiple nested files (like an author name or project ID), simply create a `global.py` file in your root folder:

```python
def global_context():
    return {"author": "Jane Doe"}
```
You can then inject this data into any Markdown cell using the `<glb>` tag!
```markdown
Written by <glb>author</glb>
```

### 4. Compile to Markdown
Run the compiler from your terminal to generate your final Markdown document:
```bash
pyact path/to/your_file.pamd -o output.md
```

### 5. Compile to Word (DOCX)
You can also compile straight to a native Microsoft Word Document, complete with CSS styling! 
```bash
pyact path/to/your_file.pamd -o output.md --docx output.docx
```
*Note: If you have a `style.css` file in the same directory, PyAct will automatically load it to style your Word Document. You can also specify one manually using the `--css path/to/style.css` flag!*

### 6. Configure Word Export via `pamd.conf`
Control document metadata, running headers, and footers with a `pamd.conf` file:

```ini
[Header]
left = My Project
right = 2026

[Footer]
left = Confidential
center = Page {page} of {pages}

[Metadata]
author = Jane Doe
title = Monthly Report
```

PyAct will automatically detect `pamd.conf` in your directory, inject dynamic page numbers (`{page}` / `{pages}`), configure tab stops, and populate document metadata!

### 7. Scaffolding New Projects with `pyact init`
Quickly spin up a new project ready to compile:
```bash
pyact init my_project --template engineering
```
Templates: `default`, `engineering`, `academic`.

That's it! You now have documents ready to be shared, published, or distributed.
