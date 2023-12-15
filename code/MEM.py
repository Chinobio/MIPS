from WB import WB
CONTROL_dict = {
    "lw":  "01011",
    "sw":  "0010X",
    "beq": "1000X",
    "add": "00010",
    "sub": "00010"
}

class MEM:
    def __init__(self):
        pass
    
    def execute(self, instruction, cycle, TOTAL_CONTROL) -> list:
        TOTAL_CONTROL.append(str(cycle) + " " + instruction.split(" ")[0] + ":MEM -> " + CONTROL_dict[instruction.split(" ")[0]])
        return TOTAL_CONTROL
