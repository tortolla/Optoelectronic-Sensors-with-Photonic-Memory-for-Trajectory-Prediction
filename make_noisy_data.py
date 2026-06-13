import os
import numpy as np
from PIL import Image

# Запрашиваем у пользователя среднее и дисперсию
mean = float(input("Введите значение mean (среднее): "))
std = float(input("Введите значение std (дисперсия): "))

# Запрашиваем путь к папке с изображениями
image_folder = input("Введите путь к папке с изображениями: ")

# Запрашиваем путь к папке для сохранения изображений и создаем ее, если не существует
output_folder = input("Введите путь к папке для сохранения изображений: ")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Получаем список файлов изображений из папки
image_files = os.listdir(image_folder)

# Обработка каждого изображения
for i, image_file in enumerate(image_files):
    image_path = os.path.join(image_folder, image_file)
    img = Image.open(image_path)
    image_array = np.array(img)
    
    # Проверка, если изображение не в градациях серого, преобразуем
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        image_array = np.mean(image_array, axis=2)
    
    rows, cols = image_array.shape
    gaussian = np.random.normal(mean, std, (rows, cols))
    noisy_image = image_array + gaussian

    # Обрезаем значения до диапазона 0-255 и конвертируем в тип uint8
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

    # Сохранение изображения в новую папку
    output_path = os.path.join(output_folder, image_file)
    noisy_image_pil = Image.fromarray(noisy_image)
    noisy_image_pil.save(output_path)

    print(f"Обработано изображение: {image_file}, сохранено в: {output_path}")

print("Все изображения успешно обработаны.")
