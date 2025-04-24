# 키보드 입력 감지

> 이제는 키보드 화살표를 이용해서 사각형을 움직이는 예제입니다.
> 키보드 입력을 어떻게 처리해야 할지 알 수 있습니다.

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("움직이는 사각형")

x, y = 400, 300
speed = 5
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((0, 0, 0))  # 배경을 검은색으로 채움

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    pygame.draw.rect(screen, (0, 255, 0), (x, y, 50, 50))  # 초록색 사각형
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```