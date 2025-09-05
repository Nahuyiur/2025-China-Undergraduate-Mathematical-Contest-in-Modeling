from utils.motion import calculate_drop_and_explosion_position,calculate_missile_position
from utils.judge_cross_by_point_pick import generate_initial_guess_and_judge
from utils.judge_cross1 import 
import numpy as np
import math
# Initial conditions
drone_initial_position = np.array([17800, 0, 1800])
flight_speed = 120  # m/s
missile_initial_position = np.array([20000, 0, 2000])
drop_time = 1.5  # seconds after mission start
explosion_delay = 3.6  # seconds after drop
flight_direction = np.array([0, 0, 1800]) - drone_initial_position  # Direction towards target (0, 0, 0)
radius = 10
# Time range
time_range = np.linspace(0, 50, 50000)


true_count=0
false_count=0
for t in time_range:
    time_since_explosion = t - (drop_time + explosion_delay)  # 从引爆开始的时间
    if time_since_explosion < 0:
        continue
    # 错误检查：烟幕干扰弹已消失
    elif time_since_explosion > 20:
        continue

    drop_position, explosion_position, smoke_position = calculate_drop_and_explosion_position(
        drone_initial_position, flight_direction, flight_speed, drop_time, explosion_delay, t)
    
    missile_position = calculate_missile_position(missile_initial_position, t)
    x1, y1, z1 = smoke_position
    x2, y2, z2 = missile_position
    
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    
    # 如果距离小于半径，输出 True
    if distance < radius:
        print(f"At time {t}, the result is: True")
        continue
    # 调用 final_cross_judge 判断是否有交点
    is_intersecting = generate_initial_guess_and_judge(missile_position,smoke_position)
    
    # 统计结果
    if is_intersecting:
        print(f"At time {t}, the result is: True")
        true_count += 1

    else:
        print(f"At time {t}, the result is: False")
        false_count += 1



# 输出最终统计结果
print(f"Total True: {true_count}")
print(f"Total False: {false_count}")
