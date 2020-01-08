from typing import Dict


class Language:
    def __init__(self, lang_code):
        file_name = f"resources/svm-{lang_code}.locale"
        self.strings: Dict[str, str] = {}

        def __add_line(line: str) -> None:
            key, value = line.split(":=")
            self.strings[key] = value.strip("\n")
        with open(file_name, "r", encoding="utf8") as file:
            for line in file.readlines():
                if line == "":
                    continue
                __add_line(line)

    def __getattr__(self, item) -> str:
        return self.strings[item]


class Config:
    def __init__(self):
        self.file_name = "resources/svm.conf"
        self.settings: Dict[str, str] = {}

        def __add_line(line: str) -> None:
            key, value = line.split(":=")
            self.settings[key] = value
        with open(self.file_name, "r") as file:
            for line in file.readlines():
                if line == "":
                    continue
                __add_line(line)

    def set(self, key, value) -> None:
        self.settings[key] = value
        output: str = "\n".join(":=".join(pair) for pair in self.settings.items())
        with open(self.file_name, "w") as file:
            file.write(output)

    def get(self, item) -> str:
        return self.settings[item]