import pygame
import sys

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("LVLLife Prototype")

font = pygame.font.SysFont("Fixedsys", 28)
clock = pygame.time.Clock()

# --- Data ---
tasks = []
xp = 0
level = 1
input_text = ""
adding_task = True  # start in typing mode

# --- Functions ---
def draw_text(text, x, y, color=(255, 255, 255)):
    """Draw text easily."""
    screen.blit(font.render(text, True, color), (x, y))

def get_level(xp):
    """Each 100 XP = 1 level."""
    return xp // 100 + 1

# --- Main Loop ---
while True:
    screen.fill((20, 20, 30))

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if adding_task:
            # Typing mode
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        tasks.append({"text": input_text, "done": False})
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_TAB:
                    adding_task = False
                else:
                    input_text += event.unicode
        else:
            # Click mode
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, task in enumerate(tasks):
                    y = 120 + i * 40
                    if 50 <= mx <= 70 and y <= my <= y + 30:
                        if not task["done"]:
                            task["done"] = True
                            xp += 50
                            level = get_level(xp)
                # Press TAB to switch back
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                adding_task = True

    # --- Draw ---
    draw_text(f"LVL: {level} | XP: {xp}", 50, 20, (180, 200, 255))
    draw_text("TAB = switch modes (Add / Complete)", 50, 60, (150, 150, 200))

    if adding_task:
        draw_text("Add task:", 50, 100, (255, 255, 150))
        draw_text(input_text + "|", 180, 100, (255, 255, 255))
    else:
        for i, task in enumerate(tasks):
            y = 120 + i * 40
            if task["done"]:
                draw_text("✓", 50, y, (0, 255, 100))
                draw_text(task["text"], 80, y, (100, 255, 100))
            else:
                draw_text("[ ]", 50, y, (255, 255, 255))
                draw_text(task["text"], 90, y, (255, 255, 255))

    pygame.display.flip()
    clock.tick(30)
