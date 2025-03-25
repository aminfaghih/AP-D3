import pygame
import sqlite3
import json
import uuid
from authentication import authenticate_players
from settings import settings_screen
from leaderboard import leaderboard_screen
from game import Game
from player import Player
from user import User
from load import load_saved_game

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Shooter")
pygame.display.set_icon(pygame.image.load('icon.png'))

# Load assets
shoot_sound = pygame.mixer.Sound('shoot.wav')
hit_sound = pygame.mixer.Sound('hit.wav')
auth_background = pygame.transform.scale(
    pygame.image.load('background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)
)
game_background = pygame.transform.scale(
    pygame.image.load('game_background.jpg').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT - 50)
)

# Play background music at startup
pygame.mixer.music.load('background_music.mp3')
sound_volume = 1.0  # Initial volume
pygame.mixer.music.set_volume(sound_volume)
pygame.mixer.music.play(-1)  # Loop indefinitely
shoot_sound.set_volume(sound_volume)
hit_sound.set_volume(sound_volume)

# Initial control schemes
control_schemes = {
    "scheme1": {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "shoot": pygame.K_SPACE},
    "scheme2": {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "shoot": pygame.K_RETURN}
}
player1_controls = control_schemes["scheme1"]
player2_controls = control_schemes["scheme2"]

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (uuid TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS matches
             (match_id INTEGER PRIMARY KEY AUTOINCREMENT,
              player1_uuid TEXT, player2_uuid TEXT, player1_score INTEGER,
              player2_score INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS saved_games
             (game_uuid TEXT PRIMARY KEY,
              player1_uuid TEXT, player2_uuid TEXT, game_state TEXT,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

def save_scores(player1, player2, conn):
    """Saves the match scores to the database."""
    c = conn.cursor()
    c.execute("INSERT INTO matches (player1_uuid, player2_uuid, player1_score, player2_score) VALUES (?, ?, ?, ?)",
              (player1.uuid, player2.uuid, player1.score, player2.score))
    conn.commit()

def save_game_state(game, conn):
    """Saves the current game state to the database."""
    game_uuid = str(uuid.uuid4())
    game_state = json.dumps(game.to_dict())
    c = conn.cursor()
    c.execute("INSERT INTO saved_games (game_uuid, player1_uuid, player2_uuid, game_state) VALUES (?, ?, ?, ?)",
              (game_uuid, game.player1.uuid, game.player2.uuid, game_state))
    conn.commit()
    print(f"Game saved with ID: {game_uuid}")

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def initial_menu(screen, background_image):
    """Displays the initial menu with options."""
    font = pygame.font.Font(None, 32)
    options = [
        ("New Game", pygame.Rect(100, 100, 150, 50), (0, 255, 0), "start_new_game"),
        ("Load Game", pygame.Rect(100, 160, 150, 50), (0, 0, 255), "load_game"),
        ("Leaderboard", pygame.Rect(100, 220, 150, 50), (255, 165, 0), "leaderboard"),
        ("Settings", pygame.Rect(100, 280, 150, 50), (128, 128, 128), "settings"),
        ("Quit", pygame.Rect(100, 340, 150, 50), (255, 0, 0), "quit")
    ]

    while True:
        screen.blit(background_image, (0, 0))
        draw_text(screen, "Main Menu", (10, 10), font)
        for text, rect, color, value in options:
            pygame.draw.rect(screen, color, rect)
            draw_text(screen, text, (rect.x + 10, rect.y + 15), font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for _, rect, _, value in options:
                    if rect.collidepoint(event.pos):
                        if value == "quit":
                            pygame.quit()
                            exit()
                        return value
        clock.tick(30)

def main():
    global player1_controls, player2_controls, sound_volume
    while True:
        choice = initial_menu(screen, auth_background)
        if choice in ["start_new_game", "load_game"]:
            # Authenticate players with sign up, login, and back options
            player1_user, player2_user = authenticate_players(
                screen, conn, auth_background, settings_screen, leaderboard_screen,
                control_schemes, player1_controls, player2_controls, sound_volume,
                shoot_sound, hit_sound, allow_signup=(choice == "start_new_game")
            )
            if not player1_user or not player2_user:
                continue  # Back to main menu

            # Pause music before entering game
            pygame.mixer.music.pause()

            if choice == "start_new_game":
                player1 = Player(player1_user, player1_controls, (255, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT)
                player2 = Player(player2_user, player2_controls, (0, 0, 255), SCREEN_WIDTH, SCREEN_HEIGHT)
                game = Game(player1, player2, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif choice == "load_game":
                saved_game = load_saved_game(screen, conn, player1_user, player2_user, SCREEN_WIDTH, SCREEN_HEIGHT)
                if saved_game:
                    game = saved_game
                else:
                    pygame.mixer.music.unpause()
                    continue  # Back to menu

            while True:
                font = pygame.font.Font(None, 40)
                paused = False
                pause_start_time = None
                pause_menu_font = pygame.font.Font(None, 50)
                resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
                quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)

                # Countdown only for new games, timers start after countdown
                if game.is_new:
                    screen.blit(game_background, (0, 50))
                    pygame.display.flip()
                    countdown_font = pygame.font.Font(None, 100)
                    for i in range(3, 0, -1):
                        screen.blit(game_background, (0, 50))
                        text = countdown_font.render(str(i), True, (255, 255, 255))
                        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 + 25))
                        pygame.display.flip()
                        pygame.time.wait(1000)
                    screen.blit(game_background, (0, 50))
                    text = countdown_font.render("Go!", True, (255, 255, 255))
                    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 + 25))
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    game.player1.start_timer()
                    game.player2.start_timer()
                    game.is_new = False  # Set to False after countdown

                while game.running:
                    dt = clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            game.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                if paused:
                                    pause_duration = pygame.time.get_ticks() - pause_start_time
                                    for player in [game.player1, game.player2]:
                                        if player.start_time is not None:
                                            player.pause_offset += pause_duration
                                    paused = False
                                    pause_start_time = None
                                else:
                                    pause_start_time = pygame.time.get_ticks()
                                    paused = True
                            elif not paused:
                                if event.key == player1_controls["shoot"] and not game.player1.frozen:
                                    game.player1.shoot(game, shoot_sound, hit_sound)
                                elif event.key == player2_controls["shoot"] and not game.player2.frozen:
                                    game.player2.shoot(game, shoot_sound, hit_sound)
                        elif event.type == pygame.MOUSEBUTTONDOWN and paused:
                            if resume_rect.collidepoint(event.pos):
                                pause_duration = pygame.time.get_ticks() - pause_start_time
                                for player in [game.player1, game.player2]:
                                    if player.start_time is not None:
                                        player.pause_offset += pause_duration
                                paused = False
                                pause_start_time = None
                            elif quit_rect.collidepoint(event.pos):
                                save_game_state(game, conn)
                                game.running = False

                    if not paused:
                        keys = pygame.key.get_pressed()
                        game.player1.move_aim(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
                        game.player2.move_aim(keys, SCREEN_WIDTH, SCREEN_HEIGHT)
                        game.update(dt)

                    game.draw(screen, game_background, font)
                    if paused:
                        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 128))
                        screen.blit(overlay, (0, 0))
                        draw_text(screen, "Paused", (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100), pause_menu_font, (255, 255, 255))
                        pygame.draw.rect(screen, (0, 255, 0), resume_rect)
                        draw_text(screen, "Resume", (resume_rect.x + 50, resume_rect.y + 15), font, (255, 255, 255))
                        pygame.draw.rect(screen, (255, 0, 0), quit_rect)
                        draw_text(screen, "Save and Quit", (quit_rect.x + 20, quit_rect.y + 15), font, (255, 255, 255))
                    pygame.display.flip()

                # Save scores
                save_scores(game.player1, game.player2, conn)

                # End-game screen
                replay_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, (SCREEN_HEIGHT // 2)+10, 200, 50)
                menu_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, (SCREEN_HEIGHT // 2)+10, 200, 50)
                end_game_running = True
                replay = False
                menu = False

                while end_game_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            end_game_running = False
                            menu = True
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if replay_rect.collidepoint(event.pos):
                                replay = True
                                end_game_running = False
                            elif menu_rect.collidepoint(event.pos):
                                pygame.mixer.music.unpause()  # Resume music
                                menu = True
                                end_game_running = False

                    screen.fill((0, 0, 0))
                    draw_text(screen, "Game Over", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100), font, (255, 255, 255))
                    draw_text(screen, f"{game.player1.name}: {game.player1.score}", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50), font, game.player1.color)
                    draw_text(screen, f"{game.player2.name}: {game.player2.score}", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20), font, game.player2.color)
                    pygame.draw.rect(screen, (0, 255, 0), replay_rect)
                    draw_text(screen, "Replay", (replay_rect.x + 50, replay_rect.y + 15), font, (255, 255, 255))
                    pygame.draw.rect(screen, (255, 0, 0), menu_rect)
                    draw_text(screen, "Back to Menu", (menu_rect.x + 20, menu_rect.y + 15), font, (255, 255, 255))
                    pygame.display.flip()
                    clock.tick(30)

                if menu:
                    break
                elif replay:
                    player1 = Player(player1_user, player1_controls, (255, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT)
                    player2 = Player(player2_user, player2_controls, (0, 0, 255), SCREEN_WIDTH, SCREEN_HEIGHT)
                    game = Game(player1, player2, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif choice == "leaderboard":
            leaderboard_screen(screen, conn, auth_background)
        elif choice == "settings":
            player1_controls, player2_controls, sound_volume = settings_screen(
                screen, control_schemes, player1_controls, player2_controls,
                sound_volume, shoot_sound, hit_sound, auth_background
            )
            pygame.mixer.music.set_volume(sound_volume)  # Update music volume

if __name__ == "__main__":
    main()