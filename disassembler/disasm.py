import sys

instructions = {
    0b000101:       {"name": "B",    "type": "B", "output": "B {address}"},
    0b100101:       {"name": "BL",   "type": "B", "output": "BL {address}"},
    0b10110101:     {"name": "CBNZ", "type": "CB", "output": "CBNZ X{rt}, {address}"},
    0b10110100:     {"name": "CBZ",  "type": "CB", "output": "CBZ X{rt}, {address}"},
    0b01010100:     {"name": "Bcond","type": "CB", "output": "B.{rt} {address}"},
    0b1101001000:   {"name": "EORI", "type": "I", "output": "EORI X{rd}, X{rn}, #{imm}"},
    0b1101000100:   {"name": "SUBI", "type": "I", "output": "SUBI X{rd}, X{rn}, #{imm}"},
    0b1111000100:   {"name": "SUBIS","type": "I", "output": "SUBIS X{rd}, X{rn}, #{imm}"},
    0b1011001000:   {"name": "ORRI", "type": "I", "output": "ORRI X{rd}, X{rn}, #{imm}"},
    0b1001000100:   {"name": "ADDI", "type": "I", "output": "ADDI X{rd}, X{rn}, #{imm}"},
    0b1001001000:   {"name": "ANDI", "type": "I", "output": "ANDI X{rd}, X{rn}, #{imm}"},
    0b11010110000:  {"name": "BR",   "type": "R", "output": "BR X{rn}"},
    0b10001010000:  {"name": "AND",  "type": "R", "output": "AND X{rd}, X{rn}, X{rm}"},
    0b11111111100:  {"name": "PRNL", "type": "R", "output": "PRNL"},
    0b10001011000:  {"name": "ADD",  "type": "R", "output": "ADD X{rd}, X{rn}, X{rm}"},
    0b11111111110:  {"name": "DUMP", "type": "R", "output": "DUMP"},
    0b11001010000:  {"name": "EOR",  "type": "R", "output": "EOR X{rd}, X{rn}, X{rm}"},
    0b11111111111:  {"name": "HALT", "type": "R", "output": "HALT"},
    0b11010011011:  {"name": "LSL",  "type": "R", "output": "LSL X{rd}, X{rn}, #{shamt}"},
    0b11010011010:  {"name": "LSR",  "type": "R", "output": "LSR X{rd}, X{rn}, #{shamt}"},
    0b10011011000:  {"name": "MUL",  "type": "R", "output": "MUL X{rd}, X{rn}, X{rm}"},
    0b10101010000:  {"name": "ORR",  "type": "R", "output": "ORR X{rd}, X{rn}, X{rm}"},
    0b11111111101:  {"name": "PRNT", "type": "R", "output": "PRNT X{rd}"},
    0b11001011000:  {"name": "SUB",  "type": "R", "output": "SUB X{rd}, X{rn}, X{rm}"},
    0b11101011000:  {"name": "SUBS", "type": "R", "output": "SUBS X{rd}, X{rn}, X{rm}"},
    0b11111000010:  {"name": "LDUR", "type": "D", "output": "LDUR X{rd}, [X{rn}, #{address}]"},
    0b11111000000:  {"name": "STUR", "type": "D", "output": "STUR X{rd}, [X{rn}, #{address}]"},
}

cond_codes = {
    0b0000: "EQ",
    0b0001: "NE",
    0b0010: "HS",
    0b0011: "LO",
    0b0100: "MI",
    0b0101: "PL",
    0b0110: "VS",
    0b0111: "VC",
    0b1000: "HI",
    0b1001: "LS",
    0b1010: "GE",
    0b1011: "LT",
    0b1100: "GT",
    0b1101: "LE",
}

instruction_types = {
    "R":{
        "iso": [[21,0x7FF], [16,0x1F], [10,0x3F], [5,0x1F], [None,0x1F]],
        "fields": ["opcode", "rm", "shamt", "rn", "rd"],
    },

    "D":{
        "iso": [[21,0x7FF], [12,0x1FF], [10,0x3], [5,0x1F], [None,0x1F]],
        "fields": ["opcode", "address", "op", "rn", "rd"],
    },

    "I":{
        "iso": [[22,0x3FF], [10,0xFFF], [5,0x1F], [None,0x1F]],
        "fields": ["opcode", "imm", "rn", "rd"],
    },

    "B":{
        "iso": [[26,0x3F], [None,0x3FFFFFF]],
        "fields": ["opcode", "address"],
    },

    "CB":{
        "iso": [[24,0xFF], [5,0x7FFFF], [None,0x1F]],
        "fields": ["opcode", "address", "rt"],
    }
}

labels = {
} # dynamic labels for branch addressing

output_arr = []


