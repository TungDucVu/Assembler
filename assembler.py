import argparse

register_numbers = {
    "zero": 0b00000,   # x0
    "ra": 0b00001,     # x1
    "sp": 0b00010,     # x2
    "gp": 0b00011,     # x3
    "tp": 0b00100,     # x4
    "t0": 0b00101,     # x5
    "t1": 0b00110,     # x6
    "t2": 0b00111,     # x7
    "s0": 0b01000,     # x8
    "fp": 0b01000,     # x8
    "s1": 0b01001,     # x9
    "a0": 0b01010,     # x10
    "a1": 0b01011,     # x11
    "a2": 0b01100,     # x12
    "a3": 0b01101,     # x13
    "a4": 0b01110,     # x14
    "a5": 0b01111,     # x15
    "a6": 0b10000,     # x16
    "a7": 0b10001,     # x17
    "s2": 0b10010,     # x18
    "s3": 0b10011,     # x19
    "s4": 0b10100,     # x20
    "s5": 0b10101,     # x21
    "s6": 0b10110,     # x22
    "s7": 0b10111,     # x23
    "s8": 0b11000,     # x24
    "s9": 0b11001,     # x25
    "s10": 0b11010,    # x26
    "s11": 0b11011,    # x27
    "t3": 0b11100,     # x28
    "t4": 0b11101,     # x29
    "t5": 0b11110,     # x30
    "t6": 0b11111      # x31
}

