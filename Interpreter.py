from Screen import Screen
import random
import numpy as np
import pygame
import winsound

if not pygame.get_init():
    pygame.init()


class Interpreter(object):

    digits = {
        0x0: [0xf0, 0x90, 0x90, 0x90, 0xf0],
        0x1: [0x20, 0x60, 0x20, 0x20, 0x70],
        0x2: [0xf0, 0x10, 0xf0, 0x80, 0xf0],
        0x3: [0xf0, 0x10, 0xf0, 0x10, 0xf0],
        0x4: [0x90, 0x90, 0xf0, 0x10, 0x10],
        0x5: [0xf0, 0x80, 0xf0, 0x10, 0xf0],
        0x6: [0xf0, 0x80, 0xf0, 0x90, 0xf0],
        0x7: [0xf0, 0x10, 0x20, 0x40, 0x40],
        0x8: [0xf0, 0x90, 0xf0, 0x90, 0xf0],
        0x9: [0xf0, 0x90, 0xf0, 0x10, 0xf0],
        0xa: [0xf0, 0x90, 0xf0, 0x90, 0x90],
        0xb: [0xe0, 0x90, 0xf0, 0x10, 0xf0],
        0xc: [0xf0, 0x80, 0x80, 0x80, 0xf0],
        0xd: [0xe0, 0x90, 0x90, 0x90, 0xe0],
        0xe: [0xf0, 0x80, 0xf0, 0x80, 0xf0],
        0xf: [0xf0, 0x80, 0xf0, 0x80, 0x80]
    }

    def __init__(self, rom_name, scale=5):
        self.screen = Screen(scale=scale)

        self.rom_name = None
        self.registers = np.zeros(16, dtype=np.uint8)
        self.I = np.zeros(1, dtype=np.uint16)
        self.mem = np.zeros(4096, dtype=np.uint8)
        self.digit_locs = {d: 5 * d for d in range(16)}

        self.keyboard = np.zeros(16, dtype=np.uint8)

        self.stack = []

        self.dt = np.zeros(1, dtype=np.uint8)
        self.st = np.zeros(1, dtype=np.uint8)

        self.pc = 0x200

        self.clock = pygame.time.Clock()
        self.clock_speed = 600  # Hz
        self.cycle = 0

        self.open(rom_name)

    def reset_mem(self):
        self.pc = 0x200

        self.mem[:] = 0

        for d in range(16):
            self.mem[5 * d: 5 * d + 5] = self.digits[d]

    def open(self, rom_name):
        self.rom_name = rom_name
        self.screen.set_caption(rom_name)

        self.reset_mem()

        with open(f".//rom//{rom_name}.ch8", "rb") as f:
            i = 0x200
            byte = f.read(1)
            while byte:
                self.mem[i] = int.from_bytes(byte, byteorder="big")
                byte = f.read(1)

                i += 1

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:

                for i in range(16):
                    if event.key == getattr(pygame, "K_" + "x123qweasdzc4rfv"[i]):
                        self.keyboard[i] = 1
                        break

            elif event.type == pygame.KEYUP:
                for i in range(16):
                    if event.key == getattr(pygame, "K_" + "x123qweasdzc4rfv"[i]):
                        self.keyboard[i] = 0
                        break

    def get_key(self):
        print("GET KEY")
        while True:
            self.handle_events()

            for i in range(16):
                if self.keyboard[i]:
                    return i

            self.clock.tick(self.clock_speed)

    def run(self):

        while True:

            self.execute()
            self.cycle = (self.cycle + 1) % self.clock_speed

            if self.cycle % 60 == 0:
                self.handle_events()

                if np.any(self.dt):
                    self.dt -= 1

                if np.any(self.st):
                    self.st -= 1
                    winsound.Beep(2500, 100)

            self.clock.tick(self.clock_speed)

    def execute(self):
        instruction = int(0x100 * self.mem[self.pc] + self.mem[self.pc + 1])
        self.pc += 2

        x = (instruction & 0x0f00) // 0x0100
        y = (instruction & 0x00f0) // 0x0010

        # CLS
        if instruction == 0x00e0:
            self.screen.clear()

        # RET
        elif instruction == 0x00ee:
            self.pc = self.stack.pop(-1)

        # JP
        elif instruction & 0xf000 == 0x1000:
            self.pc = instruction & 0x0fff

        # CALL
        elif instruction & 0xf000 == 0x2000:
            self.stack.append(self.pc)  # todo: +2 or no?
            assert len(self.stack) <= 16
            self.pc = instruction & 0x0fff

        # SE
        elif instruction & 0xf000 == 0x3000:
            if self.registers[x] == (instruction & 0x00ff):
                self.pc += 2

        # SNE
        elif instruction & 0xf000 == 0x4000:
            if self.registers[x] != (instruction & 0x00ff):
                self.pc += 2

        # SE
        elif instruction & 0xf000 == 0x5000:
            if self.registers[x] == self.registers[y]:
                self.pc += 2

        # LD
        elif instruction & 0xf000 == 0x6000:
            self.registers[x] = instruction & 0x00ff

        # ADD
        elif instruction & 0xf000 == 0x7000:
            self.registers[x] += instruction & 0x00ff

        elif instruction & 0xf000 == 0x8000:

            # LD
            if instruction & 0x000f == 0x0000:
                self.registers[x] = self.registers[y]

            # OR
            elif instruction & 0x000f == 0x0001:
                self.registers[x] |= self.registers[y]

            # AND
            elif instruction & 0x000f == 0x0002:
                self.registers[x] &= self.registers[y]

            # XOR
            elif instruction & 0x000f == 0x0003:
                self.registers[x] ^= self.registers[y]

            # ADD
            elif instruction & 0x000f == 0x0004:
                self.registers[x] += self.registers[y]
                self.registers[0xf] = int(self.registers[x]) + int(self.registers[y]) > 255

            # SUB
            elif instruction & 0x000f == 0x0005:
                self.registers[0xf] = self.registers[x] > self.registers[y]
                self.registers[x] -= self.registers[y]

            # SHR
            elif instruction & 0x000f == 0x0006:
                self.registers[0xf] = self.registers[x] & 0b00000001
                self.registers[x] //= 2

            # SUBN
            elif instruction & 0x000f == 0x0007:
                self.registers[0xf] = self.registers[x] < self.registers[y]
                self.registers[x] = self.registers[y] - self.registers[x]

            # SHL
            elif instruction & 0x000f == 0x000e:
                self.registers[0xf] = self.registers[x] & 0b10000000
                self.registers[x] *= 2

            else:
                raise Exception(f"Unknown instruction: {hex(instruction)}")

        # SNE
        elif instruction & 0xf000 == 0x9000:
            if self.registers[x] != self.registers[y]:
                self.pc += 2

        # LD I
        elif instruction & 0xf000 == 0xa000:
            self.I[0] = instruction & 0x0fff

        # JP V0
        elif instruction & 0xf000 == 0xb000:
            self.pc = (instruction & 0x0fff) + self.registers[0x0]

        # RND
        elif instruction & 0xf000 == 0xc000:
            self.registers[x] = random.randint(0, 255) & (instruction & 0x00ff)

        # DRW
        elif instruction & 0xf000 == 0xd000:
            self.registers[0xf] = self.screen.draw(
                self.mem[int(self.I[0]):int(self.I[0]) + (instruction & 0x000f)],
                (self.registers[x], self.registers[y])
            )

        elif instruction & 0xf000 == 0xe000:

            # SKP
            if instruction & 0x00ff == 0x009e:
                if self.keyboard[self.registers[x]]:
                    self.pc += 2

            # SKNP
            elif instruction & 0x00ff == 0x00a1:
                if not self.keyboard[self.registers[x]]:
                    self.pc += 2

            else:
                raise Exception(f"Unknown instruction: {hex(instruction)}")

        elif instruction & 0xf000 == 0xf000:

            # LD
            if instruction & 0x00ff == 0x0007:
                self.registers[x] = self.dt[0]

            # LD
            elif instruction & 0x00ff == 0x000a:
                self.registers[x] = self.get_key()

            # LD DT
            elif instruction & 0x00ff == 0x0015:
                self.dt[0] = self.registers[x]

            # LD ST
            elif instruction & 0x00ff == 0x0018:
                self.st[0] = self.registers[x]

            # ADD I
            elif instruction & 0x00ff == 0x001e:
                self.I[0] += self.registers[x]

            # LD F
            elif instruction & 0x00ff == 0x0029:
                self.I[0] = self.digit_locs[int(self.registers[x])]

            # LD B
            elif instruction & 0x00ff == 0x0033:
                decimal = str(int(self.registers[x])).zfill(3)
                for i in range(3):
                    self.mem[int(self.I[0]) + i] = int(decimal[i])

            # LD [I]
            elif instruction & 0x00ff == 0x0055:
                for i in range((instruction & 0x0f00) // 0x0100 + 1):
                    self.mem[int(self.I[0]) + i] = self.registers[i]

            # LD
            elif instruction & 0x00ff == 0x0065:
                for i in range((instruction & 0x0f00) // 0x0100 + 1):
                    self.registers[i] = self.mem[int(self.I[0]) + i]

            else:
                raise Exception(f"Unknown instruction: {hex(instruction)}")

        else:
            raise Exception(f"Unknown instruction: {hex(instruction)}")
