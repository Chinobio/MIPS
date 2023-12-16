import numpy as np
from IF import IF
from EX import EX
from ID import ID
from WB import WB
from MEM import MEM

root_file = "database/"
register = np.ones(32)
register[0] = 0
memory = np.ones(32)
aa = 123
enter = 1
class control_signals:
    def __init__(self, instructions):
        self.instructions = instructions
        self.cycle = 0
        self.TOTAL_CONTROL = []
        self.stages = [IF(), ID(), EX(), MEM(), WB()]  # 將階段的物件存儲到列表中
        self.current_instructions = [None, None, None, None, None]  # 存儲每個週期中的指令

    def execute(self):
        for i in range(len(self.instructions) + len(self.stages) - 1):
            self.cycle += 1
            # 將新的指令添加到當前指令列表中
            if i < len(self.instructions):
                self.current_instructions = [self.instructions[i]] + self.current_instructions[:-1]
            else:
                self.current_instructions = [None] + self.current_instructions[:-1]

            # 然後，對當前指令列表中的每個指令進行操作
            for j in range(len(self.stages)):
                if self.current_instructions[j] is not None:
                    stage_name = self.stages[j].__class__.__name__
                    self.stages[j].execute(self.current_instructions[j], self.cycle, self.TOTAL_CONTROL)
                    # self.TOTAL_CONTROL.append(str(self.cycle) + " " + self.current_instructions[j].split(" ")[0] + ":" + stage_name)

        # sorted_NOW = sorted(self.TOTAL_CONTROL, key=lambda x: int(x.split(' ')[0]))
        self.printAns()
    
    def printAns(self): #格式輸出並輸出至txt
        with open('output.txt', 'w') as file:
            num_of_cycles = int(self.TOTAL_CONTROL[-1][0]) #取cycle個數
            for i in range(num_of_cycles):
                print("cycle",i+1)
                file.write("cycle "+str(i+1) + '\n') #txt
                for elements in reversed(self.TOTAL_CONTROL):
                    if(elements[0] == str(i+1)):
                        print("\t"+elements[2:])
                        file.write("\t"+elements[2:] + '\n') #txt

class MIPS:
    def __init__(self):
        self.instructions = []
    
    def read_file(self, file):
        f = open(f"{root_file}/{file}", "r")
        lines = f.readlines()
        for line in lines:
            self.instructions.append(line)
        f.close() 
        self.execute_instructions()
        control_signals(self.instructions).execute()
        # ['lw $2, 8($0)\n', 'lw $3, 16($0) \n', 'add $6, $4, $5\n', 'sw $6, 24($0)']
        # self.instructions
        
    
    def execute_instructions(self):
        for instruction in self.instructions:
            self.control_signals(instruction)
    
    def control_signals(self, instruction):
        LIST = ["lw", "sw", "add", "sub", "beq"]
        get_title = instruction.split(" ")[0]
        title_index = LIST.index(get_title)
        switch = {
            0: lw,
            1: sw,
            2: add,
            3: sub,
            4: beq
        }
        switch[title_index]().execute(instruction)

class lw:
    def __init__(self):
        pass
    
    def execute(self, instruction):
        rt = int(instruction.split(" ")[1][1:-1])
        rs = int(instruction.split(" ")[2].split(",")[0].split("(")[0]) / 4
        base_register = int(instruction.split("(")[1].split(")")[0].split("$")[1])
        base_address = register[base_register]
        address = base_address + rs
        data = memory[int(address)]
        register[rt] = data

class sw:
    def __init__(self):
        pass
    
    def execute(self, instruction):
        rt = int(instruction.split(" ")[1][1:-1])
        rs = int(instruction.split(" ")[2].split(",")[0].split("(")[0]) / 4
        base_register = int(instruction.split("(")[1].split(")")[0].split("$")[1])
        base_address = register[base_register]
        address = base_address + rs
        data = register[rt]
        memory[int(address)] = data

class add:
    def __init__(self):
        pass
    
    def execute(self, instruction):
        rd = int(instruction.split(" ")[1][1:-1])
        rs = int(instruction.split(" ")[2][1:-1])
        rt = int(instruction.split(" ")[3][1:-1])
        result = register[rs] + register[rt]
        register[rd] = result

class sub:
    def __init__(self):
        pass
    
    def execute(self, instruction):
        rd = int(instruction.split(" ")[1][1:-1])
        rs = int(instruction.split(" ")[2][1:-1])
        rt = int(instruction.split(" ")[3][1:-1])
        result = register[rs] - register[rt]
        register[rd] = result

class beq:
    def __init__(self):
        pass
    
    def execute(self, instruction):
        rs = int(instruction.split(" ")[1][1:-1])
        rt = int(instruction.split(" ")[2][1:-1])
        offset = int(instruction.split(" ")[3])
        if register[rs] == register[rt]:
            address = offset * 4
            return address


EX1 = MIPS().read_file("ex1.txt")
print(register)
print(memory)