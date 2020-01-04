from dataclasses import dataclass
from typing import Final, List, Tuple
from string import hexdigits


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

    def get_var_byte_length(self, index) -> int:
        var_stop = self.variable_indexes[index][0]
        var_start = self.variable_indexes[index][1]
        return var_stop - var_start

    def assemble(self, line: str) -> str:
        mnemonic, *variable_bloc = line.split(" ", 1)
        if mnemonic == "halt":
            return "C000"
        variables = [variable.replace(self.variable_prefixes[i], "").replace(self.variable_suffixes[i], "") for i, variable in enumerate(variable_bloc[0].split(","))]
        if mnemonic == "ror":
            variables.insert(1, "0")
        if mnemonic == "move":
            variables.reverse()
        ins = (self.immutable_byte_index + ''.join(variables)).replace(" ", "").replace("<=r0", "").replace("=r0", "").replace("<=R0", "").replace("=R0", "")
        return ''.join(filter(lambda char: char in hexdigits, ins))


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
                                            Instruction("B", "jmpeq", [(1, 2), (2, 4)], ["R", ""], ["=R0", "h"]),
                                            Instruction("C0", "halt", [], [], []),
                                            Instruction("D0", "load", [(2, 3), (3, 4)], ["R", "R["], ["", "]"]),
                                            Instruction("E0", "store", [(2, 3), (3, 4)], ["R", "R["], ["", "]"]),
                                            Instruction("F", "jmple", [(1, 2), (2, 4)], ["R", ""], ["<=R0", "h"])]


MATCH_TO_CONTESTED_INSTRUCTION = [
    (lambda mnemonic, line: mnemonic == "load" and "[" in line and "r[" not in line, INSTRUCTIONS[0]),
    (lambda mnemonic, line: mnemonic == "load" and "[" not in line, INSTRUCTIONS[1]),
    (lambda mnemonic, line: mnemonic == "store" and "[" in line and "r[" not in line, INSTRUCTIONS[2]),
    (lambda mnemonic, line: mnemonic == "store" and "r[" in line, INSTRUCTIONS[14]),
    (lambda mnemonic, line: mnemonic == "load" and "r[" in line, INSTRUCTIONS[13])
]