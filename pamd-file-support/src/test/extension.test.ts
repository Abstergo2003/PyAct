import * as assert from 'assert';
import {
	contextCompletionPrefix,
	createPyActCommand,
	extractContextKeys,
	shouldCloseContextTag
} from '../extension';

suite('Extension Test Suite', () => {
	test('builds a non-shell PyAct command', () => {
		const command = createPyActCommand('python-custom', ['document.pamd', '--no-cache'], 'C:\\project');

		assert.strictEqual(command.command, 'python-custom');
		assert.deepStrictEqual(command.args, ['-m', 'pyact.cli', 'document.pamd', '--no-cache']);
		assert.strictEqual(command.cwd, 'C:\\project');
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
