from typing import List, Dict, Union, Callable
from re import sub
from re import compile as regex_compile
from os import system


def clear_screen():
    system("cls")

def right_shift(x: str, y: int) -> str:
    """
    Right shift x by a factor of y
    :param x: Bit-pattern to shift
    :param y: Shifting factor
    :return: Shifted bit-pattern
    """
    bit_length = len(x)
    new_bit = ""
    for i in range(bit_length - y):
        new_bit += "0"
    for i in range(y):
        new_bit += x[i]
    return new_bit


def right_rotation(x: str, y: int) -> str:
    """
    Rotate x right by a factor of y
    :param x: Bitstring to rotate.
    :param y: Rotation factor.
    :return: Rotated bit.
    """
    new_bit = ""
    for i in range(y, len(x)):
        new_bit += x[i]
    for i in range(y):
        new_bit += x[i]
    return new_bit


class OctalFloat:
    """
    Implementation of 8-Bit Semi-IEEE 754 compliant Floating Point Numerals
    """
    __bias: int = 8

    def __init__(self, hex_rep: str):
        binary_representation = format(int(hex_rep, base=16), "08b")
        self.__binary_representation = binary_representation
        self.__sign: int = (-1) ** int(binary_representation[0], base=2)
        self.__exponent = int(binary_representation[1:4], base=2) - self.__bias
        self.__mantissa = int(binary_representation[4:], base=2)

    def __float__(self) -> float:
        """
        Convert the number into float.
        :return:
        """
        return self.__sign * (self.__mantissa**self.__exponent)

    def __add__(self, other: "OctalFloat") -> "OctalFloat":
        """
        Add to OctalFloat's together
        :param other: Other OctoFloat to add
        :return: Sum of two OctoFloats, possibly overflown.
        """
        exponent_difference: int = other.__exponent - self.__exponent
        if exponent_difference >= 0:
            operated_mantissa = right_shift(format(self.__mantissa, "04b"), exponent_difference)
            operated = self
            operand = other
        else:
            operated_mantissa = right_shift(format(other.__mantissa, "04b"), abs(exponent_difference))
            operated = other
            operand = self
        number_whole: int = int(operated_mantissa, base=2) * operated.__sign + operand.__mantissa * operand.__sign
        new_sign = "0" if number_whole >= 0 else "1"
        new_mantissa = format(abs(number_whole), "04b")[:4]
        new_exponent = format(operand.__sign + self.__bias, "03b")
        return OctalFloat(new_sign + new_exponent + new_mantissa)

    def __str__(self) -> str:
        """
        Convert to string.
        :return:
        """
        return format(int(self.__binary_representation, base=2), "02X")

    def __int__(self) -> int:
        """
        Convert to integer
        :return:
        """
        return int(self.__binary_representation, base=2)

    def __repr__(self) -> str:
        """
        String representation for printing and debugging.
        :return:
        """
        return self.__binary_representation


