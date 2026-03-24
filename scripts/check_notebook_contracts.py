"""Проверяет ролевой контракт учебных notebook-ов после реструктуризации.

Идея простая: в корне каждой опубликованной лаборатории должны лежать только
student notebooks, а полностью разобранные worked examples должны жить только
в `examples-civil/` и `examples-military/`.
"""

from __future__ import annotations

from pathlib import Path
import re
import warnings

import nbformat
from nbformat.warnings import MissingIDFieldWarning
import yaml


ROOT = Path(__file__).resolve().parents[1]
TOC_PATH = ROOT / "_toc.yml"
EXCLUDED_PARTS = {
    ".beads",
    ".git",
    ".jupyter_cache",
    ".ipynb_checkpoints",
    ".serena",
    ".venv",
    "_build",
}
LAB_ROOT_PATTERN = re.compile(r"^\d{2}-")
STUDENT_COUNT = 4
EXAMPLE_COUNT_PER_TRACK = 3
EXPECTED_STUDENT_SPLIT = 2


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


def iter_toc_files(node: object) -> list[Path]:
    """Достаёт все `file:` записи из `_toc.yml`."""

    files: list[Path] = []
    if isinstance(node, dict):
        file_name = node.get("file")
        if isinstance(file_name, str):
            files.append(Path(file_name))
        for value in node.values():
            files.extend(iter_toc_files(value))
    elif isinstance(node, list):
        for item in node:
            files.extend(iter_toc_files(item))
    return files


def discover_published_lab_roots() -> list[Path]:
    """Находит опубликованные numbered labs через `_toc.yml`."""

    with TOC_PATH.open("r", encoding="utf-8") as handle:
        toc = yaml.safe_load(handle)

    lab_roots = {
        Path(file_path.parts[0])
        for file_path in iter_toc_files(toc)
        if len(file_path.parts) >= 2 and LAB_ROOT_PATTERN.match(file_path.parts[0])
    }
    return sorted(lab_roots)


def main() -> None:
    """Проверяет, что структура notebook-ов совпадает с учебным контрактом."""

    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    errors: list[str] = []
    lab_roots = discover_published_lab_roots()
    if not lab_roots:
        raise SystemExit("No published numbered lab roots found in _toc.yml.")

    for relative_lab_root in lab_roots:
        lab_root = ROOT / relative_lab_root
        checked: list[Path] = []
        if not lab_root.is_dir():
            errors.append(f"{relative_lab_root} is listed in _toc.yml but is not a directory.")
            continue

        root_notebooks = sorted(
            path
            for path in lab_root.glob("*.ipynb")
            if not is_excluded(path)
        )

        if len(root_notebooks) != STUDENT_COUNT:
            errors.append(
                f"{relative_lab_root}: expected {STUDENT_COUNT} student notebooks in root, "
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

        if civil_students != EXPECTED_STUDENT_SPLIT:
            errors.append(
                f"{relative_lab_root}: expected {EXPECTED_STUDENT_SPLIT} civil student notebooks, "
                f"found {civil_students}."
            )
        if military_students != EXPECTED_STUDENT_SPLIT:
            errors.append(
                f"{relative_lab_root}: expected {EXPECTED_STUDENT_SPLIT} military student notebooks, "
                f"found {military_students}."
            )

        for track in ("examples-civil", "examples-military"):
            examples_dir = lab_root / track
            example_notebooks = sorted(
                path
                for path in examples_dir.glob("*.ipynb")
                if not is_excluded(path)
            )

            if len(example_notebooks) != EXAMPLE_COUNT_PER_TRACK:
                errors.append(
                    f"{examples_dir.relative_to(ROOT)}: expected "
                    f"{EXAMPLE_COUNT_PER_TRACK} worked examples, "
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
                f"{path.relative_to(ROOT)} is outside the allowed notebook layout for "
                f"{relative_lab_root}."
            )

    if errors:
        raise SystemExit("\n".join(errors))

    for relative_lab_root in lab_roots:
        for path in sorted(iter_notebooks(ROOT / relative_lab_root)):
            print(f"contract-ok: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
