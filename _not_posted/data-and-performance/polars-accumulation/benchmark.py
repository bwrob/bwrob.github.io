import gc
import os
import threading
import time
from dataclasses import dataclass, field
from typing import NamedTuple, TypedDict

import pandas as pd
import polars as pl
import psutil
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

NUM_ROWS = 200_000
NUM_RUNS = 10
CHUNK_SIZE = 50_000


# ==========================================
# 0. OS-Level Memory Monitor
# ==========================================
class PeakMemoryMonitor:
    """Spins up a background thread to poll the OS for true process memory usage (RSS)."""

    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.keep_measuring = False
        self.start_rss = 0
        self.peak_rss = 0

    def _monitor(self) -> None:
        while self.keep_measuring:
            current_rss = self.process.memory_info().rss
            self.peak_rss = max(self.peak_rss, current_rss)
            time.sleep(0.005)  # Poll every 5ms

    def start(self) -> None:
        self.start_rss = self.process.memory_info().rss
        self.peak_rss = self.start_rss
        self.keep_measuring = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self):
        self.keep_measuring = False
        self.thread.join()
        # Return the "Spike" (Peak memory added during the operation) in MB
        return (self.peak_rss - self.start_rss) / (1024 * 1024)


# ==========================================
# 1. Setup Models & Accumulators
# ==========================================


class InMemoryChunkedAccumulator:
    def __init__(self, engine="pandas") -> None:
        self.engine = engine
        self.chunks = []
        self._reset()

    def _reset(self) -> None:
        self.id, self.username, self.email, self.age = [], [], [], []
        self.balance, self.is_active, self.department, self.role = [], [], [], []

    def append(
        self, id, username, email, age, balance, is_active, department, role
    ) -> None:
        self.id.append(id)
        self.username.append(username)
        self.email.append(email)
        self.age.append(age)
        self.balance.append(balance)
        self.is_active.append(is_active)
        self.department.append(department)
        self.role.append(role)
        if len(self.id) >= CHUNK_SIZE:
            self.flush()

    def flush(self) -> None:
        if not self.id:
            return
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "age": self.age,
            "balance": self.balance,
            "is_active": self.is_active,
            "department": self.department,
            "role": self.role,
        }
        if self.engine == "pandas":
            self.chunks.append(pd.DataFrame(data))
        else:
            self.chunks.append(pl.DataFrame(data))
        self._reset()

    def finalize(self):
        self.flush()
        if not self.chunks:
            return None
        if self.engine == "pandas":
            return pd.concat(self.chunks, ignore_index=True)
        return pl.concat(self.chunks)


@dataclass(slots=True, frozen=True)
class ColumnarDataclass:
    id: list[int] = field(default_factory=list)
    username: list[str] = field(default_factory=list)
    email: list[str] = field(default_factory=list)
    age: list[int] = field(default_factory=list)
    balance: list[float] = field(default_factory=list)
    is_active: list[bool] = field(default_factory=list)
    department: list[str] = field(default_factory=list)
    role: list[str] = field(default_factory=list)

    def append(
        self,
        id: int,
        username: str,
        email: str,
        age: int,
        balance: float,
        is_active: bool,
        department: str,
        role: str,
    ) -> None:
        self.id.append(id)
        self.username.append(username)
        self.email.append(email)
        self.age.append(age)
        self.balance.append(balance)
        self.is_active.append(is_active)
        self.department.append(department)
        self.role.append(role)


class ColumnarAccumulator:
    def __init__(self) -> None:
        self.id, self.username, self.email, self.age = [], [], [], []
        self.balance, self.is_active, self.department, self.role = [], [], [], []

    def append(
        self,
        id: int,
        username: str,
        email: str,
        age: int,
        balance: float,
        is_active: bool,
        department: str,
        role: str,
    ) -> None:
        self.id.append(id)
        self.username.append(username)
        self.email.append(email)
        self.age.append(age)
        self.balance.append(balance)
        self.is_active.append(is_active)
        self.department.append(department)
        self.role.append(role)


class PydanticUser(BaseModel):
    id: int
    username: str
    email: str
    age: int
    balance: float
    is_active: bool
    department: str
    role: str


class NamedTupleUser(NamedTuple):
    id: int
    username: str
    email: str
    age: int
    balance: float
    is_active: bool
    department: str
    role: str


class TypedDictUser(TypedDict):
    id: int
    username: str
    email: str
    age: int
    balance: float
    is_active: bool
    department: str
    role: str


# ==========================================
# 2. Data Generators
# ==========================================


def columnar_dataclass():
    data = ColumnarDataclass()
    for i in range(NUM_ROWS):
        data.append(
            i,
            f"user_{i}",
            f"user_{i}@example.com",
            25 + (i % 40),
            i * 2.5,
            bool(i % 2),
            "Eng" if i % 3 == 0 else "Sales",
            "Admin",
        )
    return data


