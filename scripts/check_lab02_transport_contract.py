"""Проверяет учебный контракт транспортных notebook-ов ЛР-02.

Проверка намеренно узкая: она защищает notebook-и транспортной задачи после
расширения LP-теории, но не навязывает тот же стиль другим лабораторным.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
import warnings

import nbformat
from nbformat.warnings import MissingIDFieldWarning


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "02-lab-transport-problem"
MAX_CODE_LINE_LENGTH = 100

EXPECTED_DATA = {
    "examples-civil/lab_02_example_civil_01.ipynb": {
        "supplies": [
            35,
            50,
            40,
        ],
        "demands": [
            20,
            30,
            25,
            50,
        ],
        "costs": [
            [4, 6, 8, 13],
            [5, 4, 7, 9],
            [6, 3, 4, 7],
        ],
    },
    "examples-civil/lab_02_example_civil_02.ipynb": {
        "supplies": [
            25,
            45,
            35,
        ],
        "demands": [
            15,
            30,
            25,
            35,
        ],
        "costs": [
            [4, 8, 50, 9],
            [6, 5, 7, 8],
            [7, 4, 6, 5],
        ],
    },
    "examples-civil/lab_02_example_civil_03.ipynb": {
        "supplies": [
            28,
            32,
            25,
        ],
        "demands": [
            18,
            22,
            20,
            15,
        ],
        "costs": [
            [4, 5, 7, 8],
            [6, 4, 5, 7],
            [7, 6, 4, 6],
        ],
    },
    "examples-military/lab_02_example_military_01.ipynb": {
        "supplies": [
            24,
            30,
            26,
        ],
        "demands": [
            18,
            20,
            16,
            26,
        ],
        "costs": [
            [5, 6, 8, 9],
            [4, 5, 7, 8],
            [7, 5, 4, 6],
        ],
    },
    "examples-military/lab_02_example_military_02.ipynb": {
        "supplies": [
            42,
            28,
            20,
        ],
        "demands": [
            20,
            18,
            16,
            14,
        ],
        "costs": [
            [4, 7, 8, 9],
            [5, 4, 6, 7],
            [7, 6, 4, 5],
        ],
    },
    "examples-military/lab_02_example_military_03.ipynb": {
        "supplies": [
            18,
            24,
            20,
        ],
        "demands": [
            14,
            18,
            16,
            22,
        ],
        "costs": [
            [6, 5, 8, 10],
            [5, 4, 6, 7],
            [7, 6, 5, 6],
        ],
    },
    "lab_02_student_civil_01.ipynb": {
        "supplies": [
            30,
            40,
            35,
        ],
        "demands": [
            20,
            25,
            30,
            30,
        ],
        "costs": [
            [5, 7, 6, 10],
            [8, 4, 5, 7],
            [6, 6, 4, 5],
        ],
    },
    "lab_02_student_civil_02.ipynb": {
        "supplies": [
            40,
            35,
            30,
        ],
        "demands": [
            20,
            25,
            30,
            15,
        ],
        "costs": [
            [4, 6, 8, 7],
            [5, 4, 7, 6],
            [6, 5, 4, 8],
        ],
    },
    "lab_02_student_military_01.ipynb": {
        "supplies": [
            50,
            40,
            35,
        ],
        "demands": [
            30,
            25,
            35,
            35,
        ],
        "costs": [
            [6, 7, 9, 12],
            [5, 4, 8, 10],
            [8, 6, 5, 7],
        ],
    },
    "lab_02_student_military_02.ipynb": {
        "supplies": [
            25,
            30,
            20,
        ],
        "demands": [
            15,
            20,
            18,
            30,
        ],
        "costs": [
            [7, 5, 9, 11],
            [6, 4, 7, 8],
            [8, 6, 5, 7],
        ],
    },
}

COMMON_MARKERS = (
    "A_eq",
    "b_eq",
    "bounds",
    "route_index",
    "balance_transport_problem",
    "build_transport_lp",
)

WORKED_MARKERS = (
    "solve_transport_problem",
    "make_plan_frame",
    "make_used_routes_frame",
    "make_balance_check_frames",
    "Аргументы:",
    "Возвращает:",
    "Исключения:",
    "display(",
    "np.allclose",
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
    r"(?P<name>supplies|demands|costs) = np\.array\(\n"
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
    except SyntaxError as exc:
        raise AssertionError(
            f"{relative_path} code cell {cell_index} has invalid Python: {exc}"
        ) from exc


def literal_np_array(node: ast.AST) -> object | None:
    """Достает первый аргумент из простого вызова ``np.array([...])``."""

    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "array":
        return None
    if not node.args:
        return None
    return ast.literal_eval(node.args[0])


def extract_numeric_statement(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
) -> dict[str, object]:
    """Достает исходные массивы ``supplies``, ``demands`` и ``costs``."""

    extracted: dict[str, object] = {}
    wanted_names = {"supplies", "demands", "costs"}

    for cell_index, source in enumerate(code_sources(notebook)):
        tree = parse_code_cell(source, relative_path, cell_index)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue

            target_name = node.targets[0].id
            if target_name not in wanted_names or target_name in extracted:
                continue

            value = literal_np_array(node.value)
            if value is not None:
                extracted[target_name] = value

    return extracted


def has_uncommented_call(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
    call_name: str,
) -> bool:
    """Проверяет, вызывается ли функция вне комментариев."""

    for cell_index, source in enumerate(code_sources(notebook)):
        tree = parse_code_cell(source, relative_path, cell_index)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == call_name:
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
        for line_index, line in enumerate(source.splitlines(), start=1):
            if "\t" in line:
                errors.append(
                    f"{relative_path} code cell {cell_index} line {line_index}: "
                    "tabs are not allowed."
                )
            if len(line) > MAX_CODE_LINE_LENGTH:
                errors.append(
                    f"{relative_path} code cell {cell_index} line {line_index}: "
                    f"line is longer than {MAX_CODE_LINE_LENGTH} characters."
                )


def check_russian_docstrings(
    notebook: nbformat.NotebookNode,
    relative_path: Path,
    errors: list[str],
) -> None:
    """Проверяет русские Google-style секции в docstrings функций ЛР-02."""

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

            for section in ("Аргументы:", "Возвращает:"):
                if section not in docstring:
                    errors.append(
                        f"{relative_path} code cell {cell_index}: "
                        f"function {node.name!r} misses Russian section "
                        f"{section!r}."
                    )

            if node.name == "solve_transport_problem" and "Исключения:" not in docstring:
                errors.append(
                    f"{relative_path} code cell {cell_index}: "
                    "solve_transport_problem must document 'Исключения:'."
                )


def check_russian_comments(source: str, relative_path: Path, errors: list[str]) -> None:
    """Не дает вернуть английские учебные комментарии в ЛР-02."""

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
    """Проверяет многострочное форматирование векторов и матрицы затрат."""

    matches = {
        match.group("name"): match.group("body").splitlines()
        for match in ARRAY_ASSIGNMENT_PATTERN.finditer(source)
    }

    for name in ("supplies", "demands", "costs"):
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
        if name == "costs":
            expected_rows = expected["costs"]
            row_lines = [line for line in value_lines if line.strip()]
            if len(row_lines) != len(expected_rows):
                errors.append(
                    f"{relative_path}: costs must have one source line per "
                    "matrix row."
                )
            for line in row_lines:
                if not re.fullmatch(r"        \[[0-9, ]+\],", line):
                    errors.append(
                        f"{relative_path}: costs row is not a clean indented "
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
    """Проверяет один notebook ЛР-02 по контракту транспортной задачи."""

    relative_path = Path(relative_name)
    path = LAB_ROOT / relative_path
    notebook = read_notebook(path)
    source = notebook_source(notebook)

    extracted = extract_numeric_statement(notebook, relative_path)
    for name, expected_value in expected.items():
        if extracted.get(name) != expected_value:
            errors.append(
                f"{relative_path}: {name} changed. "
                f"Expected {expected_value}, got {extracted.get(name)}."
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
        if "TODO" in source:
            errors.append(f"{relative_path}: worked examples must not contain TODO.")
        for marker in WORKED_MARKERS:
            if marker not in source:
                errors.append(
                    f"{relative_path}: missing worked-example marker {marker!r}."
                )
        if not has_uncommented_call(notebook, relative_path, "linprog"):
            errors.append(f"{relative_path}: worked example must call linprog.")

    if is_student:
        if "TODO" not in source:
            errors.append(f"{relative_path}: student notebook must contain TODO.")
        if not has_uncommented_call(notebook, relative_path, "build_transport_lp"):
            errors.append(
                f"{relative_path}: student notebook must show build_transport_lp usage."
            )
        if has_uncommented_call(notebook, relative_path, "linprog"):
            errors.append(
                f"{relative_path}: student notebook must not contain a ready solver call."
            )


def main() -> None:
    """Запускает проверку контракта транспортных notebook-ов ЛР-02."""

    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    found = {
        path.relative_to(LAB_ROOT).as_posix()
        for path in LAB_ROOT.rglob("*.ipynb")
    }
    expected = set(EXPECTED_DATA)
    errors: list[str] = []

    if found != expected:
        errors.append(
            "Lab 02 notebook set mismatch. "
            f"Expected {sorted(expected)}, found {sorted(found)}."
        )

    for relative_name, expected_data in EXPECTED_DATA.items():
        check_notebook(relative_name, expected_data, errors)

    if errors:
        raise SystemExit("\n".join(errors))

    for relative_name in sorted(EXPECTED_DATA):
        print(f"lab02-contract-ok: 02-lab-transport-problem/{relative_name}")


if __name__ == "__main__":
    main()
