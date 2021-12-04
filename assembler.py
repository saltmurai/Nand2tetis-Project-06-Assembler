import re
import sys
import os

class SymbolTable:
	symbols = {
		'SP': 0,
		'LCL': 1,
		'ARG': 2,
		'THIS': 3,
		'THAT': 4,
		'R0': 0,
		'R1': 1,
		'R2': 2,
		'R3': 3,
		'R4': 4,
		'R5': 5,
		'R6': 6,
		'R7': 7,
		'R8': 8,
		'R9': 9,
		'R10': 10,
		'R11': 11,
		'R12': 12,
		'R13': 13,
		'R14': 14,
		'R15': 15,
		'SCREEN': 0x4000,
		'KBD': 0x6000
	}
	nextVariableAddress = 16

	def register_label(self, label, address):
		self.symbols[label] = address

	def resolve(self, symbol):
		if not symbol in self.symbols:
			self.symbols[symbol] = self.nextVariableAddress
			self.nextVariableAddress += 1
		return self.symbols[symbol]

class Code:
    def __init__(self, file, symbol_table):
        self.file = file
        self.symbol_table = symbol_table
    def encode(self, instruction):
        if instruction[0] == '@':
            self._write(self._A_instruction(instruction))
        else:
            self._write(self._C_instruction(instruction))


    def _write(self, line):
        self.file.write(line + '\n')

    
    def _A_instruction(self, instruction):
        instruction_strip = instruction.strip("@")
        if not instruction_strip.isdigit():
            binary = bin(self.symbol_table.resolve(instruction_strip))[2:].zfill(16)
        else:
            binary = self._dec_to_binary(instruction_strip)
        return binary
    
    def _dec_to_binary(self, instruction_interger):
        binary = bin(int(instruction_interger))[2:].zfill(16)
        return binary
    
    def _C_instruction(self, instruction):
        dest_codes = ['', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']
        comp_codes = { '0':'0101010',  '1':'0111111',  '-1':'0111010', 'D':'0001100', 
                        'A':'0110000',  '!D':'0001101', '!A':'0110001', '-D':'0001111', 
                        '-A':'0110011', 'D+1':'0011111','A+1':'0110111','D-1':'0001110', 
                        'A-1':'0110010','D+A':'0000010','D-A':'0010011','A-D':'0000111', 
                        'D&A':'0000000','D|A':'0010101',
                        '':'xxxxxxx',   '':'xxxxxxx',   '':'xxxxxxx',   '':'xxxxxxx', 
                        'M':'1110000',  '':'xxxxxxx',   '!M':'1110001', '':'xxxxxxx', 
                        '-M':'1110011', '':'xxxxxxx',   'M+1':'1110111','':'xxxxxxx', 
                        'M-1':'1110010','D+M':'1000010','D-M':'1010011','M-D':'1000111', 
                        'D&M':'1000000', 'D|M':'1010101' }
        jump_codes = ['', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']

        dest, comp, jump = self._c_parse(instruction)
        dest_bin = bin(dest_codes.index(dest))[2:].zfill(3)
        jump_bin = bin(jump_codes.index(jump))[2:].zfill(3)
        comp_bin = comp_codes[comp]
        return '111' + comp_bin + dest_bin + jump_bin
    
    def _c_parse(self, instruction):
        dest = ''
        comp = ''
        jump = ''
        if '=' in instruction:
            temp_1 = instruction.split("=")
            if ";" in temp_1[1]:
                temp_2 = temp_1[1].split(";")
                dest = temp_1[0]
                comp = temp_2[0]
                jump = temp_2[1]
            else:
                dest = temp_1[0]
                comp = temp_1[1]
        else:
            temp_1 = instruction.split(";")
            if len(temp_1) == 2:
                comp = temp_1[0]
                jump = temp_1[1]
            else:
                comp = temp_1[0]

        return dest, comp, jump

class Parser:
    def __init__(self, code, symbol_table):
        self.code = code
        self.symbol_table = symbol_table
    def parsefile(self, filename):
        instruction = []
        with open(filename) as file:
            for line in file.readlines():
                line = self._strip(line)
                if len(line):
                    if line[0] == '(':
                        self.symbol_table.register_label(line[1: -1], len(instruction))
                    else:
                        instruction.append(line)
        for i in instruction:
            self.code.encode(i)
        
    def _strip(self, line):
        line = re.sub('//.*', '', line)
        line = re.sub(r'\s', '', line)
        return line

def translate_file(asm_file):
    hack_filename = os.path.splitext(asm_file)
    print(hack_filename[0])
    with open(hack_filename[0] + '.hack', "w") as asm:
        symbol_table = SymbolTable()
        writer = Code(asm, symbol_table)
        parser = Parser(writer, symbol_table)
        parser.parsefile(asm_file)
def main(argv):
    if len(argv) == 1 and os.path.splitext(argv[0])[1] == ".asm":
        translate_file(argv[0])
    else:
        print("Useage: python3 Assembler.py <filename>.asm")
        sys.exit(1)
if __name__ == "__main__":
    main(sys.argv[1:])