def columnar_class():
    data = ColumnarAccumulator()
    for i in range(NUM_ROWS):
        data.append(
            i,
            f"user_{i}",
            f"user_{i}@example.com",
            25 + (i % 40),
            i * 2.5,
            bool(i % 2),
            "Eng" if i % 3 == 0 else "Sales",
            "Admin",
        )
    return data


def columnar_dict():
    data = {
        "id": [],
        "username": [],
        "email": [],
        "age": [],
        "balance": [],
        "is_active": [],
        "department": [],
        "role": [],
    }
    for i in range(NUM_ROWS):
        data["id"].append(i)
        data["username"].append(f"user_{i}")
        data["email"].append(f"user_{i}@example.com")
        data["age"].append(25 + (i % 40))
        data["balance"].append(i * 2.5)
        data["is_active"].append(bool(i % 2))
        data["department"].append("Eng" if i % 3 == 0 else "Sales")
        data["role"].append("Admin")
    return data


def tuple_list():
    return [
        (
            i,
            f"user_{i}",
            f"user_{i}@example.com",
            25 + (i % 40),
            i * 2.5,
            bool(i % 2),
            "Eng" if i % 3 == 0 else "Sales",
            "Admin",
        )
        for i in range(NUM_ROWS)
    ]


def namedtuple_list():
    return [
        NamedTupleUser(
            i,
            f"user_{i}",
            f"user_{i}@example.com",
            25 + (i % 40),
            i * 2.5,
            bool(i % 2),
            "Eng" if i % 3 == 0 else "Sales",
            "Admin",
        )
        for i in range(NUM_ROWS)
    ]


def typeddict_list():
    return [
        {
            "id": i,
            "username": f"user_{i}",
            "email": f"user_{i}@example.com",
            "age": 25 + (i % 40),
            "balance": i * 2.5,
            "is_active": bool(i % 2),
            "department": "Eng" if i % 3 == 0 else "Sales",
            "role": "Admin",
        }
        for i in range(NUM_ROWS)
    ]


def pydantic_list():
    return [
        PydanticUser(
            id=i,
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            age=25 + (i % 40),
            balance=i * 2.5,
            is_active=bool(i % 2),
            department="Eng" if i % 3 == 0 else "Sales",
            role="Admin",
        )
        for i in range(NUM_ROWS)
    ]


# ==========================================
# 3. DataFrame Converters
# ==========================================

columns = [
    "id",
    "username",
    "email",
    "age",
    "balance",
    "is_active",
    "department",
    "role",
]


def to_pandas_dataclass(data):
    return pd.DataFrame({k: getattr(data, k) for k in data.__slots__})


def to_pandas_class(data):
    return pd.DataFrame(data.__dict__)


def to_pandas_dict(data):
    return pd.DataFrame(data)


def to_pandas_tuple(data):
    return pd.DataFrame(data, columns=columns)


def to_pandas_pydantic(data):
    return pd.DataFrame([m.model_dump() for m in data])


def to_polars_dataclass(data):
    return pl.DataFrame({k: getattr(data, k) for k in data.__slots__})


def to_polars_class(data):
    return pl.DataFrame(data.__dict__)


def to_polars_dict(data):
    return pl.DataFrame(data)


def to_polars_tuple(data):
    return pl.DataFrame(data, schema=columns, orient="row")


def to_polars_pydantic(data):
    return pl.DataFrame([m.model_dump() for m in data])


# ==========================================
# 4. Benchmark Runners
# ==========================================


def run_in_memory_chunked_benchmark(name, table, console, num_runs=NUM_RUNS) -> None:
    console.print(f"Running [bold cyan]{name}[/bold cyan] ({num_runs}x)...")
    total_pd_spike, total_pd_time = 0.0, 0.0
    total_pl_spike, total_pl_time = 0.0, 0.0
    monitor = PeakMemoryMonitor()

    for _ in range(num_runs):
        # Pandas Run
        monitor.start()
        start_pd = time.perf_counter()
        pd_acc = InMemoryChunkedAccumulator(engine="pandas")
        for i in range(NUM_ROWS):
            pd_acc.append(
                i,
                f"user_{i}",
                f"user_{i}@example.com",
                25 + (i % 40),
                i * 2.5,
                bool(i % 2),
                "Eng",
                "Admin",
            )
        df_pd = pd_acc.finalize()
        total_pd_time += time.perf_counter() - start_pd
        total_pd_spike += monitor.stop()
        del pd_acc, df_pd
        gc.collect()

        # Polars Run
        monitor.start()
        start_pl = time.perf_counter()
        pl_acc = InMemoryChunkedAccumulator(engine="polars")
        for i in range(NUM_ROWS):
            pl_acc.append(
                i,
                f"user_{i}",
                f"user_{i}@example.com",
                25 + (i % 40),
                i * 2.5,
                bool(i % 2),
                "Eng",
                "Admin",
            )
        df_pl = pl_acc.finalize()
        total_pl_time += time.perf_counter() - start_pl
        total_pl_spike += monitor.stop()
        del pl_acc, df_pl
        gc.collect()

    table.add_row(
        name,
        "---",
        "---",
        f"[bold red]+{total_pd_spike / num_runs:,.1f} MB[/bold red]",
        f"[bold green]{total_pd_time / num_runs:.3f}s[/bold green]",
        f"[bold red]+{total_pl_spike / num_runs:,.1f} MB[/bold red]",
        f"[bold green]{total_pl_time / num_runs:.3f}s[/bold green]",
    )


