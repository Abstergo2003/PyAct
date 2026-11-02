import json
import os
import time

import pytest

from pyact.cli import is_cache_valid, main
from pyact.core import map_content


def test_cli_compiles_pamd_to_markdown(tmp_path, monkeypatch):
    source = tmp_path / "main.pamd"
    source.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": "def context():\n    return {'name': 'World'}\n",
                    },
                    {
                        "cell_type": "markdown",
                        "source": "# Hello <ctx>name</ctx>\n",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "output.md"
    monkeypatch.setattr(
        "sys.argv",
        ["pyact", str(source), "--output", str(output)],
    )

    main()

    assert output.read_text(encoding="utf-8") == "# Hello World\n"
    assert (tmp_path / ".pamd-cache" / "main.cache.md").exists()


def test_cli_supports_no_cache_and_clear_cache(tmp_path, monkeypatch, capsys):
    source = tmp_path / "main.pamd"
    source.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": "def context():\n    return {'value': 'one'}\n",
                    },
                    {
                        "cell_type": "markdown",
                        "source": "<ctx>value</ctx>\n",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "output.md"

    monkeypatch.setattr(
        "sys.argv",
        ["pyact", str(source), "--output", str(output)],
    )
    main()
    capsys.readouterr()

    monkeypatch.setattr(
        "sys.argv",
        ["pyact", str(source), "--output", str(output), "--no-cache"],
    )
    main()
    assert "one" in output.read_text(encoding="utf-8")
    assert "Cache invalid or missing" in capsys.readouterr().out

    monkeypatch.setattr(
        "sys.argv",
        ["pyact", str(source), "--output", str(output), "--clear-cache"],
    )
    main()
    assert (tmp_path / ".pamd-cache" / "main.cache.md").exists()


def test_cache_invalidates_when_project_style_changes(tmp_path):
    source = tmp_path / "main.pamd"
    source.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": "def context():\n    return {}\n"},
                    {"cell_type": "markdown", "source": "<ctx>x</ctx>\n"},
                ]
            }
        ),
        encoding="utf-8",
    )
    style = tmp_path / "style.css"
    style.write_text("body { color: #000; }\n", encoding="utf-8")
    cache = tmp_path / "cache.md"
    cache.write_text("cached\n", encoding="utf-8")

    future = time.time() + 5
    os.utime(style, (future, future))

    assert not is_cache_valid(
        map_content("main", tmp_path),
        cache.stat().st_mtime,
        tmp_path,
        [style],
    )


def test_cli_reports_code_cell_source_location(tmp_path, monkeypatch, capsys):
    source = tmp_path / "broken.pamd"
    source.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": "def context(:\n    return {}\n"},
                    {"cell_type": "markdown", "source": "<ctx>x</ctx>\n"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.argv", ["pyact", str(source)])

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 1
    error_output = capsys.readouterr().err
    assert "broken.pamd" in error_output
    assert "code cell" in error_output


def test_cli_initializes_custom_project_template(tmp_path, monkeypatch):
    project = tmp_path / "report"
    monkeypatch.setattr(
        "sys.argv",
        ["pyact", "init", str(project), "--template", "academic"],
    )

    main()

    assert (project / "main.pamd").exists()
    assert (project / "global.py").exists()
    assert (project / "pamd.conf").exists()
    assert "Research Data Repository" in (project / "main.pamd").read_text(
        encoding="utf-8"
    )
