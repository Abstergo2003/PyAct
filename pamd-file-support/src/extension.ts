import * as vscode from 'vscode';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';
import { TextDecoder, TextEncoder } from 'util';

interface RawNotebook {
	cells: RawNotebookCell[];
}

interface RawNotebookCell {
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

export function extractContextKeys(code: string): string[] {
	const contextStart = code.search(/\bdef\s+context\s*\([^)]*\)\s*:/);
	if (contextStart < 0) {
		return [];
	}
	const body = code.slice(contextStart).replace(/^\s*def\s+\w+\s*\([^)]*\)\s*:/m, '');
	const keys = new Set<string>();
	const returnObject = body.match(/\breturn\s*{/);
	if (!returnObject || returnObject.index === undefined) {
		return [];
	}

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

export function contextCompletionPrefix(text: string, offset: number): string | undefined {
	const beforeCursor = text.slice(0, offset);
	const openingTag = beforeCursor.lastIndexOf('<ctx>');
	if (openingTag < 0 || beforeCursor.slice(openingTag).includes('</ctx>')) {
		return undefined;
	}
	const prefix = beforeCursor.slice(openingTag + '<ctx>'.length);
	return /^[\w.]*$/.test(prefix) ? prefix : undefined;
}

export function shouldCloseContextTag(text: string, offset: number): boolean {
	return text.slice(Math.max(0, offset - '<ctx>'.length), offset) === '<ctx>'
		&& !text.slice(offset).startsWith('</ctx>');
}

const diagnosticCollection = vscode.languages.createDiagnosticCollection('pamd');

function defaultNotebook(): RawNotebook {
	return {
		cells: [
			{
				cell_type: 'markdown',
				source: ['# Document Title\n', '\n', 'Write your markdown here...\n']
			},
			{
				cell_type: 'code',
				source: [
					'import pamd_helpers\n',
					'\n',
					'def context():\n',
					'    return {\n',
					'        \n',
					'    }\n'
				]
			}
		]
	};
}

function normalizeNotebook(raw: unknown, uri: vscode.Uri): RawNotebook {
	if (!raw || typeof raw !== 'object' || !Array.isArray((raw as RawNotebook).cells)) {
		throw new Error(`Invalid PAMD file: ${uri.fsPath} must contain a cells array.`);
	}

	const cells = (raw as RawNotebook).cells;
	let markdownCount = 0;
	const normalized = cells.map((cell, index) => {
		if (!cell || !['code', 'markdown'].includes(cell.cell_type)) {
			throw new Error(`Invalid PAMD file: cell ${index} must be code or markdown.`);
		}
		if (
			typeof cell.source !== 'string' &&
			(!Array.isArray(cell.source) || !cell.source.every(line => typeof line === 'string'))
		) {
			throw new Error(`Invalid PAMD file: cell ${index} source must be a string or string array.`);
		}
		if (cell.cell_type === 'markdown') {
			markdownCount++;
		}
		return {
			cell_type: cell.cell_type,
			source: Array.isArray(cell.source) ? cell.source.join('') : cell.source
		} as RawNotebookCell;
	});

	if (markdownCount !== 1) {
		throw new Error(`Invalid PAMD file: expected exactly one markdown cell, found ${markdownCount}.`);
	}
	return { cells: normalized };
}

export class PamdNotebookSerializer implements vscode.NotebookSerializer {
	async deserializeNotebook(content: Uint8Array, _token: vscode.CancellationToken): Promise<vscode.NotebookData> {
		const contents = new TextDecoder().decode(content);
		const raw = contents.trim() ? normalizeNotebook(JSON.parse(contents), vscode.Uri.parse('pamd')) : defaultNotebook();
		const cells = raw.cells.map(item => {
			const source = typeof item.source === 'string' ? item.source : item.source.join('');
			return new vscode.NotebookCellData(
				item.cell_type === 'code' ? vscode.NotebookCellKind.Code : vscode.NotebookCellKind.Markup,
				source,
				item.cell_type === 'code' ? 'python' : 'markdown'
			);
		});
		return new vscode.NotebookData(cells);
	}

	async serializeNotebook(data: vscode.NotebookData, _token: vscode.CancellationToken): Promise<Uint8Array> {
		const cells: RawNotebookCell[] = data.cells.map(cell => ({
			cell_type: cell.kind === vscode.NotebookCellKind.Code ? 'code' : 'markdown',
			source: cell.value.split(/(?<=\n)/g)
		}));
		return new TextEncoder().encode(JSON.stringify({ cells }, null, 2));
	}
}

export function createPyActCommand(
	pythonPath: string,
	args: string[],
	cwd: string
): PyActCommand {
	return { command: pythonPath, args: ['-m', 'pyact.cli', ...args], cwd };
}

function runCommand(command: PyActCommand): Promise<CommandResult> {
	return new Promise((resolve, reject) => {
		const child = spawn(command.command, command.args, {
			cwd: command.cwd,
			shell: false,
			windowsHide: true
		});
		let stdout = '';
		let stderr = '';
		child.stdout.on('data', data => stdout += data.toString());
		child.stderr.on('data', data => stderr += data.toString());
		child.on('error', reject);
		child.on('close', code => resolve({ exitCode: code ?? 1, stdout, stderr }));
	});
}

function currentPamdUri(uri?: vscode.Uri): vscode.Uri | undefined {
	if (uri?.fsPath.endsWith('.pamd')) {
		return uri;
	}
	const editor = vscode.window.activeNotebookEditor;
	return editor?.notebook.notebookType === 'pamd-notebook' ? editor.notebook.uri : undefined;
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
		return new vscode.Diagnostic(
			new vscode.Range(lineNumber, column, lineNumber, column + 1),
			line,
			vscode.DiagnosticSeverity.Error
		);
	});
	diagnosticCollection.set(uri, diagnostics);
}

