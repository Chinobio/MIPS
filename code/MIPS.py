import numpy as np

root_file = "database/"

class Instruction:
    name = ""
    current_stage = ""

def read_file(file):
    instructions = []
    f = open(f"{root_file}/{file}", "r")
    lines = f.readlines()
    for line in lines:
        instructions.append(line)
    f.close() 
    return instructions

def IF():
    pass

def ID():
    pass

def EX():
    pass

def MEM():
    pass

def WB():
    pass

reg = np.zeros(32)
mem = np.zeros(32)
# 原始指令字串list
rawInstructions = read_file("ex1.txt")
# 在stage中的指令
stageInstructions = {
    "IF": Instruction(),
    "ID": Instruction(),
    "EX": Instruction(),
    "MEM": Instruction(),
    "WB": Instruction()
}

while rawInstructions != [] or stageInstructions != {}:
    IF()
    ID()
    EX()
    MEM()
    WB()

    stageInstructions2 = stageInstructions.copy()
    for stage in reversed(stageInstructions2):
        if stageInstructions[stage].current_stage == stage:
            break
        else:
            stageInstructions2[stageInstructions[stage].current_stage] = stageInstructions[stage]
    stageInstructions = stageInstructions2.copy()


            