# 마우스 클릭 감지

> 이 예제는 마우스 클릭을 감지하고 처리하는 방법을 보여주는 예제입니다.

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("마우스 클릭으로 원 그리기")

clock = pygame.time.Clock()
circles = []

running = True
while running:
    screen.fill((255, 255, 255))  # 배경을 흰색으로 설정

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            circles.append(pos)

    for pos in circles:
        pygame.draw.circle(screen, (0, 0, 255), pos, 30)  # 파란색 원

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```