jmp 20h

dividesignificants:
	org 	20h
	load	R1, 80h
	load	R2, 00001111b
	load	R3, 11110000b
	and	R4, R1, R2
	and	R5, R1, R3
	ror	R5, 4

substract:
	load	R6, 11111111b ; NOT için kullanýlacak kýsým.  
	xor	R7, R5, R6; NOT Y
	and	R8, R7, R4; y - x'in elde kýsmý
	xor	R5, R5, R4 ; y - x'nin çýkarma kýsmý
	move	R4, R8
	addi	R4, R4, R4 ; kendisini eklemek = ikiyle çarpmak = left shift
	jmpEQ R4 = R0, end ; Eðer, ç?kar?lacak elde kalmadýysa bitir.
	jmp substract

end:
	halt





