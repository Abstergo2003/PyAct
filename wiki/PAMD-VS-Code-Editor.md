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

## Implementation structure

- `src/extension.ts` handles VS Code activation, custom-editor lifecycle,
  document synchronization, commands, diagnostics, and theme extraction.
- `src/pamdEditorHtml.ts` contains the webview HTML, CSS, Monaco setup,
  tokenizers, theme mapping, completions, and cell rendering.
- `out/` contains generated JavaScript used by the extension runtime.
