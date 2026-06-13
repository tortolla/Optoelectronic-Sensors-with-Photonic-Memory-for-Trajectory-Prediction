import random
import numpy as np
from PIL import Image, ImageDraw
import os
from tqdm import tqdm
from scipy.interpolate import interp1d
import math

# ======= Параметры =======
size = 600  # Размер изображения и поля

# Ввод параметров пользователем
radius = int(input("Введите радиус шариков: "))  # Радиус шарика
num_frames = int(input("Введите количество кадров: "))  # Количество кадров
output_folder = input("Введите папку для сохранения изображений: ")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
num_balls = int(input("Введите количество шариков: "))  # Количество шариков
pixels_per_frame = 1  # Сдвиг за кадр
random_param = 0  # Убираем случайность для перемещения
min_steps = int(input("Введите минимальное количество шагов перед переключением функции: "))
max_steps = int(input("Введите максимальное количество шагов перед переключением функции: "))

# ======= Определение функций траекторий =======

def func_parabola(x, a=0.0001, h=size/2, k=size/2):
    y = a * (x - h) ** 2 + k
    return y

def func_linear_with_noise(x, noise_level=0.005):
    y = x
    noise = np.random.uniform(-noise_level, noise_level, size=x.shape)
    y_noisy = y + noise * size
    return y_noisy

# ======= Функции нормализации =======

def normalize_func_with_phase(f, phase):
    x_values = np.linspace(0, size, num=10000)
    y_values = f(x_values, phase=phase)
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    y_scaled = y_normalized * (size - 2 * radius) + radius
    return x_values, y_scaled

def func_sine(x, amplitude=100, frequency=0.01, phase=0):
    return amplitude * np.sin(frequency * x + phase) + size / 2

def func_spiral(x, a=0.1, b=0.05):
    return size / 2 + a * x * np.cos(b * x), size / 2 + a * x * np.sin(b * x)

def normalize_func_parabola(f):
    x_values = np.linspace(0, size, num=10000)
    y_values = f(x_values)
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    y_scaled = y_normalized * (size - 2 * radius) + radius
    return x_values, y_scaled

def normalize_func_spiral(f):
    x_values = np.linspace(0, size, num=10000)
    y_values = [f(x) for x in x_values]
    x_vals = [val[0] for val in y_values]
    y_vals = [val[1] for val in y_values]
    min_y = np.min(y_vals)
    max_y = np.max(y_vals)
    y_normalized = (y_vals - min_y) / (max_y - min_y + 1e-6)
    y_scaled = y_normalized * (size - 2 * radius) + radius
    return x_vals, y_scaled

def normalize_func_sine(f):
    x_values = np.linspace(0, size, num=10000)
    y_values = f(x_values)
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    y_scaled = y_normalized * (size - 2 * radius) + radius
    return x_values, y_scaled

def normalize_func_linear_with_noise(f):
    x_values = np.linspace(0, size, num=10000)
    y_values = f(x_values)
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    y_scaled = y_normalized * (size - 2 * radius) + radius
    return x_values, y_scaled

import numpy as np

def func_linear(x, slope, intercept):
    y = slope * x + intercept
    return y
    
def normalize_func_linear(f):
    # Генерация значений x
    x_values = np.linspace(0, size, num=10000)
    
    # Вычисление значений y на основе функции f
    y_values = f(x_values)
    
    # Нормализация y: приведение к диапазону [0, 1]
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    
    # Масштабирование и сдвиг значений y в новый диапазон
    y_scaled = y_normalized * (size - 2 * radius) + radius
    
    return x_values, y_scaled
# ======= Список доступных функций =======
function_choices = ['linear']



# ======= Параметры для линейной функции =======
linear_params = [
    {'slope': 1.0, 'intercept': 0.0},  # Параметры для стандартной линейной функции
    {'slope': 2.0, 'intercept': 1.0},  # Увеличенный наклон и сдвиг
    {'slope': -1.0, 'intercept': 0.0}, # Отрицательный наклон
    {'slope': 0.5, 'intercept': -2.0}, # Маленький наклон и отрицательный сдвиг
    {'slope': 3.0, 'intercept': 5.0},  # Большой наклон и положительный сдвиг
]

