import math
import random

import pygame

from scripts.particle import Particle
from scripts.spark import Spark
from scripts.fireball import Fireball,Fireball_vertical

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
       
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):

            if entity_rect.colliderect(rect):
                self.velocity[0]=0
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                    
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class FlyingEntity:
    def __init__(self, game,e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
       
        
        self.pos[1] += frame_movement[1]
        

        

        
      
        
        
        
            
       
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))




class Enemy2(FlyingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game,'flying_enemy', pos, size)

        self.flying = True
        self.direction = 600
        self.patrol_r= list(pos)
        self.patrol_l = [pos[0]-200,pos[1]]
        self.flip = False
        self.patrol = 50
        self.attack = False
        self.firefall_attack = False
        self.damage = False
        self.health = 10
        self.phase = 1
        self.attack_available = 0
        self.attack_cooldown = 0
        self.hurt = 0
        self.velocity = [0,0]
        self.fireball_offset = [0,0]

    def PLAYER_IN_RANGE(self):
        if (math.pow((self.game.player.pos[0]-self.pos[0]),2)+math.pow((self.game.player.pos[1]-self.pos[1]),2))<=1:
            if (self.game.player.pos[0]-self.pos[0])<0:
                self.flip = False
            else:
                self.flip = True
            return True
        else:
            
          
            return False

    def update(self,tilemap, movement=(0,0)):
        if self.health <=6:
            self.phase = 2
        elif self.health<=2:
            self.phase = 3
        if self.health == 0:
            self.set_action("death")
            done = self.animation.done
            if done:
                return True
        
        if self.hurt:
            self.hurt-=1
        




        if self.damage and self.health:
         
            self.set_action("damage")

        if self.firefall_attack:
            self.firefall_attack = False
            for i in range(7):
                if i!=0:

                    self.game.firefall.append(Fireball_vertical(self.game,(self.game.player.pos[0]+i*32,self.pos[1]-40)))
                    self.game.firefall.append(Fireball_vertical(self.game,(self.game.player.pos[0]-i*32  ,self.pos[1]-40)))
                
                if i==0:
                     self.game.firefall.append(Fireball_vertical(self.game,(self.game.player.pos[0]+i*32,self.pos[1]-40)))

        

        if self.attack and not self.damage and self.health:
            self.flying = False
            self.attack = max(0,self.attack -1)
            if self.attack ==0:
                self.flying = True
            self.set_action('attack')
            if self.animation.frame == 25:
                for i in range(self.phase):
                    self.fireball_offset[0] = 0
                    self.fireball_offset[1] = 0
                    self.game.fireballs.append(Fireball(self.game,(self.pos[0]+18+self.fireball_offset[0],self.pos[1]+25+self.fireball_offset[1])))




        if (self.game.player.pos[0]-self.pos[0])<0:
                self.flip = False
                self.still = False
        elif ((self.game.player.pos[0]-self.pos[0]-80)>0):
                self.flip = True
                self.still = False
        else: 
                self.still = True
        
        if self.flying :
            self.patrol = self.patrol -1
         
            
            if not self.still:
                if self.flip:
                
                    movement = (movement[0] +1, movement[1])
                if not self.flip:
                    movement = (movement[0] -1, movement[1])

               
        
        
        

        
        super().update(tilemap, movement=movement)
        self.animation.update()
        if self.damage:
            done = self.animation.done
            if done:
                self.damage = False
                print('yes')

        if not self.attack and not self.damage and self.health:
            if movement[0] !=0:
                self.set_action('flying')
               
            else:
                self.set_action('idle')

        
    
    def Shoot_Fireball(self):
      
        self.attack = 56
        self.fireball_offset = offset
    
    def firefall(self):

        self.firefall_attack = True
    
    def Damage(self):
        if self.health:
            self.health = self.health -1
            self.hurt = 60
        
        self.damage = True
    

        

        
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
      



class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0
        self.velocity = [0,0]
        self.sprint = False
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        for shuriken in self.game.shurikens:
            shuriken_rect = pygame.Rect(shuriken[0][0],shuriken[0][1],9,9)
            if self.rect().colliderect(shuriken_rect):
                self.game.shurikens.remove(shuriken)
                
                for i in range(10):
                    self.game.sparks.append(Spark(shuriken[0],random.random()*2*math.pi, 2 + random.random(), color='red'))
                return True
                
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))





    

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.sprint = False
        self.velocity =[0,0]
    
    def update(self, tilemap, movement=(0, 0)):
        if self.sprint and movement[0]!=0 and abs(self.dashing)<=50 and not self.wall_slide and self.collisions['down']:
            
            if self.flip:
            
                if self.velocity[0]>0:
                    self.velocity[0]=0
                self.velocity[0] = max(-1,self.velocity[0]-0.04)
               
                
            else:
               if self.velocity[0]<0:
                   self.velocity[0] = 0
               self.velocity[0] = min(1 ,self.velocity[0]+0.04)
        
       
        super().update(tilemap, movement=movement)
    
        
        self.air_time += 1
        
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        

        
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            print(self.velocity[0])
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        print(self.sprint , movement[0] , self.dashing)
        if (self.velocity[0] > 0 and not self.sprint) or  (movement[0]==0 and abs(self.dashing)<=50):
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
            print("happended")
        elif not self.sprint:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
        print(self.velocity[0])
       
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
            
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
                
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
    
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
    def throw_shuriken(self,directionx,directiony):
        self.directionx = directionx
        self.directiony = directiony
        self.direction_unit = [2,2]
        self.direction_magnitude = math.pow(self.directionx*self.directionx+self.directiony*self.directiony,0.5)
        self.direction_unit[0] = self.directionx/self.direction_magnitude
        self.direction_unit[1] = self.directiony/self.direction_magnitude
        
        
        self.game.shurikens.append([[self.pos[0],self.pos[1]],[self.direction_unit[0]*2,self.direction_unit[1]*2]])


        

