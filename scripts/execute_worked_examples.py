"""Ищет и исполняет все worked examples проекта.

Скрипт нужен для CI и локальной проверки после перехода на discovery-based
структуру: мы больше не хардкодим по одному notebook-у на лабораторную.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


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


def is_excluded(path: Path) -> bool:
    """Пропускает служебные каталоги."""

    return any(part in EXCLUDED_PARTS for part in path.parts)


def iter_worked_examples() -> list[Path]:
    """Находит все notebook-и внутри examples-папок."""

    notebooks: list[Path] = []
    for path in ROOT.rglob("*.ipynb"):
        if is_excluded(path):
            continue
        if "examples-civil" not in path.parts and "examples-military" not in path.parts:
            continue
        if "_example_" not in path.name:
            continue
        notebooks.append(path)
    return sorted(notebooks)


def execute_notebook(path: Path) -> None:
    """Исполняет один notebook на месте через nbconvert."""

    command = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        "--ExecutePreprocessor.timeout=180",
        str(path),
    ]
    subprocess.run(command, check=True, cwd=ROOT)


def main() -> None:
    """Исполняет все найденные worked examples."""

    notebooks = iter_worked_examples()
    if not notebooks:
        raise SystemExit("No worked examples found to execute.")

    for path in notebooks:
        print(f"executing: {path.relative_to(ROOT)}")
        execute_notebook(path)


if __name__ == "__main__":
    main()
