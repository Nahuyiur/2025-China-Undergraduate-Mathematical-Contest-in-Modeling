import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from q2.calculate_effective_coverage_time import calculate_effective_coverage_time_for_optimization
from q2.adaptive_pso_sa import AdaptivePSOWithSA

def main():
    # 设置初始位置
    drone_initial_position = np.array([17800, 0, 1800])
    missile_initial_position = np.array([20000, 0, 2000])
    
    # 定义优化参数的边界
    # [flight_speed, drop_time, explosion_delay, theta]
    param_bounds = [
        (70, 140),    # flight_speed (m/s)
        (0, 10),      # drop_time (seconds)
        (0, 10),      # explosion_delay (seconds)
        (175, 185)      # theta (degrees)
    ]
    
    # 定义适应度函数
    def fitness_function(params):
        try:
            # 从参数中提取theta并转换为方向向量
            flight_speed, drop_time, explosion_delay, theta = params
            # 将角度转换为弧度
            theta_rad = np.radians(theta)
            # 计算方向向量分量
            dir_x = np.cos(theta_rad)
            dir_y = np.sin(theta_rad)
            
            # 创建飞行方向向量（z方向速度为0）
            flight_direction = np.array([dir_x, dir_y, 0])
            
            normalized_params = [flight_speed, drop_time, explosion_delay, dir_x, dir_y]
            coverage_time = calculate_effective_coverage_time_for_optimization(
                normalized_params, drone_initial_position, missile_initial_position)
            
            # 只有当覆盖时间大于0.5时才打印参数和覆盖时间
            if coverage_time > 0.5:
                print(f"Parameters: Flight Speed={flight_speed:.2f}, Drop Time={drop_time:.2f}, Explosion Delay={explosion_delay:.2f}, Direction=({dir_x:.4f}, {dir_y:.4f}), Theta={theta:.2f}°, Coverage Time={coverage_time:.4f}")
            
            return coverage_time
        except Exception as e:
            # 如果计算过程中出现错误，返回一个很小的适应度值
            print(f"Error in fitness function: {e}")
            return 0.0
    
    # 创建自适应PSO+SA优化器
    # 定义一些初始解来引导优化，包括q1中的参数作为验证
    # 初始解格式：[flight_speed, drop_time, explosion_delay, theta]
    initial_solutions = [
        [120, 1.5, 3.6, 180],  # q1中的参数：飞行速度120m/s，投放时间1.5s，爆炸延迟3.6s，方向角180度（对应方向向量(-1,0)）
        [115, 0.5, 2, 179],
        [114, 0.3, 0, 181]
    ]
    
    pso_sa = AdaptivePSOWithSA(
        fitness_function=fitness_function,
        param_bounds=param_bounds,
        num_particles=30,
        max_iterations=100,
        initial_solutions=initial_solutions
    )
    
    # 执行优化
    print("开始优化过程...")
    best_position, best_fitness, best_solutions = pso_sa.optimize()
    
    # 打印最佳解
    print("\n" + "="*50)
    print("优化完成！")
    print("="*50)
    print(f"最佳适应度值: {best_fitness}")
    print(f"最佳参数:")
    print(f"  飞行速度: {best_position[0]:.2f} m/s")
    print(f"  投放时间: {best_position[1]:.2f} s")
    print(f"  爆炸延迟: {best_position[2]:.2f} s")
    print(f"  方向角度: {best_position[3]:.2f}°")
    # 计算对应的方向向量分量
    theta_rad = np.radians(best_position[3])
    dir_x = np.cos(theta_rad)
    dir_y = np.sin(theta_rad)
    print(f"  飞行方向X: {dir_x:.4f}")
    print(f"  飞行方向Y: {dir_y:.4f}")
    
    # 打印前10个最佳解
    print("\n" + "="*50)
    print("前10个最佳解:")
    print("="*50)
    for i, solution in enumerate(best_solutions):
        params = solution['params']
        print(f"第 {i+1} 名:")
        print(f"  有效遮蔽时间: {solution['fitness']:.4f} 秒")
        print(f"  飞行速度: {params[0]:.2f} m/s")
        print(f"  投放时间: {params[1]:.2f} s")
        print(f"  爆炸延迟: {params[2]:.2f} s")
        print(f"  方向角度: {params[3]:.2f}°")
        # 计算对应的方向向量分量
        theta_rad = np.radians(params[3])
        dir_x = np.cos(theta_rad)
        dir_y = np.sin(theta_rad)
        print(f"  飞行方向X: {dir_x:.4f}")
        print(f"  飞行方向Y: {dir_y:.4f}")
        print("-" * 30)

if __name__ == "__main__":
    main()