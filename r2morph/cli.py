"""
Command-line interface for r2morph.

Primary product flow:
    r2morph input.bin [output.bin]
    r2morph mutate input.bin -o output.bin --report report.json
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from r2morph import __version__
from r2morph.core.config import EngineConfig
from r2morph.core.engine import MorphEngine
from r2morph.core.support import PRODUCT_SUPPORT, is_experimental_mutation
from r2morph.utils.logging import setup_logging
from r2morph.validation import BinaryValidator
from r2morph.validation.validator import RuntimeComparisonConfig

from r2morph.reporting.report_helpers import (
    _attach_gate_evaluation,
    _pass_severity_requirements_met,
    _severity_threshold_met,
)
from r2morph.reporting.report_resolver import (
    _resolve_general_report_flow_state,
)
from r2morph.reporting.filtered_summary_builder import (
    _build_report_dispatch_state,
)
from r2morph.reporting.report_orchestrator import (
    _dispatch_report_flow,
)

app = typer.Typer(
    name="r2morph",
    help="Metamorphic mutation engine with structured validation and reporting",
    add_completion=False,
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
experimental_app = typer.Typer(
    name="experimental",
    help="Secondary experimental commands outside the stable mutation engine surface",
    add_completion=False,
)
app.add_typer(experimental_app, name="experimental")
console = Console()

SUPPORTED_MUTATIONS = set(PRODUCT_SUPPORT.stable_mutations)
EXPERIMENTAL_MUTATIONS = set(PRODUCT_SUPPORT.experimental_mutations)
KNOWN_COMMANDS = {
    "analyze",
    "functions",
    "morph",
    "mutate",
    "validate",
    "diff",
    "report",
    "version",
    "cache",
}

SEVERITY_ORDER = {
    "mismatch": 0,
    "without-coverage": 1,
    "bounded-only": 2,
    "clean": 3,
    "not-requested": 4,
}


def _build_config(aggressive: bool, force: bool) -> EngineConfig:
    config = EngineConfig.create_aggressive() if aggressive else EngineConfig.create_default()
    if force:
        config.force_different = True
        config.nop.force_different = True
        config.substitution.force_different = True
        config.register.force_different = True
        config.expansion.force_different = True
        config.block.force_different = True
    return config


def _mutation_config(section: Any, seed: int | None, offset: int) -> dict[str, Any]:
    cfg: dict[str, Any] = section.to_dict()
    if seed is not None:
        cfg["seed"] = seed + offset
    return cfg






def _build_runtime_validator(
    *,
    timeout: int,
    corpus: Path | None = None,
    compare_files: bool = False,
    normalize_whitespace: bool = False,
) -> BinaryValidator:
    """Build a runtime validator from CLI options."""
    validator = BinaryValidator(
        timeout=timeout,
        comparison=RuntimeComparisonConfig(
            compare_files=compare_files,
            normalize_whitespace=normalize_whitespace,
        ),
    )
    if corpus is not None:
        with open(corpus, "r", encoding="utf-8") as handle:
            validator.load_test_cases(json.load(handle))
    return validator


def _load_binary_analyzer() -> type:
    """Lazy import for analysis-only flows outside the stable mutate/report path."""
    from r2morph.analysis.analyzer import BinaryAnalyzer

    return BinaryAnalyzer


def _load_diff_analyzer() -> type:
    """Lazy import for diff-only flows outside the stable mutate/report hot path."""
    pass


def _load_mutation_pass_types() -> dict[str, type]:
    """Lazy import mutation passes so stable report/validate flows avoid extra imports."""
    from r2morph.mutations import (
        BlockReorderingPass,
        InstructionExpansionPass,
        InstructionSubstitutionPass,
        NopInsertionPass,
        RegisterSubstitutionPass,
    )

    return {
        "nop": NopInsertionPass,
        "substitute": InstructionSubstitutionPass,
        "register": RegisterSubstitutionPass,
        "expand": InstructionExpansionPass,
        "block": BlockReorderingPass,
    }


def _resolve_min_severity(min_severity: str | None) -> tuple[str | None, int | None]:
    """Validate and normalize a minimum severity option."""
    if min_severity is None:
        return None, None
    if min_severity not in SEVERITY_ORDER:
        console.print(f"[bold red]Error:[/bold red] Invalid --min-severity: {min_severity}")
        raise typer.Exit(2)
    return min_severity, SEVERITY_ORDER[min_severity]


def _resolve_report_context(
    *,
    payload: dict[str, Any],
    only_pass: str | None,
    only_pass_failure: str | None,
    only_expected_severity: str | None,
) -> dict[str, Any]:
    """Thin CLI wrapper: resolves pass aliases then delegates to reporting layer."""
    from r2morph.reporting.report_resolver import _resolve_report_context as _resolve_ctx

    return _resolve_ctx(
        payload=payload,
        resolved_only_pass=_resolve_report_pass_filter(only_pass),
        resolved_only_pass_failure=_resolve_report_pass_filter(only_pass_failure),
        only_expected_severity=only_expected_severity,
    )


def _resolve_pass_severity_requirements(
    requirements: list[str] | None,
    *,
    alias_map: dict[str, str] | None = None,
) -> list[tuple[str, str, int]]:
    """Parse repeated PassName=severity requirements for mutate gating."""
    pass


def _add_mutations(
    engine: MorphEngine,
    mutations: list[str],
    config: EngineConfig,
    *,
    seed: int | None = None,
) -> None:
    for _mutation_name, mutation_pass in _selected_mutation_passes(
        mutations,
        config,
        seed=seed,
    ):
        engine.add_mutation(mutation_pass)


def _selected_mutation_passes(
    mutations: list[str],
    config: EngineConfig,
    *,
    seed: int | None = None,
) -> list[tuple[str, Any]]:
    """Build pass instances for the selected mutation names."""
    pass_types = _load_mutation_pass_types()
    selected: list[tuple[str, Any]] = []
    offset = 0
    if "nop" in mutations:
        selected.append(("nop", pass_types["nop"](config=_mutation_config(config.nop, seed, offset))))
        offset += 1
    if "substitute" in mutations:
        selected.append(
            (
                "substitute",
                pass_types["substitute"](config=_mutation_config(config.substitution, seed, offset)),
            )
        )
        offset += 1
    if "register" in mutations:
        selected.append(
            (
                "register",
                pass_types["register"](config=_mutation_config(config.register, seed, offset)),
            )
        )
        offset += 1
    if "expand" in mutations:
        selected.append(
            (
                "expand",
                pass_types["expand"](config=_mutation_config(config.expansion, seed, offset)),
            )
        )
        offset += 1
    if "block" in mutations:
        selected.append(("block", pass_types["block"](config=_mutation_config(config.block, seed, offset))))
    return selected


def _mutation_pass_alias_map(
    config: EngineConfig,
    *,
    seed: int | None = None,
) -> dict[str, str]:
    """Build aliases from short mutation names to concrete pass names."""
    aliases: dict[str, str] = {}
    all_mutations = list(SUPPORTED_MUTATIONS | EXPERIMENTAL_MUTATIONS)
    for mutation_name, mutation_pass in _selected_mutation_passes(
        all_mutations,
        config,
        seed=seed,
    ):
        aliases[mutation_name] = mutation_pass.name
        aliases[mutation_pass.name] = mutation_pass.name
    return aliases


def _resolve_report_pass_filter(pass_name: str | None) -> str | None:
    """Resolve report-side pass filters using the product alias map."""
    if pass_name is None:
        return None
    alias_map = _mutation_pass_alias_map(_build_config(False, False), seed=None)
    return alias_map.get(pass_name.strip(), pass_name.strip())


def _limited_symbolic_passes(
    mutations: list[str],
    config: EngineConfig,
    *,
    seed: int | None,
) -> list[dict[str, str]]:
    """Return passes that declare symbolic support as limited."""
    pass


def _warn_or_block_limited_symbolic(
    mutations: list[str],
    config: EngineConfig,
    *,
    seed: int | None,
    allow_limited_symbolic: bool,
) -> None:
    """Block symbolic mode for passes that declare limited symbolic support unless explicitly allowed."""
    pass


def _resolve_validation_mode(
    *,
    requested_mode: str,
    mutations: list[str],
    config: EngineConfig,
    seed: int | None,
    allow_limited_symbolic: bool,
    limited_symbolic_policy: str,
) -> tuple[str, dict[str, object] | None]:
    """Resolve requested vs effective validation mode for limited symbolic passes."""
    pass


def _print_mutation_summary(result: dict[str, Any], output_path: Path | None = None) -> None:
    table = Table(title="Mutation Engine Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    requested_mode = result.get("requested_validation_mode", result.get("validation_mode", "off"))
    effective_mode = result.get("validation_mode", "off")
    table.add_row("Requested Validation", str(requested_mode))
    table.add_row("Effective Validation", str(effective_mode))
    table.add_row("Total Mutations", str(result.get("total_mutations", 0)))
    table.add_row("Passes Run", str(result.get("passes_run", 0)))
    table.add_row("Rolled Back Passes", str(result.get("rolled_back_passes", 0)))
    table.add_row("Discarded Mutations", str(result.get("discarded_mutations", 0)))
    table.add_row(
        "Validation Passed",
        "yes" if result.get("validation", {}).get("all_passed", False) else "no",
    )
    total_issues = result.get("validation", {}).get("total_issues", 0)
    table.add_row("Validation Issues", str(total_issues))
    for pass_name, pass_result in result.get("pass_results", {}).items():
        if "error" in pass_result:
            table.add_row(pass_name, f"[red]Error: {pass_result['error']}[/red]")
            continue
        rolled_back = ""
        if pass_result.get("rolled_back"):
            reason = pass_result.get("rollback_reason", "rollback")
            rolled_back = f" (rolled back: {reason})"
        table.add_row(
            pass_name,
            f"{pass_result.get('mutations_applied', 0)} mutations{rolled_back}",
        )

    console.print(table)
    if output_path is not None:
        console.print(f"\n[bold green]✓[/bold green] Binary saved to: {output_path}")


def _run_simple_mode(
    input_file: Path,
    output_file: Path | None,
    *,
    aggressive: bool,
    force: bool,
    seed: int | None,
    verbose: bool,
    debug: bool,
) -> None:
    setup_logging("DEBUG" if (verbose or debug) else "INFO")

    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_morphed{input_file.suffix}"

    mode_str = "[bold red]AGGRESSIVE[/bold red]" if aggressive else "[bold green]STANDARD[/bold green]"
    force_str = " [bold yellow](FORCE)[/bold yellow]" if force else ""
    console.print(f"[bold green]r2morph - Simple Mode ({mode_str}{force_str})[/bold green]")
    console.print(f"Input:  {input_file}")
    console.print(f"Output: {output_file}")
    console.print("Applying stable mutations: [cyan]nop, substitute, register[/cyan]\n")

    with console.status("[bold green]Transforming binary..."):
        with MorphEngine(config={"seed": seed, "requested_mutations": ["nop", "substitute", "register"]}) as engine:
            engine.load_binary(input_file).analyze()
            config = _build_config(aggressive, force)
            _add_mutations(engine, ["nop", "substitute", "register"], config, seed=seed)

            report_path = output_file.parent / f"{output_file.stem}.report.json"
            result = engine.run(
                validation_mode="structural",
                rollback_policy="skip-invalid-pass",
                report_path=report_path,
                seed=seed,
            )

            engine.save(output_file)

        _print_mutation_summary(result, output_file)
        console.print(f"[cyan]Report:[/cyan] {report_path}")


@app.callback()
def main_callback(
    ctx: typer.Context,
    input_opt: Path | None = typer.Option(None, "--input", "-i", help="Input binary file (alternative style)"),
    output_opt: Path | None = typer.Option(None, "--output", "-o", help="Output binary file (alternative style)"),
    aggressive: bool = typer.Option(
        False, "--aggressive", "-a", help="Aggressive mode: more mutations, higher probability"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force mutations to be different from original"),
    seed: int | None = typer.Option(None, "--seed", help="Deterministic seed for stable mutation selection"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug output"),
) -> None:
    """
    r2morph - mutation engine with validation

    SIMPLE USAGE (like r2morph):
        r2morph input.exe [output.exe]
        r2morph -i input.exe -o output.exe

    This applies the stable mutation set:
    nop + substitute + register, then validates and writes a report.

    AGGRESSIVE MODE:
        r2morph -i input.exe -o output.exe --aggressive
        r2morph input.exe output.exe -a

    ADVANCED USAGE:
        r2morph analyze input.exe
        r2morph functions input.exe
        r2morph morph input.exe -m nop
    """
    pass


@app.command()
def analyze(
    binary: Path = typer.Argument(..., help="Path to binary file", exists=True),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Analyze a binary and display statistics.
    """
    setup_logging("DEBUG" if verbose else "INFO")

    with console.status("[bold green]Analyzing binary..."):
        try:
            BinaryAnalyzer = _load_binary_analyzer()
            with MorphEngine() as engine:
                engine.load_binary(binary).analyze()
                analyzer = BinaryAnalyzer(engine.binary)
                stats = analyzer.get_statistics()

            table = Table(title=f"Binary Analysis: {binary.name}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            arch = stats["architecture"]
            table.add_row("Architecture", f"{arch['arch']} ({arch['bits']}-bit)")
            table.add_row("Format", arch["format"])
            table.add_row("Endian", arch["endian"])
            table.add_row("Total Functions", str(stats["total_functions"]))
            table.add_row("Total Instructions", str(stats["total_instructions"]))
            table.add_row("Total Basic Blocks", str(stats["total_basic_blocks"]))
            table.add_row("Total Code Size", f"{stats['total_code_size']} bytes")
            table.add_row("Avg Function Size", f"{stats['avg_function_size']:.2f} bytes")
            table.add_row(
                "Avg Instructions/Function",
                f"{stats['avg_instructions_per_function']:.2f}",
            )

            console.print(table)

        except typer.Exit:
            raise
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)


