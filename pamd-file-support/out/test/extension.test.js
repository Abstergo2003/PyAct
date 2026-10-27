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
const assert = __importStar(require("assert"));
const extension_1 = require("../extension");
suite('Extension Test Suite', () => {
    test('builds a non-shell PyAct command', () => {
        const command = (0, extension_1.createPyActCommand)('python-custom', ['document.pamd', '--no-cache'], 'C:\\project');
        assert.strictEqual(command.command, 'python-custom');
        assert.deepStrictEqual(command.args, ['-m', 'pyact.cli', 'document.pamd', '--no-cache']);
        assert.strictEqual(command.cwd, 'C:\\project');
    });
    test('extracts context keys for completion suggestions', () => {
        const keys = (0, extension_1.extractContextKeys)(`
def context():
    return {
        "project": {"author": "Ada"},
        "empty": "",
    }
`);
        assert.deepStrictEqual(keys, ['empty', 'project', 'project.author']);
    });
    test('only offers completion inside an open ctx tag', () => {
        assert.strictEqual((0, extension_1.contextCompletionPrefix)('Value: <ctx>pro', 15), 'pro');
        assert.strictEqual((0, extension_1.contextCompletionPrefix)('Value: <ctx>project</ctx>', 25), undefined);
        assert.strictEqual((0, extension_1.contextCompletionPrefix)('Value: project', 14), undefined);
    });
    test('detects when an opening ctx tag needs its closing tag', () => {
        assert.strictEqual((0, extension_1.shouldCloseContextTag)('<ctx>', 5), true);
        assert.strictEqual((0, extension_1.shouldCloseContextTag)('<ctx></ctx>', 5), false);
        assert.strictEqual((0, extension_1.shouldCloseContextTag)('Value: <ctx>pro', 15), false);
    });
});
//# sourceMappingURL=extension.test.js.map