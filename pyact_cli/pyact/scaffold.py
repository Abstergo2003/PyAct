import os
import json

def init_project(target_dir: str = ".", template: str = "default"):
    """
    Scaffolds a new PyAct project with boilerplate files.
    
    Why it is needed:
    Enables users to instantly create a ready-to-run PyAct project with main.pamd, 
    global.py, pamd.conf, style.css, and .gitignore without manual setup.
    
    Inputs:
        target_dir (str): Destination folder path.
        template (str): 'default', 'engineering', or 'academic'.
    """
    if target_dir != "." and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    project_name = os.path.basename(os.path.abspath(target_dir))
    if project_name == "" or project_name == ".":
        project_name = "My PyAct Project"
        
    # 1. global.py
    global_py_content = f'''def global_context():
    """
    Global variables accessible across all templates using <glb>var_name</glb>.
    """
    return {{
        "author": "Author Name",
        "project_name": "{project_name}",
        "company": "Company Name",
        "version": "1.0.0"
    }}
'''

    # 2. pamd.conf
    pamd_conf_content = f'''[Header]
left = {project_name}
right = 2026
font_size = 9pt
color = #666666

[Footer]
left = Confidential
center = Page {{page}} of {{pages}}
font_size = 9pt

[Metadata]
author = Author Name
title = {project_name}
subject = Technical Report

[Page]
size = A4
margin = 1in
'''

    # 3. style.css
    style_css_content = '''body {
    font-family: Calibri, sans-serif;
    font-size: 11pt;
    line-height: 1.25;
    color: #222222;
}

h1 {
    color: #1a365d;
    font-size: 22pt;
    font-weight: bold;
    margin-bottom: 14pt;
}

h2 {
    color: #2b6cb0;
    font-size: 16pt;
    font-weight: bold;
    margin-top: 14pt;
    margin-bottom: 8pt;
}

h3 {
    color: #4a5568;
    font-size: 13pt;
    font-weight: bold;
    margin-top: 10pt;
    margin-bottom: 6pt;
}

p {
    margin-bottom: 8pt;
}
'''

    # 4. .gitignore
    gitignore_content = '''.pamd-cache/
__pycache__/
*.pyc
'''

    # 5. main.pamd based on template
    if template == "engineering":
        cells = [
            {
                "cell_type": "code",
                "source": [
                    "import pamd_helpers\n",
                    "\n",
                    "def context():\n",
                    "    # 1. Design formula with Greek symbols and subscripts\n",
                    "    f_cd = lambda f_ck, gamma_c: f_ck / gamma_c\n",
                    "    design_strength = pamd_helpers.equation(f_cd, [30, 1.5])\n",
                    "    \n",
                    "    # 2. Table of material properties\n",
                    "    headers = [\"Property\", \"Symbol\", \"Value\", \"Unit\"]\n",
                    "    rows = [\n",
                    "        [\"Char. Compressive Strength\", \"f_ck\", \"30\", \"MPa\"],\n",
                    "        [\"Partial Safety Factor\", \"gamma_c\", \"1.5\", \"-\"],\n",
                    "        [\"Design Compressive Strength\", \"f_cd\", \"20\", \"MPa\"]\n",
                    "    ]\n",
                    "    mat_table = pamd_helpers.table(headers, rows, \"Concrete Material Properties\", add_no=True)\n",
                    "    \n",
                    "    return {\n",
                    "        \"strength_calc\": design_strength,\n",
                    "        \"material_table\": mat_table\n",
                    "    }\n"
                ]
            },
            {
                "cell_type": "markdown",
                "source": [
                    "# <glb>project_name</glb>\n",
                    "Author: **<glb>author</glb>** | Organization: **<glb>company</glb>**\n",
                    "\n",
                    "<toc/>\n",
                    "\n",
                    "<pagebreak/>\n",
                    "\n",
                    "## 1. Material Specifications\n",
                    "Below are the design material parameters:\n",
                    "<ctx>material_table</ctx>\n",
                    "\n",
                    "## 2. Design Strength Verification\n",
                    "The design compressive strength is calculated in accordance with Eurocode 2:\n",
                    "<ctx>strength_calc</ctx>\n"
                ]
            }
        ]
    elif template == "academic":
        cells = [
            {
                "cell_type": "code",
                "source": [
                    "import pamd_helpers\n",
                    "\n",
                    "def context():\n",
                    "    fn1 = pamd_helpers.Footnote(1, \"Comprehensive study published in Journal of Applied Sciences, 2026.\")\n",
                    "    hyp = pamd_helpers.hyperlink(\"Research Data Repository\", \"https://example.org/dataset\")\n",
                    "    \n",
                    "    return {\n",
                    "        \"fn_ref\": fn1.adnotation(),\n",
                    "        \"fn_def\": fn1.define_string(),\n",
                    "        \"data_link\": hyp\n",
                    "    }\n"
                ]
            },
            {
                "cell_type": "markdown",
                "source": [
                    "# <glb>project_name</glb>\n",
                    "**<glb>author</glb>** (<glb>company</glb>)\n",
                    "\n",
                    "### Abstract\n",
                    "This document explores computational report generation with PyAct.\n",
                    "\n",
                    "<toc/>\n",
                    "\n",
                    "<pagebreak/>\n",
                    "\n",
                    "## 1. Introduction\n",
                    "Recent advancements in dynamic markdown have bridged computational logic with formal report generation<ctx>fn_ref</ctx>.\n",
                    "\n",
                    "The primary datasets are hosted at <ctx>data_link</ctx>.\n",
                    "\n",
                    "---\n",
                    "<ctx>fn_def</ctx>\n"
                ]
            }
        ]
    else:  # default template
        cells = [
            {
                "cell_type": "code",
                "source": [
                    "import pamd_helpers\n",
                    "\n",
                    "def context():\n",
                    "    eq = pamd_helpers.equation(lambda x, y: x**2 + y, [4, 5])\n",
                    "    tasks = pamd_helpers.checklist([\"Setup project\", \"Write logic\", \"Export to Word\"])\n",
                    "    \n",
                    "    return {\n",
                    "        \"math\": eq,\n",
                    "        \"todo\": tasks\n",
                    "    }\n"
                ]
            },
            {
                "cell_type": "markdown",
                "source": [
                    "# <glb>project_name</glb>\n",
                    "Prepared by: **<glb>author</glb>**\n",
                    "\n",
                    "<toc/>\n",
                    "\n",
                    "<pagebreak/>\n",
                    "\n",
                    "## 1. Overview\n",
                    "Welcome to PyAct! This project was initialized with `pyact init`.\n",
                    "\n",
                    "## 2. Dynamic Computation\n",
                    "Here is a mathematical calculation:\n",
                    "<ctx>math</ctx>\n",
                    "\n",
                    "## 3. Project Tasks\n",
                    "<ctx>todo</ctx>\n"
                ]
            }
        ]

    pamd_content = json.dumps({"cells": cells}, indent=2)

    files_to_create = {
        "global.py": global_py_content,
        "pamd.conf": pamd_conf_content,
        "style.css": style_css_content,
        ".gitignore": gitignore_content,
        "main.pamd": pamd_content
    }

    created = []
    skipped = []
    for fname, content in files_to_create.items():
        fpath = os.path.join(target_dir, fname)
        if os.path.exists(fpath):
            skipped.append(fname)
        else:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            created.append(fname)

    target_display = target_dir if target_dir != "." else "current directory"
    print(f"Initialized PyAct project in {target_display} (template: {template}):")
    for f in created:
        print(f"  + Created {f}")
    for f in skipped:
        print(f"  ~ Skipped {f} (already exists)")
    print("\nNext steps:")
    if target_dir != ".":
        print(f"  cd {target_dir}")
    print("  pyact main.pamd -o output.md --docx output.docx")
