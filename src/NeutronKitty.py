from tkinter import Tk, Text, Button, Menu, END, RAISED
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror, showwarning
from re import compile as regex_compile
from typing import Optional
from simpleGui import SpaceCatSimulator


class NeutronKitty:
    mnemonic_pattern = regex_compile(r"(?i)load|xor|and|move|store|addi|addf|or|ror|jmpeq|jmp|jmple|halt")
    comment_pattern = regex_compile(";.*")

    def __init__(self, master: Tk, string: str = "", file_path: str = "", svm: SpaceCatSimulator = None):
        self.master = master
        self.master.title("NeutronKitty Text Editor")
        self.master.geometry("500x500")
        self.master.bind("<Control-S>", self.__save)
        self.master.bind("<Control-s>", self.__save)
        self.vm: SpaceCatSimulator = svm

        self.editor = Text(master=self.master)
        self.editor.insert(END, string)
        self.editor.pack(fill="both", expand=True)

        self.file_path: Optional[str] = None
        self.edited = False

        self.menubar = Menu(self.master, relief=RAISED)
        self.file_menu = Menu(self.menubar)
        self.assemble_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open", command=self.__open)
        self.file_menu.add_command(label="Save", command=self.__save)
        self.file_menu.add_command(label="Save As", command=self.__save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=lambda: quit())
        self.assemble_menu.add_command(label="Assemble", command=self.__assemble)
        self.assemble_menu.add_command(label="Disassemble", command=None)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Assembler", menu=self.assemble_menu)
        self.master.config(menu=self.menubar)


        if file_path:
            self.file_path = file_path
            try:
                self.__open_file(file_path)
            except FileNotFoundError:
                showerror("File Not Found Error", "Failed to Locate File")
                exit(2)

    def __save(self, *args):
        if not self.file_path:
            self.__save_as()
        else:
            self.__save_file(self.file_path)

    def __save_as(self):
        self.file_path = asksaveasfilename(filetypes=[("Assembly Files", "*.asm"), ("All files", "*.*")])
        self.__save_file(self.file_path)

    def __open(self) -> None:
        """
        Wrapper around __open_file to ask the user for the file_path
        :return: None
        """
        self.__open_file(askopenfilename(filetypes=[("Assembly File", "*.asm"), ("Text File", "*.txt"),
                                                    ("All files", "*.*")]))

    def __update_title(self) -> None:
        """
        Update the title to the current file's name.
        :return:
        """
        self.master.title(f"NeutronKitty Text Editor - {self.file_path.split('/')[-1]}")


    def __save_file(self, file_path: str) -> None:
        """
        Save the contents of the textfield to a given file.
        :param file_path: Path to the file.
        :return: None.
        """
        self.file_path = file_path
        with open(file_path, "w") as file:
            file.write(self.editor.get(1.0, END))

    def __open_file(self, file_path: str) -> None:
        """
        Open a file with a given path..
        :param file_path: File path to open.
        :return: None.
        """
        with open(file_path, "r") as file:
            self.editor.delete("1.0", END)
            self.editor.insert(END, file.read())
            self.file_path = file_path

    def __assemble(self) -> None:
        """
        Assemble the results in the assembler.
        :return:
        """
        self.__save()
        if self.file_path:
            self.vm.open_file(self.file_path)
        else:
            showwarning("Save the file first", "You must save the file first.")

    def __set_tags(self):
        self.editor.tag_configure("mnemonic", foreground="green")
        self.editor.tag_configure("comment", foreground="grey")

    def __colour(self) -> None:
        for line in self.editor.get(1.0, END):
            mnemonics = self.mnemonic_pattern.findall(line)
            comments = self.comment_pattern.findall(line)

if __name__ == "__main__":
    root = Tk()
    nr = NeutronKitty(root)
    root.mainloop()