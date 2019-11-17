from tkinter import Tk, Label, Canvas, Entry, END, Menu, Event, Button, Frame, RAISED, BOTTOM, TOP, SUNKEN, FLAT
from typing import List, Dict, TypeVar
from simulator import Simulator
from common_utils import Cell, OctalFloat


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


class SpaceCatSimulator:
    def __init__(self, master: Tk):

        self.master = master
        self.master.resizable(height=False, width=False)
        self.master.geometry("500x500")
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

        self.cells = [Entry(master=self.memory_canvas, width=3)
                      for _ in range(self.MEMORY_SIZE)]
        for cell in self.cells:
            cell.bind("<Button-1>", self.on_click)
        self.registers = [Entry(master=self.register_canvas, width=3) for _ in range(self.REGISTER_SIZE)]
        self.__populate_canvases()


        self.__run = Button(master=self.buttons_frame, text="Run", relief=FLAT)
        self.__step = Button(master=self.buttons_frame, text="Step", relief=FLAT)
        self.__editor = Button(master=self.buttons_frame, text="Editor", relief=FLAT)
        self.__disassemble = Button(master=self.buttons_frame, text="Disassemble", relief=FLAT)

        self.__run.grid(row=0, column=0)
        self.__step.grid(row=0, column=1)
        self.__editor.grid(row=0, column=2)
        self.__disassemble.grid(row=0, column=3)


        self.menubar = Menu(self.master, relief=RAISED)
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open", command=lambda: None)
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


    def on_click(self, event: Event):
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
        self.__load_memory_to_view()

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

    def __update_view(self, new_memory: List[Cell], new_registers: List[Cell]):
        """
        Update the view without explicitly reloading the view.
        :param new_memory: New memory to be loaded.
        :param new_registers: New registers to be loaded.
        :return:
        """
        register_differences = get_difference(self.__register_values, new_registers)
        memory_differences =  get_difference(self.__memory_values, new_memory)
        self.__memory_values = new_memory
        self.__register_values = new_registers
        for change_index, new_value in memory_differences:
            self.cells[change_index].delete(0, END)
            self.cells[change_index].insert(0, str(new_value))
        for change_index, new_value in register_differences:
            self.registers[change_index].delete(0, END)
            self.registers[change_index].insert(0, str(new_memory))

if __name__ == "__main__":
    root = Tk()
    SVM = SpaceCatSimulator(root)
    root.mainloop();