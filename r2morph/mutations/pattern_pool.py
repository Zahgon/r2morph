"""
Pattern Pool Registry for instruction pattern matching and mutation.

Provides a system for matching instruction patterns and generating
equivalent replacement code with weighted probabilities.
"""

import random
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class Instruction:
    """Pattern-style Instruction class for pattern matching."""

    address: int = 0
    mnemonic: str = ""
    operand_1: str = ""
    operand_2: str = ""
    operand_3: str = ""
    operand_str: str = ""
    bytes: str = ""
    type: str = ""
    opcode: str = ""
    mutated: bool = False


@dataclass
class BasicBlock:
    """Pattern-style BasicBlock for pattern matching."""

    address: int = 0
    label: str = ""
    instructions: list[Instruction] = field(default_factory=list)
    jump: int | None = None
    fail: int | None = None


@dataclass
class MatchResult:
    index: int
    length: int
    operands: list[Any] = field(default_factory=list)


MatchRule = Callable[[list[Instruction]], list[MatchResult]]
Generator = Callable[[list[Any], str], list[Instruction]]


class MutationPatternPool:
    """
    Detects specific instruction patterns and replaces them with
    semantically equivalent alternatives.

    Each pattern pool contains:
    - match_rules: Functions that detect specific patterns
    - generators: Functions that produce replacement code (with weights)
    - mutation_probability: Chance to apply mutation (0-100%)
    """

    def __init__(
        self,
        name: str,
        match_rules: list[MatchRule],
        generators: list[tuple[Generator, int]],
        mutation_probability: int = 100,
    ):
        self.name = name
        self.match_rules = match_rules
        self.generators = generators
        self.mutation_probability = mutation_probability

    def match(self, block: BasicBlock, os_type: str = "linux", verbose: bool = False) -> BasicBlock:
        for rule in self.match_rules:
            matches = rule(block.instructions)

            for match in reversed(matches):
                if random.randint(0, 100) <= self.mutation_probability:
                    block = self._mutate(block, match.index, match.length, match.operands, os_type, verbose)

        return block

    def _mutate(
        self,
        block: BasicBlock,
        ins_idx: int,
        n_match_ins: int,
        operands: list[Any],
        os_type: str,
        verbose: bool,
    ) -> BasicBlock:
        generators_list, weights = zip(*self.generators)
        selected_generator = random.choices(generators_list, weights=weights, k=1)[0]

        new_instructions = selected_generator(operands, os_type)

        if verbose:
            self._print_mutation(
                block.instructions[ins_idx].address if ins_idx < len(block.instructions) else 0,
                block.instructions[ins_idx : ins_idx + n_match_ins],
                new_instructions,
            )

        block.instructions[ins_idx : ins_idx + n_match_ins] = new_instructions

        return block

    def _print_mutation(
        self,
        mutation_addr: int,
        old_instructions: list[Instruction],
        new_instructions: list[Instruction],
    ) -> None:
        old_opcodes = [ins.mnemonic if hasattr(ins, "mnemonic") else str(ins) for ins in old_instructions]
        new_opcodes = []

        for ins in new_instructions:
            if hasattr(ins, "mnemonic") and hasattr(ins, "operand_str"):
                new_opcodes.append([f"{ins.mnemonic} {ins.operand_str}"])
            elif hasattr(ins, "bytes"):
                hex_bytes = ins.bytes if isinstance(ins.bytes, str) else ins.bytes.hex()
                new_opcodes.append([hex_bytes[i : i + 35] for i in range(0, len(hex_bytes), 35)])
            else:
                new_opcodes.append([str(ins)])

        print(f"[v] mutation at {hex(mutation_addr)}:")
        print(f"{'old':<35} | {'new':<35}")
        print("-" * 75)

        max_len = max(len(old_opcodes), len(new_opcodes))
        for i in range(max_len):
            old = old_opcodes[i] if i < len(old_opcodes) else ""
            new = new_opcodes[i] if i < len(new_opcodes) else [""]
            if i == 0 and old == "":
                old = "[insertion]"
            print(f"{old:<35} | {new[0]:<35}")
            for line in new[1:]:
                print(f"{'':<35} | {line:<35}")


