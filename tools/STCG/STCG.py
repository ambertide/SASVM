import csv
from sys import argv

def generate_memory_list_view(expected_memory) -> str:
    """
    Convert expected memory's bytestring to a list of Cells (in string)
    :param expected_memory: "A00023"
    :return: [Cell("A0"), Cell("00"), Cell("23")]
    """
    list_view = "["
    for i in range(0, len(expected_memory), 2):
        list_view += f"Cell(\"{expected_memory[i] + expected_memory[i + 1]}\","
    list_view += "]"
    return list_view


def generate_test_case(file_name: str, expected_memory: str, expected_output: str) -> str:
    """
    Generate a test case string to test an *.asm file.
    :param file_name: *.asm file to test
    :param expected_memory: Expected memory as bytestring
    :param expected_output: Expected output from STDOUT
    :return: String
    """
    expected_memory_list: str = generate_memory_list_view(expected_memory)
    output: str = f"""
import unittest
from spacecat import assembler, simulator
from spacecat.common_utils import Cell

class AlphabetBenchmark(unittest.TestCase):
    def test_assembler(self):
        with open({file_name}) as file:
            a_ = assembler.Assembler.instantiate(file.read())
            self.assertEqual({expected_memory_list}, a_.memory)

    def test_simulator(self):
        with open({file_name}) as file:
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
        self.assertEqual({expected_output}, output)

if __name__ == '__main__':
    unittest.main()
"""
    return output


def generate_test_file(output_directory: str, file_name: str, expected_memory: str, expected_output: str) -> None:
    output_directory += f"/test_{file_name.strip('*.asm')}.py"
    with open(output_directory, "w") as file:
        try:
            file.write(generate_test_case(file_name, expected_memory, expected_output))
        except (IOError, FileNotFoundError):
            print(f"Couldn't generate test case for {file_name}")


def generate_from_config(input_directory: str, config_file: str, output_directory: str) -> None:
    try:
        with open(config_file) as file:
            reader = csv.reader(file, delimiter=",")
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                try:
                    generate_test_file(output_directory, input_directory + "/" + row[0], row[1], row[2])
                except:
                    pass
    except FileNotFoundError:
        print("Config file not found.")
        return


if __name__ == "__main__":
    print("Generating...")
    relative_import_directory = argv[1]
    config_file = argv[2]
    output_directory = argv[3]
    generate_from_config(relative_import_directory, config_file, output_directory)