from typing import List


class Preprocessor:
    def __init__(self, file_str: str, terminal_sign: str, is_file: bool = True):
        self.data: str = ""
        if is_file:
            with open(file_str) as file:
                self.data = file.read()
        else:
            self.data = file_str
            self.terminal_sign = terminal_sign
        self.data = self.process_data()

    def process_data(self) -> List[str]:
        intermediate: List[str] = self.data.split(self.terminal_sign)
        intermediate = list(map(lambda x: x + ";", intermediate))
        return intermediate