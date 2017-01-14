# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 23:56:54 2017

@author: anonymous
"""

import pygame
import pytmx
from settings import TILESIZE, WIDTH, HEIGHT

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                # strip() strips characters, here: "\n"
                self.data.append(line.strip())
                
        # How many tiles wide/high is map
        self.titlewidth = len(self.data[0])
        self.titleheight = len(self.data)
        self.width = self.titlewidth * TILESIZE
        self.height = self.titleheight * TILESIZE
        
class TiledMap:
    def __init__(self, filename):
        # Pixelalpha=True to make sure the transparency go on
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        # Width in tiles
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        # We will store all data in this variable
        self.tmxdata = tm
        
    def render(self, surface):
        # ti will be shorter alias to this command
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))
                        
    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface
    
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    # Apply offset to a sprite
    def apply(self, entity):
        # move() gives new rectangle shifter by amount of an argument
        return entity.rect.move(self.camera.topleft)
        
    # Apply offset to rectangle
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
        
    def update(self, target):
        # We want centered on the screen
        x = -target.rect.centerx + (WIDTH // 2)
        y = -target.rect.centery + (HEIGHT // 2)
        
        # Limit scrolling to map size
        x = min(0, x) # left
        y = min(0, y) # top
        x = max(-(self.width - WIDTH), x) # right
        y = max(-(self.height - HEIGHT), y) # bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)