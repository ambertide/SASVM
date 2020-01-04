from tkinter import Tk, Label, filedialog, Entry, END, Menu, Event, Button, Frame, RAISED, BOTTOM, TOP, FLAT, Toplevel, \
    StringVar, OptionMenu, W, E, S, N
from tkinter.messagebox import showwarning
from typing import List, Dict, TypeVar, Optional, Callable
from spacecat.simulator import Simulator
from spacecat.common_utils import Cell, OctalFloat
from spacecat.assembler import Assembler
from string import hexdigits
from copy import deepcopy
from enum import Enum
from spacecat.disassembler import disassemble
from svm_config import Language, Config

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


class TICK(Enum):
    """
    Tick is the running speed of the machine.
    """
    HIGH: int = 500
    MEDIUM: int = 300
    LOW: int = 100


class CellEntry(Entry):
    def __init__(self, index_of: int, register_type: str, list_of: List[Cell], monitor_callback: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_type = register_type
        self.index_of = index_of
        self.__variable = StringVar()
        self.__variable.trace_add("write", self.__validate)
        self.config(textvariable=self.__variable)
        self.list_of = list_of

    def __validate(self, *others):
        value: Optional[str] = self.__variable.get()
        if value is None or value == "":
            value = "00"
        value_two: str = value[:2]
        if all(char in hexdigits for char in value_two):
            hex: int = int(value_two, base=16)
        else:
            hex: int = 0
        self.__variable.set(format(hex, "02X"))
        self.__on_edit()

    def __on_edit(self):
        self.list_of[self.index_of].value = self.__variable.get()

    def set(self, value):
        self.__variable.set(value)


class SpaceCatSimulator:
    def __init__(self, master: Tk):

        self.conf = Config()
        self.lang = Language(self.conf.get("lang"))

        self.master = master
        self.master.resizable(height=False, width=False)
        self.master.geometry("510x520")
        self.master.iconbitmap("resources/spacecat.ico")
        self.master.title(self.lang.title)

        self.MEMORY_SIZE = 256
        self.REGISTER_SIZE = 16
        self.ROW_SIZE = 16
        self.STDOUT_REGISTER_INDICES = [15]

        self.file_path: Optional[str] = None
        self.current_tick: TICK = TICK.LOW
        self.clicked_cells: List[CellEntry] = []

        self.__machine: Simulator = Simulator(self.MEMORY_SIZE, self.REGISTER_SIZE, self.STDOUT_REGISTER_INDICES)
        self.__memory_values: List[Cell] = self.__machine.return_memory()  # Memory from previous turn.
        self.__register_values: List[Cell] = self.__machine.return_registers()  # Registers from previous turn.
        self.__define_gui()

    def __define_gui(self):
        self.memory_canvas = Frame(self.master)
        self.register_canvas = Frame(self.master)
        self.monitor_canvas = Frame(self.master)
        self.buttons_frame = Frame(self.master, bd= 1, relief=RAISED)
        self.prev_run_cell = 0

        self.cells = [CellEntry(index_of=i, register_type="M", list_of= self.__machine.return_memory(),
                                monitor_callback=self.__check_monitor, master=self.memory_canvas, width=3)
                      for i in range(self.MEMORY_SIZE)]
        for cell in self.cells:
            cell.bind("<Button-1>", self.on_click)

        self.registers = [CellEntry(index_of=i, register_type="R", list_of=self.__machine.return_registers(),
                                    monitor_callback=self.__check_monitor,
                                    master=self.register_canvas, width=3) for i in range(self.REGISTER_SIZE)]
        for register in self.registers:
            register.bind("<Button-1>", self.on_click)
        self.__populate_canvases()

        self.__run = Button(master=self.buttons_frame, text=self.lang.run, relief=FLAT, command=self.__run_machine)
        self.__step_button = Button(master=self.buttons_frame, text=self.lang.step, relief=FLAT, command=self.__step)
        self.__editor = Button(master=self.buttons_frame, text=self.lang.editor, relief=FLAT)
        self.__disassemble = Button(master=self.buttons_frame, text=self.lang.disassemble, relief=FLAT, command=self.__dis)
        self.__edit_button = Button(master=self.buttons_frame, text=self.lang.edit, relief=FLAT, command=self.__edit)

        self.__run.grid(row=0, column=0)
        self.__step_button.grid(row=0, column=1)
        self.__editor.grid(row=0, column=2)
        self.__disassemble.grid(row=0, column=3)
        self.__edit_button.grid(row=0, column=4)

        self.menubar = Menu(self.master, relief=RAISED)
        self.file_menu = Menu(self.menubar)
        self.emulator_menu = Menu(self.menubar)
        self.speed = Menu(self.menubar)
        self.speed.add_command(label=self.lang.fast, command=lambda : self.__change_tick(TICK.LOW))
        self.speed.add_command(label=self.lang.medium, command=lambda : self.__change_tick(TICK.MEDIUM))
        self.speed.add_command(label=self.lang.slow, command=lambda : self.__change_tick(TICK.HIGH))
        self.file_menu.add_command(label=self.lang.open, command=self.open_file)
        self.file_menu.add_command(label=self.lang.save_state, command=self.__save)
        self.file_menu.add_command(label=self.lang.language_change, command=self.__language_selection)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.lang.exit, command=lambda: quit())
        self.menubar.add_cascade(label=self.lang.file, menu=self.file_menu)
        self.emulator_menu.add_cascade(label=self.lang.speed, menu=self.speed)
        self.menubar.add_cascade(label=self.lang.simulator, menu=self.emulator_menu)
        self.master.config(menu=self.menubar)

        self.bottom_bar = Label(self.master, text=f"{self.lang.decimal}: \t{self.lang.hex}: "
                                                  f"\t{self.lang.float}: \t{self.lang.bin}: ", relief=RAISED)

        self.buttons_frame.pack(fill="x", side=TOP)
        self.memory_canvas.pack()
        self.register_canvas.pack()
        self.monitor_canvas.pack(fill="x")
        self.bottom_bar.pack(fill="x", side=BOTTOM)

    def __on_edit(self, entry):
        index = entry.index_of
        if entry.register_type == "R":
            self.__machine.return_registers()[index].value = int(entry.get(), base=16)
        elif entry.register_type == "M":
            self.__machine.return_memory()[index].value = int(entry.get(), base=16)

    def __change_tick(self, tick_speed: TICK) -> None:
        """
        Set the machine speed
        :param tick_speed: Speed of the machine in ticks.
        :return: None.
        """
        self.current_tick = tick_speed

    def __save(self) -> None:
        """
        Save the state of the machine.
        :return:
        """
        save_file_name: str = filedialog.asksaveasfilename(title=self.lang.save_as,
                                                           filetypes=[(self.lang.prog, ".prg"),
                                                                      (self.lang.svm, ".svm")])
        if save_file_name == "":
            return None
        if save_file_name.endswith(".prg"):
            with open(save_file_name, "wb") as file:
                file.write(self.__machine.dump_program_memory())
        elif save_file_name.endswith(".svm"):
            with open(save_file_name, "wb") as file:
                file.write(self.__machine.dump_program_svm_state())
        else:
            with open(save_file_name + ".prg", "wb") as file:
                file.write(self.__machine.dump_program_memory())
            showwarning(self.lang.warn_title, self.lang.warn_message)

    def __edit(self) -> None:
        """
        Open a NeutronKitty editor to edit the file.
        :return:
        """
        if self.file_path:
            from NeutronKitty import NeutronKitty
            neutron_kitty = NeutronKitty(Tk(), file_path=self.file_path, svm=self)

    def __dis(self) -> None:
        """
        Disassemble the file and open a NeutronKitty to edit and see the results.
        :return:
        """
        values = []
        for i in range(0, len(self.__memory_values), 2):
            values.append(str(self.__memory_values[i]) + str(self.__memory_values[i + 1]))
        dis_ = disassemble(values)
        commands = filter(lambda x: x != "", dis_)
        string = '\n'.join(commands)
        from NeutronKitty import NeutronKitty
        neutron_kitty = NeutronKitty(Tk(), string)

    def __check_monitor(self):
        new_text = self.monitor["text"] + self.__machine.return_stdout()
        self.monitor["text"] = new_text.split("\n")[-1]

    def __sync_machine(self):
        """
        Sync the machine's registers with the entry fields in case modified
        :return:
        """
        print(self.clicked_cells)
        for clicked in self.clicked_cells:
            index = clicked.index_of

    def __run_machine(self):
        """
        Run the machine.
        :return:
        """
        self.__step()
        try:
            self.master.after(self.current_tick.value, self.__run_machine)
        except StopIteration:
            pass

    def __step(self):
        """
        Take a step in the program.
        :return:
        """
        try:
            memory_cells, register_cells = self.__machine.__next__()
