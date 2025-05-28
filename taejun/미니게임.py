import pygame
import sys
import random

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("서바이벌 발판 게임")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# 글꼴
font = pygame.font.SysFont(None, 32)

# 발판 위치
tile_positions = [
    (250, 100), (310, 100),
    (210, 160), (270, 160), (330, 160),
    (250, 220), (310, 220)
]

TILE_SIZE = 50
rankings = []

# 도트 타일 이미지 로드
tile_image = pygame.image.load("dot_tile.png").convert_alpha()
tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))

# 텍스트 출력 함수
def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# 발판 그리기 함수
def draw_tiles(tiles, removed, highlight=None, animate_highlight=False, anim_progress=0):
    for i, rect in enumerate(tiles):
        if i in removed:
            continue

        # 일반 발판
        if i == highlight and animate_highlight:
            # 애니메이션 시 확대된 이미지 표시
            scale = 1.1 + 0.1 * (anim_progress % 2)
            new_size = int(TILE_SIZE * scale)
            enlarged = pygame.transform.scale(tile_image, (new_size, new_size))
            offset = (new_size - TILE_SIZE) // 2
            screen.blit(enlarged, (rect.x - offset, rect.y - offset))
        else:
            screen.blit(tile_image, rect)

        # 테두리
        if i == highlight:
            pygame.draw.rect(screen, GREEN, rect, 3)
        else:
            pygame.draw.rect(screen, BLACK, rect, 2)

# 게임 오버 화면
def game_over(score):
    global rankings
    rankings.append(score)
    rankings = sorted(rankings, reverse=True)[:5]
    screen.fill(WHITE)
    draw_text("Game Over!", 220, 150, RED)
    draw_text(f"Score: {score}", 230, 180)
    draw_text("Top 5:", 250, 220)
    for idx, s in enumerate(rankings):
        draw_text(f"{idx+1}. {s}", 260, 250 + idx * 25)
    pygame.display.flip()
    pygame.time.wait(3000)

# 클릭 애니메이션 함수
def animate_click(tiles, removed_tiles, clicked_index, score, rope_used):
    for i in range(10):  # 10프레임 정도 깜빡이게
        screen.fill(WHITE)
        draw_tiles(tiles, removed_tiles, highlight=clicked_index, animate_highlight=True, anim_progress=i)
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Rope Used: {'Yes' if rope_used else 'No'}", 10, 40)
        pygame.display.flip()
        clock.tick(30)

# 메인 게임 루프
def main():
    tiles = [pygame.Rect(*pos, TILE_SIZE, TILE_SIZE) for pos in tile_positions]
    alive = True
    score = 0
    rope_used = False

    while alive:
        removed_tiles = []

        screen.fill(WHITE)
        draw_tiles(tiles, removed_tiles)
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Rope Used: {'Yes' if rope_used else 'No'}", 10, 40)
        pygame.display.flip()

        clicked_index = None
        rope_active = False
        waiting_click = True

        # 발판 클릭 전 대기
        while waiting_click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not rope_used:
                        rope_active = True
                        rope_used = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, rect in enumerate(tiles):
                        if rect.collidepoint(pos):
                            clicked_index = i
                            waiting_click = False
                            break
            clock.tick(60)

        # 클릭 애니메이션
        animate_click(tiles, removed_tiles, clicked_index, score, rope_used)

        # 발판 무작위로 3개 또는 4개 제거
        all_indexes = list(range(len(tiles)))
        remove_count = 3 if random.random() < 0.85 else 4
        removed_this_turn = random.sample(all_indexes, remove_count)

        # 발판 사라진 상태 보여주기
        screen.fill(WHITE)
        draw_tiles(tiles, removed_this_turn, highlight=clicked_index)
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Rope Used: {'Yes' if rope_used else 'No'}", 10, 40)
        pygame.display.flip()
        pygame.time.wait(1500)

        # 생존 판단
        if clicked_index in removed_this_turn:
            if rope_active:
                pass  # 밧줄 덕분에 생존
            else:
                alive = False
                game_over(score)
                return

        # 생존 시 점수 증가
        score += 1
        clock.tick(60)

# 프로그램 실행
while True:
    main()
