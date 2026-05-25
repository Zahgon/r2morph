"""
Hot path detection for performance-aware mutations.
"""

import logging

from r2morph.core.binary import Binary

logger = logging.getLogger(__name__)


class HotPathDetector:
    """
    Detects hot execution paths in binaries.

    Uses heuristics when profiling data unavailable:
    - Functions called frequently
    - Loop headers
    - Error handling paths (cold)
    """

    def __init__(self, binary: Binary):
        """
        Initialize hot path detector.

        Args:
            binary: Binary instance
        """
        self.binary = binary

    def detect_hot_paths(self) -> dict[str, list[int]]:
        """
        Detect likely hot paths using static analysis.

        Returns:
            Dict of function -> hot basic block addresses
        """
        pass

    def _identify_hot_blocks(self, basic_blocks: list[dict]) -> list[int]:
        """
        Identify hot basic blocks heuristically.

        Args:
            basic_blocks: List of basic block dicts

        Returns:
            List of hot block addresses
        """
        pass

    def is_hot_path(self, func_name: str, block_addr: int, hot_paths: dict[str, list[int]]) -> bool:
        """
        Check if a block is on a hot path.

        Args:
            func_name: Function name
            block_addr: Block address
            hot_paths: Hot paths dict

        Returns:
            True if hot
        """
        pass
