import pygame
import math


from scripts.utils import load_image




class Fireball:
    def __init__(self,game,pos):
        self.pos = list(pos)
        self.game = game
        self.direction = pygame.Vector2()
        self.velocity = [0,0]
        self.angle = 0
        self.rotation_angle = 0
        self.base_img = load_image('fireball.png')
        self.time = 0
        self.flip = False
        self.follow = 100
    
    def update(self):
        
        self.direction.xy = self.game.player.pos[0]-self.pos[0]-10 , self.game.player.pos[1]-self.pos[1]-15
        self.magnitude = self.direction.magnitude()
        self.time = self.time + 1
        self.follow = max(self.follow -1,0)

        if self.velocity[0]>0:
            self.angle = math.atan(self.velocity[1]/self.velocity[0])
            self.rotation_angle = (math.pi+ self.angle)
        elif self.velocity[0]<0:
            self.rotation_angle = (self.angle)
        
        if (self.direction.x>0):
            self.flip = True
        elif (self.direction.x<0):
            self.flip = False
        
     
        if self.follow:
            self.velocity[0] = self.direction.x / self.magnitude
            self.velocity[1] = self.direction.y /self.magnitude
       
        self.pos[0] += self.velocity[0]*1.25
        self.pos[1] += self.velocity[1]*1.25

    def render(self,surf, offset = (0,0)):
        
        self.current_img = pygame.transform.rotate(self.base_img,self.rotation_angle)
        surf.blit(pygame.transform.flip(self.current_img,self.flip,False),(self.pos[0]-offset[0],self.pos[1]-offset[1]))


class Fireball_vertical:
    def __init__(self,game,pos):
        self.game = game
        self.pos = list(pos)
        self.air_time = 180

    def update(self):
        self.air_time -= 1
        self.pos[1] += 1
        if not self.air_time:
            return True

    def render(self,surf, offset =(0,0)):
        surf.blit(self.game.assets["fireball_vertical"],(self.pos[0]-offset[0],self.pos[1]-offset[1]))
