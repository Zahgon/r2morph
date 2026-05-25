"""Report builder extensions: build and populate functions for report payloads.

Extracted from cli.py -- no logic changes.
"""

from pathlib import Path
from typing import Any

from r2morph.reporting.report_helpers import (
    _sort_pass_evidence,
    _summary_first,
    _visible_rows,
    _resolve_general_report_views,
    _resolve_summary_pass_sources,
)


def _build_base_filtered_summary(
    *,
    mutations: list[dict[str, Any]],
    symbolic_requested: int,
    observable_match: int,
    observable_mismatch: int,
    bounded_only: int,
    observable_not_run: int,
    requested_validation_mode: str | None,
    effective_validation_mode: str | None,
    degraded_validation: bool,
    degraded_passes: list[dict[str, Any]],
    risky_pass_names: set[str],
    structural_risk_pass_names: set[str],
    symbolic_risk_pass_names: set[str],
    covered_pass_names: set[str],
    uncovered_pass_names: set[str],
    clean_pass_names: set[str],
    failed_gates: bool,
    validation_policy: dict[str, Any] | None,
    gate_evaluation: dict[str, Any],
    gate_failure_summary: dict[str, Any],
    summary: dict[str, Any],
    gate_failure_priority: list[dict[str, Any]],
    gate_failure_severity_priority: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the base filtered_summary payload used by general report views."""
    pass


def _build_general_filtered_summary(
    *,
    summary: dict[str, Any],
    mutations: list[dict[str, Any]],
    pass_results: dict[str, Any],
    pass_support: dict[str, Any],
    requested_validation_mode: str | None,
    effective_validation_mode: str | None,
    degraded_validation: bool,
    degraded_passes: list[dict[str, Any]],
    risky_pass_names: set[str],
    structural_risk_pass_names: set[str],
    symbolic_risk_pass_names: set[str],
    covered_pass_names: set[str],
    uncovered_pass_names: set[str],
    clean_pass_names: set[str],
    failed_gates: bool,
    validation_policy: dict[str, Any] | None,
    gate_evaluation: dict[str, Any],
    gate_failure_summary: dict[str, Any],
    gate_failure_priority: list[dict[str, Any]],
    gate_failure_severity_priority: list[dict[str, Any]],
    symbolic_requested: int,
    observable_match: int,
    observable_mismatch: int,
    bounded_only: int,
    observable_not_run: int,
    by_pass: dict[str, dict[str, int]],
    degradation_roles: dict[str, int],
    normalized_pass_map: dict[str, dict[str, Any]],
    selected_risk_pass_names: set[str],
    resolved_only_pass: str | None,
    only_risky_filters: bool,
    only_degraded: bool,
    only_risky_passes: bool,
    only_structural_risk: bool,
    only_symbolic_risk: bool,
    only_uncovered_passes: bool,
    only_covered_passes: bool,
    only_clean_passes: bool,
    only_failed_gates: bool,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Build the general filtered_summary payload for report()."""
    pass


def _build_only_mismatches_filtered_summary(
    *,
    filtered_mutations: list[dict[str, Any]],
    filtered_passes: list[str],
    mismatch_counts_by_pass: dict[str, int],
    mismatch_observables_by_pass: dict[str, list[str]],
    persisted_mismatch_priority: list[dict[str, Any]],
    mismatch_severity_rows: list[dict[str, Any]],
    mismatch_pass_context: dict[str, Any],
    requested_validation_mode: str,
    effective_validation_mode: str,
    degraded_validation: bool,
    mismatch_degraded_passes: list[dict[str, Any]],
    degraded_passes: list[dict[str, Any]],
    degradation_roles: dict[str, int],
    failed_gates: bool,
    pass_support: dict[str, Any],
    gate_evaluation: dict[str, Any],
    gate_failure_summary: dict[str, Any],
    gate_failure_priority: list[dict[str, Any]],
    gate_failure_severity_priority: list[dict[str, Any]],
    min_severity: str | None,
    only_expected_severity: str | None,
    resolved_only_pass_failure: str | None,
    validation_policy: dict[str, Any] | None,
    pass_region_evidence_map: dict[str, list[dict[str, Any]]] | None = None,
    mismatch_final_rows: list[dict[str, Any]] | None = None,
    mismatch_final_by_pass: dict[str, dict[str, Any]] | None = None,
    mismatch_compact_rows: list[dict[str, Any]] | None = None,
    mismatch_compact_by_pass: dict[str, dict[str, Any]] | None = None,
    mismatch_compact_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the filtered_summary payload for `report --only-mismatches`."""
    final_rows = list(mismatch_final_rows or [])
    compact_rows = list(mismatch_compact_rows or [])
    compact_by_pass = dict(mismatch_compact_by_pass or {})
    compact_summary = dict(mismatch_compact_summary or {})
    final_by_pass = dict(mismatch_final_by_pass or {})
    compact_row_by_pass = {str(row.get("pass_name")): dict(row) for row in compact_rows if row.get("pass_name")}
    if not final_rows and compact_rows:
        if final_by_pass:
            final_rows = [dict(final_by_pass[pass_name]) for pass_name in sorted(final_by_pass)]
        else:
            final_rows = [
                {
                    "pass_name": str(row.get("pass_name", "")),
                    "mismatch_count": int(row.get("mismatch_count", 0)),
                    "severity": row.get("severity", "mismatch"),
                    "role": row.get("role", "requested-mode"),
                    "symbolic_confidence": row.get("symbolic_confidence", "unknown"),
                    "degraded_execution": bool(row.get("degraded_execution", False)),
                    "region_count": int(row.get("region_count", 0)),
                    "region_mismatch_count": int(row.get("region_mismatch_count", 0)),
                    "region_exit_match_count": int(row.get("region_exit_match_count", 0)),
                    "compact_region": dict(row.get("compact_region", {})),
                }
                for row in compact_rows
            ]
    elif final_rows:
        enriched_final_rows = []
        for row in final_rows:
            pass_name = str(row.get("pass_name", ""))
            compact_row = compact_row_by_pass.get(pass_name, {})
            enriched = dict(row)
            if "compact_region" not in enriched and compact_row.get("compact_region"):
                enriched["compact_region"] = dict(compact_row.get("compact_region", {}))
            enriched_final_rows.append(enriched)
        final_rows = enriched_final_rows
    if not compact_by_pass and compact_rows:
        compact_by_pass = {str(row.get("pass_name")): dict(row) for row in compact_rows if row.get("pass_name")}
    if not compact_summary:
        compact_summary = {
            "pass_count": len(compact_rows) or len(filtered_passes),
            "mismatch_count": sum(mismatch_counts_by_pass.values()),
            "degraded_pass_count": len([row for row in compact_rows if row.get("degraded_execution")]),
            "region_count": sum(int(row.get("region_count", 0)) for row in compact_rows),
            "region_mismatch_count": sum(int(row.get("region_mismatch_count", 0)) for row in compact_rows),
            "region_exit_match_count": sum(int(row.get("region_exit_match_count", 0)) for row in compact_rows),
            "passes": list(filtered_passes),
        }
    filtered_summary: dict[str, Any] = {
        "mutations": len(filtered_mutations),
        "passes": filtered_passes,
        "symbolic_requested": sum(
            1 for mutation in filtered_mutations if mutation.get("metadata", {}).get("symbolic_requested")
        ),
        "observable_match": 0,
        "observable_mismatch": len(filtered_mutations),
        "bounded_only": 0,
        "without_symbolic_coverage": 0,
        "symbolic_statuses": (
            {"bounded-step-observable-mismatch": len(filtered_mutations)} if filtered_mutations else {}
        ),
        "pass_capabilities": {
            pass_name: pass_support.get(pass_name, {}).get("validator_capabilities", {})
            for pass_name in filtered_passes
            if pass_support.get(pass_name)
        },
        "symbolic_severity_by_pass": mismatch_severity_rows,
        "mismatch_counts_by_pass": mismatch_counts_by_pass,
        "mismatch_observables_by_pass": mismatch_observables_by_pass,
        "observable_mismatch_priority": [
            dict(row) for row in persisted_mismatch_priority if row.get("pass_name") in filtered_passes
        ]
        or [
            {
                "pass_name": pass_name,
                "mismatch_count": mismatch_counts_by_pass.get(pass_name, 0),
                "observables": mismatch_observables_by_pass.get(pass_name, []),
            }
            for pass_name in filtered_passes
        ],
        "pass_validation_context": mismatch_pass_context,
        "pass_region_evidence_map": {
            pass_name: list((pass_region_evidence_map or {}).get(pass_name, []))
            for pass_name in filtered_passes
            if (pass_region_evidence_map or {}).get(pass_name)
        },
        "mismatch_compact_rows": compact_rows,
        "mismatch_compact_by_pass": compact_by_pass,
        "mismatch_compact_summary": compact_summary,
        "mismatch_final_rows": final_rows,
        "mismatch_final_by_pass": final_by_pass,
        "requested_validation_mode": requested_validation_mode,
        "validation_mode": effective_validation_mode,
        "degraded_validation": degraded_validation,
        "degraded_passes": mismatch_degraded_passes or degraded_passes,
        "degradation_roles": degradation_roles,
        "failed_gates": failed_gates,
    }
    if gate_evaluation:
        filtered_summary["gate_evaluation"] = gate_evaluation
        filtered_summary["gate_failures"] = gate_failure_summary
        filtered_summary["gate_failure_priority"] = gate_failure_priority
        filtered_summary["gate_failure_severity_priority"] = gate_failure_severity_priority
    if min_severity is not None:
        filtered_summary["min_severity"] = min_severity
    if only_expected_severity is not None:
        filtered_summary["only_expected_severity"] = only_expected_severity
    if resolved_only_pass_failure is not None:
        filtered_summary["only_pass_failure"] = resolved_only_pass_failure
    if validation_policy is not None:
        filtered_summary["validation_policy"] = validation_policy
    return filtered_summary


def _build_only_mismatches_payload(
    *,
    payload: dict[str, Any],
    summary: dict[str, Any],
    filtered_summary: dict[str, Any],
    filtered_mutations: list[dict[str, Any]],
    filtered_passes: list[str],
    mismatch_counts_by_pass: dict[str, int],
    mismatch_observables_by_pass: dict[str, list[str]],
    persisted_mismatch_priority: list[dict[str, Any]],
    mismatch_severity_rows: list[dict[str, Any]],
    mismatch_pass_context: dict[str, Any],
    requested_validation_mode: str,
    effective_validation_mode: str,
    degraded_validation: bool,
    mismatch_degraded_passes: list[dict[str, Any]],
    degraded_passes: list[dict[str, Any]],
    degradation_roles: dict[str, int],
    failed_gates: bool,
    pass_support: dict[str, Any],
    gate_evaluation: dict[str, Any],
    gate_failure_summary: dict[str, Any],
    gate_failure_priority: list[dict[str, Any]],
    gate_failure_severity_priority: list[dict[str, Any]],
    min_severity: str | None,
    only_expected_severity: str | None,
    resolved_only_pass_failure: str | None,
    validation_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build the filtered payload for report --only-mismatches."""
    mismatch_view = dict((dict(summary.get("report_views", {}) or {})).get("only_mismatches", {}) or {})
    filtered_payload = dict(payload)
    filtered_payload["mutations"] = filtered_mutations
    filtered_payload["filtered_summary"] = _build_only_mismatches_filtered_summary(
        filtered_mutations=filtered_mutations,
        filtered_passes=filtered_passes,
        mismatch_counts_by_pass=mismatch_counts_by_pass,
        mismatch_observables_by_pass=mismatch_observables_by_pass,
        persisted_mismatch_priority=persisted_mismatch_priority,
        mismatch_severity_rows=mismatch_severity_rows,
        mismatch_pass_context=mismatch_pass_context,
        requested_validation_mode=requested_validation_mode,
        effective_validation_mode=effective_validation_mode,
        degraded_validation=degraded_validation,
        mismatch_degraded_passes=mismatch_degraded_passes,
        degraded_passes=degraded_passes,
        degradation_roles=degradation_roles,
        failed_gates=failed_gates,
        pass_support=pass_support,
        gate_evaluation=gate_evaluation,
        gate_failure_summary=gate_failure_summary,
        gate_failure_priority=gate_failure_priority,
        gate_failure_severity_priority=gate_failure_severity_priority,
        min_severity=min_severity,
        only_expected_severity=only_expected_severity,
        resolved_only_pass_failure=resolved_only_pass_failure,
        validation_policy=validation_policy,
        pass_region_evidence_map=filtered_summary.get("pass_region_evidence_map", {}),
        mismatch_final_rows=list(mismatch_view.get("final_rows", []) or []),
        mismatch_final_by_pass=dict(mismatch_view.get("final_by_pass", {}) or {}),
        mismatch_compact_rows=list(mismatch_view.get("compact_rows", []) or []),
        mismatch_compact_by_pass=dict(mismatch_view.get("compact_by_pass", {}) or {}),
        mismatch_compact_summary=dict(mismatch_view.get("compact_summary", {}) or {}),
    )
    return filtered_payload


def _build_general_report_payload(
    *,
    payload: dict[str, Any],
    mutations: list[dict[str, Any]],
    filtered_summary: dict[str, Any],
    resolved_only_pass: str | None,
    only_status: str | None,
    only_degraded: bool,
    only_failed_gates: bool,
    only_risky_passes: bool,
    only_uncovered_passes: bool,
    only_covered_passes: bool,
    only_clean_passes: bool,
    only_structural_risk: bool,
    only_symbolic_risk: bool,
    min_severity: str | None,
    only_expected_severity: str | None,
    resolved_only_pass_failure: str | None,
) -> dict[str, Any]:
    """Build the filtered payload for the general report path."""
    filtered_payload = dict(payload)
    filtered_payload["mutations"] = mutations
    filtered_payload["filtered_summary"] = filtered_summary
    report_filters = _build_report_filters(
        resolved_only_pass=resolved_only_pass,
        only_status=only_status,
        only_degraded=only_degraded,
        only_failed_gates=only_failed_gates,
        only_risky_passes=only_risky_passes,
        only_uncovered_passes=only_uncovered_passes,
        only_covered_passes=only_covered_passes,
        only_clean_passes=only_clean_passes,
        only_structural_risk=only_structural_risk,
        only_symbolic_risk=only_symbolic_risk,
        min_severity=min_severity,
        only_expected_severity=only_expected_severity,
        resolved_only_pass_failure=resolved_only_pass_failure,
    )
    if report_filters:
        filtered_payload["report_filters"] = report_filters
    if min_severity is not None:
        filtered_payload["filtered_summary"]["min_severity"] = min_severity
    if only_expected_severity is not None:
        filtered_payload["filtered_summary"]["only_expected_severity"] = only_expected_severity
    if resolved_only_pass_failure is not None:
        filtered_payload["filtered_summary"]["only_pass_failure"] = resolved_only_pass_failure
    return filtered_payload


def _build_report_dispatch_state(
    *,
    context: dict[str, Any],
    general_state: dict[str, Any],
    payload: dict[str, Any],
    pass_results: dict[str, Any],
    only_pass: str | None,
    only_pass_failure: str | None,
    only_status: str | None,
    only_degraded: bool,
    only_failed_gates: bool,
    only_risky_passes: bool,
    only_structural_risk: bool,
    only_symbolic_risk: bool,
    only_uncovered_passes: bool,
    only_covered_passes: bool,
    only_clean_passes: bool,
    output: Path | None,
    summary_only: bool,
    require_results: bool,
    min_severity: str | None,
    min_severity_rank: int | None,
    only_expected_severity: str | None,
    only_mismatches: bool,
) -> dict[str, Any]:
    """Assemble the final dispatch state for report()."""
    return {
        "only_mismatches": only_mismatches,
        "payload": payload,
        "summary": context["summary"],
        "filtered_summary": general_state["filtered_summary"],
        "mutations": general_state["mutations"],
        "pass_results": pass_results,
        "pass_support": general_state["pass_support"],
        "requested_validation_mode": context["requested_validation_mode"],
        "effective_validation_mode": context["effective_validation_mode"],
        "degraded_validation": context["degraded_validation"],
        "degraded_passes": general_state["degraded_passes"],
        "degradation_roles": general_state["degradation_roles"],
        "failed_gates": context["failed_gates"],
        "gate_evaluation": context["gate_evaluation"],
        "gate_requested": context["gate_requested"],
        "gate_results": context["gate_results"],
        "gate_failure_summary": context["gate_failure_summary"],
        "gate_failure_priority": context["gate_failure_priority"],
        "gate_failure_severity_priority": context["gate_failure_severity_priority"],
        "validation_policy": context["validation_policy"],
        "resolved_only_pass": context["resolved_only_pass"],
        "resolved_only_pass_failure": context["resolved_only_pass_failure"],
        "only_status": only_status,
        "only_degraded": only_degraded,
        "only_failed_gates": only_failed_gates,
        "only_risky_passes": only_risky_passes,
        "only_structural_risk": only_structural_risk,
        "only_symbolic_risk": only_symbolic_risk,
        "only_uncovered_passes": only_uncovered_passes,
        "only_covered_passes": only_covered_passes,
        "only_clean_passes": only_clean_passes,
        "output": output,
        "summary_only": summary_only,
        "require_results": require_results,
        "min_severity": min_severity,
        "min_severity_rank": min_severity_rank,
        "only_expected_severity": only_expected_severity,
        "only_pass": only_pass,
        "only_pass_failure": only_pass_failure,
        "selected_risk_pass_names": general_state["selected_risk_pass_names"],
        "symbolic_state": general_state["symbolic_state"],
    }


def _build_report_filters(
    *,
    resolved_only_pass: str | None,
    only_status: str | None,
    only_degraded: bool,
    only_failed_gates: bool,
    only_risky_passes: bool,
    only_uncovered_passes: bool,
    only_covered_passes: bool,
    only_clean_passes: bool,
    only_structural_risk: bool,
    only_symbolic_risk: bool,
    only_mismatches: bool = False,
    min_severity: str | None = None,
    only_expected_severity: str | None = None,
    resolved_only_pass_failure: str | None = None,
) -> dict[str, object]:
    """Build a stable report_filters payload."""
    report_filters: dict[str, object] = {}
    if only_mismatches:
        report_filters["only_mismatches"] = True
    if resolved_only_pass:
        report_filters["only_pass"] = resolved_only_pass
    if only_status:
        report_filters["only_status"] = only_status
    if only_degraded:
        report_filters["only_degraded"] = True
    if only_failed_gates:
        report_filters["only_failed_gates"] = True
    if only_risky_passes:
        report_filters["only_risky_passes"] = True
    if only_uncovered_passes:
        report_filters["only_uncovered_passes"] = True
    if only_covered_passes:
        report_filters["only_covered_passes"] = True
    if only_clean_passes:
        report_filters["only_clean_passes"] = True
    if only_structural_risk:
        report_filters["only_structural_risk"] = True
    if only_symbolic_risk:
        report_filters["only_symbolic_risk"] = True
    if min_severity is not None:
        report_filters["min_severity"] = min_severity
    if only_expected_severity is not None:
        report_filters["only_expected_severity"] = only_expected_severity
    if resolved_only_pass_failure is not None:
        report_filters["only_pass_failure"] = resolved_only_pass_failure
    return report_filters


def _build_filtered_summary_gate_sections(
    *,
    summary: dict[str, Any],
    gate_evaluation: dict[str, Any],
    gate_failure_summary: dict[str, Any],
    gate_failure_priority: list[dict[str, Any]],
    gate_failure_severity_priority: list[dict[str, Any]],
    failed_gates: bool,
) -> dict[str, Any]:
    """Build filtered_summary gate-related sections from persisted report views first."""
    pass


def _build_filtered_summary_risk_coverage_sections(
    *,
    summary: dict[str, Any],
    risky_pass_names: set[str],
    structural_risk_pass_names: set[str],
    symbolic_risk_pass_names: set[str],
    covered_pass_names: set[str],
    uncovered_pass_names: set[str],
    clean_pass_names: set[str],
) -> dict[str, Any]:
    """Build filtered_summary risk/coverage sections from persisted summary first."""
    pass


def _build_filtered_summary_degradation_sections(
    *,
    summary: dict[str, Any],
    validation_policy: dict[str, Any] | None,
    requested_validation_mode: str | None,
    effective_validation_mode: str | None,
    degraded_validation: bool,
    degraded_passes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build filtered_summary degradation/validation-mode sections."""
    pass


def _populate_pass_capabilities_and_context(
    *,
    filtered_summary: dict[str, Any],
    pass_results: dict[str, Any],
    pass_support: dict[str, Any],
    requested_validation_mode: str | None,
    effective_validation_mode: str | None,
    degradation_roles: dict[str, int],
    normalized_pass_map: dict[str, dict[str, Any]],
    summary_pass_capabilities: dict[str, Any],
    summary_pass_validation_context: dict[str, Any],
) -> None:
    """Populate pass_capabilities and pass_validation_context for each visible pass."""
    pass


def _populate_symbolic_issue_passes(
    *,
    filtered_summary: dict[str, Any],
    summary: dict[str, Any],
    pass_results: dict[str, Any],
    by_pass: dict[str, dict[str, int]],
    summary_symbolic_issue_map: dict[str, Any],
    summary_pass_evidence_compact: list[dict[str, Any]],
    summary_pass_evidence_map: dict[str, Any],
    summary_general_symbolic: dict[str, Any],
) -> None:
    """Populate pass_evidence and symbolic_issue_passes sections."""
    pass


def _populate_symbolic_coverage_and_severity(
    *,
    filtered_summary: dict[str, Any],
    by_pass: dict[str, dict[str, int]],
    degraded_passes: list[dict[str, Any]],
    only_degraded: bool,
    summary_symbolic_coverage_map: dict[str, Any],
    summary_symbolic_severity_map: dict[str, Any],
    pass_results: dict[str, Any],
) -> None:
    """Populate symbolic_coverage_by_pass and symbolic_severity_by_pass sections."""
    pass


def _populate_triage_and_results(
    *,
    filtered_summary: dict[str, Any],
    summary: dict[str, Any],
    summary_pass_triage_map: dict[str, Any],
    summary_normalized_pass_results: list[dict[str, Any]],
    summary_pass_capability_summary_map: dict[str, Any],
    summary_validation_role_map: dict[str, Any],
    summary_report_views: dict[str, Any],
    summary_general_pass_rows: list[dict[str, Any]],
    summary_general_passes: list[dict[str, Any]],
    summary_discarded_mutation_summary: dict[str, Any],
    summary_discarded_view: dict[str, Any],
    summary_discarded_mutation_priority: list[dict[str, Any]],
    summary_general_discards: dict[str, Any],
) -> None:
    """Populate triage rows, normalized results, capability summary, and validation role rows."""
    pass


def _populate_pass_evidence(
    *,
    filtered_summary: dict[str, Any],
    pass_results: dict[str, Any],
    normalized_pass_map: dict[str, dict[str, Any]],
    selected_risk_pass_names: set[str],
    resolved_only_pass: str | None,
    only_risky_filters: bool,
    summary_pass_region_evidence_map: dict[str, Any],
    summary_pass_evidence_map: dict[str, Any],
    summary_general_pass_rows: list[dict[str, Any]],
) -> None:
    """Populate pass_evidence and pass_region_evidence_map with fallback chains."""
    pass


def _apply_risk_filters(
    *,
    filtered_summary: dict[str, Any],
    selected_risk_pass_names: set[str],
    only_risky_filters: bool,
) -> None:
    """Apply risk-based filtering and final symbolic summary fallbacks."""
    pass


def _populate_filtered_summary_pass_sections(
    *,
    filtered_summary: dict[str, Any],
    summary: dict[str, Any],
    pass_results: dict[str, Any],
    pass_support: dict[str, Any],
    requested_validation_mode: str | None,
    effective_validation_mode: str | None,
    degraded_passes: list[dict[str, Any]],
    degradation_roles: dict[str, int],
    by_pass: dict[str, dict[str, int]],
    normalized_pass_map: dict[str, dict[str, Any]],
    selected_risk_pass_names: set[str],
    resolved_only_pass: str | None,
    only_risky_filters: bool,
    only_degraded: bool,
) -> dict[str, int]:
    """Populate filtered_summary pass-related sections using summary-first data."""
    pass


def _populate_filtered_summary_symbolic_sections(
    *,
    filtered_summary: dict[str, Any],
    summary: dict[str, Any],
    pass_results: dict[str, Any],
    by_pass: dict[str, dict[str, int]],
    degraded_passes: list[dict[str, Any]],
    only_degraded: bool,
    summary_symbolic_issue_map: dict[str, Any],
    summary_symbolic_coverage_map: dict[str, Any],
    summary_symbolic_severity_map: dict[str, Any],
    summary_pass_symbolic_summary: dict[str, Any],
) -> None:
    """Populate symbolic report sections with summary-first fallbacks."""
    pass


def _populate_filtered_summary_discarded_sections(
    *,
    filtered_summary: dict[str, Any],
    summary_discarded_mutation_summary: dict[str, Any],
    summary_discarded_view: dict[str, Any],
    summary_discarded_mutation_priority: list[dict[str, Any]],
) -> None:
    """Populate discarded-mutation sections with summary-first compact/final rows."""
    pass
