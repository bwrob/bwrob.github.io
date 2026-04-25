import os
import random
import time
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from datetime import datetime, timedelta
from multiprocessing import Manager
from typing import Any

import plotly.express as px
import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table


# --- DYNAMIC TOPOLOGY DETECTION ---
def detect_hybrid_topology() -> tuple[list[int], list[int]]:
    """Uses the Logical vs Physical core count to map P-Cores and E-Cores."""
    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)

    if not logical_cores or not physical_cores or logical_cores == physical_cores:
        return list(range(logical_cores or os.cpu_count() or 1)), []

    num_p_cores = logical_cores - physical_cores

    p_core_ids = list(range(num_p_cores * 2))
    e_core_ids = list(range(num_p_cores * 2, logical_cores))

    return p_core_ids, e_core_ids


P_CORES, E_CORES = detect_hybrid_topology()
TOTAL_CORES = len(P_CORES) + len(E_CORES)

# --- DYNAMIC THRESHOLD CONFIGURATION ---
MIN_THRESHOLD_SAMPLES = 5
ROLLING_WINDOW_SIZE = 20
MULTIPLIER = 1.5
FALLBACK_THRESHOLD = 3.0


def heavy_task(name: str, duration: float, shared_pids: dict[str, int]) -> str:
    """The worker function. It resets itself to E-cores at the start of every task."""
    try:
        target_cores = E_CORES or P_CORES
        psutil.Process().cpu_affinity(target_cores)
    except Exception:
        pass

    shared_pids[name] = os.getpid()

    time.sleep(duration)

    shared_pids.pop(name, None)

    return f"Result for {name}"


def run_multiprocessing(num_workers: int = TOTAL_CORES, total_tasks: int = 120) -> None:
    tasks_to_do: list[tuple[str, float]] = []
    for i in range(total_tasks):
        if random.random() > 0.90:
            tasks_to_do.append((f"T-{i:03d} (Heavy)", random.uniform(6.0, 8.0)))
        else:
            tasks_to_do.append((f"T-{i:03d}", random.uniform(1.0, 2.0)))

    history: list[dict[str, Any]] = []
    active_slots: dict[int, dict[str, Any] | None] = dict.fromkeys(range(num_workers))
    completed_durations: list[float] = []
    current_threshold: float = FALLBACK_THRESHOLD

    console: Console = Console()

    console.print(f"[bold yellow]System Detected:[/] {TOTAL_CORES} Total Threads")
    console.print(f"├─ [bold red]P-Cores (Hyper-threaded):[/] {len(P_CORES)} threads")
    console.print(
        f"└─ [bold blue]E-Cores (Single-threaded):[/] {len(E_CORES)} threads\n"
    )

    start_wall_clock: float = time.perf_counter()

    manager = Manager()
    task_pids = manager.dict()

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures: dict[Future[str], tuple[str, int, float]] = {}

        def get_status_table(thresh: float) -> Table:
            table = Table(
                title=f"Hybrid Monitor | {len(history)}/{total_tasks} Done | Dynamic Threshold: {thresh:.2f}s",
                header_style="bold magenta",
            )
            table.add_column("Worker", justify="center", style="cyan")
            table.add_column("Current Task", style="green")
            table.add_column("Progress", justify="right")
            table.add_column("Core Status", justify="center")

            for i in range(num_workers):
                data: dict[str, Any] | None = active_slots[i]
                if data:
                    elapsed: float = time.perf_counter() - data["start_abs"]

                    if elapsed > thresh and not data["promoted"] and E_CORES:
                        pid = task_pids.get(data["name"])
                        if pid:
                            try:
                                psutil.Process(pid).cpu_affinity(P_CORES)
                                data["promoted"] = True
                            except Exception:
                                pass

                    if not E_CORES:
                        core_style = "[dim]Standard Core[/]"
                    else:
                        core_style = (
                            "[bold red]🔥 P-Core[/]"
                            if data["promoted"]
                            else "[blue]🌱 E-Core[/]"
                        )

                    table.add_row(
                        f"Worker {i:02d}",
                        data["name"],
                        f"{elapsed:.1f}s active",
                        core_style,
                    )
                else:
                    table.add_row(f"Worker {i:02d}", "-", "[dim]idle[/]", "-")
            return table

        with Live(
            get_status_table(current_threshold), refresh_per_second=8, console=console
        ) as live:
            while tasks_to_do or futures:
                while len(futures) < num_workers and tasks_to_do:
                    name, duration = tasks_to_do.pop(0)
                    w_id: int = next(i for i, v in active_slots.items() if v is None)

                    start_t: float = time.perf_counter() - start_wall_clock
                    active_slots[w_id] = {
                        "name": name,
                        "start_abs": time.perf_counter(),
                        "promoted": False,
                    }

                    f: Future[str] = executor.submit(
                        heavy_task, name, duration, task_pids
                    )
                    futures[f] = (name, w_id, start_t)

                done, _ = wait(futures.keys(), timeout=0.1, return_when=FIRST_COMPLETED)

                for f in done:
                    name, w_id, start_t = futures.pop(f)
                    end_t: float = time.perf_counter() - start_wall_clock
                    task_duration = end_t - start_t

                    was_promoted = active_slots[w_id]["promoted"]

                    history.append(
                        {
                            "Task": name,
                            "Worker": f"Worker {w_id:02d}",
                            "Start_Sec": start_t,
                            "Duration_Sec": task_duration,
                            "Promoted": was_promoted,
                        }
                    )
                    active_slots[w_id] = None

                    completed_durations.append(task_duration)
                    if len(completed_durations) > ROLLING_WINDOW_SIZE:
                        completed_durations.pop(0)

                    if len(completed_durations) >= MIN_THRESHOLD_SAMPLES:
                        rolling_avg = sum(completed_durations) / len(
                            completed_durations
                        )
                        current_threshold = max(1.0, rolling_avg * MULTIPLIER)

                live.update(get_status_table(current_threshold))

    console.print("\n[bold green]Timeline Captured.[/] Generating HTML chart...")
    plot_plotly_gantt(history)

    # --- NEW: Print final task times ---
    print_task_summary(history, console)


