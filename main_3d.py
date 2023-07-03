import pygame
import numpy as np
from math import *
from moleSystem_3d import *
import random

pygame.init()
pygame.font.init()

WALL_W = 600
WALL_H = 600

screen = pygame.display.set_mode((WALL_W, WALL_H))
clock = pygame.time.Clock()

# 분자들의 계(system) 변수 초기화
system = None
def init_system(moles):
    system = MoleSystem()

    for i in range(moles):
        system.addMole(
            np.array([float(random.randrange(20,WALL_W-20))-300, 
                    float(random.randrange(20,WALL_H-20))-300,
                    float(random.randrange(20,WALL_H-20))-300]),
            random.randrange(0,60) * pi/30,
            False
        )
    return system
m = 1
system = init_system(m)

#for i in range(50, 351, 60):
#    for j in range(50, 51, 70):
#        system.addMole(
#            np.array([float(i),float(j)]), 
#            random.randrange(0,4)
#        )

my_font = pygame.font.SysFont('NanumGothicBold', 30)
camera_theta = 0 # 카메라 각도
camera_phi = 0 # 카메라 각도
def step(t):
    pygame.display.flip()
    pygame.event.pump()
    #이전 프레임의 그림 지우기
    screen.fill((50,50,100))

    #카메라 시점에 따라 사영된 분자들의 좌표
    moles_projection = []

    th = camera_theta
    phi = camera_phi
    rot_mtrx = np.array([[cos(th), -sin(th), 0],
                        [0,0,1],
                        [sin(th), cos(th), 0]])
    rot_mtrx = np.matmul(rot_mtrx,
               np.array([[0,0,1],
                        [cos(phi), -sin(phi), 0],
                        [sin(phi), cos(phi), 0]]))
    for mole in system.moles:
        opos = np.matmul(rot_mtrx, mole.pos) + (WALL_H/2, WALL_W/2, 0)
        hpos0 = np.matmul(rot_mtrx, mole.hpos[0]) + (WALL_H/2, WALL_W/2, 0)
        hrelpos0 = np.matmul(rot_mtrx, mole.h_rel_pos[0])
        hpos1 = np.matmul(rot_mtrx, mole.hpos[1]) + (WALL_H/2, WALL_W/2, 0)
        hrelpos1 = np.matmul(rot_mtrx, mole.h_rel_pos[1])
        moles_projection.append(np.array([opos, hpos0, hrelpos0, hpos1, hrelpos1]))

    moles_projection.sort(key=lambda x: x[0][2], reverse=False)
    for mole in moles_projection:
        opos = mole[0]
        hpos0 = mole[1]
        hrelpos0 = mole[2]
        hpos1 = mole[3]
        hrelpos1 = mole[4]

        
        c1 = (round(opos[2]/6.0)+150, 0, 0)
        ch0 = (150+round(hpos0[2]/6.0), 150+round(hpos0[2]/6.0), 150+round(hpos0[2]/6.0))
        ch1 = (150+round(hpos1[2]/6.0), 150+round(hpos1[2]/6.0), 150+round(hpos1[2]/6.0))
        s1 = round(15 + opos[2]/60.0)
        sh0 = round(10 + hpos0[2]/48.0)
        sh1 = round(10 + hpos1[2]/48.0)
            
        pygame.draw.line(screen, ch0, opos[:2], hpos0[:2], 8)
        pygame.draw.line(screen, ch1, opos[:2], hpos1[:2], 8)
        if(hrelpos0[2] < 0):
            pygame.draw.circle(screen, ch0, hpos0[:2], sh0)
        if(hrelpos1[2] < 0):
            pygame.draw.circle(screen, ch1, hpos1[:2], sh1)
        pygame.draw.circle(screen, c1, opos[:2], s1)
        if(hrelpos0[2] >= 0):
            pygame.draw.circle(screen, ch0, hpos0[:2], sh0)
        if(hrelpos1[2] >= 0):
            pygame.draw.circle(screen, ch1, hpos1[:2], sh1)

    sign_text = my_font.render("H2O Molecule Simulator(3D)", False, (255,255,255))
    screen.blit(sign_text, (10, 10))
    sign_text = my_font.render("moles: {0}".format(m), False, (255,255,255))
    screen.blit(sign_text, (10, 40))

    #system의 분자들 상태 update
    if(not pauseFlag):
        system.update()
    else:
        sign_text = my_font.render("PAUSED".format(m), False, (255,100,100))
        screen.blit(sign_text, (150, 40))


    pygame.display.flip()
    clock.tick(120)

rotflag = [False, False, False, False]
pauseFlag = False
if __name__ == '__main__':
    t = 0
    rot_step = pi/72
    while True:
        if(rotflag[0]):
            camera_theta += rot_step
        if(rotflag[1]):
            camera_theta -= rot_step
        if(rotflag[2]):
            camera_phi += rot_step
        if(rotflag[3]):
            camera_phi -= rot_step

        for ev in pygame.event.get():
            #checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:
                system = init_system(m)
                
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    pauseFlag = not pauseFlag
                if ev.key == pygame.K_a:
                    m -= 1
                    system = init_system(m)
                if ev.key == pygame.K_d:
                    m += 1
                    system = init_system(m)
                if ev.key == pygame.K_RIGHT:
                    rotflag[0] = True
                if ev.key == pygame.K_LEFT:
                    rotflag[1] = True
                if ev.key == pygame.K_UP:
                    rotflag[2] = True
                if ev.key == pygame.K_DOWN:
                    rotflag[3] = True
                    
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_RIGHT:
                    rotflag[0] = False
                if ev.key == pygame.K_LEFT:
                    rotflag[1] = False
                if ev.key == pygame.K_UP:
                    rotflag[2] = False
                if ev.key == pygame.K_DOWN:
                    rotflag[3] = False
        step(t)
        t+=1