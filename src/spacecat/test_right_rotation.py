from unittest import TestCase
from spacecat.common_utils import right_rotation


class TestRight_rotation(TestCase):
    def test_right_rotation(self):
        self.assertEqual("1100", right_rotation("0011", 2))
