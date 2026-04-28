"""Checks the educational code contract for Lab 02 transport notebooks.

The check is intentionally narrow: it protects the transport-problem notebooks
after the LP theory was expanded, without forcing the same code style on other
laboratory works.
"""

from __future__ import annotations

import ast
from pathlib import Path
import warnings

import nbformat
from nbformat.warnings import MissingIDFieldWarning


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "02-lab-transport-problem"
MAX_CODE_LINE_LENGTH = 100

EXPECTED_DATA = {
    "examples-civil/lab_02_example_civil_01.ipynb": {
        "supplies": [35, 50, 40],
        "demands": [20, 30, 25, 50],
        "costs": [[4, 6, 8, 13], [5, 4, 7, 9], [6, 3, 4, 7]],
    },
    "examples-civil/lab_02_example_civil_02.ipynb": {
        "supplies": [25, 45, 35],
        "demands": [15, 30, 25, 35],
        "costs": [[4, 8, 50, 9], [6, 5, 7, 8], [7, 4, 6, 5]],
    },
    "examples-civil/lab_02_example_civil_03.ipynb": {
        "supplies": [28, 32, 25],
        "demands": [18, 22, 20, 15],
        "costs": [[4, 5, 7, 8], [6, 4, 5, 7], [7, 6, 4, 6]],
    },
    "examples-military/lab_02_example_military_01.ipynb": {
        "supplies": [24, 30, 26],
        "demands": [18, 20, 16, 26],
        "costs": [[5, 6, 8, 9], [4, 5, 7, 8], [7, 5, 4, 6]],
    },
    "examples-military/lab_02_example_military_02.ipynb": {
        "supplies": [42, 28, 20],
        "demands": [20, 18, 16, 14],
        "costs": [[4, 7, 8, 9], [5, 4, 6, 7], [7, 6, 4, 5]],
    },
    "examples-military/lab_02_example_military_03.ipynb": {
        "supplies": [18, 24, 20],
        "demands": [14, 18, 16, 22],
        "costs": [[6, 5, 8, 10], [5, 4, 6, 7], [7, 6, 5, 6]],
    },
    "lab_02_student_civil_01.ipynb": {
        "supplies": [30, 40, 35],
        "demands": [20, 25, 30, 30],
        "costs": [[5, 7, 6, 10], [8, 4, 5, 7], [6, 6, 4, 5]],
    },
    "lab_02_student_civil_02.ipynb": {
        "supplies": [40, 35, 30],
        "demands": [20, 25, 30, 15],
        "costs": [[4, 6, 8, 7], [5, 4, 7, 6], [6, 5, 4, 8]],
    },
    "lab_02_student_military_01.ipynb": {
        "supplies": [50, 40, 35],
        "demands": [30, 25, 35, 35],
        "costs": [[6, 7, 9, 12], [5, 4, 8, 10], [8, 6, 5, 7]],
    },
    "lab_02_student_military_02.ipynb": {
        "supplies": [25, 30, 20],
        "demands": [15, 20, 18, 30],
        "costs": [[7, 5, 9, 11], [6, 4, 7, 8], [8, 6, 5, 7]],
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
    "Args:",
    "Returns:",
    "display(",
    "np.allclose",
)


def read_notebook(path: Path) -> nbformat.NotebookNode:
    """Reads and schema-validates one notebook."""

    with path.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)
    nbformat.validate(notebook)
    return notebook


def notebook_source(notebook: nbformat.NotebookNode) -> str:
    """Combines all cell sources into one searchable string."""

    return "\n".join("".join(cell.source) for cell in notebook.cells)


def code_sources(notebook: nbformat.NotebookNode) -> list[str]:
    """Returns source strings from code cells only."""

    return [
        "".join(cell.source)
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]


def parse_code_cell(source: str, relative_path: Path, cell_index: int) -> ast.Module:
    """Parses a code cell and reports notebook location on syntax errors."""

    try:
        return ast.parse(source)
    except SyntaxError as exc:
        raise AssertionError(
            f"{relative_path} code cell {cell_index} has invalid Python: {exc}"
        ) from exc


def literal_np_array(node: ast.AST) -> object | None:
    """Extracts the first argument from a simple ``np.array([...])`` call."""

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
    """Extracts original ``supplies``, ``demands``, and ``costs`` arrays."""

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
    """Checks whether code cells call a function outside comments."""

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
    """Checks simple readability rules for notebook code cells."""

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


def check_notebook(
    relative_name: str,
    expected: dict[str, object],
    errors: list[str],
) -> None:
    """Checks one Lab 02 notebook against the transport-contract rules."""

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
    """Runs the Lab 02 transport notebook contract check."""

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
