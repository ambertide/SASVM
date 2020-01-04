from typing import List, Tuple, Final
from spacecat.instructions import Instruction, INSTRUCTIONS


def determine_instruction(instruction: str) -> str:
    for instruction_ in INSTRUCTIONS:
        if instruction[0:2] == instruction_.immutable_byte_index or \
           instruction[0:1] == instruction_.immutable_byte_index:
            return instruction_.construct(instruction)
    return ""


def disassemble(instructions: List[str]) -> List[str]:
    instructions = [determine_instruction(instruction) for instruction in instructions]
    return instructions
