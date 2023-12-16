import numpy as np

root_file = "database/"

class Instruction:
    name = ""
    next_stage = ""

def read_file(file):
    instructions = []
    f = open(f"{root_file}/{file}", "r")
    lines = f.readlines()
    for line in lines:
        instructions.append(line)
    f.close() 
    return instructions

def IF(instruction):
    '''
    lw $3, 16($0) 
    add $6, $4, $5
    '''
    if instruction == None:
        global currentInstructionNum
        raw = rawInstructions[currentInstructionNum]
        raw = raw.replace("\n", "")
        currentInstructionNum += 1
        instruction = Instruction()
        instruction.name = raw.split(" ")[0]
        instruction.next_stage = "ID"
        stageInstructions["IF"] = instruction
        pipReg["IF/ID"] = pipInfo(None, None, None, None, instruction.name, raw)

def ID(instruction):
    if instruction == None:
        return
    if instruction.name == "add":
        rs = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[1].split("$")[1])
        rd = int(pipReg['IF/ID'].rawInstruction.split(" ")[1].split("$")[1])
        offset = 0
    elif instruction.name == "sub":
        rs = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[1].split("$")[1])
        rd = int(pipReg['IF/ID'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        offset = 0
    elif instruction.name == "lw":
        rs = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("(")[1].split("$")[1].split(")")[0])
        rt = int(pipReg['IF/ID'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        rd = 0
        offset = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("(")[0])
    elif instruction.name == "sw":
        rs = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("(")[1].split("$")[1].split(")")[0])
        rt = int(pipReg['IF/ID'].rawInstruction.split(" ")[1].split("$")[1])
        rd = 0
        offset = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("(")[0])
    elif instruction.name == "beq":
        rs = int(pipReg['IF/ID'].rawInstruction.split(" ")[1].split("$")[1])
        rt = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rd = 0
        offset = int(pipReg['IF/ID'].rawInstruction.split(" ")[2].split(",")[1])
    else:
        raise Exception("Unknown instruction name")
    instruction.next_stage = "EX"
    stageInstructions["ID"] = instruction
    pipReg["ID/EX"] = pipInfo(rs, rt, rd, offset, instruction.name)

def EX(instruction):
    pass

def MEM(instruction:Instruction):
    if instruction == None:
        return
    
    if pipReg["EX/MEM"].siganl['M'][2] == "1": #sw
        mem[ int(pipReg["EX/MEM"].address) ] = reg[ int(pipReg["EX/MEM"].rt) ]
    elif pipReg["EX/MEM"].siganl['M'][1] == "1": #lw
        loadWord = mem[ int(pipReg["EX/MEM"].address) ]
        
    pipReg["MEM/WB"] = pipReg["EX/MEM"]
    pipReg["MEM/WB"].loadword = loadWord
    instruction.next_stage = "WB"

def WB(instruction:Instruction):
    if instruction == None:
        return
    result = pipReg['MEM/WB'].ALU
    # ALU 接

    if instruction.name in ['add', 'sub', 'lw']:
        rd = pipReg['MEM/WB'].rd
        reg[rd] = result
    
    elif instruction.name == 'beq':
        pass
    else:
        raise Exception("Unknown instruction name")
    instruction.next_stage = None
    stageInstructions["WB"] = None

reg = np.ones(32)
reg[0] = 0
mem = np.ones(32)

class pipInfo:
    def __init__(self, rs, rt, rd, offset, intrsuction_name, rawInstruction = None):
        signals = {
            'lw' : {
                'EX': '01',
                'M' : '010',
                'WB' : '11'
            },
            'sw' : {
                'EX': 'X1',
                'M' : '001',
                'WB' : '0X'
            },
            'beq' : {
                'EX': 'X0',
                'M' : '100',
                'WB' : '0X'
            },
            'add' : {
                'EX': '10',
                'M' : '000',
                'WB' : '10'
            },
            'sub' : {
                'EX': '10',
                'M' : '000',
                'WB' : '10'
            },
        }
        self.rs = rs,
        self.rt = rt,
        self.rd = rd,
        self.offset = offset
        self.siganl = signals[intrsuction_name]
        self.rawInstruction = rawInstruction

pipReg = {
    'IF/ID' : None,
    'ID/EX' : None,
    'EX/MEM' : None,
    'MEM/WB' : None,
}

# 原始指令字串list
rawInstructions = read_file("ex1.txt")
# 在stage中的指令
stageInstructions = {
    "IF": None,
    "ID": None,
    "EX": None,
    "MEM": None,
    "WB": None
}
currentInstructionNum = 0
while currentInstructionNum < len(rawInstructions) or stageInstructions != {}:
    IF(stageInstructions["IF"])
    ID(stageInstructions["ID"])
    EX(stageInstructions["EX"])
    MEM(stageInstructions["MEM"])
    WB(stageInstructions["WB"])

    stageInstructions2 = stageInstructions.copy()
    for stage in reversed(stageInstructions2):
        if stageInstructions[stage] == None:
            continue
        if stageInstructions[stage].next_stage == stage:
            break
        else:
            stageInstructions2[stageInstructions[stage].next_stage] = stageInstructions[stage]
    stageInstructions = stageInstructions2.copy()

