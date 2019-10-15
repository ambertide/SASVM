from typing import List, Dict, Pattern, Tuple
from re import compile


class SVMAssembler:
    """
    Representation of an ASSEMBLER.
    """
    def __init__(self, instructions: List[str]):
        """
        Initialise a SVMAssembler instance
        :param instructions: List of instructions to assemble.
        """
        self._exportable_memory: List[int] = []
        self._intermediate_memory: List[str] = []
        self.instructions = instructions
        self.command_to_op_code: Dict[str, str] = {}
        self.args_regex: Pattern = compile(r"(?<=\s)\w+(?=,)|(?<=,)\w+(?=,)|(?<=,)\w+(?=;)")

    def _trim_instructions(self) -> None:
        """
        Trim the excess spaces themselves and those around punctuations.
        :return: None.
        """
        trim_punctuation: Pattern = compile(r"(?<=,)\s+|\s+(?=,)|\s+(?=;)|\n")
        trim_space: Pattern = compile(r"\s+")
        for i, instruction in enumerate(self.instructions):
            instruction = trim_punctuation.sub("", instruction)
            self.instructions[i] = trim_space.sub(" ", instruction)

    def _convert_to_machine_instruction(self) -> None:
        """
        Convert the keywords to their appropriate machine instructions.
        :return: None.
        """
        for instruction in self.instructions:
            instruction_base: str = instruction.split(" ")[0]
            if instruction_base in self.command_to_op_code:
                op_code: str = self.command_to_op_code[instruction_base]
                args: Tuple[str, ...] = tuple(self.args_regex.findall(instruction))  # type: ignore
                self._intermediate_memory.append(op_code + "".join(args))

    def _convert_to_integer(self) -> None:
        """
        Convert the machine instructions to integers to be stored in memory.
        :return: None.
        """
        self._exportable_memory = [0 for _ in range(len(self._intermediate_memory) * 2)]
        for i, machine_instruction in enumerate(self._intermediate_memory):
            self._exportable_memory[2*i], self._exportable_memory[2*i + 1] = int(machine_instruction[:2], base=16),\
                                                                             int(machine_instruction[2:], base=16)

    def parse(self) -> List[int]:
        """
        Parse all of the instructions and return the memory resulting.
        :return: the memory.
        """
        self._trim_instructions()
        self._convert_to_machine_instruction()
        self._convert_to_integer()
        return self._exportable_memory.copy()