def run_benchmark(
    name, list_func, pd_func, pl_func, table, console, num_runs=NUM_RUNS
) -> None:
    console.print(f"Running [bold cyan]{name}[/bold cyan] ({num_runs}x)...")

    total_list_spike, total_list_time = 0.0, 0.0
    total_pd_spike, total_pd_time = 0.0, 0.0
    total_pl_spike, total_pl_time = 0.0, 0.0
    monitor = PeakMemoryMonitor()

    for _ in range(num_runs):
        # Gen Phase
        monitor.start()
        start_time = time.perf_counter()
        data_list = list_func()
        total_list_time += time.perf_counter() - start_time
        total_list_spike += monitor.stop()

        # Pandas Phase
        monitor.start()
        start_pd = time.perf_counter()
        df_pd = pd_func(data_list)
        total_pd_time += time.perf_counter() - start_pd
        total_pd_spike += monitor.stop()
        del df_pd

        # Polars Phase
        monitor.start()
        start_pl = time.perf_counter()
        df_pl = pl_func(data_list)
        total_pl_time += time.perf_counter() - start_pl
        total_pl_spike += monitor.stop()
        del df_pl

        del data_list
        gc.collect()

    avg_list_spike = total_list_spike / num_runs
    avg_pd_spike = total_pd_spike / num_runs
    avg_pl_spike = total_pl_spike / num_runs

    avg_pd_total_time = (total_list_time + total_pd_time) / num_runs
    avg_pl_total_time = (total_list_time + total_pl_time) / num_runs

    table.add_row(
        name,
        f"+{avg_list_spike:,.1f} MB",
        f"{total_list_time / num_runs:.3f}s",
        f"[bold red]+{avg_pd_spike:,.1f} MB[/bold red]",
        f"{avg_pd_total_time:.3f}s",
        f"[bold red]+{avg_pl_spike:,.1f} MB[/bold red]",
        f"{avg_pl_total_time:.3f}s",
    )


# ==========================================
# 5. Execute
# ==========================================
if __name__ == "__main__":
    console = Console()

    title_str = (
        f"True OS-Memory Accumulation (Avg of {NUM_RUNS} runs, {NUM_ROWS:,} rows each)"
    )
    table = Table(title=title_str, show_lines=True)
    table.add_column("Data Structure", justify="left", style="cyan", no_wrap=True)
    table.add_column("Gen OS RAM Spike", justify="right", style="magenta", no_wrap=True)
    table.add_column("Gen Time", justify="right", style="magenta", no_wrap=True)
    table.add_column("Pandas OS RAM Spike", justify="right", style="blue", no_wrap=True)
    table.add_column("Pandas Total Time", justify="right", style="blue", no_wrap=True)
    table.add_column(
        "Polars OS RAM Spike", justify="right", style="yellow", no_wrap=True
    )
    table.add_column("Polars Total Time", justify="right", style="yellow", no_wrap=True)

    console.print("\n[bold]Starting True OS Peak RAM Benchmark...[/bold]\n")

    run_in_memory_chunked_benchmark("Chunk & Concat (In-Memory)", table, console)
    run_benchmark(
        "Col (Frozen Dataclass)",
        columnar_dataclass,
        to_pandas_dataclass,
        to_polars_dataclass,
        table,
        console,
    )
    run_benchmark(
        "Col (Strict Class)",
        columnar_class,
        to_pandas_class,
        to_polars_class,
        table,
        console,
    )
    run_benchmark(
        "Col (Raw Dict)", columnar_dict, to_pandas_dict, to_polars_dict, table, console
    )
    run_benchmark(
        "Regular Tuple (Rows)",
        tuple_list,
        to_pandas_tuple,
        to_polars_tuple,
        table,
        console,
    )
    run_benchmark(
        "NamedTuple (Rows)",
        namedtuple_list,
        to_pandas_dict,
        to_polars_dict,
        table,
        console,
    )
    run_benchmark(
        "TypedDict (Rows)",
        typeddict_list,
        to_pandas_dict,
        to_polars_dict,
        table,
        console,
    )
    run_benchmark(
        "Pydantic (Rows)",
        pydantic_list,
        to_pandas_pydantic,
        to_polars_pydantic,
        table,
        console,
    )

    console.print("\n")
    console.print(table)
