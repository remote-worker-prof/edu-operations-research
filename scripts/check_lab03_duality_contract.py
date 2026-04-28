"""Проверяет учебный контракт notebook-ов ЛР-03 по двойственности.

Контракт защищает тот же уровень читаемости, который уже закреплен для ЛР-02:
русские docstrings, аккуратные LP-обозначения, табличный вывод и многострочное
форматирование векторов и матриц.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
import warnings

import nbformat
from nbformat.warnings import MissingIDFieldWarning


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "03-lab-duality-sensitivity"
MAX_CODE_LINE_LENGTH = 100

EXPECTED_DATA = {
    "examples-civil/lab_03_example_civil_01.ipynb": {
        "effects": [
            90,
            78,
            70,
            96,
        ],
        "A_ub": [
            [40, 28, 22, 48],
            [20, 24, 12, 26],
            [16, 12, 10, 20],
        ],
        "b_ub": [
            88,
            52,
            42,
        ],
    },
    "examples-civil/lab_03_example_civil_02.ipynb": {
        "effects": [
            82,
            71,
            76,
            94,
        ],
        "A_ub": [
            [30, 22, 26, 48],
            [22, 11, 18, 25],
            [12, 10, 13, 19],
        ],
        "b_ub": [
            90,
            54,
            44,
        ],
    },
    "examples-civil/lab_03_example_civil_03.ipynb": {
        "effects": [
            90,
            72,
            64,
            98,
        ],
        "A_ub": [
            [42, 20, 16, 52],
            [17, 9, 19, 26],
            [16, 8, 7, 23],
        ],
        "b_ub": [
            94,
            56,
            48,
        ],
    },
    "examples-military/lab_03_example_military_01.ipynb": {
        "effects": [
            84,
            79,
            68,
            96,
        ],
        "A_ub": [
            [34, 28, 18, 46],
            [16, 13, 9, 24],
            [15, 12, 8, 20],
        ],
        "b_ub": [
            92,
            55,
            46,
        ],
    },
    "examples-military/lab_03_example_military_02.ipynb": {
        "effects": [
            87,
            83,
            76,
            69,
        ],
        "A_ub": [
            [36, 32, 24, 18],
            [17, 15, 18, 8],
            [16, 14, 11, 9],
        ],
        "b_ub": [
            95,
            58,
            47,
        ],
    },
    "examples-military/lab_03_example_military_03.ipynb": {
        "effects": [
            89,
            85,
            73,
            77,
        ],
        "A_ub": [
            [38, 34, 22, 26],
            [20, 18, 11, 15],
            [15, 14, 9, 12],
        ],
        "b_ub": [
            91,
            57,
            45,
        ],
    },
    "lab_03_student_civil_01.ipynb": {
        "effects": [
            88,
            74,
            68,
            95,
        ],
        "A_ub": [
            [38, 26, 20, 50],
            [18, 22, 10, 27],
            [16, 11, 9, 21],
        ],
        "b_ub": [
            92,
            58,
            46,
        ],
    },
    "lab_03_student_civil_02.ipynb": {
        "effects": [
            97,
            76,
            70,
            92,
        ],
        "A_ub": [
            [46, 24, 18, 44],
            [24, 16, 14, 28],
            [18, 9, 12, 22],
        ],
        "b_ub": [
            96,
            60,
            50,
        ],
    },
    "lab_03_student_military_01.ipynb": {
        "effects": [
            86,
            72,
            78,
            93,
        ],
        "A_ub": [
            [34, 22, 28, 46],
            [16, 18, 14, 24],
            [15, 10, 13, 21],
        ],
        "b_ub": [
            94,
            56,
            48,
        ],
    },
    "lab_03_student_military_02.ipynb": {
        "effects": [
            80,
            74,
            88,
            92,
        ],
        "A_ub": [
            [28, 24, 36, 44],
            [14, 11, 21, 24],
            [12, 10, 16, 18],
        ],
        "b_ub": [
            90,
            54,
            44,
        ],
    },
}

COMMON_MARKERS = (
    "effects",
    "A_ub",
    "b_ub",
    "bounds",
    "c",
    "linprog",
    "shadow_prices",
    "slack",
    "binding",
)

WORKED_MARKERS = (
    "solve_primal",
    "solve_dual",
    "rerun_with_resource_change",
    "display(",
    "np.allclose",
    "Аргументы:",
    "Возвращает:",
    "Исключения:",
)

FORBIDDEN_ENGLISH_DOCSTRING_SECTIONS = (
    "Args:",
    "Returns:",
    "Raises:",
)

FORBIDDEN_ENGLISH_COMMENTS = (
    "# Step ",
    "# Hint:",
    "task statement",
    "readable form",
    "solve only after",
)

ARRAY_ASSIGNMENT_PATTERN = re.compile(
    r"(?P<name>effects|A_ub|b_ub) = np\.array\(\n"
    r"(?P<body>.*?)"
    r"\n\)",
    flags=re.DOTALL,
)


def read_notebook(path: Path) -> nbformat.NotebookNode:
    """Читает один notebook и проверяет его JSON-схему."""

    with path.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)
    nbformat.validate(notebook)
    return notebook


def notebook_source(notebook: nbformat.NotebookNode) -> str:
    """Объединяет исходники всех ячеек в одну строку для поиска."""

    return "\n".join("".join(cell.source) for cell in notebook.cells)


def code_sources(notebook: nbformat.NotebookNode) -> list[str]:
    """Возвращает исходники только code cells."""

    return [
        "".join(cell.source)
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]


def parse_code_cell(source: str, relative_path: Path, cell_index: int) -> ast.Module:
    """Разбирает code cell и указывает notebook при синтаксической ошибке."""

    try:
        return ast.parse(source)
    except SyntaxError as error:
        raise SystemExit(
            f"{relative_path} code cell {cell_index}: syntax error: {error}"
        ) from error


def literal_np_array(node: ast.AST) -> object | None:
    """Достает первый аргумент из простого вызова ``np.array([...])``."""

    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Attribute):
        return None
    if not isinstance(node.func.value, ast.Name):
        return None
    if node.func.value.id != "np" or node.func.attr != "array":
        return None
    if not node.args:
        return None
    return ast.literal_eval(node.args[0])


def extract_numeric_statement(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
) -> dict[str, object]:
    """Достает исходные массивы ``effects``, ``A_ub`` и ``b_ub``."""

    extracted: dict[str, object] = {}
    wanted_names = {"effects", "A_ub", "b_ub"}

    for cell_index, source in enumerate(code_sources(notebook)):
        tree = parse_code_cell(source, relative_path, cell_index)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id not in wanted_names or target.id in extracted:
                    continue
                value = literal_np_array(node.value)
                if value is not None:
                    extracted[target.id] = value

    return extracted


def calls_function(tree: ast.Module, call_name: str) -> bool:
    """Проверяет, есть ли в AST вызов функции с заданным именем."""

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == call_name:
            return True
    return False


def has_uncommented_call(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
    call_name: str,
) -> bool:
    """Проверяет, вызывается ли функция вне комментариев."""

    for cell_index, source in enumerate(code_sources(notebook)):
        tree = parse_code_cell(source, relative_path, cell_index)
        if calls_function(tree, call_name):
            return True
    return False


def check_code_style(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
    errors: list[str],
) -> None:
    """Проверяет простые правила читаемости code cells."""

    for cell_index, source in enumerate(code_sources(notebook)):
        parse_code_cell(source, relative_path, cell_index)

        for line_number, line in enumerate(source.splitlines(), start=1):
            if "\t" in line:
                errors.append(
                    f"{relative_path} code cell {cell_index}, line {line_number}: "
                    "tabs are not allowed."
                )
            if len(line) > MAX_CODE_LINE_LENGTH:
                errors.append(
                    f"{relative_path} code cell {cell_index}, line {line_number}: "
                    f"line is too long ({len(line)} > {MAX_CODE_LINE_LENGTH})."
                )


def check_russian_docstrings(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
    errors: list[str],
) -> None:
    """Проверяет русские Google-style секции в docstrings функций ЛР-03."""

    for cell_index, source in enumerate(code_sources(notebook)):
        tree = parse_code_cell(source, relative_path, cell_index)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            docstring = ast.get_docstring(node) or ""
            if not docstring:
                errors.append(
                    f"{relative_path} code cell {cell_index}: "
                    f"function {node.name!r} must have a Russian docstring."
                )
                continue

            for section in FORBIDDEN_ENGLISH_DOCSTRING_SECTIONS:
                if section in docstring:
                    errors.append(
                        f"{relative_path} code cell {cell_index}: "
                        f"function {node.name!r} uses English docstring "
                        f"section {section!r}."
                    )

            for section in ("Аргументы:", "Возвращает:", "Исключения:"):
                if section not in docstring:
                    errors.append(
                        f"{relative_path} code cell {cell_index}: "
                        f"function {node.name!r} misses Russian section "
                        f"{section!r}."
                    )


def check_russian_comments(source: str, relative_path: Path, errors: list[str]) -> None:
    """Не дает вернуть английские учебные комментарии в ЛР-03."""

    for fragment in FORBIDDEN_ENGLISH_COMMENTS:
        if fragment in source:
            errors.append(
                f"{relative_path}: code comments still contain English fragment "
                f"{fragment!r}."
            )


def check_array_formatting(
    source: str,
    relative_path: Path,
    expected: dict[str, object],
    errors: list[str],
) -> None:
    """Проверяет многострочное форматирование векторов и матрицы ресурсов."""

    matches = {
        match.group("name"): match.group("body").splitlines()
        for match in ARRAY_ASSIGNMENT_PATTERN.finditer(source)
    }

    for name in ("effects", "A_ub", "b_ub"):
        lines = matches.get(name)
        if lines is None:
            errors.append(f"{relative_path}: missing formatted {name} np.array block.")
            continue

        if not lines or lines[0] != "    [":
            errors.append(
                f"{relative_path}: {name} must open with an indented '[' line."
            )
        if len(lines) < 3 or lines[-1] != "    dtype=float,":
            errors.append(
                f"{relative_path}: {name} must keep dtype=float on its own "
                "indented line."
            )
        if len(lines) < 2 or lines[-2] != "    ],":
            errors.append(f"{relative_path}: {name} np.array block is malformed.")

        value_lines = lines[1:-2]
        if name == "A_ub":
            expected_rows = expected["A_ub"]
            row_lines = [line for line in value_lines if line.strip()]
            if len(row_lines) != len(expected_rows):
                errors.append(
                    f"{relative_path}: A_ub must have one source line per "
                    "matrix row."
                )
            for line in row_lines:
                if not re.fullmatch(r"        \[[0-9, ]+\],", line):
                    errors.append(
                        f"{relative_path}: A_ub row is not a clean indented "
                        f"matrix row: {line!r}."
                    )
        else:
            expected_values = expected[name]
            item_lines = [line for line in value_lines if line.strip()]
            if len(item_lines) != len(expected_values):
                errors.append(
                    f"{relative_path}: {name} must have one source line per "
                    "vector element."
                )
            for line in item_lines:
                if not re.fullmatch(r"        [0-9]+,", line):
                    errors.append(
                        f"{relative_path}: {name} element is not cleanly "
                        f"indented: {line!r}."
                    )


def check_notebook(
    relative_name: str,
    expected: dict[str, object],
    errors: list[str],
) -> None:
    """Проверяет один notebook ЛР-03 по контракту двойственности."""

    relative_path = Path(relative_name)
    path = LAB_ROOT / relative_path
    if not path.exists():
        errors.append(f"{relative_path}: notebook is missing.")
        return

    notebook = read_notebook(path)
    source = notebook_source(notebook)

    extracted = extract_numeric_statement(notebook, relative_path)
    if extracted != expected:
        errors.append(
            f"{relative_path}: original effects/A_ub/b_ub changed. "
            f"expected {expected!r}, got {extracted!r}."
        )

    for marker in COMMON_MARKERS:
        if marker not in source:
            errors.append(f"{relative_path}: missing common marker {marker!r}.")

    check_code_style(notebook, relative_path, errors)
    check_russian_docstrings(notebook, relative_path, errors)
    check_russian_comments(source, relative_path, errors)
    check_array_formatting(source, relative_path, expected, errors)

    is_worked_example = "_example_" in path.name
    is_student = "_student_" in path.name

    if is_worked_example:
        for marker in WORKED_MARKERS:
            if marker not in source:
                errors.append(f"{relative_path}: missing worked marker {marker!r}.")
        if "TODO" in source:
            errors.append(f"{relative_path}: worked example must not contain TODO.")
        if not has_uncommented_call(notebook, relative_path, "linprog"):
            errors.append(f"{relative_path}: worked example must call linprog.")

    if is_student:
        if "TODO" not in source:
            errors.append(f"{relative_path}: student notebook must contain TODO.")
        if has_uncommented_call(notebook, relative_path, "linprog"):
            errors.append(
                f"{relative_path}: student notebook must not contain a complete "
                "uncommented linprog solve block."
            )


def main() -> None:
    """Запускает проверку контракта notebook-ов ЛР-03."""

    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    errors: list[str] = []
    expected_paths = set(EXPECTED_DATA)
    actual_paths = {
        path.relative_to(LAB_ROOT).as_posix()
        for path in LAB_ROOT.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in path.parts
    }

    missing = sorted(expected_paths - actual_paths)
    unexpected = sorted(actual_paths - expected_paths)
    if missing:
        errors.append(f"missing Lab 03 notebooks: {missing!r}.")
    if unexpected:
        errors.append(f"unexpected Lab 03 notebooks: {unexpected!r}.")

    for relative_name, expected in EXPECTED_DATA.items():
        check_notebook(relative_name, expected, errors)

    if errors:
        raise SystemExit("\n".join(errors))

    for relative_name in sorted(EXPECTED_DATA):
        print(f"lab03-contract-ok: {Path('03-lab-duality-sensitivity') / relative_name}")


if __name__ == "__main__":
    main()
