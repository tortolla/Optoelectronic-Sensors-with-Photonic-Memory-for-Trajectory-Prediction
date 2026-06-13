import os
import numpy as np
from PIL import Image

# Ask the user for the mean and standard deviation
mean = float(input("Enter the mean value: "))
std = float(input("Enter the standard deviation value: "))

# Ask for the path to the folder with images
image_folder = input("Enter the path to the folder with images: ")

# Ask for the path to the folder for saving images and create it if it does not exist
output_folder = input("Enter the path to the folder for saving images: ")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get the list of image files from the folder
image_files = os.listdir(image_folder)

# Process each image
for i, image_file in enumerate(image_files):
    image_path = os.path.join(image_folder, image_file)
    img = Image.open(image_path)
    image_array = np.array(img)
    
    # Check if the image is not grayscale; if so, convert it to grayscale
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        image_array = np.mean(image_array, axis=2)
    
    rows, cols = image_array.shape
    gaussian = np.random.normal(mean, std, (rows, cols))
    noisy_image = image_array + gaussian

    # Clip values to the 0-255 range and convert to uint8
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

    # Save the image to the new folder
    output_path = os.path.join(output_folder, image_file)
    noisy_image_pil = Image.fromarray(noisy_image)
    noisy_image_pil.save(output_path)

    print(f"Processed image: {image_file}, saved to: {output_path}")

print("All images have been successfully processed.")
