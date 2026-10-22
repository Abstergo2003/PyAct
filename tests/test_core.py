import json
from pathlib import Path

import pytest

from pyact.core import (
    find_globals,
    find_imports,
    find_templates,
    generate_markdown_toc,
    get_globals,
    get_imports,
    map_content,
    process_content,
    read_pamd_cells,
    validate_pamd_document,
)


def write_pamd(path: Path, code: str = "", markdown: str = "") -> None:
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


def test_read_pamd_cells_accepts_string_and_line_sources(tmp_path):
    path = tmp_path / "document.pamd"
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": ["x = 1\n", "y = 2\n"]},
                    {"cell_type": "markdown", "source": ["# Title\n", "Body\n"]},
                ]
            }
        ),
        encoding="utf-8",
    )

    code, markdown = read_pamd_cells(str(path))

    assert code == "x = 1\ny = 2\n"
    assert markdown == "# Title\nBody\n"


def test_multiple_code_cells_are_combined_in_order(tmp_path):
    path = tmp_path / "document.pamd"
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": "prefix = 'Hello'\n"},
                    {
                        "cell_type": "code",
                        "source": "def context():\n"
                        "    return {'message': prefix + ' world'}\n",
                    },
                    {"cell_type": "markdown", "source": "<ctx>message</ctx>\n"},
                ]
            }
        ),
        encoding="utf-8",
    )

    code, markdown = read_pamd_cells(path)

    assert "prefix = 'Hello'" in code
    assert "def context()" in code
    assert markdown == "<ctx>message</ctx>\n"
    assert process_content(map_content("document", tmp_path)) == "Hello world\n"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"cells": []}, "exactly one markdown cell"),
        (
            {"cells": [{"cell_type": "raw", "source": ""}]},
            "unsupported cell_type",
        ),
        (
            {
                "cells": [
                    {"cell_type": "markdown", "source": 42},
                ]
            },
            "'source' must be",
        ),
    ],
)
def test_pamd_format_validation_rejects_invalid_documents(tmp_path, payload, message):
    path = tmp_path / "invalid.pamd"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        read_pamd_cells(path)


def test_pamd_format_validation_rejects_malformed_json(tmp_path):
    path = tmp_path / "invalid.pamd"
    path.write_text('{"cells":', encoding="utf-8")

    with pytest.raises(ValueError, match="malformed JSON"):
        read_pamd_cells(path)


def test_tag_finders_extract_requested_values():
    text = "<ctx>title</ctx> <glb>author</glb> <tmp>chapter/one</tmp>"

    assert find_imports(text) == ["title"]
    assert find_globals(text) == ["author"]
    assert find_templates(text) == ["chapter/one"]


def test_get_imports_executes_context_and_reports_contract_errors():
    context = get_imports(
        "document",
        "def context():\n    return {'answer': 42}\n",
    )
    assert context == {"answer": 42}

    with pytest.raises(ValueError, match="missing the required"):
        get_imports("document", "value = 1\n")

    with pytest.raises(TypeError, match="must return a dictionary"):
        get_imports("document", "def context():\n    return 42\n")


def test_nested_templates_and_globals_are_compiled(tmp_path):
    write_pamd(
        tmp_path / "main.pamd",
        "def context():\n    return {'title': 'Main'}\n",
        "# <ctx>title</ctx>\n<glb>project</glb>\n<tmp>parts/child</tmp>\n",
    )
    (tmp_path / "parts").mkdir()
    write_pamd(
        tmp_path / "parts" / "child.pamd",
        "def context():\n    return {'value': 'Child'}\n",
        "Value: <ctx>value</ctx>; <glb>project</glb>\n",
    )
    (tmp_path / "global.py").write_text(
        "def global_context():\n    return {'project': 'PyAct'}\n",
        encoding="utf-8",
    )

    tree = map_content("main", str(tmp_path))
    result = process_content(tree)

    assert "# Main" in result
    assert "Value: Child; PyAct" in result


def test_windows_style_template_paths_and_nested_context_values(tmp_path):
    (tmp_path / "parts").mkdir()
    write_pamd(
        tmp_path / "main.pamd",
        "def context():\n"
        "    return {'project': {'author': 'Ada'}, 'empty': ''}\n",
        "Author: <ctx>project.author</ctx>\n"
        "Empty: '<ctx>empty</ctx>'\n"
        "<tmp>parts\\child</tmp>\n",
    )
    write_pamd(
        tmp_path / "parts" / "child.pamd",
        "def context():\n    return {}\n",
        "Child\n",
    )

    result = process_content(map_content("main", tmp_path))

    assert "Author: Ada" in result
    assert "Empty: ''" in result
    assert "Child" in result


def test_missing_context_value_is_not_treated_as_empty(tmp_path):
    write_pamd(
        tmp_path / "main.pamd",
        "def context():\n    return {'present': ''}\n",
        "Present: '<ctx>present</ctx>'\nMissing: <ctx>missing</ctx>\n",
    )

    with pytest.raises(ValueError, match="Context variable 'missing'"):
        process_content(map_content("main", tmp_path))


def test_recursive_templates_are_rejected_with_cycle_details(tmp_path):
    write_pamd(tmp_path / "main.pamd", markdown="<tmp>child</tmp>\n")
    write_pamd(tmp_path / "child.pamd", markdown="<tmp>main</tmp>\n")

    with pytest.raises(ValueError, match="Recursive <tmp> template cycle detected"):
        map_content("main", tmp_path)


def test_missing_global_is_explicit(tmp_path):
    write_pamd(
        tmp_path / "main.pamd",
        "def context():\n    return {}\n",
        "<glb>missing</glb>\n",
    )

    with pytest.raises(ValueError, match="Global variable 'missing'"):
        process_content(map_content("main", str(tmp_path)))


def test_get_globals_requires_global_context(tmp_path):
    path = tmp_path / "global.py"
    path.write_text("value = 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must define a 'global_context"):
        get_globals(str(tmp_path))


def test_generate_markdown_toc_uses_headings_after_tag_and_custom_title():
    text = (
        "# Document\n\n"
        '<toc title="Contents"/>\n\n'
        "## Intro\n\n"
        "### Details\n"
    )

    result = generate_markdown_toc(text)

    assert "## Contents" in result
    assert "- [Intro](#intro)" in result
    assert "  - [Details](#details)" in result
    assert '<toc title="Contents"/>' not in result


def test_generate_markdown_toc_ignores_code_fences():
    text = "<toc/>\n\n## Real Heading\n\n```md\n## Not a heading\n```\n"

    result = generate_markdown_toc(text)

    assert "- [Real Heading](#real-heading)" in result
    assert "Not a heading](#not-a-heading)" not in result
