<div align="center">
  <h1>📝 PAMD File Support for VS Code</h1>
  <p><b>A native Jupyter-like experience for Markdown generation.</b></p>
</div>

Writing `.pamd` files is great, but writing them in **Visual Studio Code** is magical. This extension registers `.pamd` files as native Notebooks, giving you a powerful, seamless writing experience.

## ✨ Features

- **Notebook UI**: Opens `.pamd` files as notebooks with exactly one Markdown cell and as many Python code cells as you need.
- **One-Click Magic**: Hit the **Run** button to instantly compile your document.
- **Instant Live Preview**: The moment your document compiles, the extension automatically opens a rich Markdown preview to the side!
- **Export to Word (DOCX)**: Click the Word icon in the top right of the editor to instantly convert your file into a native Microsoft Word Document.
- **Project Commands**: Compile Markdown, force a no-cache build, lint the project, or clear `.pamd-cache` directly from the editor.
- **Diagnostics**: Compilation and lint failures are published in VS Code's Problems panel.
- **PAMD Syntax Highlighting**: Tags such as `<ctx>`, `<glb>`, `<tmp>`, and `<pagebreak/>` are highlighted.
- **Context Completions**: Inside `<ctx>` tags, suggestions are collected from keys returned by `context()`, including nested paths such as `project.author`. Suggestions appear automatically while typing; press `Ctrl+Space` to reopen them manually.
- **Automatic Context Tags**: Typing `<ctx>` inserts `</ctx>` and places the cursor between the tags, ready for a context key.
- **Custom Notebook Toolbar**: A visible PyAct toolbar button opens Compile, No Cache, DOCX, Lint, and Clear Cache actions. VS Code does not allow extensions to remove its built-in Run All and Run Cell actions. Disable the PyAct toolbar with `pyact.showNotebookToolbar` if needed.
- **Configurable Python**: Select the interpreter through `pyact.pythonPath`, including a virtual-environment executable.
- **Configurable Output**: Set `pyact.outputDirectory` to write generated files into a project-relative directory.
- **CSS Auto-Discovery**: If you have a `style.css` file next to your `.pamd` file, the Export to Word tool automatically applies your custom CSS rules to the final DOCX!
- **Streamlined Workflow**: We've removed the clutter. No "Select Kernel" prompts, and no accidental cell deletions. Just pure, focused writing.

## 🚀 Getting Started

1. **Install the PyAct CLI**: The extension uses the PyAct engine under the hood. Make sure you have it installed on your system:
   ```bash
   pip install pyact-cli
   ```
2. **Install this Extension**: Search for "PAMD" in the VS Code marketplace and install it.
3. **Open a `.pamd` file**: It will automatically open in Notebook mode.
4. **Hit Run**: Watch your Python code generate a stunning Markdown document instantly.

## ⚙️ Settings

```json
{
  "pyact.pythonPath": "python",
  "pyact.autoPreview": true,
  "pyact.outputDirectory": "",
  "pyact.showNotebookToolbar": true
}
```

The extension invokes `python -m pyact.cli` without a shell, so paths and
arguments containing spaces are handled safely.

### Customizing PAMD tag colors

The contents of `<ctx>` and `<glb>` tags use the
`entity.name.tag.pamd.content` TextMate scope, while their delimiters use
`punctuation.definition.tag.pamd`. The contents of `<tmp>` tags use
`string.unquoted.pamd`. You can customize these colors in VS Code's
`settings.json`:

```json
{
  "editor.tokenColorCustomizations": {
    "textMateRules": [
      {
        "scope": "entity.name.tag.pamd.content",
        "settings": {
          "foreground": "#FFCC66"
        }
      },
      {
        "scope": "string.unquoted.pamd",
        "settings": {
          "foreground": "#98C379"
        }
      }
    ]
  }
}
```

Happy writing!
