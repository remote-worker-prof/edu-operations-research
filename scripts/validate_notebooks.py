"""Проверяет, что учебные ноутбуки проекта читаются и проходят schema-validation.

Скрипт нужен как быстрая "проверка здоровья" курса: если ноутбук сломан,
Jupyter Book и CI заметят проблему заранее, а студент не столкнётся с ней в
середине лабораторной работы.
"""

from __future__ import annotations

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


def iter_notebooks() -> list[Path]:
    """Собирает все ноутбуки проекта, которые нужно проверить.

    Returns:
        list[Path]: Отсортированный список путей к ноутбукам без служебных папок.
    """

    notebooks: list[Path] = []
    for path in ROOT.rglob("*.ipynb"):
        # Пропускаем служебные каталоги, чтобы проверять только учебные материалы.
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        notebooks.append(path)
    return sorted(notebooks)


def main() -> None:
    """Запускает полную проверку всех найденных ноутбуков."""

    notebooks = iter_notebooks()
    if not notebooks:
        raise SystemExit("No notebooks found to validate.")

    # Старые ноутбуки без cell id нам сейчас не мешают, поэтому шумное
    # предупреждение скрываем и оставляем только реальные ошибки структуры.
    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    for path in notebooks:
        # Сначала читаем ноутбук как формат nbformat, потом валидируем схему.
        with path.open("r", encoding="utf-8") as handle:
            notebook = nbformat.read(handle, as_version=4)
        nbformat.validate(notebook)
        print(f"validated: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
