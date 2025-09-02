import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Player
player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 60
player_speed = 5
player = pygame.Rect(player_x, player_y, player_width, player_height)

# Bullets
bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []

# Aliens
alien_width = 40
alien_height = 40
alien_speed = 2
aliens = []
alien_health = []
alien_rows = 5
alien_cols = 10

# Game variables
score = 0
xp = 0
level = 1
level_cap = 50
game_over = False
game_won = False
double_power_level = 0
double_power_cost = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Cost for levels 1 to 10
FPS = 60
clock = pygame.time.Clock()

def draw():
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, player)
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)
    for i, alien in enumerate(aliens):
        color = RED if alien_health[i] > 0 else (128, 0, 0)
        pygame.draw.rect(screen, color, alien)
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    xp_text = font.render(f"XP: {xp}", True, WHITE)
    upgrade_text = font.render(f"Double Power (Level {double_power_level}/10): {double_power_cost[double_power_level] if double_power_level < 10 else 'MAX'} XP (Press U)", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(xp_text, (10, 90))
    screen.blit(upgrade_text, (10, HEIGHT - 40))
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
    if game_won:
        win_text = font.render("You Won! Max Level Reached! Press R to Restart", True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - 200, HEIGHT // 2))
    pygame.display.flip()

def move_aliens():
    global aliens, game_over
    move_down = False
    for alien in aliens:
        alien.x += alien_speed
        if alien.right > WIDTH or alien.left < 0:
            move_down = True
    if move_down:
        for alien in aliens:
            alien.y += 10
            alien.x -= alien_speed
        globals()['alien_speed'] = -alien_speed
    for alien in aliens:
        if alien.bottom > player.top:
            globals()['game_over'] = True

def handle_collisions():
    global score, xp, aliens, alien_health, bullets, level, game_won
    bullet_damage = 1 + double_power_level  # Base damage 1 + upgrade level
    for bullet in bullets[:]:
        for i, alien in enumerate(aliens[:]):
            if bullet.colliderect(alien):
                bullets.remove(bullet)
                alien_health[i] -= bullet_damage
                if alien_health[i] <= 0:
                    aliens.pop(i)
                    alien_health.pop(i)
                    globals()['score'] += 10
                    globals()['xp'] += 1  # Gain 1 XP per enemy killed
                break
    # Check if level is cleared
    if not aliens and level < level_cap:
        globals()['level'] += 1
        setup_level()
    elif not aliens and level >= level_cap:
        globals()['game_won'] = True

def setup_level():
    global aliens, alien_health, alien_speed
    aliens = []
    alien_health = []
    health = level  # Health increases with level
    for row in range(alien_rows):
        for col in range(alien_cols):
            alien = pygame.Rect(col * (alien_width + 10) + 50, row * (alien_height + 10) + 50, alien_width, alien_height)
            aliens.append(alien)
            alien_health.append(health)
    globals()['alien_speed'] = 2 * (-1 if alien_speed < 0 else 1)  # Reset speed direction

def setup():
    global player, bullets, aliens, alien_health, score, xp, level, game_over, game_won, alien_speed, double_power_level
    player.x = WIDTH // 2 - player_width // 2
    player.y = HEIGHT - 60
    bullets = []
    score = 0
    xp = 0
    level = 1
    game_over = False
    game_won = False
    double_power_level = 0
    alien_speed = 2
    setup_level()

async def update_loop():
    global player, bullets, game_over, game_won, xp, double_power_level
    while True:
        if not game_over and not game_won:
            # Handle input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += player_speed
            if keys[pygame.K_SPACE]:
                bullet = pygame.Rect(player.centerx - bullet_width // 2, player.top, bullet_width, bullet_height)
                bullets.append(bullet)

            # Move bullets
            for bullet in bullets[:]:
                bullet.y -= bullet_speed
                if bullet.bottom < 0:
                    bullets.remove(bullet)

            # Move aliens
            move_aliens()

            # Handle collisions
            handle_collisions()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or game_won):
                    setup()
                if event.key == pygame.K_u and not game_over and not game_won and double_power_level < 10:
                    if xp >= double_power_cost[double_power_level]:
                        globals()['xp'] -= double_power_cost[double_power_level]
                        globals()['double_power_level'] += 1

        # Draw everything
        draw()

        # Control frame rate
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

async def main():
    setup()
    await update_loop()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
