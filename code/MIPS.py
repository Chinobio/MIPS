import numpy as np

root_file = "database/"
file_name = "ex8.txt"

f = open(f"{root_file}/output.txt", "w")
f.close()

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

    
    return False

def check_ex_hazard(rs,rt,rd):
    if PipelineRegister.EX_MEM['input'].rt[0] == -1 or rt == -1 and PipelineRegister.EX_MEM['input'].rt[0] == -1 or rt == -1 : 
        
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

    print('IF stage ',rawInstructions[currentInstructionNum])
    
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
    print("ID Stage",PipelineRegister.IF_ID['output'].rawInstruction)
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

    
    print("EX stage",PipelineRegister.ID_EX['output'].rawInstruction)
    rs = PipelineRegister.ID_EX['output'].rs[0]
    rt = PipelineRegister.ID_EX['output'].rt[0]
    rs_reg = reg[PipelineRegister.ID_EX['output'].rs].copy()
    rt_reg = reg[PipelineRegister.ID_EX['output'].rt].copy()
    PipelineRegister.ID_EX['output'].rs_reg = rs_reg
    PipelineRegister.ID_EX['output'].rt_reg = rt_reg

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

        instruction.next_stage = "MEM"
        stageInstructions["EX"] = instruction

        PipelineRegister.EX_MEM['input'] = PipelineRegister.ID_EX['output']

        PipelineRegister.EX_MEM['input'].address = address
    elif instruction.name == "sw":
        baseAddress = rs_reg.copy()
        offset = PipelineRegister.ID_EX['input'].offset
        address = baseAddress + offset/4

        instruction.next_stage = "MEM"
        stageInstructions["EX"] = instruction
        
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

    print("MEM stage",PipelineRegister.EX_MEM['output'].rawInstruction)
    if PipelineRegister.EX_MEM['output'].signal['M'][2] == "1": #sw
        temp = PipelineRegister.EX_MEM['output'].rt[0]

        mem[ int(PipelineRegister.EX_MEM['output'].address) ] = reg[ int(temp) ]
        loadWord = None
    elif PipelineRegister.EX_MEM['output'].signal['M'][1] == "1": #lw

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

    print("WB stage",PipelineRegister.MEM_WB['output'].rawInstruction)
    result = PipelineRegister.MEM_WB['output'].loadword
    # ALU 接

    if instruction.name in ['lw']:
        rd = PipelineRegister.MEM_WB['output'].rt
        temp = rd[0]
        reg[temp] = result

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
rawInstructions = read_file(file_name)

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

def cycle_output():
    f = open(f"{root_file}/output.txt", "a+")
    f.write(f"cycle {cycle}\n")
    f.write(f"IF: {stageInstructions['IF']}\n")
    f.write(f"ID: {stageInstructions['ID']}\n")
    f.write(f"EX: {stageInstructions['EX']}\n")
    f.write(f"MEM: {stageInstructions['MEM']}\n")
    f.write(f"WB: {stageInstructions['WB']}\n")
    f.close()

re_stage = ["WB", "MEM", "EX", "ID", "IF"]
flag = {"now":"","forward":""}

while cycle == 1 or  stageInstructions["WB"] != None or stageInstructions["MEM"] != None or stageInstructions["EX"] != None or stageInstructions["ID"] != None or stageInstructions["IF"] != None: 
    print("cycle",cycle)
    WB(stageInstructions["WB"])
    MEM(stageInstructions["MEM"])
    EX(stageInstructions["EX"])
    ID(stageInstructions["ID"])
    IF(stageInstructions["IF"])
    cycle_output()
    if flag['now'] == "":
        if PipelineRegister.ID_EX is not None and PipelineRegister.ID_EX['input'] is not None and  PipelineRegister.ID_EX['input'].branch == True:
            
            currentInstructionNum = PipelineRegister.ID_EX['input'].instruction_num + PipelineRegister.ID_EX['input'].offset +1
            
            stageInstructions["IF"] = None
            PipelineRegister.ID_EX['input'].branch = False
        else:
            currentInstructionNum += 1
    stageInstructions2 = stageInstructions
    for stage in re_stage:
        if stageInstructions[stage] == None:
            if stage == "WB": continue
            stageInstructions2[re_stage[re_stage.index(stage)-1]] = None
        elif stageInstructions[stage].next_stage == stage:
            delete_stage_index = list(stageInstructions.keys()).index(stage) + 1

            
            stageInstructions2[re_stage[delete_stage_index]] = None
            # ID IF 後面都保持原本的指令
            break
        else:
            stageInstructions2[stageInstructions[stage].next_stage] = stageInstructions[stage]
    stageInstructions2["IF"] = None #每次清除IF
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

    flag['now'] = ""
    print("=====================================")

f = open(f"{root_file}/output.txt", "a+",encoding='UTF-8')
print("需要花{cycle}個cycle\n")
f.write(f"需要花{cycle}個cycle\n",)
print("$0\t$1\t$2\t$3\t$4\t$5\t$6\t$7\t$8\t$9\t$10\t$11\t$12\t$13\t$14\t$15\t$16\t$17\t$18\t$19\t$20\t$21\t$22\t$23\t$24\t$25\t$26\t$27\t$28\t$29\t$30\t$31\n")
print(reg)
f.write("$0\t$1\t$2\t$3\t$4\t$5\t$6\t$7\t$8\t$9\t$10\t$11\t$12\t$13\t$14\t$15\t$16\t$17\t$18\t$19\t$20\t$21\t$22\t$23\t$24\t$25\t$26\t$27\t$28\t$29\t$30\t$31\n")
for i in reg:
    f.write(str(int(i))+"\t")
f.write("\n")
print("W0\tW1\tW2\tW3\tW4\tW5\tW6\tW7\tW8\tW9\tW10\tW11\tW12\tW13\tW14\tW15\tW16\tW17\tW18\tW19\tW20\tW21\tW22\tW23\tW24\tW25\tW26\tW27\tW28\tW29\tW30\tW31\n")
print(mem)
f.write("W0\tW1\tW2\tW3\tW4\tW5\tW6\tW7\tW8\tW9\tW10\tW11\tW12\tW13\tW14\tW15\tW16\tW17\tW18\tW19\tW20\tW21\tW22\tW23\tW24\tW25\tW26\tW27\tW28\tW29\tW30\tW31\n")
for i in mem:
    f.write(str(int(i))+"\t")
f.write("\n")


    