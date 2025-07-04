import os
import sys
import math
import random

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy,Enemy2
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark,Explosion

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'objects': load_images('tiles/objects'),
            'spawners':load_images('tiles/spawners'),
            'shuriken': Animation(load_images('shuriken'),img_dur=15),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'flying_enemy/idle': Animation(load_images('entities/enemy2/idle'),img_dur=5),
            'flying_enemy/attack': Animation(load_images('entities/enemy2/attack'),img_dur=7),
            'flying_enemy/flying': Animation(load_images('entities/enemy2/flying'),img_dur=5),
            'flying_enemy/damage': Animation(load_images('entities/enemy2/damage'),img_dur=5, loop= False),
            'flying_enemy/death': Animation(load_images('entities/enemy2/death'),img_dur=15,loop = False),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'fireball_vertical': load_image('fireball_vertical.png'),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'mine': load_image('tiles/objects/0.png'),
            'fireball': load_image('fireball.png')

        
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.level = 3
        self.load_level(self.level)
        
        self.screenshake = 0
        
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies2 = []
        self.enemies1 = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1),('spawners',2)], keep = False):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            elif spawner['variant']==1:
                self.enemies1.append(Enemy(self, spawner['pos'], (8, 15)))
            else:
                print(True)
                self.enemies2.append(Enemy2(self,spawner['pos'],(80,70)))
        
        self.mines = []
        for mine in self.tilemap.extract([('objects',0)], keep = False):
            self.mines.append([mine['pos'][0],mine['pos'][1]])
            
        
       
        self.firefall = []   
        self.shurikens = []    
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.explosions = []
        self.scroll = [0, 0]
        self.dead = 0
        self.fireballs = []
        self.transition = -30
        self.shuriken_cooldown = 0
        print(random.random())
        
        
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            self.shuriken_cooldown = max(0,self.shuriken_cooldown-1)
            
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / 2, mpos[1] /2)
            if not len(self.enemies1):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1
            
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            
         
            
                    
                    
            
            for rect in self.leaf_spawners:
                if random.random() * 29999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            for enemy in self.enemies1.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                
                if kill:
                    self.enemies1.remove(enemy)
            
            
            
            
            
            for enemy in self.enemies2.copy():
                kill = enemy.update(self.tilemap)
                enemy.render(self.display , offset = render_scroll)
                enemy_rect = pygame.Rect(enemy.pos[0]+8,enemy.pos[1]+20,64,48)
                

                for shuriken in self.shurikens:
                    shuriken_rect = pygame.Rect(shuriken[0][0]+2, shuriken[0][1]+2,5,5)
                    if shuriken_rect.colliderect(enemy_rect) and not enemy.hurt:
                        enemy.Damage()
                        self.shurikens.remove(shuriken)

                if kill:
                    self.enemies2.remove(enemy)
                
                player_rect = pygame.Rect(self.player.pos[0] ,self.player.pos[1] , 8,15)
                if player_rect.colliderect(enemy_rect) and enemy.health and not enemy.hurt:
                    print(enemy.hurt)
                    if abs(self.player.dashing)>=50 :
                        enemy.Damage()
                        self.screenshake = max(32, self.screenshake)
                       
                        self.player.velocity[1]= -3
                        self.player.dashing = 60 if self.player.dashing>0 else -60
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(enemy_rect.center, angle, 2 + random.random(), color = 'red'))
                            self.particles.append(Particle(self, 'particle', enemy_rect.center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    else:
                        self.dead+=1
                        
           
                
                if enemy.attack_cooldown <=0:
                        enemy.attack_cooldown = random.randint(120,150)
                        attack_choice = random.randint(1,2)
                        if attack_choice == 1:
                        
                            enemy.Shoot_Fireball()
                            
                        elif attack_choice == 2:
                            enemy.firefall()
                enemy.attack_cooldown += 1
                
                    

                
                   
                
                   
                
           
           
           
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
            
            for mine in self.mines.copy():
                mine_rect = pygame.Rect(mine[0]+1,mine[1]+1,6,3)
                self.display.blit(self.assets['mine'],(mine[0]-render_scroll[0],mine[1]-render_scroll[1]))
                if (self.player.rect().colliderect(mine_rect) and abs(self.player.dashing)<50):
                    self.dead +=1
                    self.mines.remove(mine)
                   
                    for i in range(30):
                        self.sparks.append(Explosion(mine,-math.pi*random.random(),1+random.random()))
                        self.sparks.append(Explosion(mine,-math.pi*random.random(),2+random.random()))
                for shuriken in self.shurikens:
                    shuriken_rect = pygame.Rect(shuriken[0][0]+2, shuriken[0][1]+2,5,5)
                    if shuriken_rect.colliderect(mine_rect):
                        self.shurikens.remove(shuriken)
                        self.mines.remove(mine)
                        for i in range(30):
                            self.sparks.append(Explosion(mine,-math.pi*random.random(),1+random.random()))
                            self.sparks.append(Explosion(mine,-math.pi*random.random(),2+random.random()))

              
            for fireball in self.fireballs:
                fireball.update()
                fireball.render(self.display,offset = render_scroll)
                
                if (self.tilemap.solid_check((fireball.pos[0], fireball.pos[1]+20))) or(self.tilemap.solid_check((fireball.pos[0]+30, fireball.pos[1]+20))):
                    self.fireballs.remove(fireball)
                    for i in range(4):
                        self.sparks.append(Spark(fireball.pos, random.random() - 0.5 + (math.pi if fireball.velocity[0] > 0 else 0), 2 + random.random()))
                
                elif fireball.time >360:
                    self.fireballs.remove(fireball)

                fireball_rect = pygame.Rect(fireball.pos[0]+8,fireball.pos[1]+12,32,24)
                for shuriken in self.shurikens:
                    shuriken_rect = pygame.Rect(shuriken[0][0]+2, shuriken[0][1]+2,5,5)
                    if shuriken_rect.colliderect(fireball_rect):
                        self.fireballs.remove(fireball)
                        self.shurikens.remove(shuriken)

            


                if (self.player.dashing<50):
                    if (self.player.rect().colliderect(fireball_rect)):
                        self.dead +=1
                        self.screenshake = max(16, self.screenshake)
                        self.fireballs.remove(fireball)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(), color = 'red'))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                        
            for fireball in self.firefall:
                kill = fireball.update()
                fireball.render(self.display,offset = render_scroll)

                if (self.tilemap.solid_check((fireball.pos[0], fireball.pos[1]+35))):
                    self.firefall.remove(fireball)
                    for i in range(4):
                        self.sparks.append(Spark(fireball.pos, random.random() - 0.5  , 2 + random.random()))
                
                fireball_rect = pygame.Rect(fireball.pos[0]+8,fireball.pos[1]+16,16,24)
                for shuriken in self.shurikens:
                    shuriken_rect = pygame.Rect(shuriken[0][0]+2, shuriken[0][1]+2,5,5)
                    if shuriken_rect.colliderect(fireball_rect):
                        self.firefall.remove(fireball)
                        self.shurikens.remove(shuriken)

                if kill:
                    self.firefall.remove(fireball)
                
                if (self.player.dashing<50):
                    if (self.player.rect().colliderect(fireball_rect)):
                        self.dead +=1
                        self.screenshake = max(16, self.screenshake)
                        self.firefall.remove(fireball)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(), color = 'red'))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        
                
                
                







            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random(), color = 'red'))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))


            for shuriken in self.shurikens.copy():
                shuriken[0][0] += shuriken[1][0]
                shuriken[0][1] += shuriken [1][1]
                img = self.assets['shuriken']
                img.update()
                self.display.blit(img.img(),(shuriken[0][0] - 9 / 2 - render_scroll[0], shuriken[0][1] - 9 / 2 - render_scroll[1]))
                if self.tilemap.solid_check(shuriken[0]):
                    self.shurikens.remove(shuriken)
                    for i in range(4):
                        self.sparks.append(Spark(shuriken[0],3-random.random()*6, 2 + random.random()))



            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            for explosion in self.explosions.copy():
                kill = explosion.update()
                explosion.render(self.display, offset = render_scroll)
                if kill:
                    self.explosions.remove(explosion)

            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.shuriken_cooldown:
                            self.shuriken_cooldown += 200
                            self.player.throw_shuriken(mpos[0]+render_scroll[0]-self.player.pos[0],mpos[1]+render_scroll[1]-self.player.pos[1])
                    if event.button ==3:
                        self.player.dash()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key ==pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_LSHIFT:
                        self.player.sprint = True


                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT:
                        self.player.sprint = False
                    if event.key == pygame.K_a or event.key ==pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            if not self.shuriken_cooldown:
                self.display.blit(pygame.transform.scale(load_image('shuriken/1.png'),(18,18)),(270,200))          
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()