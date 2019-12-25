from typing import List, Dict, Callable
from spacecat.common_utils import Cell, right_rotation, OctalFloat

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
        """
        Load the memory from a given list of Cells.
        :param memory: Memory to load.
        :return:
        """
        self.__memory = memory

    def parse_program_memory(self, bytes_list: bytes):
        """
        Parse the memory of a *.prg file.
        :param bytes_list:
        :return:
        """
        actual_bytes = [bytes_list[4*i] for i in range(len(bytes_list)//4)]
        empty_mem = [Cell() for _ in range(self.mem_size)]
        for i, byte in enumerate(actual_bytes):
            empty_mem[i].value = byte
        self.load_memory(empty_mem)

    def dump_program_memory(self) -> bytes:
        """
        Dump the program memory as in a *.pkg format.
        :return: the dumped memory as bytes.
        """
        byte_ready: List[int] = []
        for cell in self.__memory:
            byte_ready.append(cell.value)
            for i in range(3):
                byte_ready.append(0)
        bytes_obj = bytes(byte_ready)
        return bytes_obj

    def return_memory(self) -> List[Cell]:
        """
        Return memory.
        :return: the memory.
        """
        return self.__memory

    def return_registers(self) -> List[Cell]:
        """
        Return the registers
        :return: the registers.
        """
        return self.__registers

    def reset_special_registers(self) -> None:
        """
        Reset the special registers
        :return: None
        """
        self.PC = 0
        self.IR = "0000"