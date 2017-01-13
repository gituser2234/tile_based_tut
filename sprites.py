import pygame
import settings
from settings import TILESIZE, PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_HIT_RECT, MOB_IMG
from tilemap import collide_hit_rect
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Prepare our player
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        
        # Vectors
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        
        # Rotation
        self.rot = 0
        
    def get_keys(self):
        # Reset vectors to zero
        self.vel = vec(0, 0)
        self.rot_speed = 0
        
        # Check pressed keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pygame.K_RIGHT]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pygame.K_UP]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pygame.K_DOWN]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            
#        # if running diagonal to avoid speed-up
#        if self.vel.x != 0 and self.vel.y != 0:
#            self.vel *= 0.7071
        
    def collide_with_walls(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    # if movin' right        # dividin' by to due to center
                    self.pos.x = hits[0].rect.left - self.hit_rect.width / 2
                elif self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + self.hit_rect.width / 2
                # if we hit, then we stop
                self.vel.x = 0
                self.hit_rect.centerx = self.pos.x
                    
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    # if movin' right
                    self.pos.y = hits[0].rect.top - self.hit_rect.height / 2
                elif self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height / 2
                # if we hit, then we stop
                self.vel.y = 0
                self.hit_rect.centery = self.pos.y

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pygame.transform.rotate(self.game.player_img, self.rot)
        
        # Now we need to calculate when the new rectangle is
        self.rect = self.image.get_rect()
        
        # And set it to the previous position
        self.rect.center = self.pos
        
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self.collide_with_walls('x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls('y')
        self.rect.center = self.hit_rect.center
        
class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Member of all_sprites groups and walls groups
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.rot = 0
        
    def update(self):
        # We calculate angle from mob to player's vectors
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pygame.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Member of all_sprites groups and walls groups
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE