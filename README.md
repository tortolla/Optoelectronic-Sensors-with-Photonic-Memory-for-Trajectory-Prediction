Photonic-Memory Trajectory Dataset Generation

This repository contains scripts and auxiliary files for generating synthetic motion-frame datasets, applying a numerical photonic-memory sensor model, adding Gaussian noise, and storing experimental/calibration data for ZnO-based photonic-memory dynamics.

The pipeline is designed for experiments with moving white circular objects on a black background. Clean binary motion frames are generated first. Then, a photonic-memory sensor model is applied to simulate time-dependent conductivity accumulation and relaxation. Finally, Gaussian noise can be added to create noisy datasets.

Repository Structure

.
├── README.md
├── generate_motion_frames.py
├── generate_photonic_memory_frames.py
├── add_gaussian_noise.py
├── auxiliary_three_object_motion.py
├── experiment_results.csv
├── zno_potentiation_decay_trace.txt
└── zno_relaxation_trace.txt

Pipeline Overview

The main dataset generation pipeline consists of three steps:

1. Generate clean binary motion frames
2. Apply the photonic-memory sensor model
3. Add Gaussian noise if required

Recommended execution order:

python generate_motion_frames.py
python generate_photonic_memory_frames.py
python add_gaussian_noise.py

1. Generate Clean Motion Frames

File:

generate_motion_frames.py

This script generates synthetic image sequences with one or more moving white circular objects on a black background.

Each image has size:

600 × 600 pixels

Each object is represented as a white circle. The object moves along the X axis with a fixed velocity of 1 pixel per frame. The Y coordinate is calculated from a linear function:

y = kx + b

The script uses predefined linear functions with different slopes and intercepts. During generation, the trajectory function can be switched after a user-defined number of steps.

The generated object coordinates are written directly into the filename.

Example for one object:

1_123_245.png
2_124_246.png
3_125_247.png

Example for two objects:

1_123_245_342_120.png

In this filename:

1       = frame number
123_245 = coordinates of the first object
342_120 = coordinates of the second object

The script asks for the following parameters:

Enter the ball radius:
Enter the number of frames:
Enter the folder for saving images:
Enter the number of balls:
Enter the minimum number of steps before switching the function:
Enter the maximum number of steps before switching the function:

Run:

python generate_motion_frames.py

Example input:

Enter the ball radius: 10
Enter the number of frames: 100000
Enter the folder for saving images: raw_motion_frames
Enter the number of balls: 1
Enter the minimum number of steps before switching the function: 5
Enter the maximum number of steps before switching the function: 40

Output example:

raw_motion_frames/

This folder contains the generated clean binary motion-frame dataset.

2. Generate Photonic-Memory Frames

File:

generate_photonic_memory_frames.py

This script applies a numerical photonic-memory sensor model to a sequence of clean binary motion frames.

The input is a folder with generated binary images. The output is a grayscale image sequence representing the time-dependent conductivity response of a photonic-memory sensor.

For illuminated pixels, the conductivity increases according to the experimentally fitted potentiation function:

G(t) = A + Bt + Ct² + Dt³

For non-illuminated pixels, the conductivity relaxes according to the experimentally fitted double-exponential relaxation function:

G(t) = A exp(-Bt) + C exp(-Dt)

The script processes images in chronological order. The frame order is determined from the leading number in each filename.

The script uses multiprocessing. The number of CPU cores is selected by the user.

The script asks for the following parameters:

Enter the path to the directory with images:
Enter the time between frames:
Enter the number of CPUs to use:

Run:

python generate_photonic_memory_frames.py

Example input:

Enter the path to the directory with images: raw_motion_frames
Enter the time between frames: 400
Enter the number of CPUs to use, available: 8: 8

Output folder example:

raw_motion_frames_time:400/

This folder contains the photonic-memory-transformed grayscale frames.

A log file is created automatically:

data_raw_motion_frames_time400.log

3. Add Gaussian Noise

File:

add_gaussian_noise.py

This script adds Gaussian noise to an image dataset.

The script reads all images from the input folder. If an image is RGB, it is converted to grayscale. Gaussian noise is then added pixel-wise.

The noisy image is clipped to the valid grayscale range:

[0, 255]

and saved as an unsigned 8-bit image.

Noise is sampled from:

N(mean, std)

The script asks for the following parameters:

Enter the mean value:
Enter the standard deviation value:
Enter the path to the folder with images:
Enter the path to the folder for saving images:

Run:

python add_gaussian_noise.py

Example input:

Enter the mean value: 50
Enter the standard deviation value: 10
Enter the path to the folder with images: raw_motion_frames_time:400
Enter the path to the folder for saving images: raw_motion_frames_time400_noise50_10

Output example:

raw_motion_frames_time400_noise50_10/

This folder contains the noisy photonic-memory frames.

Auxiliary Script

File:

auxiliary_three_object_motion.py

This script is an auxiliary motion-generation script. It can be used for additional experiments with more complex multi-object motion scenarios.

It is not required for the main pipeline.

Main pipeline:

python generate_motion_frames.py
python generate_photonic_memory_frames.py
python add_gaussian_noise.py

Auxiliary script:

python auxiliary_three_object_motion.py

Experimental and Calibration Files

experiment_results.csv

This file contains experimental or processed numerical results associated with the trajectory-prediction experiments.

It can be used for storing metrics, model outputs, or summarized experiment results.

zno_potentiation_decay_trace.txt

This file contains the ZnO potentiation trace used for calibration of the photonic-memory sensor model.

It is associated with the conductivity increase under illumination.

zno_relaxation_trace.txt

This file contains the ZnO relaxation trace used for calibration of the photonic-memory sensor model.

It is associated with conductivity decay after illumination is removed.

Full Example Workflow

Generate clean motion frames:

python generate_motion_frames.py

Example input:

Enter the ball radius: 10
Enter the number of frames: 100000
Enter the folder for saving images: raw_motion_frames
Enter the number of balls: 1
Enter the minimum number of steps before switching the function: 5
Enter the maximum number of steps before switching the function: 40

Apply the photonic-memory model:

python generate_photonic_memory_frames.py

Example input:

Enter the path to the directory with images: raw_motion_frames
Enter the time between frames: 400
Enter the number of CPUs to use, available: 8: 8

Add Gaussian noise:

python add_gaussian_noise.py

Example input:

Enter the mean value: 50
Enter the standard deviation value: 10
Enter the path to the folder with images: raw_motion_frames_time:400
Enter the path to the folder for saving images: raw_motion_frames_time400_noise50_10

Final output:

raw_motion_frames_time400_noise50_10/

Notes

The filenames of the generated images contain the frame number and object coordinates. This makes it possible to reconstruct object trajectories directly from the filenames.

The photonic-memory model simulates temporal accumulation and relaxation of conductivity, so the output frames are not binary. They encode the memory trace left by previous object positions.

Gaussian noise can be added after the photonic-memory transformation to generate noisy experimental conditions.