async function saveNotebook(uri: vscode.Uri): Promise<void> {
	const editor = vscode.window.activeNotebookEditor;
	if (editor?.notebook.uri.toString() === uri.toString() && editor.notebook.isDirty) {
		await editor.notebook.save();
	}
}

async function compile(uri: vscode.Uri, docx: boolean, noCache = false): Promise<CommandResult> {
	await saveNotebook(uri);
	const pamdPath = uri.fsPath;
	const markdownPath = outputPath(pamdPath, 'md');
	await fs.mkdir(path.dirname(markdownPath), { recursive: true });
	const args = [pamdPath, '-o', markdownPath];
	if (docx) {
		args.push('--docx', outputPath(pamdPath, 'docx'));
	}
	if (noCache) {
		args.push('--no-cache');
	}
	const result = await runCommand(createPyActCommand(pythonPath(), args, projectCwd(pamdPath)));
	updateDiagnostics(uri, result);
	return result;
}

async function showCompileResult(uri: vscode.Uri, result: CommandResult, preview: boolean): Promise<void> {
	if (result.exitCode !== 0) {
		vscode.window.showErrorMessage(`PyAct compilation failed: ${result.stderr || result.stdout}`);
		return;
	}
	const mdPath = outputPath(uri.fsPath, 'md');
	vscode.window.showInformationMessage(`PyAct compiled ${path.basename(uri.fsPath)}.`);
	if (preview && vscode.workspace.getConfiguration('pyact').get<boolean>('autoPreview', true)) {
		await vscode.commands.executeCommand('markdown.showPreviewToSide', vscode.Uri.file(mdPath));
	}
}

async function runCompileCommand(uri: vscode.Uri | undefined, docx: boolean): Promise<void> {
	const pamdUri = currentPamdUri(uri);
	if (!pamdUri) {
		vscode.window.showErrorMessage('No active PAMD file found.');
		return;
	}
	await vscode.window.withProgress(
		{ location: vscode.ProgressLocation.Notification, title: docx ? 'Exporting PAMD to DOCX' : 'Compiling PAMD' },
		async () => showCompileResult(pamdUri, await compile(pamdUri, docx, false), !docx)
	);
}

async function runLint(uri: vscode.Uri | undefined): Promise<void> {
	const pamdUri = currentPamdUri(uri);
	if (!pamdUri) {
		vscode.window.showErrorMessage('No active PAMD file found.');
		return;
	}
	const result = await runCommand(createPyActCommand(
		pythonPath(),
		[pamdUri.fsPath, '--lint'],
		projectCwd(pamdUri.fsPath)
	));
	updateDiagnostics(pamdUri, result);
	const output = vscode.window.createOutputChannel('PyAct');
	output.clear();
	output.append(result.stdout || result.stderr);
	output.show(true);
	if (result.exitCode !== 0) {
		vscode.window.showErrorMessage('PyAct linting failed.');
	} else {
		vscode.window.showInformationMessage('PyAct linting complete.');
	}
}

