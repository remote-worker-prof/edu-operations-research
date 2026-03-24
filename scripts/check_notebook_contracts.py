"""Проверяет ролевой контракт учебных notebook-ов после реструктуризации.

Идея простая: в корне каждой лаборатории должны лежать только student notebooks,
а полностью разобранные worked examples должны жить только в
`examples-civil/` и `examples-military/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import nbformat
from nbformat.warnings import MissingIDFieldWarning


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".beads",
    ".git",
    ".jupyter_cache",
    ".ipynb_checkpoints",
    ".serena",
    ".venv",
    "_build",
}


@dataclass(frozen=True)
class LabSpec:
    root: str
    student_count: int = 4
    example_count_per_track: int = 3


LAB_SPECS = (
    LabSpec("01-lab-essentials"),
    LabSpec("02-lab-transport-problem"),
    LabSpec("03-lab-duality-sensitivity"),
)


def is_excluded(path: Path) -> bool:
    """Возвращает True для служебных путей, которые не нужно анализировать."""

    return any(part in EXCLUDED_PARTS for part in path.parts)


def read_notebook(path: Path) -> nbformat.NotebookNode:
    """Читает notebook и одновременно валидирует его базовую структуру."""

    with path.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)
    nbformat.validate(notebook)
    return notebook


def contains_marker(notebook: nbformat.NotebookNode, marker: str) -> bool:
    """Ищет обязательный текстовый маркер в markdown-ячейках."""

    for cell in notebook.cells:
        if cell.cell_type != "markdown":
            continue
        source = "".join(cell.source)
        if marker in source:
            return True
    return False


def iter_notebooks(path: Path) -> list[Path]:
    """Собирает notebook-и внутри каталога без служебных папок."""

    paths = []
    for notebook_path in path.rglob("*.ipynb"):
        if is_excluded(notebook_path):
            continue
        paths.append(notebook_path)
    return sorted(paths)


def main() -> None:
    """Проверяет, что структура notebook-ов совпадает с учебным контрактом."""

    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    errors: list[str] = []
    checked: list[Path] = []

    for spec in LAB_SPECS:
        lab_root = ROOT / spec.root
        root_notebooks = sorted(
            path
            for path in lab_root.glob("*.ipynb")
            if not is_excluded(path)
        )

        if len(root_notebooks) != spec.student_count:
            errors.append(
                f"{spec.root}: expected {spec.student_count} student notebooks in root, "
                f"found {len(root_notebooks)}."
            )

        civil_students = 0
        military_students = 0

        for path in root_notebooks:
            checked.append(path)
            if "_student_" not in path.name:
                errors.append(f"{path.relative_to(ROOT)} must use '_student_' in file name.")
                continue

            if "_civil_" in path.name:
                civil_students += 1
            if "_military_" in path.name:
                military_students += 1

            notebook = read_notebook(path)
            if not contains_marker(notebook, "Student notebook:"):
                errors.append(
                    f"{path.relative_to(ROOT)} must contain a 'Student notebook:' marker."
                )

        if civil_students != 2:
            errors.append(f"{spec.root}: expected 2 civil student notebooks, found {civil_students}.")
        if military_students != 2:
            errors.append(
                f"{spec.root}: expected 2 military student notebooks, found {military_students}."
            )

        for track in ("examples-civil", "examples-military"):
            examples_dir = lab_root / track
            example_notebooks = sorted(
                path
                for path in examples_dir.glob("*.ipynb")
                if not is_excluded(path)
            )

            if len(example_notebooks) != spec.example_count_per_track:
                errors.append(
                    f"{examples_dir.relative_to(ROOT)}: expected "
                    f"{spec.example_count_per_track} worked examples, "
                    f"found {len(example_notebooks)}."
                )

            for path in example_notebooks:
                checked.append(path)
                if "_example_" not in path.name:
                    errors.append(
                        f"{path.relative_to(ROOT)} must use '_example_' in file name."
                    )
                    continue

                notebook = read_notebook(path)
                if not contains_marker(notebook, "Worked example:"):
                    errors.append(
                        f"{path.relative_to(ROOT)} must contain a 'Worked example:' marker."
                    )

        unexpected = sorted(set(iter_notebooks(lab_root)) - set(checked))
        for path in unexpected:
            errors.append(
                f"{path.relative_to(ROOT)} is outside the allowed notebook layout for {spec.root}."
            )

    if errors:
        raise SystemExit("\n".join(errors))

    for path in sorted(checked):
        print(f"contract-ok: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
