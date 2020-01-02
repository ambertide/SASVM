# Generated with SpaceCat TestCase Generator.
import unittest
from os import getcwd
from spacecat import assembler, simulator
from spacecat.common_utils import Cell

class AlphabetBenchmark(unittest.TestCase):
    def test_assembler(self):
        with open('data/sample_scripts/benchmark_letters.asm') as file:
            a_ = assembler.Assembler.instantiate(file.read())
            self.assertEqual([Cell("20"),Cell("5A"),Cell("21"),Cell("01"),Cell("22"),Cell("40"),Cell("40"),Cell("2F"),Cell("52"),Cell("21"),Cell("F2"),Cell("06"),Cell("C0"),Cell("00"),], a_.memory)

    def test_simulator(self):
        with open('data/sample_scripts/benchmark_letters.asm') as file:
            a_ = assembler.Assembler.instantiate(file.read())
        s_ = simulator.Simulator(mem_size=126, register_size=16, stdout_register_indices=[15])
        s_.load_memory(a_.memory)
        output = ""
        i = 0
        for _ in s_:
            output += s_.return_stdout()
            i += 1
            if i == 10_000:
                self.fail("Failed to resolve in given CPU Cycles.")
        self.assertEqual('ABCDEFGHIJKLMNOPRSTUVYXWQ', output)

if __name__ == '__main__':
    unittest.main()
