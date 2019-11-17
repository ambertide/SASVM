from typing import List, Dict, Union, Callable
from os import system


def right_shift(x: str, y: int) -> str:
    """
    Right shift x by a factor of y
    :param x: Bit-pattern to shift
    :param y: Shifting factor
    :return: Shifted bit-pattern
    """
    bit_length = len(x)
    new_bit = ""
    for i in range(bit_length - y):
        new_bit += "0"
    for i in range(y):
        new_bit += x[i]
    return new_bit


def right_rotation(x: str, y: int) -> str:
    """
    Rotate x right by a factor of y
    :param x: Bitstring to rotate.
    :param y: Rotation factor.
    :return: Rotated bit.
    """
    new_bit = ""
    for i in range(y, len(x)):
        new_bit += x[i]
    for i in range(y):
        new_bit += x[i]
    return new_bit


def clear_screen():
    system("cls")


class OctalFloat:
    """
    Implementation of 8-Bit Semi-IEEE 754 compliant Floating Point Numerals
    """
    __bias: int = 8

    def __init__(self, hex_rep: str):
        binary_representation = format(int(hex_rep, base=16), "08b")
        self.__binary_representation = binary_representation
        self.__sign: int = (-1) ** int(binary_representation[0], base=2)
        self.__exponent = int(binary_representation[1:4], base=2) - self.__bias
        self.__mantissa = int(binary_representation[4:], base=2)

    def __float__(self) -> float:
        """
        Convert the number into float.
        :return:
        """
        return self.__sign * (self.__mantissa**self.__exponent)

    def __add__(self, other: "OctalFloat") -> "OctalFloat":
        """
        Add to OctalFloat's together
        :param other: Other OctoFloat to add
        :return: Sum of two OctoFloats, possibly overflown.
        """
        exponent_difference: int = other.__exponent - self.__exponent
        if exponent_difference >= 0:
            operated_mantissa = right_shift(format(self.__mantissa, "04b"), exponent_difference)
            operated = self
            operand = other
        else:
            operated_mantissa = right_shift(format(other.__mantissa, "04b"), abs(exponent_difference))
            operated = other
            operand = self
        number_whole: int = int(operated_mantissa, base=2) * operated.__sign + operand.__mantissa * operand.__sign
        new_sign = "0" if number_whole >= 0 else "1"
        new_mantissa = format(abs(number_whole), "04b")[:4]
        new_exponent = format(operand.__sign + self.__bias, "03b")
        return OctalFloat(new_sign + new_exponent + new_mantissa)

    def __str__(self) -> str:
        """
        Convert to string.
        :return:
        """
        return format(int(self.__binary_representation, base=2), "02X")

    def __int__(self) -> int:
        """
        Convert to integer
        :return:
        """
        return int(self.__binary_representation, base=2)

    def __repr__(self) -> str:
        """
        String representation for printing and debugging.
        :return:
        """
        return self.__binary_representation


class Cell:
    """
    A memory cell.
    """
    def __init__(self):
        """
        Initialise a memory cell.
        """
        self.__value: int = 0

    @property
    def binary_value(self):
        """
        :return: Binary value of the value.
        """
        return format(self.__value, "08b")

    @property
    def value(self):
        """
        Get the value of the cell
        :return: Integer value of the cell.
        """
        return self.__value

    @value.setter
    def value(self, value: Union[str, int]):
        """
        Set the value of the cell, probably overflown.
        :param value: New value to set
        :return: None
        """
        if type(value) == str:
            value = int(value, base=16)
        self.__value = value % 256

    def __repr__(self) -> str:
        return format(self.__value, "02X")


def mem_print(mem: List[Cell]):
    for i in range(16, 256, 16):
        for j in range(i - 16, i):
            print(str(mem[j]), end=" ")
        print()
