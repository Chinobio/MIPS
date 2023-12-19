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



def check_ex_hazard():
    # print(PipelineRegister.EX_MEM['output'].rawInstruction)
    if (PipelineRegister.EX_MEM['output'] is not None and
        PipelineRegister.EX_MEM['output'].signal['WB'][0] == "1" and
        PipelineRegister.EX_MEM['output'].rawInstruction.split(" ")[0] == "lw" and
        PipelineRegister.EX_MEM['output'].rd != 0 and
        (PipelineRegister.EX_MEM['output'].rd == PipelineRegister.ID_EX['output'].rs or
         PipelineRegister.EX_MEM['output'].rd == PipelineRegister.ID_EX['output'].rt)):
        print("EX hazard")
        stageInstructions["ID"].next_stage = "ID"
        return True
    else:
        return False

def MEM_hazard(instruction, register_status):
    if instruction.name == "lw":
        rt = instruction.rt
        if register_status[rt] == "EX" or register_status[rt] == "MEM":
            return True
    return False

def IF(instruction):
    '''
    lw $3, 16($0) 
    add $6, $4, $5
    '''
    global currentInstructionNum,cycle,return_value_flag
    if currentInstructionNum >= len(rawInstructions):
        stageInstructions["IF"] = None
        currentInstructionNum += 1
        return

    raw = rawInstructions[currentInstructionNum]
    raw = raw.replace("\n", "")
    currentInstructionNum += 1
    instruction = Instruction()
    instruction.name = raw.split(" ")[0]
    # print('IF instruction name ',instruction.name)
    # if return_value_flag:
    #     return
    print('IF stage ',rawInstructions[currentInstructionNum - 1],cycle)
    
    instruction.next_stage = "ID"
    stageInstructions["IF"] = instruction
    PipelineRegister.IF_ID['input'] = pipInfo(None, None, None, None, instruction.name, rawInstruction=raw,loadword=None)
    # pipReg["IF/ID"] = pipInfo(None, None, None, None, instruction.name, rawInstruction=raw)
    # print('IF raw ',pipReg["IF/ID"].rawInstruction)
    # print('ID raw ',instruction.rawInstruction)
def ID(instruction):
    
    global currentInstructionNum,cycle
    if instruction == None:
        return
    if currentInstructionNum >= len(rawInstructions) + 1:
        currentInstructionNum += 1
        stageInstructions["ID"] = None
        return
    # print('ID instruction name ',instruction.name)
    print("ID Stage",PipelineRegister.IF_ID['output'].rawInstruction,cycle)
    
    if currentInstructionNum >= 3:
        flag = check_ex_hazard()
        if flag:
            return

    
    if instruction.name == "add":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[3].split("$")[1])
        rd = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        offset = 0
    elif instruction.name == "sub":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[1].split("$")[1])
        rd = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        offset = 0
    elif instruction.name == "lw":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split("$")[1].split(")")[0])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        rd = 0
        offset = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("(")[0])
    elif instruction.name == "sw":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split("$")[1].split(")")[0])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        # print("rs , rt",rs,rt)
        rd = 0
        offset = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("(")[0])
    elif instruction.name == "beq":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split("$")[1].split(",")[0])
        rd = 0
        offset = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[3])
        if rs == rt:
            instruction.next_stage = "EX"
            PipelineRegister.ID_EX['input'] = pipInfo(rs, rt, rd, offset, instruction.name, PipelineRegister.IF_ID['output'].rawInstruction)
            stageInstructions["ID"] = instruction
        else:    
            PipelineRegister.ID_EX['input'] = None
        
       
    else:
        raise Exception("Unknown instruction name")
    instruction.next_stage = "EX"
    PipelineRegister.ID_EX['input'] = pipInfo(rs, rt, rd, offset, instruction.name,PipelineRegister.IF_ID['output'].rawInstruction)
    stageInstructions["ID"] = instruction
    # pipReg["ID/EX"] = pipInfo(rs, rt, rd, offset, instruction.name)

