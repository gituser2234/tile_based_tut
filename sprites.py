import pygame
import settings
from settings import TILESIZE, PLAYER_SPEED
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Prepare our player
        self.image = game.player_img
        self.rect = self.image.get_rect()
        
        # Vectors
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        
    def get_keys(self):
        # Reset vectors to zero
        self.vel = vec(0, 0)
        
        # Check pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.vel.y = -PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.vel.y = PLAYER_SPEED
            
        # if running diagonal to avoid speed-up
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
        
    def collide_with_walls(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    # if movin' right
                    self.pos.x = hits[0].rect.left - self.rect.width
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                # if we hit, then we stop
                self.vel.x = 0
                self.rect.x = self.pos.x
                    
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    # if movin' right
                    self.pos.y = hits[0].rect.top - self.rect.height
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                # if we hit, then we stop
                self.vel.y = 0
                self.rect.y = self.pos.y

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        

class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Member of all_sprites groups and walls groups
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface([TILESIZE, TILESIZE])
        self.image.fill(settings.GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE