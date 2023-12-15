class IF:
    def __init__(self):
        pass

    def execute(self, instruction, cycle, TOTAL_CONTROL) -> list:
        TOTAL_CONTROL.append(str(cycle) + " " + instruction.split(" ")[0] + ":IF")
        return TOTAL_CONTROL