_pattern_pool_registry: list[MutationPatternPool] = []


def register_pattern_pool(pool: MutationPatternPool) -> None:
    _pattern_pool_registry.append(pool)


def get_pattern_pools() -> list[MutationPatternPool]:
    return _pattern_pool_registry.copy()


def clear_pattern_pools() -> None:
    _pattern_pool_registry.clear()






def match_mov_reg_0_all(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "mov":
            continue

        op1 = getattr(ins, "operand_1", "")
        op2 = getattr(ins, "operand_2", "")

        if not isinstance(op1, str) or not isinstance(op2, str):
            continue

        if not REG_SIZES_MAP.get(op1.lower() if op1 else "", 0):
            continue

        if op2 != "0":
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1]))

    return matches


def match_xor_reg_reg_all(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "xor":
            continue

        op1 = getattr(ins, "operand_1", "")
        op2 = getattr(ins, "operand_2", "")

        if not isinstance(op1, str) or not isinstance(op2, str):
            continue

        if not REG_SIZES_MAP.get(op1.lower() if op1 else "", 0):
            continue

        if op1.lower() != op2.lower():
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1]))

    return matches










def _create_instruction(mnemonic: str, operands: list[str], ins_type: str = "") -> Instruction:
    ins = Instruction(
        address=0,
        mnemonic=mnemonic,
        operand_1=operands[0] if len(operands) > 0 else "",
        operand_2=operands[1] if len(operands) > 1 else "",
        operand_3=operands[2] if len(operands) > 2 else "",
        operand_str=", ".join(operands),
        bytes="",
        type=ins_type if ins_type else mnemonic,
        opcode=f"{mnemonic} {', '.join(operands)}".rstrip(),
        mutated=True,
    )
    return ins


def match_and_reg_0_all(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "and":
            continue

        op1 = getattr(ins, "operand_1", "")
        op2 = getattr(ins, "operand_2", "")

        if not isinstance(op1, str) or not isinstance(op2, str):
            continue

        if not REG_SIZES_MAP.get(op1.lower() if op1 else "", 0):
            continue

        if op2 != "0":
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1]))

    return matches




def match_inc_reg(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP, REG_64, REG_32

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "inc":
            continue

        op1 = getattr(ins, "operand_1", "")

        if not isinstance(op1, str):
            continue

        reg_size = REG_SIZES_MAP.get(op1.lower() if op1 else "", 0)
        if not (reg_size & (REG_64 | REG_32)):
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1]))

    return matches


def match_dec_reg(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP, REG_64, REG_32

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "dec":
            continue

        op1 = getattr(ins, "operand_1", "")

        if not isinstance(op1, str):
            continue

        reg_size = REG_SIZES_MAP.get(op1.lower() if op1 else "", 0)
        if not (reg_size & (REG_64 | REG_32)):
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1]))

    return matches


def match_shl_reg_imm(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP, REG_64, REG_32

    matches = []
    shift_values = {"1", "2", "4", "8"}

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic not in ("shl", "sal"):
            continue

        op1 = getattr(ins, "operand_1", "")
        op2 = getattr(ins, "operand_2", "")

        if not isinstance(op1, str) or not isinstance(op2, str):
            continue

        reg_size = REG_SIZES_MAP.get(op1.lower() if op1 else "", 0)
        if not (reg_size & (REG_64 | REG_32)):
            continue

        op2_clean = op2.strip().lower().lstrip("0x")
        if op2_clean not in shift_values and op2 not in shift_values:
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1, op2]))

    return matches




