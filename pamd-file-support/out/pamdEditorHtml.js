"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMonacoHtml = getMonacoHtml;
const vscode = __importStar(require("vscode"));
function getMonacoHtml(webview, initial, showToolbar, extensionPath) {
    const nonce = getNonce();
    const monacoRoot = webview.asWebviewUri(vscode.Uri.joinPath(vscode.Uri.file(extensionPath), 'node_modules', 'monaco-editor', 'min')).toString();
    const csp = `default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src ${webview.cspSource} 'nonce-${nonce}'; worker-src blob:;`;
    return `<!doctype html>
<html><head><meta charset="UTF-8"><meta http-equiv="Content-Security-Policy" content="${csp}">
<style>
body { color: var(--vscode-editor-foreground); background: var(--vscode-editor-background); font-family: var(--vscode-font-family); margin: 0; }
.toolbar { position: sticky; top: 0; z-index: 2; display: flex; gap: 6px; padding: 10px 14px; border-bottom: 1px solid var(--vscode-panel-border); background: var(--vscode-editor-background); }
button { color: var(--vscode-button-foreground); background: var(--vscode-button-background); border: 0; border-radius: 3px; padding: 6px 10px; cursor: pointer; }
button:hover { background: var(--vscode-button-hoverBackground); }
#cells { max-width: 90%; margin: 18px auto; padding: 0 18px 30px; }
.cell { border: 1px solid var(--vscode-panel-border); border-radius: 5px; margin: 12px 0; overflow: hidden; }
.cell-header { padding: 7px 10px; color: var(--vscode-descriptionForeground); background: var(--vscode-textCodeBlock-background); font-size: 12px; text-transform: uppercase; }
.editor-wrap { min-height: 150px; }
.monaco-editor-host { min-height: 150px; }
.suggestions { position: fixed; display: none; z-index: 4; min-width: 220px; max-height: 220px; overflow: auto; background: var(--vscode-quickInput-background); border: 1px solid var(--vscode-quickInputTitle-background); box-shadow: 0 4px 12px #0006; }
.suggestion { padding: 6px 10px; cursor: pointer; }
.suggestion:hover { background: var(--vscode-list-hoverBackground); }
#status { margin-left: auto; color: var(--vscode-descriptionForeground); align-self: center; }
</style></head><body>
<div class="toolbar" style="display:${showToolbar ? 'flex' : 'none'}">
<button data-action="compileMarkdown">Compile</button><button data-action="compileNoCache">No Cache</button>
<button data-action="generateDocx">DOCX</button><button data-action="lint">Lint</button><button data-action="clearCache">Clear Cache</button>
<span id="status">Ready</span></div><main id="cells"></main><div id="suggestions" class="suggestions"></div>
<script nonce="${nonce}" src="${monacoRoot}/vs/loader.js?v=2.2.0"></script>
<script nonce="${nonce}">
const vscode = acquireVsCodeApi();
const monacoRoot = ${JSON.stringify(monacoRoot)};
let pamd = ${initial};
let saveTimer;
let editors = [];
let monacoReady = false;
let tokenPalette = null;
let themeSeq = 0;
const cells = document.getElementById('cells');
const status = document.getElementById('status');
const suggestions = document.getElementById('suggestions');
function codeText() { return pamd.cells.filter(c => c.cell_type === 'code').map(c => String(c.source)).join('\\n'); }
function keys(code) {
  const result = new Set();
  const match = code.match(/\\bdef\\s+context\\s*\\([^)]*\\)\\s*:[\\s\\S]*?\\breturn\\s*\\{/);
  if (!match) return [];
  const body = code.slice(match.index + match[0].length - 1);
  const re = /(['"])([^'"\\\\]+)\\1\\s*:/g; let item;
  while ((item = re.exec(body))) result.add(item[2]);
  return [...result].sort();
}
function contextPrefix(text, offset) {
  const before = text.slice(0, offset);
  const start = before.lastIndexOf('<ctx>');
  if (start < 0 || before.slice(start).includes('</ctx>')) return undefined;
  const prefix = before.slice(start + 5);
  return /^[\\w.]*$/.test(prefix) ? { start, prefix } : undefined;
}
function sync() {
  pamd.cells = editors.map((entry, index) => ({ ...pamd.cells[index], source: entry.editor.getValue() }));
  status.textContent = 'Saving...';
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    vscode.postMessage({ type: 'update', text: JSON.stringify({
      cells: pamd.cells.map(c => ({ cell_type: c.cell_type, source: String(c.source).split(/(?<=\\n)/g) }))
    }, null, 2) });
    status.textContent = 'Saved';
  }, 250);
}
function resize(entry) {
  const contentHeight = Math.max(150, entry.editor.getContentHeight());
  entry.host.style.height = contentHeight + 'px';
  entry.editor.layout({ width: entry.host.clientWidth, height: contentHeight });
}
function showCompletions(entry) {
  if (entry.cell.cell_type !== 'markdown') return;
  const model = entry.editor.getModel();
  const position = entry.editor.getPosition();
  const offset = model.getOffsetAt(position);
  const context = contextPrefix(model.getValue(), offset);
  if (!context) { suggestions.style.display = 'none'; return; }
  const matches = keys(codeText()).filter(key => key.startsWith(context.prefix));
  suggestions.innerHTML = '';
  matches.forEach(key => {
    const item = document.createElement('div');
    item.className = 'suggestion';
    item.textContent = key;
    item.onclick = () => {
      const current = entry.editor.getPosition();
      const currentOffset = model.getOffsetAt(current);
      const replacementStart = model.getPositionAt(currentOffset - context.prefix.length);
      entry.editor.executeEdits('pamd-completion', [{
        range: new monaco.Range(replacementStart.lineNumber, replacementStart.column, current.lineNumber, current.column),
        text: key
      }]);
      suggestions.style.display = 'none';
      entry.editor.focus();
      sync();
    };
    suggestions.append(item);
  });
  if (!matches.length) { suggestions.style.display = 'none'; return; }
  const rect = entry.host.getBoundingClientRect();
  suggestions.style.left = rect.left + 'px';
  suggestions.style.top = (rect.top + 28) + 'px';
  suggestions.style.display = 'block';
}
// Edit these values to customize every Monaco token color in one place.
// Set a token to '' to let the active VS Code theme provide its color.
const EDITOR_COLORS = {
  dark: {
    'keyword': '#C586C0', 'constant': '#569CD6', 'variable': '#9CDCFE', 'variable.language': '#569CD6',
    'function': '#DCDCAA', 'class-name': '#4EC9B0', 'annotation': '#DCDCAA', 'namespace': '#4EC9B0',
    'import-name': '#9CDCFE', 'number': '#B5CEA8', 'string': '#CE9178', 'string.escape': '#D7BA7D',
    'operator': '#D4D4D4', 'delimiter': '#D4D4D4', 'comment': '#6A9955',
    'markdown-heading': '#569CD6', 'markdown-quote': '#6A9955', 'markdown-list': '#C586C0',
    'markdown-code-fence': '#DCDCAA', 'markdown-code': '#CE9178', 'markdown-bold': '#DCDCAA',
    'markdown-italic': '#DCDCAA', 'markdown-link': '#4FC1FF', 'markdown-entity': '#B5CEA8',
    'pamd-tag': '#4FC1FF', 'pamd-tag-content': '#DCDCAA', 'pamd-control': '#C586C0'
  },
  light: {
    'keyword': '#AF00DB', 'constant': '#0000FF', 'variable': '#001080', 'variable.language': '#0000FF',
    'function': '#795E26', 'class-name': '#267F99', 'annotation': '#795E26', 'namespace': '#267F99',
    'import-name': '#001080', 'number': '#098658', 'string': '#A31515', 'string.escape': '#EE0000',
    'operator': '#000000', 'delimiter': '#000000', 'comment': '#008000',
    'markdown-heading': '#0000FF', 'markdown-quote': '#008000', 'markdown-list': '#AF00DB',
    'markdown-code-fence': '#795E26', 'markdown-code': '#A31515', 'markdown-bold': '#795E26',
    'markdown-italic': '#795E26', 'markdown-link': '#0451A5', 'markdown-entity': '#098658',
    'pamd-tag': '#0451A5', 'pamd-tag-content': '#795E26', 'pamd-control': '#AF00DB'
  }
};
// Map each Monaco token to the VS Code theme token whose color it should use.
// Change only the right-hand side to remap colors without changing tokenization.
const THEME_TOKEN_MAP = {
  'keyword': 'keyword',
  'constant': 'constant',
  'variable': 'variable',
  'variable.language': 'variable.language',
  'function': 'function',
  'class-name': 'class-name',
  'annotation': 'annotation',
  'namespace': 'namespace',
  'import-name': 'namespace',
  'number': 'number',
  'string': 'string',
  'string.escape': 'string.escape',
  'operator': 'operator',
  'delimiter': 'delimiter',
  'comment': 'comment',
  'markdown-heading': 'keyword',
  'markdown-quote': 'comment',
  'markdown-list': 'keyword',
  'markdown-code-fence': 'function',
  'markdown-code': 'string',
  'markdown-bold': 'function',
  'markdown-italic': 'function',
  'markdown-link': 'namespace',
  'markdown-entity': 'constant',
  'pamd-tag': 'namespace',
  'pamd-tag-content': 'string',
  'pamd-control': 'keyword'
};
function themeBase() {
  const classes = document.body.classList;
  if (classes.contains('vscode-light') || classes.contains('vscode-high-contrast-light')) return 'vs';
  if (classes.contains('vscode-high-contrast')) return 'hc-black';
  return 'vs-dark';
}
function cssColor(name, fallback) {
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  if (!raw) return fallback;
  const probe = document.createElement('span');
  probe.style.color = raw;
  document.body.appendChild(probe);
  const parts = getComputedStyle(probe).color.match(/[\\d.]+/g);
  probe.remove();
  if (!parts || parts.length < 3) return fallback;
  const hex = n => Math.max(0, Math.min(255, Math.round(Number(n)))).toString(16).padStart(2, '0');
  const alpha = parts.length > 3 ? hex(Number(parts[3]) * 255) : '';
  return '#' + hex(parts[0]) + hex(parts[1]) + hex(parts[2]) + alpha;
}
function normHex(value) {
  if (typeof value !== 'string') return undefined;
  let digits = value.trim().replace(/^#/, '');
  if (/^[0-9a-fA-F]{3,4}$/.test(digits)) digits = digits.split('').map(c => c + c).join('');
  return /^[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$/.test(digits) ? digits : undefined;
}
function applyTheme() {
  if (!monacoReady) return;
  const base = themeBase();
  const dark = base !== 'vs';
  const fallback = EDITOR_COLORS[dark ? 'dark' : 'light'];
  const editorFg = cssColor('--vscode-editor-foreground', dark ? '#D4D4D4' : '#333333');
  const editorHex = normHex(editorFg);
  const rgbOf = hex => [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16));
  // "Too plain" = would read as normal text. Exact equality is not enough (#D4D4D4 vs #CCCCCC).
  const tooPlain = hex => {
    if (!hex || !editorHex) return false;
    const a = rgbOf(hex), b = rgbOf(editorHex);
    return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) < 48;
  };
  // Theme-aware colour VS Code defines for variable symbols; used when the theme leaves variables plain.
  let variableAlt = normHex(cssColor('--vscode-symbolIcon-variableForeground', fallback['variable']));
  if (tooPlain(variableAlt)) variableAlt = normHex(fallback['variable']);
  const plainTokens = ['operator', 'delimiter'];
  const rules = Object.keys(fallback).map(token => {
    const themeToken = THEME_TOKEN_MAP[token] || token;
    const entry = tokenPalette ? (tokenPalette[themeToken] || {}) : {};
    const isVariable = token === 'variable' || token === 'import-name';
    const isPlainToken = plainTokens.indexOf(token) >= 0;
    const manualColor = normHex(fallback[token]);
    let color = normHex(entry.foreground) || manualColor;
    // A highlighted token must not look like plain text: drop theme colours that are too close to it.
    if (!isPlainToken && tooPlain(color)) color = undefined;
    if (!color) {
      if (isVariable) color = variableAlt;
      else if (tokenPalette && isPlainToken) color = editorHex;
      else color = manualColor;
    }
    const rule = { token, foreground: color };
    if (typeof entry.fontStyle === 'string') rule.fontStyle = entry.fontStyle;
    return rule;
  });
  const name = 'pamd-theme-' + (++themeSeq);
  monaco.editor.defineTheme(name, {
    base,
    inherit: true,
    rules,
    colors: {
      'editor.background': '#00000000',
      'editor.foreground': editorFg,
      'editorCursor.foreground': cssColor('--vscode-editorCursor-foreground', editorFg),
      'editorLineNumber.foreground': cssColor('--vscode-editorLineNumber-foreground', '#858585'),
      'editorLineNumber.activeForeground': cssColor('--vscode-editorLineNumber-activeForeground', editorFg),
      'editor.selectionBackground': cssColor('--vscode-editor-selectionBackground', '#264F78'),
      'editor.inactiveSelectionBackground': cssColor('--vscode-editor-inactiveSelectionBackground', '#3A3D41')
    }
  });
  monaco.editor.setTheme(name);
}
let themeTimer;
function scheduleTheme() { clearTimeout(themeTimer); themeTimer = setTimeout(applyTheme, 50); }
new MutationObserver(scheduleTheme).observe(document.body, { attributes: true, attributeFilter: ['class'] });
new MutationObserver(scheduleTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['style'] });
function registerCompletions(entry) {
  if (entry.cell.cell_type !== 'markdown') return;
  entry.completion = monaco.languages.registerCompletionItemProvider('pyact-markdown', {
    triggerCharacters: ['<', '.', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '_'],
    provideCompletionItems(model, position) {
      const offset = model.getOffsetAt(position);
      const context = contextPrefix(model.getValue(), offset);
      if (!context) return { suggestions: [] };
      return {
        suggestions: keys(codeText()).filter(key => key.startsWith(context.prefix)).map(key => ({
          label: key,
          kind: monaco.languages.CompletionItemKind.Variable,
          insertText: key,
          range: new monaco.Range(
            model.getPositionAt(offset - context.prefix.length).lineNumber,
            model.getPositionAt(offset - context.prefix.length).column,
            position.lineNumber,
            position.column
          )
        }))
      };
    }
  });
}
function render() {
  editors.forEach(entry => {
    entry.editor.dispose();
    entry.completion?.dispose();
    entry.closeTag?.dispose();
  });
  editors = [];
  cells.innerHTML = '';
  pamd.cells.forEach((cell, index) => {
    const wrapper = document.createElement('section');
    wrapper.className = 'cell';
    const header = document.createElement('div');
    header.className = 'cell-header';
    header.textContent = cell.cell_type + ' cell ' + (index + 1);
    const host = document.createElement('div');
    host.className = 'monaco-editor-host';
    const editorWrap = document.createElement('div');
    editorWrap.className = 'editor-wrap';
    editorWrap.append(host);
    wrapper.append(header, editorWrap);
    cells.append(wrapper);
    const editor = monaco.editor.create(host, {
      value: String(cell.source),
      language: cell.cell_type === 'markdown' ? 'pyact-markdown' : 'pyact-python',
      automaticLayout: false,
      minimap: { enabled: false },
      lineNumbers: 'on',
      wordWrap: 'on',
      scrollBeyondLastLine: false,
      overviewRulerLanes: 0,
      folding: true,
      fontSize: 14,
      padding: { top: 12, bottom: 12 }
    });
    host.addEventListener('wheel', event => {
      if (event.deltaY === 0 && event.deltaX === 0) return;
      event.preventDefault();
      event.stopPropagation();
      window.scrollBy({ top: event.deltaY, left: event.deltaX, behavior: 'auto' });
    }, { capture: true, passive: false });
    const entry = { cell, editor, host };
    editors.push(entry);
    editor.onDidContentSizeChange(() => resize(entry));
    editor.onDidChangeModelContent(event => {
      const model = editor.getModel();
      if (cell.cell_type === 'markdown') {
        const position = editor.getPosition();
        const offset = position ? model.getOffsetAt(position) : 0;
        const valueBeforeCursor = model.getValue().slice(0, offset);
        if (position && valueBeforeCursor.endsWith('<ctx>') && !model.getValue().slice(offset).startsWith('</ctx>')) {
          editor.executeEdits('pamd-close-tag', [{
            range: new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column),
            text: '</ctx>'
          }]);
          editor.setPosition(position);
        }
      }
      sync();
    });
    editor.onDidChangeCursorSelection(() => showCompletions(entry));
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => showCompletions(entry));
    registerCompletions(entry);
    resize(entry);
  });
}
document.querySelectorAll('[data-action]').forEach(button => button.onclick = () => {
  sync();
  setTimeout(() => vscode.postMessage({ type: 'action', action: button.dataset.action }), 300);
});
window.addEventListener('message', event => {
  if (event.data.type === 'load') { pamd = event.data.pamd; render(); status.textContent = 'Ready'; }
  if (event.data.type === 'tokenColors') { tokenPalette = event.data.palette || null; applyTheme(); }
  if (event.data.type === 'error') status.textContent = event.data.message;
});
vscode.postMessage({ type: 'ready' });
window.MonacoEnvironment = {
  getWorkerUrl: function() {
    const worker = "importScripts('" + monacoRoot + "/vs/base/worker/workerMain.js');";
    return 'data:text/javascript;charset=utf-8,' + encodeURIComponent(worker);
  }
};
require.config({ paths: { vs: monacoRoot + '/vs' } });
require(['vs/editor/editor.main'], () => {
  monaco.languages.register({ id: 'pyact-markdown' });
  monaco.languages.setMonarchTokensProvider('pyact-markdown', {
    defaultToken: '',
    tokenizer: {
      root: [
        [/^\\s*#{1,6}(?=\\s)/, 'markdown-heading'],
        [/^\\s*>/, 'markdown-quote'],
        [/^\\s*(?:[-*+]\\s+|\\d+\\.\\s+)/, 'markdown-list'],
        [/^\\s*\\x60{3}.*$/, 'markdown-code-fence', '@codeBlock'],
        [/<!--/, 'comment', '@htmlComment'],
        [/<(?:ctx|glb|tmp)>/, 'pamd-tag', '@pamdContent'],
        [/<\\/?(?:toc|pagebreak|sectionbreak|landscape|pb|sb)\\s*\\/?\\s*>/, 'pamd-control'],
        [/<\\/(?:ctx|glb|tmp)>/, 'pamd-tag'],
        [/\\[[^\\]\\n]+\\]\\([^\\)\\n]+\\)/, 'markdown-link'],
        [/\\x60[^\\x60\\n]+\\x60/, 'markdown-code'],
        [/\\*\\*[^*\\n]+\\*\\*|__[^_\\n]+__/, 'markdown-bold'],
        [/\\*[^*\\n]+\\*|_[^_\\n]+_/, 'markdown-italic'],
        [/https?:\\/\\/[^\\s)>]+/, 'markdown-link'],
        [/&(?:amp|lt|gt|quot|apos|nbsp);/, 'markdown-entity'],
        [/\\s+/, 'white'],
        [/./, '']
      ],
      codeBlock: [
        [/^\\s*\\x60{3}\\s*$/, 'markdown-code-fence', '@pop'],
        [/.*$/, 'markdown-code']
      ],
      pamdContent: [
        [/<\\/(?:ctx|glb|tmp)>/, 'pamd-tag', '@pop'],
        [/[^<]+/, 'pamd-tag-content'],
        [/</, 'pamd-tag-content']
      ],
      htmlComment: [
        [/-->/, 'comment', '@pop'],
        [/[^-]+/, 'comment'],
        [/./, 'comment']
      ]
    }
  });
  monaco.languages.register({ id: 'pyact-python' });
  monaco.languages.setMonarchTokensProvider('pyact-python', {
    defaultToken: '',
    keywords: [
      'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
      'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
      'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or',
      'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
    ],
    constants: ['True', 'False', 'None'],
    selfNames: ['self', 'cls'],
    tokenizer: {
      root: [
        [/#.*$/, 'comment'],
        [/^\\s*@[A-Za-z_][\\w.]*/, 'annotation'],
        [/\\b(def)(\\s+)([A-Za-z_]\\w*)/, ['keyword', 'white', 'function']],
        [/\\b(class)(\\s+)([A-Za-z_]\\w*)/, ['keyword', 'white', 'class-name']],
        [/^(\\s*)(import)\\b/, ['white', 'keyword'], '@importModules'],
        [/^(\\s*)(from)\\b/, ['white', 'keyword'], '@fromModule'],
        [/[rRbBuUfF]{0,2}"""/, 'string', '@tripleDouble'],
        [/[rRbBuUfF]{0,2}'''/, 'string', '@tripleSingle'],
        [/[rRbBuUfF]{0,2}"/, 'string', '@doubleString'],
        [/[rRbBuUfF]{0,2}'/, 'string', '@singleString'],
        [/0[xX][0-9a-fA-F_]+/, 'number.hex'],
        [/\\d[\\d_]*(?:\\.\\d+)?(?:[eE][+-]?\\d+)?j?/, 'number'],
        [/(\\.)(\\s*)([A-Za-z_]\\w*)(?=\\s*\\()/, ['delimiter', 'white', 'function']],
        [/(\\.)(\\s*)([A-Za-z_]\\w*)/, ['delimiter', 'white', 'variable']],
        [/[A-Za-z_]\\w*(?=\\s*\\()/, {
          cases: {
            '@keywords': 'keyword',
            '@constants': 'constant',
            '@selfNames': 'variable.language',
            '@default': 'function'
          }
        }],
        [/[A-Za-z_]\\w*/, {
          cases: {
            '@keywords': 'keyword',
            '@constants': 'constant',
            '@selfNames': 'variable.language',
            '@default': 'variable'
          }
        }],
        [/[{}()\\[\\]]/, '@brackets'],
        [/[,.:;]/, 'delimiter'],
        [/[+\\-*\\/%=!<>|&~^@]+/, 'operator'],
        [/\\s+/, 'white']
      ],
      // Monarch never sees the newline, so these states must pop themselves
      // at the start of the next line (the "^" rule) or they leak into the
      // rest of the file.
      importModules: [
        [/^/, '', '@pop'],
        [/#.*$/, 'comment'],
        [/\\bas\\b/, 'keyword'],
        [/[A-Za-z_][\\w.]*/, 'namespace'],
        [/[,\\s]+/, 'delimiter'],
        [/./, '', '@pop']
      ],
      fromModule: [
        [/^/, '', '@pop'],
        [/#.*$/, 'comment'],
        [/\\bimport\\b/, 'keyword', '@importNames'],
        [/[A-Za-z_.][\\w.]*/, 'namespace'],
        [/\\s+/, 'white'],
        [/./, '', '@pop']
      ],
      importNames: [
        [/^/, '', '@pop'],
        [/#.*$/, 'comment'],
        [/\\bas\\b/, 'keyword'],
        [/\\*/, 'operator'],
        [/[A-Za-z_]\\w*/, 'import-name'],
        [/[,()\\s\\\\]+/, 'delimiter'],
        [/./, '', '@pop']
      ],
      doubleString: [
        [/[^\\\\"]+/, 'string'],
        [/\\\\./, 'string.escape'],
        [/\\\\$/, 'string.escape'],
        [/"/, 'string', '@pop']
      ],
      singleString: [
        [/[^\\\\']+/, 'string'],
        [/\\\\./, 'string.escape'],
        [/\\\\$/, 'string.escape'],
        [/'/, 'string', '@pop']
      ],
      tripleDouble: [
        [/[^\\\\"]+/, 'string'],
        [/\\\\./, 'string.escape'],
        [/"""/, 'string', '@pop'],
        [/"/, 'string']
      ],
      tripleSingle: [
        [/[^\\\\']+/, 'string'],
        [/\\\\./, 'string.escape'],
        [/'''/, 'string', '@pop'],
        [/'/, 'string']
      ]
    }
  });
  monacoReady = true;
  applyTheme();
  render();
});
</script></body></html>`;
}
function getNonce() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 32; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}
//# sourceMappingURL=pamdEditorHtml.js.map