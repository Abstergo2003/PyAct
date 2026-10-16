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
- `body`: Global defaults (font-family, font-size, color, line-height, margins).
- `h1, h2, h3, h4, h5, h6`: Heading specific formatting.
- `p` or `text`: Standard paragraph text.
- `equation`: Spacing and alignment around math blocks.
- `image`: Dimensions and alignment for images.
- `table`: Table width, alignment, padding, and border styles (`border`, `border-style`, `border-color`, `border-width`, or `style: "Table Grid"`).
- `th` or `table_header`: Header row background shading (`background-color`), font color, weight, and alignment.
- `td` or `table_cell`: Body cell alignment, background shading, and typography.
- `tr:nth-child(even)`: Alternating row background shading (zebra striping).
- `code`: Typography and shading for inline code spans.
- `hyperlink`: Colors and underlines for links.
- `list`: Indentation and spacing for bullet and numbered lists.

### Supported Properties
- `font-family`: e.g., `"Arial"`, `"Calibri"`, `"Consolas"`
- `font-size`: e.g., `11pt`, `14pt`
- `color` / `background-color`: e.g., `#2F5496`, `#F2F4F8`, `blue`
- `font-weight`: `bold` | `normal`
- `font-style`: `italic` | `normal`
- `text-decoration`: `underline` | `none`
- `text-align`: `left` | `center` | `right` | `justify` (also supports Markdown column alignments `:---:`, `---:`)
- `margin-top` / `margin-bottom`: e.g., `12pt`
- `line-height`: e.g., `1.15`, `1.5`
- `page-break-before`: `always` | `auto` (Forces a page break before the element)
- `width` / `height`: e.g., `100%`, `auto`, `6in` (For tables and images)
- `border` / `border-style` / `border-color` / `border-width`: e.g., `1px solid #D0D7DE`, `dashed`, `none` (For tables)
- `padding` / `cell-padding`: e.g., `6pt 8pt` (For table cells)

## 4. Document Settings via `pamd.conf`

To configure global Word document properties such as running headers, footers, metadata, and page layout, create a `pamd.conf` file in your project or `.pamd` directory. PyAct automatically discovers it when exporting with `--docx`.

### Example `pamd.conf`

```ini
[Header]
left = My Project
right = 2026
font_size = 9pt
color = #666666

[Footer]
left = Confidential
center = Page {page} of {pages}
font_size = 9pt

[Metadata]
author = Radek
title = Structural Engineering Calculations
subject = PyAct Project
category = Engineering

[Page]
orientation = portrait
size = A4
margin = 1in
```

### Supported Sections & Options

#### `[Header]` and `[Footer]`
- **3-Zone Layout**: `left`, `center`, `right` (automatically positioned using dynamic tab stops aligned to page margins).
- **Single Block**: `text` or `content` with optional `align = left | center | right`.
- **Dynamic Page Numbers**: Use `{page}` for the current page and `{pages}` for total pages (e.g. `Page {page} of {pages}`). You can also enable `page_number = true`.
- **Typography & Styling**:
  - `font_name` / `font`: Font family (e.g. `Arial`, `Calibri`).
  - `font_size` / `size`: Font size (e.g. `9pt`, `10pt`).
  - `color`: Hex color string (e.g. `#888888`).
  - `bold`: `true` | `false`.
  - `italic`: `true` | `false`.

#### `[Metadata]`
Sets Word document properties (`doc.core_properties`):
- `author` (or `autor` / `creator`)
- `title` (or `tytul`)
- `subject` (or `temat`)
- `keywords` (or `slowa_kluczowe` / `tags`)
- `category` (or `kategoria`)
- `comments` (or `description` / `opis`)
- `status` (or `content_status`)
- `language` (or `jezyk`)
- `version` (or `wersja`)

#### `[Page]`
- `orientation`: `portrait` | `landscape`
- `size` / `paper_size`: `A4` | `Letter` | `Legal`
- `margin` / `margins`: e.g., `1in`, `2.5cm`, `20mm`
- `margin_top`, `margin_bottom`, `margin_left`, `margin_right`: individual margin overrides.

