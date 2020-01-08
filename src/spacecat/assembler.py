from re import sub
from re import compile as regex_compile
from typing import Dict, List, Tuple, Union
from spacecat.common_utils import Cell
from spacecat.instructions import INSTRUCTIONS, MATCH_TO_CONTESTED_INSTRUCTION
from spacecat.preprocessor import preprocess


class Assembler:
    """
    Assembler for the simulator language.
    """

    def __init__(self, string: str, mem_size: int):
        self.memory: List[Cell] = [Cell() for _ in range(mem_size)]
        self.string: str = string
        self.__cleaned_string: str = ""

    @staticmethod
    def instantiate(*args, **kwargs) -> "Assembler":
        assembler_ = Assembler(*args, **kwargs)
        assembler_.__parse()
        return assembler_

    def __raise_exception(self, message):
        pass

    def __clean_string(self) -> None:
        """
        Clean the strings from tabs spaces and standardise it to be parsed.
        :return: None.
        """
        self.__cleaned_string = preprocess(self.string)

    def __generate_contested_instruction(self, mnemonic: str, line: str) -> str:
        """
        Generate a contested instruction which may resolve to multiple bytecode formats.
        :param mnemonic: Mnemonic name
        :param line: Line to translate
        :return: the instruction.
        """
        for match_case, matched in MATCH_TO_CONTESTED_INSTRUCTION:
            if match_case(mnemonic, line):
                return matched.assemble(line)
        else:
            self.__raise_exception(f"{mnemonic} is not a legal mnemonic.")

    def __generate_uncontested_instruction(self, mnemonic, line) -> str:
        """
        Generate an uncontested instruction whose mnemonic bind to only one bytecode.
        :param mnemonic: mnemonic name
        :param line: line to translate
        :return: none.
        """
        for instruction in INSTRUCTIONS:
            if instruction.mnemonic_name == mnemonic:
                return instruction.assemble(line)
        else:
            self.__raise_exception(f"{mnemonic} is not a legal mnemonic.")

    def __generate_instruction(self, line) -> str:
        """
        Generate an instruction
        :param line: Line to generate the instruction from.
        :return: the generated instruction.
        """
        mnemonic = line.split(" ")[0]
        if mnemonic in ["load", "store"]:
            return self.__generate_contested_instruction(mnemonic, line)
        else:
            return self.__generate_uncontested_instruction(mnemonic, line)

    def __insert_instruction_into_memory(self, memory_pointer: int, instruction: str) -> None:
        """
        Write a given instruction into memory.
        :param memory_pointer: Memory pointer's current location.
        :param instruction: Instruction to write to the memory.
        :return: None.
        """
        self.memory[memory_pointer].value, self.memory[memory_pointer + 1].value = int(instruction[0:2], base=16), \
                                                                                   int(instruction[2:4], base=16)

    def __db_write_to_memory(self, memory_pointer: int, operands: List[str]) -> int:
        """
        Write the contents of the db directive to the memory
        :param memory_pointer: current memory pointer
        :param operands: operands to write into memory.
        :return: new memory pointer.
        """
        for operand in operands:
            for char in operand:
                self.memory[memory_pointer].value = ord(char)
                memory_pointer += 1
        return memory_pointer

    def __consume_directive(self, line: str, memory_pointer: int) -> int:
        """
        Consume the directives by modifying necessary parameters.
        :param line: line with directive
        :param memory_pointer: current memory pointer
        :return: the new memory pointer after directive is consumed.
        """
        if line.startswith("org"):
            org_pointer: str = line.strip("org ")
            return int(org_pointer, base=16)
        else:
            mnemonic, operands = line.split(" ", 1)
            operands = operands.split(",")
            memory_pointer = self.__db_write_to_memory(memory_pointer, operands)
            return memory_pointer

    def __parse(self) -> None:
        """
        Parse the string.
        :return:
        """
        self.__clean_string()
        lines = self.__cleaned_string.split("\n")
        lines = list(filter(lambda line_: line_ != "", lines))
        memory_pointer: int = 0
        for line in lines:
            if line.startswith("org") or line.startswith("db"):
                memory_pointer = self.__consume_directive(line, memory_pointer)
                continue
            instruction = self.__generate_instruction(line)
            self.__insert_instruction_into_memory(memory_pointer, instruction)
            memory_pointer += 2


if __name__ == "__main__":
    with open("../data/sample_scripts/ceyda.asm", "r") as file:
        b = Assembler.instantiate(file.read(), 256)
