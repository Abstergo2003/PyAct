import { getMonacoHtml } from './pamdEditorHtml';
import * as vscode from 'vscode';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';

interface RawPamd {
	cells: RawCell[];
}

interface RawCell {
	cell_type: 'code' | 'markdown';
	source: string[] | string;
}

interface CommandResult {
	exitCode: number;
	stdout: string;
	stderr: string;
}

export interface PyActCommand {
	command: string;
	args: string[];
	cwd: string;
}

const diagnosticCollection = vscode.languages.createDiagnosticCollection('pamd');
let activePamdUri: vscode.Uri | undefined;

export function extractContextKeys(code: string): string[] {
	const contextStart = code.search(/\bdef\s+context\s*\([^)]*\)\s*:/);
	if (contextStart < 0) {return [];}
	const body = code.slice(contextStart).replace(/^\s*def\s+\w+\s*\([^)]*\)\s*:/m, '');
	const returnObject = body.match(/\breturn\s*{/);
	if (!returnObject || returnObject.index === undefined) {return [];}
	const keys = new Set<string>();

	const parseObject = (openBrace: number, prefix: string): number => {
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
				while (/\s/.test(body[index] ?? '')) {index++;}
				if (body[index] !== ':') {continue;}
				index++;
				while (/\s/.test(body[index] ?? '')) {index++;}
				const fullKey = prefix ? `${prefix}.${key}` : key;
				keys.add(fullKey);
				if (body[index] === '{') {index = parseObject(index, fullKey);}
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

export function contextCompletionPrefix(text: string, offset: number): string | undefined {
	const beforeCursor = text.slice(0, offset);
	const openingTag = beforeCursor.lastIndexOf('<ctx>');
	if (openingTag < 0 || beforeCursor.slice(openingTag).includes('</ctx>')) {return undefined;}
	const prefix = beforeCursor.slice(openingTag + '<ctx>'.length);
	return /^[\w.]*$/.test(prefix) ? prefix : undefined;
}

export function shouldCloseContextTag(text: string, offset: number): boolean {
	return text.slice(Math.max(0, offset - 5), offset) === '<ctx>'
		&& !text.slice(offset).startsWith('</ctx>');
}

function defaultPamd(): RawPamd {
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

function normalizePamd(value: unknown, uri: vscode.Uri): RawPamd {
	if (!value || typeof value !== 'object' || !Array.isArray((value as RawPamd).cells)) {
		throw new Error(`Invalid PAMD file: ${uri.fsPath} must contain a cells array.`);
	}
	let markdownCount = 0;
	const cells = (value as RawPamd).cells.map((cell, index) => {
		if (!cell || !['code', 'markdown'].includes(cell.cell_type)) {
			throw new Error(`Invalid PAMD file: cell ${index} must be code or markdown.`);
		}
		if (
			typeof cell.source !== 'string' &&
			(!Array.isArray(cell.source) || !cell.source.every(line => typeof line === 'string'))
		) {
			throw new Error(`Invalid PAMD file: cell ${index} source must be a string or string array.`);
		}
		if (cell.cell_type === 'markdown') {markdownCount++;}
		return {
			cell_type: cell.cell_type,
			source: Array.isArray(cell.source) ? cell.source.join('') : cell.source
		} as RawCell;
	});
	if (markdownCount !== 1) {
		throw new Error(`Invalid PAMD file: expected exactly one markdown cell, found ${markdownCount}.`);
	}
	return { cells };
}

function parsePamd(text: string, uri: vscode.Uri): RawPamd {
	return text.trim() ? normalizePamd(JSON.parse(text), uri) : defaultPamd();
}

function serializePamd(pamd: RawPamd): string {
	return JSON.stringify({
		cells: pamd.cells.map(cell => ({
			cell_type: cell.cell_type,
			source: String(cell.source).split(/(?<=\n)/g)
		}))
	}, null, 2);
}

// ---------------------------------------------------------------------------
// Theme integration: resolve the active VS Code theme's TextMate token colors
// so the Monaco cells look like the user's normal Python editor.
// ---------------------------------------------------------------------------

interface TokenRule {
	scopes: string[];
	foreground?: string;
	fontStyle?: string;
}

interface PaletteEntry {
	foreground?: string;
	fontStyle?: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = Record<string, any>;

// Monaco (Monarch) token name -> candidate TextMate scopes, most specific first.
// The first candidate that the theme actually colours is used.
const PAMD_TOKEN_SCOPES: Record<string, string[]> = {
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

function stripJsonComments(text: string): string {
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
			} else if (c === '"') {
				inString = false;
			}
			continue;
		}
		if (c === '"') {
			inString = true;
			out += c;
		} else if (c === '/' && next === '/') {
			while (i < text.length && text[i] !== '\n') {i++;}
			out += '\n';
		} else if (c === '/' && next === '*') {
			i += 2;
			while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) {i++;}
			i++;
		} else {
			out += c;
		}
	}
	return out.replace(/,(\s*[}\]])/g, '$1');
}

