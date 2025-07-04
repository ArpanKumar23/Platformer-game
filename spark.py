import math

import pygame

class Spark:
    def __init__(self, pos, angle, speed , color = 'white'):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color = color
        
    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        
        self.speed = max(0, self.speed - 0.1)
        return not self.speed
    
    def render(self, surf, offset=(0, 0)):
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]),
        ]
        if self.color == 'red':
            pygame.draw.polygon(surf, (255, 0,0), render_points)
        else:
            pygame.draw.polygon(surf, (255, 255, 255), render_points)


class Explosion:
    def __init__ (self, pos, angle , speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
    
    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        
        self.speed = max(0, self.speed - 0.1)
        return not self.speed
    
    def render(self , surf, offset =(0,0)):
        pygame.draw.circle(surf,(255,0,0),(self.pos[0]-offset[0],self.pos[1]-offset[1]),5-self.speed)
        pygame.draw.circle(surf,(200,155,50),(self.pos[0]-offset[0],self.pos[1]-offset[1]),1+self.speed)
    
    