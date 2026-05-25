"""
Summary and evidence aggregation logic extracted from cli.py and engine.py.

This module handles symbolic coverage summarization, evidence aggregation,
and pass result normalization.
"""

from dataclasses import dataclass
from typing import Any

from r2morph.reporting.gate_evaluator import ROLLBACK_SEVERITY_ORDER


@dataclass
class SymbolicStats:
    """Aggregated symbolic validation statistics."""

    symbolic_requested: int = 0
    observable_match: int = 0
    observable_mismatch: int = 0
    bounded_only: int = 0
    without_coverage: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "symbolic_requested": self.symbolic_requested,
            "observable_match": self.observable_match,
            "observable_mismatch": self.observable_mismatch,
            "bounded_only": self.bounded_only,
            "without_coverage": self.without_coverage,
        }


class SymbolicAggregator:
    """Aggregates symbolic validation statistics from mutation records."""

    @staticmethod
    def summarize_from_mutations(
        mutations: list[dict[str, Any]],
    ) -> tuple[dict[str, int], list[dict[str, Any]], dict[str, dict[str, int]]]:
        """Build global and per-pass symbolic status summaries."""
        pass

    @staticmethod
    def summarize_coverage_by_pass(
        mutations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Aggregate symbolic coverage outcomes by pass for machine-readable reports."""
        pass

    @staticmethod
    def summarize_issue_passes(
        mutations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Aggregate symbolic issue counts by pass for machine-readable reports."""
        pass

    @staticmethod
    def summarize_observable_mismatches_by_pass(
        mutations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Aggregate observable symbolic mismatches by pass for report triage."""
        pass


class EvidenceAggregator:
    """Aggregates evidence summaries from pass results."""

    @staticmethod
    def summarize_structural_evidence(
        structural_regions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a compact structural-evidence digest from region-level findings."""
        pass

    @staticmethod
    def build_for_pass(
        pass_name: str,
        pass_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a compact structural/symbolic evidence summary for one pass."""
        pass

    @staticmethod
    def summarize_pass_evidence(pass_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Aggregate per-pass evidence summaries for tooling."""
        pass


class SummaryAggregator:
    """Aggregates summaries across all passes for report generation."""

    @staticmethod
    def summarize_degradation_roles(
        pass_results: dict[str, Any],
    ) -> dict[str, int]:
        """Aggregate degradation role counts across pass validation contexts."""
        pass

    @staticmethod
    def summarize_diff_digest(pass_results: dict[str, Any]) -> dict[str, Any]:
        """Build a compact diff digest across passes."""
        pass

    @staticmethod
    def summarize_pass_timings(pass_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Build a compact per-pass timing summary for tooling."""
        pass

    @staticmethod
    def summarize_discarded_mutations(
        discarded_mutations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate discarded mutations by pass and reason."""
        pass
