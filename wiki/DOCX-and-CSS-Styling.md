# DOCX & CSS Styling

PyAct doesn't just generate Markdown—it features a custom-built, native rendering engine that translates your parsed AST into **Microsoft Word (.docx)** documents!

## 1. Generating a DOCX
To export to Word, simply append the `--docx` flag to your CLI command:

```bash
pyact document.pamd -o document.md --docx final_report.docx
```
*(If you are using the VS Code Extension, you can just click the Word Icon in the top right of the editor!)*

## 2. Supported Native Elements
Unlike basic converters, PyAct builds the `.docx` document natively using the `python-docx` API. It supports:
- **Math**: `$$ x=2 $$` converts to a native Word OMML Equation object!
- **Footnotes**: Footnotes are mapped to invisible `w:bookmark` anchors and linked using blue, superscript `w:hyperlink` cross-references.
- **Images**: Remote images (URLs) are downloaded into memory on-the-fly and embedded directly into the binary `.docx` file.
- **Lists & Tables**: Uses native Word styles (`List Bullet`, `List Number`) and `w:shd` XML injection for table headers.

## 3. Styling with CSS
By default, the DOCX is styled using standard professional defaults. However, you can completely customize the layout using a `style.css` file!

If a file named `style.css` exists in the exact same directory as your `.pamd` file, PyAct will **automatically load it** and map the CSS properties to Word formatting commands.

### Supported Selectors
- `body`: Global defaults.
- `h1, h2, h3, h4, h5, h6`: Heading specific formatting.
- `p` or `text`: Standard paragraph text.
- `equation`: Spacing around OMML math blocks.
- `image`: Dimensions for downloaded images.
- `table` / `table_header`: Table borders and header shading.
- `hyperlink`: Colors and underlines for links.
- `list`: Indentation for bullet points.

### Supported Properties
- `font-family`: e.g., `"Arial"`, `"Calibri"`
- `font-size`: e.g., `12pt`, `14pt`
- `color` / `background-color`: e.g., `#FF0000`, `blue`
- `font-weight`: `bold` | `normal`
- `font-style`: `italic` | `normal`
- `text-decoration`: `underline` | `none`
- `text-align`: `left` | `center` | `right` | `justify`
- `margin-top` / `margin-bottom`: e.g., `12pt`
- `line-height`: e.g., `1.15`, `1.5`
- `page-break-before`: `always` | `auto` (Forces a page break before the element)
- `width` / `height`: e.g., `6in` (Specifically for images/tables)