def EX(instruction):
    global cycle,currentInstructionNum
    if instruction == None:
        return
    if currentInstructionNum >= len(rawInstructions) + 3:
        stageInstructions["EX"] = None
        currentInstructionNum += 1
        return
    
    print("EX stage",PipelineRegister.ID_EX['output'].rawInstruction,cycle)
    if instruction.name == "add":
        rs = reg[PipelineRegister.ID_EX['output'].rs].copy()
        rt = reg[PipelineRegister.ID_EX['output'].rt].copy()
        rd = reg[PipelineRegister.ID_EX['output'].rd].copy()
        rd = rs + rt
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        # print("rs,rt,rd",rs,rt,rd)
        EX_result = rd
        stageInstructions["EX"] = instruction
        
        PipelineRegister.ID_EX['output'].EX_result = EX_result
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
        
    elif instruction.name == "sub":
        rs = reg[PipelineRegister.ID_EX['output'].rs].copy()
        rt = reg[PipelineRegister.ID_EX['output'].rt].copy()
        rd = reg[PipelineRegister.ID_EX['output'].rd].copy()
        rd = rs - rt
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        # print("rs,rt,rd",rs,rt,rd)
        stageInstructions["EX"] = instruction
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
    elif instruction.name == "lw":
        baseAddress = reg[PipelineRegister.ID_EX['output'].rs].copy()
        offset = PipelineRegister.ID_EX['output'].offset
        address = baseAddress + offset/4
        #data = mem[address]
        instruction.next_stage = "MEM"
        stageInstructions["EX"] = instruction
        # print("offset,address,baseAddress",offset,address,baseAddress)
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
        # print(PipelineRegister.EX_MEM['input'].rawInstruction)
        PipelineRegister.EX_MEM['input'].address = address
    elif instruction.name == "sw":
        baseAddress = reg[PipelineRegister.ID_EX['input'].rs].copy()
        offset = PipelineRegister.ID_EX['input'].offset
        address = baseAddress + offset/4
        #data = reg[pipReg["ID/EX"].rt].copy()
        instruction.next_stage = "MEM"
        stageInstructions["EX"] = instruction
        print("offset,address,baseAddress",offset,address,baseAddress)
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
        PipelineRegister.EX_MEM['input'].address = address
    elif instruction.name == "beq":
        rs = reg[PipelineRegister.ID_EX['output'].rs].copy()
        rt = reg[PipelineRegister.ID_EX['output'].rt].copy()
        rd = reg[PipelineRegister.ID_EX['output'].rd].copy()
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        if rs == rt:
            instruction.next_stage = "MEM"
            PipelineRegister.EX_MEM['input'] = pipInfo(rs, rt, rd, offset, instruction.name, PipelineRegister.ID_EX['output'].rawInstruction)
            stageInstructions["EX"] = instruction
        else:
            # 預測錯誤，抹掉捉錯的指令，再抓取正確位置的指令
            currentInstructionNum = PipelineRegister.ID_EX['output'].branch_address
            PipelineRegister.ID_EX['output'].branch = False
            stageInstructions["EX"] = None
    else:
        raise Exception("Unknown instruction name")

def MEM(instruction:Instruction):
    global cycle,currentInstructionNum,return_value_flag
    if instruction == None:
        return
    if currentInstructionNum >= len(rawInstructions) + 5:
        stageInstructions["MEM"] = None
        currentInstructionNum += 1
        return
    print("MEM stage",PipelineRegister.EX_MEM['output'].rawInstruction,cycle)
    if PipelineRegister.EX_MEM['output'].signal['M'][2] == "1": #sw
        temp = PipelineRegister.EX_MEM['output'].rt[0]
        # print(PipelineRegister.EX_MEM['output'].rt)
        mem[ int(PipelineRegister.EX_MEM['output'].address) ] = reg[ int(temp) ]
        loadWord = None
    elif PipelineRegister.EX_MEM['output'].signal['M'][1] == "1": #lw
        # print(PipelineRegister.EX_MEM['output'].address)
        loadWord = mem[int(PipelineRegister.EX_MEM['output'].address) ]
    elif instruction.name == "beq":
        loadWord = None
        rs = tuple(PipelineRegister.EX_MEM['output'].rs)
        rt = tuple(PipelineRegister.EX_MEM['output'].rt)
        rd = tuple(PipelineRegister.EX_MEM['output'].rd)
        offset = PipelineRegister.EX_MEM['output'].offset
        if rs == rt:
            instruction.next_stage = "WB"
            PipelineRegister.MEM_WB['input'] = pipInfo(rs, rt, rd, offset, instruction.name, PipelineRegister.EX_MEM['output'].rawInstruction)
            stageInstructions["MEM"] = instruction
        else:
            # 預測錯誤，抹掉捉錯的指令，再抓取正確位置的指令
            currentInstructionNum = PipelineRegister.EX_MEM['output'].branch_address
            PipelineRegister.EX_MEM['output'].branch = False
            stageInstructions["MEM"] = None
    else:
        loadWord = None
    PipelineRegister.MEM_WB['input'] = PipelineRegister.EX_MEM['output']
    PipelineRegister.MEM_WB['input'].loadword = loadWord
    instruction.next_stage = "WB"
    stageInstructions["MEM"] = instruction

