"""
Junk code generator for semantic-preserving mutations.

Generates semantically neutral junk code using Keystone assembler
and the gadgets library.
"""

import random
from typing import Any, Optional
from dataclasses import dataclass

from r2morph.analysis.register_tracker import RegTracker, REG_SIZES_MAP
from r2morph.mutations.gadgets import Gadgets, create_gadgets


@dataclass
class GeneratedCode:
    code: bytes
    size: int
    store_gadget: Optional[bytes] = None
    restore_gadget: Optional[bytes] = None


class JunkGenerator:
    """
    Generates semantically neutral junk code using Keystone assembler.

    Uses gadgets library to produce instruction sequences that preserve
    program semantics while increasing code entropy.
    """

    def __init__(self, os_type: str = "linux"):
        self.os_type = os_type
        self._reg_tracker = RegTracker()
        self._gadgets: Optional[Gadgets] = None
        self._assembler: Any = None
        self._init_assembler()



    def assemble(self, asm: str) -> tuple[bytes, int]:
        if self._assembler is None:
            return b"", 0

        try:
            encoding, count = self._assembler.asm(asm)
            return bytes(encoding), count
        except Exception:
            return b"", 0









    def clear(self) -> None:
        self._reg_tracker.clear()
        if self._gadgets:
            self._gadgets._stack_depth = 0


def create_junk_generator(os_type: str = "linux") -> JunkGenerator:
    return JunkGenerator(os_type)
