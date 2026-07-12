"""Base classes and dataclasses for AnyProduct generators."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence


@dataclass
class Section:
    """A text section inside a generated document."""

    title: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class Table:
    """Structured tabular data."""

    name: str
    columns: Sequence[str]
    rows: List[Mapping[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "columns": list(self.columns),
            "rows": [dict(row) for row in self.rows],
        }


@dataclass
class GeneratorResult:
    """The canonical representation produced by a generator."""

    title: str
    summary: str = ""
    sections: List[Section] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_section(self, title: str, content: str) -> None:
        self.sections.append(Section(title=title, content=content))

    def add_table(
        self, name: str, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]
    ) -> None:
        self.tables.append(Table(name=name, columns=columns, rows=list(rows)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": [section.to_dict() for section in self.sections],
            "tables": [table.to_dict() for table in self.tables],
            "metadata": dict(self.metadata),
        }


class Generator:
    """Base class for generator plugins."""

    #: Unique identifier used on the command line.
    slug: str = ""
    #: Human readable display name.
    name: str = "Generator"
    #: Short description of what the generator creates.
    description: str = ""

    def __init_subclass__(cls) -> None:  # pragma: no cover - metadata validation
        super().__init_subclass__()
        if cls.slug and not cls.slug.isidentifier():
            raise ValueError(f"Generator slug '{cls.slug}' must be a valid identifier")

    @classmethod
    def example_input(cls) -> Mapping[str, Any]:
        """Return an example JSON-serialisable payload."""

        return {}

    def generate(self, payload: Mapping[str, Any]) -> GeneratorResult:  # pragma: no cover
        """Generate a :class:`GeneratorResult` from ``payload``.

        Subclasses must override this method.
        """

        raise NotImplementedError
