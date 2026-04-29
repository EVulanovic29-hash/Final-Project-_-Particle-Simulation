import pygame
import sys
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITATIONAL_CONSTANT = 1
particles = []

def set_particles(particle_list):
    global particles
    particles = particle_list

class Particle:
    def __init__(self, x, y, dx, dy, radius, color, type, charge, mass):  # Constructor method
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.mass = mass
        self.radius = radius
        self.type = type
        self.charge = charge

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def update(self, particles):
        to_remove = set()
        # gravitational force
        for other in particles:
            if other != self:
                distance_x = other.x - self.x
                distance_y = other.y - self.y
                distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
                if distance > 0:
                    force = GRAVITATIONAL_CONSTANT * self.mass * other.mass / (distance ** 2)
                    acceleration = force / self.mass
                    self.dx += acceleration * (distance_x / distance)
                    self.dy += acceleration * (distance_y / distance)
        # boundary loop
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0
        self.x += self.dx
        self.y += self.dy

