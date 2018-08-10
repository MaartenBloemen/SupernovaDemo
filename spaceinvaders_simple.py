import pygame
from pygame.locals import *
import sys
import random
import time


class SpaceInvaders:
    def __init__(self, ai_manager, video_stream, ui):
        self.resolution = 1.7666666
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.ui = ui

        self.score = 0
        self.lives = 1
        pygame.font.init()
        self.font = pygame.font.Font("resources/nidsans-webfont.ttf", 15)
        barrierDesign = [[], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                         [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]]

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)      # pygame.display.set_mode((int(800 * self.resolution), int(600 * self.resolution)))
        # background = pygame.image.load("resources/image/background.jpg")
        # self.screen.blit(background, (0, 0))

        # self.player = pygame.image.load("resources/images/ship.png").convert_alpha()
        # self.playerX = 400
        # self.playerY = 550
        self.background = Background("resources/images/background.jpg", [0, 0])
        self.player = Player("resources/images/ship.png", [int(400 * self.resolution), int(550 * self.resolution)])

        self.animationOn = 0
        self.direction = 1

        self.bullet = None
        self.bullets = []

        # self.enemySprites = {
        #     0: [pygame.image.load("resources/images/enemy1_1.png").convert_alpha(),
        #         pygame.image.load("resources/images/enemy1_2.png").convert_alpha()],
        #     1: [pygame.image.load("resources/images/enemy2_1.png").convert_alpha(),
        #         pygame.image.load("resources/images/enemy2_2.png").convert_alpha()],
        #     2: [pygame.image.load("resources/images/enemy3_1.png").convert_alpha(),
        #         pygame.image.load("resources/images/enemy3_2.png").convert_alpha()],
        # }
        self.enemySpeed = int(20 * self.resolution)
        self.lastEnemyMove = 0
        self.enemies = []
        self.makeEnemies()
        self.barrierParticles = []
        # startY = 50
        # startX = 50
        # for rows in range(6):
        #     out = []
        #     if rows < 2:
        #         enemy = 0
        #     elif rows < 4:
        #         enemy = 1
        #     else:
        #         enemy = 2
        #     for columns in range(10):
        #         out.append((enemy, pygame.Rect(startX * columns, startY * rows, 35, 35)))
        #     self.enemies.append(out)
        self.chance = 990

        barrierX = int(50 * self.resolution)
        barrierY = int(400 * self.resolution)
        space = int(100 * self.resolution)

        for offset in range(1, 5):
            for b in barrierDesign:
                for b in b:
                    if b != 0:
                        self.barrierParticles.append(pygame.Rect(barrierX + space * offset, barrierY, 5, 5))
                    barrierX += int(5 * self.resolution)
                barrierX = 50 * offset * self.resolution
                barrierY += 3 * self.resolution
            barrierY = 400 * self.resolution

    def makeEnemies(self):
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

    def enemyUpdate(self):
        if not self.lastEnemyMove:
            for out in self.enemies:
                for enemy in out:
                    if enemy.rect.colliderect(
                            pygame.Rect(self.player.rect.left, self.player.rect.top, self.player.image.get_width(),
                                        self.player.image.get_height())):
                        self.lives -= 1
                        self.resetPlayer()
                    enemy.rect.x += self.enemySpeed * self.direction
                    self.lastEnemyMove = 25
                    if enemy.rect.x >= int(750 * self.resolution) or enemy.rect.x <= 0:
                        self.moveEnemiesDown()
                        self.direction *= -1

                    chance = random.randint(0, 1000)
                    if chance > self.chance:
                        self.bullets.append(pygame.Rect(enemy.rect.x, enemy.rect.y, int(5*self.resolution), int(10*self.resolution)))
                        self.score += 5
            if self.animationOn:
                self.animationOn -= 1
            else:
                self.animationOn += 1
        else:
            self.lastEnemyMove -= 1

    def moveEnemiesDown(self):
        for out in self.enemies:
            for enemy in out:
                # enemy = enemy[1]
                enemy.rect.y += 20

    def playerUpdate(self, key):
        # key = pygame.key.get_pressed()
        if key == "right" and self.player.rect.left < (int(800 * self.resolution)) - self.player.image.get_width():
            self.player.rect.left += 5
        elif key == "left" and self.player.rect.left > 0:
            self.player.rect.left -= 5
        if key == "space" and not self.bullet:
            self.bullet = pygame.Rect(self.player.rect.left + self.player.image.get_width() / 2 - 2,
                                      self.player.rect.top - 15, int(5*self.resolution), int(10*self.resolution))

    def bulletUpdate(self):
        for i, enemy in enumerate(self.enemies):
            for j, enemy in enumerate(enemy):
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
                self.resetPlayer()

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

    def resetPlayer(self):
        self.player.rect.left = int(400 * self.resolution)

    def run(self):
        clock = pygame.time.Clock()
        for x in range(3):
            self.moveEnemiesDown()
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

            if not self.enemies:
                self.screen.blit(
                    pygame.font.Font("resources/nidsans-webfont.ttf", 100).render("You Win!", -1, (52, 255, 0)),
                    (100, 200))
            elif self.lives > 0:
                self.bulletUpdate()
                self.enemyUpdate()
                prediction, probability = self.ai_manager.classify_gesture_on_image(self.video_stream.frame)
                if probability > 0.8:
                    self.playerUpdate(prediction)
            elif self.lives == 0:
                self.screen.blit(
                    pygame.font.Font("resources/nidsans-webfont.ttf", 100).render("You Lose!", -1, (52, 255, 0)),
                    (100, 200))
                self.exit()
            self.screen.blit(self.font.render("Lives: {}".format(self.lives), -1, (255, 255, 255)), (20, 10))
            self.screen.blit(self.font.render("Score: {}".format(self.score), -1, (255, 255, 255)), (400, 10))
            pygame.display.flip()

    def exit(self):
        time.sleep(2)
        self.ui.reset()
        # self.ui.video_loop()
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
