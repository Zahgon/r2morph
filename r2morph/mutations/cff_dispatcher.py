"""Dispatcher-code templates extracted from ControlFlowFlatteningPass.

Slice 7 of the CFF clean-arch decomposition: the reference x86/ARM
dispatcher-loop generators (not applied to the binary by apply(); used
for analysis/tests). Pure builders with no pass state. Plain
intra-mutations/ collaborator (no protocol, ValidationManager
precedent); imports nothing from r2morph, so the direct import in
control_flow_flattening.py introduces no cycle.
"""

from __future__ import annotations

from typing import Any


class DispatcherGenerator:
    """Builds reference flattened-dispatcher assembly templates."""

    def generate(self, binary: Any, blocks: list[Any]) -> list[str]:
        """
        Generate dispatcher code (for reference/analysis purposes).

        Note: This generates dispatcher code but doesn't apply it to the binary.
        Full dispatcher-based flattening would require binary expansion which
        is not currently implemented.

        Args:
            binary: Any instance
            blocks: List of basic blocks

        Returns:
            List of assembly instructions
        """
        pass

    @staticmethod
    def generate_x86(blocks: list[Any], bits: int) -> list[str]:
        """
        Generate x86 dispatcher code template.

        Args:
            blocks: Basic blocks
            bits: Bit width

        Returns:
            Assembly instructions
        """
        pass

    @staticmethod
    def generate_arm(blocks: list[Any], bits: int) -> list[str]:
        """
        Generate ARM dispatcher code template.

        Args:
            blocks: Basic blocks
            bits: Bit width

        Returns:
            Assembly instructions
        """
        pass
