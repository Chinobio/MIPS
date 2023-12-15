from MEM import MEM
CONTROL_dict = {
    "lw":  "0101011",
    "sw":  "X10010X",
    "beq": "X01000X",
    "add": "1000010",
    "sub": "1000010"
}
class EX:
    def __init__(self):
        pass
    def execute(self, instruction, cycle, TOTAL_CONTROL) -> list:
        TOTAL_CONTROL.append(str(cycle) + " " + instruction.split(" ")[0] + ":EX -> " + CONTROL_dict[instruction.split(" ")[0]])
        return TOTAL_CONTROL