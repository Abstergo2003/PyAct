# The `.pamd` Format

A `.pamd` file operates identically to a Jupyter Notebook (`.ipynb`). Under the hood, it is a JSON file containing a list of `cells`. PyAct strictly processes exactly one `code` cell and exactly one `markdown` cell per file.

## 1. The Context System `<ctx>`

The core philosophy of PyAct is separation of logic and presentation.

### The `context()` function
Your Python code cell **must** contain a function named `context()` that returns a `dict`. When PyAct compiles your file, it safely executes the code cell in memory and calls `context()`.

```python
import math

def context():
    return {
        "pi": math.pi,
        "author": "John Doe"
    }
```

### The `<ctx>` injection tag
In the Markdown cell, any text wrapped in `<ctx>...</ctx>` will be dynamically replaced by the string representation of the matching key from the `context()` dictionary.

```markdown
Written by: <ctx>author</ctx>
The value of Pi is <ctx>pi</ctx>.
```

## 2. Component Templates `<tmp>`

For large projects (like a book or an extensive report), putting everything into a single `.pamd` file gets messy. PyAct supports nesting!

You can create smaller "child" `.pamd` files (like `chapter1.pamd`, `header.pamd`), and inject them into a parent document using the `<tmp>` tag.

### Example

**`chapter1.pamd` (Markdown cell):**
```markdown
This is the first chapter of the book.
```

**`main.pamd` (Markdown cell):**
```markdown
# My Book

<tmp>chapter1</tmp>
```

When you compile `main.pamd`, PyAct recursively parses the AST (Abstract Syntax Tree), resolves all child templates relative to the parent's directory, compiles their individual `context()` dictionaries, and merges them into one flat, cohesive output document!
