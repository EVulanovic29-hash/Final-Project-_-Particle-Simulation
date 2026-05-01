import pygame
import sys
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITATIONAL_CONSTANT = 0.4
ELECTROSTATIC_CONSTANT = 1
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
        for other in particles:
            if other is self:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            if abs(dx) > SCREEN_WIDTH / 2:
                dx -= math.copysign(SCREEN_WIDTH, dx)
            if abs(dy) > SCREEN_HEIGHT / 2:
                dy -= math.copysign(SCREEN_HEIGHT, dy)

            distance_sq = dx * dx + dy * dy
            if distance_sq == 0:
                continue

            min_distance = max(self.radius + other.radius, 5)
            distance_sq = max(distance_sq, min_distance * min_distance)
            distance = math.sqrt(distance_sq)
            direction_x = dx / distance
            direction_y = dy / distance

            forceG = GRAVITATIONAL_CONSTANT * self.mass * other.mass / distance_sq
            accelerationG = forceG / self.mass
            self.dx += accelerationG * direction_x
            self.dy += accelerationG * direction_y

            if self.charge != 0 and other.charge != 0:
                forceE = ELECTROSTATIC_CONSTANT * self.charge * other.charge / distance_sq
                accelerationE = forceE / self.mass
                self.dx -= accelerationE * direction_x
                self.dy -= accelerationE * direction_y
            

        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.x += SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x -= SCREEN_WIDTH
        if self.y < 0:
            self.y += SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y -= SCREEN_HEIGHT