@experimental_app.command("analyze-enhanced")
def analyze_enhanced(
    binary: Path = typer.Argument(..., help="Path to binary file", exists=True),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    detect_only: bool = typer.Option(False, "--detect-only", help="Only run obfuscation detection"),
    symbolic: bool = typer.Option(False, "--symbolic", help="Enable symbolic execution analysis"),
    dynamic: bool = typer.Option(False, "--dynamic", help="Enable dynamic instrumentation"),
    devirt: bool = typer.Option(False, "--devirt", help="Enable devirtualization analysis"),
    iterative: bool = typer.Option(False, "--iterative", help="Enable iterative simplification"),
    rewrite: bool = typer.Option(False, "--rewrite", help="Enable binary rewriting"),
    bypass: bool = typer.Option(False, "--bypass", help="Enable anti-analysis bypass"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory for results"),
) -> None:
    """
    Experimental analysis for obfuscated binaries (secondary workflow).
    Requires enhanced dependencies: pip install 'r2morph[enhanced]'

    Phase 2 capabilities include:
    - Advanced packer detection (20+ packers)
    - Control Flow Obfuscation simplification
    - Iterative multi-pass simplification
    - Binary rewriting and reconstruction
    - Anti-analysis bypass framework
    """
    setup_logging("DEBUG" if verbose else "INFO")

    from r2morph.analysis.enhanced_analyzer import (
        EnhancedAnalysisOrchestrator,
        AnalysisOptions,
        check_enhanced_dependencies,
    )

    if not check_enhanced_dependencies():
        console.print("[bold red]Error:[/bold red] Enhanced analysis requires additional dependencies.")
        console.print("Install with: [cyan]pip install 'r2morph[enhanced]'[/cyan]")
        raise typer.Exit(1)

    with console.status("[bold green]Analyzing obfuscated binary..."):
        try:
            options = AnalysisOptions(
                verbose=verbose,
                detect_only=detect_only,
                symbolic=symbolic,
                dynamic=dynamic,
                devirt=devirt,
                iterative=iterative,
                rewrite=rewrite,
                bypass=bypass,
            )

            orchestrator = EnhancedAnalysisOrchestrator(
                binary_path=binary,
                output_dir=output,
                console=console,
            )

            orchestrator.analyze(options)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            if verbose:
                import traceback

                console.print(traceback.format_exc())
            raise typer.Exit(1)


@app.command()
def functions(
    binary: Path = typer.Argument(..., help="Path to binary file", exists=True),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum functions to display"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    List functions in a binary.
    """
    setup_logging("DEBUG" if verbose else "INFO")

    with console.status("[bold green]Loading binary..."):
        try:
            BinaryAnalyzer = _load_binary_analyzer()
            with MorphEngine() as engine:
                engine.load_binary(binary).analyze()
                analyzer = BinaryAnalyzer(engine.binary)
                funcs = analyzer.get_functions_list()

            table = Table(title=f"Functions in {binary.name}")
            table.add_column("Address", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Instructions", style="magenta")

            for func in funcs[:limit]:
                table.add_row(
                    f"0x{func.address:x}",
                    func.name,
                    str(func.size),
                    str(func.get_instructions_count()),
                )

            console.print(table)

            if len(funcs) > limit:
                console.print(
                    f"\n[yellow]Showing {limit} of {len(funcs)} functions. Use --limit to show more.[/yellow]"
                )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)


@app.command()
def morph(
    binary: Path = typer.Argument(..., help="Path to binary file", exists=True),
    output: Path = typer.Option(None, "--output", "-o", help="Output path for morphed binary"),
    mutations: list[str] = typer.Option(
        ["nop", "substitute", "register"],
        "--mutation",
        "-m",
        help="Mutations to apply (stable: nop, substitute, register; experimental: expand, block)",
    ),
    aggressive: bool = typer.Option(False, "--aggressive", "-a", help="Aggressive mode: more mutations"),
    force: bool = typer.Option(False, "--force", "-f", help="Force mutations to be different from original"),
    validation_mode: str = typer.Option(
        "structural",
        "--validation-mode",
        help="Validation mode: structural, runtime, symbolic, off",
    ),
    allow_limited_symbolic: bool = typer.Option(
        False,
        "--allow-limited-symbolic",
        help="Allow symbolic mode for passes that declare limited symbolic support",
    ),
    limited_symbolic_policy: str = typer.Option(
        "block",
        "--limited-symbolic-policy",
        help="How to handle limited symbolic passes: block, degrade-runtime, degrade-structural",
    ),
    rollback_policy: str = typer.Option(
        "skip-invalid-pass",
        "--rollback-policy",
        help="Rollback policy: fail-fast, skip-invalid-pass, skip-invalid-mutation",
    ),
    report: Path | None = typer.Option(
        None,
        "--report",
        help="Write a machine-readable JSON report",
    ),
    runtime_corpus: Path | None = typer.Option(
        None,
        "--runtime-corpus",
        help="Optional JSON corpus for runtime validation during mutate",
    ),
    runtime_compare_files: bool = typer.Option(
        False,
        "--runtime-compare-files",
        help="Compare monitored files during runtime validation",
    ),
    runtime_normalize_whitespace: bool = typer.Option(
        False,
        "--runtime-normalize-whitespace",
        help="Ignore trailing whitespace differences during runtime validation",
    ),
    runtime_timeout: int = typer.Option(
        10,
        "--runtime-timeout",
        help="Timeout per runtime validation test case in seconds",
    ),
    min_severity: str | None = typer.Option(
        None,
        "--min-severity",
        help="Fail with code 1 unless the final report contains at least one pass at or above: mismatch, without-coverage, bounded-only, clean, not-requested",
    ),
    require_pass_severity: list[str] = typer.Option(
        None,
        "--require-pass-severity",
        help="Require a specific pass severity in the final report, e.g. InstructionSubstitution=bounded-only",
    ),
    seed: int | None = typer.Option(None, "--seed", help="Deterministic seed for mutation selection"),
    cache: bool = typer.Option(
        False,
        "--cache",
        help="Enable analysis caching for faster repeated runs",
    ),
    clear_cache: bool = typer.Option(
        False,
        "--clear-cache",
        help="Clear the analysis cache before running",
    ),
    report_format: str = typer.Option("json", "--format", help="Report format: json (default) or sarif"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Apply tracked mutations to a binary and validate the result.

    Examples:
        r2morph mutate binary.exe -o output.exe
        r2morph mutate binary.exe -m nop -m substitute --report report.json
        r2morph mutate binary.exe --cache  # Enable caching for faster repeated runs
    """
    pass


def _run_morph_workflow(
    *,
    binary: Path,
    output: Path,
    mutations: list[str],
    aggressive: bool,
    force: bool,
    validation_mode: str,
    allow_limited_symbolic: bool,
    limited_symbolic_policy: str,
    rollback_policy: str,
    report: Path | None,
    runtime_corpus: Path | None,
    runtime_compare_files: bool,
    runtime_normalize_whitespace: bool,
    runtime_timeout: int,
    min_severity: str | None,
    require_pass_severity: list[str] | None,
    seed: int | None,
    report_format: str = "json",
) -> None:
    """Execute the mutation pipeline, validate, and write results.

    Separated from the morph() CLI command to keep typer declarations
    apart from business logic.
    """
    pass


def _evaluate_and_write_gates(
    *,
    report_payload: dict[str, Any],
    report_path: Path | None,
    min_severity: str | None,
    min_severity_rank: int | None,
    pass_severity_requirements: list[tuple[str, str, int]] | None,
    report_format: str = "json",
) -> None:
    """Evaluate severity gates, write report, and exit on failure."""
    pass


@app.command(name="mutate")
def mutate(
    binary: Path = typer.Argument(..., help="Path to binary file", exists=True),
    output: Path = typer.Option(None, "--output", "-o", help="Output path for morphed binary"),
    mutations: list[str] = typer.Option(
        ["nop", "substitute", "register"],
        "--mutation",
        "-m",
        help="Mutations to apply (stable: nop, substitute, register; experimental: expand, block)",
    ),
    aggressive: bool = typer.Option(False, "--aggressive", "-a", help="Aggressive mode: more mutations"),
    force: bool = typer.Option(False, "--force", "-f", help="Force mutations to be different from original"),
    validation_mode: str = typer.Option(
        "structural",
        "--validation-mode",
        help="Validation mode: structural, runtime, symbolic, off",
    ),
    allow_limited_symbolic: bool = typer.Option(
        False,
        "--allow-limited-symbolic",
        help="Allow symbolic mode for passes that declare limited symbolic support",
    ),
    limited_symbolic_policy: str = typer.Option(
        "block",
        "--limited-symbolic-policy",
        help="How to handle limited symbolic passes: block, degrade-runtime, degrade-structural",
    ),
    rollback_policy: str = typer.Option(
        "skip-invalid-pass",
        "--rollback-policy",
        help="Rollback policy: fail-fast, skip-invalid-pass, skip-invalid-mutation",
    ),
    report: Path | None = typer.Option(
        None,
        "--report",
        help="Write a machine-readable JSON report",
    ),
    runtime_corpus: Path | None = typer.Option(
        None,
        "--runtime-corpus",
        help="Optional JSON corpus for runtime validation during mutate",
    ),
    runtime_compare_files: bool = typer.Option(
        False,
        "--runtime-compare-files",
        help="Compare monitored files during runtime validation",
    ),
    runtime_normalize_whitespace: bool = typer.Option(
        False,
        "--runtime-normalize-whitespace",
        help="Ignore trailing whitespace differences during runtime validation",
    ),
    runtime_timeout: int = typer.Option(
        10,
        "--runtime-timeout",
        help="Timeout per runtime validation test case in seconds",
    ),
    min_severity: str | None = typer.Option(
        None,
        "--min-severity",
        help="Fail with code 1 unless the final report contains at least one pass at or above: mismatch, without-coverage, bounded-only, clean, not-requested",
    ),
    require_pass_severity: list[str] = typer.Option(
        None,
        "--require-pass-severity",
        help="Require a specific pass severity in the final report, e.g. InstructionSubstitution=bounded-only",
    ),
    seed: int | None = typer.Option(None, "--seed", help="Deterministic seed for mutation selection"),
    report_format: str = typer.Option("json", "--format", help="Report format: json (default) or sarif"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Alias for `morph` using the product-oriented command name."""
    pass


@app.command()
def validate(
    original: Path = typer.Argument(..., help="Original binary", exists=True),
    mutated: Path = typer.Argument(..., help="Mutated binary", exists=True),
    corpus: Path | None = typer.Option(
        None,
        "--corpus",
        help="Optional JSON corpus describing runtime test cases (see dataset/runtime_corpus.json)",
    ),
    compare_files: bool = typer.Option(
        False,
        "--compare-files",
        help="Compare monitored output files in addition to stdout/stderr/exitcode",
    ),
    normalize_whitespace: bool = typer.Option(
        False,
        "--normalize-whitespace",
        help="Ignore trailing whitespace differences in stdout/stderr",
    ),
    timeout: int = typer.Option(10, "--timeout", help="Timeout per test case in seconds"),
) -> None:
    """
    Run runtime validation for an original/mutated binary pair.

    Corpus schema:
        [
          {
            "description": "default-exec",
            "args": [],
            "stdin": "",
            "expected_exitcode": 0,
            "env": {},
            "working_dir": null,
            "monitored_files": []
          }
        ]
    """
    validator = _build_runtime_validator(
        timeout=timeout,
        corpus=corpus,
        compare_files=compare_files,
        normalize_whitespace=normalize_whitespace,
    )
    result = validator.validate(original, mutated)
    console.print_json(json.dumps(result.to_dict()))
    raise typer.Exit(0 if result.passed else 1)


@app.command()
def diff(
    original: Path = typer.Argument(..., help="Original binary", exists=True),
    mutated: Path = typer.Argument(..., help="Mutated binary", exists=True),
) -> None:
    """
    Show a lightweight diff summary between two binaries.
    """
    pass


@app.command()
def report(
    report_file: Path = typer.Argument(..., help="Report JSON generated by mutate", exists=True),
    only_pass: str | None = typer.Option(
        None,
        "--only-pass",
        help="Show only mutations produced by the specified pass name",
    ),
    only_status: str | None = typer.Option(
        None,
        "--only-status",
        help="Show only mutations with the specified symbolic_status",
    ),
    only_mismatches: bool = typer.Option(
        False,
        "--only-mismatches",
        help="Show only mutations with symbolic observable mismatches",
    ),
    summary_only: bool = typer.Option(
        False,
        "--summary-only",
        help="Show only the textual summary without printing report JSON",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the filtered report JSON to a file",
    ),
    require_results: bool = typer.Option(
        False,
        "--require-results",
        help="Exit with code 1 when the filtered view contains no mutations",
    ),
    min_severity: str | None = typer.Option(
        None,
        "--min-severity",
        help="Require at least one pass with severity: mismatch, without-coverage, bounded-only, clean, not-requested",
    ),
    only_expected_severity: str | None = typer.Option(
        None,
        "--only-expected-severity",
        help="Filter persisted gate failures by expected severity: mismatch, without-coverage, bounded-only, clean, not-requested",
    ),
    only_pass_failure: str | None = typer.Option(
        None,
        "--only-pass-failure",
        help="Filter persisted gate failures to a specific pass name",
    ),
    only_degraded: bool = typer.Option(
        False,
        "--only-degraded",
        help="Show/report only executions where requested and effective validation modes differ",
    ),
    only_failed_gates: bool = typer.Option(
        False,
        "--only-failed-gates",
        help="Show/report only executions where persisted CLI gate evaluation failed",
    ),
    only_risky_passes: bool = typer.Option(
        False,
        "--only-risky-passes",
        help="Show/report only passes with symbolic mismatches, structural issues, or non-clean symbolic severity",
    ),
    only_structural_risk: bool = typer.Option(
        False,
        "--only-structural-risk",
        help="Show/report only passes with structural issues",
    ),
    only_symbolic_risk: bool = typer.Option(
        False,
        "--only-symbolic-risk",
        help="Show/report only passes with symbolic mismatches or non-clean symbolic severity",
    ),
    only_clean_passes: bool = typer.Option(
        False,
        "--only-clean-passes",
        help="Show/report only passes with no structural issues and clean symbolic evidence",
    ),
    only_covered_passes: bool = typer.Option(
        False,
        "--only-covered-passes",
        help="Show/report only clean passes with effective symbolic coverage",
    ),
    only_uncovered_passes: bool = typer.Option(
        False,
        "--only-uncovered-passes",
        help="Show/report only clean passes without effective symbolic coverage",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json (default) or sarif",
    ),
) -> None:
    """
    Display a previously generated engine report.
    """
    if output_format.lower() == "sarif":
        from r2morph.reporting.sarif_formatter import format_as_sarif

    with open(report_file, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    context = _resolve_report_context(
        payload=payload,
        only_pass=only_pass,
        only_pass_failure=only_pass_failure,
        only_expected_severity=only_expected_severity,
    )
    summary = context["summary"]
    resolved_only_pass = context["resolved_only_pass"]
    requested_validation_mode = context["requested_validation_mode"]
    effective_validation_mode = context["effective_validation_mode"]
    validation_policy = context["validation_policy"]
    gate_evaluation = context["gate_evaluation"]
    gate_failure_summary = context["gate_failure_summary"]
    gate_failure_priority = context["gate_failure_priority"]
    gate_failure_severity_priority = context["gate_failure_severity_priority"]
    failed_gates = context["failed_gates"]
    degraded_validation = context["degraded_validation"]
    degraded_passes = context["degraded_passes"]

    pass_results = payload.get("passes", {})
    general_state = _resolve_general_report_flow_state(
        payload=payload,
        summary=summary,
        pass_results=pass_results,
        requested_validation_mode=requested_validation_mode,
        effective_validation_mode=effective_validation_mode,
        degraded_validation=degraded_validation,
        degraded_passes=degraded_passes,
        failed_gates=failed_gates,
        validation_policy=validation_policy,
        gate_evaluation=gate_evaluation,
        gate_failure_summary=gate_failure_summary,
        gate_failure_priority=gate_failure_priority,
        gate_failure_severity_priority=gate_failure_severity_priority,
        resolved_only_pass=resolved_only_pass,
        only_status=only_status,
        only_degraded=only_degraded,
        only_failed_gates=only_failed_gates,
        only_risky_passes=only_risky_passes,
        only_structural_risk=only_structural_risk,
        only_symbolic_risk=only_symbolic_risk,
        only_uncovered_passes=only_uncovered_passes,
        only_covered_passes=only_covered_passes,
        only_clean_passes=only_clean_passes,
    )
    _, min_severity_rank = _resolve_min_severity(min_severity)
    dispatch_state = _build_report_dispatch_state(
        context=context,
        general_state=general_state,
        payload=payload,
        pass_results=pass_results,
        only_pass=only_pass,
        only_pass_failure=only_pass_failure,
        only_status=only_status,
        only_degraded=only_degraded,
        only_failed_gates=only_failed_gates,
        only_risky_passes=only_risky_passes,
        only_structural_risk=only_structural_risk,
        only_symbolic_risk=only_symbolic_risk,
        only_uncovered_passes=only_uncovered_passes,
        only_covered_passes=only_covered_passes,
        only_clean_passes=only_clean_passes,
        output=output,
        summary_only=summary_only,
        require_results=require_results,
        min_severity=min_severity,
        min_severity_rank=min_severity_rank,
        only_expected_severity=only_expected_severity,
        only_mismatches=only_mismatches,
    )
    if output_format.lower() == "sarif":
        from r2morph.reporting.sarif_formatter import format_as_sarif

        mutations_list = payload.get("mutations", [])
        validations_list = payload.get("validations", [])
        binary_path_str = payload.get("binary_path", "")
        sarif_report = format_as_sarif(mutations_list, validations_list, binary_path_str)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(sarif_report.to_json())
            rprint(f"[green]SARIF report written to[/green] {output}")
        else:
            print(sarif_report.to_json())
        return

    _dispatch_report_flow(**dispatch_state)


@app.command()
def version() -> None:
    """
    Display version information.
    """
    rprint(f"[bold cyan]r2morph[/bold cyan] version [green]{__version__}[/green]")
    rprint("Metamorphic mutation engine with validation")


@app.command()
def cache(
    clear: bool = typer.Option(False, "--clear", "-c", help="Clear all cached analysis results"),
    stats: bool = typer.Option(False, "--stats", "-s", help="Show cache statistics"),
    path: Path | None = typer.Option(None, "--path", "-p", help="Custom cache directory path"),
) -> None:
    """
    Manage the analysis cache.

    Examples:
        r2morph cache --stats          # Show cache statistics
        r2morph cache --clear          # Clear all cached data
        r2morph cache --clear --path /custom/cache  # Clear specific cache directory
    """
    pass


def main() -> None:
    """Entry point for the CLI."""
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in KNOWN_COMMANDS:
        parser = argparse.ArgumentParser(prog="r2morph")
        parser.add_argument("input_file")
        parser.add_argument("output_file", nargs="?")
        parser.add_argument("-i", "--input", dest="input_opt")
        parser.add_argument("-o", "--output", dest="output_opt")
        parser.add_argument("-a", "--aggressive", action="store_true")
        parser.add_argument("-f", "--force", action="store_true")
        parser.add_argument("--seed", type=int)
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("-d", "--debug", action="store_true")
        args = parser.parse_args(argv)
        input_file = Path(args.input_opt or args.input_file)
        output_file = Path(args.output_opt or args.output_file) if (args.output_opt or args.output_file) else None
        _run_simple_mode(
            input_file,
            output_file,
            aggressive=args.aggressive,
            force=args.force,
            seed=args.seed,
            verbose=args.verbose,
            debug=args.debug,
        )
        return
    app()


if __name__ == "__main__":
    main()
