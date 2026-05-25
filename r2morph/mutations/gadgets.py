"""
Gadgets library for semantic-neutral code generation.

Provides categorized gadgets (instruction sequences) for generating
junk code that preserves program semantics.
"""

import random
from typing import Callable
from dataclasses import dataclass

from r2morph.analysis.register_tracker import (
    RegTracker,
    REG_64,
    REG_32,
    REG_16,
    REG_ALL,
)
from r2morph.analysis.os_flags import OSFlags


@dataclass
class GadgetCategory:
    name: str
    gadgets: dict[str, tuple[Callable, int, int]]
    description: str


class Gadgets:
    def __init__(self, os_type: str = "linux"):
        self.os_flags = OSFlags(os_type)
        self.reg_tracker = RegTracker()
        self._stack_depth: int = 0
        self._cnt_reg: str = ""
        self._in_loop: bool = False
        self._label_counter: int = 0
        self._os_type = os_type
        self.stack_gadgets: dict[str, tuple[Callable, Callable, int]] = {}
        self.jump_gadgets: dict[str, tuple[Callable, int]] = {}
        self.operate_gadgets: dict[str, tuple[Callable, int, int]] = {}
        self.branch_gadgets: dict[str, tuple[Callable, int, int]] = {}
        self.loop_gadgets: dict[str, tuple[Callable, int, int]] = {}
        self._ensure_initialized()







    def _init_stack_gadgets(self) -> None:
        self.stack_gadgets = {
            "push_reg": (
                lambda reg: f"push {reg}",
                lambda reg: f"pop {reg}",
                1,
            ),
            "sub_mov": (
                lambda reg: f"sub rsp, 8; mov [rsp], {reg}",
                lambda reg: f"mov {reg}, [rsp]; add rsp, 8",
                1,
            ),
        }

    def _init_jump_gadgets(self) -> None:
        self.jump_gadgets = {
            "jz": (lambda lbl: f"jz {lbl}", 1),
            "jnz": (lambda lbl: f"jnz {lbl}", 1),
            "jg": (lambda lbl: f"jg {lbl}", 1),
            "jge": (lambda lbl: f"jge {lbl}", 1),
            "jl": (lambda lbl: f"jl {lbl}", 1),
            "jle": (lambda lbl: f"jle {lbl}", 1),
            "ja": (lambda lbl: f"ja {lbl}", 1),
            "jae": (lambda lbl: f"jae {lbl}", 1),
            "jb": (lambda lbl: f"jb {lbl}", 1),
            "jbe": (lambda lbl: f"jbe {lbl}", 1),
        }

    def _init_operate_gadgets(self) -> None:
        self.operate_gadgets = {
            **self._mov_gadgets(),
            **self._arithmetic_gadgets(),
            **self._lea_gadgets(),
            **self._bitwise_gadgets(),
        }

    def _mov_gadgets(self) -> dict[str, tuple]:
        """MOV-family gadgets: register-register, register-memory, register-immediate."""
        return {
            "mov_reg_reg": (
                lambda reg, sec_reg: f"mov {reg}, {sec_reg}",
                REG_ALL,
                30,
            ),
            "mov_reg_rsp": (
                lambda reg, sec_reg: f"mov {reg}, rsp",
                REG_64,
                30,
            ),
            "mov_reg_mem_rsp": (
                lambda reg, sec_reg: f"mov {reg}, [rsp + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_ALL,
                30,
            ),
            "mov_reg_imm32": (
                lambda reg, sec_reg: f"mov {reg}, {random.randint(0, 0xFFFFFFFF)}",
                REG_64 | REG_32,
                5,
            ),
            "mov_reg_imm16": (
                lambda reg, sec_reg: f"mov {reg}, {random.randint(0, 0xFFFF)}",
                REG_64 | REG_32 | REG_16,
                15,
            ),
            "mov_reg_imm8": (
                lambda reg, sec_reg: f"mov {reg}, {random.randint(0, 0xFF)}",
                REG_ALL,
                20,
            ),
        }

    def _arithmetic_gadgets(self) -> dict[str, tuple]:
        """ADD/SUB/INC/DEC gadgets."""
        return {
            "add_reg_reg": (
                lambda reg, sec_reg: f"add {reg}, {sec_reg}",
                REG_ALL,
                5,
            ),
            "add_reg_mem": (
                lambda reg, sec_reg: f"add {reg}, [rsp + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_ALL,
                10,
            ),
            "add_reg_imm": (
                lambda reg, sec_reg: f"add {reg}, {random.randint(-0x80000000, 0x7FFFFFFF)}",
                REG_ALL,
                5,
            ),
            "sub_reg_reg": (
                lambda reg, sec_reg: f"sub {reg}, {sec_reg}",
                REG_ALL,
                5,
            ),
            "sub_reg_mem": (
                lambda reg, sec_reg: f"sub {reg}, [rsp + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_ALL,
                10,
            ),
            "sub_reg_imm": (
                lambda reg, sec_reg: f"sub {reg}, {random.randint(-0x80000000, 0x7FFFFFFF)}",
                REG_ALL,
                5,
            ),
            "inc_reg": (
                lambda reg, sec_reg: f"inc {reg}",
                REG_ALL,
                5,
            ),
            "dec_reg": (
                lambda reg, sec_reg: f"dec {reg}",
                REG_ALL,
                5,
            ),
        }

    def _lea_gadgets(self) -> dict[str, tuple]:
        """LEA-family gadgets: address calculation variants."""
        return {
            "lea_reg_mem": (
                lambda reg, sec_reg: f"lea {reg}, [{sec_reg}]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_rsp": (
                lambda reg, sec_reg: f"lea {reg}, [rsp + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_rbp": (
                lambda reg, sec_reg: f"lea {reg}, [rbp - {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_reg_sum": (
                lambda reg, sec_reg: f"lea {reg}, [{reg} + {sec_reg}]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_rsp_reg": (
                lambda reg, sec_reg: f"lea {reg}, [rsp + {reg} + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_64,
                5,
            ),
            "lea_reg_rsp_secreg": (
                lambda reg, sec_reg: f"lea {reg}, [rsp + {sec_reg} + {random.randint(0, max(0, self._stack_depth - 1)) * 8}]",
                REG_64,
                5,
            ),
            "lea_reg_plus_8": (
                lambda reg, sec_reg: f"lea {reg}, [{reg} + 8]",
                REG_64 | REG_32,
                5,
            ),
            "lea_secreg_plus_8": (
                lambda reg, sec_reg: f"lea {reg}, [{sec_reg} + 8]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_reg_imm": (
                lambda reg, sec_reg: f"lea {reg}, [{sec_reg} + {random.randrange(2, 0x101, 2)}]",
                REG_64 | REG_32,
                5,
            ),
            "lea_reg_reg_mul2": (
                lambda reg, sec_reg: f"lea {reg}, [{reg} + {reg}*2]",
                REG_64 | REG_32,
                10,
            ),
            "lea_secreg_secreg_mul2": (
                lambda reg, sec_reg: f"lea {reg}, [{sec_reg} + {sec_reg}*2]",
                REG_64 | REG_32,
                10,
            ),
            "lea_reg_secreg_mul4": (
                lambda reg, sec_reg: f"lea {reg}, [{reg} + {sec_reg}*4]",
                REG_64 | REG_32,
                5,
            ),
        }

    def _bitwise_gadgets(self) -> dict[str, tuple]:
        """XOR/AND/OR/ROL/SAR/SHR/SHL and NOP gadgets."""
        return {
            "nop": (
                lambda reg, sec_reg: "nop",
                REG_ALL,
                1,
            ),
            "xor_reg_reg": (
                lambda reg, sec_reg: f"xor {reg}, {reg}",
                REG_ALL,
                5,
            ),
            "xor_reg_sec": (
                lambda reg, sec_reg: f"xor {reg}, {sec_reg}",
                REG_ALL,
                5,
            ),
            "xor_reg_imm": (
                lambda reg, sec_reg: f"xor {reg}, {self.os_flags.get_safe_imm32()}",
                REG_ALL,
                5,
            ),
            "and_reg_0": (
                lambda reg, sec_reg: f"and {reg}, 0",
                REG_ALL,
                5,
            ),
            "and_reg_sec": (
                lambda reg, sec_reg: f"and {reg}, {sec_reg}",
                REG_ALL,
                5,
            ),
            "and_reg_imm": (
                lambda reg, sec_reg: f"and {reg}, {self.os_flags.get_safe_imm32()}",
                REG_ALL,
                5,
            ),
            "or_reg_0xff": (
                lambda reg, sec_reg: f"or {reg}, 0xFFFFFFFFFFFFFFFF",
                REG_ALL,
                5,
            ),
            "or_reg_sec": (
                lambda reg, sec_reg: f"or {reg}, {sec_reg}",
                REG_ALL,
                5,
            ),
            "or_reg_imm": (
                lambda reg, sec_reg: f"or {reg}, {self.os_flags.get_safe_imm32()}",
                REG_ALL,
                5,
            ),
            "rol_reg_1": (lambda reg, sec_reg: f"rol {reg}, 1", REG_ALL, 3),
            "rol_reg_2": (lambda reg, sec_reg: f"rol {reg}, 2", REG_ALL, 3),
            "rol_reg_4": (lambda reg, sec_reg: f"rol {reg}, 4", REG_ALL, 3),
            "rol_reg_8": (lambda reg, sec_reg: f"rol {reg}, 8", REG_64 | REG_32 | REG_16, 3),
            "sar_reg_1": (lambda reg, sec_reg: f"sar {reg}, 1", REG_ALL, 3),
            "sar_reg_2": (lambda reg, sec_reg: f"sar {reg}, 2", REG_ALL, 3),
            "sar_reg_4": (lambda reg, sec_reg: f"sar {reg}, 4", REG_ALL, 3),
            "sar_reg_8": (lambda reg, sec_reg: f"sar {reg}, 8", REG_64 | REG_32 | REG_16, 3),
            "shr_reg_1": (lambda reg, sec_reg: f"shr {reg}, 1", REG_ALL, 5),
            "shr_reg_2": (lambda reg, sec_reg: f"shr {reg}, 2", REG_ALL, 5),
            "shr_reg_4": (lambda reg, sec_reg: f"shr {reg}, 4", REG_ALL, 5),
            "shr_reg_8": (lambda reg, sec_reg: f"shr {reg}, 8", REG_64 | REG_32 | REG_16, 5),
            "shl_reg_1": (lambda reg, sec_reg: f"shl {reg}, 1", REG_ALL, 5),
            "shl_reg_2": (lambda reg, sec_reg: f"shl {reg}, 2", REG_ALL, 5),
            "shl_reg_4": (lambda reg, sec_reg: f"shl {reg}, 4", REG_ALL, 5),
            "shl_reg_8": (lambda reg, sec_reg: f"shl {reg}, 8", REG_64 | REG_32 | REG_16, 5),
        }

    def _init_branch_gadgets(self) -> None:
        self.branch_gadgets = {
            "check_alignment": (
                self._br_check_alignment,
                REG_ALL,
                10,
            ),
            "check_and_set_0": (
                self._br_check_and_set_0,
                REG_ALL,
                10,
            ),
            "check_regs": (
                self._br_check_regs,
                REG_ALL,
                10,
            ),
            "check_flags": (
                self._br_check_flags,
                REG_ALL,
                10,
            ),
        }

    def _init_loop_gadgets(self) -> None:
        self.loop_gadgets = {
            "loop_to_0": (
                self._lo_to_0,
                REG_ALL,
                10,
            ),
        }






    def _ensure_initialized(self) -> None:
        """Initialize gadget tables if not yet done."""
        pass


def create_gadgets(os_type: str = "linux") -> Gadgets:
    gadgets = Gadgets(os_type)
    gadgets._init_stack_gadgets()
    gadgets._init_jump_gadgets()
    gadgets._init_operate_gadgets()
    gadgets._init_branch_gadgets()
    gadgets._init_loop_gadgets()
    return gadgets
