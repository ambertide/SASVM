from re import compile
from typing import List
from spacecat_virutal_machine import SpaceCatVirtualMachine
from preprocessor import Preprocessor
from memory_creator import SVMAssembler


class OctonekoAssembler(SVMAssembler):
    def __init__(self, instructions: List[str]):
        SVMAssembler.__init__(self, instructions)
        self.command_to_op_code = {
            "ADDI": "10",
            "ADDF": "20",
            "STOR": "3",
            "STOV": "9",
            "MOVE": "4",
            "HALT": "0000",
            "JUMP": "50",
            "JMPGT": "6"
        }


class Octoneko(SpaceCatVirtualMachine):
    def __init__(self, preload_memory = None):
        SpaceCatVirtualMachine.__init__(self, 8, 128, 20, preload_memory)
        self.can_continue: bool = True
        self.internalParser.instruction_to_method = {
            compile(r"10\w{2}"): self.addi,
            compile(r"3\w{3}"): self.store,
            compile(r"4\w{3}"): self.move,
            compile(r"50\w{2}"): self.jump,
            compile(r"6\w{3}"): self.jmp_greater_than,
            compile(r"0000"): self.halt,
            compile(r"9\w{3}"):self.stov
        }
        self.internalParser.instruction_to_argument_map = {
            compile(r"10\w{2}"): (compile(r"(?<=10)\w"), compile(r"(?<=10\w)\w")),
            compile(r"3\w{3}"): (compile(r"(?<=3)\w"), compile(r"(?<=3\w)\w{2}")),
            compile(r"9\w{3}"): (compile(r"(?<=9)\w"), compile(r"(?<=9\w)\w{2}")),
            compile(r"4\w{3}"): (compile(r"(?<=4)\w{2}"), compile(r"(?<=4\w{2})\w")),
            compile(r"50\w{2}"): (compile(r"(?<=50)\w{2}"), ),
            compile(r"6\w{3}"): (compile(r"(?<=6)\w{2}"), compile(r"(?<=6\w{2})\w")),
            compile(r"0000"): tuple()
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

    def stov(self, register_one, value_one):
        self.store(register_one, value_one, False)



if __name__ == "__main__":
    prep = Preprocessor("test.neko", ";")
    assembler = OctonekoAssembler(prep.data)
    svm = Octoneko(preload_memory=assembler.parse())
    while svm.can_continue:
        svm.do_continue()