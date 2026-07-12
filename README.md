# AnyProduct Studio

Create sellable outputs from _any_ structured input: proposals, recipes, formulas, reports, and more.

## Features
- **Plugin-style generators** – add new generators by dropping Python modules into `anyproduct/generators/`.
- **Multiple formats** – render Markdown, DOCX, CSV, and JSON outputs from a single payload.
- **CLI workflow** – list and execute generators via `python -m anyproduct.main`.
- **Streamlit GUI** – friendly web UI powered by `streamlit run anyproduct/app.py`.

## Installation
```bash
pip install -r requirements.txt
```

## Command Line Quickstart
```bash
# List available generators
python -m anyproduct.main --list

# Generate a lawn proposal using the bundled sample data
python -m anyproduct.main --generate proposal \
    --input samples/proposal.json \
    --out build
```

Use `--format` to limit the rendered outputs (default: all formats) and `--preview` to print the Markdown rendition after generation.

## Streamlit App
Launch the interactive UI:

```bash
streamlit run anyproduct/app.py
```

Upload a JSON file or edit the provided example payload, choose your desired formats, and download the generated documents with one click.

## Adding Generators
1. Create a new module under `anyproduct/generators/`.
2. Subclass `anyproduct.generators.base.Generator` and implement `generate()`.
3. Provide a unique `slug`, a friendly `name`, and (optionally) an `example_input()` for the GUI.

New generators are auto-discovered by both the CLI and GUI—no manual registration required.
