import pygame
from Interpreter import Interpreter

if not pygame.get_init():
    pygame.init()

if __name__ == '__main__':

    ROM_NAME = "Tetris"

    I = Interpreter(ROM_NAME, scale=10)

    I.run()

