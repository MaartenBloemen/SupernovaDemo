import pygame
from pygame.locals import *
import random
import time
import requests
from ranking_screen import RankingWindow


class SpaceInvaders:
    def __init__(self, ai_manager, video_stream, ui, astronaut_id, name, ranking_screen: RankingWindow):
        self.ranking_screen = ranking_screen
        self.resolution = 1.7666666
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.ui = ui
        self.company_id = "LNXOG3I5"
        self.astronaut_id = astronaut_id
        self.name = name
        self.score = 0
        self.lives = 3

        pygame.font.init()
        self.font = pygame.font.Font("resources/nidsans-webfont.ttf", 15)
        barrier_design = [[],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1]]

        # self.screen = pygame.display.set_mode((int(800 * self.resolution), int(600 * self.resolution)), RESIZABLE)
        self.screen = pygame.display.set_mode((1920, 1080), RESIZABLE)
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.background = Background("resources/images/background.jpg", [0, 0])
        self.player = Player("resources/images/ship.png", [int(400 * self.resolution), int(550 * self.resolution)])

        self.animationOn = 0
        self.direction = 1

        self.bullet = None
        self.bullets = []

        self.enemySpeed = int(20 * self.resolution)
        self.lastEnemyMove = 0
        self.enemies = []
        self.make_enemies()
        self.barrierParticles = []
        self.chance = 985

        barrier_x = int(50 * self.resolution)
        barrier_y = int(425 * self.resolution)
        space = int(100 * self.resolution)

        for offset in range(1, 5):
            for a in barrier_design:
                for b in a:
                    if b != 0:
                        self.barrierParticles.append(
                            pygame.Rect(barrier_x + space * offset, barrier_y, int(10 * self.resolution),
                                        int(10 * self.resolution)))
                    barrier_x += int(10 * self.resolution)
                barrier_x = int(50 * offset * self.resolution)
                barrier_y += int(10 * self.resolution)
            barrier_y = int(425 * self.resolution)

    def make_enemies(self):
        for row in range(5):
            out = []
            if row < 2:
                enemy_sprite = ["resources/images/enemy1_1.png", "resources/images/enemy1_2.png"]
            elif row < 4:
                enemy_sprite = ["resources/images/enemy2_1.png", "resources/images/enemy2_2.png"]
            else:
                enemy_sprite = ["resources/images/enemy3_1.png", "resources/images/enemy3_2.png"]
            for column in range(10):
                enemy = Enemy(enemy_sprite[0], enemy_sprite[1], row, column)
                enemy.rect.x = int(157 * self.resolution) + (column * int(50 * self.resolution))
                enemy.rect.y = int(65 * self.resolution) + (row * int(45 * self.resolution))
                out.append(enemy)
            self.enemies.append(out)

    def enemy_update(self):
        if not self.lastEnemyMove:
            for out in self.enemies:
                for enemy in out:
                    if enemy.rect.colliderect(
                            pygame.Rect(self.player.rect.left, self.player.rect.top, self.player.image.get_width(),
                                        self.player.image.get_height())):
                        self.lives -= 1
                        self.reset_player()
                    enemy.rect.x += self.enemySpeed * self.direction
                    self.lastEnemyMove = 25
                    if enemy.rect.x >= int(750 * self.resolution) or enemy.rect.x <= 0:
                        self.move_enemies_down()
                        self.direction *= -1

                    chance = random.randint(0, 1000)
                    if chance > self.chance:
                        self.bullets.append(pygame.Rect(enemy.rect.x, enemy.rect.y, int(5 * self.resolution),
                                                        int(10 * self.resolution)))
                        self.score += 5
            if self.animationOn:
                self.animationOn -= 1
            else:
                self.animationOn += 1
        else:
            self.lastEnemyMove -= 1

    def move_enemies_down(self):
        for out in self.enemies:
            for enemy in out:
                enemy.rect.y += int(20 * self.resolution)

    def player_update(self, key):
        if key == "right" and self.player.rect.left < (int(800 * self.resolution)) - self.player.image.get_width():
            self.player.rect.left += 5
        elif key == "left" and self.player.rect.left > 0:
            self.player.rect.left -= 5
        if key == "space" and not self.bullet:
            self.bullet = pygame.Rect(self.player.rect.left + self.player.image.get_width() / 2 - 2,
                                      self.player.rect.top - 15, int(5 * self.resolution), int(10 * self.resolution))

    def bullet_update(self):
        for i, e in enumerate(self.enemies):
            for j, enemy in enumerate(e):
                if self.bullet and enemy.rect.colliderect(self.bullet):
                    self.enemies[i].pop(j)
                    self.bullet = None
                    self.chance -= 1
                    self.score += 100

        if self.bullet:
            self.bullet.y -= int(20 * self.resolution)
            if self.bullet.y < int(0 * self.resolution):
                self.bullet = None

        for x in self.bullets:
            x.y += int(20 * self.resolution)
            if x.y > int(600 * self.resolution):
                self.bullets.remove(x)
            if x.colliderect(
                    pygame.Rect(self.player.rect.left, self.player.rect.top, self.player.image.get_width(),
                                self.player.image.get_height())):
                self.lives -= 1
                self.bullets.remove(x)
                self.reset_player()

        for b in self.barrierParticles:
            check = b.collidelist(self.bullets)
            if check != -1:
                self.barrierParticles.remove(b)
                self.bullets.pop(check)
                self.score += 10
            elif self.bullet and b.colliderect(self.bullet):
                self.barrierParticles.remove(b)
                self.bullet = None
                self.score += 10

    def reset_player(self):
        self.player.rect.left = int(400 * self.resolution)

    def run(self):
        i = 0
        clock = pygame.time.Clock()
        for x in range(3):
            self.move_enemies_down()
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background.image, self.background.rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.exit()
            for out in self.enemies:
                for enemy in out:
                    self.screen.blit(enemy.image[self.animationOn],
                                     (enemy.rect.x, enemy.rect.y))
            self.screen.blit(self.player.image, self.player.rect)

            if self.bullet:
                pygame.draw.rect(self.screen, (52, 255, 0), self.bullet)
            for bullet in self.bullets:
                pygame.draw.rect(self.screen, (255, 255, 255), bullet)
            for b in self.barrierParticles:
                pygame.draw.rect(self.screen, (52, 255, 0), b)

            if not self.enemies[0] and not self.enemies[1] and not self.enemies[2] and not self.enemies[3] and not \
                    self.enemies[4]:
                self.screen.blit(
                    pygame.font.Font("resources/nidsans-webfont.ttf", 100).render(
                        "You Win!", -1, (52, 255, 0)),
                    (int(225 * self.resolution), int(175 * self.resolution)))
                self.screen.blit(
                    pygame.font.Font("resources/nidsans-webfont.ttf", 50).render(
                        "Well done, astronaut {}".format(self.name), -1, (52, 255, 0)),
                    (int(175 * self.resolution), int(250 * self.resolution)))
                pygame.display.flip()
                self.exit()
            elif self.lives > 0:
                self.bullet_update()
                self.enemy_update()
                frame = self.video_stream.frame
                prediction, probability = self.ai_manager.classify_gesture_on_image(frame)
                if i == 5:
                    self.ranking_screen.video_loop(frame, True)
                    i = 0
                else:
                    i += 1
                    time.sleep(0.01)
                if probability > 0.8:
                    self.player_update(prediction)
            elif self.lives <= 0:
                self.screen.blit(self.background.image, self.background.rect)
                self.screen.blit(pygame.font.Font("resources/nidsans-webfont.ttf", 100).render(
                    "You Lose!", -1, (52, 255, 0)),
                    (int(225 * self.resolution), int(175 * self.resolution)))
                self.screen.blit(
                    pygame.font.Font("resources/nidsans-webfont.ttf", 100).render(
                        "{} - {}".format(self.name, self.score), -1, (52, 255, 0)),
                    (int(175 * self.resolution), int(225 * self.resolution)))
                pygame.display.flip()
                self.exit()
            self.screen.blit(self.font.render("Lives: {}".format(self.lives), -1, (255, 255, 255)), (20, 10))
            self.screen.blit(self.font.render("Score: {}".format(self.score), -1, (255, 255, 255)), (400, 10))
            pygame.display.flip()

    def exit(self):
        # points / company_id / astronaut_id
        url = "http://supernova.madebyartcore.com/api/checkout/{}/{}/{}".format(self.score, self.company_id,
                                                                                self.astronaut_id).strip()
        response = requests.post(url)
        print(response.json())
        time.sleep(2)
        self.ui.reset(self.astronaut_id, self.score, self.name)
        pygame.quit()


class Player(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        resolution = 1.7666666
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(image_file).convert_alpha(),
                                            ((int(50 * resolution)), (int(48 * resolution))))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        resolution = 1.7666666
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(image_file).convert(),
                                            ((int(800 * resolution)), (int(600 * resolution))))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_file, image_file2, row, column):
        resolution = 1.7666666
        pygame.sprite.Sprite.__init__(self)
        self.image = [pygame.transform.scale(pygame.image.load(image_file).convert_alpha(),
                                             ((int(35 * resolution)), (int(35 * resolution)))),
                      pygame.transform.scale(pygame.image.load(image_file2).convert_alpha(), (
                          (int(35 * resolution)), (int(35 * resolution))))]
        self.row = row
        self.column = column
        self.rect = self.image[0].get_rect()
        self.rect.left = 0
        self.rect.top = 0
