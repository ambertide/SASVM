from spacecat.common_utils import Cell
from spacecat.simulator import Simulator
from time import time

bench = """
LOAD R0, 5Ah; Load the end of the capital English ASCII block.
LOAD R1, 1; Load the increment register.
LOAD R2, 90h; Load the start of the capital English ASCII block.
LOOP:
    MOVE RF, R2; Move the value at R2 to the STDOUT register.
    ADDI R2, R2, R1; Increment
    JMPLE R2<=R0, loop
    HALT
"""

benchmark = "207E21012220402F5221F206C000"
if __name__ == "__main__":
    memory = [Cell(benchmark[i:i+2]) for i in range(0, len(benchmark), 2)]
    start_time = time()
    s = Simulator(mem_size=14, register_size=16, stdout_register_indices=[15])
    s.load_memory(memory)
    for i in s:
        print(s.return_stdout(), end='')
        pass
    print("\n")
    end_time= time()
    print(end_time - start_time)