def match_add_reg_imm_small(instructions: list[Instruction]) -> list[MatchResult]:
    from r2morph.analysis.register_tracker import REG_SIZES_MAP

    matches = []

    for idx in range(len(instructions) - 1):
        ins = instructions[idx]
        next_ins = instructions[idx + 1]

        if not hasattr(ins, "mnemonic") or ins.mnemonic != "add":
            continue

        op1 = getattr(ins, "operand_1", "")
        op2 = getattr(ins, "operand_2", "")

        if not isinstance(op1, str) or not isinstance(op2, str):
            continue

        if not REG_SIZES_MAP.get(op1.lower() if op1 else "", 0):
            continue

        try:
            imm_val = int(op2, 0) if op2.startswith("0x") else int(op2)
            if not (1 <= imm_val <= 8):
                continue
        except ValueError:
            continue

        if hasattr(next_ins, "type") and next_ins.type == "cjmp":
            continue

        matches.append(MatchResult(index=idx, length=1, operands=[op1, op2]))

    return matches




























and_reg_0_pool = MutationPatternPool(
    name="and_reg_0",
    match_rules=[match_and_reg_0_all],
    generators=[
        (generator_and_reg_0, 5),
        (generator_sub_reg_same, 5),
    ],
    mutation_probability=100,
)
register_pattern_pool(and_reg_0_pool)

inc_reg_pool = MutationPatternPool(
    name="inc_reg",
    match_rules=[match_inc_reg],
    generators=[
        (generator_inc_to_add, 5),
        (generator_add_to_lea, 2),
    ],
    mutation_probability=80,
)
register_pattern_pool(inc_reg_pool)

dec_reg_pool = MutationPatternPool(
    name="dec_reg",
    match_rules=[match_dec_reg],
    generators=[
        (generator_dec_to_sub, 5),
        (generator_dec_chain, 5),
    ],
    mutation_probability=80,
)
register_pattern_pool(dec_reg_pool)

shl_reg_pool = MutationPatternPool(
    name="shl_reg",
    match_rules=[match_shl_reg_imm],
    generators=[
        (generator_shl_to_lea, 3),
    ],
    mutation_probability=60,
)
register_pattern_pool(shl_reg_pool)

add_small_pool = MutationPatternPool(
    name="add_small",
    match_rules=[match_add_reg_imm_small],
    generators=[
        (generator_add_to_lea, 3),
        (generator_add_inc_chain, 2),
    ],
    mutation_probability=70,
)
register_pattern_pool(add_small_pool)

sub_small_pool = MutationPatternPool(
    name="sub_small",
    match_rules=[match_sub_reg_imm_small],
    generators=[
        (generator_dec_chain, 2),
    ],
    mutation_probability=70,
)
register_pattern_pool(sub_small_pool)

lea_off_pool = MutationPatternPool(
    name="lea_off",
    match_rules=[match_lea_reg_off],
    generators=[
        (generator_mov_reg_reg, 1),
    ],
    mutation_probability=50,
)
register_pattern_pool(lea_off_pool)

junk_enhanced_pool = MutationPatternPool(
    name="junk_enhanced",
    match_rules=[match_mov_reg_0_all, match_xor_reg_reg_all],
    generators=[
        (generator_xor_with_junk, 3),
        (generator_mov_with_junk_before, 3),
        (generator_mov_reg_0, 10),
        (generator_xor_reg_reg, 10),
    ],
    mutation_probability=30,
)
register_pattern_pool(junk_enhanced_pool)


mov_reg_value_pool = MutationPatternPool(
    name="mov_reg_value",
    match_rules=[match_mov_reg_reg_reg64_reg16, match_push_pop_reg64_reg16],
    generators=[
        (generator_mov_reg_reg, 1),
        (generator_push_pop_reg, 1),
    ],
    mutation_probability=100,
)
register_pattern_pool(mov_reg_value_pool)

set_reg_to_0_pool = MutationPatternPool(
    name="set_reg_to_0",
    match_rules=[match_mov_reg_0_all, match_xor_reg_reg_all],
    generators=[
        (generator_mov_reg_0, 10),
        (generator_xor_reg_reg, 10),
    ],
    mutation_probability=100,
)
register_pattern_pool(set_reg_to_0_pool)
