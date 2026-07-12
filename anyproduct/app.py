"""Streamlit UI for AnyProduct Studio."""
from __future__ import annotations

import json
from typing import Dict

import streamlit as st

from .formatters import FormattedOutput, render_outputs, supported_formats
from .registry import available_generators


def _get_generators() -> Dict[str, Generator]:
    generators: Dict[str, Generator] = {}
    for generator_cls in sorted(available_generators(), key=lambda cls: cls.slug):
        generators[generator_cls.slug] = generator_cls()
    return generators


def _render_downloads(outputs: Dict[str, FormattedOutput]) -> None:
    for spec in supported_formats().values():
        if spec.slug not in outputs:
            continue
        output = outputs[spec.slug]
        st.download_button(
            label=f"Download {spec.label}",
            data=output.content,
            file_name=output.filename,
            mime=output.mime_type,
            key=f"download-{spec.slug}",
        )


def main() -> None:
    st.set_page_config(page_title="AnyProduct Studio", layout="wide")
    st.title("AnyProduct Studio")
    st.caption("Create sellable outputs from any structured input.")

    generators = _get_generators()
    if not generators:
        st.warning("No generators were found. Add modules under anyproduct/generators.")
        return

    selected_slug = st.selectbox(
        "Choose a generator", options=list(generators.keys()), format_func=lambda slug: generators[slug].name
    )
    generator = generators[selected_slug]

    st.markdown(f"**Description:** {generator.description or 'No description provided.'}")

    example_json = json.dumps(generator.__class__.example_input(), indent=2)

    st.subheader("Input data")
    uploaded = st.file_uploader("Upload JSON file", type=["json"])

    default_text = example_json
    input_text = default_text
    if uploaded is not None:
        input_text = uploaded.read().decode("utf-8")
    input_text = st.text_area("JSON payload", value=input_text, height=300)

    format_options = st.multiselect(
        "Select output formats",
        options=list(supported_formats().keys()),
        default=list(supported_formats().keys()),
        format_func=lambda slug: supported_formats()[slug].label,
    )

    col1, col2 = st.columns((2, 1))
    with col1:
        generate_clicked = st.button("Generate", type="primary")
    with col2:
        show_example = st.checkbox("Show example payload", value=False)

    if show_example:
        st.code(example_json, language="json")

    if generate_clicked:
        if not format_options:
            st.error("Choose at least one format.")
            return
        try:
            payload = json.loads(input_text)
        except json.JSONDecodeError as exc:
            st.error(f"Input must be valid JSON: {exc}")
            return
        if not isinstance(payload, dict):
            st.error("Input JSON must be an object with key/value pairs.")
            return

        result = generator.generate(payload)
        try:
            outputs = render_outputs(result, format_options)
        except RuntimeError as exc:
            st.error(str(exc))
            return

        st.success("Generation complete!")

        if "markdown" in outputs:
            st.subheader("Preview")
            st.markdown(outputs["markdown"].content.decode("utf-8"))

        st.subheader("Downloads")
        _render_downloads(outputs)


if __name__ == "__main__":  # pragma: no cover
    main()
