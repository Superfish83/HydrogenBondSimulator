from math import *
import numpy as np

WALL_W = 800
WALL_H = 600

rad_104 = 1.8238691 # 104.5도 (라디안으로)
delta = 0.1 # Division by Zero 방지

class H2O:
    def __init__(self, pos, theta):
        self.pos = pos # np.array 형식 -> 분자의 중심점(산소 원자) 위치
        self.v = np.array([0.0, 0.0]) # 분자의 속도

        self.theta1 = theta # -> 수소 원자 1의 방향 라디안으로 저장
        self.theta2 = theta + rad_104 # -> 수소 원자 2의 방향 라디안으로 저장
        self.r = 35 # 수소 - 산소 간 결합 길이
        self.hpos = np.array(
            [
                [self.pos[0] + self.r * cos(self.theta1),
                  self.pos[1] + self.r * sin(self.theta1)],
                [self.pos[0] + self.r * cos(self.theta2),
                  self.pos[1] + self.r * sin(self.theta2)]
            ]
        )
        self.angvel = 0 # 분자의 회전 각속도

    def update(self, force, torque):
        rate1, rate2 = 2, 0.02
        decay_rate = 0.97

        self.v += rate1 * force
        self.angvel += rate1 * torque

        self.v *= decay_rate
        self.angvel *= decay_rate

        self.pos += rate2 * self.v
        self.theta1 += rate2 * self.angvel
        self.theta2 = self.theta1 + rad_104
        self.hpos = np.array(
            [
                [self.pos[0] + self.r * cos(self.theta1),
                  self.pos[1] + self.r * sin(self.theta1)],
                [self.pos[0] + self.r * cos(self.theta2),
                  self.pos[1] + self.r * sin(self.theta2)]
            ]
        )

        # 벽면과 충돌
        if self.pos[0] < 20:
            self.v[0] = -1 * self.v[0]
        if self.pos[0] > WALL_W-20:
            self.v[0] = -1 * self.v[0]
        if self.pos[1] < 20:
            self.v[1] = -1 * self.v[1]
        if self.pos[1] > WALL_H-20:
            self.v[1] = -1 * self.v[1]

def get_force(pos1, pos2):
    scale = 0.1
    r = scale * np.linalg.norm(pos1-pos2) + delta
    return np.array([
        (pos1[0] - pos2[0]) / r**3,
        (pos1[1] - pos2[1]) / r**3
    ])

def get_torque(pos1, pos2, r, theta):
    scale = 0.1
    r = scale * np.linalg.norm(pos1-pos2) + delta
    F = np.array([
        (pos1[0] - pos2[0]) / r**3,
        (pos1[1] - pos2[1]) / r**3,
        0.0
    ])
    R = scale * np.array([
        r * cos(theta),
        r * sin(theta),
        0.0
    ])
    return np.cross(F,R)[2] # 외적으로 구한 돌림힘


class MoleSystem:
    def __init__(self):
        self.moles = []
    
    def addMole(self, pos, theta):
        mole = H2O(pos, theta)
        self.moles.append(mole)

    def update(self):
        net_force_list = []
        net_torque_list = []

        for i in range(len(self.moles)):
            tgtMole = self.moles[i] # 업데이트 대상(Target Mole) 변수
            net_force = np.array([0.0, 0.0]) # 알짜힘 벡터
            net_torque = 0.0 # 알짜 돌림힘 벡터
            
            for j in range(len(self.moles)):
                if i==j:
                    continue
                mole = self.moles[j]

                # 산소와 산소 사이 상호작용
                net_force += 14 * get_force(tgtMole.pos, mole.pos)

                # 산소와 수소 사이 상호작용
                net_force -= 2 * get_force(tgtMole.pos, mole.hpos[0])
                net_force -= 2 * get_force(tgtMole.pos, mole.hpos[1])

                # 수소와 산소 사이 상호작용
                net_force += 2 * get_force(tgtMole.hpos[0], mole.pos)
                net_force += 2 * get_force(tgtMole.hpos[1], mole.pos)
                net_torque += 2 * get_torque(tgtMole.hpos[0], mole.pos, 
                                         tgtMole.r, tgtMole.theta1)
                net_torque += 2 * get_torque(tgtMole.hpos[1], mole.pos, 
                                         tgtMole.r, tgtMole.theta2)

                # 수소와 수소 사이 상호작용
                net_force -= 1.5* get_force(tgtMole.hpos[0], mole.hpos[0])
                net_force -= 1.5* get_force(tgtMole.hpos[0], mole.hpos[1])
                net_force -= 1.5* get_force(tgtMole.hpos[1], mole.hpos[0])
                net_force -= 1.5* get_force(tgtMole.hpos[1], mole.hpos[1])
                net_torque -= 1.5* get_torque(tgtMole.hpos[0], mole.hpos[0], 
                                         tgtMole.r, tgtMole.theta1)
                net_torque -= 1.5* get_torque(tgtMole.hpos[0], mole.hpos[1], 
                                         tgtMole.r, tgtMole.theta1)
                net_torque -= 1.5* get_torque(tgtMole.hpos[1], mole.hpos[0], 
                                         tgtMole.r, tgtMole.theta2)
                net_torque -= 1.5* get_torque(tgtMole.hpos[1], mole.hpos[1], 
                                         tgtMole.r, tgtMole.theta2)
                
            #화면 중심 방향으로 받는 압력
            net_force -= 0.025 * np.array([
                (tgtMole.pos[0] - WALL_W/2),
                (tgtMole.pos[1] - WALL_H/2)
            ])

            net_force_list.append(net_force)
            net_torque_list.append(net_torque)

        for i in range(len(self.moles)):
            self.moles[i].update(
                net_force_list[i],
                net_torque_list[i]
            )