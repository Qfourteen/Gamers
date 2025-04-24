# 화면 조정

> 이 예제에서는 화면 바깥으로 벗어난 객체가 다시 화면 안으로 들어오도록 설정하는 예제입니다.

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("자동으로 움직이는 원")

x = 0
y = 300
speed = 3
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((255, 255, 255))  # 흰색 배경

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    x += speed
    if x > 800:
        x = -30  # 화면을 벗어나면 다시 왼쪽으로

    pygame.draw.circle(screen, (255, 0, 0), (x, y), 30)  # 빨간색 원

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```