def WB(instruction):
    global cycle
    if instruction == None:
        return
    # print(PipelineRegister.MEM_WB['output'].loadword)
    print("WB stage",PipelineRegister.MEM_WB['output'].rawInstruction,cycle)
    result = PipelineRegister.MEM_WB['output'].loadword
    # ALU 接

    if instruction.name in ['lw']:
        rd = PipelineRegister.MEM_WB['output'].rt
        temp = rd[0]
        reg[temp] = result
        # print("reg[rd]",reg[temp])
    elif instruction.name in ['add', 'sub']:
        rd = PipelineRegister.MEM_WB['output'].EX_result
        reg[PipelineRegister.MEM_WB['output'].rd] = rd
    elif instruction.name == 'sw':
        address = int(PipelineRegister.MEM_WB['output'].address)
        rt = int(PipelineRegister.MEM_WB['output'].rt[0])
        mem[address] = reg[rt]
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
    def __init__(self, rs, rt, rd, offset, intrsuction_name, rawInstruction = None, address = None, branch = False, branch_address = None, loadword = None,EX_result = None):
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
        self.signal = signals[intrsuction_name]
        self.rawInstruction = rawInstruction
        self.address = address
        self.branch = branch
        self.branch_address = branch_address
        self.loadword = loadword
        self.EX_result = EX_result

pipReg = {
    'IF/ID' : None,
    'ID/EX' : None,
    'EX/MEM' : None,
    'MEM/WB' : None,
}

class PipelineRegister:
    IF_ID = {'input': None, 'output': None}
    ID_EX = {'input': None, 'output': None}
    EX_MEM = {'input': None, 'output': None}
    MEM_WB = {'input': None, 'output': None}

# 原始指令字串list
rawInstructions = read_file("ex2.txt")

# 在stage中的指令
stageInstructions = {
    "IF": None,
    "ID": None,
    "EX": None,
    "MEM": None,
    "WB": None
}

currentInstructionNum = 0
cycle = 1

qq = ["WB", "MEM", "EX", "ID", "IF"]
while currentInstructionNum < len(rawInstructions) or stageInstructions["WB"] != None or stageInstructions["MEM"] != None or stageInstructions["EX"] != None or stageInstructions["ID"] != None or stageInstructions["IF"] != None:
    if cycle == 5:
        a = 0
        # for i in stageInstructions.values():
        #     if i is not None:
        #         print(i.name)
        #     else:
        #         print("NONE")
    WB(stageInstructions["WB"])
    MEM(stageInstructions["MEM"])
    EX(stageInstructions["EX"])
    ID(stageInstructions["ID"])
    IF(stageInstructions["IF"])
    stageInstructions2 = stageInstructions
    for stage in ["WB", "MEM", "EX", "ID", "IF"]:
        if stageInstructions[stage] == None:
            continue
        if stageInstructions[stage].next_stage == stage:
            delete_stage_index = list(stageInstructions.keys()).index(stage) + 1
            # print("aaa",delete_stage_index)
            stageInstructions2
            stageInstructions2[qq[delete_stage_index]] = None
            break
        else:
            stageInstructions2[stageInstructions[stage].next_stage] = stageInstructions[stage]
    
    print("CYCLE",cycle)
    stageInstructions = stageInstructions2
    # if cycle == 4:
    #     for i in stageInstructions.values():
    #         if i is not None:
    #             print(i.name)
    #         else:
    #             print("NONE")
    # print(stageInstructions)
    PipelineRegister.IF_ID['output'] = PipelineRegister.IF_ID['input']
    PipelineRegister.ID_EX['output'] = PipelineRegister.ID_EX['input']
    PipelineRegister.EX_MEM['output'] = PipelineRegister.EX_MEM['input']
    PipelineRegister.MEM_WB['output'] = PipelineRegister.MEM_WB['input']
    if cycle == 4:
        print(PipelineRegister.IF_ID['output'].rawInstruction)
        print(PipelineRegister.ID_EX['output'].rawInstruction)
        print(PipelineRegister.EX_MEM['output'].rawInstruction)
        print(PipelineRegister.MEM_WB['output'].rawInstruction)
    cycle += 1
    print("=====================================")
    if stageInstructions["WB"] is None and stageInstructions["MEM"] is None and stageInstructions["EX"] is None and stageInstructions["ID"] is None and stageInstructions["IF"] is None:
        break

print("reg",reg)
print("mem",mem)