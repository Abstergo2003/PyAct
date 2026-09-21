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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const util_1 = require("util");
class PamdNotebookSerializer {
    async deserializeNotebook(content, _token) {
        var contents = new util_1.TextDecoder().decode(content);
        let raw;
        try {
            raw = JSON.parse(contents);
        }
        catch {
            raw = { cells: [] };
        }
        const cells = raw.cells.map(item => {
            const sourceStr = Array.isArray(item.source) ? item.source.join('') : item.source;
            return new vscode.NotebookCellData(item.cell_type === 'code' ? vscode.NotebookCellKind.Code : vscode.NotebookCellKind.Markup, sourceStr, item.cell_type === 'code' ? 'python' : 'markdown');
        });
        return new vscode.NotebookData(cells);
    }
    async serializeNotebook(data, _token) {
        let contents = [];
        for (const cell of data.cells) {
            contents.push({
                cell_type: cell.kind === vscode.NotebookCellKind.Code ? 'code' : 'markdown',
                // To emulate standard ipynb format which is an array of strings per line
                source: cell.value.split(/(?<=\n)/g)
            });
        }
        return new util_1.TextEncoder().encode(JSON.stringify({ cells: contents }, null, 2));
    }
}
function activate(context) {
    context.subscriptions.push(vscode.workspace.registerNotebookSerializer('pamd-notebook', new PamdNotebookSerializer()));
    // Register a controller to execute the pyact command when "Run" is pressed
    const controller = vscode.notebooks.createNotebookController('pamd-dummy-controller', 'pamd-notebook', 'PAMD Editor');
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
                exec(`python -m pyact.cli "${pamdPath}" -o "${outPath}"`, async (error, stdout, stderr) => {
                    if (error) {
                        execution.replaceOutput([
                            new vscode.NotebookCellOutput([
                                vscode.NotebookCellOutputItem.text(stderr || error.message)
                            ])
                        ]);
                        execution.end(false, Date.now());
                    }
                    else {
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
            }
            catch (err) {
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
    const openedNotebooks = new Set();
    context.subscriptions.push(vscode.window.onDidChangeActiveNotebookEditor(async (editor) => {
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
    }));
}
function deactivate() { }
//# sourceMappingURL=extension.js.map