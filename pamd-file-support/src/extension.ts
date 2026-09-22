import * as vscode from 'vscode';
import { TextDecoder, TextEncoder } from 'util';

interface RawNotebook {
	cells: RawNotebookCell[];
}

interface RawNotebookCell {
	cell_type: 'code' | 'markdown';
	source: string[] | string;
}

class PamdNotebookSerializer implements vscode.NotebookSerializer {
	async deserializeNotebook(
		content: Uint8Array,
		_token: vscode.CancellationToken
	): Promise<vscode.NotebookData> {
		var contents = new TextDecoder().decode(content);

		let raw: RawNotebook;
		try {
			raw = <RawNotebook>JSON.parse(contents);
		} catch {
			if (!contents.trim()) {
				raw = {
					cells: [
						{
							cell_type: 'markdown',
							source: [
								"# Document Title\n",
								"\n",
								"Write your markdown here...\n"
							]
						},
						{
							cell_type: 'code',
							source: [
								"import pamd_helpers\n",
								"\n",
								"def context():\n",
								"    return {\n",
								"        \n",
								"    }"
							]
						}
					]
				};
			} else {
				raw = { cells: [] };
			}
		}

		const cells = raw.cells.map(
			item => {
				const sourceStr = Array.isArray(item.source) ? item.source.join('') : item.source;
				return new vscode.NotebookCellData(
					item.cell_type === 'code' ? vscode.NotebookCellKind.Code : vscode.NotebookCellKind.Markup,
					sourceStr,
					item.cell_type === 'code' ? 'python' : 'markdown'
				);
			}
		);

		return new vscode.NotebookData(cells);
	}

	async serializeNotebook(
		data: vscode.NotebookData,
		_token: vscode.CancellationToken
	): Promise<Uint8Array> {
		let contents: RawNotebookCell[] = [];

		for (const cell of data.cells) {
			contents.push({
				cell_type: cell.kind === vscode.NotebookCellKind.Code ? 'code' : 'markdown',
				// To emulate standard ipynb format which is an array of strings per line
				source: cell.value.split(/(?<=\n)/g)
			});
		}

		return new TextEncoder().encode(JSON.stringify({ cells: contents }, null, 2));
	}
}

export function activate(context: vscode.ExtensionContext) {
	context.subscriptions.push(
		vscode.workspace.registerNotebookSerializer('pamd-notebook', new PamdNotebookSerializer())
	);

	// Register a controller to execute the pyact command when "Run" is pressed
	const controller = vscode.notebooks.createNotebookController(
		'pamd-dummy-controller',
		'pamd-notebook',
		'PAMD Editor'
	);
	controller.supportedLanguages = ['python', 'markdown'];
	controller.supportsExecutionOrder = false;
	controller.description = 'Compile PAMD to Markdown';
	
	controller.executeHandler = async (cells, notebook, ctrl) => {
		for (const cell of cells) {
			const execution = ctrl.createNotebookCellExecution(cell);
			execution.start(Date.now());
			
			try {
				if (notebook.isDirty) {
					await notebook.save();
				}

				const pamdPath = notebook.uri.fsPath;
				// Replace .pamd with .md for the output file
				const outPath = pamdPath.replace(/\.pamd$/, '.md');

				const { exec } = require('child_process');
				exec(`python -m pyact.cli "${pamdPath}" -o "${outPath}"`, async (error: any, stdout: string, stderr: string) => {
					if (error) {
						execution.replaceOutput([
							new vscode.NotebookCellOutput([
								vscode.NotebookCellOutputItem.text(stderr || error.message)
							])
						]);
						execution.end(false, Date.now());
					} else {
						execution.replaceOutput([
							new vscode.NotebookCellOutput([
								vscode.NotebookCellOutputItem.text(`Compiled successfully to ${outPath}\n${stdout}`)
							])
						]);
						execution.end(true, Date.now());
						
						// Open the compiled .md file in markdown preview to the side
						const outUri = vscode.Uri.file(outPath);
						await vscode.commands.executeCommand('markdown.showPreviewToSide', outUri);
					}
				});
			} catch (err: any) {
				execution.replaceOutput([
					new vscode.NotebookCellOutput([
						vscode.NotebookCellOutputItem.error(err)
					])
				]);
				execution.end(false, Date.now());
			}
		}
	};
	
	context.subscriptions.push(controller);

	const openedNotebooks = new Set<string>();

	context.subscriptions.push(
		vscode.window.onDidChangeActiveNotebookEditor(async editor => {
			if (editor && editor.notebook.notebookType === 'pamd-notebook') {
				const uriStr = editor.notebook.uri.toString();
				if (!openedNotebooks.has(uriStr)) {
					openedNotebooks.add(uriStr);
					const mdCellIndex = editor.notebook.getCells().findIndex(c => c.kind === vscode.NotebookCellKind.Markup);
					if (mdCellIndex >= 0) {
						editor.selections = [new vscode.NotebookRange(mdCellIndex, mdCellIndex + 1)];
						await vscode.commands.executeCommand('notebook.cell.edit');
					}
				}
			}
		})
	);

	// Register Export to DOCX command
	context.subscriptions.push(
		vscode.commands.registerCommand('pamd.generateDocx', async (contextUri?: vscode.Uri) => {
			let uri = contextUri;
			if (!uri) {
				if (vscode.window.activeNotebookEditor && vscode.window.activeNotebookEditor.notebook.notebookType === 'pamd-notebook') {
					uri = vscode.window.activeNotebookEditor.notebook.uri;
				} else {
					vscode.window.showErrorMessage('No active PAMD file found.');
					return;
				}
			}

			const pamdPath = uri.fsPath;
			const outMdPath = pamdPath.replace(/\.pamd$/, '.md');
			const outDocxPath = pamdPath.replace(/\.pamd$/, '.docx');

			// Save the document if it's dirty
			if (vscode.window.activeNotebookEditor && vscode.window.activeNotebookEditor.notebook.uri.toString() === uri.toString()) {
				if (vscode.window.activeNotebookEditor.notebook.isDirty) {
					await vscode.window.activeNotebookEditor.notebook.save();
				}
			}

			vscode.window.withProgress({
				location: vscode.ProgressLocation.Notification,
				title: "Compiling PAMD to DOCX",
				cancellable: false
			}, async (progress) => {
				return new Promise<void>((resolve, reject) => {
					const { exec } = require('child_process');
					// We execute python via pyact.cli so it generates both MD and DOCX
					exec(`python -m pyact.cli "${pamdPath}" -o "${outMdPath}" --docx "${outDocxPath}"`, (error: any, stdout: string, stderr: string) => {
						if (error) {
							vscode.window.showErrorMessage(`Error generating DOCX: ${stderr || error.message}`);
							reject(error);
						} else {
							vscode.window.showInformationMessage(`Successfully generated ${outDocxPath}`);
							resolve();
						}
					});
				});
			});
		})
	);
}

export function deactivate() {}
