import random
import math
from pygame import Rect
from pgzero.builtins import Actor, keyboard, sounds

WIDTH = 800
HEIGHT = 600

TILE_SIZE = 64
ANIM_DELAY = 0.15

is_game_running = False
game_over = False
sound_on = True
score = 0

enemy_spawn_timer = 0
enemy_spawn_delay = 0.25 # a cada 0.25 segundos

# --- Classes --- #

class Character:
    def __init__(self, idle_imgs, walk_imgs, pos, speed=2):
        self.idle_imgs = idle_imgs
        self.walk_imgs = walk_imgs
        self.actor = Actor(idle_imgs[0], pos)
        self.rect = Rect((self.actor.left, self.actor.top), (self.actor.width, self.actor.height))
        self.speed = speed
        self.frame = 0
        self.frame_time = 0
        self.moving = False

    def update(self, dt):
        self.frame_time += dt
        if self.frame_time >= ANIM_DELAY:
            self.frame_time = 0
            self.frame = (self.frame + 1) % len(self.get_current_anim())
            self.actor.image = self.get_current_anim()[self.frame]
        self.rect.topleft = (self.actor.left, self.actor.top)

    def draw(self):
        self.actor.draw()

    def get_current_anim(self):
        return self.walk_imgs if self.moving else self.idle_imgs


class Hero(Character):
    def __init__(self, idle_imgs, walk_imgs, pos, speed=3):
        super().__init__(idle_imgs, walk_imgs, pos, speed)
        self.health = 3
        self.invulnerable = 0
        self.is_attacking = False
        self.attack_cooldown = 0.5
        self.attack_timer = 0

    def take_damage(self):
        if self.invulnerable <= 0:
            self.health -= 1
            self.invulnerable = 1

    def handle_input(self):
        self.moving = False
        if keyboard.left:
            self.actor.x -= self.speed
            self.moving = True
        if keyboard.right:
            self.actor.x += self.speed
            self.moving = True
        if keyboard.up:
            self.actor.y -= self.speed
            self.moving = True
        if keyboard.down:
            self.actor.y += self.speed
            self.moving = True

        if keyboard.space and self.attack_timer <= 0:
            self.attack()

    def attack(self):
        self.is_attacking = True
        self.attack_timer = self.attack_cooldown
        if sound_on:
            sounds.attack.play()

    def update(self, dt):
        super().update(dt)
        if self.invulnerable > 0:
            self.invulnerable -= dt
        if self.attack_timer > 0:
            self.attack_timer -= dt
        else:
            self.is_attacking = False


class Enemy(Character):
    def __init__(self, idle_imgs, walk_imgs, pos, speed=1.5):
        super().__init__(idle_imgs, walk_imgs, pos, speed)
        self.health = 1

    def update(self, dt, hero_pos):
        super().update(dt)
        self.move_towards(hero_pos)

    def move_towards(self, target_pos):
        dx = target_pos[0] - self.actor.x
        dy = target_pos[1] - self.actor.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            dx /= dist
            dy /= dist
            self.actor.x += dx * self.speed
            self.actor.y += dy * self.speed
            self.moving = True
        else:
            self.moving = False


# --- Recursos --- #

idle_imgs = ['hero_idle_0', 'hero_idle_1']
walk_imgs = ['hero_walk_0', 'hero_walk_1', 'hero_walk_2']
enemy_idle_imgs = ['enemy_idle_0', 'enemy_idle_1']
enemy_walk_imgs = ['enemy_walk_0', 'enemy_walk_1']

hero = None
enemies = []

# --- Funções do jogo --- #

def draw():
    screen.clear()

    if not is_game_running:
        screen.draw.text("Pressione ENTER para começar", center=(WIDTH//2, HEIGHT//2), fontsize=40, color="white")
        return

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
        return

    hero.draw()
    for enemy in enemies:
        enemy.draw()
    draw_ui()

def update(dt):
    if not is_game_running or game_over:
        return

    hero.handle_input()
    hero.update(dt)

    for enemy in enemies[:]:
        enemy.update(dt, hero.actor.pos)
        if hero.is_attacking and hero.actor.colliderect(enemy.actor):
            enemies.remove(enemy)
            global score
            score += 1  
            if sound_on:
                sounds.hit.play()
        elif hero.actor.colliderect(enemy.actor) and hero.invulnerable <= 0:
            hero.take_damage()
            
    # Spawn de inimigos ao longo do tempo
    global enemy_spawn_timer
    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0:
        spawn_enemy()
        enemy_spawn_timer = enemy_spawn_delay
    
    check_game_over()

def draw_ui():
    screen.draw.text(f"Vida: {hero.health}", topleft=(10, 10), fontsize=30, color="white")
    screen.draw.text(f"Pontos: {score}", topleft=(10, 40), fontsize=30, color="yellow")

def on_key_down(key):
    global is_game_running, game_over
    if key == keys.RETURN and not is_game_running:
        is_game_running = True
        reset_game()

def reset_game():
    global hero, game_over, score, enemies
    hero = Hero(idle_imgs, walk_imgs, pos=(WIDTH//2, HEIGHT//2))
    game_over = False
    score = 0
    enemies = []
    hero.health = 3
    hero.invulnerable = 0
    hero.is_attacking = False
    hero.attack_timer = 0

    for _ in range(5):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        enemy = Enemy(enemy_idle_imgs, enemy_walk_imgs, (x, y))
        enemies.append(enemy)

def spawn_enemy():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemy = Enemy(enemy_idle_imgs, enemy_walk_imgs, (x, y))
    enemies.append(enemy)

def check_game_over():
    global game_over
    if hero.health <= 0:
        game_over = True

import pgzrun
pgzrun.go()
