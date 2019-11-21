from tkinter import Tk, Label, filedialog, Entry, END, Menu, Event, Button, Frame, RAISED, BOTTOM, TOP, FLAT, messagebox
from typing import List, Dict, TypeVar
from spacecat.simulator import Simulator
from spacecat.common_utils import Cell
from spacecat.assembler import Assembler
from copy import deepcopy
from enum import Enum

T = TypeVar("T")


def get_difference(previous_list: List[T], current_list: List[T]) -> Dict[int, T]:
    """
    Get the difference between two lists.
    :param previous_list: First iteration of the list.
    :param current_list: Second iteration of the list
    :return: The indices and new values of the changed cells of the list as a dictionary.
    """
    diff_dict: Dict[int, T] = {i: new_value for i, new_value in
                               enumerate(current_list) if new_value != previous_list[i]}
    return diff_dict


class TICKS(Enum):
    HIGH: int = 500
    MEDIUM: int = 300
    LOW: int = 100


class SpaceCatSimulator:
    def __init__(self, master: Tk):

        self.master = master
        self.master.resizable(height=False, width=False)
        self.master.geometry("500x500")
        self.master.iconbitmap("data\spacecat.ico")
        self.master.title("SpaceCat Simple Assembly Simulator")

        self.MEMORY_SIZE = 256
        self.REGISTER_SIZE = 16
        self.ROW_SIZE = 16

        self.__machine: Simulator = Simulator(self.MEMORY_SIZE, self.REGISTER_SIZE)
        self.__memory_values: List[Cell] = self.__machine.return_memory()  # Memory from previous turn.
        self.__register_values: List[Cell] = self.__machine.return_registers()  # Registers from previous turn.

        self.memory_canvas = Frame(master)
        self.register_canvas = Frame(master)
        self.buttons_frame = Frame(master, bd= 1, relief=RAISED)
        self.prev_run_cell = 0

        self.cells = [Entry(master=self.memory_canvas, width=3)
                      for _ in range(self.MEMORY_SIZE)]
        for cell in self.cells:
            cell.bind("<Button-1>", self.on_click)

        self.registers = [Entry(master=self.register_canvas, width=3) for _ in range(self.REGISTER_SIZE)]
        for register in self.registers:
            register.bind("<Button-1>", self.on_click)
        self.__populate_canvases()

        self.__run = Button(master=self.buttons_frame, text="Run", relief=FLAT, command=self.__run_machine)
        self.__step_button = Button(master=self.buttons_frame, text="Step", relief=FLAT, command=self.__step)
        self.__editor = Button(master=self.buttons_frame, text="Editor", relief=FLAT)
        self.__disassemble = Button(master=self.buttons_frame, text="Disassemble", relief=FLAT)

        self.__run.grid(row=0, column=0)
        self.__step_button.grid(row=0, column=1)
        self.__editor.grid(row=0, column=2)
        self.__disassemble.grid(row=0, column=3)

        self.menubar = Menu(self.master, relief=RAISED)
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save Machine State", command=lambda: None)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=lambda: quit())
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.master.config(menu=self.menubar)

        self.bottom_bar = Label(self.master, text="Decimal Value: \tHexadecimal Value: "
                                                  "\tFloat Value: \tBinary Value: ", relief=RAISED)

        self.buttons_frame.pack(fill="x", side=TOP)
        self.memory_canvas.pack()
        self.register_canvas.pack()
        self.bottom_bar.pack(fill="x", side=BOTTOM)

    def __run_machine(self):
        self.__step()
        try:
            self.master.after(500, self.__run_machine)
        except StopIteration:
            pass

    def __step(self):
        try:
            memory_cells, register_cells = self.__machine.__next__()
            self.__update_view(memory_cells, register_cells)
        except StopIteration:
            pass


    def open_file(self):
        """
        Open a file to load to the memory.
        :return:
        """
        file_name: str = filedialog.askopenfilename(title="Select file", filetypes=(("Assembly source code", "*.asm"),
                                                                                   ("SimpSim Memory State", "*.prg"),
                                                                                   ("SpaceCat Machine State", "*.svm")))
        if file_name.endswith(".asm"):
            assembler: Assembler = Assembler.instantiate(open(file_name, "r").read(), 256)
            self.__machine.load_memory(assembler.memory)
        elif file_name.endswith(".prg"):
            self.__machine.parse_program_memory(open(file_name, "rb").read())
            self.__reset_ir_pc()
            self.__machine.reset_special_registers()
        self.__update_view(self.__machine.return_memory(), self.__machine.return_registers())

    def on_click(self, event: Event):
        """
        When clicked over an event.
        :param event:
        :return:
        """
        value = event.widget.get()
        real_val = int(value, base=16)
        self.bottom_bar["text"] = f"Decimal Value: {real_val}\tHexadecimal Value:{real_val:02X}\tBinary Value: {real_val:08b}"

    def __populate_canvases(self):
        """
        Populate the canvases by drawing entry fields into them.
        :return:
        """
        for i in range(1, self.ROW_SIZE + 1):
            Label(master=self.memory_canvas, text=f"{i - 1:X}").grid(row=0, column=i)
            Label(master=self.memory_canvas, text=f"{i - 1:X}_").grid(row=i, column=0)
            Label(master=self.register_canvas, text=f"{i - 1:X}").grid(row=0, column=i)
        for i, cell in enumerate(self.cells):
            cell.grid(row=i // self.ROW_SIZE + 1, column=i % self.ROW_SIZE + 1)
        Label(master=self.register_canvas, text="R_").grid(row=1, column=0)
        for i, register in enumerate(self.registers):
            register.grid(row=1, column=i + 1)
        Label(master=self.register_canvas, text="PC: ").grid(row=2, column=4, columnspan=2)
        self.pc = Entry(master=self.register_canvas, width=3)
        self.pc.grid(row=2, column=6)
        Label(master=self.register_canvas, text="IR: ").grid(row=2, column=7, columnspan=2)
        self.ir = Entry(master=self.register_canvas, width=6)
        self.ir.grid(row=2, column=9, columnspan=2)
        Button(master=self.register_canvas, text="∅", command=self.__reset_ir_pc).grid(row=2, column=11)
        self.__load_memory_to_view()

    def __reset_ir_pc(self) -> None:
        """
        Reset the instruction register and the pc
        :return:
        """
        self.__machine.reset_special_registers()
        self.__load_special_registers()

    def __load_memory_to_view(self):
        """
        Load the self.memory to view
        :return:
        """
        for i, memory_value in enumerate(self.__memory_values):
            entry_field = self.cells[i]
            entry_field.delete(0, END)
            entry_field.insert(0, str(memory_value))
        for j, register_value in enumerate(self.__register_values):
            register_field = self.registers[j]
            register_field.delete(0, END)
            register_field.insert(0, register_value)
        self.__load_special_registers()

    def __update_view(self, new_memory: List[Cell], new_registers: List[Cell]):
        """
        Update the view without explicitly reloading the view.
        :param new_memory: New memory to be loaded.
        :param new_registers: New registers to be loaded.
        :return:
        """
        register_differences = get_difference(self.__register_values, new_registers)
        memory_differences = get_difference(self.__memory_values, new_memory)
        self.__memory_values = deepcopy(new_memory)
        self.__register_values = deepcopy(new_registers)
        for change_index, new_value in memory_differences.items():
            self.cells[change_index].delete(0, END)
            self.cells[change_index].insert(0, str(new_value))
        for change_index, new_value in register_differences.items():
            self.registers[change_index].delete(0, END)
            self.registers[change_index].insert(0, str(new_value))
        self.__load_special_registers()
        self.cells[self.__machine.PC]["background"] = "Green"
        self.cells[self.prev_run_cell]["background"] = "White"
        self.prev_run_cell = self.__machine.PC

    def __load_special_registers(self):
        self.pc.delete(0, END)
        self.pc.insert(0, f"{self.__machine.PC:02X}")
        self.ir.delete(0, END)
        self.ir.insert(0, str(self.__machine.IR))


if __name__ == "__main__":
    root = Tk()
    SVM = SpaceCatSimulator(root)
    root.mainloop();