function toTokenRule(entry: Json): TokenRule | undefined {
	const raw = entry?.scope;
	const list: unknown[] = Array.isArray(raw) ? raw : typeof raw === 'string' ? raw.split(',') : [];
	const scopes = list
		.filter((s): s is string => typeof s === 'string')
		.map(s => s.trim())
		.filter(s => s && !/\s/.test(s));
	if (!scopes.length) {return undefined;}
	const settings: Json = entry.settings ?? {};
	return {
		scopes,
		foreground: typeof settings.foreground === 'string' ? settings.foreground : undefined,
		fontStyle: typeof settings.fontStyle === 'string' ? settings.fontStyle : undefined
	};
}

async function readThemeRules(file: string, depth = 0): Promise<TokenRule[]> {
	if (depth > 5) {return [];}
	const json: Json = JSON.parse(stripJsonComments(await fs.readFile(file, 'utf8')));
	const rules: TokenRule[] = [];
	if (typeof json.include === 'string') {
		rules.push(...await readThemeRules(path.resolve(path.dirname(file), json.include), depth + 1));
	}
	if (Array.isArray(json.tokenColors)) {
		for (const entry of json.tokenColors) {
			const rule = toTokenRule(entry);
			if (rule) {rules.push(rule);}
		}
	}
	return rules;
}

function activeThemeLabel(): string | undefined {
	const workbench = vscode.workspace.getConfiguration('workbench');
	if (workbench.get<boolean>('autoDetectColorScheme')) {
		const kind = vscode.window.activeColorTheme.kind;
		const key = kind === vscode.ColorThemeKind.Light ? 'preferredLightColorTheme'
			: kind === vscode.ColorThemeKind.HighContrast ? 'preferredHighContrastColorTheme'
			: kind === vscode.ColorThemeKind.HighContrastLight ? 'preferredHighContrastLightColorTheme'
			: 'preferredDarkColorTheme';
		const preferred = workbench.get<string>(key);
		if (preferred) {return preferred;}
	}
	return workbench.get<string>('colorTheme');
}

function findThemeFile(label: string): string | undefined {
	for (const extension of vscode.extensions.all) {
		const themes: Json[] = extension.packageJSON?.contributes?.themes ?? [];
		const match = themes.find(theme => theme.label === label || theme.id === label);
		if (match && typeof match.path === 'string') {
			return path.join(extension.extensionPath, match.path);
		}
	}
	return undefined;
}

function customizationRules(label: string | undefined): TokenRule[] {
	const config = vscode.workspace.getConfiguration('editor').get<Json>('tokenColorCustomizations') ?? {};
	const layers: Json[] = [config];
	if (label) {
		for (const [key, value] of Object.entries(config)) {
			if (key.startsWith('[') && key.includes(`[${label}]`) && value && typeof value === 'object') {
				layers.push(value as Json);
			}
		}
	}
	const simple: Record<string, string> = {
		comments: 'comment',
		strings: 'string',
		keywords: 'keyword',
		numbers: 'constant.numeric',
		types: 'entity.name.type',
		functions: 'entity.name.function',
		variables: 'variable'
	};
	const rules: TokenRule[] = [];
	for (const layer of layers) {
		for (const [name, scope] of Object.entries(simple)) {
			const value = layer[name];
			if (typeof value === 'string') {
				rules.push({ scopes: [scope], foreground: value });
			} else if (value && typeof value === 'object') {
				rules.push({ scopes: [scope], foreground: value.foreground, fontStyle: value.fontStyle });
			}
		}
		if (Array.isArray(layer.textMateRules)) {
			for (const entry of layer.textMateRules) {
				const rule = toTokenRule(entry);
				if (rule) {rules.push(rule);}
			}
		}
	}
	return rules;
}

