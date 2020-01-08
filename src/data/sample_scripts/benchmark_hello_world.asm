load R1, cat
load R7, 13
load R8, 1
addi R0, R1, R7
loop:
	load R3, [R1] 
	move RF, R3
	addi R1, R1, R8
	jmple R1<=R0, loop
	halt
cat: db "Hello, World!