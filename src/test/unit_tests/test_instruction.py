from unittest import TestCase
from spacecat.instructions import INSTRUCTIONS, Instruction

class TestInstruction(TestCase):
    def test_value_load_assemble(self):
        instruction = "load R1, [20h]"
        expected = "1120"
        self.assertEqual(expected, INSTRUCTIONS[0].assemble(instruction))

    def test_value_load_disassemble(self):
        instruction = "1120"
        expected = "load R1, [20h]; 1120"
        self.assertEqual(expected, INSTRUCTIONS[0].construct(instruction))

    def test_pointer_load_assemble(self):
        instruction = "load R2, 20h"
        expected = "2220"
        self.assertEqual(expected, INSTRUCTIONS[1].assemble(instruction))

    def test_pointer_store_assemble(self):
        instruction = "store R3, [20h]"
        expected = "3320"
        self.assertEqual(expected, INSTRUCTIONS[2].assemble(instruction))

    def test_move_assemble(self):
        instruction = "move R1, R2"
        expected = "4021"
        self.assertEqual(expected, INSTRUCTIONS[3].assemble(instruction))

    def test_addi_assemble(self):
        instruction = "addi R1, R1, R2"
        expected = "5112"
        self.assertEqual(expected, INSTRUCTIONS[4].assemble(instruction))

    def test_addf_assemble(self):
        instruction = "addf R1, R1, R2"
        expected = "6112"
        self.assertEqual(expected, INSTRUCTIONS[5].assemble(instruction))

    def test_or_assemble(self):
        instruction = "or R1, R2, R3"
        expected = "7123"
        self.assertEqual(expected, INSTRUCTIONS[6].assemble(instruction))

    def test_and_assemble(self):
        instruction = "and R1, R2, R3"
        expected = "8123"
        self.assertEqual(expected, INSTRUCTIONS[7].assemble(instruction))

    def test_xor_assemble(self):
        instruction = "xor R1, R1, R2"
        expected = "9112"
        self.assertEqual(expected, INSTRUCTIONS[8].assemble(instruction))

    def test_ror_assemble(self):
        instruction = "ror R4, 4"
        expected = "A404"
        self.assertEqual(expected, INSTRUCTIONS[9].assemble(instruction))

    def test_jmp_assemble(self):
        instruction = "jmp 20h"
        expected = "B020"
        self.assertEqual(expected, INSTRUCTIONS[10].assemble(instruction))

    def test_jmpeq_assemble(self):
        instruction = "jmpeq r1=r0, 20h"
        expected = "B120"
        self.assertEqual(expected, INSTRUCTIONS[11].assemble(instruction))

    def test_halt_assemble(self):
        instruction = "halt"
        expected = "C000"
        self.assertEqual(expected, INSTRUCTIONS[12].assemble(instruction))

    def test_register_load_assemble(self):
        instruction = "load R1, R[2]"
        expected = "D012"
        self.assertEqual(expected, INSTRUCTIONS[13].assemble(instruction))

    def test_register_store_assemble(self):
        instruction = "store R1, R[2]"
        expected = "E012"
        self.assertEqual(expected, INSTRUCTIONS[14].assemble(instruction))

    def test_jmple_assemble(self):
        instruction = "jmple r1<=r0, 20h"
        expected = "F120"
        self.assertEqual(expected, INSTRUCTIONS[15].assemble(instruction))