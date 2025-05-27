import asyncio, random, sys, pygame


# ===== 상수 =====
# 화면 크기는 SCREENRECT.size 로 통일
SCREENRECT = pygame.Rect(0, 0, 480, 640)
FPS = 40
PLAYER_SIZE = (40, 40)
PLAYER_SPEED = 6
BULLET_SIZE = (4, 10)
BULLET_SPEED = -10
ENEMY_SIZE = (34, 34)
ENEMY_SPEED_START = 2
ENEMY_SPAWN_INTERVAL = 800      # ms
DIFFICULTY_STEP_MS = 10_000
ENEMY_SPEED_INCREMENT = 0.5

score = 0

# ==== 스프라이트 ====
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            (0,255,255),
            [(PLAYER_SIZE[0]//2,0), (0,PLAYER_SIZE[1]), (PLAYER_SIZE[0],PLAYER_SIZE[1])]
        )

        # SCREENRECT로 midbottom 위치 지정

        self.rect = self.image.get_rect(
            midbottom=(SCREENRECT.centerx, SCREENRECT.bottom - 10)
        )



    def update(self, keys):
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        dy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])   * PLAYER_SPEED

        # 이동 후에도 SCREENRECT 영역을 벗어나지 않도록
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        self.rect.x = max(SCREENRECT.left, min(SCREENRECT.right - PLAYER_SIZE[0], new_x))
        self.rect.y = max(SCREENRECT.top, min(SCREENRECT.bottom - PLAYER_SIZE[1], new_y))



class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.Surface(BULLET_SIZE)

        self.image.fill((255,255,0))

        self.rect = self.image.get_rect(midbottom=(x, y))



    def update(self):

        self.rect.y += BULLET_SPEED

        if self.rect.bottom < SCREENRECT.top:

            self.kill()



class Enemy(pygame.sprite.Sprite):

    def __init__(self, speed):

        super().__init__()

        self.speed = speed

        self.image = pygame.Surface(ENEMY_SIZE)

        self.image.fill((255,0,0))

        # SCREENRECT.width 대신 SCREENRECT.right 사용

        x_pos = random.randint(

            ENEMY_SIZE[0]//2,

            SCREENRECT.right - ENEMY_SIZE[0]//2

        )

        self.rect = self.image.get_rect(midtop=(x_pos, -ENEMY_SIZE[1]))



    def update(self):

        self.rect.y += self.speed

        if self.rect.top > SCREENRECT.bottom:

            self.kill()



async def main():

    # 잠깐 대기 (로딩 효과)

    await asyncio.sleep(1)

    pygame.init()



    screen = pygame.display.set_mode(SCREENRECT.size, 0)

    clock = pygame.time.Clock()

    font  = pygame.font.Font(None, 24)



    player = Player()

    player_grp  = pygame.sprite.GroupSingle(player)

    bullets     = pygame.sprite.Group()

    enemies     = pygame.sprite.Group()

    all_sprites = pygame.sprite.LayeredUpdates(player)



    cur_enemy_speed = ENEMY_SPEED_START

    spawn_timer, diff_timer = 0, 0

    # score = 0
    global score

    running = True



    clock.tick(FPS)

    while running:

        dt = clock.tick(FPS)

        spawn_timer += dt

        diff_timer  += dt



        for ev in pygame.event.get():

            if ev.type == pygame.QUIT:

                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:

                b = Bullet(player.rect.centerx, player.rect.top)

                bullets.add(b)

                all_sprites.add(b, layer=1)



        # 적 생성 및 난이도 증가

        if spawn_timer >= ENEMY_SPAWN_INTERVAL:

            enemies.add(Enemy(cur_enemy_speed))

            all_sprites.add(enemies.sprites()[-1], layer=2)

            spawn_timer -= ENEMY_SPAWN_INTERVAL

        if diff_timer >= DIFFICULTY_STEP_MS:

            cur_enemy_speed += ENEMY_SPEED_INCREMENT

            diff_timer -= DIFFICULTY_STEP_MS



        # 업데이트

        keys = pygame.key.get_pressed()

        player_grp.update(keys)

        bullets.update()

        enemies.update()



        # 화면 아래로 적이 닿으면 게임 종료
        if any(e.rect.bottom >= SCREENRECT.bottom for e in enemies):
            running = False

        if pygame.sprite.spritecollideany(player, enemies):
            running = False



        score += len(pygame.sprite.groupcollide(enemies, bullets, True, True))



        # 그리기

        screen.fill((0,0,32))
        all_sprites.draw(screen)
        screen.blit(
            font.render(f"Score: {score}", True, (255,255,255)),
            (8,8)
        )
        pygame.display.flip()
        await asyncio.sleep(0.01)   # EventLoop에 제어권 양도



asyncio.ensure_future(main())
