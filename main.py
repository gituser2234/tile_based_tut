# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame
import sys
import settings
from settings import WIDTH, HEIGHT, TITLE, TILESIZE, FPS, PLAYER_IMG, WALL_IMG, MOB_IMG
from settings import BULLET_IMG
from sprites import Player, Wall, Mob
from os import path
from tilemap import Map, Camera

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
        
        # Load data from map
        self.map_data = []
        self.map = Map(path.join(game_folder, 'map3.txt'))
        
        # Load img data
        self.player_img = pygame.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_img = pygame.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.mob_img = pygame.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pygame.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        # Scale wall img due to its huge dimensions
        self.wall_img = pygame.transform.scale(self.wall_img, (TILESIZE, TILESIZE))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Spawning walls
        # enumerate makes row as index, example:
        # l = ['a', 'b', 'c', 'd']
        # for index, item in enumerate(l):
        #   print(index, item)
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                elif tile == 'P':
                    # Spawn player
                    self.player = Player(self, col, row)
                elif tile == 'M':
                    Mob(self, col, row)
                    
        self.camera = Camera(self.map.width, self.map.height)
                    

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        
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
        
        # Bullets hit mobs
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.kill()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, settings.LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, settings.LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # Display FPS
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(settings.BGCOLOR)
        #self.draw_grid()
        for sprite in self.all_sprites:
            #self.screen.blit(sprite.image, sprite.rect)
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        #used to draw rect showing additional helpful info
        #pygame.draw.rect(self.screen, settings.WHITE, self.player.hit_rect, 2)
        pygame.display.flip()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

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