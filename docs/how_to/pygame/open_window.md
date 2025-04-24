# 창 열기

> 이 예제는 pygame에서 가장 기초적인 창을 만들고 보여주는 예제입니다.

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame 예제")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 255))  # 배경색 파란색
    pygame.draw.circle(screen, (255, 255, 0), (320, 240), 50)  # 노란 원 그리기
    pygame.display.flip()

pygame.quit()
```

