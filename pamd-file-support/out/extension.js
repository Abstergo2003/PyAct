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
exports.PamdCustomEditorProvider = void 0;
exports.extractContextKeys = extractContextKeys;
exports.contextCompletionPrefix = contextCompletionPrefix;
exports.shouldCloseContextTag = shouldCloseContextTag;
exports.createPyActCommand = createPyActCommand;
exports.activate = activate;
exports.deactivate = deactivate;
const pamdEditorHtml_1 = require("./pamdEditorHtml");
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const fs_1 = require("fs");
const path = __importStar(require("path"));
const diagnosticCollection = vscode.languages.createDiagnosticCollection('pamd');
let activePamdUri;
function extractContextKeys(code) {
    const contextStart = code.search(/\bdef\s+context\s*\([^)]*\)\s*:/);
    if (contextStart < 0) {
        return [];
    }
    const body = code.slice(contextStart).replace(/^\s*def\s+\w+\s*\([^)]*\)\s*:/m, '');
    const returnObject = body.match(/\breturn\s*{/);
    if (!returnObject || returnObject.index === undefined) {
        return [];
    }
    const keys = new Set();
    const parseObject = (openBrace, prefix) => {
        let depth = 1;
        let index = openBrace + 1;
        while (index < body.length && depth > 0) {
            if (body[index] === '{') {
                depth++;
                index++;
                continue;
            }
            if (body[index] === '}') {
                depth--;
                index++;
                continue;
            }
            if (depth === 1 && (body[index] === '"' || body[index] === "'")) {
                const quote = body[index];
                const keyStart = ++index;
                while (index < body.length && body[index] !== quote) {
                    index += body[index] === '\\' ? 2 : 1;
                }
                const key = body.slice(keyStart, index);
                index++;
                while (/\s/.test(body[index] ?? '')) {
                    index++;
                }
                if (body[index] !== ':') {
                    continue;
                }
                index++;
                while (/\s/.test(body[index] ?? '')) {
                    index++;
                }
                const fullKey = prefix ? `${prefix}.${key}` : key;
                keys.add(fullKey);
                if (body[index] === '{') {
                    index = parseObject(index, fullKey);
                }
                continue;
            }
            if (body[index] === '"' || body[index] === "'") {
                const quote = body[index++];
                while (index < body.length && body[index] !== quote) {
                    index += body[index] === '\\' ? 2 : 1;
                }
                index++;
                continue;
            }
            index++;
        }
        return index;
    };
    parseObject(body.indexOf('{', returnObject.index), '');
    return [...keys].sort();
}
function contextCompletionPrefix(text, offset) {
    const beforeCursor = text.slice(0, offset);
    const openingTag = beforeCursor.lastIndexOf('<ctx>');
    if (openingTag < 0 || beforeCursor.slice(openingTag).includes('</ctx>')) {
        return undefined;
    }
    const prefix = beforeCursor.slice(openingTag + '<ctx>'.length);
    return /^[\w.]*$/.test(prefix) ? prefix : undefined;
}
function shouldCloseContextTag(text, offset) {
    return text.slice(Math.max(0, offset - 5), offset) === '<ctx>'
        && !text.slice(offset).startsWith('</ctx>');
}
function defaultPamd() {
    return {
        cells: [
            { cell_type: 'markdown', source: '# Document Title\n\nWrite your markdown here...\n' },
            {
                cell_type: 'code',
                source: 'import pamd_helpers\n\ndef context():\n    return {\n        \n    }\n'
            }
        ]
    };
}
function normalizePamd(value, uri) {
    if (!value || typeof value !== 'object' || !Array.isArray(value.cells)) {
        throw new Error(`Invalid PAMD file: ${uri.fsPath} must contain a cells array.`);
    }
    let markdownCount = 0;
    const cells = value.cells.map((cell, index) => {
        if (!cell || !['code', 'markdown'].includes(cell.cell_type)) {
            throw new Error(`Invalid PAMD file: cell ${index} must be code or markdown.`);
        }
        if (typeof cell.source !== 'string' &&
            (!Array.isArray(cell.source) || !cell.source.every(line => typeof line === 'string'))) {
            throw new Error(`Invalid PAMD file: cell ${index} source must be a string or string array.`);
        }
        if (cell.cell_type === 'markdown') {
            markdownCount++;
        }
        return {
            cell_type: cell.cell_type,
            source: Array.isArray(cell.source) ? cell.source.join('') : cell.source
        };
    });
    if (markdownCount !== 1) {
        throw new Error(`Invalid PAMD file: expected exactly one markdown cell, found ${markdownCount}.`);
    }
    return { cells };
}
function parsePamd(text, uri) {
    return text.trim() ? normalizePamd(JSON.parse(text), uri) : defaultPamd();
}
function serializePamd(pamd) {
    return JSON.stringify({
        cells: pamd.cells.map(cell => ({
            cell_type: cell.cell_type,
            source: String(cell.source).split(/(?<=\n)/g)
        }))
    }, null, 2);
}
// Monaco (Monarch) token name -> candidate TextMate scopes, most specific first.
// The first candidate that the theme actually colours is used.
const PAMD_TOKEN_SCOPES = {
    'keyword': ['keyword.control.flow.python', 'keyword.control', 'keyword'],
    'constant': ['constant.language.python', 'constant.language', 'constant'],
    'variable': ['variable.other.readwrite.python', 'variable', 'meta.definition.variable.name', 'support.variable', 'entity.name.variable'],
    'variable.language': ['variable.language.special.self.python', 'variable.language', 'variable.parameter'],
    'function': ['entity.name.function.python', 'entity.name.function', 'support.function'],
    'class-name': ['entity.name.type.class.python', 'entity.name.class', 'entity.name.type', 'support.class'],
    'annotation': ['entity.name.function.decorator.python', 'meta.function.decorator', 'entity.name.function'],
    'namespace': ['entity.name.namespace.python', 'entity.name.namespace', 'entity.name.type.module', 'entity.name.type'],
    'import-name': ['variable.other.readwrite.python', 'variable', 'entity.name.variable'],
    'number': ['constant.numeric.python', 'constant.numeric', 'constant'],
    'string': ['string.quoted.double.python', 'string.quoted', 'string'],
    'string.escape': ['constant.character.escape.python', 'constant.character.escape', 'constant.character'],
    'operator': ['keyword.operator.python', 'keyword.operator'],
    'delimiter': ['punctuation.separator.python', 'punctuation'],
    'comment': ['comment.line.number-sign.python', 'comment.line', 'comment'],
    'markdown-heading': ['markup.heading.markdown', 'markup.heading'],
    'markdown-quote': ['markup.quote.markdown', 'markup.quote'],
    'markdown-list': ['markup.list.unnumbered.markdown', 'markup.list.numbered.markdown', 'markup.list'],
    'markdown-code-fence': ['markup.fenced_code.block.markdown', 'markup.fenced_code'],
    'markdown-code': ['markup.inline.raw.markdown', 'markup.raw'],
    'markdown-bold': ['markup.bold.markdown', 'markup.bold'],
    'markdown-italic': ['markup.italic.markdown', 'markup.italic'],
    'markdown-link': ['string.other.link.title.markdown', 'markup.underline.link.markdown', 'markup.underline.link'],
    'markdown-entity': ['constant.character.entity.html', 'constant.character.entity'],
    'pamd-tag': ['entity.name.tag.pamd', 'punctuation.definition.tag.pamd', 'entity.name.tag'],
    'pamd-tag-content': ['entity.name.tag.pamd.content', 'string.unquoted.pamd', 'entity.name.tag'],
    'pamd-control': ['entity.name.tag.pamd', 'entity.name.tag']
};
function stripJsonComments(text) {
    let out = '';
    let inString = false;
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        const next = text[i + 1];
        if (inString) {
            out += c;
            if (c === '\\') {
                out += next ?? '';
                i++;
            }
            else if (c === '"') {
                inString = false;
            }
            continue;
        }
        if (c === '"') {
            inString = true;
            out += c;
        }
        else if (c === '/' && next === '/') {
            while (i < text.length && text[i] !== '\n') {
                i++;
            }
            out += '\n';
        }
        else if (c === '/' && next === '*') {
            i += 2;
            while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) {
                i++;
            }
            i++;
        }
        else {
            out += c;
        }
    }
    return out.replace(/,(\s*[}\]])/g, '$1');
}
function toTokenRule(entry) {
    const raw = entry?.scope;
    const list = Array.isArray(raw) ? raw : typeof raw === 'string' ? raw.split(',') : [];
    const scopes = list
        .filter((s) => typeof s === 'string')
        .map(s => s.trim())
        .filter(s => s && !/\s/.test(s));
    if (!scopes.length) {
        return undefined;
    }
    const settings = entry.settings ?? {};
    return {
        scopes,
        foreground: typeof settings.foreground === 'string' ? settings.foreground : undefined,
        fontStyle: typeof settings.fontStyle === 'string' ? settings.fontStyle : undefined
    };
}
async function readThemeRules(file, depth = 0) {
    if (depth > 5) {
        return [];
    }
    const json = JSON.parse(stripJsonComments(await fs_1.promises.readFile(file, 'utf8')));
    const rules = [];
    if (typeof json.include === 'string') {
        rules.push(...await readThemeRules(path.resolve(path.dirname(file), json.include), depth + 1));
    }
    if (Array.isArray(json.tokenColors)) {
        for (const entry of json.tokenColors) {
            const rule = toTokenRule(entry);
            if (rule) {
                rules.push(rule);
            }
        }
    }
    return rules;
}
function activeThemeLabel() {
    const workbench = vscode.workspace.getConfiguration('workbench');
    if (workbench.get('autoDetectColorScheme')) {
        const kind = vscode.window.activeColorTheme.kind;
        const key = kind === vscode.ColorThemeKind.Light ? 'preferredLightColorTheme'
            : kind === vscode.ColorThemeKind.HighContrast ? 'preferredHighContrastColorTheme'
                : kind === vscode.ColorThemeKind.HighContrastLight ? 'preferredHighContrastLightColorTheme'
                    : 'preferredDarkColorTheme';
        const preferred = workbench.get(key);
        if (preferred) {
            return preferred;
        }
    }
    return workbench.get('colorTheme');
}
function findThemeFile(label) {
    for (const extension of vscode.extensions.all) {
        const themes = extension.packageJSON?.contributes?.themes ?? [];
        const match = themes.find(theme => theme.label === label || theme.id === label);
        if (match && typeof match.path === 'string') {
            return path.join(extension.extensionPath, match.path);
        }
    }
    return undefined;
}
function customizationRules(label) {
    const config = vscode.workspace.getConfiguration('editor').get('tokenColorCustomizations') ?? {};
    const layers = [config];
    if (label) {
        for (const [key, value] of Object.entries(config)) {
            if (key.startsWith('[') && key.includes(`[${label}]`) && value && typeof value === 'object') {
                layers.push(value);
            }
        }
    }
    const simple = {
        comments: 'comment',
        strings: 'string',
        keywords: 'keyword',
        numbers: 'constant.numeric',
        types: 'entity.name.type',
        functions: 'entity.name.function',
        variables: 'variable'
    };
    const rules = [];
    for (const layer of layers) {
        for (const [name, scope] of Object.entries(simple)) {
            const value = layer[name];
            if (typeof value === 'string') {
                rules.push({ scopes: [scope], foreground: value });
            }
            else if (value && typeof value === 'object') {
                rules.push({ scopes: [scope], foreground: value.foreground, fontStyle: value.fontStyle });
            }
        }
        if (Array.isArray(layer.textMateRules)) {
            for (const entry of layer.textMateRules) {
                const rule = toTokenRule(entry);
                if (rule) {
                    rules.push(rule);
                }
            }
        }
    }
    return rules;
}
function resolveScope(rules, scope) {
    let foreground;
    let fontStyle;
    for (const rule of rules) {
        for (const candidate of rule.scopes) {
            if (scope !== candidate && !scope.startsWith(candidate + '.')) {
                continue;
            }
            // Longer (more specific) scope wins; on a tie the later rule wins.
            if (rule.foreground !== undefined && (!foreground || candidate.length >= foreground.length)) {
                foreground = { length: candidate.length, value: rule.foreground };
            }
            if (rule.fontStyle !== undefined && (!fontStyle || candidate.length >= fontStyle.length)) {
                fontStyle = { length: candidate.length, value: rule.fontStyle };
            }
        }
    }
    return { foreground: foreground?.value, fontStyle: fontStyle?.value };
}
async function resolveTokenPalette() {
    const label = activeThemeLabel();
    let rules = [];
    try {
        const file = label ? findThemeFile(label) : undefined;
        if (file) {
            rules = await readThemeRules(file);
        }
    }
    catch {
        rules = [];
    }
    rules.push(...customizationRules(label));
    console.log(`[PAMD] colour theme "${label}": ${rules.length} token rules resolved`);
    if (!rules.length) {
        return undefined;
    }
    const palette = {};
    for (const [token, scopes] of Object.entries(PAMD_TOKEN_SCOPES)) {
        let entry = {};
        for (const scope of scopes) {
            const resolved = resolveScope(rules, scope);
            if (resolved.foreground) {
                entry = resolved;
                break;
            }
        }
        palette[token] = entry;
    }
    return palette;
}
class PamdCustomEditorProvider {
    extensionPath;
    constructor(extensionPath) {
        this.extensionPath = extensionPath;
    }
    async resolveCustomTextEditor(document, webviewPanel, _token) {
        activePamdUri = document.uri;
        webviewPanel.webview.options = {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(vscode.Uri.file(this.extensionPath), 'node_modules', 'monaco-editor', 'min')]
        };
        const update = () => {
            try {
                webviewPanel.webview.postMessage({ type: 'load', pamd: parsePamd(document.getText(), document.uri) });
            }
            catch (error) {
                webviewPanel.webview.postMessage({
                    type: 'error',
                    message: error instanceof Error ? error.message : String(error)
                });
            }
        };
        let ignoreNextDocumentChange = false;
        const sendTheme = async () => {
            try {
                await webviewPanel.webview.postMessage({ type: 'tokenColors', palette: await resolveTokenPalette() });
            }
            catch {
                // panel was disposed while the theme was being resolved
            }
        };
        const themeSubscriptions = [
            vscode.window.onDidChangeActiveColorTheme(() => void sendTheme()),
            vscode.workspace.onDidChangeConfiguration(event => {
                if (event.affectsConfiguration('workbench') || event.affectsConfiguration('editor.tokenColorCustomizations')) {
                    void sendTheme();
                }
            })
        ];
        webviewPanel.onDidDispose(() => themeSubscriptions.forEach(subscription => subscription.dispose()));
        webviewPanel.webview.html = (0, pamdEditorHtml_1.getMonacoHtml)(webviewPanel.webview, JSON.stringify(parsePamd(document.getText(), document.uri)).replace(/</g, '\\u003c'), vscode.workspace.getConfiguration('pyact').get('showToolbar', true), this.extensionPath);
        webviewPanel.onDidChangeViewState(() => {
            if (webviewPanel.active) {
                activePamdUri = document.uri;
            }
        });
        webviewPanel.onDidDispose(() => {
            if (activePamdUri?.toString() === document.uri.toString()) {
                activePamdUri = undefined;
            }
        });
        webviewPanel.webview.onDidReceiveMessage(async (message) => {
            if (message.type === 'ready') {
                await sendTheme();
                return;
            }
            if (message.type === 'update' && typeof message.text === 'string') {
                ignoreNextDocumentChange = document.getText() !== message.text;
                const edit = new vscode.WorkspaceEdit();
                edit.replace(document.uri, new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length)), message.text);
                const applied = await vscode.workspace.applyEdit(edit);
                if (!applied) {
                    ignoreNextDocumentChange = false;
                }
                return;
            }
            if (message.type === 'action' && typeof message.action === 'string') {
                await vscode.commands.executeCommand(`pamd.${message.action}`, document.uri);
            }
        });
        const changeSubscription = vscode.workspace.onDidChangeTextDocument(event => {
            if (event.document.uri.toString() !== document.uri.toString()) {
                return;
            }
            if (ignoreNextDocumentChange) {
                ignoreNextDocumentChange = false;
                return;
            }
            update();
        });
        webviewPanel.onDidDispose(() => changeSubscription.dispose());
        update();
    }
}
exports.PamdCustomEditorProvider = PamdCustomEditorProvider;
function createPyActCommand(pythonPath, args, cwd) {
    return { command: pythonPath, args: ['-m', 'pyact.cli', ...args], cwd };
}
function runCommand(command) {
    return new Promise((resolve, reject) => {
        const child = (0, child_process_1.spawn)(command.command, command.args, { cwd: command.cwd, shell: false, windowsHide: true });
        let stdout = '';
        let stderr = '';
        child.stdout.on('data', data => stdout += data.toString());
        child.stderr.on('data', data => stderr += data.toString());
        child.on('error', reject);
        child.on('close', code => resolve({ exitCode: code ?? 1, stdout, stderr }));
    });
}
function currentPamdUri(uri) {
    return uri?.fsPath.endsWith('.pamd') ? uri : activePamdUri;
}
function outputPath(pamdPath, extension) {
    const configured = vscode.workspace.getConfiguration('pyact').get('outputDirectory', '');
    const directory = configured ? path.resolve(path.dirname(pamdPath), configured) : path.dirname(pamdPath);
    return path.join(directory, `${path.basename(pamdPath, '.pamd')}.${extension}`);
}
function pythonPath() {
    return vscode.workspace.getConfiguration('pyact').get('pythonPath', 'python');
}
function projectCwd(pamdPath) {
    return vscode.workspace.getWorkspaceFolder(vscode.Uri.file(pamdPath))?.uri.fsPath ?? path.dirname(pamdPath);
}
function updateDiagnostics(uri, result) {
    if (result.exitCode === 0) {
        diagnosticCollection.delete(uri);
        return;
    }
    const message = (result.stderr || result.stdout || 'PyAct command failed').trim();
    const diagnostics = message.split(/\r?\n/).filter(Boolean).map(line => {
        const match = line.match(/(?:line\s+)?(\d+)(?::(\d+))?/i);
        const lineNumber = match ? Math.max(0, Number(match[1]) - 1) : 0;
        const column = match?.[2] ? Math.max(0, Number(match[2]) - 1) : 0;
        return new vscode.Diagnostic(new vscode.Range(lineNumber, column, lineNumber, column + 1), line, vscode.DiagnosticSeverity.Error);
    });
    diagnosticCollection.set(uri, diagnostics);
}
async function compile(uri, docx, noCache = false) {
    const document = await vscode.workspace.openTextDocument(uri);
    await document.save();
    const args = [uri.fsPath, '-o', outputPath(uri.fsPath, 'md')];
    if (docx) {
        args.push('--docx', outputPath(uri.fsPath, 'docx'));
    }
    if (noCache) {
        args.push('--no-cache');
    }
    const result = await runCommand(createPyActCommand(pythonPath(), args, projectCwd(uri.fsPath)));
    updateDiagnostics(uri, result);
    return result;
}
async function showCompileResult(uri, result, preview) {
    if (result.exitCode !== 0) {
        vscode.window.showErrorMessage(`PyAct compilation failed: ${result.stderr || result.stdout}`);
        return;
    }
    vscode.window.showInformationMessage(`PyAct compiled ${path.basename(uri.fsPath)}.`);
    if (preview && vscode.workspace.getConfiguration('pyact').get('autoPreview', true)) {
        await vscode.commands.executeCommand('markdown.showPreviewToSide', vscode.Uri.file(outputPath(uri.fsPath, 'md')));
    }
}
async function runCompileCommand(uri, docx, noCache = false) {
    const pamdUri = currentPamdUri(uri);
    if (!pamdUri) {
        vscode.window.showErrorMessage('No active PAMD file found.');
        return;
    }
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: docx ? 'Exporting PAMD to DOCX' : 'Compiling PAMD' }, async () => showCompileResult(pamdUri, await compile(pamdUri, docx, noCache), !docx));
}
async function runLint(uri) {
    const pamdUri = currentPamdUri(uri);
    if (!pamdUri) {
        vscode.window.showErrorMessage('No active PAMD file found.');
        return;
    }
    const result = await runCommand(createPyActCommand(pythonPath(), [pamdUri.fsPath, '--lint'], projectCwd(pamdUri.fsPath)));
    updateDiagnostics(pamdUri, result);
    const output = vscode.window.createOutputChannel('PyAct');
    output.clear();
    output.append(result.stdout || result.stderr);
    output.show(true);
    if (result.exitCode !== 0) {
        vscode.window.showErrorMessage('PyAct linting failed.');
    }
    else {
        vscode.window.showInformationMessage('PyAct linting complete.');
    }
}
async function clearCache(uri) {
    const pamdUri = currentPamdUri(uri);
    if (!pamdUri) {
        vscode.window.showErrorMessage('No active PAMD file found.');
        return;
    }
    await fs_1.promises.rm(path.join(path.dirname(pamdUri.fsPath), '.pamd-cache'), { recursive: true, force: true });
    vscode.window.showInformationMessage('PyAct cache cleared.');
}
async function showPyActActions(uri) {
    const action = await vscode.window.showQuickPick([
        { label: '$(markdown)  Compile Markdown', command: 'pamd.compileMarkdown' },
        { label: '$(sync)  Compile Markdown (No Cache)', command: 'pamd.compileNoCache' },
        { label: '$(export)  Export to Word (.docx)', command: 'pamd.generateDocx' },
        { label: '$(check)  Lint PAMD Project', command: 'pamd.lint' },
        { label: '$(clear-all)  Clear PAMD Cache', command: 'pamd.clearCache' }
    ], { placeHolder: 'Choose a PyAct action' });
    if (action) {
        await vscode.commands.executeCommand(action.command, uri);
    }
}
function activate(context) {
    context.subscriptions.push(diagnosticCollection);
    context.subscriptions.push(vscode.window.registerCustomEditorProvider('pamd-editor', new PamdCustomEditorProvider(context.extensionPath), { webviewOptions: { retainContextWhenHidden: true }, supportsMultipleEditorsPerDocument: false }));
    context.subscriptions.push(vscode.commands.registerCommand('pamd.actions', (uri) => showPyActActions(uri)), vscode.commands.registerCommand('pamd.compileMarkdown', (uri) => runCompileCommand(uri, false)), vscode.commands.registerCommand('pamd.compileNoCache', (uri) => runCompileCommand(uri, false, true)), vscode.commands.registerCommand('pamd.generateDocx', (uri) => runCompileCommand(uri, true)), vscode.commands.registerCommand('pamd.lint', (uri) => runLint(uri)), vscode.commands.registerCommand('pamd.clearCache', (uri) => clearCache(uri)));
}
function deactivate() {
    diagnosticCollection.dispose();
}
function getNonce() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 32; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}
//# sourceMappingURL=extension.js.map