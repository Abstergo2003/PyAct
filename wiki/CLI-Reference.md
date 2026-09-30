# CLI Reference

The PyAct Compiler is invoked from the command line using the `pyact` command (or `python -m pyact.cli`).

## Usage

```bash
pyact [-h] [-o OUTPUT] [--docx DOCX_PATH] [--css CSS_PATH] input
```

## Positional Arguments

- `input`
  **Required.** The path to the main `.pamd` file you want to compile. The `.pamd` extension is automatically inferred if omitted.

## Optional Arguments

- `-o OUTPUT`, `--output OUTPUT`
  The file path to save the generated `.md` (Markdown) file. If this flag is omitted, the compiler will simply print the raw compiled Markdown directly to `stdout`.

- `--docx DOCX_PATH`
  Triggers the native Word rendering engine to generate a `.docx` file at the specified path alongside the Markdown file.

- `--css CSS_PATH`
  Provides a specific `style.css` file to use for styling the `.docx` document. 
  *(Note: If omitted, the CLI will automatically look for a `style.css` file in the same directory as the `input` file. If none exists, it uses the built-in system defaults.)*

- `--lint`
  Runs the PyAct Linter on your project. This tool scans the `.pamd` files in your directory, tracks down nested dependencies, and reports any defined context variables that were never used, as well as dangling `.pamd` files that are never imported.

## Automatic Caching (pamd-cache)

PyAct features a completely automatic, AST-aware caching system. 

When you compile a `.pamd` document, PyAct saves the compiled Markdown into a hidden `.pamd-cache` directory. On subsequent builds, the engine recursively checks the "last modified" timestamps of the main file **and all its nested `<tmp>` templates**. If nothing has changed, PyAct completely bypasses the Python execution engine and instantly loads the cache, resulting in lightning-fast document generation. 

## Example Pipeline

Compile a document to both Markdown and DOCX, using a custom CSS theme:

```bash
pyact ./docs/main.pamd -o ./out/compiled.md --docx ./out/final.docx --css ./themes/dark_mode.css
```
