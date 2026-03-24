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
    notebooks: list[Path] = []
    for path in ROOT.rglob("*.ipynb"):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        notebooks.append(path)
    return sorted(notebooks)


def main() -> None:
    notebooks = iter_notebooks()
    if not notebooks:
        raise SystemExit("No notebooks found to validate.")

    warnings.filterwarnings("ignore", category=MissingIDFieldWarning)

    for path in notebooks:
        with path.open("r", encoding="utf-8") as handle:
            notebook = nbformat.read(handle, as_version=4)
        nbformat.validate(notebook)
        print(f"validated: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
