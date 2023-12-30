import numpy as np

root_file = "database/"

class Instruction:
    name = ""
    next_stage = ""
    next_stage = ""

def read_file(file):
    instructions = []
    f = open(f"{root_file}/{file}", "r")
    lines = f.readlines()
    for line in lines:
        instructions.append(line)
    f.close() 
    return instructions

TWO_CYCLE_BEQ = False
ONE_CYCLE_BEQ = False
ONE_TEMP_CYCLE = -1
TWO_TEMP_CYCLE = -1

def check_beq_hazard(rs, rt,cycle):
    global ONE_CYCLE_BEQ,TWO_CYCLE_BEQ,ONE_TEMP_CYCLE,TWO_TEMP_CYCLE
    #PY 蝦改
    if ONE_CYCLE_BEQ == True and cycle - ONE_TEMP_CYCLE >= 1:
        ONE_CYCLE_BEQ = False
    if TWO_CYCLE_BEQ == True and cycle - TWO_TEMP_CYCLE >= 2:
        TWO_CYCLE_BEQ = False
    elif TWO_CYCLE_BEQ == True and cycle - TWO_TEMP_CYCLE >= 1:
        stageInstructions["ID"].next_stage = "ID"
        flag['now'] = "ID"
        return True
    # 抓到NONE
    if PipelineRegister.EX_MEM['input'].signal['WB'][0] == "2" or PipelineRegister.EX_MEM['input'].signal['WB'][0] == "2":
        if TWO_CYCLE_BEQ == True and cycle - TWO_TEMP_CYCLE == 1:
            stageInstructions["ID"].next_stage = "ID"
            flag['now'] = "ID"
            return True
        elif PipelineRegister.MEM_WB['input'].signal["EX"][0] == "1":
            if PipelineRegister.MEM_WB['input'].rd[0] == rs or PipelineRegister.EX_MEM['input'].rd[0] == rt:
                print("BEQ hazard:forwarding")
                flag['forward'] = "EX_MEM_beq"
                return True   
        return False

        # Need 1 stall cycle lw 接 R_type 
    if ONE_CYCLE_BEQ == False and TWO_CYCLE_BEQ == False:
        if PipelineRegister.MEM_WB['input'].signal['M'][1] == "1" and PipelineRegister.EX_MEM['input'].signal["EX"][0] == "1":
            if PipelineRegister.IF_ID['input'].signal["M"][0] == "1" :
                if PipelineRegister.IF_ID['input'].rt[0] == rs or PipelineRegister.IF_ID['input'].rt[0] == rt:
                    print("BEQ hazard")
                    flag['now'] = "ID"
                    stageInstructions["ID"].next_stage = "ID"
                    ONE_CYCLE_BEQ = True
                    ONE_TEMP_CYCLE = cycle
                    return True
        # Need 2 stall cycle 連續 lw lw 
        elif PipelineRegister.EX_MEM['input'].signal["M"][1] == "1" and PipelineRegister.IF_ID['input'].signal["M"][0] == "1":
            if PipelineRegister.IF_ID['input'].signal["M"][0] == "1" :
                if PipelineRegister.ID_EX['input'].rt[0] == rs or PipelineRegister.ID_EX['input'].rt[0] == rt:
                    print("BEQ hazard")
                    flag['now'] = "ID"
                    stageInstructions["ID"].next_stage = "ID"
                    TWO_CYCLE_BEQ = True
                    TWO_TEMP_CYCLE = cycle
                    return True
        # Need 1 stall cycle 直接 R_type
        elif PipelineRegister.EX_MEM['input'].signal["EX"][0] == "1":
            print(PipelineRegister.IF_ID['input'].rawInstruction)
            if PipelineRegister.IF_ID['input'].signal["M"][0] == "1" :
                if PipelineRegister.EX_MEM['input'].rd[0] == rs or PipelineRegister.EX_MEM['input'].rd[0] == rt:
                    print("BEQ hazard")
                    flag['now'] = "ID"
                    stageInstructions["ID"].next_stage = "ID"
                    ONE_CYCLE_BEQ = True
                    # PY 蝦改
                    ONE_TEMP_CYCLE = cycle
                    return True
        elif PipelineRegister.MEM_WB['input'].signal["EX"][0] == "1":
            if PipelineRegister.MEM_WB['input'].rd[0] == rs or PipelineRegister.EX_MEM['input'].rd[0] == rt:
                print("BEQ hazard:forwarding")
                flag['forward'] = "EX_MEM_beq"
                return True   
    # #PY 蝦改
    # if ONE_CYCLE_BEQ == True and cycle - ONE_TEMP_CYCLE >= 1:
    #     ONE_CYCLE_BEQ = False
    # 存在兩次STALL
    
    return False

