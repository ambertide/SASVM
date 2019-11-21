from unittest import TestCase
from spacecat.common_utils import right_shift


class TestRight_shift(TestCase):
    def test_right_shift(self):
        to_shift = "1111"
        self.assertEqual("0011", right_shift(to_shift, 2))
