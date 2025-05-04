# physics.py


import math
import pygame


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0.2  # accelerazione per frame
        self.size = 12
        self.health = 100
        self.vx = 0
        self.vy = 0
        self.max_speed = 5
        self.friction = 0.98  # più vicino a 1 = meno attrito

    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def rotate(self, direction):
        self.angle += direction * 5

    def move_forward(self):
        radians = math.radians(self.angle)
        self.vx += self.speed * math.cos(radians)
        self.vy -= self.speed * math.sin(radians)  # screen y+ is down

        # Limita la velocità massima
        velocity = math.hypot(self.vx, self.vy)
        if velocity > self.max_speed:
            scale = self.max_speed / velocity
            self.vx *= scale
            self.vy *= scale

    def update_position(self, walls, circles, map_width, map_height):
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        new_rect = pygame.Rect(new_x - 10, new_y - 10, 20, 20)

        if new_rect.left < 0 or new_rect.right > map_width or new_rect.top < 0 or new_rect.bottom > map_height:
            return

        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return

        for circle in circles:
            distance = math.hypot(new_x - circle.x, new_y - circle.y)
            if distance < self.size + circle.radius:
                return

        self.x = new_x
        self.y = new_y

        # Applica attrito
        self.vx *= self.friction
        self.vy *= self.friction

    def draw(self, surface, offset):
        radians = math.radians(self.angle)
        tip = (self.x + self.size * math.cos(radians), self.y - self.size * math.sin(radians))
        left = (self.x + self.size * math.cos(radians + 2.5), self.y - self.size * math.sin(radians + 2.5))
        right = (self.x + self.size * math.cos(radians - 2.5), self.y - self.size * math.sin(radians - 2.5))
        points = [tip, left, right]
        shifted = [(p[0] - offset[0], p[1] - offset[1]) for p in points]
        pygame.draw.polygon(surface, (0, 255, 0), shifted)


class Bullet:
    def __init__(self, x, y, angle, owner, speed=8):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.speed = speed
        self.active = True

    def update(self, obstacles):
        if not self.active:
            return
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))  # screen y+ is down
        bullet_rect = pygame.Rect(self.x - 2, self.y - 2, 4, 4)

        for obs in obstacles:
            if hasattr(obs, 'rect') and bullet_rect.colliderect(obs.rect):
                self.active = False
                break
            elif hasattr(obs, 'x') and hasattr(obs, 'y') and hasattr(obs, 'radius'):
                distance = math.hypot(self.x - obs.x, self.y - obs.y)
                if distance < obs.radius:
                    self.active = False
                    break

    def draw(self, surface, offset, color=(255, 0, 0)):
        if self.active:
            pygame.draw.circle(
                surface,
                color,
                (int(self.x - offset[0]), int(self.y - offset[1])),
                4
            )

