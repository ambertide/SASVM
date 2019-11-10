import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QVBoxLayout, QGridLayout, QTextEdit, QPushButton, QBoxLayout
from PyQt5.QtGui import QIcon


class Memory(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__grid = QGridLayout(self)
        self.__grid.setHorizontalSpacing(0)
        self.__grid.setVerticalSpacing(0)
        self.__grid.setContentsMargins(0, 0, 0, 0)
        self.__memory = [0 for _ in range(256)]
        for i in range(16):
            for j in range(16):
                obj = QPushButton()
                obj.setFixedWidth(30)
                obj.setFixedHeight(30)
                self.__grid.addWidget(obj, i, j)

        self.setLayout(self.__grid)

    @staticmethod
    def convert_cartesian(x: int, base: int) -> (int, int):
        i = x // base
        j = x % base
        return i, j

class Example(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 760, 620)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('web.png'))

        self.first_layout = QVBoxLayout()
        self.setLayout(self.first_layout)

        self.main_memory = Memory()
        self.first_layout.addWidget(self.main_memory)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())