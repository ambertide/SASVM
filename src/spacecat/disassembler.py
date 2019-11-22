from typing import List, Tuple, Final
from dataclasses import dataclass


@dataclass
class Instruction:
    immutable_byte_index: str
    mnemonic_name: str
    variable_indexes: List[Tuple[int, int]]
    variable_prefixes: List[str]
    variable_suffixes: List[str]

    def construct(self, instruction: str) -> str:
        variables = [instruction[i:j] for i, j in self.variable_indexes]
        variables_form = [self.variable_prefixes[i] + variable + self.variable_suffixes[i]
                          for i, variable in enumerate(variables)]
        variable_part = ', '.join(variables_form)
        command = self.mnemonic_name + " " + variable_part + "; " + instruction
        return command


THREE_REGISTER_ARITHMATIC = [[(1, 2), (2, 3), (3, 4)], ["R", "R", "R"], ["", "", ""]]


INSTRUCTIONS: Final[List['Instruction']] = [Instruction("1", "load", [(1, 2), (2, 4)], ["R", "["], ["", "h]"]),
                                            Instruction("2", "load", [(1, 2), (2, 4)], ["R", ""], ["", "h"]),
                                            Instruction("3", "store", [(1, 2), (2, 4)], ["R", "["], ["", "h]"]),
                                            Instruction("40", "move", [(2, 3), (3, 4)], ["R", "R"], ["", ""]),
                                            Instruction("5", "addi", *THREE_REGISTER_ARITHMATIC),
                                            Instruction("6", "addf", *THREE_REGISTER_ARITHMATIC),
                                            Instruction("7", "or", *THREE_REGISTER_ARITHMATIC),
                                            Instruction("8", "and", *THREE_REGISTER_ARITHMATIC),
                                            Instruction("9", "xor", *THREE_REGISTER_ARITHMATIC),
                                            Instruction("A", "ror", [(1, 2), (3, 4)], ["R", ""], ["", ""]),
                                            Instruction("B0", "jmp", [(2, 4)], [""], ["h"]),
                                            Instruction("B", "jmpEQ", [(1, 2), (2, 4)], ["R", ""], ["=R0", "h"]),
                                            Instruction("C0", "halt", [], [], []),
                                            Instruction("D0", "load", [(2, 3), (3, 4)], ["R", "R["], ["", "]"]),
                                            Instruction("E0", "store", [(2, 3), (3, 4)], ["R", "R["], ["", "]"]),
                                            Instruction("F", "jmpLE", [(1, 2), (2, 4)], ["R", ""], ["<=R0", "h"])]


def determine_instruction(instruction: str) -> str:
    for instruction_ in INSTRUCTIONS:
        if instruction[0:2] == instruction_.immutable_byte_index or \
           instruction[0:1] == instruction_.immutable_byte_index:
            return instruction_.construct(instruction)
    return ""


def disassemble(instructions: List[str]) -> List[str]:
    instructions = [determine_instruction(instruction) for instruction in instructions]
    return instructions
