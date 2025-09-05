import math
r=10
epsilon=1e-8
from scipy.optimize import minimize
def calculate_distance(missile_point, ball_center):
    """计算球心和点之间的距离"""
    x, y, z = missile_point
    a, b, c = ball_center
    d = math.sqrt((x - a)**2 + (y - b)**2 + (z - c)**2)
    return d

def calculate_cos_theta(r, d):
    """根据公式计算圆锥角"""
    if d == 0:
        return 0  # 避免除以零的错误
    cos_theta=math.sqrt(d*d-r*r)/d
    return d

def calculate_alpha(missile_point,ball_center):
    """计算根轴向量"""
    x, y, z = missile_point
    a, b, c = ball_center
    alpha=(x-a,y-b,z-c)
    return alpha

def calculate_beta(missile_point,vars):
    x, y, z = missile_point
    f, g, h = vars
    beta = (x-f,y-g,z-h)

def cylinder_constraint(vars):
    """圆柱侧面的约束：高度+圆"""
    f, g, h = vars
    # 圆柱的约束
    constraint1 = f**2 + (g - 200)**2 - 49  # 要求 f(t)^2 + (g(t) - 200)^2 <= 49
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
    
    # 判断是否满足夹角条件
    return (cos_theta - expected_cos_theta)**2  # 返回误差的平方，越接近零，越满足条件

def solve_equation(missile_point, ball_center):
    """求解方程并判断是否有解"""
    # 初始猜测
    initial_guess = [1, 200, 5]  # 初始猜测 f(t) = 1, g(t) = 200, h(t) = 5
    
    # 设置约束条件
    constraints = (
        {'type': 'eq', 'fun': lambda vars: -cylinder_constraint(vars)[0]},  # f^2 + (g - 200)^2 <= 49
        {'type': 'ineq', 'fun': lambda vars: -cylinder_constraint(vars)[1]},  # h <= 10
        {'type': 'ineq', 'fun': lambda vars: -cylinder_constraint(vars)[2]}   # h >= 0
    )
    
    # 使用 scipy.optimize.minimize 求解
    result = minimize(cross_equation, initial_guess, args=(missile_point, ball_center), constraints=constraints)
    
    # 判断是否成功找到解
    if result.success and result.fun < 1e-8:  # 判断误差是否足够小
        return True, result.x  # 如果解满足条件，返回解
    else:
        return False, None  # 否则返回没有解


# 实际操作上你得给这两个坐标
ball_center = (0, 0, 0)  # 球心坐标
missile_position = (1, 1, 1)  # 

has_solution, solution = solve_equation(missile_position, ball_center)

if has_solution:
    print("方程组有解，解为：", solution)
else:
    print("方程组无解")
