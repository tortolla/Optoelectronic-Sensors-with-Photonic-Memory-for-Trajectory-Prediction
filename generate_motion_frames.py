import random
import numpy as np
from PIL import Image, ImageDraw
import os
from tqdm import tqdm
from scipy.interpolate import interp1d
import math

# ======= Parameters =======
size = 600  # Image and field size

# User input parameters
radius = int(input("Enter the ball radius: "))  # Ball radius
num_frames = int(input("Enter the number of frames: "))  # Number of frames
output_folder = input("Enter the folder for saving images: ")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
num_balls = int(input("Enter the number of balls: "))  # Number of balls
pixels_per_frame = 1  # Shift per frame
random_param = 0  # Remove randomness from movement
min_steps = int(input("Enter the minimum number of steps before switching the function: "))
max_steps = int(input("Enter the maximum number of steps before switching the function: "))

# ======= Definition of trajectory functions =======

def func_parabola(x, a=0.0001, h=size/2, k=size/2):
    y = a * (x - h) ** 2 + k
    return y

def func_linear_with_noise(x, noise_level=0.005):
    y = x
    noise = np.random.uniform(-noise_level, noise_level, size=x.shape)
    y_noisy = y + noise * size
    return y_noisy

# ======= Normalization functions =======

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
    # Generate x values
    x_values = np.linspace(0, size, num=10000)
    
    # Compute y values using function f
    y_values = f(x_values)
    
    # Normalize y: bring values to the [0, 1] range
    min_y = np.min(y_values)
    max_y = np.max(y_values)
    y_normalized = (y_values - min_y) / (max_y - min_y + 1e-6)
    
    # Scale and shift y values to the new range
    y_scaled = y_normalized * (size - 2 * radius) + radius
    
    return x_values, y_scaled

# ======= List of available functions =======
function_choices = ['linear']



# ======= Parameters for the linear function =======
linear_params = [
    {'slope': 1.0, 'intercept': 0.0},  # Parameters for the standard linear function
    {'slope': 2.0, 'intercept': 1.0},  # Increased slope and shift
    {'slope': -1.0, 'intercept': 0.0}, # Negative slope
    {'slope': 0.5, 'intercept': -2.0}, # Small slope and negative shift
    {'slope': 3.0, 'intercept': 5.0},  # Large slope and positive shift
]

# # ======= Parameters for the sinusoidal trajectory =======
# sine_params = [
#     {'amplitude': 100 + 10, 'frequency': 0.01 , 'phase': 0.3* np.pi},
#     {'amplitude': 150 - 20, 'frequency': 0.02 , 'phase': np.pi*0.7},

# ]


