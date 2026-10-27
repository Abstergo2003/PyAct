<div align="center">
  <h1>🚀 PyAct</h1>
  <p><b>Dynamic Markdown Generation powered by Python</b></p>
</div>

Welcome to **PyAct**! Have you ever wanted to write a Markdown document but needed to do complex math, generate tables on the fly, or automatically convert Python functions to LaTeX? 

PyAct solves this by introducing `.pamd` files — a powerful format that merges the simplicity of Markdown with the computational power of Python.

## 🌟 Why PyAct?
- **Code & Content Together**: Write your Python logic and your Markdown content side-by-side. 
- **Auto-LaTeX Generation**: Turn standard Python lambda functions directly into LaTeX math equations!
- **Native Word Documents (DOCX)**: Compile your Markdown straight into fully formatted Microsoft Word Documents, complete with native tables, footnotes, and math!
- **Custom CSS Styling**: Use standard CSS syntax (via `style.css`) to customize the fonts, colors, and layout of your exported Word Documents!
- **Component Templates**: Keep your documents clean by splitting them into smaller `<tmp>` templates.
- **Validated PAMD Format**: Use one Markdown cell and as many Python cells as needed for modular logic.
- **Jupyter-like Experience**: A custom Monaco-based VS Code editor makes writing `.pamd` feel like a focused Jupyter-style document editor without native notebook controls.

## 📦 The Ecosystem

PyAct is built for users, with two easy-to-use tools:

### 1. The PyAct Compiler (CLI)
Available on PyPI, the CLI is the brain of PyAct. It compiles your `.pamd` files into standard, clean `.md` files that you can publish anywhere.
👉 [Check out the CLI](./pyact_cli/)

### 2. Install the VS Code Extension
For the ultimate Jupyter-like writing experience, install the official PAMD extension directly from the VS Code Marketplace!
1. Open VS Code
2. Search for **PAMD** in the Extensions tab
3. Click Install and enjoy cell-based editing, Monaco syntax highlighting, completions, automatic context tags, and toolbar actions that compile and preview your document.
👉 [Check out the Extension](./pamd-file-support/)

The extension's editor behavior and syntax color remapping are documented in
[PAMD VS Code Editor](./wiki/PAMD-VS-Code-Editor.md).

### 3. Technical Sheet (For AI Assistants & Developers)
Developing features, building integrations, or working with an AI assistant on the codebase? Read the single source of truth detailing the architecture, compilation AST, OOXML engine, and invariants:  
👉 [Check out the Tech Sheet](./TECH_SHEET.md)

---
Get started today by checking out the individual folders above to supercharge your Markdown workflow!
