import pygame
import sys
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITATIONAL_CONSTANT = 0.04
ELECTROSTATIC_CONSTANT = 0.1
STRONG_FORCE_CONSTANT = 0.2
WEAK_FORCE_CONSTANT = 0.03
STRONG_FORCE_RANGE = 50
WEAK_FORCE_RANGE = 200
CONTACT_FORCE_CONSTANT = 10.0
CONTACT_SOFTNESS = 1.5
ORBIT_RANGE = 120
ORBIT_SPEED_SCALE = 0.7
ORBIT_CORRECTION = 0.03
particles = []

def set_particles(particle_list):
    global particles
    particles = particle_list

def reset_particles():
    global particles
    particles.clear()

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

            real_distance = math.sqrt(distance_sq)
            touch_distance = self.radius + other.radius + 5  # Add 5 pixel gap

            # Repulsion force using real distance
            if real_distance < touch_distance:
                repulsion = CONTACT_FORCE_CONSTANT / (real_distance ** 12)
                accelerationR = repulsion / self.mass
                max_acceleration = 10.0  # Lower cap to prevent exploding
                accelerationR = min(accelerationR, max_acceleration)
                self.dx -= accelerationR * (dx / real_distance)
                self.dy -= accelerationR * (dy / real_distance)

            # Clamp distance for other forces to prevent singularities
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

            strong_decay = math.exp(-(distance / STRONG_FORCE_RANGE) ** 2)
            forceS = STRONG_FORCE_CONSTANT * self.mass * other.mass * strong_decay / (distance_sq + 1)
            accelerationS = forceS / self.mass
            self.dx += accelerationS * direction_x
            self.dy += accelerationS * direction_y

            weak_decay = math.exp(-(distance / WEAK_FORCE_RANGE) ** 2)
            forceW = WEAK_FORCE_CONSTANT * self.mass * other.mass * weak_decay / (distance_sq + 1)
            accelerationW = forceW / self.mass
            self.dx += accelerationW * direction_x
            self.dy += accelerationW * direction_y

            if self.type == "electron" and other.type == "proton":
                if 10 < real_distance < ORBIT_RANGE:
                    tangent_x = -direction_y
                    tangent_y = direction_x
                    current_tangential = self.dx * tangent_x + self.dy * tangent_y
                    desired_tangential = math.sqrt(abs(ELECTROSTATIC_CONSTANT * self.charge * other.charge) / (self.mass * real_distance)) * ORBIT_SPEED_SCALE
                    correction = (desired_tangential - current_tangential) * ORBIT_CORRECTION
                    self.dx += correction * tangent_x
                    self.dy += correction * tangent_y

        # Apply damping to prevent excessive speeds
        damping = 0.95
        self.dx *= damping
        self.dy *= damping

        self.x += self.dx
        self.y += self.dy

        # Separate overlapping particles
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
            real_distance = math.sqrt(distance_sq)
            touch_distance = self.radius + other.radius + 3
            if real_distance < touch_distance:
                separation = (touch_distance - real_distance) * 0.5
                dir_x = dx / real_distance if real_distance > 0 else 0
                dir_y = dy / real_distance if real_distance > 0 else 0
                self.x -= separation * dir_x
                self.y -= separation * dir_y
                other.x += separation * dir_x
                other.y += separation * dir_y

        if self.x < 0:
            self.x += SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x -= SCREEN_WIDTH
        if self.y < 0:
            self.y += SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y -= SCREEN_HEIGHT

