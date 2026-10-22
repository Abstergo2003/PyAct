from pathlib import Path

from pyact.conf_parser import conf_parser
from pyact.css2json import css_to_dict
from pyact.mdTOword import markdown_parser


def test_css_parser_handles_comments_important_and_grouped_selectors():
    css = """
    /* ignored */
    h1, h2 { color: #123456 !important; font-size: 18pt; }
    """

    parsed = css_to_dict(css)

    assert parsed["h1"]["color"] == "#123456"
    assert parsed["h2"]["font-size"] == "18pt"


def test_conf_parser_reads_sections_and_values(tmp_path):
    config = tmp_path / "pamd.conf"
    config.write_text(
        "[Header]\nleft = Project\n\n[Metadata]\nauthor = Ada\n",
        encoding="utf-8",
    )

    assert conf_parser(str(config)) == {
        "Header": {"left": "Project"},
        "Metadata": {"author": "Ada"},
    }


def test_markdown_parser_recognizes_document_blocks():
    blocks = markdown_parser(
        "# Heading\n"
        "\n"
        "> [!WARNING] Be careful\n"
        "> Check this value.\n"
        "\n"
        "| A | B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n"
        "\n"
        "<pagebreak/>\n"
        "$$ x^2 $$\n"
    )

    assert ("heading", 1, "Heading") in blocks
    assert ("callout", "WARNING", "Be careful", ["Check this value."]) in blocks
    assert ("table", ["| A | B |", "|---|---|", "| 1 | 2 |"]) in blocks
    assert ("pagebreak",) in blocks
    assert ("math", "x^2") in blocks
