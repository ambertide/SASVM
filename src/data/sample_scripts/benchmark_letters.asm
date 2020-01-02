load R0, 5Ah; Load the end of the capital English ASCII block.
load R1, 1; Load the increment register.
load R2, 40h; Load the start of the capital English ASCII block.
loop:
    move RF, R2; Move the value at R2 to the STDOUT register.
    addi R2, R2, R1; Increment
    jmpLE R2<=R0, loop
    halt