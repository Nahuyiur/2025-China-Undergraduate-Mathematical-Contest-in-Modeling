import numpy as np

def calculate_drop_and_explosion_position(drone_initial_position, flight_direction, flight_speed, drop_time, explosion_delay, t):
    """
    计算烟幕干扰弹的投放点和引爆点位置，以及当前时间下烟幕干扰弹的位置。

    参数:
    drone_initial_position (np.array): 无人机的初始位置（坐标），例如 [x, y, z]。
    flight_direction (np.array): 无人机的飞行方向（单位向量），例如 [dx, dy, dz]。
    flight_speed (float): 无人机的飞行速度，单位为 m/s。
    drop_time (float): 投放时间，单位为秒。
    explosion_delay (float): 引爆延迟时间，单位为秒。
    current_time (float): 当前时间，单位为秒。

    返回:
    tuple: 投放点位置、引爆点位置和当前时间下烟幕干扰弹的位置
    """
    # 确保飞行方向是单位向量
    flight_direction = flight_direction / np.linalg.norm(flight_direction)
    #print(f"Normalized flight direction: {flight_direction}")
    # 计算无人机投放时的位置
    drop_position = drone_initial_position + flight_direction * flight_speed * drop_time
    
    # 计算引爆点位置
    # 水平运动（匀速）：
    horizontal_position = drop_position + flight_direction * flight_speed * explosion_delay

    # 垂直运动（自由落体）：y(t) = y0 - 0.5 * g * t^2
    g = 9.81  # 重力加速度，单位 m/s^2
    vertical_position = drop_position[2] - 0.5 * g * (explosion_delay ** 2)
    
    # 计算引爆点位置
    explosion_position = np.array([horizontal_position[0], horizontal_position[1], vertical_position])
    
    # 计算烟幕干扰弹在当前时间下的位置
    # 当前时间下的飞行时间：
    time_since_explosion = t - (drop_time + explosion_delay)  # 从引爆开始的时间
    
    # 水平位置不变
    current_horizontal_position =  horizontal_position
    
    # 垂直位置：如果当前时间小于引爆时间，则打印错误信息，否则匀速下沉
    if time_since_explosion < 0:
        print(f"在 t = {t} 时，错误：烟幕干扰弹未引爆")
        current_vertical_position = None  # 按照自由落体计算
    # 错误检查：烟幕干扰弹已消失
    elif time_since_explosion > 20:
        print(f"在 t = {t} 时，错误：烟幕干扰弹已消失")
        current_vertical_position = None  # 烟幕已消失，不再计算垂直位置
    else:
        # 引爆后：匀速下沉
        current_vertical_position = explosion_position[2] - 3 * time_since_explosion
    
    # 当前时间下烟幕干扰弹的位置
    current_position = np.array([current_horizontal_position[0], current_horizontal_position[1], current_vertical_position])
    #print(f"Smoke position at t = {t}: {current_position}")
    return drop_position, explosion_position, current_position

def calculate_missile_position(missile_initial_position, t):
    """
    计算导弹在时间t时的位置。

    参数:
    missile_initial_position (np.array): 导弹的初始位置（坐标），例如 [x, y, z]。
    t (float): 飞行时间，单位为秒。

    返回:
    np.array: 导弹在时间t时的位置（坐标）。
    """
    # 假目标位置固定为原点 (0, 0, 0)
    target_position = np.array([0, 0, 0])
    
    # 计算导弹飞行方向向量（从初始位置指向假目标）
    direction = target_position - missile_initial_position
    direction_norm = np.linalg.norm(direction)  # 方向向量的模（距离）
    unit_direction = direction / direction_norm  # 单位方向向量
    
    # 固定飞行速度
    missile_speed = 300  # 飞行速度 300 m/s
    
    # 计算导弹在时间t时的位置
    missile_position = missile_initial_position + unit_direction * missile_speed * t
    #print(f"missile_position at t = {t}: {missile_position}")
    return missile_position
