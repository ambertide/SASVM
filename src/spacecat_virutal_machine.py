from typing import List, Dict
from typing_extensions import Final


class MemoryAddressException(Exception):
    pass


class InsufficientSpaceException(Exception):
    pass


class _MemorySpace:
    """
    Class representing anything representable as a memory.
    """
    def __init__(self, bit_size: int, size: int, preload_memory: List[int] = []) -> None:
        """
        Initiate a _MemorySpace instance.
        :param bit_size: Size of individual cells.
        :param size: Size of the memory.
        :param preload_memory: Preloaded instructions.
        """
        self._memory_list = [0 for _ in range(size)]
        if preload_memory:
            try:
                assert size >= len(preload_memory)
            except AssertionError:
                raise InsufficientSpaceException("Not enough space in memory with size {size}"
                                                 "to load the instructions which require {len(preload_memory)}"
                                                 "cells of space.")
            for i, instruction in enumerate(preload_memory):
                self._memory_list[i] = instruction
        self.BIT_SIZE: Final[int] = bit_size
        self.SIZE: Final[int] = size

    def retrieve(self, memory_location) -> int:
        """
        Retrieve a value from the memory.
        :param memory_location: Location of the value in the memory.
        :return: The value if the location is valid
        """
        try:
            return self._memory_list[memory_location]
        except IndexError:
            raise MemoryAddressException(f"Address {memory_location} not found in memory with size {self.SIZE}")

    def store(self, memory_location: int, value: int) -> None:
        """
        Store a value inside the memory, overriding the value previously stored.
        :param memory_location: location to write the value.
        :param value: Value to write.
        :return: None.
        """
        self.retrieve(memory_location)
        self._memory_list[memory_location] = value % 2**(self.BIT_SIZE - 1)

    def retrieve_instruction(self, memory_location: int) -> str:
        """
        Retrieve an instruction, this means it returns two cell values.
        :param memory_location: Location at the memory.
        :return: Instruction
        """
        op_code_operation = self.retrieve(memory_location)
        op_code_operands = self.retrieve(memory_location + 1)
        return f"{op_code_operation:X}{op_code_operands:X}"


class SpaceCatVirtualMachine:
    """
    Pythonic representation of the SpaceCat Virtual Machine
    """
    def __init__(self, bit_size: int, machine_size: int, register_size: int, preload_memory: List[int]):
        """
        Initiate a SpaceCatVirtualMachine instance.
        :param bit_size: Size limit of the individual cells of memory and registers
        :param machine_size: Number of cells in the memory.
        :param register_size: Number of cells in the registers.
        :param preload_memory: Instructions to be preloaded into the memory.
        """
        self.BIT_SIZE: Final[int] = bit_size
        self.MEMORY_SIZE: Final[int] = machine_size
        self.REGISTER_SIZE: Final[int] = register_size
        if preload_memory:
            self.memory = _MemorySpace(bit_size=bit_size, size=machine_size, preload_memory=preload_memory)
        else:
            self.memory = _MemorySpace(bit_size=bit_size, size=machine_size)
        self.registers = _MemorySpace(bit_size=bit_size, size=register_size)
        self.instruction_pointer: int = 0
        self.program_counter: str = self.memory.retrieve_instruction(self.instruction_pointer)

    def set_instruction_pointer(self, value: int) -> None:
        """
        Set the instruction pointer to a given value.
        :param value: Value to set.
        :return: None.
        """
        self.instruction_pointer = value % (2**self.BIT_SIZE - 1)

    def increment_instruction_pointer(self) -> None:
        """
        Increment the instruction pointer to the next instruction, traditionally by two cells.
        :return: None.
        """
        self.set_instruction_pointer(self.instruction_pointer + 2)

    def update_program_counter(self) -> None:
        """
        Update the program counter by reading from the instruction pointer.
        :return: None.
        """
        self.program_counter = self.memory.retrieve_instruction(self.instruction_pointer)

    def store(self, register_address: int, memory_address_or_number: int, is_memory_address: bool) -> None:
        """
        Store a value from a memory address or a direct value in a register.
        :param register_address: Register to store the value in.
        :param memory_address_or_number: Memory address to take the value from
        :param is_memory_address: True if second operand is a pointer to a memory address.
        :return: None.
        """
        value_to_store: int
        if is_memory_address:
            value_to_store = self.memory.retrieve(memory_address_or_number)
        else:
            value_to_store = memory_address_or_number
        self.registers.store(register_address, value_to_store)

    def add(self, store_register_address, first_register_address, seconds_register_address) -> None:
        """
        Add values from two registers and store it in a third.
        :param store_register_address: Register address to store the value.
        :param first_register_address: Register address first operand resides in.
        :param seconds_register_address: Register address second operand resides in.
        :return: None
        """
        self.registers.store(store_register_address,
                             self.registers.retrieve(first_register_address) +
                             self.registers.retrieve(seconds_register_address))

    def move(self, memory_address_to_move, register_address_source) -> None:
        """
        Move a value from a register to a cell in memory.
        :param memory_address_to_move: Memory address to store the value.
        :param register_address_source: Register address value is residing in.
        :return: None.
        """
        self.memory.store(memory_address_to_move, self.registers.retrieve(register_address_source))

    def jump(self, instruction_to_jump) -> None:
        """
        Jump to an instruction residing in memory.
        :param instruction_to_jump: Instruction address to jump.
        :return: None.
        """
        self.set_instruction_pointer(instruction_to_jump)
