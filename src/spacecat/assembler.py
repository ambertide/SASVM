from re import sub
from re import compile as regex_compile
from typing import Dict, List
from spacecat.common_utils import Cell


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

    def __parse(self):
        """
        Parse the string.
        :return:
        """
        self.__cleaned_string = self.string.lower()
        self.__cleaned_string = self.__strip_comments_spaces_tabs(self.__cleaned_string)
        self.__cleaned_string = self.__replace_labels(self.__cleaned_string)
        self.__cleaned_string = self.convert_numerals_hexadecimal(self.__cleaned_string)
        lines = self.__cleaned_string.split("\n")
        memory_pointer: int = 0
        instruction = ""
        for line in lines:
            if line == "":
                continue
            mnemonic, operands = "", ""
            if line.startswith("org"):
                org_pointer: str = line.strip("org ")
                memory_pointer = int(org_pointer, base=16)
                continue
            if line == "halt":
                instruction = "C000"
            else:
                mnemonic, operands = line.split(" ", 1)
            if line.startswith("db"):
                operands = operands.split(",")
                for operand in operands:
                    if type(operand) == str:
                        for char in operand:
                            self.memory[memory_pointer].value = ord(char)
                            memory_pointer += 1
                    elif type(operand) == int:
                        self.memory[memory_pointer].value = int(operand, 16)
                        memory_pointer += 1
            elif line.startswith("load"):
                register, operand = operands.split(",")
                if operand.startswith("["):
                    if operand.startswith("[R"):  # Indirect Load
                        register_from = operand
                        instruction = "D0" + register.strip("r") + register_from.strip("[R").strip("]")
                    else:  # Direct load
                        memory_address_pointer = operand
                        instruction = "1" + register.strip("r") + memory_address_pointer.strip("[").strip("]")
                else:  # Immediate Load
                    number = operand
                    instruction = "2" + register.strip("r") + number
            elif line.startswith("store"):
                register, operand = operands.split(",")
                if operand.startswith("[R"): # Indirect Store
                    register_pointer = operand
                    instruction = "E0" + register.strip("r") + register_pointer.strip("[R").strip("]")
                else: # Direct store
                    memory_address_pointer = operand
                    instruction = "3" + register.strip("r") + memory_address_pointer.strip("[").strip("]")
            elif line.startswith("move"):
                register, register_from = operands.split(",")
                instruction = "40" + register_from.strip("r") + register.strip("r")

            elif line.startswith("addi"):
                register, register_one, register_two = operands.split(",")
                instruction = "5" + register.strip("r") + register_one.strip("r") + register_two.strip("r")
            elif line.startswith("addf"):
                register, register_one, register_two = operands.split(",")
                instruction = "6" + register.strip("r") + register_one.strip("r") + register_two.strip("r")
            elif mnemonic in self.three_register_operations: # Arithmatic operations
                instruction = self.three_register_op_codes[mnemonic] + \
                              ''.join(map(lambda r: r.strip("r"), operands.split(",")))
            elif line.startswith("ror"):
                register, number_of_rotations = operands.split(",")
                if int(number_of_rotations) > 15:
                    raise SyntaxError("Can't rotate more than 15 times.")
                instruction = "A" + register.strip("r") + number_of_rotations
            elif line.startswith("jmpeq"):
                register, address = operands.split(",")
                register = register.split("=")[0].strip("r")
                instruction = "B" + register + address
            elif line.startswith("jmple"):
                register, address = operands.split(",")
                register = register.split("<=")[0].strip("r")
                instruction = "F" + register + address
            elif line.startswith("jmp"):
                instruction = "B0" + operands
            if instruction:
                self.memory[memory_pointer].value, self.memory[memory_pointer + 1].value = int(instruction[0:2], base= 16), \
                                                                                           int(instruction[2:4], base=16)
                memory_pointer += 2
                instruction = ""

if __name__ == "__main__":
    with open("ceyda.asm", "r") as file:
        Assembler.instantiate(file.read(), 256)