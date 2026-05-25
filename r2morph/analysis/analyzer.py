"""
Binary analyzer for extracting information and finding mutation candidates.
"""

import logging
from typing import Any

from r2morph.core.binary import Binary
from r2morph.core.constants import MINIMUM_FUNCTION_SIZE, SMALL_FUNCTION_THRESHOLD
from r2morph.core.function import Function
from r2morph.core.instruction import Instruction

logger = logging.getLogger(__name__)


class BinaryAnalyzer:
    """
    Analyzer for extracting detailed information from binaries.

    Provides high-level analysis functions for identifying mutation
    candidates, extracting control flow graphs, and gathering statistics.

    Attributes:
        binary: Binary instance being analyzed
    """

    def __init__(self, binary: Binary):
        """
        Initialize the analyzer.

        Args:
            binary: Binary instance to analyze
        """
        self.binary = binary

    def get_functions_list(self) -> list[Function]:
        """
        Get list of Function objects from the binary.

        Returns:
            List of Function instances
        """
        functions_data = self.binary.get_functions()
        functions = []

        for func_data in functions_data:
            func = Function.from_r2_dict(func_data)

            try:
                func.instructions = self.binary.get_function_disasm(func.address)
                func.basic_blocks = self.binary.get_basic_blocks(func.address)
            except Exception as e:
                logger.debug(f"Failed to enrich function {func.name}: {e}")

            functions.append(func)

        return functions

    def get_instructions_for_function(self, address: int) -> list[Instruction]:
        """
        Get list of Instruction objects for a function.

        Args:
            address: Function address

        Returns:
            List of Instruction instances
        """
        instructions_data = self.binary.get_function_disasm(address)
        return [Instruction.from_r2_dict(insn) for insn in instructions_data]

    def find_nop_insertion_candidates(self) -> list[dict[str, Any]]:
        """
        Find safe locations for NOP insertion.

        Returns:
            List of candidate locations with metadata
        """
        pass

    def find_substitution_candidates(self) -> list[dict[str, Any]]:
        """
        Find instructions that can be substituted with equivalents.

        Returns:
            List of candidate instructions with metadata
        """
        pass

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics about the binary.

        Returns:
            Dictionary with binary statistics
        """
        functions = self.get_functions_list()
        arch_info = self.binary.get_arch_info()

        total_instructions = 0
        total_blocks = 0
        total_size = 0

        for func in functions:
            instructions = self.get_instructions_for_function(func.address)
            total_instructions += len(instructions)
            total_blocks += len(func.basic_blocks)
            total_size += func.size

        return {
            "architecture": arch_info,
            "total_functions": len(functions),
            "total_instructions": total_instructions,
            "total_basic_blocks": total_blocks,
            "total_code_size": total_size,
            "avg_function_size": total_size / len(functions) if functions else 0,
            "avg_instructions_per_function": (total_instructions / len(functions) if functions else 0),
        }

    def identify_hot_functions(self, min_size: int = SMALL_FUNCTION_THRESHOLD) -> list[Function]:
        """
        Identify functions suitable for mutation (not too small, not library code).

        Args:
            min_size: Minimum function size in bytes

        Returns:
            List of candidate functions for mutation
        """
        pass