class Cell:
    """
    A memory cell.
    """
    def __init__(self):
        """
        Initialise a memory cell.
        """
        self.__value: int = 0

    @property
    def binary_value(self):
        """
        :return: Binary value of the value.
        """
        return format(self.__value, "08b")

    @property
    def value(self):
        """
        Get the value of the cell
        :return: Integer value of the cell.
        """
        return self.__value

    @value.setter
    def value(self, value: Union[str, int]):
        """
        Set the value of the cell, probably overflown.
        :param value: New value to set
        :return: None
        """
        if type(value) == str:
            value = int(value, base=16)
        self.__value = value % 256

    def __repr__(self) -> str:
        return format(self.__value, "02X")


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
    def __convert_numeral(string: str) -> str:
        """
        Convert a assembly numeral into a hexadecimal numeral
        :param string:
        :return:
        """
        return_num: int = 0
        pointer_flag: bool = False
        if string.startswith("[") and string.endswith("]"):
            string = string.strip("[").strip("]")
            pointer_flag = True
        if string.endswith('b'):
            return_num = int(string.replace('b', ''), base=2)
        elif string.startswith(s := '0x') or string.startswith(s :='$') or string.endswith(s := 'h'):
            return_num = int(string.replace(s, ''), base=16)
        elif string.startswith('-'):
            return_num = int(string.replace('-', ''))
        elif string.isnumeric():
            return_num =  int(string)
        else:
            raise SyntaxError(f'{string} is not a number.')
        if pointer_flag:
            return "[" + format(return_num, "02X") + "]"
        return format(return_num, "02X")

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
        :return: Memory address in hex, if there is no adress, return ""
        """
        if match := Assembler.org_pattern.findall(string):
            number_hex: str = Assembler.__convert_numeral(match[0])
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
                    operands[i] = Assembler.__convert_numeral(operand)
                except SyntaxError:
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
                continue
            elif last_label_name: # If before came a label definition
                address_str: str = Assembler.__org_compile(line) # Suceeding ORG definition is the mem. add. of label.
                address = int(address_str, base=16) if address_str != "" else memory_address # Otherwise it is just the next
                labels_memory_loc[last_label_name] = address
                last_label_name = '' # Last label name is released so to go on evaluating.
                if type(address) == str:
                    memory_address = address
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
        self.__cleaned_string = self.__strip_comments_spaces_tabs(self.string)
        self.__cleaned_string = self.__replace_labels(self.__cleaned_string)
        lines = self.__cleaned_string.split("\n")
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
                        instruction = "D0" + register.strip("R") + register_from.strip("[R").strip("]")
                    else:  # Direct load
                        memory_address_pointer = operand
                        instruction = "1" + register.strip("R") + memory_address_pointer.strip("[").strip("]")
                else:  # Immediate Load
                    number = operand
                    instruction = "2" + register.strip("R") + number
            elif line.startswith("store"):
                register, operand = operands.split(",")
                if operand.startswith("[R"): # Indirect Store
                    register_pointer = operand
                    instruction = "E0" + register.strip("R") + register_pointer.strip("[R").strip("]")
                else: # Direct store
                    memory_address_pointer = operand
                    instruction = "3" + register.strip("R") + memory_address_pointer.strip("[").strip("]")
            elif line.startswith("move"):
                register, register_from = operands.split(",")
                instruction = "40" + register.strip("R") + register_from.strip("R")

            elif line.startswith("addi"):
                register, register_one, register_two = operands.split(",")
                instruction = "5" + register.strip("R") + register_one.strip("R") + register_two.strip("R")
            elif line.startswith("addf"):
                register, register_one, register_two = operands.split(",")
                instruction = "6" + register.strip("R") + register_one.strip("R") + register_two.strip("R")
            elif mnemonic in self.three_register_operations: # Arithmatic operations
                instruction = self.three_register_op_codes[mnemonic] + \
                              ''.join(map(lambda r : r.strip("R"), operands.split(",")))
            elif line.startswith("ror"):
                register, number_of_rotations = operands.split(",")
                if int(number_of_rotations) > 15:
                    raise SyntaxError("Can't rotate more than 15 times.")
                instruction = "A" + register.strip("R") + number_of_rotations
            elif line.startswith("jmpEQ"):
                register, address = operands.split(",")
                register = register.split("=")[0].strip("R")
                instruction = "B" + register + address
            elif line.startswith("jmpLE"):
                register, address = operands.split(",")
                register = register.split("<=")[0].strip("R")
                instruction = "F" + register + address
            elif line.startswith("jmp"):
                instruction = "B0" + operands
            if instruction:
                self.memory[memory_pointer].value, self.memory[memory_pointer + 1].value = int(instruction[0:2], base= 16), \
                                                                                           int(instruction[2:4], base=16)
                memory_pointer += 2
                instruction = ""


class Simulator:
    """
    Simulator for the simulator.
    """
    def __init__(self, mem_size: int, register_size: int):
        """
        Initialise the simulator
        :param mem_size: Size of the memory
        :param register_size: Size of the registers
        """
        self.__memory = [Cell() for _ in range(mem_size)]
        self.mem_size = mem_size
        self.__registers = [Cell() for _ in range(register_size)]
        self.IR: str = "0000"  # Current instruction under execution.
        self.PC: int = 0  # Next value index.
        self.__can_continue: bool = True
        self.__op_code_method: Dict[str, Callable] = {
            "1": lambda: self.__direct_load(),
            "2": lambda: self.__immediate_load(),
            "3": lambda: self.__direct_store(),
            "4": lambda: self.__move(),
            "5": lambda: self.__integer_addition(),
            "6": lambda: self.__floating_point_addition(),
            "7": lambda: self.__bitwise_or(),
            "8": lambda: self.__bitwise_and(),
            "9": lambda: self.__bitwise_exclusive_or(),
            "A": lambda: self.__rotate_right(),
            "B": lambda: self.__jump_when_equal(),
            "C": lambda: self.__halt(),
            "D": lambda: self.__indirect_load(),
            "E": lambda: self.__indirect_store(),
            "F": lambda: self.__jump_when_less_or_equal(),
            "0": lambda: self.__invalid
        }
        self.check_reference_register = lambda: self.__registers[0].value
        self.__jmp = False

    def __immediate_load(self):
        register_index = self.IR[1]
        value = self.IR[2:]
        self.__registers[int(register_index, base=16)].value = value

    def __direct_load(self):
        register_index = self.IR[1]
        memory_index = self.IR[2:]
        self.__registers[int(register_index, base=16)].value = self.__memory[int(memory_index, base=16)].value

    def __indirect_load(self):
        register_index = self.IR[2]
        memory_index_register_index = self.IR[3]
        memory_index = self.__registers[int(memory_index_register_index, base=16)].value
        self.__registers[int(register_index, base=16)].value = self.__memory[memory_index].value

    def __direct_store(self):
        register_index = self.IR[1]
        memory_index = self.IR[2:]
        self.__memory[int(memory_index, base=16)].value = self.__registers[int(register_index, base=16)]

    def __indirect_store(self):
        register_index = self.IR[2]
        memory_index_register_index = self.IR[3]
        memory_index = self.__registers[int(memory_index_register_index, base=16)].value
        self.__memory[memory_index].value = self.__registers[int(register_index, base=16)]

    def __move(self):
        register_sender_index: int = int(self.IR[2], base=16)
        register_receiver_index: int = int(self.IR[3], base=16)
        self.__registers[register_receiver_index].value = self.__registers[register_sender_index].value

    def __integer_addition(self):
        register_receiver_index: int = int(self.IR[1], base=16)
        register_operand_one: int = int(self.IR[2], base=16)
        register_operand_two: int = int(self.IR[3], base=16)
        self.__registers[register_receiver_index].value = self.__registers[register_operand_one].value + \
                                                          self.__registers[register_operand_two].value

    def __invalid(self):
        pass

    def __floating_point_addition(self):
        register_receiver_index: int = int(self.IR[1], base=16)
        register_operand_one: int = int(self.IR[2], base=16)
        register_operand_two: int = int(self.IR[3], base=16)
        num_one = OctalFloat(str(self.__registers[register_operand_one]))
        num_two = OctalFloat(str(self.__registers[register_operand_two]))
        result = num_one + num_two
        self.__registers[register_receiver_index].value = int(result)

    def __bitwise_or(self):
        register_receiver_index: int = int(self.IR[1], base=16)
        register_operand_one: int = int(self.IR[2], base=16)
        register_operand_two: int = int(self.IR[3], base=16)
        self.__registers[register_receiver_index].value = self.__registers[register_operand_one].value | \
                                                          self.__registers[register_operand_two].value

    def __bitwise_and(self):
        register_receiver_index: int = int(self.IR[1], base=16)
        register_operand_one: int = int(self.IR[2], base=16)
        register_operand_two: int = int(self.IR[3], base=16)
        self.__registers[register_receiver_index].value = self.__registers[register_operand_one].value & \
                                                          self.__registers[register_operand_two].value

    def __bitwise_exclusive_or(self):
        register_receiver_index: int = int(self.IR[1], base=16)
        register_operand_one: int = int(self.IR[2], base=16)
        register_operand_two: int = int(self.IR[3], base=16)
        self.__registers[register_receiver_index].value = self.__registers[register_operand_one].value ^ \
                                                          self.__registers[register_operand_two].value

    def __rotate_right(self):
        register_to_rotate_index: int = int(self.IR[1], base=16)
        rotate_by: int = int(self.IR[3], base=16)
        self.__registers[register_to_rotate_index].value = int(right_rotation(self.__registers[register_to_rotate_index].binary_value, rotate_by), base=2)

    def __jump_when_equal(self):
        register_to_check_index = int(self.IR[1], base=16)
        jump_to = int(self.IR[2:], base=16)
        self.__jmp = True
        if self.__registers[register_to_check_index] == self.__registers[0]:
            self.PC = jump_to

    def __jump_when_less_or_equal(self):
        register_to_check_index = int(self.IR[1], base=16)
        jump_to = int(self.IR[2:], base=16)
        self.__jmp = True
        if self.__registers[register_to_check_index] <= self.check_reference_register:
            self.PC = jump_to

    def __unconditional_jump(self):
        jump_to = int(self.IR[2:], base=16)
        self.__jmp = True
        self.PC = jump_to

    def __halt(self):
        self.__can_continue = False

    def __execute(self):
        if self.IR[:2] == "B0":
            self.__unconditional_jump()
        else:
            self.__op_code_method[self.IR[0]]()

    def __next__(self):
        if not self.__can_continue:
            raise StopIteration
        if self.PC == 256:
            raise StopIteration
        self.IR = str(self.__memory[self.PC]) + str(self.__memory[self.PC + 1])
        if not self.__jmp:
            self.PC += 2
        else:
            self.__jmp = False
        self.__execute()
        return self.__memory, self.__registers

    def __iter__(self):
        return self

    def load_memory(self, memory: List[Cell]):
        self.__memory = memory

    def parse_program_memory(self, bytes_list: bytes):
        actual_bytes = [bytes_list[4*i] for i in range(len(bytes_list)//4)]
        empty_mem = [Cell() for _ in range(self.mem_size)]
        for i, byte in enumerate(actual_bytes):
            empty_mem[i].value = byte
        self.load_memory(empty_mem)

    def return_memory(self):
        return self.__memory

    def return_registers(self):
        return self.__registers

def mem_print(mem: List[Cell]):
    for i in range(16, 256, 16):
        for j in range(i - 16, i):
            print(str(mem[j]), end=" ")
        print()

if __name__ == "__main__":
    cpu_cycle = 0
#    with open("ceyda.asm") as file:
#        assembler = Assembler.instantiate(file.read(), 256)
    simulator = Simulator(256, 16)
#    simulator.load_memory(assembler.memory)
#    mem_print(assembler.memory)
    with open("example_prog_file.prg", "rb") as file:
        simulator.parse_program_memory(file.read())
    mem_print(simulator.return_memory())
    for memory, registers in simulator:
        cpu_cycle += 1
        continue
    mem_print(simulator.return_memory())
    print(simulator.return_registers())
