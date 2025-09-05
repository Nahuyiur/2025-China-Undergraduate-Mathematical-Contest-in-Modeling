import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.motion import calculate_drop_and_explosion_position, calculate_missile_position
from utils.judge_cross_by_point_pick import *
import numpy as np
import math
import random

def calculate_effective_coverage_time(drone_initial_position, missile_initial_position, 
                                      flight_speed, drop_time, explosion_delay, 
                                      flight_direction, radius=10, time_range=None):
    """
    计算有效遮蔽时间。

    参数：
    drone_initial_position: 无人机的初始位置 (np.array)
    missile_initial_position: 导弹的初始位置 (np.array)
    flight_speed: 无人机的飞行速度 (m/s)
    drop_time: 投放烟幕干扰弹的延时 (s)
    explosion_delay: 起爆延迟 (s)
    flight_direction: 无人机飞行方向的向量 (np.array)
    radius: 烟幕有效遮蔽的半径 (m)
    time_range: 时间范围 (np.array), 用于计算每个时刻的遮蔽效果，默认为None

    返回：
    effective_coverage_time: 有效遮蔽的时间总和 (秒)
    """
    initial_time, final_time=0,50
    total_count=50000
    interval= (final_time-initial_time)/total_count
    if time_range is None:
        time_range = np.linspace(initial_time, final_time, total_count)  # 默认为50秒的时间范围

    effective_coverage_count = 0  # 初始化有效遮蔽时间
    for t in time_range:
        time_since_explosion = t - (drop_time + explosion_delay)  # 从引爆开始的时间
        if time_since_explosion < 0:
            continue
        # 错误检查：烟幕干扰弹已消失
        elif time_since_explosion > 20:
            continue

        # 计算烟幕干扰弹的投放位置、爆炸位置、烟雾位置
        drop_position, explosion_position, smoke_position = calculate_drop_and_explosion_position(
            drone_initial_position, flight_direction, flight_speed, drop_time, explosion_delay, t)
        
        # 计算导弹当前位置
        missile_position = calculate_missile_position(missile_initial_position, t)
        x1, y1, z1 = smoke_position
        x2, y2, z2 = missile_position
        
        # 计算烟雾与导弹之间的距离
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        
        # 如果距离小于半径，说明有效遮蔽
        if distance < radius:
            effective_coverage_count += 1  # 每秒都计入有效遮蔽时间
            continue
        
        # 调用 final_cross_judge 判断是否有交点
        is_intersecting = complete_judge(missile_position, smoke_position,num=200)
        
        # 如果有交点，说明有遮蔽
        if is_intersecting:
            effective_coverage_count += 1  # 每秒都计入有效遮蔽时间

    effective_coverage_time=effective_coverage_count*interval
    return effective_coverage_time


def calculate_effective_coverage_time_for_optimization(params, drone_initial_position, missile_initial_position):
    """
    为优化算法计算有效遮蔽时间的包装函数。

    参数：
    params: 优化参数 [flight_speed, drop_time, explosion_delay, flight_direction_x, flight_direction_y]
    drone_initial_position: 无人机的初始位置 (np.array)
    missile_initial_position: 导弹的初始位置 (np.array)

    返回：
    effective_coverage_time: 有效遮蔽的时间总和 (秒)
    """
    flight_speed, drop_time, explosion_delay, dir_x, dir_y = params
    
    # 创建飞行方向向量（z方向速度为0）
    flight_direction = np.array([dir_x, dir_y, 0])
    
    # 如果方向向量为零向量，则使用默认方向（朝向原点）
    if np.linalg.norm(flight_direction) == 0:
        target_direction = np.array([0, 0, 0]) - drone_initial_position
        flight_direction = np.array([target_direction[0], target_direction[1], 0])
    
    # 归一化方向向量
    flight_direction = flight_direction / np.linalg.norm(flight_direction)
    
    effective_coverage_time = calculate_effective_coverage_time(
        drone_initial_position, missile_initial_position,
        flight_speed, drop_time, explosion_delay, flight_direction
    )
    
    # 只有当覆盖时间超过0.5才打印信息
    if effective_coverage_time > 0.5:
        print(f"High coverage time detected: {effective_coverage_time:.4f} seconds for params: Flight Speed={flight_speed:.2f}, Drop Time={drop_time:.2f}, Explosion Delay={explosion_delay:.2f}, Direction=({dir_x:.4f}, {dir_y:.4f})")
    
    return effective_coverage_time


# 示例用法
drone_initial_position = np.array([17800, 0, 1800])
missile_initial_position = np.array([20000, 0, 2000])
