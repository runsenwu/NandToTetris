    @R2
    M=0

    @R0
    D=M

    @i
    M=D // i host the first multiplier

(LOOP)
    @END  // jump to end if less than 0
    D;JLE
    
    @R1
    D=M

    @R2
    M=D+M

    @i
    M=M-1
    D=M

    @LOOP
    0;JMP

(END)
    @END
    0;JMP
    