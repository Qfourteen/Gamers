import sys
import random
import pygame
import asyncio

# ===== 설정 상수 =====
SCREENRECT = pygame.Rect(0, 0, 480, 640)
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -10
SCROLL_TRIGGER = SCREENRECT.height // 3  # 플레이어가 화면 위 1/3 위치에 오면 스크롤 발생

PLAYER_SIZE = (40, 50)
PLAYER_COLOR = (0, 150, 255)

PLATFORM_HEIGHT = 15
PLATFORM_COLOR = (0, 200, 0)
PLATFORM_WIDTH_RANGE = (60, 120)
PLATFORM_GAP_Y = (70, 120)  # 플랫폼 간 최소 / 최대 y 간격

BG_COLOR = (30, 30, 30)
score = 0

def spawn_platform(y: int, full_width: bool = False) -> pygame.sprite.Sprite:
    if full_width:
        width = SCREENRECT.width
        x = 0
    else:
        width = random.randint(*PLATFORM_WIDTH_RANGE)
        x = random.randint(0, SCREENRECT.width - width)
    platform = pygame.Surface((width, PLATFORM_HEIGHT))
    platform.fill(PLATFORM_COLOR)
    sprite = pygame.sprite.Sprite()
    sprite.image = platform
    sprite.rect = platform.get_rect(topleft=(x, y))
    return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.Vector2(0, 0)
        self.score = 0

    def update(self, platforms: pygame.sprite.Group):
        keys = pygame.key.get_pressed()
        self.vel.x = -5 if keys[pygame.K_LEFT] else 5 if keys[pygame.K_RIGHT] else 0

        # 점프: 바닥과 접촉 중 & 스페이스
        if keys[pygame.K_SPACE]:
            self.rect.y += 1
            on_ground = pygame.sprite.spritecollideany(self, platforms)
            self.rect.y -= 1
            if on_ground:
                self.vel.y = JUMP_VELOCITY

        # 중력 적용
        self.vel.y += GRAVITY
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        # 화면 래핑
        if self.rect.right < 0:
            self.rect.left = SCREENRECT.width
        elif self.rect.left > SCREENRECT.width:
            self.rect.right = 0

        # 플랫폼 충돌 처리
        if self.vel.y > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            for platform in hits:
                if self.rect.bottom <= platform.rect.centery + self.vel.y:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0


async def main():
    global score # 점수 변수
    await asyncio.sleep(1)
    pygame.init()
    screen = pygame.display.set_mode((SCREENRECT.width, SCREENRECT.height))
    pygame.display.set_caption("Endless Climber")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # 시작 지점에 전체 넓이 플랫폼 생성
    ground = spawn_platform(SCREENRECT.height - 40, full_width=True)
    platforms.add(ground)
    all_sprites.add(ground)

    y = SCREENRECT.height - 100
    while y > -SCREENRECT.height:
        p = spawn_platform(y)
        platforms.add(p)
        all_sprites.add(p)
        y -= random.randint(*PLATFORM_GAP_Y)

    player = Player(SCREENRECT.width // 2, SCREENRECT.height - 60)
    all_sprites.add(player)

    offset_y = 0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 업데이트
        player.update(platforms)

        # 게임 오버: 플레이어가 화면 하단 벗어나면 종료
        if player.rect.top > SCREENRECT.height:
            running = False

        # 카메라 스크롤
        if player.rect.top <= SCROLL_TRIGGER:
            shift = SCROLL_TRIGGER - player.rect.top
            player.rect.top = SCROLL_TRIGGER
            for sprite in list(platforms):
                sprite.rect.y += shift

            offset_y += shift
            player.score = max(player.score, offset_y)

        # 화면 밖 플랫폼 제거 및 새 플랫폼 생성(항상 화면 위 랜덤 위치에)
        for plat in list(platforms):
            if plat.rect.top >= SCREENRECT.height:
                plat.kill()
                # 위 화면에 새 플랫폼 배치 (y는 음수 영역)
                new_y = random.randint(-PLATFORM_GAP_Y[1], -PLATFORM_GAP_Y[0])
                new_p = spawn_platform(new_y)
                platforms.add(new_p)
                all_sprites.add(new_p)

        # 렌더링
        screen.fill(BG_COLOR)
        all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {player.score // 10}", True, (255, 255, 255))
        score = player.score # 점수 등록
        screen.blit(score_surf, (10, 10))

        pygame.display.flip()
        await asyncio.sleep(0.01)

    pygame.quit()

asyncio.ensure_future(main())
