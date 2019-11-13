"""CPU functionality."""
import sys


PRN = 0b01000111
LDI = 0b10000010
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.program_filename = ''
        self.running = True

        # Place methods on branch_table key=>pay dictionary to enable O(1) access inside run() loop
        self.branch_table = {}
        self.branch_table[PRN] = self.handle_prn
        self.branch_table[LDI] = self.handle_ldi
        self.branch_table[HLT] = self.handle_halt
        self.branch_table[MUL] = self.handle_mul
        self.branch_table[PUSH] = self.handle_push
        self.branch_table[POP] = self.handle_pop

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, addr, value):
        self.ram[addr] = value

    def load(self):
        """Load a program into memory."""
        try:
            address = 0
            with open(self.program_filename) as f:
                for line in f:
                    # deal with comments
                    # split before and after any comment symbol '#'
                    comment_split = line.split("#")

                    # convert the pre-comment portion (to the left) from binary to a value
                    # extract the first part of the split to a number variable
                    # and trim whitespace
                    num = comment_split[0].strip()

                    # ignore blank lines / comment only lines
                    if len(num) == 0:
                        continue

                    # set the number to an integer of base 2
                    value = int(num, 2)
                    # print the value in binary and in decimal
                    # uncomment for debugging: print(f"{value:08b}: {value:d}")

                    # add the value in to the memory at the index of address
                    self.ram[address] = value

                    # increment the address
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def handle_ldi(self, op_a, op_b):
        self.reg[op_a] = op_b
        self.pc += 3

    def handle_prn(self, op_a, op_b):
        print(self.reg[op_a])
        self.pc += 2

    def handle_mul(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        self.pc += 3

    def handle_push(self, op_a, op_b):
        # EXECUTE
        reg = self.ram_read(self.pc + 1)
        val = self.reg[reg]

        # PUSH
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], val)
        self.pc += 2

    def handle_pop(self, op_a, op_b):
        # EXECUTE
        # SETUP
        reg = self.ram_read(self.pc + 1)
        val = self.ram_read(self.reg[self.sp])

        # POP
        self.reg[reg] = val
        self.reg[self.sp] += 1
        self.pc += 2

    def handle_halt(self, op_a, op_b):
        self.running = False

    def run(self):
        """Run the CPU."""
        IR = self.ram[self.pc]

        if len(sys.argv) != 2:
            print("usage: cpy.py filename")
            sys.exit(1)

        self.program_filename = sys.argv[1]
        self.load()

        while self.running:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Invoke the method responsible for handling this instruction
            self.branch_table[IR](operand_a, operand_b)


cpu = CPU()

# cpu.load()
cpu.run()
