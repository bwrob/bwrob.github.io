"""Python startup script."""

import os
import subprocess
import time
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Callable, Generator, TypeVar

T = TypeVar("T")
TaskListOptionalDelay = list[tuple[T, int] | T]
TaskList = list[tuple[T, int]]

NAME_EXCLUDES = ("$", "tmp")
EXT_EXCLUDES = ("exe",)
DEFAULT_DELAY_SECONDS = 4
FILES_IN_TREE_PATTERN = r"**\*.*"


class Program(Enum):
    """Types of programs."""

    POWERSHELL = Path(r"C:\windows\system32\windowspowershell\v1.0\powershell.exe")
    NOTEPAD = Path(r"C:\Program Files\Notepad++\notepad++.exe")
    FIREFOX = Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Firefox.lnk")


def filter_excluded(
    path: Path,
) -> bool:
    """Filter path based on name and extension exclude lists.

    Args:
        path: Path to filter.
    """
    return (path.stem not in NAME_EXCLUDES) and (path.suffix not in EXT_EXCLUDES)


def start_process(
    *,
    name: str,
    path: Path,
    delay: int = DEFAULT_DELAY_SECONDS,
) -> None:
    """Given a path, starts the target.

    Behavior:
        * Minimizes all windows.
        * Depending on the path target:
            * executable files are run,
            * content files are opened with system default program,
            * folders are opened with system explorer.
        * Waits for delay seconds afterwards.

    Args:
        name: Name of the process to start.
        delay: Time to wait after starting the process.
    """
    if path.is_dir():
        print(f"Opening folder {name}")
    elif path.suffix in (".exe", ".lnk"):
        print(f"Running app {name}")
    else:
        print(f"Opening file {name}")

    os.startfile(path)
    time.sleep(delay)


def run_command(
    command: str,
    delay: int,
) -> None:
    """Runs a powershell command.

    Args:
        command: Command to run.
    """
    subprocess.call(
        f"powershell.exe {command}",
        shell=False,
    )
    time.sleep(delay)


def path_files(
    folder: Path,
    delay: int,
) -> Generator[tuple[Path, int], None, None]:
    """Generates all files in the work folder that are not excluded.

    Yields the folder path at beginning of the generator.

    Args:
        temp_folder: Path to the work folder.
    """
    yield folder, delay

    all_files = folder.glob(FILES_IN_TREE_PATTERN)
    filtered = filter(filter_excluded, all_files)

    for file in filtered:
        yield file, delay


def with_optional_delay(
    task_worker: Callable[[TaskList[T]], None],
) -> Callable[[TaskListOptionalDelay[T]], None]:
    """Adds default delay to all non-tuple items.

    Args:
        mixed_list: mixed list of items T or tuples (T, int) with delays
    """

    @wraps(task_worker)
    def task_defaulted_worker(task_list: TaskListOptionalDelay[T]) -> None:
        tasks_with_defaulted_delays = [
            item if isinstance(item, tuple) else (item, DEFAULT_DELAY_SECONDS)
            for item in task_list
        ]
        return task_worker(tasks_with_defaulted_delays)

    return task_defaulted_worker


@with_optional_delay
def start_programs(
    programs: TaskList[Program],
) -> None:
    """Starts listed programs.

    Args:
        programs: List of programs to start.
            Can be a string or a tuple. If a tuple is given, the first
            element is the name, the second is the delay.
    """
    for program, delay in programs:
        start_process(
            name=program.name,
            path=program.value,
            delay=delay,
        )


@with_optional_delay
def start_work_files(
    folders: TaskList[Path],
) -> None:
    """Starts all  files in the work folders.

    Args:
        delay: Time to wait after starting the process.
    """
    for folder_path, folder_delay in folders:
        for path, delay in path_files(folder_path, folder_delay):
            start_process(
                name=path.name,
                path=path,
                delay=delay,
            )


@with_optional_delay
def run_commands(
    commands: TaskList[str],
) -> None:
    """Runs all commands in the command list.

    Args:
        commands: List of commands to run.
    """
    for command, delay in commands:
        run_command(command, delay)


def run_startup_script():
    """
    Runs the startup script.
    """
    print(f" Welcome {os.getlogin()}! ".center(40, "*"))
    start_programs(
        [
            Program.POWERSHELL,
            Program.NOTEPAD,
            (Program.FIREFOX, 8),
        ]
    )
    start_work_files([Path.home() / ".temp"])
    run_commands(['Write-Output "test"'])


if __name__ == "__main__":
    run_startup_script()
