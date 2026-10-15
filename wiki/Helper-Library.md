# The Helper Library

PyAct ships with a built-in library called `pamd_helpers`. You can import it directly into your `.pamd` Python cell to programmatically generate complex Markdown structures!

```python
import pamd_helpers

def context():
    return { ... }
```

## 1. LaTeX Equations
Generates a Markdown math string (`$$ Equation = Value $$`) by automatically translating a Python lambda function into LaTeX!

```python
# Code Cell
eq = pamd_helpers.equation(lambda x, y: x**2 + y, [5, 2])
# Returns: "$$ x^{2} + y = 27 $$"
```

## 2. Dynamic Tables
Generating Markdown tables by hand is tedious. The `table` helper takes a 2D Python array and formats it instantly, along with a caption and optional auto-numbering.

```python
# Code Cell
headers = ["Name", "Age"]
data = [
    ["Alice", 25],
    ["Bob", 30]
]
my_table = pamd_helpers.table(headers, data, caption="User Data", add_no=True)
```

## 3. Images with Captions
Standard Markdown `![caption](url)` doesn't render the caption as text below the image. The `image` helper injects an HTML span below the image to force a styled, italicized caption.

```python
my_image = pamd_helpers.image("https://example.com/img.png", "A beautiful view")
```

## 4. Footnotes
Footnotes in Markdown require an inline annotation (`[^1]`) and a bottom-of-page definition (`[^1]: Text`). The `Footnote` class keeps these linked.

```python
fn1 = pamd_helpers.Footnote(1, "This is the source.")

def context():
    return {
        "fn1_mark": fn1.adnotation(),
        "fn1_def": fn1.define_string()
    }
```

In your Markdown:
```markdown
Here is a claim.<ctx>fn1_mark</ctx>

<ctx>fn1_def</ctx>
```

## 5. Lists
Generate perfectly formatted bulleted, numbered, or task lists from Python arrays.

```python
bullets = pamd_helpers.unordered_list(["Apples", "Bananas"])
numbers = pamd_helpers.ordered_list(["First", "Second"])
tasks = pamd_helpers.checklist(["Write tests", "Refactor"])
```

## 6. The `Unit` Class and Engineering Math

Engineering and science documents require numbers with units. The `Unit` class seamlessly wraps values, allowing you to perform standard Python math (addition, multiplication, powers, etc.) on them while retaining their physical meaning.

```python
from pyact_cli.pamd_helpers.unit import Unit

def context():
    force = Unit(500, "[kN]")
    area = Unit(2, "[m2]")
    pressure = force / area
    # pressure is evaluated as 250!
    return {"pressure": pressure}
```
*Note: During mathematical operations, the `Unit` class automatically extracts its raw float value, allowing it to interface perfectly with standard Python math libraries.*

## 7. The Standard Value Catalogues

PyAct is heavily geared toward science and engineering. It ships with massive built-in databases of standard properties so you never have to look them up. All numerical values in these catalogues are pre-wrapped in the `Unit` class.

### Civil Engineering
Located in `catalogue.CivilEngineering`:
- **Beams (`Steel`, `Wood`)**: Full structural properties (Area, Inertia, section moduli, mass) for thousands of standard European profiles (IPE, HEA, UKB, CHS, RHS, Timber sections).
- **Concrete & Rebar**: Characteristic strengths, elastic moduli, and standard rebar diameters/areas.
- **Geotech & Soil**: Bulk weights, friction angles, cohesion, and bearing capacities for sands, clays, and gravels.
- **Materials**: Standard mechanical properties for Aluminium, Steel, Softwood, Mortar, and Masonry Units.

### Chemistry
Located in `catalogue.Chemistry`:
- **PeriodicTable**: Comprehensive element properties (atomic mass, density, melting/boiling points, electronegativity).
- **Compounds & Physical Constants**: Enthalpies of formation, heat capacities, Antoine vapor pressure coefficients, bond energies, latent heats, and solubility constants ($K_{sp}$).

### Biology
Located in `catalogue.Biology`:
- **Amino & Nucleic Acids**: Molecular weights, isoelectric points, and hydropathy indices.
- **Cellular & Kinetics**: Standard cell volumes, enzyme kinetic parameters ($K_m$, $k_{cat}$), bioenergetics ($\Delta G^\circ$), and macromolecule densities.

```python
from pyact_cli.pamd_helpers.catalogue.CivilEngineering.Concrete import Concrete
from pyact_cli.pamd_helpers.catalogue.Chemistry.PeriodicTable import PeriodicTable

# Instantly access standard engineering values:
fck = Concrete().C30_37["fck"]
ti_density = PeriodicTable().elements.Titanium["density"]
```

## 8. Plotting and Figures (`pamd_helpers.plot`)

Seamlessly embed charts, graphs, and figures from **Matplotlib**, **Seaborn**, or **Pillow** directly into your documents. The `plot` helper saves the figure into an images folder and outputs a Markdown image tag that renders in both Markdown and Microsoft Word (DOCX).

```python
import matplotlib.pyplot as plt
import pamd_helpers

def context():
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([0, 1, 2, 3], [0, 5, 20, 45], 'r-', label='Moment Diagram')
    ax.set_title('Bending Moment')
    ax.legend()
    
    chart_md = pamd_helpers.plot(fig, caption="Bending Moment along Span", filename="moment_diagram.png")
    plt.close(fig)
    
    return {"moment_chart": chart_md}
```

In your Markdown:
```markdown
## Structural Response
<ctx>moment_chart</ctx>
```

## 9. Callouts and Alerts (`pamd_helpers.callout`)

Generate styled GitHub-flavored Markdown alert boxes:

```python
warning_box = pamd_helpers.callout("Check shear capacity at support per EN 1992-1-1.", callout_type="warning", title="Safety Check")
```
Supported types: `'note'`, `'tip'`, `'important'`, `'warning'`, `'caution'`.
