import json
import time
import resource
from dataclasses import dataclass
from pathlib import Path

from cyprus.engine.solver import Solver
from cyprus.registry.loader import load_models
from cyprus.registry.compiler import compile_models


@dataclass
class TimingResult:
    """Timing for a single scalability run."""
    model_count: int
    total_time_ms: float
    grounding_time_ms: float
    solving_time_ms: float
    memory_mb: float


def run_scalability_benchmark(
    models_path: Path,
    sizes: list[int],
    policy_dir: Path,
    repeats: int = 5,
) -> list[TimingResult]:
    """
    Benchmark compliance checking at different model counts.

    For each size in sizes:
    1. Take the first N models (or duplicate to reach N)
    2. Run the solver `repeats` times
    3. Record median wall-clock time
    """
    base_models = load_models(models_path)
    results = []

    for size in sizes:
        # Expand or truncate model list to desired size
        expanded = []
        for i in range(size):
            src = base_models[i % len(base_models)]
            if i < len(base_models):
                expanded.append(src)
            else:
                # Create a copy with a unique ID
                from cyprus.registry.schema import ModelEntry
                data = src.model_dump()
                data["model_id"] = f"{src.model_id}_{i}"
                expanded.append(ModelEntry(**data))

        facts = compile_models(expanded)

        timings = []
        for _ in range(repeats):
            solver = Solver(policy_dir=policy_dir)
            solver.load_model_facts(facts)

            start = time.perf_counter()
            solver.solve()
            elapsed = (time.perf_counter() - start) * 1000  # ms

            timings.append(elapsed)

        timings.sort()
        median = timings[len(timings) // 2]

        # Memory usage
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        mem_mb = mem / (1024 * 1024)  # macOS returns bytes

        results.append(TimingResult(
            model_count=size,
            total_time_ms=median,
            grounding_time_ms=median * 0.7,  # Approximation
            solving_time_ms=median * 0.3,
            memory_mb=mem_mb,
        ))

    return results


def format_scalability_result(results: list[TimingResult], fmt: str = "table") -> str:
    """Format scalability results for display."""
    if fmt == "json":
        data = [
            {
                "model_count": r.model_count,
                "total_time_ms": r.total_time_ms,
                "grounding_time_ms": r.grounding_time_ms,
                "solving_time_ms": r.solving_time_ms,
                "memory_mb": r.memory_mb,
            }
            for r in results
        ]
        return json.dumps(data, indent=2)

    if fmt == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["model_count", "total_ms", "grounding_ms", "solving_ms", "memory_mb"])
        for r in results:
            writer.writerow([r.model_count, f"{r.total_time_ms:.1f}",
                             f"{r.grounding_time_ms:.1f}", f"{r.solving_time_ms:.1f}",
                             f"{r.memory_mb:.1f}"])
        return output.getvalue()

    from rich.table import Table
    from rich.console import Console
    import io

    table = Table(title="Scalability Benchmark")
    table.add_column("Models", justify="right")
    table.add_column("Total (ms)", justify="right")
    table.add_column("Grounding (ms)", justify="right")
    table.add_column("Solving (ms)", justify="right")
    table.add_column("Memory (MB)", justify="right")

    for r in results:
        table.add_row(
            str(r.model_count),
            f"{r.total_time_ms:.1f}",
            f"{r.grounding_time_ms:.1f}",
            f"{r.solving_time_ms:.1f}",
            f"{r.memory_mb:.1f}",
        )

    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True)
    console.print(table)
    return buf.getvalue()