def plot_plotly_gantt(history: list[dict[str, Any]]) -> None:
    base_time: datetime = datetime(2000, 1, 1, 0, 0, 0)
    df_data: list[dict[str, Any]] = []

    for h in history:
        start_dt: datetime = base_time + timedelta(seconds=h["Start_Sec"])
        end_dt: datetime = base_time + timedelta(
            seconds=h["Start_Sec"] + h["Duration_Sec"]
        )

        if E_CORES:
            exec_type = "Rescued by P-Core" if h["Promoted"] else "Stayed on E-Core"
        else:
            exec_type = "Standard Execution"

        df_data.append(
            {
                "Task": h["Task"],
                "Worker": h["Worker"],
                "Start": start_dt,
                "Finish": end_dt,
                "Duration (s)": round(h["Duration_Sec"], 2),
                "Execution Type": exec_type,
            }
        )

    df_data.sort(key=lambda x: x["Worker"])

    color_map = {
        "Rescued by P-Core": "#ef4444",
        "Stayed on E-Core": "#3b82f6",
        "Standard Execution": "#10b981",
    }

    fig = px.timeline(
        df_data,
        x_start="Start",
        x_end="Finish",
        y="Worker",
        color="Execution Type",
        color_discrete_map=color_map,
        text="Task",
        hover_data=["Duration (s)"],
        title="Execution Timeline: Dynamic Load Balancing",
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        showlegend=True,
        xaxis=dict(
            title="Elapsed Time (Minutes:Seconds)",
            tickformat="%M:%S",
        ),
        font=dict(family="sans-serif", size=14),
        hovermode="closest",
    )

    fig.update_traces(textposition="inside", insidetextanchor="middle")

    output_filename: str = "multiprocessing_timeline.html"
    fig.write_html(output_filename)

    print(f"Success! Timeline saved to {output_filename}\n")


def print_task_summary(history: list[dict[str, Any]], console: Console) -> None:
    """Prints a neat terminal table of all task durations, sorted longest to shortest."""
    table = Table(
        title="Final Task Durations (Sorted by Longest)", header_style="bold yellow"
    )
    table.add_column("Task Name", style="cyan")
    table.add_column("Worker", justify="center")
    table.add_column("Duration", justify="right", style="green")
    table.add_column("Final Core Type", justify="center")

    # Sort tasks so the heaviest ones are at the top
    sorted_history = sorted(history, key=lambda x: x["Duration_Sec"], reverse=True)

    for h in sorted_history:
        if not E_CORES:
            core_type = "[dim]Standard[/]"
        else:
            core_type = (
                "[bold red]P-Core (Promoted)[/]" if h["Promoted"] else "[blue]E-Core[/]"
            )

        table.add_row(h["Task"], h["Worker"], f"{h['Duration_Sec']:.2f}s", core_type)

    console.print(table)


if __name__ == "__main__":
    run_multiprocessing()
