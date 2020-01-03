# Generated with SpaceCat TestCase Generator.
import unittest
from spacecat import assembler, simulator
from spacecat.common_utils import Cell

test_code = """load R5, 01010001b
load R4, 1
substract:
	load	R6, 11111111b
	xor	R7, R5, R6
	and	R8, R7, R4
	xor	R5, R5, R4
	move	R4, R8
	addi	R4, R4, R4
	jmpEQ R4 = R0, end
	jmp substract
end:
	move RF, R5
	halt




"""

class AlphabetBenchmark(unittest.TestCase):
    def test_assembler(self):
        a_ = assembler.Assembler.instantiate(test_code, mem_size=24)
        self.assertEqual([Cell("25"),Cell("51"),Cell("24"),Cell("01"),Cell("26"),Cell("FF"),Cell("97"),Cell("56"),Cell("88"),Cell("74"),Cell("95"),Cell("54"),Cell("40"),Cell("84"),Cell("54"),Cell("44"),Cell("B4"),Cell("14"),Cell("B0"),Cell("04"),Cell("40"),Cell("5F"),Cell("C0"),Cell("00"),], a_.memory)

    def test_simulator(self):
        a_ = assembler.Assembler.instantiate(test_code, mem_size=128)
        s_ = simulator.Simulator(mem_size=128, register_size=16, stdout_register_indices=[15])
        s_.load_memory(a_.memory)
        output = ""
        i = 0
        for _ in s_:
            output += s_.return_stdout()
            i += 1
            if i == 10_000:
                self.fail("Failed to resolve in given CPU Cycles.")
        self.assertEqual('P', output)

if __name__ == '__main__':
    unittest.main()
