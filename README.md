# 📝 PyAct Builder

**PyAct Builder** is a lightweight yet powerful Markdown template engine that allows you to dynamically generate documents using Python scripts.

Thanks to recursive processing, you can build complex documents from small, independent blocks ("nodes"), inject data (dates, API results, calculations), and automate the creation of reports or static pages.

## 🚀 Key Features

  * **Python Integration:** Each text fragment can have a corresponding `.py` script that supplies data.
  * **Recursion:** Nest templates within templates without limits (e.g., `Main -> Section -> Component`).
  * **Simple Syntax:** Use `{[component]}` to insert blocks and `{{variable}}` to insert data.
  * **CLI Tool:** A built-in command-line tool for quick setup and building.

## 📦 Installation

Install the package directly from PyPI:

```bash
pip install pyact
```


## ⚡ Quick Start

1.  **Initialize a new project:**
    The tool automatically generates the directory structure and example files.

    ```bash
    pyact make
    ```

2.  **Build the document:**
    Processes `main.md` and saves the result in the `output/` folder.

    ```bash
    pyact run
    ```

## 📂 Project Structure

After running the `make` command, your project will look like this:

```text
.
├── main.md           # Main input file
├── output/           # Destination for the final file (output.md)
└── nodes/            # Folder containing your components
    ├── header.md     # Component template
    └── header.py     # Component logic (optional)
```

## 📖 How It Works

The system relies on two types of tags:

### 1\. Component Tags: `{[name]}`

These insert content from the `nodes/name.md` file. If a corresponding `nodes/name.py` file exists, it will be executed first to provide data to the template.

**Example in `main.md`:**

```markdown
# Daily Report
Below are the sales figures.

{[sales_table]}
```

### 2\. Variable Tags: `{{key}}`

Inside `.md` files located in the `nodes/` folder, you can use variables that will be replaced by the Python script.

**Example in `nodes/sales_table.py`:**

```python
def sales_table():
    # Return a dictionary (dict) with data
    return {
        "date": "2023-10-27",
        "total": 1500
    }
```

**Example in `nodes/sales_table.md`:**

```markdown
### Sales for {{date}}
Total revenue was: **{{total}} USD**.
```

### Final Result (`output.md`):

```markdown
# Daily Report
Below are the sales figures.

### Sales for 2023-10-27
Total revenue was: **1500 USD**.
```

## 🛠️ Advanced

### Returning JSON

If your Python script is complex, instead of a dictionary (`dict`), it can return a **JSON formatted string**. The engine will parse it automatically.

### Error Handling

If you forget to create an `.md` file or if a `.py` script returns an error, the `builder` will notify you in the console. In the final output file, it will simply skip the faulty fragment instead of breaking the entire document.