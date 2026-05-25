"""
SARIF 2.1.0 formatter for r2morph mutation reports.

Converts mutation and validation results to SARIF format for CI/CD integration
with tools like GitHub Security, Azure DevOps, and SonarQube.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from r2morph.reporting.sarif_schema import (
    SARIFArtifact,
    SARIFArtifactLocation,
    SARIFCodeFlow,
    SARIFFix,
    SARIFFileChange,
    SARIFInvocation,
    SARIFLevel,
    SARIFLocation,
    SARIFLogicalLocation,
    SARIFMessage,
    SARIFPhysicalLocation,
    SARIFRegion,
    SARIFReplacement,
    SARIFReport,
    SARIFResult,
    SARIFRule,
    SARIFRun,
    SARIFSnippet,
    SARIFTaxon,
    SARIFTaxonomy,
    SARIFTaxonReference,
    SARIFThreadFlow,
    SARIFThreadFlowLocation,
    SARIFTool,
    SARIFToolComponent,
)


@dataclass
class MutationResult:
    address: int
    original_bytes: bytes
    mutated_bytes: bytes
    pass_name: str
    description: str | None = None
    function: str | None = None
    section: str | None = None
    disassembly: str | None = None


@dataclass
class ValidationResult:
    passed: bool
    address: int | None = None
    message: str | None = None
    validation_type: str = "structural"
    severity: str = "warning"
    details: dict[str, Any] | None = None


@dataclass
class ReportData:
    binary_path: str
    output_path: str | None = None
    mutations: list[MutationResult] | None = None
    validations: list[ValidationResult] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    exit_code: int = 0


MUTATION_RULES: list[dict[str, Any]] = [
    {
        "id": "RM001",
        "name": "nop-insertion",
        "short_description": "NOP instruction insertion",
        "full_description": "Inserts benign NOP instructions at safe locations",
        "default_level": "note",
    },
    {
        "id": "RM002",
        "name": "instruction-substitution",
        "short_description": "Instruction substitution",
        "full_description": "Replaces instructions with semantically equivalent alternatives",
        "default_level": "note",
    },
    {
        "id": "RM003",
        "name": "register-substitution",
        "short_description": "Register substitution",
        "full_description": "Substitutes registers while preserving program semantics",
        "default_level": "note",
    },
    {
        "id": "RM004",
        "name": "block-reordering",
        "short_description": "Basic block reordering",
        "full_description": "Reorders basic blocks to change code layout",
        "default_level": "warning",
    },
    {
        "id": "RM005",
        "name": "dead-code-injection",
        "short_description": "Dead code injection",
        "full_description": "Injects dead code sequences that execute but have no effect",
        "default_level": "warning",
    },
    {
        "id": "RM006",
        "name": "opaque-predicates",
        "short_description": "Opaque predicate insertion",
        "full_description": "Inserts conditional branches with known outcomes",
        "default_level": "warning",
    },
    {
        "id": "RM007",
        "name": "instruction-expansion",
        "short_description": "Instruction expansion",
        "full_description": "Expands instructions into longer equivalent sequences",
        "default_level": "note",
    },
    {
        "id": "RM008",
        "name": "control-flow-flattening",
        "short_description": "Control flow flattening",
        "full_description": "Flattens control flow to obscure program structure",
        "default_level": "warning",
    },
]

VALIDATION_RULES: list[dict[str, Any]] = [
    {
        "id": "RV001",
        "name": "structural-validation",
        "short_description": "Structural validation failure",
        "full_description": "Binary structure validation detected an issue",
        "default_level": "error",
    },
    {
        "id": "RV002",
        "name": "runtime-validation",
        "short_description": "Runtime validation failure",
        "full_description": "Runtime behavior validation detected a mismatch",
        "default_level": "error",
    },
    {
        "id": "RV003",
        "name": "semantic-validation",
        "short_description": "Semantic validation failure",
        "full_description": "Semantic equivalence validation failed",
        "default_level": "error",
    },
    {
        "id": "RV004",
        "name": "cfg-integrity",
        "short_description": "CFG integrity violation",
        "full_description": "Control flow graph integrity check failed",
        "default_level": "error",
    },
]

MITRE_ATTACK: dict[str, dict[str, str]] = {
    "nop": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "nop-insertion": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "substitute": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "instruction-substitution": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "register": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "register-substitution": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "block": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "block-reordering": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "dead-code": {"id": "T1027.001", "name": "Binary Padding"},
    "dead-code-injection": {"id": "T1027.001", "name": "Binary Padding"},
    "opaque": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "opaque-predicates": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "expand": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "instruction-expansion": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "cff": {"id": "T1027.002", "name": "Software Packing"},
    "control-flow-flattening": {"id": "T1027.002", "name": "Software Packing"},
}


class SARIFFormatter:
    def __init__(
        self,
        tool_version: str = "0.2.0",
        information_uri: str = "https://github.com/anomalyco/r2morph",
    ) -> None:
        self.tool_version = tool_version
        self.information_uri = information_uri
        self._mutation_rules = self._build_rules(MUTATION_RULES)
        self._validation_rules = self._build_rules(VALIDATION_RULES)














    def to_json(self, report_data: ReportData) -> str:
        report = self.format(report_data)
        return report.to_json()



def format_as_sarif(
    mutations: list[dict[str, Any]],
    validations: list[dict[str, Any]],
    binary_path: str,
    output_path: str | None = None,
    tool_version: str = "0.2.0",
) -> SARIFReport:
    formatter = SARIFFormatter(tool_version=tool_version)

    mutation_results = [
        MutationResult(
            address=m.get("address", 0),
            original_bytes=m.get("original_bytes", b""),
            mutated_bytes=m.get("mutated_bytes", b""),
            pass_name=m.get("pass_name", "unknown"),
            description=m.get("description"),
            function=m.get("function"),
            section=m.get("section"),
            disassembly=m.get("disassembly") or m.get("original_disasm"),
        )
        for m in mutations
    ]

    validation_results = [
        ValidationResult(
            passed=v.get("passed", True),
            address=v.get("address"),
            message=v.get("message"),
            validation_type=v.get("validation_type", "structural"),
            severity=v.get("severity", "warning"),
            details=v.get("details"),
        )
        for v in validations
    ]

    report_data = ReportData(
        binary_path=binary_path,
        output_path=output_path,
        mutations=mutation_results,
        validations=validation_results,
    )
    return formatter.format(report_data)
