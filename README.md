# SpaceCat Assembly Simulator

[![Maintainability](https://api.codeclimate.com/v1/badges/95ea78743aed47ad7530/maintainability)](https://codeclimate.com/github/ambertide/SASVM/maintainability)

SpaceCat Assembly Simulator is an educational tool that simulates an 8-bit processor as defined in
Computer Science: An Overview by Brookshear & Brylow. It is compatible with a previous implementation of the same machine
called SimpSim (or BasSim, depending on the locale.)

## The Machine
SVM is a simple machine, it contains 256 memory addresses each holding up to 32 bits of data, as well as 16 registers.

### Special Registers
Name | Representation | Usage
-----|----------------|------
Program Counter | PC | Program counter holds the address of the next memory cell to execute|
Instruction Register |IR | Instruction register holds the last instruction that was executed.|
STDOUT | RF | RF register is mapped to the STDOUT, when RF is modified in some way, character corresponding to the value inside RF according to RF is outputted to STDOUT, which is almost always the screen.

## Instructions and Assembly Language

SVM works on a simplified assembly language.

### Data

In SVM, as in the previous implementation, there are integers, and only* integers.

#### the Integer

Name | Representation | Example
-----|----------------|--------
Decimal | -D, Dd, D | -10, 10d, -10d, 10
Binary | Db | 10101b
Hexadecimal | 0xD, Dh, $D | 0xAA, AAh, $AA

#### The Float

The floating point numerals are represented as proposed in the book Computer Science: An Overview, this representation is...
 *close* to IEEE 754, however, there are differences. To start our journey, it is important to understand that
 
 * Assembly Language as used in SVM **does not** formally define floating point numbers, when two values are combined using ADDF instruction, they are 
 interpreted as Floating point numerals.
 
 * SVM's floating point numerals are 8-bit floating point numerals sometimes lovingly called *minifloats*
 
 * They are structured as follows
 
 Sign Bit | Exponent | Mantissa
 --------|-----------|------
 1 bit | 4 bits | 3 bits
 one for negative, zero for positive | balanced for 1000 = 0 | The mantissa.
 
 And then calculated as for exponent = ``e``, mantissa = ``m``  2<sup>e</sup>m. 

### Base Instructions
Instruction | Operands | Explanation | OP-Code Representation 
--------|----------|-------------|----------
LOAD | Register, [Memory Address] | Loads the value in the memory address to register | 1RMe
LOAD | Register, Value | Loads the value to the register | 2RVa
STORE | Register, [Memory Address] | Store the value in register in the memory address | 3RMe
MOVE | Register, Register | Move the value in register 1 to register 2 | 40RR
ROR | Register, Value | Rotate the Register right Value times | AR0V
JMP |  Value | Jump to the memory cell indexed value | B0Va
JMPEq | Register =R0, Value | Jump to Value index if Register equals R0 | BRVa
HALT | No operands. | Halt the program execution, for SVM this mostly means stopping the program | C000
LOAD | Register, Register | Load the value in the memory index hold by the second register to the first register | D0RR
STORE | Register, Register | Store the value in register one to the memory index hold in second register. | E0RR
JMPLe | Register <=R0, Value | Jump to the value index if the value in register is less then the one in R0. | FRVa

### Arithmatic Instructions
Instructions which always take three registers as operands, applies an operation to values in second and third registers
and stores the result in the first register.

Mnemonic | Operation | OP-Code Representation
--------|------------|-----------------------
ADDI | Integer addition | 5RRR
ADDF | Floating point addition | 6RRR
OR | Bitwise or | 7RRR
AND| Bitwise and | 8RRR
XOR | Bitwise exclusive or | 9RRR

### Directives
Assembly language used by SVM also has a directives. Directives
may change the assembled memory, but they do not get converted into an OP-Code.

Directive | Usage | Effect
----------|-------|-------
ORG | Org Address | Tells the assembler that the succeeding instruction will be put into the memory adress.
DB | DB String | Tells the assembler to put the ASCII values of the characters in string to memory cells, one character at a time.

### Labels
Labels are pretty much pointers, they denote a place in the memory, they can be assigned to a DB directive or to the start of a line,
afterwards, they reefer to the address of the following line.

### Comments

Start of a comment statement in SVM Assembly is denoted by a ``;`` and its end is denoted by the end-of-line character ``\n``.
Comments are ignored by the assembler.

## On SpaceCat

### Frequently Asked Questions

#### What are the requirements for SpaceCat?
SpaceCat requires at least Python 3.8  due to its use of typing hints (3.5+) and the walrus operator (3.8+) in some places,
it also requires tkinter package for its GUI.

#### How compatible is it with SimpSim/BasSim?
Very compatible, it can do most of the stuff SimpSim does and aims for total coverage very soon, moreover, it supports the *.prg
file format, which is what SimpSim exports its memory.

##### What is a machine state?
It is a new addition, rather than only dumping the memory, it saves the registers as well, so it can freeze the machine state and save it.

#### Why Python?
SVM is implemented in Python 3.8, it can therefore run in any platform supporting 3.8, but it also offers binaries for
Windows. It *probably* can run on PyPy as well.

## The missing stuff

* Turkish translation.
* Editable cells.
* OctalFloat might not be working as intended, I can't wrap my head around additions and truncations.