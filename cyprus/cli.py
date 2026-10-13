import sys
from pathlib import Path

import click
from rich.console import Console

from cyprus.engine.solver import Solver
from cyprus.registry.loader import load_models
from cyprus.registry.compiler import compile_models
from cyprus.reporting.compliance import generate_report
from cyprus.reporting.traceability import generate_traceability_matrix
from cyprus.reporting.formatters import format_result


console = Console()

# Resolve default policy directory
DEFAULT_POLICY_DIR = Path(__file__).parent / "policies" / "eu_ai_act"


@click.group()
@click.version_option()
def main():
    """Cyprus: Symbolic reasoning engine for AI regulatory compliance."""
    pass


@main.command()
@click.argument("models_path", type=click.Path(exists=True, path_type=Path))
@click.option("--policy", "-p", type=click.Path(exists=True, path_type=Path),
              default=None, help="Policy module directory. Default: eu_ai_act")
@click.option("--model", "-m", type=str, default=None,
              help="Check a single model by ID")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv", "markdown"]),
              default="table", help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed violations")
def check(models_path: Path, policy: Path | None, model: str | None,
          output: str, verbose: bool):
    """
    Check model compliance against a policy.

    MODELS_PATH is a YAML/JSON file or directory of model files.

    Examples:
        cyprus check models.yaml
        cyprus check data/real_models/ --policy cyprus/policies/eu_ai_act
        cyprus check models.yaml --model meta_llama3_8b --verbose
        cyprus check models.yaml --output json > results.json
    """
    policy_dir = policy or DEFAULT_POLICY_DIR

    # Load and validate models
    try:
        models = load_models(models_path)
    except Exception as e:
        console.print(f"[red]Error loading models:[/red] {e}")
        sys.exit(1)

    # Filter to single model if specified
    if model:
        models = [m for m in models if m.model_id == model]
        if not models:
            console.print(f"[red]Model '{model}' not found in {models_path}[/red]")
            sys.exit(1)

    # Compile to ASP facts
    facts = compile_models(models)

    # Solve
    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    # Output
    formatted = format_result(result, fmt=output, verbose=verbose)
    console.print(formatted)


@main.command()
@click.argument("models_path", type=click.Path(exists=True, path_type=Path))
@click.option("--policy", "-p", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--traceability", is_flag=True, help="Include traceability matrix")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv", "markdown"]),
              default="markdown")
def report(models_path: Path, policy: Path | None, traceability: bool, output: str):
    """
    Generate a full compliance report.

    Includes per-model compliance status, violation details,
    and optionally a traceability matrix.

    Examples:
        cyprus report models.yaml
        cyprus report models.yaml --traceability --output markdown > report.md
    """
    policy_dir = policy or DEFAULT_POLICY_DIR
    models = load_models(models_path)
    facts = compile_models(models)

    solver = Solver(policy_dir=policy_dir)
    solver.load_model_facts(facts)
    result = solver.solve()

    report_text = generate_report(result, fmt=output)
    console.print(report_text)

    if traceability:
        matrix = generate_traceability_matrix(policy_dir)
        console.print("\n")
        console.print(matrix)


@main.group()
def policy():
    """Manage policy modules."""
    pass


@policy.command("list")
def policy_list():
    """List available policy modules."""
    import yaml
    policies_dir = Path(__file__).parent / "policies"
    for p in sorted(policies_dir.iterdir()):
        if p.is_dir() and not p.name.startswith("_") and (p / "manifest.yaml").exists():
            manifest = yaml.safe_load((p / "manifest.yaml").read_text())
            name = manifest.get("name", p.name)
            version = manifest.get("version", "unknown")
            articles = len(manifest.get("articles_covered", []))
            console.print(f"  [bold]{p.name}[/bold] — {name} v{version} ({articles} articles)")


@policy.command("validate")
@click.argument("policy_name", type=str)
def policy_validate(policy_name: str):
    """
    Validate a policy module.

    Checks that manifest.yaml is well-formed, all referenced .lp files exist,
    rules parse without errors, and required fields are present.

    Example:
        cyprus policy validate eu_ai_act
    """
    import clingo
    import yaml

    policy_dir = Path(__file__).parent / "policies" / policy_name
    if not policy_dir.exists():
        console.print(f"[red]Policy '{policy_name}' not found[/red]")
        sys.exit(1)

    errors: list[str] = []

    # Check manifest
    manifest_path = policy_dir / "manifest.yaml"
    if not manifest_path.exists():
        errors.append("Missing manifest.yaml")
    else:
        manifest = yaml.safe_load(manifest_path.read_text())
        for field in ["name", "version", "articles_covered", "output_predicates"]:
            if field not in manifest:
                errors.append(f"manifest.yaml missing required field: {field}")

    # Check rule files exist
    rules_dir = policy_dir / "rules"
    if not rules_dir.exists():
        errors.append("Missing rules/ directory")
    else:
        lp_files = list(rules_dir.glob("*.lp"))
        if not lp_files:
            errors.append("No .lp files found in rules/")

    # Check rules parse with Clingo
    if not errors:
        for lp_file in lp_files:
            try:
                ctl = clingo.Control()
                ctl.load(str(lp_file))
                ctl.ground([("base", [])])
            except Exception as e:
                errors.append(f"{lp_file.name}: parse error — {e}")

    if errors:
        console.print("[red]Validation failed:[/red]")
        for err in errors:
            console.print(f"  - {err}")
        sys.exit(1)
    else:
        console.print(f"[green]Policy '{policy_name}' is valid.[/green]")


