# PyAct Roadmap

PyAct's core differentiator is computational document authoring with publishing
to both Markdown and native DOCX. The roadmap prioritizes reliability and
authoring quality before adding more output formats.

## v1.2 - Reliability and Core Stability

- [x] Define and validate the `.pamd` JSON format.
- [x] Report malformed files and invalid cell types with useful diagnostics.
- [x] Complete the `pathlib.Path` migration across the compiler and supporting tools.
- [x] Detect recursive `<tmp>` template references before compilation.
- [x] Support nested context and global values with dotted lookup.
- [x] Distinguish missing values from valid empty values.
- [x] Add explicit cache controls such as `--no-cache` and cache clearing.
- [x] Improve cache invalidation to include templates, configuration, styling, and relevant helper-library changes.
- [x] Expand automated coverage for compiler, CLI, Markdown, and DOCX behavior.

## v1.3 - Authoring Experience

- [ ] Add richer CLI diagnostics with file, cell, and source-location information.
- [ ] Improve linting for unused and missing context values, templates, and globals.
- [x] Add VS Code diagnostics for compilation and lint errors.
- [x] Add VS Code commands for Markdown compilation, DOCX export, linting, and cache management.
- [x] Add syntax highlighting for `<ctx>`, `<glb>`, `<tmp>`, and document-control tags.
- [x] Support configurable Python interpreters and virtual environments in the VS Code extension.
- [x] Replace the native VS Code notebook surface with a controlled custom PAMD editor.
- [x] Provide a dedicated PyAct toolbar without native notebook execution controls.
- [ ] Improve project scaffolding and template customization.

## v1.4 - Shared Rendering Architecture

- [ ] Introduce a shared intermediate document AST between evaluation and output.
- [ ] Separate parsing, evaluation, and rendering responsibilities.
- [ ] Make Markdown and DOCX rendering consume the same structured document model.
- [ ] Improve inline formatting, table alignment, list handling, and footnotes.
- [ ] Add stronger golden-file and OOXML invariant tests.
- [ ] Add HTML export using the same document model.

## v2.0 - Extensibility and Secure Execution

- [ ] Stabilize and formally document the `.pamd` specification.
- [ ] Add a plugin/component API for custom document elements.
- [ ] Support reusable report themes and component libraries.
- [ ] Add secure execution profiles for untrusted projects.
- [ ] Add configurable execution timeouts and project-root file-access controls.
- [ ] Add bibliography, citation, and reference support.
- [ ] Support additional publishing backends such as PDF and LaTeX.

## Cross- Cutting Engineering Work

- [ ] Move packaging from `setup.py` to `pyproject.toml`.
- [ ] Add CI for supported Python versions and Windows/Linux environments.
- [ ] Publish wheels and source distributions automatically.
- [ ] Maintain semantic versioning and a changelog.
- [ ] Keep generated caches, build artifacts, and temporary test outputs out of version control.
- [ ] Preserve key invariants:
  - [ ] dynamic `linecache` mocking for source inspection and equation helpers;
  - [ ] separation of `global.py`, `pamd.conf`, and CSS responsibilities;
  - [ ] pre-populated Word TOC fields;
  - [ ] repeated table headers and non-splitting table rows.

## Recommended Priority

The highest - value next investment is a shared document model backed by a broad regression suite. Together they reduce rendering regressions and provide a clean foundation for HTML, PDF, and other future output formats.
