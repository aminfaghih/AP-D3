import pygame

def settings_screen(screen, control_schemes, player1_controls, player2_controls, sound_volume,
                    shoot_sound, hit_sound, background_image):
    """Allows players to adjust sound volume and set custom controls."""
    font = pygame.font.Font(None, 32)
    mute_rect = pygame.Rect(100, 100, 100, 50)
    unmute_rect = pygame.Rect(100, 160, 100, 50)
    p1_set_controls_rect = pygame.Rect(100, 220, 150, 50)
    p2_set_controls_rect = pygame.Rect(300, 220, 150, 50)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mute_rect.collidepoint(event.pos):
                    sound_volume = 0
                    pygame.mixer.music.set_volume(0)
                    shoot_sound.set_volume(0)
                    hit_sound.set_volume(0)
                elif unmute_rect.collidepoint(event.pos):
                    sound_volume = 1.0
                    pygame.mixer.music.set_volume(1.0)
                    shoot_sound.set_volume(1.0)
                    hit_sound.set_volume(1.0)
                elif p1_set_controls_rect.collidepoint(event.pos):
                    custom = get_custom_controls(screen, "Player 1", background_image)
                    player1_controls.clear()
                    player1_controls.update(custom)
                elif p2_set_controls_rect.collidepoint(event.pos):
                    custom = get_custom_controls(screen, "Player 2", background_image)
                    player2_controls.clear()
                    player2_controls.update(custom)
                else:
                    return player1_controls, player2_controls, sound_volume
        screen.blit(background_image, (0, 0))
        draw_text(screen, "Settings", (10, 10), font)
        pygame.draw.rect(screen, (255, 0, 0), mute_rect)
        draw_text(screen, "Mute", (110, 110), font)
        pygame.draw.rect(screen, (0, 255, 0), unmute_rect)
        draw_text(screen, "Unmute", (110, 170), font)
        pygame.draw.rect(screen, (255, 165, 0), p1_set_controls_rect)
        draw_text(screen, "P1: Set", (110, 230), font)
        pygame.draw.rect(screen, (0, 191, 255), p2_set_controls_rect)
        draw_text(screen, "P2: Set", (310, 230), font)
        pygame.display.flip()
        clock.tick(30)

def get_custom_controls(screen, player_name, background_image):
    """Collects custom control inputs from the player."""
    actions = ["up", "down", "left", "right", "shoot"]
    custom_controls = {}
    font = pygame.font.Font(None, 32)
    for action in actions:
        screen.blit(background_image, (0, 0))
        draw_text(screen, f"{player_name}: Press key for {action}", (10, 10), font)
        pygame.display.flip()
        key = wait_for_key()
        custom_controls[action] = key
    return custom_controls

def wait_for_key():
    """Waits for a key press and returns the key code."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return event.key
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)