import pygame
import pytweening as tween
from settings import TILESIZE, PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_HIT_RECT,\
MOB_SPEEDS, MOB_HIT_RECT, BULLET_SPEED, BULLET_LIFETIME, BULLET_RATE, BARREL_OFFSET,\
KICKBACK, GUN_SPREAD, GREEN, YELLOW, RED, MOB_HEALTH, PLAYER_HEALTH, AVOID_RADIUS,\
FLASH_DURATION, WALL_LAYER, PLAYER_LAYER, BULLET_LAYER, MOB_LAYER, EFFECTS_LAYER,\
ITEMS_LAYER, BOB_RANGE, BOB_SPEED, DETECT_RADIUS

from tilemap import collide_hit_rect
from random import uniform, choice, randint, random
vec = pygame.math.Vector2


def collide_with_walls(sprite, group, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                # check if the walls' center is greater than player's center
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    # if movin' right        # dividin' by to due to center
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                # if we hit, then we stop
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
                    
        if direction == 'y':
            hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    # if movin' right
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                # if we hit, then we stop
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Setting layer before calling parental constructor
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Prepare our player
        self.image = game.player_img
        self.rect = self.image.get_rect()
        # BUGFIX: @part15
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        
        # Vectors
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        
        # Rotation
        self.rot = 0
        
        # Others
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        
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
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                choice(self.game.weapon_sounds['gun']).play()
                self.last_shot = now
                direction = vec(1, 0).rotate(-self.rot)
                # player's position + our's offset
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, direction)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)
                MuzzleFlash(self.game, pos)
            
#        # if running diagonal to avoid speed-up
#        if self.vel.x != 0 and self.vel.y != 0:
#            self.vel *= 0.7071
        
    
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
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        
    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH
        
        
class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        # Member of all_sprites groups and walls groups
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # BUGFIX: @part18: using copy() to prevent from drawing buggy bars
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        # BUGFIX: @part15
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player
        
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    # Vectors addin' (look: math vectors addin' (like in school))
                    self.acc += dist.normalize()
        
    def update(self):
        target_dist = self.target.pos - self.pos
        # Instead of comparing square root and radius
        # We compare square and radius square
        # Because it is much faster to compute
        if target_dist.length_squared() < DETECT_RADIUS ** 2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            # We calculate angle from mob to player's vectors
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pygame.transform.rotate(self.game.mob_img, self.rot)
            #self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            # Now he has maximum speed
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
    
    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
            
        width = int(self.rect.width * self.health / MOB_HEALTH)
        # Location accordin' to sprite img, not screen
        self.health_bar = pygame.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pygame.draw.rect(self.image, col, self.health_bar)
        
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        # Copies vector to another to avoid usin' player's pos
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = direction.rotate(spread) * BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()
        
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
            
        
        
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
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
        
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        # Member of all_sprites groups and walls groups
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        
class MuzzleFlash(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pygame.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pygame.time.get_ticks()
        
    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()
            
class Item(pygame.sprite.Sprite):
    def __init__(self, game, pos, item_type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[item_type]
        self.rect = self.image.get_rect()
        self.item_type = item_type
        self.pos = pos
        self.rect.center = pos
        # Choose tween function
        self.tween = tween.easeInOutSine
        # Store where we are, range: [0, 1]
        self.step = 0
        self.direction = 1
        
    def update(self):
        # Bobbing motion
        # - 0.5 because we start from the center
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.direction
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.direction *= -1
        