#            self.__sync_machine()
            self.__update_view(memory_cells, register_cells)
            self.__check_monitor()
        except StopIteration:
            pass

    def open_file(self, file_name=None):
        """
        Open a file to load to the memory.
        :return:
        """
        if not file_name:
            file_name: str = filedialog.askopenfilename(title=self.lang.select,
                                                        filetypes=((self.lang.asm, "*.asm"),
                                                                   (self.lang.prog, "*.prg"),
                                                                   (self.lang.svm, "*.svm")))
        if file_name.endswith(".asm"):
            self.file_path = file_name
            assembler: Assembler = Assembler.instantiate(open(file_name, "r").read(), 256)
            self.__machine.load_memory(assembler.memory)
        elif file_name.endswith(".prg"):
            self.__machine.parse_program_memory(open(file_name, "rb").read())
            self.__reset_ir_pc()
            self.__machine.reset_special_registers()
        elif file_name.endswith(".svm"):
            self.__machine.parse_program_state(open(file_name, "rb").read())
            self.__load_special_registers()
        self.__update_view(self.__machine.return_memory(), self.__machine.return_registers())

    def on_click(self, event: Event):
        """
        When clicked over an event.
        :param event:
        :return:
        """
        value = event.widget.get()
        self.clicked_cells.append(event.widget)
        real_val = int(value, base=16)
        self.bottom_bar["text"] = f"{self.lang.decimal}: {real_val:03}" \
                                  f"\t{self.lang.hex}: {real_val:02X}" \
                                  f"\t{self.lang.float}: {OctalFloat(format(real_val, '02X')).__float__():.3f}" \
                                  f"\t{self.lang.bin}: {real_val:08b}"

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
        self.monitor = Label(self.monitor_canvas, text="", width=1000)
        self.monitor.config(bg="black", fg="green", font=("fixedsys", 15))
        self.monitor.pack(fill="x")
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
            self.cells[change_index].set(str(new_value))
        for change_index, new_value in register_differences.items():
            self.registers[change_index].set(str(new_value))
        self.__load_special_registers()
        self.cells[self.__machine.PC]["background"] = "Green"
        self.cells[self.prev_run_cell]["background"] = "White"
        self.prev_run_cell = self.__machine.PC

    def __load_special_registers(self):
        """
        Load the special registers
        :return:
        """
        self.pc.delete(0, END)
        self.pc.insert(0, f"{self.__machine.PC:02X}")
        self.ir.delete(0, END)
        self.ir.insert(0, str(self.__machine.IR))

    def __language_selection(self) -> None:
        """
        Open a window to select the language
        :return:
        """
        lang = {"en": "English", "tr": "Türkçe"}
        lang_rev = {"English": "en", "Türkçe": "tr"}
        langs = ["English", "Türkçe"]
        language_selector = Toplevel(self.master)
        Label(master=language_selector, text=self.lang.language_change).grid(row=0, column=0)
        language_selection = StringVar(language_selector)
        language_selection.set(lang[self.conf.get("lang")])
        language_sel = OptionMenu(language_selector, language_selection, *langs)
        language_sel.grid(row=1, column=0)

        def __set_language():
            self.conf.set("lang", lang_rev[language_selection.get()])
            showwarning(title=self.lang.restart_title, message=self.lang.restart_message)
        approve_button = Button(master=language_selector, text=self.lang.save, command=__set_language)
        approve_button.grid(row=0, column=1, rowspan=2, sticky=W+E+S+N)


if __name__ == "__main__":
    root = Tk()
    SVM = SpaceCatSimulator(root)
    root.mainloop()
