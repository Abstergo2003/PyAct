import * as vscode from 'vscode';
import { TextDecoder, TextEncoder } from 'util';

/**
 * Interface defining the raw JSON structure of a .pamd file.
 * .pamd files share the exact same underlying structure as Jupyter Notebooks (.ipynb),
 * meaning they consist of an array of cell objects.
 */
interface RawNotebook {
	cells: RawNotebookCell[];
}

/**
 * Interface defining an individual cell inside a .pamd file.
 */
interface RawNotebookCell {
	/** The type of cell. PyAct only supports 'code' (Python) and 'markdown' cells. */
	cell_type: 'code' | 'markdown';
	/** The text content of the cell. Can be a single string or an array of strings (lines). */
	source: string[] | string;
}

/**
 * Notebook Serializer for handling custom .pamd files.
 * 
 * Why it is needed:
 * VS Code Notebooks natively only understand JSON or text if told how to parse it. 
 * This class acts as the translation layer between the raw `.pamd` JSON file on disk 
 * and the visual Notebook UI inside the VS Code editor.
 */
class PamdNotebookSerializer implements vscode.NotebookSerializer {
	
	/**
	 * Deserializes raw file bytes into VS Code Notebook data.
	 * 
	 * Why it is needed:
	 * Called automatically when a user opens a `.pamd` file. It reads the raw JSON 
	 * and builds the interactive Markdown and Python cells. If the file is completely 
	 * empty, it bootstraps it with a default Markdown and Python `context()` cell.
	 * 
	 * @param content The raw binary data of the file from disk.
	 * @param _token Cancellation token.
	 * @returns A parsed `vscode.NotebookData` object ready to render.
	 */
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
				// Bootstrap a new, empty .pamd file with the required boilerplate structure
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

	/**
	 * Serializes VS Code Notebook data back into raw file bytes.
	 * 
	 * Why it is needed:
	 * Called automatically when a user saves a `.pamd` file (Ctrl+S). It converts 
	 * the modified interactive cells back into standard Jupyter JSON format so the 
	 * Python PyAct compiler can read it safely.
	 * 
	 * @param data The interactive Notebook data from the VS Code editor.
	 * @param _token Cancellation token.
	 * @returns The raw binary string encoded into a Uint8Array.
	 */
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

/**
 * Main activation function for the VS Code Extension.
 * 
 * Why it is needed:
 * This is the entry point that VS Code calls when the extension is launched. 
 * It registers the `.pamd` Notebook serializer, the execution controller (Run button), 
 * UI event listeners, and the DOCX export command.
 * 
 * @param context The extension context provided by VS Code.
 */
export function activate(context: vscode.ExtensionContext) {
	// Register the Serializer to handle .pamd file opening/saving
	context.subscriptions.push(
		vscode.workspace.registerNotebookSerializer('pamd-notebook', new PamdNotebookSerializer())
	);

	// Register the Execution Controller (The "Run" button in the Notebook UI)
	const controller = vscode.notebooks.createNotebookController(
		'pamd-dummy-controller',
		'pamd-notebook',
		'PAMD Editor'
	);
	controller.supportedLanguages = ['python', 'markdown'];
	controller.supportsExecutionOrder = false;
	controller.description = 'Compile PAMD to Markdown';
	
	/**
	 * The handler executed when the user presses the "Run" button.
	 * 
	 * Why it is needed:
	 * Instead of executing Python code natively inside VS Code like a true Jupyter backend, 
	 * this handler saves the file to disk and shells out to `python -m pyact.cli`. 
	 * It then displays the output in the cell and automatically opens the compiled Markdown preview.
	 */
	controller.executeHandler = async (cells, notebook, ctrl) => {
		for (const cell of cells) {
			const execution = ctrl.createNotebookCellExecution(cell);
			execution.start(Date.now());
			
			try {
				// Auto-save before running to ensure CLI has latest data
				if (notebook.isDirty) {
					await notebook.save();
				}

				const pamdPath = notebook.uri.fsPath;
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

	/**
	 * Window Editor Event Listener.
	 * 
	 * Why it is needed:
	 * Automatically focuses the Markdown cell when a new `.pamd` file is opened so 
	 * the user can start typing their document immediately without needing to click.
	 */
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

	/**
	 * Register the DOCX Export Command.
	 * 
	 * Why it is needed:
	 * Binds to the `pamd.generateDocx` button in the editor title bar. 
	 * It triggers the PyAct CLI in the background with the `--docx` switch 
	 * to generate a finished Word document directly from the editor.
	 */
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
