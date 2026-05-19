import pygame
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

GRAVITATIONAL_CONSTANT = 4

ELECTROSTATIC_CONSTANT = -434

SOFTENING = 2.0

STRONG_FORCE_CONSTANT = 350000
STRONG_FORCE_RANGE = 22.0
STRONG_FORCE_CORE = 10.0

WEAK_FORCE_CONSTANT = 9
WEAK_FORCE_RANGE = 10.0

DAMPING = 1.0

TIME_STEP = 0.02
SUBSTEPS = 32

MAX_SPEED = 10000

particles = []


def set_particles(particle_list):
    global particles
    particles = particle_list


def reset_particles():
    particles.clear()


class Particle:

    def __init__(
        self,
        x,
        y,
        dx,
        dy,
        radius,
        color,
        type,
        charge,
        mass
    ):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy

        self.ax = 0
        self.ay = 0

        self.radius = radius
        self.color = color

        self.type = type
        self.charge = charge
        self.mass = mass

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )


def wrap_delta(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if dx > SCREEN_WIDTH / 2:
        dx -= SCREEN_WIDTH
    elif dx < -SCREEN_WIDTH / 2:
        dx += SCREEN_WIDTH

    if dy > SCREEN_HEIGHT / 2:
        dy -= SCREEN_HEIGHT
    elif dy < -SCREEN_HEIGHT / 2:
        dy += SCREEN_HEIGHT

    return dx, dy


def enforce_no_overlap(p1, p2, dx, dy, dist):

    if "electron" in (p1.type, p2.type):
        return

    min_dist = p1.radius + p2.radius

    if dist < min_dist and dist > 0:
        push = (min_dist - dist) * 0.5

        nx = dx / dist
        ny = dy / dist

        p1.x -= nx * push
        p1.y -= ny * push
        p2.x += nx * push
        p2.y += ny * push


def compute_force(p1, p2):

    dx, dy = wrap_delta(p1, p2)
    dist = math.hypot(dx, dy)

    if dist <= 0.000001:
        return 0, 0

    enforce_no_overlap(p1, p2, dx, dy, dist)

    nx = dx / dist
    ny = dy / dist

    softened_dist = math.sqrt(dist**2 + SOFTENING**2)

    Fg = (
        GRAVITATIONAL_CONSTANT
        * p1.mass
        * p2.mass
        / softened_dist**2
    )

    Fe = (
        ELECTROSTATIC_CONSTANT
        * p1.charge
        * p2.charge
        / softened_dist**2
    )

    Fs = 0

    if p1.type in ("proton", "neutron") and p2.type in ("proton", "neutron"):

        sr = math.exp(-dist / STRONG_FORCE_RANGE)

        Fs = (
            STRONG_FORCE_CONSTANT
            * sr
            / softened_dist**2
        )

        if dist < STRONG_FORCE_CORE:
            core_push = ((STRONG_FORCE_CORE - dist) / STRONG_FORCE_CORE) ** 2
            Fs *= -core_push

    Fw = 0

    if p1.type in ("proton", "neutron") and p2.type in ("proton", "neutron"):
        if dist < WEAK_FORCE_RANGE:
            Fw = WEAK_FORCE_CONSTANT / softened_dist**2

    F = Fg + Fe + Fs + Fw

    return F * nx, F * ny


def update_particles():

    dt = TIME_STEP / SUBSTEPS

    for _ in range(SUBSTEPS):

        for p in particles:
            p.ax = 0
            p.ay = 0

        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):

                p1 = particles[i]
                p2 = particles[j]

                fx, fy = compute_force(p1, p2)

                p1.ax += fx / p1.mass
                p1.ay += fy / p1.mass

                p2.ax -= fx / p2.mass
                p2.ay -= fy / p2.mass

        for p in particles:

            p.dx += p.ax * dt
            p.dy += p.ay * dt

            speed = math.hypot(p.dx, p.dy)
            if speed > MAX_SPEED:
                scale = MAX_SPEED / speed
                p.dx *= scale
                p.dy *= scale

            p.x += p.dx * dt
            p.y += p.dy * dt

            p.x %= SCREEN_WIDTH
            p.y %= SCREEN_HEIGHT

    apply_nuclear_stabilization()


def apply_nuclear_stabilization():

    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):

            p1 = particles[i]
            p2 = particles[j]

            if p1.type in ("proton", "neutron") and p2.type in ("proton", "neutron"):

                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist = math.hypot(dx, dy)

                if 0 < dist < STRONG_FORCE_RANGE:

                    vx = p2.dx - p1.dx
                    vy = p2.dy - p1.dy

                    damping = 0.03

                    p1.dx += vx * damping
                    p1.dy += vy * damping
                    p2.dx -= vx * damping
                    p2.dy -= vy * damping

                    tx = -dy / dist
                    ty = dx / dist

                    rel_v = p1.dx * tx + p1.dy * ty

                    max_spin = 2.0

                    if abs(rel_v) > max_spin:
                        correction = (max_spin - rel_v) * 0.1
                        p1.dx += tx * correction
                        p1.dy += ty * correction


def throw(particle):

    first_click_pos = None
    second_click_pos = None

    while first_click_pos is None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                first_click_pos = pygame.mouse.get_pos()

    while second_click_pos is None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                second_click_pos = pygame.mouse.get_pos()

    vx = (second_click_pos[0] - first_click_pos[0]) * 0.2
    vy = (second_click_pos[1] - first_click_pos[1]) * 0.2

    particle.dx += vx
    particle.dy += vy

    return vx, vy