"""Command line interface for AnyProduct Studio."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

from .formatters import supported_formats, write_outputs
from .registry import available_generators, get_generator


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AnyProduct Studio CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available generators")
    group.add_argument("--generate", metavar="GENERATOR", help="Generator slug to run")

    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a JSON file used as generator input",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("build"),
        help="Directory where generated files will be written",
    )
    parser.add_argument(
        "--format",
        choices=list(supported_formats().keys()),
        nargs="+",
        default=list(supported_formats().keys()),
        help="Output format(s) to render",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print the Markdown output to stdout after generation",
    )
    return parser.parse_args(argv)


def _load_input(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Input file must be valid JSON: {path}\n{exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Input JSON must be an object at the top level")
    return data


def _list_generators() -> int:
    lines: List[str] = []
    for generator_cls in sorted(available_generators(), key=lambda cls: cls.slug):
        lines.append(f"{generator_cls.slug}: {generator_cls.name}")
        if generator_cls.description:
            lines.append(f"    {generator_cls.description}")
    if not lines:
        lines.append("No generators were discovered.")
    print("\n".join(lines))
    return 0


def _run_generator(slug: str, data_path: Path, out_dir: Path, formats: List[str], preview: bool) -> int:
    generator_cls = get_generator(slug)
    payload = _load_input(data_path)
    generator = generator_cls()
    result = generator.generate(payload)
    try:
        written = write_outputs(result, formats, out_dir)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    for fmt, output_path in written.items():
        print(f"✔ Generated {fmt.upper()} -> {output_path}")
    if preview and "markdown" in written:
        markdown_path = written["markdown"]
        print()
        print(markdown_path.read_text() if markdown_path.exists() else "")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if args.list:
        return _list_generators()
    if args.generate:
        if args.input is None:
            raise SystemExit("--input is required when using --generate")
        return _run_generator(args.generate, args.input, args.out, args.format, args.preview)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
