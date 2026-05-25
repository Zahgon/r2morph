"""
Factory functions for dependency injection following SOLID principles.

This module provides factory functions that create properly configured instances
while respecting Interface Segregation Principle (ISP).

Usage:
    from r2morph.factories import create_binary_reader, create_report_emitter

    reader = create_binary_reader(r2_connection)
    emitter = create_report_emitter(console=Console())
"""

from pathlib import Path
from typing import Any

from rich.console import Console


def create_binary_reader(
    r2: Any,
    lazy_load: bool = True,
) -> Any:
    """
    Factory function for BinaryReader.

    Args:
        r2: r2pipe connection instance
        lazy_load: Whether to use lazy loading for functions

    Returns:
        Configured BinaryReader instance
    """
    pass


def create_binary_writer(
    r2: Any,
    path: Path,
    writable: bool = False,
) -> Any:
    """
    Factory function for BinaryWriter.

    Args:
        r2: r2Pipe connection instance
        path: Path to the binary file
        writable: Whether the binary was opened in write mode

    Returns:
        Configured BinaryWriter instance
    """
    pass


def create_assembly_service() -> Any:
    """
    Factory function for AssemblyService.

    Returns:
        Configured AssemblyService instance
    """
    pass


def create_memory_manager(
    batch_size: int = 1000,
    low_memory: bool = False,
) -> Any:
    """
    Factory function for MemoryManager.

    Args:
        batch_size: Number of mutations before checkpoint
        low_memory: Whether to enable low memory mode

    Returns:
        Configured MemoryManager instance
    """
    pass


def create_report_emitter(
    console: Console | None = None,
) -> dict[str, Any]:
    """
    Factory function for report emission.

    Args:
        console: Optional Console instance (creates new if None)

    Returns:
        Dict with emit functions
    """
    pass


def create_console_renderer(
    console: Console | None = None,
) -> dict[str, Any]:
    """
    Factory function for console rendering.

    Args:
        console: Optional Console instance (creates new if None)

    Returns:
        Dict with render functions
    """
    pass


def create_gate_evaluator() -> type:
    """
    Factory function for GateEvaluator.

    Returns:
        GateEvaluator class (stateless, can be reused)
    """
    pass


def create_summary_aggregator() -> Any:
    """
    Factory function for SummaryAggregator.

    Returns:
        SummaryAggregator instance
    """
    pass


def create_symbolic_aggregator() -> type:
    """
    Factory function for SymbolicAggregator.

    Returns:
        SymbolicAggregator class (stateless, can be reused)
    """
    pass


def create_evidence_aggregator() -> type:
    """
    Factory function for EvidenceAggregator.

    Returns:
        EvidenceAggregator class (stateless, can be reused)
    """
    pass


def create_report_builder() -> type:
    """
    Factory function for ReportBuilder.

    Returns:
        ReportBuilder class (stateless, can be reused)
    """
    pass


def create_pass_filter_resolver() -> type:
    """
    Factory function for PassFilterResolver.

    Returns:
        PassFilterResolver class (stateless, can be reused)
    """
    pass


def create_report_filters() -> type:
    """
    Factory function for ReportFilters.

    Returns:
        ReportFilters class (stateless, can be reused)
    """
    pass


__all__ = [
    "create_binary_reader",
    "create_binary_writer",
    "create_assembly_service",
    "create_memory_manager",
    "create_report_emitter",
    "create_console_renderer",
    "create_gate_evaluator",
    "create_summary_aggregator",
    "create_symbolic_aggregator",
    "create_evidence_aggregator",
    "create_report_builder",
    "create_pass_filter_resolver",
    "create_report_filters",
]
