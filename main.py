# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame
import sys
import settings
from settings import WIDTH, HEIGHT, TITLE, TILESIZE, FPS, PLAYER_IMG, WALL_IMG,\
MOB_IMG, BULLET_IMG, BULLET_DAMAGE, MOB_DAMAGE, MOB_KNOCKBACK, GREEN, YELLOW,\
RED, WHITE, PLAYER_HEALTH, CYAN, MUZZLE_FLASHES, ITEM_IMAGES, HEALTH_PACK_AMOUNT,\
BG_MUSIC, EFFECTS_SOUNDS, WEAPON_SOUNDS_GUN, ZOMBIE_MOAN_SOUNDS, PLAYER_HIT_SOUNDS,\
ZOMBIE_HIT_SOUNDS
from sprites import Player, Mob, collide_hit_rect, Obstacle, Item
from os import path
from tilemap import Camera, TiledMap
from random import random, choice
vec = pygame.math.Vector2

# HUD FUNCTION
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pygame.draw.rect(surf, col, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set screen settings
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        
        # Set clock to limit FPS
        self.clock = pygame.time.Clock()
        
        # pygame.key.set_repeat(when, inteval)
        pygame.key.set_repeat(500, 100)
        
        # Load data
        self.load_data()

    def load_data(self):
        # Specify game folder
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'maps')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')

        
        # Load data from map
        self.map_data = []
        self.map = TiledMap(path.join(map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect() 
        
        # Load img data
        self.player_img = pygame.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_img = pygame.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.mob_img = pygame.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pygame.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        # Scale wall img due to its huge dimensions
        self.wall_img = pygame.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pygame.image.load(path.join(img_folder, img)).convert_alpha())
            
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pygame.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
            
        # Sound load
        pygame.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pygame.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        
        self.weapon_sounds = {}
        self.weapon_sounds['gun'] = []
        for snd in WEAPON_SOUNDS_GUN:
            self.weapon_sounds['gun'].append(pygame.mixer.Sound(path.join(snd_folder, snd)))
            
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pygame.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
            
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))
            
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        # Spawning walls
        # enumerate makes row as index, example:
        # l = ['a', 'b', 'c', 'd']
        # for index, item in enumerate(l):
        #   print(index, item)
#        for row, tiles in enumerate(self.map.data):
#            for col, tile in enumerate(tiles):
#                if tile == '1':
#                    Wall(self, col, row)
#                elif tile == 'P':
#                    # Spawn player
#                    self.player = Player(self, col, row)
#                elif tile == 'M':
#                    Mob(self, col, row)
        for tile_object in self.map.tmxdata.objects:
            # To spawn our object in the center of the object in map, not in left upper corner
            obj_center = vec(tile_object.x + tile_object.width // 2, tile_object.y + tile_object.height // 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['health']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
                    

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        
        # Loops=-1 means loop and repeat
        pygame.mixer.music.play(loops=-1)
        
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        
        # Playa' hits items
        hits = pygame.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.item_type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
        
        # Mobs hits playa'
        hits = pygame.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            # Rotate whatever mob hit us
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # Bullets hit mobs
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            # When we hit, we stop it
            hit.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, settings.LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, settings.LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # Display FPS
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(settings.BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.draw_grid()
        for sprite in self.all_sprites:
            # If it is a Mob, then draw its health
            if isinstance(sprite, Mob):
                sprite.draw_health()
            #self.screen.blit(sprite.image, sprite.rect)
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pygame.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pygame.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)

        #used to draw rect showing additional helpful info
        #pygame.draw.rect(self.screen, settings.WHITE, self.player.hit_rect, 2)
        
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        
        pygame.display.flip()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.draw_debug = not self.draw_debug

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()