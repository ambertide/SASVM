LOAD R0, 5Ah; Load the end of the capital English ASCII block.
LOAD R1, 1; Load the increment register.
LOAD R2, 40h; Load the start of the capital English ASCII block.
LOOP:
    MOVE RF, R2; Move the value at R2 to the STDOUT register.
    ADDI R2, R2, R1; Increment
    JMPLE R2<=R0, loop
    HALT