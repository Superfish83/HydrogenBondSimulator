from math import *
import numpy as np

WALL_W = 600
WALL_H = 600

rad_104 = 1.8238691 # 104.5도 (라디안으로)
delta = 0.1 # Division by Zero 방지

class H2O:
    def __init__(self, pos, theta, fixed):
        self.fixed = fixed
        self.pos = pos # np.array 형식 -> 분자의 중심점(산소 원자) 위치
        self.p = np.array([0.0, 0.0, 0.0]) # 분자의 운동량
        self.l = np.array([0.0, 0.0, 0.0]) # 분자의 각운동량

        #초기 수소 원자 2개의 방향
        theta1 = theta
        phi1 = 0
        theta2 = theta + rad_104
        phi2 = 0

        self.r = 24 # 수소 - 산소 간 결합 길이
        self.h_rel_pos = np.array(
            [
                [cos(phi1) * sin(theta1), sin(phi1) * sin(theta1), cos(theta1)],
                [cos(phi2) * sin(theta2), sin(phi2) * sin(theta2), cos(theta2)],
            ]
        )
        #print(self.h_rel_pos)
        self.hpos = pos + self.r * self.h_rel_pos

    def update(self, force, torque):
        rate1, rate2 = 2.0, 0.1
        decay_rate = 0.97

        self.p += rate1 * force
        self.l += rate1 * torque

        self.p *= decay_rate
        self.l *= decay_rate

        if self.fixed:
            self.p = np.array([0.0, 0.0, 0.0])

        # 분자 전체의 운동
        self.pos += rate2 * self.p
        # 수소 원자의 원운동 (접선 방향으로 조금 이동)
        tmp = self.h_rel_pos[0] + rate2 * np.cross(self.h_rel_pos[0], self.l)
        tmp /= np.linalg.norm(tmp) # h_rel_pos 벡터 정규화
        self.h_rel_pos[0] = tmp
        tmp = self.h_rel_pos[1] + rate2 * np.cross(self.h_rel_pos[1], self.l)
        tmp /= np.linalg.norm(tmp) # h_rel_pos 벡터 정규화
        self.h_rel_pos[1] = tmp
        self.hpos = self.pos + self.r * self.h_rel_pos

        # 벽면과 충돌 시
        for i in range(3):
            if self.pos[i] < 20 - WALL_H/2:
                self.p[i] = -1 * self.p[0]
            if self.pos[i] > WALL_W/2 -20:
                self.p[i] = -1 * self.p[0]

def get_force(pos1, pos2):
    scale = 0.1
    r = scale * np.linalg.norm(pos1-pos2) + delta
    return np.array([
        (pos1[0] - pos2[0]) / r**3,
        (pos1[1] - pos2[1]) / r**3,
        (pos1[2] - pos2[2]) / r**3
    ])

def get_torque(pos1, pos2, R):
    scale = 0.1
    r = scale * np.linalg.norm(pos1-pos2) + delta
    F = np.array([
        (pos1[0] - pos2[0]) / r**3,
        (pos1[1] - pos2[1]) / r**3,
        (pos1[2] - pos2[2]) / r**3,
    ])
    return -np.cross(F,R) # F, R 외적 -> 돌림힘


class MoleSystem:
    def __init__(self):
        self.moles = []
    
    def addMole(self, pos, theta, fixed):
        mole = H2O(pos, theta, fixed)
        self.moles.append(mole)

    def update(self):
        net_force_list = []
        net_torque_list = []

        for i in range(len(self.moles)):
            tgtMole = self.moles[i] # 업데이트 대상(Target Mole) 변수
            net_force = np.array([0.0, 0.0, 0.0]) # 알짜힘 벡터
            net_torque = np.array([0.0, 0.0, 0.0]) # 알짜 돌림힘 벡터
            
            for j in range(len(self.moles)):
                if i==j:
                    continue
                mole = self.moles[j]

                # 산소와 산소 사이 상호작용
                net_force += 12 * get_force(tgtMole.pos, mole.pos)

                # 산소와 수소 사이 상호작용
                net_force -= 2 * get_force(tgtMole.pos, mole.hpos[0])
                net_force -= 2 * get_force(tgtMole.pos, mole.hpos[1])

                # 수소와 산소 사이 상호작용
                net_force += 2 * get_force(tgtMole.hpos[0], mole.pos)
                net_force += 2 * get_force(tgtMole.hpos[1], mole.pos)
                net_torque += 2 * get_torque(tgtMole.hpos[0], mole.pos, tgtMole.h_rel_pos[0])
                net_torque += 2 * get_torque(tgtMole.hpos[1], mole.pos, tgtMole.h_rel_pos[1])

                # 수소와 수소 사이 상호작용
                net_force -= 1* get_force(tgtMole.hpos[0], mole.hpos[0])
                net_force -= 1* get_force(tgtMole.hpos[0], mole.hpos[1])
                net_force -= 1* get_force(tgtMole.hpos[1], mole.hpos[0])
                net_force -= 1* get_force(tgtMole.hpos[1], mole.hpos[1])
                net_torque -= 1* get_torque(tgtMole.hpos[0], mole.hpos[0], tgtMole.h_rel_pos[0])
                net_torque -= 1* get_torque(tgtMole.hpos[0], mole.hpos[1], tgtMole.h_rel_pos[0])
                net_torque -= 1* get_torque(tgtMole.hpos[1], mole.hpos[0], tgtMole.h_rel_pos[1])
                net_torque -= 1* get_torque(tgtMole.hpos[1], mole.hpos[1], tgtMole.h_rel_pos[1])
                
            #화면 중심 방향으로 받는 압력
            net_force -= 0.01 * np.array([
                (tgtMole.pos[0]),
                (tgtMole.pos[1]),
                (tgtMole.pos[2])
            ])

            net_force_list.append(net_force)
            net_torque_list.append(net_torque)

        for i in range(len(self.moles)):
            self.moles[i].update(
                net_force_list[i],
                net_torque_list[i]
            )