# ======= Ball class =======
class Ball:
    def __init__(self, min_steps, max_steps, balls):
        self.radius = radius
        self.function_switch_counter = random.randint(min_steps, max_steps)
        self.prev_y = None
        self.direction = 1  # Direction along the X axis; randomness removed
        self.speed = pixels_per_frame  # Movement speed
        
        # Generate a random position with collision checking against other balls
        self.set_random_position(balls)
        
        # First select the movement function and normalize the values
        self.set_new_function()
        
        # Now call update_y after all parameters have been initialized
        self.update_y()

    def set_random_position(self, balls):
        # Try to find a valid random position that is not too close to other balls
        while True:
            self.x = random.uniform(self.radius, size - self.radius)
            self.y = random.uniform(self.radius, size - self.radius)
            # Check collision with other balls
            if all(np.sqrt((self.x - other_ball.x) ** 2 + (self.y - other_ball.y) ** 2) > 2 * self.radius for other_ball in balls):
                break

    def set_new_function(self):
        self.old_function = getattr(self, 'function', None)
        self.old_x_vals = getattr(self, 'x_vals', None)
        self.old_y_vals = getattr(self, 'y_vals', None)
        self.old_interp_function = getattr(self, 'interp_function', None)
        self.transition_progress = 0  # For smooth transition
        self.transition_steps = 10  # Number of steps for transition

        # Randomly select the movement function
        function_choice = random.choice(function_choices)
        self.function_choice = function_choice

        # if function_choice == 'parabola':
        #     # Randomly select parameters for the parabola
        #     params = random.choice(parabola_params)
        #     self.function = lambda x: func_parabola(x, **params)
        #     self.x_vals, self.y_vals = normalize_func_parabola(self.function)

        # elifunction_choice == 'linear':
        # Randomly select parameters for the linear trajectory with noise
        params = random.choice(linear_params)
        self.function = lambda x: func_linear(x, **params)
        self.x_vals, self.y_vals = normalize_func_linear(self.function)

        self.interp_function = interp1d(self.x_vals, self.y_vals, kind='linear', fill_value="extrapolate")

    def update_y(self):
        # Smooth transition between trajectories
        y_new = self.interp_function(self.x)
        if self.old_function and self.transition_progress < self.transition_steps:
            y_old = self.old_interp_function(self.x)
            alpha = self.transition_progress / self.transition_steps
            y = (1 - alpha) * y_old + alpha * y_new
            self.transition_progress += 1
        else:
            y = y_new

        # Limit the maximum y change per frame
        y = float(y)
        if self.prev_y is not None:
            delta_y = y - self.prev_y
            max_delta = 1  # Maximum y change per frame
            if abs(delta_y) > max_delta:
                y = self.prev_y + np.sign(delta_y) * max_delta
        self.y = y
        self.prev_y = y

    def move(self, balls):
        # Update the X position
        self.x += self.direction * self.speed
        self.x = round(self.x)

        # Keep x within the boundaries
        self.x = max(min(self.x, size - self.radius), self.radius)
        
        # Update y
        self.update_y()
        
        # Check collisions with other balls
        for other_ball in balls:
            if self != other_ball and self.check_collision(other_ball):
                # If there is a collision, change the directions of the balls
                self.resolve_collision(other_ball)
                
        # Check collision with the walls along X
        if self.x - self.radius <= 0 or self.x + self.radius >= size:
            self.direction *= -1  # Change direction
            self.x = max(min(self.x, size - self.radius), self.radius)
            self.set_new_function()

        # Check Y boundaries
        if self.y - self.radius <= 0 or self.y + self.radius >= size:
            self.set_new_function()
            self.y = max(min(self.y, size - self.radius), self.radius)
        
        # Decrease the function-switching counter
        self.function_switch_counter -= 1
        if self.function_switch_counter <= 0:
            self.set_new_function()
            self.function_switch_counter = random.randint(min_steps, max_steps)

    def get_position(self):
        return (self.x, self.y)

    def check_collision(self, other_ball):
        # Collision check
        dist = np.sqrt((self.x - other_ball.x) ** 2 + (self.y - other_ball.y) ** 2)
        return dist < 2 * radius

    def resolve_collision(self, other_ball):
        # Compute velocity vectors along X and Y for both balls
        dx = self.x - other_ball.x
        dy = self.y - other_ball.y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Check if the balls are colliding
        if distance <= 2 * self.radius:
            # Compute the normalized collision vector
            if distance != 1:
                nx = dx / distance
                ny = dy / distance
            else:
                # If the balls are at the same point (distance == 0), set the normal
                nx = -1
                ny = -1  # The direction can be arbitrary; the only important thing is that the vector is not zero
    
            # Compute relative velocity
            relative_velocity_x = self.direction - other_ball.direction
            
            # Compute elastic collision response by exchanging velocities
            self.direction -= 2 * relative_velocity_x * nx
            other_ball.direction += 2 * relative_velocity_x * nx
            
            # Compute overlap and correct positions
            overlap = 2 * self.radius - distance
            if overlap > 0:  # If they actually overlap
                self.x += nx * overlap / 2
                self.y += ny * overlap / 2
                other_ball.x -= nx * overlap / 2
                other_ball.y -= ny * overlap / 2
    
            # Additional protection against sticking: if they are still too close,
            # minimize the overlap
            min_distance = 2 * self.radius + 0.01  # Minimum distance between balls
            new_distance = np.sqrt((self.x - other_ball.x)**2 + (self.y - other_ball.y)**2)
            if new_distance < min_distance:
                correction = min_distance - new_distance

                # Correct positions so that the balls do not get stuck
                self.x += nx * correction / 2
                self.y += ny * correction / 2
                other_ball.x -= nx * correction / 2
                other_ball.y -= ny * correction / 2



# ======= Create balls =======
balls = []
for _ in range(num_balls):
    balls.append(Ball(min_steps, max_steps, balls))  # Pass the list of balls to check collisions when generating new ones

# Generate and save frames
for frame_num in tqdm(range(1, num_frames + 1), desc="Saving images"):
    # Create a black image
    img = Image.new('RGB', (size, size), 'black')
    draw = ImageDraw.Draw(img)

    coords = []

    # Update positions and draw balls
    for ball in balls:
        ball.move(balls)  # Pass the balls list to the move() method
        x, y = ball.get_position()
        x1 = x - ball.radius
        y1 = y - ball.radius
        x2 = x + ball.radius
        y2 = y + ball.radius
        draw.ellipse([x1, y1, x2, y2], fill='white')
        
        # Add ball coordinates to the list
        coords.append(f"{int(x)}_{int(y)}")

    # Build the coordinate string for the filename
    coords_str = '_'.join(coords)

    # Build the filename: frame number and ball coordinates
    filename = f"{frame_num}_{coords_str}.png"
    img.save(os.path.join(output_folder, filename))