class Emulator:
    def __init__(self, file_bytes):
        '''initialize registers, PC, and file path'''
        self.instructions = file_bytes
        self.pc = 0
        self.running = True

    def fetch(self, pc):
        '''Fetch the instruction at the PC'''
        if pc >= len(self.instructions):
            self.running = False
            return None
        inst = self.instructions[pc:pc+4]
        bitstring = int.from_bytes(inst, byteorder='big')
        return bitstring

    def two_complement(self, input, bits):
        '''Converts a number to two's complement'''
        if input & (1 << (bits - 1)):
            input -= 1 << bits
        return input

    def simple_parse(self, inst, instruction):
        '''parse the instruction based on the type of instruction'''
        data = ""
        data += instruction["output"] + " "

        self.pc += 4

        masks = instruction_types[instruction["type"]]["iso"]
        fields = instruction_types[instruction["type"]]["fields"]
        outs = []
        count = 0

        # calculate necessary fields for the specific instruction
        for (shift, mask) in masks:
            if fields[count] in instruction["output"]:
                if shift == None:
                    field = inst & mask
                    outs.append(field)
                    count += 1
                else:
                    field = (inst >> shift) & mask
                    outs.append(field)
                    count += 1
            else:
                count += 1


        # Format the output
        # output for branching will be different, need to insert label, otherwise just format output
        if instruction["type"] == "B":
            outs[0] = self.two_complement(outs[0], 26)
            # skip PC-relative addressing for BL instruction
            if instruction["name"] == "BL":
                if outs[0] not in labels:
                    labels[outs[0]] = f"label_{len(labels)}"
                data = data.format(address=labels[outs[0]])
                output_arr.append(data)
                return 0


            if outs[0] < 0:
                outs[0] = outs[0]*4-self.pc  
            else:
                outs[0] = outs[0]*4+self.pc
            if outs[0] not in labels:
                labels[outs[0]] = f"label_{len(labels)}"
            data = data.format(address=labels[outs[0]])
            output_arr.append(data)
            return 0
        elif instruction["type"] == "CB":
            outs[0] = self.two_complement(outs[0], 19)
            if outs[0] < 0:
                outs[0] = outs[0]*4-self.pc  
            else:
                outs[0] = outs[0]*4+self.pc
            if instruction["name"] == "Bcond":
                if outs[0] not in labels:
                    labels[outs[0]] = f"label_{len(labels)}"
                data = data.format(rt=cond_codes[int(outs[1])], address=labels[outs[0]])
                output_arr.append(data)
                return 0
            else:
                if outs[0] not in labels:
                    labels[outs[0]] = f"label_{len(labels)}"
                data = data.format(rt=outs[1], address=labels[outs[0]])
                output_arr.append(data)
                return 0
        elif instruction["type"] == "R":
            if instruction["name"] == "PRNL" or instruction["name"] == "DUMP" or instruction["name"] == "HALT":
                pass
            elif instruction["name"] == "PRNT":
                data = data.format(rd=outs[0])
                output_arr.append(data)
                return 0
            elif instruction["name"] == "BR":
                data = data.format(rn=outs[0])
                output_arr.append(data)
                return 0
            elif instruction["name"] == "LSL" or instruction["name"] == "LSR":
                outs[0] = self.two_complement(outs[0], 6)
                data = data.format(rd=outs[2], rn=outs[1], shamt=outs[0])
                output_arr.append(data)
                return 0
            else:
                data = data.format(rd=outs[2], rn=outs[1], rm=outs[0])
                output_arr.append(data)
                return 0
        elif instruction["type"] == "D":
            outs[0] = self.two_complement(outs[0], 9)
            data = data.format(rd=outs[2], rn=outs[1], address=outs[0])
            output_arr.append(data)
            return 0
        elif instruction["type"] == "I":
            outs[0] = self.two_complement(outs[0], 12)
            data = data.format(rd=outs[2], rn=outs[1], imm=outs[0])
            output_arr.append(data)
            return 0


    def decode(self, inst):
        '''Decode the instruction'''
        if inst == None:
            return 0
        opcheck = False
        
        opcode = (inst >> 26) & 0x3f # 6 bit opcode
        if opcode in instructions:
            opcheck = True
            instruction = instructions[opcode]
            self.simple_parse(inst, instruction)
            return instruction
        
        opcode = (inst >> 24) & 0xff # 8 bit opcode
        if opcode in instructions and opcheck == False:
            opcheck = True
            instruction = instructions[opcode]
            self.simple_parse(inst, instruction)
            return instruction

        opcode = (inst >> 22) & 0x3ff # 10 bit opcode
        if opcode in instructions and opcheck == False:
            opcheck = True
            instruction = instructions[opcode]
            self.simple_parse(inst, instruction)
            return instruction

        opcode = (inst >> 21) & 0x7ff # 11 bit opcode
        if opcode in instructions and opcheck == False:
            opcheck = True
            instruction = instructions[opcode]
            self.simple_parse(inst, instruction)
            return instruction
        else:
            print(f'Instruction Not Supported: {opcode:b}')
            self.pc += 4
        return 0

    def insert_labels(self):
        '''fix the output to match legv8asm syntax'''
        # key is the address, value is the label_# to insert
        for label in labels:
            output_arr.insert(label >> 2, labels[label] + ":")


    
    def run(self):
        '''loop to iterate over instructions'''
        while self.running:
            bitstring = self.fetch(self.pc) # Fetch the instruction
            self.decode(bitstring) # Decode the instruction

        self.insert_labels()

        print("Legv8asm Instructions:")
        for i in output_arr:
            print(i)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python disasm.py <machine_code_file>')
        sys.exit(1)

    filename = sys.argv[1]
    # run the emulator with the machine code file as byte stream
    with open(filename, 'rb') as f:
        data = f.read()
        emulator = Emulator(data)
        emulator.run()

