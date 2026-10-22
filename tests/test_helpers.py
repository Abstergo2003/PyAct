from pathlib import Path

import pamd_helpers


def test_calculation_renders_equation_and_supports_arithmetic():
    calculation = pamd_helpers.Calculation(lambda x, y: x + y, [2, 3])

    assert calculation.value == 5
    assert "5" in repr(calculation)
    assert calculation + 1 == 6
    assert 10 - calculation == 5


def test_deprecated_equation_supports_inline_lambda():
    equation = pamd_helpers.equation(lambda x: x**2, [5])

    assert "25" in equation
    assert "x^{2}" in equation


def test_table_and_lists_render_markdown():
    table = pamd_helpers.Table(["Name", "Value"], [["A", 1]], "Results", add_no=True)
    ordered = pamd_helpers.CList(["one", "two"], pamd_helpers.ListType.ORDERED)
    checklist = pamd_helpers.CList(["done"], pamd_helpers.ListType.CHECKLIST)

    assert "|No.|Name|Value|" in repr(table)
    assert "|1|A|1|" in repr(table)
    assert "1. one" in repr(ordered)
    assert "- [ ] done" in repr(checklist)


def test_footnote_repr_matches_definition():
    footnote = pamd_helpers.Footnote(2, "A source.")

    assert repr(footnote) == "[^2]: A source."
    assert footnote.adnotation() == "[^2]\n"


def test_plot_saves_supported_image_object(tmp_path):
    from PIL import Image

    image = Image.new("RGB", (2, 2), "white")
    result = pamd_helpers.plot(
        image,
        caption="Tiny image",
        filename="tiny.png",
        output_dir=str(tmp_path),
    )

    assert (tmp_path / "tiny.png").exists()
    assert "![Tiny image](\"" not in result
    assert "tiny.png" in result
