import sys
import os

def sext(imm):
    if imm[0] == '0':
        imm = '0' * (32 - len(imm)) + imm
    else:
        imm = '1' * (32 - len(imm)) + imm
    return imm

def dec_to_bin(num):
    num = int(num)
    if num >= 0:
        s = ''.join(str((num >> i) & 1) for i in range(31, -1, -1))
        s = '0' * (32 - len(s)) + s
    else:
        s = bin(num & (2**32 - 1))[2:]
    return s

def sgn_con(imm):
    if imm[0] == '1':
        flipped_bits = ''.join('1' if bit == '0' else '0' for bit in imm[1:])
        return -(int(flipped_bits, 2) + 1)
    else:
        return int(imm, 2)

def unsgn_con(imm):
    return int(imm, 2)

def beq(rs1, rs2, imm, pc):
    rs1, rs2, imm = [sext(val) for val in (rs1, rs2, imm)]
    rs1, rs2, imm = [sgn_con(val) for val in (rs1, rs2, imm)]
    pc += imm if rs1 == rs2 else 4
    return pc

def bne(rs1, rs2, imm, pc):
    rs1, rs2, imm = [sext(val) for val in (rs1, rs2, imm)]
    rs1, rs2, imm = [sgn_con(val) for val in (rs1, rs2, imm)]
    pc += imm if rs1 != rs2 else 4
    return pc

def bge(rs1, rs2, imm, pc):
    rs1, rs2, imm = [sext(val) for val in (rs1, rs2, imm)]
    rs1, rs2, imm = [sgn_con(val) for val in (rs1, rs2, imm)]
    pc += imm if rs1 >= rs2 else 4
    return pc

def blt(rs1, rs2, imm, pc):
    rs1, rs2, imm = [sext(val) for val in (rs1, rs2, imm)]
    rs1, rs2, imm = [sgn_con(val) for val in (rs1, rs2, imm)]
    pc += imm if rs1 < rs2 else 4
    return pc

def B(i, pc, r_dict):
    imm = i[0] + i[24] + i[1:7] + i[20:24]
    imm = sext(imm)
    func3 = i[-15:-12]
    rs1 = i[-20:-15]
    rs2 = i[-25:-20]
    operations = {
        "000": beq,
        "001": bne,
        "100": blt,
        "101": bge
    }
    for func_code, operation in operations.items():
        if func3 == func_code:
            pc = operation(r_dict[rs1], r_dict[rs2], imm, pc)
            break

    return pc

def add(rd, rs1, rs2, pc, r_dict):
    rs1 = sext(rs1)
    rs2 = sext(rs2)
    r_dict[rd] = dec_to_bin(rs1 + rs2)
    return pc + 4

