# visualizer.py


import pygame
import math
import random
from physics import Ship, Bullet


# === INITIALIZATION ===
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ship Game - Big Map + Radar")
clock = pygame.time.Clock()
FPS = 60


MAP_WIDTH = SCREEN_WIDTH * 12
MAP_HEIGHT = SCREEN_HEIGHT * 12


# === COLORS ===
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# === GAME OBJECT CLASSES ===


class CircleObstacle:
   def __init__(self, x, y, radius):
       self.x = x
       self.y = y
       self.radius = radius


   def get_rect(self):
       return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


   def draw(self, surface, offset):
       pygame.draw.circle(surface, GRAY, (int(self.x - offset[0]), int(self.y - offset[1])), self.radius)


class Wall:
   def __init__(self, x, y, width, height):
       self.rect = pygame.Rect(x, y, width, height)


   def draw(self, surface, offset):
       shifted = self.rect.move(-offset[0], -offset[1])
       pygame.draw.rect(surface, GRAY, shifted)


# === RADAR ===


def draw_radar(surface, ship, walls, circles):
   radar_width = SCREEN_WIDTH // 8
   radar_height = SCREEN_HEIGHT // 8
   radar_x = SCREEN_WIDTH - radar_width - 10
   radar_y = SCREEN_HEIGHT - radar_height - 10
   radar_rect = pygame.Rect(radar_x, radar_y, radar_width, radar_height)


   pygame.draw.rect(surface, (30, 30, 30), radar_rect)
   pygame.draw.rect(surface, WHITE, radar_rect, 2)


   radar_range_x = SCREEN_WIDTH * 1.5
   radar_range_y = SCREEN_HEIGHT * 1.5
   view_left = ship.x - radar_range_x
   view_top = ship.y - radar_range_y


   def map_to_radar(x, y):
       rel_x = x - view_left
       rel_y = y - view_top
       rx = radar_x + (rel_x / (radar_range_x * 2)) * radar_width
       ry = radar_y + (rel_y / (radar_range_y * 2)) * radar_height
       return int(rx), int(ry)


   for wall in walls:
       if abs(wall.rect.centerx - ship.x) <= radar_range_x and abs(wall.rect.centery - ship.y) <= radar_range_y:
           rx, ry = map_to_radar(wall.rect.centerx, wall.rect.centery)
           pygame.draw.rect(surface, GRAY, pygame.Rect(rx - 2, ry - 2, 4, 4))


   for circle in circles:
       if abs(circle.x - ship.x) <= radar_range_x and abs(circle.y - ship.y) <= radar_range_y:
           rx, ry = map_to_radar(circle.x, circle.y)
           pygame.draw.circle(surface, GRAY, (rx, ry), 3)


   rx, ry = map_to_radar(ship.x, ship.y)
   pygame.draw.circle(surface, YELLOW, (rx, ry), 4)


# === OBSTACLE GENERATOR ===


def generate_obstacles(count, ship):
   walls = []
   circles = []
   attempts = 0
   max_attempts = count * 10


   while len(walls) + len(circles) < count and attempts < max_attempts:
       choice = random.choice([1, 2, 3, 4])
       is_circle = choice in [1, 3]


       if is_circle:
           radius = random.randint(15, 50)
           x = random.randint(radius, MAP_WIDTH - radius)
           y = random.randint(radius, MAP_HEIGHT - radius)
           new_circle = CircleObstacle(x, y, radius)
           new_rect = new_circle.get_rect()
       else:
           width = random.randint(20, 60)
           height = random.randint(20, 60)
           x = random.randint(0, MAP_WIDTH - width)
           y = random.randint(0, MAP_HEIGHT - height)
           new_rect = pygame.Rect(x, y, width, height)


       if new_rect.colliderect(ship.get_rect().inflate(200, 200)):
           attempts += 1
           continue


       overlap = False
       for wall in walls:
           if new_rect.colliderect(wall.rect.inflate(10, 10)):
               overlap = True
               break
       for circle in circles:
           distance = math.hypot(x - circle.x, y - circle.y)
           if distance < radius + circle.radius + 20:
               overlap = True
               break


       if overlap:
           attempts += 1
           continue


       if is_circle:
           circles.append(new_circle)
       else:
           walls.append(Wall(x, y, width, height))


       attempts += 1


   return walls, circles


# === MAIN ===


def main():
   ship = Ship(MAP_WIDTH // 2, MAP_HEIGHT // 2)
   walls, circles = generate_obstacles(700, ship)
   bullets = []


   running = True
   while running:
       dt = clock.tick(FPS)
       screen.fill(BLACK)


       keys = pygame.key.get_pressed()
       if keys[pygame.K_a]:
           ship.rotate(1)
       if keys[pygame.K_d]:
           ship.rotate(-1)
       if keys[pygame.K_w]:
           ship.move_forward()

       ship.update_position(walls, circles, MAP_WIDTH, MAP_HEIGHT)

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_SPACE:
                   bullets.append(Bullet(ship.x, ship.y, ship.angle, owner="player"))


       offset_x = ship.x - SCREEN_WIDTH // 2
       offset_y = ship.y - SCREEN_HEIGHT // 2
       offset = (offset_x, offset_y)


       ship.draw(screen, offset)


       for wall in walls:
           wall.draw(screen, offset)
       for circle in circles:
           circle.draw(screen, offset)


       for bullet in bullets:
           bullet.update(walls + circles)
           bullet.draw(screen, offset)


       bullets = [b for b in bullets if b.active]


       draw_radar(screen, ship, walls, circles)


       map_border_rect = pygame.Rect(-offset_x, -offset_y, MAP_WIDTH, MAP_HEIGHT)
       pygame.draw.rect(screen, RED, map_border_rect, 5)


       pygame.display.flip()


   pygame.quit()


if __name__ == '__main__':
   main()
