from re import compile
from spacecat_virutal_machine import SpaceCatVirtualMachine


class Octoneko(SpaceCatVirtualMachine):
    def __init__(self, preload_memory = None):
        SpaceCatVirtualMachine.__init__(self, 8, 128, 20, preload_memory)
        self.can_continue: bool = True
        self.internalParser.instruction_to_method = {
            compile(r"10\w{2}"):self.addi,
            compile(r"3\w{3}"):self.store,
            compile(r"4\w{3}"):self.move,
            compile(r"50\w{2}"):self.jump,
            compile(r"6\w{3}"):self.jmp_greater_than,
            compile(r"0000"):self.halt
        }
        self.internalParser.instruction_to_argument_map = {
            compile(r"10\w{2}"): (compile(r"(?<=10)\w"), compile(r"(?<=10\w)\w")),
            compile(r"3\w{3}"): (compile(r"(?<=3)\w"), compile(r"(?<=10\w)\w{2}")),
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

if __name__ == "__main__":
    svm = Octoneko()
    while svm.can_continue:
        svm.do_continue()