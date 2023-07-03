import pygame
import numpy as np
from math import *
from moleSystem import *
import random

pygame.init()
pygame.font.init()

WALL_W = 800
WALL_H = 600

screen = pygame.display.set_mode((WALL_W, WALL_H))
clock = pygame.time.Clock()

# 분자들의 계(system) 변수 초기화
system = None
def init_system(moles):
    system = MoleSystem()
    for i in range(moles):
        system.addMole(
            np.array([float(random.randrange(20,WALL_W-20)), 
                    float(random.randrange(20,WALL_H-20))]),
            random.randrange(0,60) * pi/30
        )
    return system
m = 6
system = init_system(m)

#for i in range(50, 351, 60):
#    for j in range(50, 51, 70):
#        system.addMole(
#            np.array([float(i),float(j)]), 
#            random.randrange(0,4)
#        )


color_red = (200,0,0)
color_yellow = (200,200,200)
color_gray = (150,150,150)

my_font = pygame.font.SysFont('NanumGothicBold', 30)
def step(t):
    pygame.display.flip()
    pygame.event.pump()
    #이전 프레임의 그림 지우기
    screen.fill((50,50,100))

    #system의 분자들 그리기
    for mole in system.moles:
        pygame.draw.line(screen, color_gray, mole.pos, mole.hpos[0], 8)
        pygame.draw.line(screen, color_gray, mole.pos, mole.hpos[1], 8)
        pygame.draw.circle(screen, color_red, mole.pos, 15)
        pygame.draw.circle(screen, color_yellow, mole.hpos[0], 10)
        pygame.draw.circle(screen, color_yellow, mole.hpos[1], 10)

    sign_text = my_font.render("H2O Molecule Simulator", False, (255,255,255))
    screen.blit(sign_text, (10, 10))
    sign_text = my_font.render("moles: {0}".format(m), False, (255,255,255))
    screen.blit(sign_text, (10, 40))

    #system의 분자들 상태 update
    system.update()


    pygame.display.flip()
    clock.tick(120)

if __name__ == '__main__':
    t = 0
    while True:
        for ev in pygame.event.get():
            #checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:
                system = init_system(m)
                
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    system = init_system(m)
                if ev.key == pygame.K_RIGHT:
                    m+=1
                    system = init_system(m)
                if ev.key == pygame.K_LEFT:
                    m-=1
                    system = init_system(m)
        step(t)
        t+=1