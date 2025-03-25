import pygame
from datetime import datetime

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def leaderboard_screen(screen, conn, background_image):
    """Displays the top 5 matches by highest score."""
    c = conn.cursor()
    c.execute("""
        SELECT u1.username, u2.username, m.player1_score, m.player2_score, m.timestamp
        FROM matches m
        JOIN users u1 ON m.player1_uuid = u1.uuid
        JOIN users u2 ON m.player2_uuid = u2.uuid
        ORDER BY MAX(m.player1_score, m.player2_score) DESC
        LIMIT 5
    """)
    matches = c.fetchall()
    font = pygame.font.Font(None, 32)
    screen.blit(background_image, (0, 0))
    draw_text(screen, "Leaderboard - Top 5 Matches", (300, 50), font)
    for i, (p1, p2, p1_score, p2_score, timestamp) in enumerate(matches):
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        time_str = dt.strftime("%m/%d/%Y %I:%M %p").replace("AM", "am").replace("PM", "pm")
        text = f"{p1}: {p1_score} vs {p2}: {p2_score} ({time_str})"
        draw_text(screen, text, (300, 100 + i * 40), font)
    draw_text(screen, "Press any key to return.", (300, 300), font)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()