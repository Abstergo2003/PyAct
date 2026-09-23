<div align="center">
  <h1>📝 PAMD File Support for VS Code</h1>
  <p><b>A native Jupyter-like experience for Markdown generation.</b></p>
</div>

Writing `.pamd` files is great, but writing them in **Visual Studio Code** is magical. This extension registers `.pamd` files as native Notebooks, giving you a powerful, seamless writing experience.

## ✨ Features

- **Two-Cell Notebook UI**: Opens your `.pamd` files beautifully separated into a Python code cell and a Markdown cell.
- **One-Click Magic**: Hit the **Run** button to instantly compile your document.
- **Instant Live Preview**: The moment your document compiles, the extension automatically opens a rich Markdown preview to the side!
- **Export to Word (DOCX)**: Click the Word icon in the top right of the editor to instantly convert your file into a native Microsoft Word Document.
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

Happy writing!
