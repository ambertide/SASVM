from tkinter import Tk, Text, Button, END
from re import compile as regex_compile


class NeutronKitty:
    mnemonic_pattern = regex_compile(r"(?i)load|xor|and|move|store|addi|addf|or|ror|jmpeq|jmp|jmple|halt")
    comment_pattern = regex_compile(";.*")

    def __init__(self, master: Tk, string: str = ""):
        self.master = master
        self.master.title("NeutronKitty Text Editor")
        self.master.geometry("500x500")

        self.editor = Text(master=self.master, height=28)
        self.editor.insert(END, string)
        self.editor.pack(fill="x")

        self.assemble_button = Button(master=self.master, text="Assemble")
        self.assemble_button.pack(fill="x")

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