from unittest import TestCase
from spacecat.common_utils import  OctalFloat


class TestOctalFloat(TestCase):
    def setUp(self) -> None:
        self.octal = OctalFloat("AA")

    def test_octal_creation(self):
        self.assertEqual(-0.15625, float(self.octal))
