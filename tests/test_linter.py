import json

from pyact.linter import run_linter


def write_document(path, code, markdown):
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": code},
                    {"cell_type": "markdown", "source": markdown},
                ]
            }
        ),
        encoding="utf-8",
    )


def test_linter_reports_unused_and_missing_context_and_globals(tmp_path, capsys):
    write_document(
        tmp_path / "main.pamd",
        "def context():\n    return {'used': 'ok', 'unused': 'unused'}\n",
        "<ctx>used</ctx> <ctx>missing</ctx> <glb>author</glb> <glb>missing_global</glb>\n",
    )
    (tmp_path / "global.py").write_text(
        "def global_context():\n    return {'author': 'Ada', 'unused_global': 'unused'}\n",
        encoding="utf-8",
    )

    assert run_linter("main", str(tmp_path)) is False
    output = capsys.readouterr().out
    assert "Unused context exports" in output
    assert "Missing context exports" in output
    assert "Unused global exports" in output
    assert "Missing global exports" in output


def test_linter_accepts_resolved_templates(tmp_path, capsys):
    write_document(
        tmp_path / "main.pamd",
        "def context():\n    return {}\n",
        "<tmp>child</tmp>\n",
    )
    write_document(
        tmp_path / "child.pamd",
        "def context():\n    return {}\n",
        "Child\n",
    )

    assert run_linter("main", str(tmp_path)) is True
    assert "Template references resolved" in capsys.readouterr().out
