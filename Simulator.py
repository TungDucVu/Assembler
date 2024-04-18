import argparse
import sys

class Processor:
    def __init__(self):
        self.dictreg = {"R0": 0, "R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0, "R6": 0, "V": 0, "L": 0, "G": 0, "E": 0}
        self.opreg = {"R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110", "FLAGS": "111"}
        self.variables = {}
        self.E = ['01100', '01101', '01111']

    def convert(self, imm):
        imm = imm[::-1]
        val = 0
        k = 0
        for i in imm:
            if i == '1':
                val += 2 ** k
            k += 1
        return val

    def printfunc(self, i, over):
        pstr = ""
        i = str(bin(i))[2:]
        s = len(i)
        while s < 8:
            i = "0" + i
            s = len(i)
        pstr += i + " "
        k = 0
        f = 0
        for i in self.dictreg.values():
            t = str(bin(i))[2:]
            if k < 7:
                t = self.regval(t)
                pstr += t + " "
            else:
                if over == 1:
                    pstr += "0000000000001000"
                elif i == 1:
                    if self.dictreg["E"] == 1:
                        pstr += "0000000000000001"
                    elif self.dictreg["L"] == 1:
                        pstr += "0000000000000100"
                    elif self.dictreg["G"] == 1:
                        pstr += "0000000000000010"
                    f = 1
            k += 1
        if f == 0:
            pstr += "0000000000000000"
        print(pstr)

    def regval(self, t):
        s = len(t)
        while s < 16:
            t = "0" + t
            s = len(t)
        return t

    def typeA(self, str1):
        s1 = str1[:5]
        x = str1[7:10]
        y = str1[10:13]
        z = str1[13:]
        for key, value in self.opreg.items():
            if x == value:
                x = key
            if y == value:
                y = key
            if z == value:
                z = key
        a = self.dictreg[x]
        b = self.dictreg[y]
        c = self.dictreg[z]
        check = 2 ** 16 - 1
        if s1 == '10000':
            solve = b + c
            over = 0
            if solve > check:
                over = 1
                self.dictreg["E"] = 0
                self.dictreg["G"] = 0
                self.dictreg["L"] = 0
                self.dictreg["V"] = 1
                b = str(bin(solve))[2:]
                b = b[::-1]
                b = b[:16]
                b = b[::-1]
                solve = self.convert(b)
            self.dictreg[x] = solve
            return over
        elif s1 == '10001':
            solve = b - c
            if solve < 0:
                solve = 0
            self.dictreg[x] = solve
        elif s1 == '10110':
            solve = b * c
            over = 0
            if solve > check:
                over = 1
                self.dictreg["E"] = 0
                self.dictreg["G"] = 0
                self.dictreg["L"] = 0
                self.dictreg["V"] = 1
                b = str(bin(solve))[2:]
                b = b[::-1]
                b = b[:16]
                b = b[::-1]
                solve = self.convert(b)
            self.dictreg[x] = solve
            return over
        elif s1 == '11010':
            solve = b ^ c
            self.dictreg[x] = solve
        elif s1 == '11011':
            solve = b | c
            self.dictreg[x] = solve
        elif s1 == '11100':
            solve = b & c
            self.dictreg[x] = solve

    def typeB(self, str1):
        s1 = str1[:5]
        reg = str1[5:8]
        imm = str1[8:]
        val = self.convert(imm)
        for key, value in self.opreg.items():
            if reg == value:
                reg = key
        if s1 == '10010':
            self.dictreg[reg] = val
        if s1 == '11001':
            k = self.dictreg[reg]
            k = k << val
            self.dictreg[reg] = k
        if s1 == '11000':
            k = self.dictreg[reg]
            k = k >> val
            self.dictreg[reg] = k

    def typeC(self, str1):
        s1 = str1[:5]
        x = str1[10:13]
        y = str1[13:]
        for key, value in self.opreg.items():
            if x == value:
                x = key
            if y == value:
                y = key
        if s1 == '10010':
            self.dictreg[x] = value
        if s1 == '10011':
            if y == '111':
                if self.dictreg["V"] == 1:
                    self.dictreg[x] = 1
                elif self.dictreg["L"] == 1:
                    self.dictreg[x] = 1
                if self.dictreg["G"] == 1:
                    self.dictreg[x] = 1

    def typeD(self, str1):
        s1 = str1[:5]
        reg = str1[5:8]
        for key, value in self.opreg.items():
            if reg == value:
                reg = key
        addr = str1[8:]
        val = self.dictreg[reg]
        if s1 == '10101':
            self.variables[addr] = val
        if s1 == '10100':
            if addr not in self.variables.keys():
                self.variables[addr] = 0
            memval = self.variables[addr]
            self.dictreg[reg] = memval

    def typeE(self, str1, i):
        s1 = str1[:5]
        addr = str1[8:]
        addr = self.convert(addr)
        if s1 == '11111':
            return addr + 1
        if s1 == '01100':
            l = self.dictreg["L"]
            if l == 1:
                return addr + 1
        if s1 == '01101':
            g = self.dictreg["G"]
            if g == 1:
                return addr + 1
        if s1 == '01111':
            e = self.dictreg["E"]
            if e == 1:
                return addr + 1
        return i + 2
def process_assembly(input_file_path, output_file_path):
    p = Processor()
    A = sys.stdin.readlines()
    B = [i.rstrip() for i in A]

    i = 0
    while i < len(B) - 1:
        over = 0
        t = i
        str1 = B[i]
        s1 = str1[:5]
        if s1 not in p.E:
            p.dictreg["E"] = 0
            p.dictreg["G"] = 0
            p.dictreg["L"] = 0
            p.dictreg["V"] = 0
        if s1 in ['10000', '10001', '10110', '11010', '11011', '11100']:
            over = p.typeA(str1)
        if s1 in ['10010', '11001', '11000']:
            p.typeB(str1)
        if s1 in ['10011', '10111', '11101', '11110']:
            p.typeC(str1)
        if s1 in ['10101', '10100']:
            p.typeD(str1)
        if s1 in ['11111', '01100', '01101', '01111']:
            t = p.typeE(str1, i) - 2
        p.printfunc(i, over)
        i = t

    p.printfunc(i, 0)

    final = {}
    for key, value in p.variables.items():
        val = bin(value)[2:]
        s = len(val)
        while s < 16:
            val = "0" + val
            s = len(val)
        k = int(key)
        final[k] = val

    list_keys = sorted(final.keys())
    j = 256 - len(B) - len(list_keys)

    for i in B:
        print(i)

    for i in list_keys:
        print(final[i])

    str2 = "0000000000000000"
    for i in range(j):
        print(str2)

def main():
    parser = argparse.ArgumentParser(description="Assembler for converting assembly code to machine code")
    parser.add_argument("input_file", help="Path to the input assembly code file")
    parser.add_argument("output_file", help="Path to the output machine code file")
    args = parser.parse_args()

    process_assembly(args.input_file, args.output_file)

if __name__ == "__main__":
    main()