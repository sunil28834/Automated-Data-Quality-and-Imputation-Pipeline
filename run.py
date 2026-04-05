#!/usr/bin/env python3
"""CLI entry point for the Data Quality & Imputation Pipeline."""
import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich import box

console = Console()

@click.group()
def cli():
    """Data Quality & Imputation Pipeline CLI"""
    pass

@cli.command()
@click.argument("input_path")
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--config", "-c", default="config/pipeline_config.yaml", help="Config YAML")
@click.option("--report", "-r", is_flag=True, help="Print full report")
def run(input_path, output, config, report):
    """Run the full pipeline on INPUT_PATH."""
    from src.utils.config import PipelineConfig
    from src.pipeline.orchestrator import PipelineOrchestrator

    if output is None:
        p = Path(input_path)
        output = str(p.parent / f"{p.stem}_cleaned{p.suffix}")

    cfg = PipelineConfig.from_yaml(config) if Path(config).exists() else PipelineConfig()
    orchestrator = PipelineOrchestrator(cfg)

    console.print(Panel.fit(
        f"[bold cyan]Data Quality Pipeline[/]\n[dim]{input_path} → {output}[/]",
        border_style="cyan"
    ))

    steps = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.percentage:>3.0f}%"), console=console) as prog:
        task = prog.add_task("Running...", total=100)

        def cb(msg, pct):
            prog.update(task, completed=pct, description=msg)
            steps.append((pct, msg))

        try:
            result = orchestrator.run(input_path, output, progress_cb=cb)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise SystemExit(1)

    dr = result.detection_report
    console.print()
    console.print(Panel(
        f"[green]Quality Score:[/] [bold]{dr.total_score:.1f}/100[/]  |  "
        f"Issues: [yellow]{len(dr.issues)}[/]  |  "
        f"Duration: {result.duration_seconds}s  |  "
        f"Shape: {result.raw_shape} → {result.clean_shape}",
        title="[bold]Pipeline Summary[/]", border_style="green"
    ))

    if report and dr.issues:
        table = Table(title="Quality Issues", box=box.ROUNDED)
        table.add_column("Column", style="cyan")
        table.add_column("Issue Type")
        table.add_column("Severity")
        table.add_column("Count")
        table.add_column("Details")
        sev_colors = {"critical": "red", "high": "yellow", "medium": "blue", "low": "dim"}
        for issue in dr.issues:
            c = sev_colors.get(issue.severity, "white")
            table.add_row(issue.column, issue.issue_type,
                         f"[{c}]{issue.severity}[/]",
                         str(issue.count), issue.details)
        console.print(table)

    console.print(f"\n[bold green]Saved to:[/] {output}")

@cli.command()
@click.argument("input_path")
def profile(input_path):
    """Profile a dataset and show column statistics."""
    from src.utils.io_utils import load_data
    from src.pipeline.profiler import DataProfiler

    df = load_data(input_path)
    prof = DataProfiler().profile(df)

    table = Table(title=f"Profile: {input_path}", box=box.SIMPLE_HEAVY)
    table.add_column("Column", style="cyan")
    table.add_column("Type")
    table.add_column("Missing %")
    table.add_column("Unique")
    table.add_column("Stats")

    for col, info in prof["columns"].items():
        stats = ""
        if "mean" in info:
            stats = f"μ={info['mean']} σ={info['std']}"
        elif "top_values" in info:
            top = list(info["top_values"].keys())[:2]
            stats = ", ".join(top)
        miss_color = "red" if info["missing_pct"] > 20 else "yellow" if info["missing_pct"] > 5 else "green"
        table.add_row(col, info["dtype"],
                     f"[{miss_color}]{info['missing_pct']}%[/]",
                     str(info["unique"]), stats)

    console.print(table)
    console.print(f"\n[dim]Shape: {prof['shape']['rows']} × {prof['shape']['columns']} | "
                  f"Memory: {prof['memory_mb']} MB[/]")

@cli.command()
def ui():
    """Launch the Streamlit dashboard."""
    import subprocess, sys
    console.print("[bold cyan]Launching Streamlit dashboard...[/]")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/app.py"])

if __name__ == "__main__":
    cli()
