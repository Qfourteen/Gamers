# 충돌 감지

> 이 예제에서는 충돌을 감지하고 이후 동작을 정의하는 예제입니다.

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("충돌 감지 예제")

clock = pygame.time.Clock()

rect1 = pygame.Rect(100, 100, 100, 100)
rect2 = pygame.Rect(300, 250, 100, 100)
speed = 5

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rect1.x -= speed
    if keys[pygame.K_RIGHT]:
        rect1.x += speed
    if keys[pygame.K_UP]:
        rect1.y -= speed
    if keys[pygame.K_DOWN]:
        rect1.y += speed

    if rect1.colliderect(rect2):
        color = (255, 0, 0)  # 충돌 시 빨간색
    else:
        color = (0, 255, 0)  # 기본 초록색

    pygame.draw.rect(screen, color, rect1)
    pygame.draw.rect(screen, (0, 0, 255), rect2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```