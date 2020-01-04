from re import sub
from re import compile as regex_compile
from typing import Dict, List, Tuple
from spacecat.common_utils import Cell
from spacecat.instructions import INSTRUCTIONS, MATCH_TO_CONTESTED_INSTRUCTION


def convert_numeral(string: str) -> str:
    """
    Convert a assembly numeral into a hexadecimal numeral
    :param string: A string representation of a simpSim numeral
    :return: Hexadecimal representation of the numeral
    """
    return_num: int = 0
    is_pointer: bool = string.startswith("[") and string.endswith("]")
    string = string.strip("[").strip("]")
    replacement_dict = {
        'b': 2,
        '0x': 16,
        '$': 16,
        'h': 16,
        '-': 10,
        '': 10
    }
    for identifier in replacement_dict:
        if identifier in string:
            string = string.replace(identifier, '')
            return_num = int(string, base=replacement_dict[identifier])
            break
    if is_pointer:  # If number is a pointer.
        return "[" + format(return_num, "02X") + "]"
    return format(return_num, "02X")


class Assembler:
    """
    Assembler for the simulator language.
    """
    comment_pattern = regex_compile(r";.*")
    org_pattern = regex_compile(r"(?<=org )\w+")
    string_pattern = regex_compile(r"\"\w+\"|'\w+'")
    three_register_operations = ["addi", "addf", "or", "xor", "and"]
    three_register_op_codes = {"addi":"5", "addf":"6", "or":"7", "and":"8", "xor":"9"}

    def __init__(self, string: str, mem_size: int):
        self.memory: List[Cell] = [Cell() for _ in range(mem_size)]
        self.string: str = string
        self.__cleaned_string: str = ""

    @staticmethod
    def instantiate(*args, **kwargs) -> "Assembler":
        assembler_ = Assembler(*args, **kwargs)
        assembler_.__parse()
        return assembler_

    @staticmethod
    def __is_label(string: str) -> bool:
        """
        Return if a given string is a label declaration.
        :param string:
        :return:
        """
        return string.endswith(":")

    @staticmethod
    def __return_label_name(string: str) -> str:
        """
        Return the name of label from a label statement
        :param string:
        :return:
        """
        return string.replace(":", "")

    @staticmethod
    def __org_compile(string: str) -> str:
        """
        Return the memory address from an org statement
        :param string: ex: org 16
        :return: Memory address in hex, if there is no address, return ""
        """
        if match := Assembler.org_pattern.findall(string):
            number_hex: str = convert_numeral(match[0])
            return number_hex
        else:
            return ""

    @staticmethod
    def convert_numerals_hexadecimal(string: str) -> str:
        """
        Convert all decimal, binary and hexadecimals numbers to hexadecimal numbers for easy conversion.
        :param string: String to decode
        :return: The converted string.
        """
        converted_string = ""
        for line in string.split("\n"):
            if " " not in line:
                converted_string += line + "\n"
                continue
            mnemonic, operands = line.split(" ")
            operands = operands.split(',')
            for i, operand in enumerate(operands):
                try:
                    operands[i] = convert_numeral(operand)
                except ValueError:
                    continue
            converted_string += ' '.join((mnemonic, ','.join(operands))) + "\n"
        return converted_string

    @staticmethod
    def __strip_comments_spaces_tabs(string: str) -> str:
        """
        Strip assembly comments and spaces as well as tabs from a string
        :param string:
        :return:
        """
        string_substiuted: str = ""
        for line in string.split("\n"):
            if line == "":
                continue
            else:
                substitute: str = sub(Assembler.comment_pattern, "", line)
                substitute = substitute.strip()
                substitute = substitute.replace("\t", "RESERVED_TAB_CHAR", 1)
                substitute = substitute.replace("\t", "")
                substitute = substitute.replace("RESERVED_TAB_CHAR", " ")
                substitute = substitute.replace(" ", "RESERVED_SPACE_CHAR", 1)
                substitute = substitute.replace(" ", "")
                substitute = substitute.replace("RESERVED_SPACE_CHAR", " ")
                string_substiuted += substitute + "\n"
        return string_substiuted

    @staticmethod
    def __replace_labels(string: str) -> str:
        """
        Delete label declarations and replace label references with explicit declarations.
        :param string:
        :return:
        """
        labels_memory_loc: Dict[str, int] = {}
        label_filtered: str = ""
        last_label_name = ""
        memory_address: int = 0
        for line in string.split("\n"):
            if Assembler.__is_label(line):
                labels_memory_loc[Assembler.__return_label_name(line)] = 0
                last_label_name = Assembler.__return_label_name(line)
            elif last_label_name: # If before came a label definition
                address_str: str = Assembler.__org_compile(line) # Suceeding ORG definition is the mem. add. of label.
                address: int = int(address_str, base=16) if address_str != "" else memory_address # Otherwise it is just the next
                labels_memory_loc[last_label_name] = address
                last_label_name = ''  # Last label name is released so to go on evaluating.
                memory_address = address + 1  # Why does this even work, I have no idea whatsoever?
            else:
                # Any other command other than a label def or org statement is a mnemonic and will increment memory.
                memory_address += 2
        # By this point, we know what labels go into what memory address.
        for line in string.split("\n"):
            if Assembler.__is_label(line):
                continue
            for label in labels_memory_loc:
                if label in Assembler.string_pattern.sub('', line):
                    line = line.replace(label, str(labels_memory_loc[label]))
            label_filtered += line + "\n"
        return label_filtered

    def __raise_exception(self, message):
        pass

    def __clean_string(self) -> None:
        """
        Clean the strings from tabs spaces and standardise it to be parsed.
        :return: None.
        """
        self.__cleaned_string = self.string.lower()
        self.__cleaned_string = self.__strip_comments_spaces_tabs(self.__cleaned_string)
        self.__cleaned_string = self.__replace_labels(self.__cleaned_string)
        self.__cleaned_string = self.convert_numerals_hexadecimal(self.__cleaned_string)

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

    def __parse(self):
        """
        Parse the string.
        :return:
        """
        self.__clean_string()
        lines = self.__cleaned_string.split("\n")
        lines = list(filter(lambda line_: line_ != "", lines))
        memory_pointer: int = 0
        instruction = ""
        for line in lines:
            if line.startswith("org") or line.startswith("db"):
                memory_pointer = self.__consume_directive(line, memory_pointer)
                continue
            instruction = self.__generate_instruction(line)
            if instruction:
                self.__insert_instruction_into_memory(memory_pointer, instruction)
                memory_pointer += 2
                instruction = ""

if __name__ == "__main__":
    with open("../data/sample_scripts/ceyda.asm", "r") as file:
        Assembler.instantiate(file.read(), 256)