def check_ex_hazard(rs,rt,rd):
    if PipelineRegister.EX_MEM['input'].rt[0] == -1 or rt == -1 and PipelineRegister.EX_MEM['input'].rt[0] == -1 or rt == -1 : 
        print("false")
        return False
    
    if PipelineRegister.EX_MEM['input'] is not None:
        if (PipelineRegister.EX_MEM['input'].signal['WB'][0] == "1" and
            (PipelineRegister.EX_MEM['input'].signal["M"][1] == "1" or
            PipelineRegister.EX_MEM['input'].signal["M"][2] == "1") and
            PipelineRegister.EX_MEM['input'].rt[0] != 0 and
            (PipelineRegister.EX_MEM['input'].rt[0] == rs or
            PipelineRegister.EX_MEM['input'].rt[0] == rt)):
            print("EX hazard:stall")
            stageInstructions["ID"].next_stage = "ID"
            flag['now'] = "ID" #需要stall
            return True
        elif(PipelineRegister.EX_MEM['input'].signal['WB'][0] == "1" and
            (PipelineRegister.EX_MEM['input'].signal["EX"][0] == "1") and
            PipelineRegister.EX_MEM['input'].rd[0] != 0): #但不用stall，做forwarding
            if PipelineRegister.EX_MEM['input'].rd[0] == rs:
                flag['forward'] = "EX_MEM"
                print("EX hazard:forwarding")
                return True
            if PipelineRegister.EX_MEM['input'].rd[0] == rt:
                flag['forward'] = "EX_MEM"
                print("EX hazard:forwarding")
                return True 
            return False
        else:
            return False
    else:
        return False

def check_mem_hazard(rs,rt,rd):
    if PipelineRegister.MEM_WB['input'].rt[0] == -1 or rt == -1 and PipelineRegister.MEM_WB['input'].rt[0] == -1 or rt == -1 : 
        print("false")
        return False
    if PipelineRegister.MEM_WB['input'] is not None:
        if (PipelineRegister.MEM_WB['input'].signal['WB'][0] == "1" and #MEM/WB.RegWrite = TRUE
            PipelineRegister.MEM_WB['input'].rt[0] != 0): #MEM/WB.RegisterRd != 0
            if stageInstructions["MEM"] != None: 
                if stageInstructions["MEM"].name == "add" or stageInstructions["MEM"].name == "sub" : #如果是R-format
                    # print("-----------------------------------------------Rformat")
                    if(PipelineRegister.MEM_WB['input'].rd[0] != 0 and
                        (PipelineRegister.MEM_WB['input'].rd[0] == rs or
                        PipelineRegister.MEM_WB['input'].rd[0] == rt)):
                        print("MEM hazard")
                        return True
                elif stageInstructions["MEM"].name == "lw" or stageInstructions["MEM"].name == "sw" : #如果是I-format
                    if(PipelineRegister.MEM_WB['input'].rt[0] != 0 and
                        (PipelineRegister.MEM_WB['input'].rt[0] == rs or
                        PipelineRegister.MEM_WB['input'].rt[0] == rt)):
                        print("MEM hazard")
                        return True
    return False

def IF(instruction):
    
    '''
    lw $3, 16($0) 
    add $6, $4, $5
    '''
        
    global currentInstructionNum,cycle
    

    if currentInstructionNum >= len(rawInstructions):
        PipelineRegister.IF_ID['input'] = pipInfo(-1,-1,-1,0,'None')
        print("IF stage: None")

        return

    raw = rawInstructions[currentInstructionNum]
    raw = raw.replace("\n", "")
    instruction = Instruction()
    instruction.name = raw.split(" ")[0]

    print('IF stage ',rawInstructions[currentInstructionNum],cycle)
    
    instruction.next_stage = "ID"
    stageInstructions["IF"] = instruction
    PipelineRegister.IF_ID['input'] = pipInfo(None, None, None, None, instruction.name, rawInstruction=raw,loadword=None, instruction_num=currentInstructionNum)

