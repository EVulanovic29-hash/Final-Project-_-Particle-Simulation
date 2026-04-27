import pygame
import sys


class Particle:
    def __init__(self, x, y, dx, dy, radius, color, type, charge):  # Constructor method
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.radius = radius
        self.type = type
        self.charge = charge

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def update(self):
        self.x += self.dx
        self.y += self.dy