async function clearCache(uri: vscode.Uri | undefined): Promise<void> {
	const pamdUri = currentPamdUri(uri);
	if (!pamdUri) {
		vscode.window.showErrorMessage('No active PAMD file found.');
		return;
	}
	await fs.rm(path.join(path.dirname(pamdUri.fsPath), '.pamd-cache'), { recursive: true, force: true });
	vscode.window.showInformationMessage('PyAct cache cleared.');
}

async function showPyActActions(uri: vscode.Uri | undefined): Promise<void> {
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

export function activate(context: vscode.ExtensionContext) {
	context.subscriptions.push(diagnosticCollection);
	context.subscriptions.push(
		vscode.workspace.registerNotebookSerializer('pamd-notebook', new PamdNotebookSerializer(), {
			transientOutputs: true
		})
	);
	context.subscriptions.push(
		vscode.languages.registerCompletionItemProvider(
			{ language: 'markdown', notebookType: 'pamd-notebook' },
			{
				provideCompletionItems(document, position) {
				const prefix = contextCompletionPrefix(document.getText(), document.offsetAt(position));
				if (prefix === undefined) {
					return undefined;
				}
				const notebook = vscode.workspace.notebookDocuments.find(candidate =>
					candidate.getCells().some(cell => cell.document.uri.toString() === document.uri.toString())
				);
				if (!notebook) {
					return undefined;
				}
				const code = notebook.getCells()
					.filter(cell => cell.kind === vscode.NotebookCellKind.Code)
					.map(cell => cell.document.getText())
					.join('\n');
				const wordStart = position.translate(0, -prefix.length);
				const range = new vscode.Range(wordStart, position);
				return extractContextKeys(code).map(key => {
					const item = new vscode.CompletionItem(key, vscode.CompletionItemKind.Variable);
					item.range = range;
					item.insertText = key;
					return item;
				});
				}
			},
			'<',
			'.',
			...Array.from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
		)
	);
	let closingTagEditInProgress = false;
	context.subscriptions.push(
		vscode.workspace.onDidChangeTextDocument(async event => {
			if (closingTagEditInProgress || event.document.languageId !== 'markdown') {
				return;
			}
			for (const change of event.contentChanges) {
				const insertionEnd = change.rangeOffset + change.text.length;
				if (shouldCloseContextTag(event.document.getText(), insertionEnd)) {
					const closingOffset = insertionEnd;
					closingTagEditInProgress = true;
					try {
						const edit = new vscode.WorkspaceEdit();
						edit.insert(event.document.uri, event.document.positionAt(closingOffset), '</ctx>');
						await vscode.workspace.applyEdit(edit);
						const editor = vscode.window.activeTextEditor;
						if (editor?.document.uri.toString() === event.document.uri.toString()) {
							const cursor = event.document.positionAt(closingOffset);
							editor.selection = new vscode.Selection(cursor, cursor);
						}
					} finally {
						closingTagEditInProgress = false;
					}
				}
				if (contextCompletionPrefix(event.document.getText(), insertionEnd) !== undefined) {
					setTimeout(() => {
						void vscode.commands.executeCommand('editor.action.triggerSuggest');
					}, 0);
				}
			}
		})
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('pamd.actions', (uri?: vscode.Uri) => showPyActActions(uri)),
		vscode.commands.registerCommand('pamd.compileMarkdown', (uri?: vscode.Uri) => runCompileCommand(uri, false)),
		vscode.commands.registerCommand('pamd.generateDocx', (uri?: vscode.Uri) => runCompileCommand(uri, true)),
		vscode.commands.registerCommand('pamd.lint', (uri?: vscode.Uri) => runLint(uri)),
		vscode.commands.registerCommand('pamd.clearCache', (uri?: vscode.Uri) => clearCache(uri)),
		vscode.commands.registerCommand('pamd.compileNoCache', async (uri?: vscode.Uri) => {
			const pamdUri = currentPamdUri(uri);
			if (pamdUri) {
				await showCompileResult(pamdUri, await compile(pamdUri, false, true), true);
			}
		})
	);

	context.subscriptions.push(
		vscode.window.onDidChangeActiveNotebookEditor(async editor => {
			if (editor?.notebook.notebookType !== 'pamd-notebook') {
				return;
			}
			const markdownCell = editor.notebook.getCells().findIndex(cell => cell.kind === vscode.NotebookCellKind.Markup);
			if (markdownCell >= 0) {
				editor.selections = [new vscode.NotebookRange(markdownCell, markdownCell + 1)];
			}
		})
	);
}

export function deactivate() {
	diagnosticCollection.dispose();
}
