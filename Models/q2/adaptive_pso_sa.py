import numpy as np
import random
import math

class AdaptivePSOWithSA:
    """
    自适应粒子群优化算法结合模拟退火算法
    """
    def __init__(self, fitness_function, param_bounds, num_particles=30, max_iterations=100, initial_solutions=None):
        """
        初始化参数
        :param fitness_function: 适应度函数
        :param param_bounds: 参数边界 [(min1, max1), (min2, max2), ...]
        :param num_particles: 粒子数量
        :param max_iterations: 最大迭代次数
        :param initial_solutions: 初始解列表，用于引导优化
        """
        self.fitness_function = fitness_function
        self.param_bounds = param_bounds
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.dimensions = len(param_bounds)
        self.initial_solutions = initial_solutions if initial_solutions is not None else []
        
        # PSO参数
        self.w = 0.9  # 惯性权重
        self.c1 = 2.0  # 个体学习因子
        self.c2 = 2.0  # 社会学习因子
        self.w_damp = 0.99  # 惯性权重阻尼因子
        
        # SA参数
        self.initial_temperature = 100
        self.cooling_rate = 0.95
        self.min_temperature = 1e-8
        
        # 初始化粒子群
        self.positions = np.zeros((num_particles, self.dimensions))
        self.velocities = np.zeros((num_particles, self.dimensions))
        self.pbest_positions = np.zeros((num_particles, self.dimensions))
        self.pbest_fitness = np.full(num_particles, -np.inf)
        self.gbest_position = np.zeros(self.dimensions)
        self.gbest_fitness = -np.inf
        
        # 记录最佳解
        self.best_solutions = []
        
        self._initialize_particles()
    
    def _initialize_particles(self):
        """初始化粒子群"""
        # 首先放置初始解
        for i, initial_solution in enumerate(self.initial_solutions):
            if i >= self.num_particles:
                break
            # 确保初始解在边界内
            for j in range(self.dimensions):
                min_val, max_val = self.param_bounds[j]
                self.positions[i][j] = np.clip(initial_solution[j], min_val, max_val)
            self.velocities[i][j] = random.uniform(-abs(max_val-min_val)/2, abs(max_val-min_val)/2)
            
            self.pbest_positions[i] = self.positions[i].copy()
            fitness = self.fitness_function(self.positions[i])
            self.pbest_fitness[i] = fitness
            
            if fitness > self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = self.positions[i].copy()
        
        # 初始化剩余的粒子
        start_index = len(self.initial_solutions)
        for i in range(start_index, self.num_particles):
            for j in range(self.dimensions):
                min_val, max_val = self.param_bounds[j]
                self.positions[i][j] = random.uniform(min_val, max_val)
                self.velocities[i][j] = random.uniform(-abs(max_val-min_val)/2, abs(max_val-min_val)/2)
            
            self.pbest_positions[i] = self.positions[i].copy()
            fitness = self.fitness_function(self.positions[i])
            self.pbest_fitness[i] = fitness
            
            if fitness > self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = self.positions[i].copy()
    
    def _update_velocity_and_position(self):
        """更新粒子的速度和位置"""
        for i in range(self.num_particles):
            for j in range(self.dimensions):
                r1, r2 = random.random(), random.random()
                # 更新速度
                self.velocities[i][j] = (self.w * self.velocities[i][j] + 
                                        self.c1 * r1 * (self.pbest_positions[i][j] - self.positions[i][j]) +
                                        self.c2 * r2 * (self.gbest_position[j] - self.positions[i][j]))
                
                # 限制速度范围
                min_val, max_val = self.param_bounds[j]
                velocity_max = 0.2 * abs(max_val - min_val)
                self.velocities[i][j] = np.clip(self.velocities[i][j], -velocity_max, velocity_max)
                
                # 更新位置
                self.positions[i][j] += self.velocities[i][j]
                
                # 边界处理
                self.positions[i][j] = np.clip(self.positions[i][j], min_val, max_val)
    
    def _adaptive_parameters(self, iteration):
        """自适应调整参数"""
        # 自适应惯性权重
        self.w = 0.9 - (0.7 * iteration / self.max_iterations)
        
        # 自适应学习因子
        self.c1 = 2.5 - (1.5 * iteration / self.max_iterations)
        self.c2 = 0.5 + (1.5 * iteration / self.max_iterations)
    
    def _simulated_annealing(self, current_position, current_fitness, temperature):
        """模拟退火机制"""
        # 生成邻域解
        new_position = current_position.copy()
        for j in range(self.dimensions):
            min_val, max_val = self.param_bounds[j]
            # 在当前位置附近随机扰动
            perturbation = random.uniform(-0.1 * abs(max_val - min_val), 0.1 * abs(max_val - min_val))
            new_position[j] += perturbation
            new_position[j] = np.clip(new_position[j], min_val, max_val)
        
        new_fitness = self.fitness_function(new_position)
        
        # Metropolis准则
        if new_fitness > current_fitness or random.random() < math.exp((new_fitness - current_fitness) / temperature):
            return new_position, new_fitness
        else:
            return current_position, current_fitness
    
    def _update_best_solutions(self, position, fitness):
        """更新最佳解记录"""
        solution = {
            'fitness': fitness,
            'params': position.copy()
        }
        
        self.best_solutions.append(solution)
        # 按适应度排序，保留最好的10个解
        self.best_solutions.sort(key=lambda x: x['fitness'], reverse=True)
        self.best_solutions = self.best_solutions[:10]
    
    def optimize(self):
        """执行优化过程"""
        temperature = self.initial_temperature

        for iteration in range(self.max_iterations):
            # 更新粒子
            self._update_velocity_and_position()

            # 评估适应度
            for i in range(self.num_particles):
                fitness = self.fitness_function(self.positions[i])

                # 更新个体最优
                if fitness > self.pbest_fitness[i]:
                    self.pbest_fitness[i] = fitness
                    self.pbest_positions[i] = self.positions[i].copy()

                # 更新全局最优
                if fitness > self.gbest_fitness:
                    self.gbest_fitness = fitness
                    self.gbest_position = self.positions[i].copy()
                    self._update_best_solutions(self.gbest_position, self.gbest_fitness)

                # 模拟退火机制
                if temperature > self.min_temperature:
                    self.positions[i], self.pbest_fitness[i] = self._simulated_annealing(
                        self.positions[i], self.pbest_fitness[i], temperature)

                    # 更新全局最优（SA可能找到更好的解）
                    if self.pbest_fitness[i] > self.gbest_fitness:
                        self.gbest_fitness = self.pbest_fitness[i]
                        self.gbest_position = self.pbest_positions[i].copy()
                        self._update_best_solutions(self.gbest_position, self.gbest_fitness)

            # 自适应参数调整
            self._adaptive_parameters(iteration)

            # 降温
            temperature *= self.cooling_rate

            # 调试：打印维度信息
            print(f"Iteration {iteration + 1}/{self.max_iterations}, Best Fitness: {self.gbest_fitness}")
            print(f"gbest_position: {self.gbest_position}")
            print(f"gbest_position length: {len(self.gbest_position)}")

            # 确保数组维度符合要求
            if len(self.gbest_position) == 5:  # 确保是5个优化参数
                print(f"Best Parameters: Flight Speed={self.gbest_position[0]:.2f}, Drop Time={self.gbest_position[1]:.2f}, Explosion Delay={self.gbest_position[2]:.2f}, Direction=({self.gbest_position[3]:.4f}, {self.gbest_position[4]:.4f})")
            else:
                print("Error: gbest_position does not have the expected length!")
        
        return self.gbest_position, self.gbest_fitness, self.best_solutions
