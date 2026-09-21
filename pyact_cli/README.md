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

### 3. Compile!
Run the compiler from your terminal to generate your final Markdown document:
```bash
pyact path/to/your_file.pamd -o output.md
```

That's it! You now have a standard Markdown file ready to be shared, published, or converted to PDF.
