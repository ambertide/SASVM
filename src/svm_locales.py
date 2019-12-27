from typing import Dict


class Language:
    def __init__(self, lang_code):
        file_name = f"svm-{lang_code}.locale"
        self.strings: Dict[str, str] = {}
        def __add_line(line: str) -> None:
            key, value = line.split(",")
            self.strings[key] = value
        with open(file_name, "r") as file:
            for line in file.readlines():
                __add_line(line)

    def __getattr__(self, item) -> str:
        return self.strings[item]
