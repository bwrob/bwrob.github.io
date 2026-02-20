"""Check Jupyter notebooks for quality criteria."""

import json
import sys
from pathlib import Path
from typing import TypedDict, cast


class Cell(TypedDict):
    """A cell in a Jupyter notebook."""

    cell_type: str
    outputs: list[dict]
    execution_count: int
    source: list[str]
    metadata: dict[str, str]


def first_cell_is_markdown(cells: list[Cell]) -> bool:
    """Check if the first cell in the notebook is a markdown cell."""
    first = cells[0]
    cell_type: str | None = first.get("cell_type")
    return cell_type == "markdown"


def outputs_are_empty(cells: list[Cell]) -> bool:
    """Check if all cells in the notebook have empty outputs."""
    for cell in cells:
        outputs = cell.get("outputs")
        if outputs:
            return False
    return True


def check_notebook(path: Path) -> bool:
    """Check if a notebook satisfies the quality criteria."""
    json_string = path.read_text(encoding="utf8")
    data = json.loads(json_string)

    cells = data.get("cells")
    if not cells:
        return True
    cells = cast("list[Cell]", cells)

    return all(
        (
            first_cell_is_markdown(cells),
            outputs_are_empty(cells),
            # Potentially more checks could be added here in the future.
        )
    )


def check_directory(path_str: str) -> int:
    """Check all notebooks in a directory and its subdirectories."""
    all_notebooks = Path(path_str).glob("**/*.ipynb")
    failed = [path for path in all_notebooks if not check_notebook(path)]

    if not failed:
        return 0

    failed_str = "\n\t".join(str(path) for path in failed)
    print(f"Failed check on notebooks:\n\t{failed_str}")
    return 1


if __name__ == "__main__":
    sys.exit(check_directory("."))
