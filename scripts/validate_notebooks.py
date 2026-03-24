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
INDENT_PREFIX = "    "
MARKDOWNISH_PREFIXES = ("- ", "* ", "+ ", "#")
MATH_CORRUPTION_FRAGMENT = "\t" + "ext{"
MIN_INDENTED_MARKDOWN_LINES = 3


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


def has_suspicious_markdown_indentation(source: str) -> bool:
    """Ловит markdown, который случайно превратится в code block.

    Нас интересуют именно учебные текстовые блоки, где большая часть строк
    внезапно начинается с 4+ пробелов и при этом выглядит как обычный
    markdown или LaTeX, а не как намеренный кодовый пример.
    """

    non_empty_lines = [line for line in source.splitlines() if line.strip()]
    if len(non_empty_lines) < MIN_INDENTED_MARKDOWN_LINES:
        return False

    indented_lines = [line for line in non_empty_lines if line.startswith(INDENT_PREFIX)]
    if len(indented_lines) < MIN_INDENTED_MARKDOWN_LINES:
        return False

    # Если indented only небольшой кусок, это ещё не похоже на поломку.
    if len(indented_lines) * 2 < len(non_empty_lines):
        return False

    suspicious_lines = 0
    for line in indented_lines:
        stripped = line.lstrip()
        if (
            stripped.startswith(MARKDOWNISH_PREFIXES)
            or stripped == "$$"
            or "$" in stripped
            or "\\" in stripped
        ):
            suspicious_lines += 1

    return suspicious_lines >= MIN_INDENTED_MARKDOWN_LINES


def has_literal_tab_text_corruption(source: str) -> bool:
    """Ищет типичную поломку `\\text{...}` -> tab + `ext{...}`."""

    return MATH_CORRUPTION_FRAGMENT in source


def validate_markdown_content(path: Path, notebook: nbformat.NotebookNode) -> list[str]:
    """Проверяет markdown-ячейки на поломки, заметные только на рендере."""

    errors: list[str] = []
    relative_path = path.relative_to(ROOT)

    for cell_index, cell in enumerate(notebook.cells):
        if cell.cell_type != "markdown":
            continue

        source = "".join(cell.source)
        if has_suspicious_markdown_indentation(source):
            errors.append(
                f"{relative_path} markdown cell {cell_index}: suspicious leading indentation "
                "would render explanatory markdown as a code block."
            )

        if has_literal_tab_text_corruption(source):
            errors.append(
                f"{relative_path} markdown cell {cell_index}: literal tab before 'ext{{' "
                "suggests a broken '\\text{...}' escape."
            )

    return errors


def main() -> None:
    """Запускает полную проверку всех найденных ноутбуков."""

    notebooks = iter_notebooks()
    if not notebooks:
        raise SystemExit("No notebooks found to validate.")

    # Старые ноутбуки без cell id нам сейчас не мешают, поэтому шумное
    # предупреждение скрываем и оставляем только реальные ошибки структуры.
    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)
    errors: list[str] = []

    for path in notebooks:
        # Сначала читаем ноутбук как формат nbformat, потом валидируем схему.
        with path.open("r", encoding="utf-8") as handle:
            notebook = nbformat.read(handle, as_version=4)
        nbformat.validate(notebook)
        errors.extend(validate_markdown_content(path, notebook))
        print(f"validated: {path.relative_to(ROOT)}")

    if errors:
        raise SystemExit("\n".join(errors))


if __name__ == "__main__":
    main()
