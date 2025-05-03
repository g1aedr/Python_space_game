import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game - Inertia, Rotation & Infinite World")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, offset):
        pygame.draw.rect(screen, GRAY, self.rect.move(offset))

class Bullet:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.speed = 8
        self.angle = angle
        self.owner = owner
        self.active = True

    def update(self, obstacles):
        if not self.active:
            return
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        bullet_rect = pygame.Rect(self.x - 2, self.y - 2, 4, 4)
        for obs in obstacles:
            if bullet_rect.colliderect(obs.rect):
                self.active = False
                break

    def draw(self, offset):
        if self.active:
            pygame.draw.circle(screen, RED, (int(self.x + offset[0]), int(self.y + offset[1])), 4)

class Ship:
    def __init__(self, x, y, color=BLUE):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.max_speed = 5
        self.bullets = []
        self.radius = 15
        self.health = 100
        self.color = color

    def rotate(self, direction):
        self.angle += direction * 4

    def thrust(self):
        self.velocity_x += self.acceleration * math.cos(math.radians(self.angle))
        self.velocity_y += self.acceleration * math.sin(math.radians(self.angle))
        speed = math.hypot(self.velocity_x, self.velocity_y)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.velocity_x *= scale
            self.velocity_y *= scale

    def update(self, obstacles):
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        ship_rect = pygame.Rect(new_x - self.radius, new_y - self.radius, self.radius * 2, self.radius * 2)
        for obs in obstacles:
            if ship_rect.colliderect(obs.rect):
                self.velocity_x = 0
                self.velocity_y = 0
                break
        else:
            self.x = new_x
            self.y = new_y
        self.velocity_x *= 0.99
        self.velocity_y *= 0.99
        for bullet in self.bullets:
            bullet.update(obstacles)

    def shoot(self):
        bullet = Bullet(self.x, self.y, self.angle, self)
        self.bullets.append(bullet)

    def draw(self, offset):
        rad = math.radians(self.angle)
        p1 = (self.x + 20 * math.cos(rad), self.y + 20 * math.sin(rad))
        p2 = (self.x + 10 * math.cos(rad + math.radians(140)), self.y + 10 * math.sin(rad + math.radians(140)))
        p3 = (self.x + 10 * math.cos(rad - math.radians(140)), self.y + 10 * math.sin(rad - math.radians(140)))
        pygame.draw.polygon(screen, self.color, [(p1[0] + offset[0], p1[1] + offset[1]),
                                                 (p2[0] + offset[0], p2[1] + offset[1]),
                                                 (p3[0] + offset[0], p3[1] + offset[1])])
        for bullet in self.bullets:
            bullet.draw(offset)
        if self.color == BLUE:
            pygame.draw.rect(screen, RED, (10, 10, 100, 10))
            pygame.draw.rect(screen, GREEN, (10, 10, self.health, 10))

class Enemy(Ship):
    def __init__(self, x, y):
        super().__init__(x, y, color=YELLOW)

    def ai(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        if random.random() < 0.6:
            self.thrust()
        if random.random() < 0.02:
            self.shoot()

    def draw_out_of_screen_indicator(self, offset):
        # Verifica se la nave è fuori dallo schermo
        if not (0 < self.x < WIDTH and 0 < self.y < HEIGHT):
            # Calcola la direzione in cui si trova la nave rispetto al centro dello schermo
            direction = math.atan2(self.y - HEIGHT // 2, self.x - WIDTH // 2)
            edge_offset = 30  # La distanza del segnalino dal bordo dello schermo

            # Calcola la posizione del segnalino
            x_offset = WIDTH // 2 + edge_offset * math.cos(direction)
            y_offset = HEIGHT // 2 + edge_offset * math.sin(direction)

            # Disegna il segnalino
            pygame.draw.circle(screen, YELLOW, (int(x_offset), int(y_offset)), 5)

player = Ship(0, 0)
enemies = [Enemy(random.randint(-1000, 1000), random.randint(-1000, 1000)) for _ in range(2)]

obstacles = []
for _ in range(600):
    ox = random.randint(-5000, 5000)
    oy = random.randint(-5000, 5000)
    obstacles.append(Obstacle(ox, oy))

def draw_end_message(message):
    text = font.render(message, True, WHITE)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(3000)

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.rotate(-1)
    if keys[pygame.K_RIGHT]:
        player.rotate(1)
    if keys[pygame.K_UP]:
        player.thrust()

    player.update(obstacles)
    for enemy in enemies[:]:
        enemy.ai(player)
        enemy.update(obstacles)

    for enemy in enemies:
        for bullet in enemy.bullets[:]:
            if not bullet.active:
                enemy.bullets.remove(bullet)
                continue
            bullet_rect = pygame.Rect(bullet.x - 4, bullet.y - 4, 8, 8)
            player_rect = pygame.Rect(player.x - player.radius, player.y - player.radius, player.radius * 2, player.radius * 2)
            if bullet_rect.colliderect(player_rect):
                player.health -= 10
                enemy.bullets.remove(bullet)

    for bullet in player.bullets[:]:
        if not bullet.active:
            player.bullets.remove(bullet)
            continue
        bullet_rect = pygame.Rect(bullet.x - 4, bullet.y - 4, 8, 8)
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)
            if bullet_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
                player.bullets.remove(bullet)
                break

    if player.health <= 0:
        screen.fill((0, 0, 0))
        draw_end_message("You Lose")
        running = False
    elif not enemies:
        screen.fill((0, 0, 0))
        draw_end_message("You Win")
        running = False

    offset_x = WIDTH // 2 - int(player.x)
    offset_y = HEIGHT // 2 - int(player.y)
    offset = (offset_x, offset_y)

    screen.fill((0, 0, 0))

    for obs in obstacles:
        if -100 < obs.rect.x + offset[0] < WIDTH + 100 and -100 < obs.rect.y + offset[1] < HEIGHT + 100:
            obs.draw(offset)

    player.draw(offset)
    for enemy in enemies:
        enemy.draw_out_of_screen_indicator(offset)
        enemy.draw(offset)

    pygame.display.flip()

pygame.quit()
