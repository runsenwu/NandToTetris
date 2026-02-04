// Thoughts, this one should be quite simple

1. make sure that we are filling the whole screen

storage = keyboard;

loop
    if storage > 0
        fill screen
    else:
        pass


(LOOP)
    @SCREEN
    D=A     // why do we do D=A here? Instead of using M? Because when we use A we are getting the address
    
    @addr
    M=D

    @8192
    D=A

    @i
    M=D+M

    @KBD
    D=M

    @CLEAR
    D;JEQ

(DRAW) // need to think about drawing the whole screen here, 8192
    @addr
    A=M
    M=-1

    @addr
    M=M+1

    @i
    M=M-1
    D=M
    
    @DRAW
    D;JGT

    @LOOP
    0;JMP

(CLEAR)
    @addr
    A=M
    M=0

    @addr
    M=M+1

    @i
    M=M-1
    D=M
    
    @CLEAR
    D;JGT

    @LOOP
    0;JMP