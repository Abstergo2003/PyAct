# PAMD VS Code Editor

The PAMD File Support extension provides a custom cell-based editor for
`.pamd` files. It uses an embedded Monaco editor instead of VS Code's native
notebook surface, so native notebook controls such as **Run All** are not
shown.

## Editor behavior

- Each file contains exactly one Markdown cell and zero or more Python cells.
- Python cells use a dedicated PyAct tokenizer for keywords, variables,
  functions, classes, imports, namespaces, strings, numbers, and comments.
- Markdown cells support headings, lists, quotes, links, emphasis, inline and
  fenced code, HTML comments, and PAMD tags.
- Cells grow vertically with their content.
- Mouse-wheel scrolling moves the document rather than trapping the pointer
  inside a cell.
- Editing preserves the active cell focus, cursor, and document scroll
  position.
- Typing `<ctx>` automatically inserts `</ctx>` and places the cursor inside
  the tag.
- Context completions are available automatically and with `Ctrl+Space`.

## Toolbar actions

The in-editor toolbar provides:

- Compile Markdown
- Compile without cache
- Export to DOCX
- Lint the project
- Clear the PAMD cache

The same actions are also available from the editor title bar and the
**PyAct** command menu.

## Syntax color customization

The editor resolves colors from the active VS Code theme and translates them
to Monaco tokens. The mapping is defined in:

`pamd-file-support/src/pamdEditorHtml.ts`

### Remapping theme colors

Edit `THEME_TOKEN_MAP` to make one Monaco token use another VS Code theme
token's color:

```ts
const THEME_TOKEN_MAP = {
  'markdown-heading': 'keyword',
  'markdown-link': 'namespace',
  'pamd-tag': 'namespace',
  'pamd-tag-content': 'string',
  'import-name': 'variable'
};
```

The left-hand side is a Monaco token emitted by the editor tokenizer. The
right-hand side is a logical theme token whose color is resolved from the
active VS Code theme.

### Manual fallback colors

`EDITOR_COLORS.dark` and `EDITOR_COLORS.light` define fallback colors for
tokens that the active theme does not provide. Set a fallback entry to an
empty string to leave the token color to the active theme.

After changing the TypeScript source, run:

```bash
cd pamd-file-support
npm run compile
```

Reload the VS Code window and reopen the `.pamd` file to load the rebuilt
webview.

### User-configurable editor theme

Use the Command Palette command **`PyAct: Configure PAMD Editor Theme`**.
It opens the `pyact.editorTheme` setting, whose values override the built-in
Monaco palette without requiring a source change.

The complete token list is:

```text
keyword              constant              variable
variable.language    function              class-name
annotation           namespace             import-name
number               string                string.escape
operator              delimiter             comment
markdown-heading     markdown-quote        markdown-list
markdown-code-fence  markdown-code         markdown-bold
markdown-italic      markdown-link         markdown-entity
pamd-tag              pamd-tag-content      pamd-control
```

Example settings:

```json
"pyact.editorTheme": {
  "string": "#CE9178",
  "string.escape": "#D7BA7D",
  "class-name": "#4EC9B0",
  "function": "#DCDCAA",
  "variable": "#9CDCFE",
  "variable.language": "#569CD6",
  "import-name": "#9CDCFE",
  "namespace": "#4EC9B0",
  "keyword": "#C586C0",
  "constant": "#569CD6",
  "number": "#B5CEA8",
  "operator": "#D4D4D4",
  "delimiter": "#D4D4D4",
  "comment": "#6A9955",
  "markdown-heading": "#569CD6",
  "markdown-quote": "#6A9955",
  "markdown-list": "#C586C0",
  "markdown-code-fence": "#DCDCAA",
  "markdown-code": "#CE9178",
  "markdown-bold": "#DCDCAA",
  "markdown-italic": "#DCDCAA",
  "markdown-link": "#4FC1FF",
  "markdown-entity": "#B5CEA8",
  "pamd-tag": "#4FC1FF",
  "pamd-tag-content": "#DCDCAA",
  "pamd-control": "#C586C0"
}
```

Values may be hex colors or objects such as
`{ "foreground": "#4EC9B0", "fontStyle": "bold" }`. User settings take
precedence over the built-in dark/light palettes.

## Implementation structure

- `src/extension.ts` handles VS Code activation, custom-editor lifecycle,
  document synchronization, commands, diagnostics, and theme extraction.
- `src/pamdEditorHtml.ts` contains the webview HTML, CSS, Monaco setup,
  tokenizers, theme mapping, completions, and cell rendering.
- `out/` contains generated JavaScript used by the extension runtime.
