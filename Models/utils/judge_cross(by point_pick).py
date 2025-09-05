import math
from scipy.optimize import minimize
import random

r=10
def calculate_vector(point1,point2):
    """从point1指向point2"""
    x1,y1,z1=point1
    x2,y2,z2=point2
    x,y,z=x2-x1,y2-y1,z2-z1
    return (x,y,z)

def calculate_alpha(missile_point, ball_center):
    """计算根轴向量"""
    x, y, z = missile_point
    a, b, c = ball_center
    alpha = (x - a, y - b, z - c)
    return alpha

def calculate_beta(missile_point, point):
    """计算 beta 向量（导弹与圆柱侧面点的向量）"""
    x, y, z = missile_point
    f, g, h = vars
    beta = (x - f, y - g, z - h)
    return beta

def generate_initial_guess(num=2000):
    """取在圆柱侧面的点"""
    points_pick = []
    
    for _ in range(num):
        # 随机选择角度 theta（范围从 0 到 2pi）
        theta = random.uniform(0, 2 * math.pi)
        
        # 计算 f 和 g
        f = 7 * math.cos(theta)
        g = 200 + 7 * math.sin(theta)
        
        # 生成 h (0 <= h <= 10)
        h = random.uniform(0, 10)
        
        # 将 (f, g, h) 添加到初始猜测列表中
        points_pick.append([f, g, h])
    
    return points_pick
def calculate_distance(point1,point2):
    x1,y1,z1=point1
    x2,y2,z2=point2
    d=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    return d
def judge_inner(missile_point,ball_center,point):
    """如果函数返回False，说明圆柱在内部"""
    dist1=calculate_distance(point1=point,point2=missile_point)
    dist2=calculate_distance(point1=point,point2=ball_center)
    d=calculate_distance(point1=missile_point,point2=ball_center)

    temp_d=math.sqrt(d*d-r*r)
    if dist1<temp_d and dist2>r:
        return False
    return True

def calculate_cos_theta(r, d):
    """根据公式计算圆锥角"""
    if d == 0:
        return 0  # 避免除以零的错误
    cos_theta = math.sqrt(d*d - r*r) / d
    return cos_theta

def judge_theta(missile_point,ball_center,point):
    """如果函数返回True，说明该点处角度小于切线角度"""
    alpha = calculate_alpha(missile_point, ball_center)
    beta = calculate_beta(missile_point, point)

    dot_product=sum(a*b for a,b in zip(alpha,beta))
    if dot_product<0:
        return False
    
    alpha_mag = math.sqrt(sum(a**2 for a in alpha))
    beta_mag = math.sqrt(sum(b**2 for b in beta))

    cos_theta2 = dot_product / (alpha_mag * beta_mag)

    d=calculate_distance(ball_center,missile_point)
    cos_theta=calculate_cos_theta(r,d)
    if cos_theta2<=cos_theta:
        return False
    return True
    
def cascade_judge(missile_point,ball_center,point):
    if judge_theta(missile_point,ball_center,point):
        if judge_inner(missile_point,ball_center,point):
            return True
    return False




