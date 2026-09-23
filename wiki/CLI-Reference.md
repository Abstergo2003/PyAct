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

## Example Pipeline

Compile a document to both Markdown and DOCX, using a custom CSS theme:

```bash
pyact ./docs/main.pamd -o ./out/compiled.md --docx ./out/final.docx --css ./themes/dark_mode.css
```
