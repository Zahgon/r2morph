"""
Subregister-aware mutation utilities.

Provides functions for working with register sizes and subregisters
in x86-64, enabling size-aware code transformations.
"""

from typing import Optional, Final
from dataclasses import dataclass


@dataclass
class RegisterInfo:
    name: str
    size_bits: int
    base_register: str
    subregisters: tuple[Optional[str], ...]
    index: int


REG_64: Final[int] = 1
REG_32: Final[int] = 2
REG_16: Final[int] = 4
REG_8H: Final[int] = 8
REG_8L: Final[int] = 16
REG_ALL: Final[int] = REG_64 | REG_32 | REG_16 | REG_8H | REG_8L

REGISTER_MAP: dict[str, tuple[Optional[str], Optional[str], Optional[str], str]] = {
    "rax": (None, "eax", "ax", "al"),
    "rbx": (None, "ebx", "bx", "bl"),
    "rcx": (None, "ecx", "cx", "cl"),
    "rdx": (None, "edx", "dx", "dl"),
    "rsi": (None, "esi", "si", "sil"),
    "rdi": (None, "edi", "di", "dil"),
    "rbp": (None, "ebp", "bp", "bpl"),
    "rsp": (None, "esp", "sp", "spl"),
    "r8": (None, "r8d", "r8w", "r8b"),
    "r9": (None, "r9d", "r9w", "r9b"),
    "r10": (None, "r10d", "r10w", "r10b"),
    "r11": (None, "r11d", "r11w", "r11b"),
    "r12": (None, "r12d", "r12w", "r12b"),
    "r13": (None, "r13d", "r13w", "r13b"),
    "r14": (None, "r14d", "r14w", "r14b"),
    "r15": (None, "r15d", "r15w", "r15b"),
}

HIGH_BYTE_REGS: dict[str, tuple[str, str, str, str]] = {
    "rax": ("rax", "eax", "ax", "ah"),
    "rbx": ("rbx", "ebx", "bx", "bh"),
    "rcx": ("rcx", "ecx", "cx", "ch"),
    "rdx": ("rdx", "edx", "dx", "dh"),
}

PRESERVED_REGS: Final[list[str]] = ["rbx", "rbp", "r12", "r13", "r14", "r15"]
SCRATCH_REGS: Final[list[str]] = ["rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11"]


_register_info_cache: dict[str, RegisterInfo] = {}
_size_to_regs: dict[int, list[str]] = {64: [], 32: [], 16: [], 8: []}
_base_to_index: dict[str, int] = {}


def _init_caches() -> None:
    global _register_info_cache, _size_to_regs, _base_to_index

    if _register_info_cache:
        return

    for idx, (base, subregs) in enumerate(REGISTER_MAP.items()):
        _base_to_index[base] = idx

        size_64 = base
        size_32 = subregs[0]
        size_16 = subregs[1]
        size_8 = subregs[2] if len(subregs) > 2 else None

        _size_to_regs[64].append(size_64)
        if size_32:
            _size_to_regs[32].append(size_32)
        if size_16:
            _size_to_regs[16].append(size_16)
        if size_8:
            _size_to_regs[8].append(size_8)

        _register_info_cache[size_64] = RegisterInfo(
            name=size_64,
            size_bits=64,
            base_register=base,
            subregisters=subregs,
            index=idx,
        )

        if size_32:
            _register_info_cache[size_32] = RegisterInfo(
                name=size_32,
                size_bits=32,
                base_register=base,
                subregisters=subregs,
                index=idx,
            )

        if size_16:
            _register_info_cache[size_16] = RegisterInfo(
                name=size_16,
                size_bits=16,
                base_register=base,
                subregisters=subregs,
                index=idx,
            )

        if size_8:
            _register_info_cache[size_8] = RegisterInfo(
                name=size_8,
                size_bits=8,
                base_register=base,
                subregisters=subregs,
                index=idx,
            )

    for base, subregs in HIGH_BYTE_REGS.items():
        if len(subregs) > 3 and subregs[3]:
            _register_info_cache[subregs[3]] = RegisterInfo(
                name=subregs[3],
                size_bits=8,
                base_register=base,
                subregisters=subregs[:3],
                index=_base_to_index.get(base, 0),
            )


_init_caches()






























_size_to_refs = _size_to_regs