def sub(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(sgn_con(rs1) - sgn_con(rs2))
    return pc + 4

def slt(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(1) if sgn_con(rs1) < sgn_con(rs2) else "0b0"
    return pc + 4

def sltu(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(1) if rs1 < rs2 else "0b0"
    return pc + 4

def xor(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(rs1 ^ rs2)
    return pc + 4

def sll(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(rs1 << int(rs2[-5:], 2))
    return pc + 4

def srl(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(rs1 >> int(rs2[-5:], 2))
    return pc + 4

def or_(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(rs1 | rs2)
    return pc + 4

def and_(rd, rs1, rs2, pc, r_dict):
    r_dict[rd] = dec_to_bin(rs1 & rs2)
    return pc + 4
def R(i, pc, r_dict):
    rd = i[-7:]
    rs1 = i[-20:-15]
    rs2 = i[-25:-20]
    funct3 = i[-15:-12]
    funct7 = i[:7]

    operations = {
        ("000", "0000000"): add,
        ("000", "0100000"): sub,
        ("010", "0000000"): slt,
        ("011", "0000000"): sltu,
        ("100", "0000000"): xor,
        ("001", "0000000"): sll,
        ("101", "0000000"): srl,
        ("110", "0000000"): or_,
        ("111", "0000000"): and_
    }

    for func_code, func_op in operations:
        if (funct3, funct7) == (func_code, func_op):
            pc = func_op(rd, r_dict[rs1], r_dict[rs2], pc, r_dict)
            break

    return pc

def lw(rd, rs1, imm, pc, r_dict, mem_dict):
    rs1 = sext(rs1)
    rs1 = sgn_con(rs1)
    imm = sgn_con(imm)
    r_dict[rd] = mem_dict[rs1 + imm]
    return pc + 4

def addi(rd, rs1, imm, pc, r_dict):
    rs1 = sext(rs1)
    rs1 = sgn_con(rs1)
    imm = sgn_con(imm)
    r_dict[rd] = dec_to_bin(rs1 + imm)
    return pc + 4

def jalr(rd, x6, imm, pc, r_dict):
    r_dict[rd] = dec_to_bin(pc + 4)
    x6 = sext(x6)
    x6 = sgn_con(x6)
    imm = sgn_con(imm)
    pc = dec_to_bin(x6 + imm)
    pc = pc[:-1] + "0"  # Adjusting PC format
    return pc
def I(i, pc, r_dict, mem_dict):
    imm = sext(i[:12])
    rd = i[-12:-7]
    rs1 = i[-20:-15]
    func3 = i[-15:-12]
    opcode = i[-7:]
    
    operations = {
        ("010", "0000011"): lambda: lw(rd, r_dict[rs1], imm, pc, r_dict, mem_dict),
        ("000", "0010011"): lambda: addi(rd, r_dict[rs1], imm, pc, r_dict),
        ("000", "1100111"): lambda: jalr(rd, r_dict[rs1], imm, pc, r_dict)
    }

    for (func3_val, opcode_val), operation in operations.items():
        if func3 == func3_val and opcode == opcode_val:
            pc = operation()
            break

    return pc

def S_sw(i, pc, r_dict, mem_dict):
    imm = sext(i[:-25] + i[-12:-7])
    rs1 = sext(i[-20:-15])
    rs2 = i[-25:-20]

    r_dict[rs2] = mem_dict[sgn_con(rs1 + imm)]
    return pc + 4

def lui(rd, imm, pc, r_dict):
    imm = sgn_con(imm)
    r_dict[rd] = dec_to_bin(pc + imm)
    return pc + 4

def aiupc(rd, imm, pc, r_dict):
    r_dict[rd] = imm
    return pc + 4

def U(i, pc, r_dict):
    imm = "000000000000" + i[:-12]
    rd = i[-12:-7]
    opcode = i[-7:]

    operations = {
        "0110111": lambda: lui(rd, imm, pc, r_dict),
        "0010111": lambda: aiupc(rd, imm, pc, r_dict)
    }

    for opcode_val, operation in operations.items():
        if opcode == opcode_val:
            pc = operation()
            break

    return pc

def J_jal(i, pc, r_dict):
    imm = sext(i[0] + i[13:21] + i[12] + i[1:11])
    rd = i[-12:-7]
    r_dict[rd] = dec_to_bin(pc + 4)
    pc += imm
    return pc

def simulator(r_dict, mem_dict, pc_dict):
    pc = 0
    while pc <= 252:
        inst = pc_dict[pc]
        opc = inst[-7:]
        
        operations = {
            "0110011": lambda: R(inst, pc, r_dict),
            "0000011": lambda: I(inst, pc, r_dict, mem_dict),
            "0010011": lambda: I(inst, pc, r_dict, mem_dict),
            "1100111": lambda: I(inst, pc, r_dict, mem_dict),
            "0100011": lambda: S_sw(inst, pc, r_dict, mem_dict),
            "1100011": lambda: B(inst, pc, r_dict),
            "0010111": lambda: U(inst, pc, r_dict),
            "0110111": lambda: U(inst, pc, r_dict),
            "1101111": lambda: J_jal(inst, pc, r_dict)
        }

        pc = operations[opc]()

        r_dict["program"] = "0b" + dec_to_bin(pc)
        
r_dict = {"program":"0b00000000000000000000000000000000", }
mem_dict = {}

if len(sys.argv) < 3:
    sys.exit("Input path and output path: required")

input = sys.argv[1]
output = sys.argv[2]

if not os.path.exists(input):
    sys.exit("Doesnt exist")

input_file = open(input, "r")
with open(input, "r") as input_file:
    x = input_file.readlines()
    pc_dict = {}
    pc = 0
    for line in x:
        pc_dict[pc] = line
        pc += 4

simulator(r_dict, mem_dict, pc_dict)

with open(output, "w") as output_file:
    for pc, inst in pc_dict.items():
        output_file.write(f"{pc}: {inst}\n")

sys.exit()
