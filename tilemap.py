# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 23:56:54 2017

@author: anonymous
"""

import pygame
from settings import TILESIZE, WIDTH, HEIGHT

class Map():
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
        
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        # move() gives new rectangle shifter by amount of an argument
        return entity.rect.move(self.camera.topleft)
        
    def update(self, target):
        # We want centered on the screen
        x = -target.rect.x + (WIDTH // 2)
        y = -target.rect.y + (HEIGHT // 2)
        
        # Limit scrolling to map size
        x = min(0, x) # left
        y = min(0, y) # top
        x = max(-(self.width - WIDTH), x) # right
        y = max(-(self.height - HEIGHT), y) # bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)