@policy.command("init")
@click.argument("name", type=str)
def policy_init(name: str):
    """
    Scaffold a new policy module from the template.

    Example:
        cyprus policy init nist_ai_rmf
    """
    import shutil
    template_dir = Path(__file__).parent / "policies" / "_template"
    target_dir = Path(__file__).parent / "policies" / name
    if target_dir.exists():
        console.print(f"[red]Policy '{name}' already exists[/red]")
        sys.exit(1)
    shutil.copytree(template_dir, target_dir)
    console.print(f"[green]Created policy module at {target_dir}[/green]")
    console.print("Next steps:")
    console.print("  1. Edit manifest.yaml with regulation metadata")
    console.print("  2. Add .lp rule files to rules/")
    console.print("  3. Add traceability mappings to traceability.yaml")
    console.print("  4. Add tests to tests/")


@main.command()
@click.argument("models_path", type=click.Path(exists=True, path_type=Path))
def validate(models_path: Path):
    """
    Validate model data against the schema without running compliance checks.

    Example:
        cyprus validate data/real_models/
    """
    try:
        models = load_models(models_path)
        console.print(f"[green]Valid: {len(models)} model(s) loaded successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Validation error:[/red] {e}")
        sys.exit(1)


@main.group()
def evaluate():
    """Run evaluation benchmarks (for paper)."""
    pass


@evaluate.command("accuracy")
@click.argument("ground_truth", type=click.Path(exists=True, path_type=Path))
@click.argument("models_path", type=click.Path(exists=True, path_type=Path))
@click.option("--policy", "-p", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--baselines", type=click.Choice(["all", "heuristic", "keyword", "none"]),
              default="all")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv"]), default="table")
def evaluate_accuracy(ground_truth: Path, models_path: Path, policy: Path | None,
                      baselines: str, output: str):
    """
    Evaluate accuracy against ground truth annotations.

    GROUND_TRUTH is a YAML file with manual compliance labels.
    MODELS_PATH is the model data to evaluate.

    Example:
        cyprus evaluate accuracy ground_truth.yaml data/real_models/ --baselines all
    """
    from cyprus.evaluation.benchmark import run_accuracy_benchmark
    policy_dir = policy or DEFAULT_POLICY_DIR
    results = run_accuracy_benchmark(ground_truth, models_path, policy_dir, baselines)

    from cyprus.evaluation.benchmark import format_accuracy_result
    formatted = format_accuracy_result(results, fmt=output)
    console.print(formatted)


@evaluate.command("scalability")
@click.argument("models_path", type=click.Path(exists=True, path_type=Path))
@click.option("--sizes", type=str, default="10,50,100,500,1000,5000,10000",
              help="Comma-separated model counts to test")
@click.option("--policy", "-p", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv"]), default="table")
def evaluate_scalability(models_path: Path, sizes: str, policy: Path | None, output: str):
    """
    Benchmark compliance checking at different scales.

    Example:
        cyprus evaluate scalability data/synthetic_models/ --sizes 10,50,100,500,1000
    """
    from cyprus.evaluation.scalability import run_scalability_benchmark, format_scalability_result
    size_list = [int(s.strip()) for s in sizes.split(",")]
    policy_dir = policy or DEFAULT_POLICY_DIR
    results = run_scalability_benchmark(models_path, size_list, policy_dir)
    formatted = format_scalability_result(results, fmt=output)
    console.print(formatted)


@evaluate.command("agreement")
@click.argument("annotations_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Choice(["table", "json"]), default="table")
def evaluate_agreement(annotations_dir: Path, output: str):
    """
    Compute inter-annotator agreement (Fleiss' kappa).

    ANNOTATIONS_DIR contains one YAML file per annotator.

    Example:
        cyprus evaluate agreement data/ground_truth/annotations/
    """
    from cyprus.evaluation.agreement import compute_agreement, format_agreement_result
    results = compute_agreement(annotations_dir)
    formatted = format_agreement_result(results, fmt=output)
    console.print(formatted)


@main.command()
@click.argument("source", type=str)
@click.argument("model_id", type=str)
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None,
              help="Output file path. Default: stdout")
def scrape(source: str, model_id: str, output: Path | None):
    """
    Scrape model metadata from an external source.

    SOURCE is the data source (currently: 'huggingface').
    MODEL_ID is the model identifier on that platform.

    Example:
        cyprus scrape huggingface meta-llama/Meta-Llama-3-8B
        cyprus scrape huggingface meta-llama/Meta-Llama-3-8B -o data/real_models/llama3_8b.yaml
    """
    if source != "huggingface":
        console.print(f"[red]Unknown source: {source}. Available: huggingface[/red]")
        sys.exit(1)

    from cyprus.data.scrapers.huggingface import scrape_model
    model_data = scrape_model(model_id)

    import yaml
    yaml_output = yaml.dump(model_data, default_flow_style=False, sort_keys=False)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml_output)
        console.print(f"[green]Saved to {output}[/green]")
    else:
        console.print(yaml_output)
