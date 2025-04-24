# 음악 설정

> 이 예제에서는 화면에 음악이 나오도록 설정하는 예제입니다.

## 주의

웹에서는 배경음악 자동 재생을 막아두는 경우가 많습니다.
이 경우, 사용자가 수동으로 설정을 바꿔야 정상적으로 플레이되는 점을 감안하여 개발해야 합니다.

```python
import pygame
pygame.init()

# 사운드 초기화
pygame.mixer.init()

# 배경 음악 로드 및 재생; wav 또는 mp3 파일
# 음악 파일을 다운로드 받아서 직접 경로 설정을 해야 합니다.
pygame.mixer.music.load("backgournd.wav")
pygame.mixer.music.play(-1)  # 무한 반복

# 효과음 로드; wav 또는 mp3 파일
sound_effect = pygame.mixer.Sound("button.mp3")

# 화면 설정
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("사운드 예제")

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            sound_effect.play()

    pygame.display.flip()

pygame.quit()
```