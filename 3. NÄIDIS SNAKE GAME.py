# 3. NÄIDIS MÄNG

# LINK: https://github.com/Escgot/Snake-Game
# TESTIMINE: kõik toimis
# MEELDIB: Erinevad powerupid
# EI MEELDI: Pole eriti kasutajasõbralik, puudub game over screen, raske mängida kui ruudustikku pole.


import pygame
import sys
import random

# --- 1. Setup ---
pygame.init()
GAME_WIDTH, GAME_HEIGHT = 600, 400
UI_WIDTH = 200
WINDOW_WIDTH, WINDOW_HEIGHT = GAME_WIDTH + UI_WIDTH, GAME_HEIGHT
BLOCK_SIZE = 20

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake: Power-up Edition")
clock = pygame.time.Clock()

# Fonts and Colors
pygame.font.init()
stat_font = pygame.font.SysFont("monospace", 18)
WHITE, BLACK, RED, GREEN, GOLD, BLUE, DARK_GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (255, 215, 0), (
    0, 100, 255), (40, 40, 40)


def main(high_score):
    snake_body = [[GAME_WIDTH // 2, GAME_HEIGHT // 2]]
    dx, dy = BLOCK_SIZE, 0
    score, base_fps, fps = 0, 12, 12

    # Food
    food_x = random.randrange(0, GAME_WIDTH, BLOCK_SIZE)
    food_y = random.randrange(0, GAME_HEIGHT, BLOCK_SIZE)

    # Special Items System
    special_item = {"pos": None, "type": None, "expiry": 0}
    # Active power-up effect timer
    active_effect = {"type": None, "expiry": 0, "duration": 0}

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK_SIZE
                elif event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK_SIZE, 0

        # --- Spawning Logic ---
        # 1% chance every frame to spawn a special item if one isn't already there
        if not special_item["pos"] and random.random() < 0.01:
            special_item["pos"] = [random.randrange(0, GAME_WIDTH, BLOCK_SIZE),
                                   random.randrange(0, GAME_HEIGHT, BLOCK_SIZE)]
            special_item["type"] = random.choice(["gold", "slow", "scissors"])
            special_item["expiry"] = current_time + 5000  # 5 seconds

        # Remove expired items
        if special_item["pos"] and current_time > special_item["expiry"]:
            special_item = {"pos": None, "type": None, "expiry": 0}

        # --- Game Logic ---
        new_head = [(snake_body[0][0] + dx) % GAME_WIDTH, (snake_body[0][1] + dy) % GAME_HEIGHT]

        if new_head in snake_body:
            if score > high_score: high_score = score
            running = False
        else:
            snake_body.insert(0, new_head)

            # Eating Standard Food
            if new_head[0] == food_x and new_head[1] == food_y:
                score += 1
                food_x, food_y = random.randrange(0, GAME_WIDTH, BLOCK_SIZE), random.randrange(0, GAME_HEIGHT,
                                                                                               BLOCK_SIZE)

            # Eating Special Item
            elif special_item["pos"] and new_head[0] == special_item["pos"][0] and new_head[1] == special_item["pos"][
                1]:
                effect_type = special_item["type"]
                if effect_type == "gold":
                    score += 5
                elif effect_type == "slow":
                    fps = 5
                    active_effect = {"type": "slow", "expiry": current_time + 5000, "duration": 5000}
                elif effect_type == "scissors":
                    snake_body = snake_body[:max(1, len(snake_body) // 2)]
                special_item = {"pos": None, "type": None, "expiry": 0}
            else:
                snake_body.pop()

        # Expire active effect
        if active_effect["type"] and current_time > active_effect["expiry"]:
            if active_effect["type"] == "slow": fps = base_fps  # Restore speed
            active_effect = {"type": None, "expiry": 0, "duration": 0}

        # --- Drawing ---
        window.fill(BLACK)
        pygame.draw.rect(window, RED, (food_x, food_y, BLOCK_SIZE, BLOCK_SIZE))  # Food

        # Draw Special Item
        if special_item["pos"]:
            color = GOLD if special_item["type"] == "gold" else (
                BLUE if special_item["type"] == "slow" else (255, 0, 255))
            pygame.draw.rect(window, color, (special_item["pos"][0], special_item["pos"][1], BLOCK_SIZE, BLOCK_SIZE))

        for b in snake_body: pygame.draw.rect(window, GREEN, (b[0], b[1], BLOCK_SIZE, BLOCK_SIZE))

        # UI
        pygame.draw.rect(window, DARK_GRAY, (GAME_WIDTH, 0, UI_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(window, BLUE, (GAME_WIDTH, 0), (GAME_WIDTH, WINDOW_HEIGHT), 3)
        window.blit(stat_font.render(f"Score: {score}", True, WHITE), (GAME_WIDTH + 10, 20))
        window.blit(stat_font.render(f"Best:  {high_score}", True, WHITE), (GAME_WIDTH + 10, 50))

        # Special item countdown (on field)
        if special_item["pos"]:
            bar_pct = max(0, special_item["expiry"] - current_time) / 5000
            window.blit(stat_font.render(f"Pickup: {special_item['type']}", True, GOLD), (GAME_WIDTH + 10, 100))
            pygame.draw.rect(window, (80, 80, 80), (GAME_WIDTH + 10, 125, 180, 12))
            pygame.draw.rect(window, GOLD, (GAME_WIDTH + 10, 125, int(180 * bar_pct), 12))

        # Active slow effect countdown
        if active_effect["type"] == "slow":
            bar_pct = max(0, active_effect["expiry"] - current_time) / active_effect["duration"]
            window.blit(stat_font.render("SLOW MODE", True, BLUE), (GAME_WIDTH + 10, 160))
            pygame.draw.rect(window, (80, 80, 80), (GAME_WIDTH + 10, 185, 180, 12))
            pygame.draw.rect(window, BLUE, (GAME_WIDTH + 10, 185, int(180 * bar_pct), 12))

        pygame.display.flip()
        clock.tick(fps)

    main(high_score)


if __name__ == "__main__": main(0)