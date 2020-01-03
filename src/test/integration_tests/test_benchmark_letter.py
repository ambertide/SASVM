# Generated with SpaceCat TestCase Generator.
import unittest
from spacecat import assembler, simulator
from spacecat.common_utils import Cell

test_code = """load R0, 5Ah; Load the end of the capital English ASCII block.
load R1, 1; Load the increment register.
load R2, 40h; Load the start of the capital English ASCII block.
loop:
    move RF, R2; Move the value at R2 to the STDOUT register.
    addi R2, R2, R1; Increment
    jmpLE R2<=R0, loop
    halt"""

class AlphabetBenchmark(unittest.TestCase):
    def test_assembler(self):
        a_ = assembler.Assembler.instantiate(test_code, mem_size=14)
        self.assertEqual([Cell("20"),Cell("5A"),Cell("21"),Cell("01"),Cell("22"),Cell("40"),Cell("40"),Cell("2F"),Cell("52"),Cell("21"),Cell("F2"),Cell("06"),Cell("C0"),Cell("00"),], a_.memory)

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
        self.assertEqual('@ABCDEFGHIJKLMNOPQRSTUVWXYZ', output)

if __name__ == '__main__':
    unittest.main()
