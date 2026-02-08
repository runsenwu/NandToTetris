#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# -----------------------------
# Hack spec tables
# -----------------------------

PREDEFINED_SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    **{f"R{i}": i for i in range(16)},
}

DEST_TABLE = {
    "":   "000",
    "M":  "001",
    "D":  "010",
    "MD": "011",
    "A":  "100",
    "AM": "101",
    "AD": "110",
    "AMD":"111",
}

JUMP_TABLE = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

# comp (a,c1..c6) bits for the Hack CPU
COMP_TABLE = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",

    # a=1 variants (use M)
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}


# -----------------------------
# Helpers
# -----------------------------

def clean_lines(text: str) -> list[str]:
    """
    Remove comments and whitespace. Returns only meaningful lines:
    - A-instructions: @xxx
    - C-instructions: dest=comp;jump (dest/jump optional)
    - Labels: (LABEL)
    """
    out: list[str] = []
    for raw in text.splitlines():
        # drop inline comment
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        out.append(line)
    return out

def is_label(line: str) -> bool:
    return line.startswith("(") and line.endswith(")")

def label_name(line: str) -> str:
    # assumes valid label form
    return line[1:-1].strip()

def to_16bit(n: int) -> str:
    if not (0 <= n <= 32767):
        raise ValueError(f"A-instruction value out of range (0..32767): {n}")
    return format(n, "016b")

def parse_c_instruction(line: str) -> tuple[str, str, str]:
    """
    Returns (dest, comp, jump) strings, with dest/jump possibly "".
    Grammar:
      dest=comp;jump
      dest=comp
      comp;jump
      comp
    """
    dest = ""
    jump = ""
    comp = line

    if "=" in comp:
        dest, comp = comp.split("=", 1)
        dest = dest.strip()
        comp = comp.strip()

    if ";" in comp:
        comp, jump = comp.split(";", 1)
        comp = comp.strip()
        jump = jump.strip()

    return dest, comp, jump


# -----------------------------
# Assembler (two pass)
# -----------------------------

def first_pass(lines: list[str], symbol_table: dict[str, int]) -> list[str]:
    """
    Record labels -> ROM addresses.
    Returns instruction-only list (labels removed).
    """
    rom_address = 0
    out: list[str] = []

    for line in lines:
        if is_label(line):
            name = label_name(line)
            if not name:
                raise ValueError("Empty label () is not allowed")
            # In Hack, re-defining a label is typically an error.
            if name in symbol_table:
                # If you want to allow redefinition, remove this.
                raise ValueError(f"Label redefined: {name}")
            symbol_table[name] = rom_address
        else:
            out.append(line)
            rom_address += 1

    return out

def second_pass(lines: list[str], symbol_table: dict[str, int]) -> list[str]:
    """
    Translate A and C instructions to binary.
    Allocate variables starting at RAM[16].
    """
    next_var_address = 16
    out: list[str] = []

    for line in lines:
        if line.startswith("@"):
            sym = line[1:].strip()
            if not sym:
                raise ValueError("Invalid A-instruction: '@' with no symbol/value")

            # numeric constant?
            if sym.isdigit():
                value = int(sym, 10)
                out.append(to_16bit(value))
                continue

            # symbol: label or variable
            if sym not in symbol_table:
                symbol_table[sym] = next_var_address
                next_var_address += 1

            out.append(to_16bit(symbol_table[sym]))
            continue

        # C-instruction
        dest, comp, jump = parse_c_instruction(line)

        if dest not in DEST_TABLE:
            raise ValueError(f"Invalid dest '{dest}' in: {line}")
        if jump not in JUMP_TABLE:
            raise ValueError(f"Invalid jump '{jump}' in: {line}")
        if comp not in COMP_TABLE:
            raise ValueError(f"Invalid comp '{comp}' in: {line}")

        bin_line = "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
        out.append(bin_line)

    return out

def assemble_text(asm_text: str) -> str:
    symbol_table: dict[str, int] = dict(PREDEFINED_SYMBOLS)

    cleaned = clean_lines(asm_text)
    no_labels = first_pass(cleaned, symbol_table)
    binary_lines = second_pass(no_labels, symbol_table)

    return "\n".join(binary_lines) + "\n"


# -----------------------------
# CLI
# -----------------------------

def main(argv: list[str]) -> int:
    asm_path = Path(r".\pong.asm")

    if not asm_path.exists():
        print(f"File not found: {asm_path}")
        return 2
    if asm_path.suffix.lower() != ".asm":
        print("Warning: input does not end with .asm (still attempting).")

    asm_text = asm_path.read_text(encoding="utf-8")
    hack_text = assemble_text(asm_text)

    out_path = asm_path.with_suffix(".hack")
    out_path.write_text(hack_text, encoding="utf-8")

    print(f"Wrote: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
