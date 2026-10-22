import * as assert from 'assert';
import { TextEncoder } from 'util';

// You can import and use all API from the 'vscode' module
// as well as import your extension to test it
import * as vscode from 'vscode';
import {
	contextCompletionPrefix,
	createPyActCommand,
	extractContextKeys,
	PamdNotebookSerializer,
	shouldCloseContextTag
} from '../extension';

suite('Extension Test Suite', () => {
	test('builds a non-shell PyAct command', () => {
		const command = createPyActCommand('python-custom', ['document.pamd', '--no-cache'], 'C:\\project');

		assert.strictEqual(command.command, 'python-custom');
		assert.deepStrictEqual(command.args, ['-m', 'pyact.cli', 'document.pamd', '--no-cache']);
		assert.strictEqual(command.cwd, 'C:\\project');
	});

	test('serializes and deserializes one markdown with multiple code cells', async () => {
		const serializer = new PamdNotebookSerializer();
		const data = await serializer.deserializeNotebook(
			new TextEncoder().encode(JSON.stringify({
				cells: [
					{ cell_type: 'code', source: ['x = 1\n'] },
					{ cell_type: 'code', source: ['def context():\n', '    return {"x": x}\n'] },
					{ cell_type: 'markdown', source: ['Value: <ctx>x</ctx>\n'] }
				]
			})),
			new vscode.CancellationTokenSource().token
		);

		assert.strictEqual(data.cells.length, 3);
		assert.strictEqual(data.cells[1].value, 'def context():\n    return {"x": x}\n');
		assert.strictEqual(data.cells[2].languageId, 'markdown');
	});

	test('rejects PAMD documents without exactly one markdown cell', async () => {
		const serializer = new PamdNotebookSerializer();

		await assert.rejects(
			serializer.deserializeNotebook(
				new TextEncoder().encode(JSON.stringify({
					cells: [{ cell_type: 'code', source: 'x = 1\n' }]
				})),
				new vscode.CancellationTokenSource().token
			),
			/expected exactly one markdown cell/
		);
	});

	test('extracts context keys for completion suggestions', () => {
		const keys = extractContextKeys(`
def context():
    return {
        "project": {"author": "Ada"},
        "empty": "",
    }
`);

		assert.deepStrictEqual(keys, ['empty', 'project', 'project.author']);
	});

	test('only offers completion inside an open ctx tag', () => {
		assert.strictEqual(contextCompletionPrefix('Value: <ctx>pro', 15), 'pro');
		assert.strictEqual(contextCompletionPrefix('Value: <ctx>project</ctx>', 25), undefined);
		assert.strictEqual(contextCompletionPrefix('Value: project', 14), undefined);
	});

	test('detects when an opening ctx tag needs its closing tag', () => {
		assert.strictEqual(shouldCloseContextTag('<ctx>', 5), true);
		assert.strictEqual(shouldCloseContextTag('<ctx></ctx>', 5), false);
		assert.strictEqual(shouldCloseContextTag('Value: <ctx>pro', 15), false);
	});
});
