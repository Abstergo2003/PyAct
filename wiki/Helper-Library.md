# The Helper Library

PyAct ships with a built-in library called `pamd_helpers`. You can import it directly into your `.pamd` Python cell to programmatically generate complex Markdown structures!

```python
import pamd_helpers

def context():
    return { ... }
```

## 1. LaTeX Equations
Generates a Markdown math string (`$$ Equation = Value $$`) by automatically translating a Python lambda function into LaTeX!

```python
# Code Cell
eq = pamd_helpers.equation(lambda x, y: x**2 + y, [5, 2])
# Returns: "$$ x^{2} + y = 27 $$"
```

## 2. Dynamic Tables
Generating Markdown tables by hand is tedious. The `table` helper takes a 2D Python array and formats it instantly, along with a caption and optional auto-numbering.

```python
# Code Cell
headers = ["Name", "Age"]
data = [
    ["Alice", 25],
    ["Bob", 30]
]
my_table = pamd_helpers.table(headers, data, caption="User Data", add_no=True)
```

## 3. Images with Captions
Standard Markdown `![caption](url)` doesn't render the caption as text below the image. The `image` helper injects an HTML span below the image to force a styled, italicized caption.

```python
my_image = pamd_helpers.image("https://example.com/img.png", "A beautiful view")
```

## 4. Footnotes
Footnotes in Markdown require an inline annotation (`[^1]`) and a bottom-of-page definition (`[^1]: Text`). The `Footnote` class keeps these linked.

```python
fn1 = pamd_helpers.Footnote(1, "This is the source.")

def context():
    return {
        "fn1_mark": fn1.adnotation(),
        "fn1_def": fn1.define_string()
    }
```

In your Markdown:
```markdown
Here is a claim.<ctx>fn1_mark</ctx>

<ctx>fn1_def</ctx>
```

## 5. Lists
Generate perfectly formatted bulleted, numbered, or task lists from Python arrays.

```python
bullets = pamd_helpers.unordered_list(["Apples", "Bananas"])
numbers = pamd_helpers.ordered_list(["First", "Second"])
tasks = pamd_helpers.checklist(["Write tests", "Refactor"])
```
