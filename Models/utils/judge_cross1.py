import math
from scipy.optimize import minimize
import random

r = 10  # 烟雾弹半径
epsilon = 1e-8  # 精度


def generate_initial_guess(num_guesses=2000):
    """
    生成多个初始猜测，每个猜测是一个三元组 (f, g, h)，
    其中 f 和 g 满足约束 f^2 + (g - 200)^2 = 49，h 是 [0, 10] 范围内的随机数。
    
    参数：
    num_guesses -- 生成的初始猜测数量（默认为 5）
    
    返回：
    初始猜测的列表，每个元素是一个三元组 (f, g, h)
    """
    initial_guesses = []
    
    for _ in range(num_guesses):
        # 随机选择角度 theta（范围从 0 到 2pi）
        theta = random.uniform(0, 2 * math.pi)
        
        # 计算 f 和 g
        f = 7 * math.cos(theta)
        g = 200 + 7 * math.sin(theta)
        
        # 生成 h (0 <= h <= 10)
        h = random.uniform(0, 10)
        
        # 将 (f, g, h) 添加到初始猜测列表中
        initial_guesses.append([f, g, h])
    
    return initial_guesses

def calculate_distance(missile_point, ball_center):
    """计算两点之间的距离"""
    x, y, z = missile_point
    a, b, c = ball_center
    d = math.sqrt((x - a)**2 + (y - b)**2 + (z - c)**2)
    return d

def calculate_cos_theta(r, d):
    """根据公式计算圆锥角"""
    if d == 0:
        return 0  # 避免除以零的错误
    cos_theta = math.sqrt(d*d - r*r) / d
    return cos_theta

def calculate_alpha(missile_point, ball_center):
    """计算根轴向量"""
    x, y, z = missile_point
    a, b, c = ball_center
    alpha = (x - a, y - b, z - c)
    return alpha

def calculate_beta(missile_point, vars):
    """计算 beta 向量（导弹与圆柱侧面点的向量）"""
    x, y, z = missile_point
    f, g, h = vars
    beta = (x - f, y - g, z - h)
    return beta

def cylinder_constraint(vars):
    """圆柱侧面的约束：高度+圆"""
    f, g, h = vars
    # 圆柱的约束
    constraint1 = f**2 + (g - 200)**2 - 49  # 等式约束：f^2 + (g - 200)^2 = 49
    constraint2 = h - 10  # h(t) <= 10
    constraint3 = -h  # h(t) >= 0
    return [constraint1, constraint2, constraint3]

def cross_equation(vars, missile_point, ball_center):
    """计算 beta 和 alpha 的夹角，并与 cos_theta 比较"""
    f, g, h = vars
    # 计算 alpha 和 beta 向量
    alpha = calculate_alpha(missile_point, ball_center)
    beta = calculate_beta(missile_point, (f, g, h))
    
    # 计算它们的点积
    dot_product = sum(a * b for a, b in zip(alpha, beta))
    
    # 计算 alpha 和 beta 的模长
    alpha_mag = math.sqrt(sum(a**2 for a in alpha))
    beta_mag = math.sqrt(sum(b**2 for b in beta))
    
    # 计算 cos_theta
    cos_theta = dot_product / (alpha_mag * beta_mag)
    
    # 计算球心和点之间的距离
    d = calculate_distance(missile_point, ball_center)
    
    # 计算目标 cos_theta
    expected_cos_theta = calculate_cos_theta(r, d)
    
    # 返回误差的平方，越接近零，越满足条件
    return abs(cos_theta - expected_cos_theta)

def solve_equation(missile_point, ball_center, initial_guesses):
    """求解方程并判断是否有解"""
    # 设置约束条件
    constraints = (
        {'type': 'eq', 'fun': lambda vars: cylinder_constraint(vars)[0]},  # f^2 + (g - 200)^2 = 49（等式约束）
        {'type': 'ineq', 'fun': lambda vars: -cylinder_constraint(vars)[1]},  # h <= 10
        {'type': 'ineq', 'fun': lambda vars: -cylinder_constraint(vars)[2]}   # h >= 0
    )

    # 尝试多个初始猜测
    best_result = None
    for initial_guess in initial_guesses:
        result = minimize(cross_equation, initial_guess, args=(missile_point, ball_center), constraints=constraints, options={'disp': False})

        # 如果找到解并且误差小于阈值，更新最优解
        if result.success and result.fun < epsilon:
            best_result = result
            break  # 找到一个解就停止优化
    
    # 判断是否成功找到解
    if best_result:
        return True, best_result.x  # 返回解
    else:
        return False, None  # 否则返回没有解

# 输入：球心坐标、导弹坐标
ball_center = (0, 0, 0)  # 球心坐标
missile_position = (1, 1, 1)  # 导弹坐标

# 多个初始猜测
initial_guesses = [
    [7, 200, 5],  # 初始猜测 f(t) = 1, g(t) = 200, h(t) = 5
    [1.5, 200, 0],
    [1, 210, 5],
    [1, 190, 5]
]


def final_cross_judge(missile_position,ball_center):
    initial_guesses = generate_initial_guess(num_guesses=10)
    # 调用方法判断是否有解
    has_solution, solution = solve_equation(missile_position, ball_center, initial_guesses)

    if has_solution:
        print("方程组有解，解为：", solution)
        return False
    else:
        print("方程组无解")# 这个意味着没有相交
        return True
    
# if __name__ == "__main__":
#     # 测试函数生成初始猜测
#     initial_guesses = generate_initial_guess(num_guesses=10)

#     # 输出生成的初始猜测
#     for guess in initial_guesses:
#         print(f"初始猜测: f = {guess[0]}, g = {guess[1]}, h = {guess[2]}")



    
