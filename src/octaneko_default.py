from typing import Dict
from spacecat_virutal_machine import SpaceCatVirtualMachine


class Octoneko(SpaceCatVirtualMachine):
    def __init__(self, preload_memory = None):
        SpaceCatVirtualMachine.__init__(self, 8, 128, 20, preload_memory)
        self.can_continue: bool = True
        self.internalParser.instruction_to_method = {
            r"10\w{2}":self.addi,
            r"3\w{3}":self.store,
            r"4\w{3}":self.move,
            r"50\w{2}"self.jump,
            r"6\w{3}":self.jmp_greater_than,
            r"0000":self.halt
        }
        self.internalParser.instruction_to_argument_map = {
            r"10\w{2}": (r"(?<=10)\w", r"(?<=10\w)\w"),
            r"3\w{3}": (r"(?<=3)\w", r"(?<=10\w)\w{2}"),
            r"4\w{3}": (r"(?<=4)\w{2}", r"(?<=4\w{2})\w"),
            r"50\w{2}": (r"(?<=50)\w{2}", )
            r"6\w{3}": (r"(?<=6)\w{2}", r"(?<=6\w{2})\w"),
            r"0000": tuple()
        }

    def addi(self, register_one: int, register_two: int) -> None:
        self.add(register_one, register_one, register_two)

    def halt(self):
        self.can_continue = False

    def jmp_greater_than(self, memory_one, register_one):
        if self.registers.retrieve_instruction(register_one) > 0:
            self.jump(memory_one)

    def take_turn(self):
        if self.can_continue:
            self.do_continue()

if __name__ == "__main__":
    svm = Octoneko()
    while svm.can_continue:
        svm.do_continue()