def ID(instruction:Instruction):
    global currentInstructionNum,cycle, flag
    next_stage = "EX"
    if instruction == None or PipelineRegister.IF_ID['output'].rawInstruction == None:
        print("ID stage: None")
        PipelineRegister.ID_EX['input'] = pipInfo(-1,-1,-1,0,'None')
        return
    print("ID Stage",PipelineRegister.IF_ID['output'].rawInstruction,cycle)
    isBranch = False
    if instruction.name == "add":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[3].split("$")[1])
        rd = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[1].split("$")[1].split(",")[0])
        offset = 0
    elif instruction.name == "sub":
        rs = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[2].split(",")[0].split("$")[1])
        rt = int(PipelineRegister.IF_ID['output'].rawInstruction.split(" ")[3].split("$")[1])
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
        
       
    else:
        raise Exception("Unknown instruction name")
    

    
    if check_beq_hazard(rs,rt,cycle):
        if flag['now'] == 'ID':
            next_stage = "ID"
            return
    if check_ex_hazard(rs,rt,rd):
        # print("ID return")
        if flag['now'] == 'ID':
            return
        elif flag['forward'] == "MEM":
            pass
    elif check_mem_hazard(rs,rt,rd):
        pass #yet
    
    if(instruction.name == "beq"):
        if flag['forward'] == "EX_MEM_beq":
            
            print("PipelineRegister.EX_MEM['output'].rd",PipelineRegister.EX_MEM['output'].rd[0])
            if rs == PipelineRegister.EX_MEM['output'].rd[0]:
                rs_reg = PipelineRegister.EX_MEM['output'].EX_result
                rt_reg = reg[rt]
            if rt == PipelineRegister.EX_MEM['output'].rd[0]:
                rt_reg = PipelineRegister.EX_MEM['output'].EX_result
                rs_reg = reg[rs]
            flag['forward'] = ""
        else:
            rs_reg = reg[rs]
            rt_reg = reg[rt]
        if rs_reg == rt_reg:
            isBranch = True
    instruction.next_stage = next_stage
    PipelineRegister.ID_EX['input'] = pipInfo(rs, rt, rd, offset, instruction.name,PipelineRegister.IF_ID['output'].rawInstruction,branch=isBranch, instruction_num=PipelineRegister.IF_ID['output'].instruction_num)
    stageInstructions["ID"] = instruction


def EX(instruction:Instruction):
    global cycle,currentInstructionNum
    if instruction == None:
        PipelineRegister.EX_MEM['input'] = pipInfo(-1,-1,-1,0,'None')
        print("EX stage: None")
        return

    
    print("EX stage",PipelineRegister.ID_EX['output'].rawInstruction,cycle)
    rs = PipelineRegister.ID_EX['output'].rs[0]
    rt = PipelineRegister.ID_EX['output'].rt[0]
    rs_reg = reg[PipelineRegister.ID_EX['output'].rs].copy()
    rt_reg = reg[PipelineRegister.ID_EX['output'].rt].copy()
    PipelineRegister.ID_EX['output'].rs_reg = rs_reg
    PipelineRegister.ID_EX['output'].rt_reg = rt_reg
    print("rsrt",rs_reg,rt_reg)
    if flag['forward'] == "EX_MEM":
        if PipelineRegister.ID_EX['output'].rs[0] == PipelineRegister.EX_MEM['output'].rd[0]:
            rs_reg = PipelineRegister.EX_MEM['output'].EX_result
        if PipelineRegister.ID_EX['output'].rt[0] == PipelineRegister.EX_MEM['output'].rd[0]:
            rt_reg = PipelineRegister.EX_MEM['output'].EX_result
        flag['forward'] = ""
    if instruction.name == "add":
        rd_reg = reg[PipelineRegister.ID_EX['output'].rd_reg].copy()
        rd_reg = rs_reg + rt_reg
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        # print("rs,rt,rd",rs,rt,rd)
        EX_result = rd_reg
        stageInstructions["EX"] = instruction
        
        PipelineRegister.ID_EX['output'].EX_result = EX_result
        PipelineRegister.ID_EX['output'].rd_reg = rd_reg
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
        
    elif instruction.name == "sub":
        rd_reg = reg[PipelineRegister.ID_EX['output'].rd].copy()
        rd_reg = rs_reg - rt_reg
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        EX_result = rd_reg
        # print("rs,rt,rd",rs,rt,rd)
        stageInstructions["EX"] = instruction
        PipelineRegister.ID_EX['output'].EX_result = EX_result
        PipelineRegister.ID_EX['output'].rd_reg = rd_reg
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
    elif instruction.name == "lw":
        baseAddress = rs_reg.copy()
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
        baseAddress = rs_reg.copy()
        offset = PipelineRegister.ID_EX['input'].offset
        address = baseAddress + offset/4
        #data = reg[pipReg["ID/EX"].rt].copy()
        instruction.next_stage = "MEM"
        stageInstructions["EX"] = instruction
        print("offset,address,baseAddress",offset,address,baseAddress)
        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
        PipelineRegister.EX_MEM['input'].address = address
    elif instruction.name == "beq":
        rd_reg = reg[PipelineRegister.ID_EX['output'].rd[0]].copy()
        offset = PipelineRegister.ID_EX['output'].offset
        instruction.next_stage = "MEM"
        if rs_reg == rt_reg:
            instruction.next_stage = "MEM"
            PipelineRegister.EX_MEM['input'] = pipInfo(rs, rt, -1, offset, instruction.name, PipelineRegister.ID_EX['output'].rawInstruction, rd_reg=rd_reg)
            stageInstructions["EX"] = instruction
        else:
            # 預測錯誤，抹掉捉錯的指令，再抓取正確位置的指令
            PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']
    else:
        raise Exception("Unknown instruction name")

