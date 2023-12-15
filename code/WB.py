CONTROL_dict = {
    "lw":  "11",
    "sw":  "0X",
    "beq": "0X",
    "add": "10",
    "sub": "10"
}

class WB:
    def __init__(self):
        pass
    
    def execute(self, instruction, cycle,TOTAL_CONTROL) -> list:
        TOTAL_CONTROL.append(str(cycle) + " " + instruction.split(" ")[0]+ ":WB -> " + CONTROL_dict[instruction.split(" ")[0]])
        # print(f"Cycle {cycle} {instruction}: WB")
        return TOTAL_CONTROL
