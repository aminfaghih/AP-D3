import pygame
import sqlite3
import uuid
from user import User

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def get_text_input(screen, prompt, background_image):
    """Collects text input from the user with a back option."""
    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(300, 300, 200, 32)
    back_rect = pygame.Rect(300, 340, 100, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    text = ''
    active = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    color = color_active if active else color_inactive
                elif back_rect.collidepoint(event.pos):
                    return None
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.blit(background_image, (0, 0))
        draw_text(screen, prompt, (300, 260), font)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.draw.rect(screen, (255, 0, 0), back_rect)
        draw_text(screen, "Back", (back_rect.x + 20, back_rect.y + 5), font)
        pygame.display.flip()
        clock.tick(30)

def get_password_input(screen, prompt, background_image):
    """Collects password input with asterisks and a back option."""
    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(300, 300, 200, 32)
    back_rect = pygame.Rect(300, 340, 100, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    text = ''
    display_text = ''
    active = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    color = color_active if active else color_inactive
                elif back_rect.collidepoint(event.pos):
                    return None
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                        display_text = '*' * len(text)
                    else:
                        text += event.unicode
                        display_text = '*' * len(text)

        screen.blit(background_image, (0, 0))
        draw_text(screen, prompt, (300, 260), font)
        txt_surface = font.render(display_text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.draw.rect(screen, (255, 0, 0), back_rect)
        draw_text(screen, "Back", (back_rect.x + 20, back_rect.y + 5), font)
        pygame.display.flip()
        clock.tick(30)

def sign_up_screen(screen, conn, background_image):
    """Handles user sign-up."""
    while True:
        username = get_text_input(screen, "Enter username:", background_image)
        if username is None:
            return None
        if not username:
            continue
        password = get_password_input(screen, "Enter password:", background_image)
        if password is None:
            return None
        if not password:
            continue
        c = conn.cursor()
        try:
            user_uuid = str(uuid.uuid4())
            c.execute("INSERT INTO users (uuid, username, password) VALUES (?, ?, ?)",
                      (user_uuid, username, password))
            conn.commit()
            return User(user_uuid, username, password)
        except sqlite3.IntegrityError:
            screen.blit(background_image, (0, 0))
            font = pygame.font.Font(None, 32)
            draw_text(screen, "Username already taken.", (300, 400), font, (255, 0, 0))
            pygame.display.flip()
            pygame.time.wait(2000)

def login_screen(screen, conn, background_image):
    """Handles user login."""
    while True:
        username = get_text_input(screen, "Enter username:", background_image)
        if username is None:
            return None
        if not username:
            continue
        password = get_password_input(screen, "Enter password:", background_image)
        if password is None:
            return None
        c = conn.cursor()
        c.execute("SELECT uuid, username, password FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        if user_data and user_data[2] == password:
            return User(user_data[0], user_data[1], user_data[2])
        screen.blit(background_image, (0, 0))
        font = pygame.font.Font(None, 32)
        draw_text(screen, "Invalid username or password.", (300, 400), font, (255, 0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)

def authenticate_players(screen, conn, background_image, settings_screen, leaderboard_screen,
                         control_schemes, player1_controls, player2_controls, sound_volume,
                         shoot_sound, hit_sound, allow_signup=True):
    """Authenticate two players with options for sign-up, login, settings, and leaderboard."""
    font = pygame.font.Font(None, 32)
    player1 = None
    player2 = None
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    button_data = []
    if allow_signup:
        button_data.append(("Sign Up", (0, 255, 0), "signup"))
    button_data.append(("Login", (0, 0, 255), "login"))
    button_data.append(("Settings", (128, 128, 128), "settings"))
    button_data.append(("Leaderboard", (255, 165, 0), "leaderboard"))
    button_data.append(("Back", (255, 0, 0), "back"))

    button_height = 50
    spacing = 10
    total_height = len(button_data) * button_height + (len(button_data) - 1) * spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2
    start_x = 300

    buttons = []
    for i, (text, color, action) in enumerate(button_data):
        text_surface = font.render(text, True, (0, 0, 0))
        width = text_surface.get_width() + 20
        y = start_y + i * (button_height + spacing)
        rect = pygame.Rect(start_x, y, width, button_height)
        buttons.append((text, rect, color, action))

    while True:
        if not player1:
            prompt = "Player 1: Choose an option"
        elif not player2:
            prompt = "Player 2: Choose an option"
        else:
            return player1, player2

        screen.blit(background_image, (0, 0))
        draw_text(screen, prompt, (300, 120), font)
        for text, rect, color, _ in buttons:
            pygame.draw.rect(screen, color, rect)
            draw_text(screen, text, (rect.x + 10, rect.y + 15), font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for _, rect, _, action in buttons:
                    if rect.collidepoint(event.pos):
                        if action == "signup" and allow_signup:
                            user = sign_up_screen(screen, conn, background_image)
                            if user and not player1:
                                player1 = user
                            elif user and not player2 and user.uuid != player1.uuid:
                                player2 = user
                        elif action == "login":
                            user = login_screen(screen, conn, background_image)
                            if user and not player1:
                                player1 = user
                            elif user and not player2 and user.uuid != player1.uuid:
                                player2 = user
                        elif action == "settings":
                            player1_controls, player2_controls, sound_volume = settings_screen(
                                screen, control_schemes, player1_controls, player2_controls,
                                sound_volume, shoot_sound, hit_sound, background_image
                            )
                        elif action == "leaderboard":
                            leaderboard_screen(screen, conn, background_image)
                        elif action == "back":
                            return None, None
        clock.tick(30)