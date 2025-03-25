import pygame
import sqlite3
import json
from game import Game
from datetime import datetime

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def load_saved_game(screen, conn, player1_user, player2_user, screen_width, screen_height):
    """Loads a saved game for the two specified players."""
    c = conn.cursor()
    c.execute("""
        SELECT game_uuid, game_state, timestamp
        FROM saved_games
        WHERE (player1_uuid = ? AND player2_uuid = ?) OR (player1_uuid = ? AND player2_uuid = ?)
        ORDER BY timestamp DESC
    """, (player1_user.uuid, player2_user.uuid, player2_user.uuid, player1_user.uuid))
    saved_games = c.fetchall()

    if not saved_games:
        font = pygame.font.Font(None, 32)
        screen.blit(pygame.transform.scale(pygame.image.load('background.jpg').convert(), (screen_width, screen_height)), (0, 0))
        draw_text(screen, "No saved games found.", (300, 300), font, (255, 0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)
        return None

    font = pygame.font.Font(None, 32)
    selected = 0
    clock = pygame.time.Clock()
    background = pygame.transform.scale(pygame.image.load('background.jpg').convert(), (screen_width, screen_height))

    while True:
        screen.blit(background, (0, 0))
        draw_text(screen, "Select a saved game (Up/Down, Enter to load, Esc to back)", (150, 50), font)
        for i, (game_uuid, game_state, timestamp) in enumerate(saved_games):
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime("%m/%d/%Y %I:%M %p").replace("AM", "am").replace("PM", "pm")
            text = f"Game {i + 1}: {time_str} (ID: {game_uuid})"
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            draw_text(screen, text, (150, 100 + i * 40), font, color)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected > 0:
                    selected -= 1
                elif event.key == pygame.K_DOWN and selected < len(saved_games) - 1:
                    selected += 1
                elif event.key == pygame.K_RETURN:
                    game_data = json.loads(saved_games[selected][1])
                    return Game.from_dict(game_data, player1_user, player2_user, screen_width, screen_height)
                elif event.key == pygame.K_ESCAPE:
                    return None  # Back to menu
        clock.tick(30)