def MEM(instruction:Instruction):
    global cycle,currentInstructionNum,return_value_flag
    if instruction == None:
        PipelineRegister.MEM_WB['input'] = pipInfo(-1,-1,-1,0,'None')
        print("MEM stage: None")
        return
    # if currentInstructionNum >= len(rawInstructions) + 5:
    #     stageInstructions["MEM"] = None
    #     currentInstructionNum += 1
    #     return
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
            PipelineRegister.MEM_WB['input'] = PipelineRegister.EX_MEM['output']
    else:
        loadWord = None
    PipelineRegister.MEM_WB['input'] = PipelineRegister.EX_MEM['output']
    PipelineRegister.MEM_WB['input'].loadword = loadWord
    instruction.next_stage = "WB"
    stageInstructions["MEM"] = instruction

def WB(instruction):
    global cycle
    if instruction == None:
        print("WB stage: None")
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
    def __init__(self, rs, rt, rd, offset, intrsuction_name, rawInstruction = None, address = None, branch = False, branch_address = None, loadword = None,EX_result = None, instruction_num = None, rs_reg = None, rt_reg = None, rd_reg = None):
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
            'None': {
                'EX': '22',
                'M' : '222',
                'WB' : '22'
            }
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
        self.instruction_num = instruction_num
        self.rs_reg = rs_reg
        self.rt_reg = rt_reg
        self.rd_reg = rd_reg

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
rawInstructions = read_file("ex8.txt")

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

def checkPiplineRegister_Rs_Rt_Rd(asked:dict):
    if asked['input'] != None:
        print("input--------")
        print("Rs",asked['input'].rs[0],"Rt",asked['input'].rt[0],"Rd",asked['input'].rd[0])
    if asked['output'] != None:
        print("output-------")
        print("Rs",asked['output'].rs[0],"Rt",asked['output'].rt[0],"Rd",asked['output'].rd[0])
        print("-------------")

re_stage = ["WB", "MEM", "EX", "ID", "IF"]
flag = {"now":"","forward":""}
while cycle == 1 or  stageInstructions["WB"] != None or stageInstructions["MEM"] != None or stageInstructions["EX"] != None or stageInstructions["ID"] != None or stageInstructions["IF"] != None: 
    WB(stageInstructions["WB"])
    MEM(stageInstructions["MEM"])
    EX(stageInstructions["EX"])
    ID(stageInstructions["ID"])
    IF(stageInstructions["IF"])
    if flag['now'] == "":
        print("PipelineRegister.ID_EX['input'].branch",PipelineRegister.ID_EX['input'].branch)
        if PipelineRegister.ID_EX is not None and PipelineRegister.ID_EX['input'] is not None and  PipelineRegister.ID_EX['input'].branch == True:
            
            currentInstructionNum = PipelineRegister.ID_EX['input'].instruction_num + PipelineRegister.ID_EX['input'].offset +1
            print(PipelineRegister.ID_EX['input'].instruction_num)
            print(PipelineRegister.ID_EX['input'].offset)
            stageInstructions["IF"] = None
            PipelineRegister.ID_EX['input'].branch = False
            print('jump')
        else:
            currentInstructionNum += 1
    stageInstructions2 = stageInstructions
    for stage in re_stage:
        if stageInstructions[stage] == None:
            if stage == "WB": continue
            stageInstructions2[re_stage[re_stage.index(stage)-1]] = None
        elif stageInstructions[stage].next_stage == stage:
            delete_stage_index = list(stageInstructions.keys()).index(stage) + 1
            # print("aaa",delete_stage_index)
            
            stageInstructions2[re_stage[delete_stage_index]] = None
            # ID IF 後面都保持原本的指令
            break
        else:
            stageInstructions2[stageInstructions[stage].next_stage] = stageInstructions[stage]
    stageInstructions2["IF"] = None #每次清除IF
    print("CYCLE",cycle)
    stageInstructions = stageInstructions2

    if flag["now"] == "ID":
        PipelineRegister.EX_MEM['output'] = PipelineRegister.EX_MEM['input']
        PipelineRegister.MEM_WB['output'] = PipelineRegister.MEM_WB['input']
    else:
        PipelineRegister.IF_ID['output'] = PipelineRegister.IF_ID['input']
        PipelineRegister.ID_EX['output'] = PipelineRegister.ID_EX['input']
        PipelineRegister.EX_MEM['output'] = PipelineRegister.EX_MEM['input']
        PipelineRegister.MEM_WB['output'] = PipelineRegister.MEM_WB['input']

    cycle += 1
    if cycle > 15:
        break
    # if flag['now'] != "":
    #     currentInstructionNum -= 1
    #     print("currentInstructionNum -= 1")
    flag['now'] = ""
    print("=====================================")


print("reg",reg)

print("mem",mem)