def r_type_instruction(rd, rs1, rs2, instruction):
    opcode = 0b0110011
    funct3, funct7 = r_type_funct3_funct7_mapping[instruction]
    return format((funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode, '032b')

r_type_funct3_funct7_mapping = {
    "add": (0b000, 0b0000000),
    "sub": (0b000, 0b0100000),
    "sll": (0b001, 0b0000000),
    "slt": (0b010, 0b0000000),
    "sltu": (0b011, 0b0000000),
    "xor": (0b100, 0b0000000),
    "srl": (0b101, 0b0000000),
    "or": (0b110, 0b0000000),
    "and": (0b111, 0b0000000),
}

def i_type_instruction(rd, rs1, imm, instruction):
    if imm >= 0:
        imm = format(imm & ((1 << 12) - 1), '012b')
    else: 
        imm = format(-imm & ((1 << 12) - 1), '012b')
        inverted = ''.join('1' if bit == '0' else '0' for bit in imm)
        twos_comp = (bin(int(inverted, 2) + 1))
        imm = twos_comp

    opcode, funct3 = i_type_opcode_funct3_mapping[instruction]
    return format((int(imm,2) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode, '032b')

i_type_opcode_funct3_mapping = {
    "lw": (0b0000011, 0b010),
    "addi": (0b0010011, 0b000),
    "sltiu": (0b0010011, 0b011),
    "jalr": (0b1100111, 0b000),
}

def s_type_instruction(rs1, rs2, imm):
    opcode = 0b0100011
    funct3 = 0b010
    if imm >= 0:
        imm = format(imm & ((1 << 12) - 1), '012b')
    else:
        imm = format(-imm & ((1 << 12) - 1), '012b')
        inverted = ''.join('1' if bit == '0' else '0' for bit in imm)
        twos_comp = bin(int(inverted, 2) + 1)
        imm = twos_comp
    imm = int(imm,2)
    imm3 = imm & 0b11111
    imm5 = (imm >> 5) & 0b1111111
    return format((imm5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm3 << 7) | opcode, '032b')

def b_type_instruction(rs1, rs2, imm, instruction):
    opcode = 0b1100011
    funct3 = b_type_funct3_mapping[instruction]
    if imm >= 0:
        imm = format(imm & ((1 << 12) - 1), '012b')
    else:
        imm = format(-imm & ((1 << 12) - 1), '012b')
        inverted = ''.join('1' if bit == '0' else '0' for bit in imm)
        twos_comp = bin(int(inverted, 2) + 1)
        imm = twos_comp   
    imm = int(imm,2)
    imm12 = (imm >> 11) & 0b1
    imm10_5 = (imm >> 5) & 0b111111
    imm4_1 = (imm >> 1) & 0b1111
    imm11 = (imm >> 10) & 0b1

    return format((imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4_1 << 8) | (imm11 << 7) | opcode, '032b')
b_type_funct3_mapping = {
    "beq": 0b000,
    "bne": 0b001,
    "blt": 0b100,
    "bge": 0b101,
    "bltu": 0b110,
    "bgeu": 0b111,
}

def u_type_instruction(rd, imm, instruction):
    if imm >= 0:
        imm = format(imm & ((1 << 20) - 1), '020b')
    else:
        imm = format(-imm & ((1 << 20) - 1), '020b')
        inverted = ''.join('1' if bit == '0' else '0' for bit in imm)
        twos_comp = bin(int(inverted, 2) + 1)
        imm = twos_comp
    
    opcode = u_type_opcode_mapping[instruction]
    return format((int(imm,2) << 12) | (rd << 7) | opcode, '032b')

u_type_opcode_mapping = {
    "lui": 0b0110111,
    "auipc": 0b0010111,
}

def j_type_instruction(rd, imm):
    if imm >= 0:
        imm = format(imm & ((1 << 21) - 1), '021b')
    else:
        imm = format(-imm & ((1 << 21) - 1), '021b')
        inverted = ''.join('1' if bit == '0' else '0' for bit in imm)
        twos_comp = bin(int(inverted, 2) + 1)
        imm = twos_comp
    imm = int(imm,2)
    imm20 = (imm >> 20) & 0b1
    imm10_1 = (imm >> 1) & 0b1111111111
    imm11 = (imm >> 11) & 0b1
    imm19_12 = (imm >> 12) & 0b1111111

    opcode = 0b1101111
    return format((imm20 << 31) | (imm10_1 << 21) | (imm11 << 20) | (imm19_12 << 12) | (rd << 7) | opcode, '032b')


def process_assembly(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        contents = file.readlines()

    processed_contents = [line for line in contents]
    print_list = []


    for line in processed_contents: 
        b_line = line.strip().split()
        instruction = b_line[0]
        
        if instruction in r_type_funct3_funct7_mapping:
            b_line_1 = b_line[1].split(',')
            rd = register_numbers[b_line_1[0]]
            rs1 = register_numbers[b_line_1[1]]
            rs2 = register_numbers[b_line_1[2]]
            print_list.append(r_type_instruction(rd, rs1, rs2, instruction))
        
        elif instruction in i_type_opcode_funct3_mapping:
            b_line_1 = b_line[1].split(',')
            rd = register_numbers[b_line_1[0]]
            if instruction == "lw":
                imm_rs1 = b_line_1[1]
                imm = int(imm_rs1[:imm_rs1.find('(')])
                rs1 = register_numbers[imm_rs1[imm_rs1.find('(')+1:-1]]
            else:
                rs1 = register_numbers[b_line_1[1]]
                imm = int(b_line_1[2])
            print_list.append(i_type_instruction(rd, rs1, imm, instruction))

        elif instruction == "sw":
            b_line_1 = b_line[1].split(',')
            rs2 = register_numbers[b_line_1[0]]
            imm_rs1 = b_line_1[1]
            imm = int(imm_rs1[:imm_rs1.find('(')])
            rs1 = register_numbers[imm_rs1[imm_rs1.find('(')+1:-1]]
            print_list.append(s_type_instruction(rs1, rs2, imm))

        elif instruction in b_type_funct3_mapping:
            b_line_1 = b_line[1].split(',')
            rs1 = register_numbers[b_line_1[0]]
            rs2 = register_numbers[b_line_1[1]]
            imm = int(b_line_1[2])
            print_list.append(b_type_instruction(rs1, rs2, imm, instruction))

        elif instruction in u_type_opcode_mapping:
            b_line_1 = b_line[1].split(',')
            rd = register_numbers[b_line_1[0]]
            imm = int(b_line_1[1])
            print_list.append(u_type_instruction(rd, imm, instruction))

        elif instruction == "jal":
            b_line_1 = b_line[1].split(',')
            rd = register_numbers[b_line_1[0]]
            imm = int(b_line_1[1])
            print_list.append(j_type_instruction(rd, imm))

    with open(output_file_path, 'a') as output:
        for item in print_list:
            output.write(str(item) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Assembler for converting assembly code to machine code")
    parser.add_argument("input_file", help="Path to the input assembly code file")
    parser.add_argument("output_file", help="Path to the output machine code file")
    args = parser.parse_args()

    process_assembly(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
