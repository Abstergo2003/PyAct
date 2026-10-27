<div align="center">
  <h1>📝 PAMD File Support for VS Code</h1>
  <p><b>A native Jupyter-like experience for Markdown generation.</b></p>
</div>

Writing `.pamd` files is great, and writing them in **Visual Studio Code** should feel purpose-built. This extension provides a dedicated PAMD editor with a controlled cell-based interface and PyAct actions.

## ✨ Features

- **Custom PAMD Editor**: Opens `.pamd` files in a dedicated editor with exactly one Markdown cell and as many Python code cells as you need, without VS Code's native notebook controls.
- **One-Click Compile**: Use the **Compile** button to instantly compile your document.
- **Instant Live Preview**: The moment your document compiles, the extension automatically opens a rich Markdown preview to the side!
- **Export to Word (DOCX)**: Click the Word icon in the top right of the editor to instantly convert your file into a native Microsoft Word Document.
- **Project Commands**: Compile Markdown, force a no-cache build, lint the project, or clear `.pamd-cache` directly from the editor.
- **Diagnostics**: Compilation and lint failures are published in VS Code's Problems panel.
- **Monaco Syntax Highlighting**: Python and Markdown cells use the embedded Monaco editor for full language tokenization, including strings, numbers, comments, variables, and keywords.
- **PAMD Markdown Highlighting**: Markdown headings, lists, quotes, links, emphasis, inline code, fenced code, HTML comments, and PAMD tags such as `<ctx>`, `<glb>`, `<tmp>`, and `<pagebreak/>` are highlighted inside the custom editor.
- **Context Completions**: Inside `<ctx>` tags, suggestions are collected from keys returned by `context()`, including nested paths such as `project.author`. Suggestions appear automatically while typing; press `Ctrl+Space` to reopen them manually.
- **Automatic Context Tags**: Typing `<ctx>` inserts `</ctx>` and places the cursor between the tags, ready for a context key.
- **Stable Editing**: Typing does not rebuild the webview, so the active cell keeps focus and the document does not jump to the top.
- **Custom Toolbar**: Compile, No Cache, DOCX, Lint, and Clear Cache are available directly inside the PAMD editor.
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
3. **Open a `.pamd` file**: It will automatically open in the custom PAMD editor.
4. **Use Compile**: Watch your Python code generate a stunning Markdown document instantly.

## ⚙️ Settings

```json
{
  "pyact.pythonPath": "python",
  "pyact.autoPreview": true,
  "pyact.outputDirectory": "",
  "pyact.showToolbar": true
}
```

The extension invokes `python -m pyact.cli` without a shell, so paths and
arguments containing spaces are handled safely.

Syntax highlighting is provided by the Monaco editor bundled with the
extension, so it works without a network connection. The editor uses the
active VS Code theme family and keeps each cell independently resizable.

To customize token colors, edit `EDITOR_COLORS` near the top of
`src/pamdEditorHtml.ts`. The `dark` and `light` sections include separate
entries for Python, Markdown, and PAMD tokens. Set an entry to an empty string
to use the active VS Code theme color for that token instead.

To reuse a different VS Code theme color for a Monaco token, edit
`THEME_TOKEN_MAP` in the same file. For example,
`'markdown-heading': 'keyword'` makes Markdown headings use the theme's keyword
color, while `'pamd-tag': 'namespace'` makes PAMD tags use the namespace color.
The left side is a Monaco token and the right side is the logical VS Code
theme token whose resolved color should be reused.

After changing the extension source, run `npm run compile`, reload the VS Code
window, and reopen the `.pamd` file.

Happy writing!
