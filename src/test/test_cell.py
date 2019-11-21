from unittest import TestCase
from spacecat.common_utils import Cell


class TestCell(TestCase):
    def setUp(self) -> None:
        self.cell = Cell()
        self.cell.value = 16

    def test_binary_value(self):
        self.assertEqual("00010000", self.cell.binary_value)

    def test_value(self):
        self.assertEqual(16, self.cell.value)
