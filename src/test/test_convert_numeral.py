from unittest import TestCase
from spacecat.assembler import convert_numeral


class TestConvert_numeral(TestCase):
    def test_convert_numeral_hex_capital(self):
        str_num: str = "0xA0"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numeral_hex_lower(self):
        str_num: str = "0xa0"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numeral_hex_pascal_cap(self):
        str_num: str = "$A0"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numeral_hex_pascal_lower(self):
        str_num: str = "$a0"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numeral_hex_assembler_cap(self):
        str_num: str = "A0h"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numeral_hex_assembler_low(self):
        str_num: str = "a0h"
        self.assertTrue("A0" == convert_numeral(str_num))

    def test_convert_numberal_bin(self):
        str_num: str = "10000001b"
        self.assertTrue("81" == convert_numeral(str_num))