function resolveScope(rules: TokenRule[], scope: string): PaletteEntry {
	let foreground: { length: number; value: string } | undefined;
	let fontStyle: { length: number; value: string } | undefined;
	for (const rule of rules) {
		for (const candidate of rule.scopes) {
			if (scope !== candidate && !scope.startsWith(candidate + '.')) {continue;}
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

async function resolveTokenPalette(): Promise<Record<string, PaletteEntry> | undefined> {
	const label = activeThemeLabel();
	let rules: TokenRule[] = [];
	try {
		const file = label ? findThemeFile(label) : undefined;
		if (file) {rules = await readThemeRules(file);}
	} catch {
		rules = [];
	}
	rules.push(...customizationRules(label));
	console.log(`[PAMD] colour theme "${label}": ${rules.length} token rules resolved`);
	if (!rules.length) {return undefined;}
	const palette: Record<string, PaletteEntry> = {};
	for (const [token, scopes] of Object.entries(PAMD_TOKEN_SCOPES)) {
		let entry: PaletteEntry = {};
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

export class PamdCustomEditorProvider implements vscode.CustomTextEditorProvider {
	constructor(private readonly extensionPath: string) {}

	async resolveCustomTextEditor(
		document: vscode.TextDocument,
		webviewPanel: vscode.WebviewPanel,
		_token: vscode.CancellationToken
	): Promise<void> {
		activePamdUri = document.uri;
		webviewPanel.webview.options = {
			enableScripts: true,
			localResourceRoots: [vscode.Uri.joinPath(vscode.Uri.file(this.extensionPath), 'node_modules', 'monaco-editor', 'min')]
		};
		const update = () => {
			try {
				webviewPanel.webview.postMessage({ type: 'load', pamd: parsePamd(document.getText(), document.uri) });
			} catch (error) {
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
			} catch {
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
		webviewPanel.webview.html = getMonacoHtml(
			webviewPanel.webview,
			JSON.stringify(parsePamd(document.getText(), document.uri)).replace(/</g, '\\u003c'),
			vscode.workspace.getConfiguration('pyact').get<boolean>('showToolbar', true),
			this.extensionPath
		);
		webviewPanel.onDidChangeViewState(() => {
			if (webviewPanel.active) {activePamdUri = document.uri;}
		});
		webviewPanel.onDidDispose(() => {
			if (activePamdUri?.toString() === document.uri.toString()) {activePamdUri = undefined;}
		});
		webviewPanel.webview.onDidReceiveMessage(async message => {
			if (message.type === 'ready') {
				await sendTheme();
				return;
			}
			if (message.type === 'update' && typeof message.text === 'string') {
				ignoreNextDocumentChange = document.getText() !== message.text;
				const edit = new vscode.WorkspaceEdit();
				edit.replace(document.uri, new vscode.Range(
					document.positionAt(0),
					document.positionAt(document.getText().length)
				), message.text);
				const applied = await vscode.workspace.applyEdit(edit);
				if (!applied) {ignoreNextDocumentChange = false;}
				return;
			}
			if (message.type === 'action' && typeof message.action === 'string') {
				await vscode.commands.executeCommand(`pamd.${message.action}`, document.uri);
			}
		});
		const changeSubscription = vscode.workspace.onDidChangeTextDocument(event => {
			if (event.document.uri.toString() !== document.uri.toString()) {return;}
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



export function createPyActCommand(pythonPath: string, args: string[], cwd: string): PyActCommand {
	return { command: pythonPath, args: ['-m', 'pyact.cli', ...args], cwd };
}

function runCommand(command: PyActCommand): Promise<CommandResult> {
	return new Promise((resolve, reject) => {
		const child = spawn(command.command, command.args, { cwd: command.cwd, shell: false, windowsHide: true });
		let stdout = '';
		let stderr = '';
		child.stdout.on('data', data => stdout += data.toString());
		child.stderr.on('data', data => stderr += data.toString());
		child.on('error', reject);
		child.on('close', code => resolve({ exitCode: code ?? 1, stdout, stderr }));
	});
}

function currentPamdUri(uri?: vscode.Uri): vscode.Uri | undefined {
	return uri?.fsPath.endsWith('.pamd') ? uri : activePamdUri;
}

function outputPath(pamdPath: string, extension: string): string {
	const configured = vscode.workspace.getConfiguration('pyact').get<string>('outputDirectory', '');
	const directory = configured ? path.resolve(path.dirname(pamdPath), configured) : path.dirname(pamdPath);
	return path.join(directory, `${path.basename(pamdPath, '.pamd')}.${extension}`);
}

function pythonPath(): string {
	return vscode.workspace.getConfiguration('pyact').get<string>('pythonPath', 'python');
}

function projectCwd(pamdPath: string): string {
	return vscode.workspace.getWorkspaceFolder(vscode.Uri.file(pamdPath))?.uri.fsPath ?? path.dirname(pamdPath);
}

function updateDiagnostics(uri: vscode.Uri, result: CommandResult): void {
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

async function compile(uri: vscode.Uri, docx: boolean, noCache = false): Promise<CommandResult> {
	const document = await vscode.workspace.openTextDocument(uri);
	await document.save();
	const args = [uri.fsPath, '-o', outputPath(uri.fsPath, 'md')];
	if (docx) {args.push('--docx', outputPath(uri.fsPath, 'docx'));}
	if (noCache) {args.push('--no-cache');}
	const result = await runCommand(createPyActCommand(pythonPath(), args, projectCwd(uri.fsPath)));
	updateDiagnostics(uri, result);
	return result;
}

async function showCompileResult(uri: vscode.Uri, result: CommandResult, preview: boolean): Promise<void> {
	if (result.exitCode !== 0) {
		vscode.window.showErrorMessage(`PyAct compilation failed: ${result.stderr || result.stdout}`);
		return;
	}
	vscode.window.showInformationMessage(`PyAct compiled ${path.basename(uri.fsPath)}.`);
	if (preview && vscode.workspace.getConfiguration('pyact').get<boolean>('autoPreview', true)) {
		await vscode.commands.executeCommand('markdown.showPreviewToSide', vscode.Uri.file(outputPath(uri.fsPath, 'md')));
	}
}

async function runCompileCommand(uri: vscode.Uri | undefined, docx: boolean, noCache = false): Promise<void> {
	const pamdUri = currentPamdUri(uri);
	if (!pamdUri) {
		vscode.window.showErrorMessage('No active PAMD file found.');
		return;
	}
	await vscode.window.withProgress(
		{ location: vscode.ProgressLocation.Notification, title: docx ? 'Exporting PAMD to DOCX' : 'Compiling PAMD' },
		async () => showCompileResult(pamdUri, await compile(pamdUri, docx, noCache), !docx)
	);
}

async function runLint(uri?: vscode.Uri): Promise<void> {
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
	if (result.exitCode !== 0) {vscode.window.showErrorMessage('PyAct linting failed.');}
	else {vscode.window.showInformationMessage('PyAct linting complete.');}
}

async function clearCache(uri?: vscode.Uri): Promise<void> {
	const pamdUri = currentPamdUri(uri);
	if (!pamdUri) {
		vscode.window.showErrorMessage('No active PAMD file found.');
		return;
	}
	await fs.rm(path.join(path.dirname(pamdUri.fsPath), '.pamd-cache'), { recursive: true, force: true });
	vscode.window.showInformationMessage('PyAct cache cleared.');
}

async function showPyActActions(uri?: vscode.Uri): Promise<void> {
	const action = await vscode.window.showQuickPick([
		{ label: '$(markdown)  Compile Markdown', command: 'pamd.compileMarkdown' },
		{ label: '$(sync)  Compile Markdown (No Cache)', command: 'pamd.compileNoCache' },
		{ label: '$(export)  Export to Word (.docx)', command: 'pamd.generateDocx' },
		{ label: '$(check)  Lint PAMD Project', command: 'pamd.lint' },
		{ label: '$(clear-all)  Clear PAMD Cache', command: 'pamd.clearCache' }
	], { placeHolder: 'Choose a PyAct action' });
	if (action) {await vscode.commands.executeCommand(action.command, uri);}
}

export function activate(context: vscode.ExtensionContext): void {
	context.subscriptions.push(diagnosticCollection);
	context.subscriptions.push(vscode.window.registerCustomEditorProvider(
		'pamd-editor',
		new PamdCustomEditorProvider(context.extensionPath),
		{ webviewOptions: { retainContextWhenHidden: true }, supportsMultipleEditorsPerDocument: false }
	));
	context.subscriptions.push(
		vscode.commands.registerCommand('pamd.actions', (uri?: vscode.Uri) => showPyActActions(uri)),
		vscode.commands.registerCommand('pamd.compileMarkdown', (uri?: vscode.Uri) => runCompileCommand(uri, false)),
		vscode.commands.registerCommand('pamd.compileNoCache', (uri?: vscode.Uri) => runCompileCommand(uri, false, true)),
		vscode.commands.registerCommand('pamd.generateDocx', (uri?: vscode.Uri) => runCompileCommand(uri, true)),
		vscode.commands.registerCommand('pamd.lint', (uri?: vscode.Uri) => runLint(uri)),
		vscode.commands.registerCommand('pamd.clearCache', (uri?: vscode.Uri) => clearCache(uri))
	);
}

export function deactivate(): void {
	diagnosticCollection.dispose();
}

function getNonce(): string {
	const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	let result = '';
	for (let i = 0; i < 32; i++) {result += chars.charAt(Math.floor(Math.random() * chars.length));}
	return result;
}