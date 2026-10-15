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

## 3. Global Variables `<glb>`

When building large projects with many nested templates, you often have variables (like the author's name, the project ID, or the company) that you need to access from *anywhere*, without having to pass them around through local `context()` functions.

### The `global.py` file
Create a standard Python file named `global.py` at the root of your project directory. Inside it, define a function named `global_context()` that returns your global variables dictionary.

```python
def global_context():
    return {
        "company": "Acme Corp",
        "author": "John Doe",
        "project_id": "PRJ-993"
    }
```

### The `<glb>` injection tag
In any Markdown cell, across any nested template, you can inject these global variables using the `<glb>` tag!

```markdown
Welcome to the report for <glb>project_id</glb> prepared by <glb>author</glb> at <glb>company</glb>.
```

*Note: PyAct's `pamd-cache` engine automatically watches your `global.py` file. If you change a global variable, the cache for your entire nested document tree is instantly invalidated and rebuilt!*

## 4. Native Table of Contents `<toc/>`

You can inject an interactive Table of Contents into your document by adding the `<toc/>` tag:

```markdown
# Comprehensive Engineering Report

<toc/>

<pagebreak/>

## 1. Introduction
...
```

When compiling to Markdown, PyAct automatically generates a hyperlinked Table of Contents linked to the document's headings. When exporting to Word (`--docx`), PyAct builds a native Microsoft Word TOC with pre-populated heading entries, dot leader tab stops, internal navigation bookmarks, dynamic `PAGEREF` fields, and `w:updateFields` enabled.

Custom titles are supported:
```markdown
<toc title="Document Contents"/>
```

## 5. Alerts & Callouts (`> [!IMPORTANT]`, `pamd_helpers.callout`)

PyAct supports GitHub-flavored Markdown alert callouts and blockquotes, rendering them into color-accented 1x1 callout boxes with shaded backgrounds in Word (`.docx`) and native blockquotes in Markdown:

```markdown
> [!NOTE] Implementation Note
> Default parameters will be used if omitted.

> [!IMPORTANT] Compliance Notice
> Must comply with Eurocode standards.

> [!WARNING] High Stress Area
> Exceeds standard allowable limits.
```

Supported alert types:
- `[!NOTE]` (Blue border and soft blue background)
- `[!TIP]` (Green border and soft green background)
- `[!IMPORTANT]` (Purple border and soft lavender background)
- `[!WARNING]` (Amber/Orange border and soft warm background)
- `[!CAUTION]` (Red border and soft pink background)
- Standard quotes `> Text` (Gray border and soft light gray background)

You can also generate callouts programmatically using [`pamd_helpers.callout()`](Helper-Library.md).

## 6. Page Breaks & Section Layouts (`<pagebreak/>`, `<landscape>`)

PyAct provides native tags to control pagination and page orientation in Word exports:

### Page Breaks
Insert `<pagebreak/>` (or `<pb/>`) anywhere to push subsequent content onto a new page:
```markdown
## Chapter 1
Content here...

<pagebreak/>

## Chapter 2
Starts on a clean page!
```

### Landscape Sections
Wrap wide tables or extensive charts in `<landscape>...</landscape>`:
```markdown
<landscape>
# Wide Beam Property Table
<ctx>wide_table</ctx>
</landscape>
```
PyAct automatically creates a dedicated horizontal section in Word, renders the content, and restores standard portrait orientation afterward!