# # ======= Параметры для синусоидальной траектории =======
# sine_params = [
#     {'amplitude': 100 + 10, 'frequency': 0.01 , 'phase': 0.3* np.pi},
#     {'amplitude': 150 - 20, 'frequency': 0.02 , 'phase': np.pi*0.7},

# ]


# ======= Класс шарика =======
class Ball:
    def __init__(self, min_steps, max_steps, balls):
        self.radius = radius
        self.function_switch_counter = random.randint(min_steps, max_steps)
        self.prev_y = None
        self.direction = 1  # Направление по оси X, случайность убрана
        self.speed = pixels_per_frame  # Скорость движения
        
        # Генерация случайной позиции с проверкой на столкновения с другими шариками
        self.set_random_position(balls)
        
        # Сначала выбираем функцию движения и нормализуем значения
        self.set_new_function()
        
        # Теперь вызываем update_y, после инициализации всех параметров
        self.update_y()

    def set_random_position(self, balls):
        # Пытаемся найти корректную случайную позицию, не слишком близкую к другим шарикам
        while True:
            self.x = random.uniform(self.radius, size - self.radius)
            self.y = random.uniform(self.radius, size - self.radius)
            # Проверка на столкновение с другими шариками
            if all(np.sqrt((self.x - other_ball.x) ** 2 + (self.y - other_ball.y) ** 2) > 2 * self.radius for other_ball in balls):
                break

    def set_new_function(self):
        self.old_function = getattr(self, 'function', None)
        self.old_x_vals = getattr(self, 'x_vals', None)
        self.old_y_vals = getattr(self, 'y_vals', None)
        self.old_interp_function = getattr(self, 'interp_function', None)
        self.transition_progress = 0  # Для плавного перехода
        self.transition_steps = 10  # Количество шагов для перехода

        # Случайно выбираем функцию движения
        function_choice = random.choice(function_choices)
        self.function_choice = function_choice

        # if function_choice == 'parabola':
        #     # Случайно выбираем параметры для параболы
        #     params = random.choice(parabola_params)
        #     self.function = lambda x: func_parabola(x, **params)
        #     self.x_vals, self.y_vals = normalize_func_parabola(self.function)

        # elifunction_choice == 'linear':
        # Случайно выбираем параметры для линейной траектории с шумом
        params = random.choice(linear_params)
        self.function = lambda x: func_linear(x, **params)
        self.x_vals, self.y_vals = normalize_func_linear(self.function)

        self.interp_function = interp1d(self.x_vals, self.y_vals, kind='linear', fill_value="extrapolate")

    def update_y(self):
        # Плавный переход между траекториями
        y_new = self.interp_function(self.x)
        if self.old_function and self.transition_progress < self.transition_steps:
            y_old = self.old_interp_function(self.x)
            alpha = self.transition_progress / self.transition_steps
            y = (1 - alpha) * y_old + alpha * y_new
            self.transition_progress += 1
        else:
            y = y_new

        # Ограничиваем максимальное изменение y за кадр
        y = float(y)
        if self.prev_y is not None:
            delta_y = y - self.prev_y
            max_delta = 1  # Максимальное изменение y за кадр
            if abs(delta_y) > max_delta:
                y = self.prev_y + np.sign(delta_y) * max_delta
        self.y = y
        self.prev_y = y

    def move(self, balls):
        # Обновляем позицию по X
        self.x += self.direction * self.speed
        self.x = round(self.x)
        # Ограничиваем x в пределах границ
        self.x = max(min(self.x, size - self.radius), self.radius)
        
        # Обновляем y
        self.update_y()
        
        # Проверка столкновений с другими шариками
        for other_ball in balls:
            if self != other_ball and self.check_collision(other_ball):
                # Если есть столкновение, меняем направления шариков
                self.resolve_collision(other_ball)
                
        # Проверяем столкновение со стенками по X
        if self.x - self.radius <= 0 or self.x + self.radius >= size:
            self.direction *= -1  # Меняем направление
            self.x = max(min(self.x, size - self.radius), self.radius)
            self.set_new_function()

        # Проверяем границы по Y
        if self.y - self.radius <= 0 or self.y + self.radius >= size:
            self.set_new_function()
            self.y = max(min(self.y, size - self.radius), self.radius)
        
        # Уменьшаем счетчик переключения функции
        self.function_switch_counter -= 1
        if self.function_switch_counter <= 0:
            self.set_new_function()
            self.function_switch_counter = random.randint(min_steps, max_steps)

    def get_position(self):
        return (self.x, self.y)

    def check_collision(self, other_ball):
        # Проверка на столкновение
        dist = np.sqrt((self.x - other_ball.x) ** 2 + (self.y - other_ball.y) ** 2)
        return dist < 2 * radius

    def resolve_collision(self, other_ball):
        # Вычисление векторов скорости по осям X и Y для обоих шариков
        dx = self.x - other_ball.x
        dy = self.y - other_ball.y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Проверка, если шарики сталкиваются
        if distance <= 2 * self.radius:
            # Вычисление нормализованного вектора столкновения
            if distance != 1:
                nx = dx / distance
                ny = dy / distance
            else:
                # Если шарики находятся в одной точке (distance == 0), задаем нормаль
                nx = -1
                ny = -1  # Направление можно задать любое, важно только не нулевой вектор
    
            # Вычисление относительной скорости
            relative_velocity_x = self.direction - other_ball.direction
            
            # Вычисление упругого столкновения (обмен скоростями)
            self.direction -= 2 * relative_velocity_x * nx
            other_ball.direction += 2 * relative_velocity_x * nx
            
            # Вычисление перекрытия и коррекция положения
            overlap = 2 * self.radius - distance
            if overlap > 0:  # Если они действительно перекрываются
                self.x += nx * overlap / 2
                self.y += ny * overlap / 2
                other_ball.x -= nx * overlap / 2
                other_ball.y -= ny * overlap / 2
    
            # Дополнительная защита от застревания: если они все еще слишком близки,
            # минимизируем перекрытие
            min_distance = 2 * self.radius + 0.01  # Минимальное расстояние между шариками
            new_distance = np.sqrt((self.x - other_ball.x)**2 + (self.y - other_ball.y)**2)
            if new_distance < min_distance:
                correction = min_distance - new_distance
                # Корректируем позиции, чтобы шарики не застряли
                self.x += nx * correction / 2
                self.y += ny * correction / 2
                other_ball.x -= nx * correction / 2
                other_ball.y -= ny * correction / 2



# ======= Создаем шарики =======
balls = []
for _ in range(num_balls):
    balls.append(Ball(min_steps, max_steps, balls))  # Передаем список шариков для проверки столкновений при генерации новых

# Генерация и сохранение кадров
for frame_num in tqdm(range(1, num_frames + 1), desc="Сохранение изображений"):
    # Создаем черное изображение
    img = Image.new('RGB', (size, size), 'black')
    draw = ImageDraw.Draw(img)

    coords = []
    # Обновляем позиции и рисуем шарики
    for ball in balls:
        ball.move(balls)  # Переходим к передаче списка balls в метод move()
        x, y = ball.get_position()
        x1 = x - ball.radius
        y1 = y - ball.radius
        x2 = x + ball.radius
        y2 = y + ball.radius
        draw.ellipse([x1, y1, x2, y2], fill='white')
        
        # Добавляем координаты шарика в список
        coords.append(f"{int(x)}_{int(y)}")

    # Формируем строку с координатами для имени файла
    coords_str = '_'.join(coords)

    # Формируем имя файла: номер кадра и координаты шариков
    filename = f"{frame_num}_{coords_str}.png"
    img.save(os.path.join(output_folder, filename))