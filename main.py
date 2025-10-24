import pygame
pygame.init()

screen = pygame.display.set_mode((450, 800), pygame.RESIZABLE)
pygame.display.set_caption("LVLLife")

# colors
color1 = 0
color2 = 0
color3 = 0
background_color = (10, 0, 10)
text_color = (255, 255, 255)

font = pygame.font.Font(None, 40)
button_rect = pygame.Rect(125, 350, 200, 60)
button_text = font.render("Click Me", True, text_color)

clock = pygame.time.Clock()
last_click_time = 0
click_delay = 150  # milliseconds
counter = 0

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # button logic
    if button_rect.collidepoint(mouse_pos):
        color = (min(color1 + 40, 255), min(color2 + 40, 255), min(color3 + 40, 255))
        if mouse_pressed[0] and current_time - last_click_time > click_delay:
            counter += 5
            color1 += 5
            if color1 > 255:
                color1 = 0
                color3 += 5
                if color3 > 255:
                    color3 = 0
                    color2 += 5
                    if color2 > 255:
                        color2 = 0
            last_click_time = current_time
    else:
        color = (color1, color2, color3)

    # drawing
    screen.fill(background_color)
    pygame.draw.rect(screen, color, button_rect, border_radius=10)

    counter_text = font.render(f"RGB: ({color1}, {color2}, {color3})  Count: {counter}", True, text_color)
    counter_rect = counter_text.get_rect(center=(button_rect.centerx, button_rect.top - 40))
    screen.blit(counter_text, counter_rect)

    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
