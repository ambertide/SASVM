load R5, 01010001b
load R4, 1
substract:
	load	R6, 11111111b
	xor	R7, R5, R6
	and	R8, R7, R4
	xor	R5, R5, R4
	move	R4, R8
	addi	R4, R4, R4
	jmpEQ R4 = R0, end
	jmp substract

end:
	move RF, R5
	halt




