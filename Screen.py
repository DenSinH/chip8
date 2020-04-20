import pygame
import numpy as np

if not pygame.get_init():
    pygame.init()


class Screen(object):

    off = (0, 0, 0)
    on = (255, 255, 255)

    def __init__(self, scale):
        self.scale = scale
        self.display = pygame.display.set_mode((scale * 64, scale * 32))
        self.pixels = np.zeros((64, 32), dtype=bool)

    def set_caption(self, title):
        pygame.display.set_caption(title)

    def clear(self):
        self.pixels[:] = 0
        self.display.fill(self.off)
        pygame.display.flip()

    def draw(self, bs, pos):

        collision = False

        dy = 0
        for byte in bs:
            dx = 0
            for bit in "{0:b}".format(byte).rjust(8, "0"):

                if self.pixels[(pos[0] + dx) % 64, (pos[1] + dy) % 32] and int(bit):
                    collision = True

                self.pixels[(pos[0] + dx) % 64, (pos[1] + dy) % 32] ^= int(bit)
                dx += 1
            dy += 1

        surface = pygame.surfarray.make_surface(255 * self.pixels.astype(int))

        self.display.blit(pygame.transform.scale(surface, (self.scale * 64, self.scale * 32)), (0, 0))

        pygame.display.flip()

        return collision
