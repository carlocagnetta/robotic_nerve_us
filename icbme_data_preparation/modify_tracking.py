import os
import pandas as pd
from PIL import Image
import numpy as np
from scipy import ndimage
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt


# ... [previous function definitions] ...

def fit_and_plot_spline(x, z_values, full_idx, s=3000):
    # Using UnivariateSpline to create a smooth spline. s parameter controls the smoothness
    spl = UnivariateSpline(x, z_values, s=s)
    z_smooth = spl(full_idx)

    # Plotting
    plt.plot(x, z_values, 'bo', label='Original z values')
    plt.plot(full_idx, z_smooth, 'r-', label='Smoothed spline')
    plt.legend()
    plt.xlabel('Image Index')
    plt.ylabel('Z Coordinate')
    plt.title('Smooth Spline Fit on Z Coordinates')
    plt.show()

    return z_smooth


def read_images_from_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if
                   os.path.isfile(os.path.join(folder_path, f)) and f.endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()
    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        with Image.open(image_path) as img:
            images.append(np.array(img))
    return images


def get_center_of_mass(image):
    # This finds the center of mass of the pixels labeled as 1
    center_of_mass = ndimage.measurements.center_of_mass(image)
    return center_of_mass


def read_tracking_data(tracking_file):
    # Read the CSV using pandas
    df = pd.read_csv(tracking_file, sep='\t', header=None, usecols=[12, 13, 14])
    return df.values


def compute_world_center_of_mass(image_center, world_coords):
    resolution = np.array([0.556, 0.385875])
    adjusted_center = np.array(image_center) * resolution
    image_size = np.array([256, 256])
    image_center_to_adjusted_center = image_size / 2 * resolution - adjusted_center
    world_center_of_mass = [world_coords[0], world_coords[2]] + -1 * adjusted_center
    # keeping the same z-coordinate from world_coords
    return (world_center_of_mass[0], world_coords[1], world_center_of_mass[1]), image_center_to_adjusted_center


folder_path = '/mnt/projects/aorta_scan/Aorta_scan_Live3D/felix_rec/breathing_speed50/all_imgs/cactuss_seg_pred/'  # Replace with your folder path
tracking_file = '/mnt/projects/aorta_scan/Aorta_scan_Live3D/felix_rec/breathing_speed50/tracking.csv'
modified_tracking_file = '/mnt/projects/aorta_scan/Aorta_scan_Live3D/felix_rec/breathing_speed50/modified_tracking.csv'

images = read_images_from_folder(folder_path)
world_coords = read_tracking_data(tracking_file)

if len(images) != len(world_coords):
    raise ValueError("The number of images and tracking records do not match!")

world_centers = []
mass_centers = []
non_empty_indices = []
non_empty_z_values = []
full_idx = []

for idx, (image, coords) in enumerate(zip(images, world_coords)):
    full_idx.append(idx)
    if np.any(image == 1):  # Check if there's any pixel with value 1
        y, x = get_center_of_mass(image)  # Center of mass returns in (y, x) format
        world_center, mass_center = compute_world_center_of_mass((x, y), coords)
        world_centers.append(world_center)
        mass_centers.append(mass_center)
        non_empty_indices.append(idx)
        non_empty_z_values.append(coords[2])
    else:
        world_centers.append(world_centers[-1] if len(world_centers) > 0 else coords)
        mass_centers.append(mass_centers[-1] if len(mass_centers) > 0 else [0, 0])

z_smooth = fit_and_plot_spline(non_empty_indices, non_empty_z_values, full_idx)

# Modifying the original world coordinates with the smoothed z values
modified_world_coords = world_coords.copy()
for idx in range(len(world_coords)):
    modified_world_coords[idx, 2] = z_smooth[idx] - z_smooth[0] + world_coords[0][2] + mass_centers[0][1] - mass_centers[idx][1] # -mass_centers[idx][1] + 264 # z_smooth[idx]

#
# for i in range(len(world_centers)):
#     modified_world_coords[i][2] = z_smooth[i]

plt.plot(modified_world_coords[:, 2], 'r-')
plt.plot(modified_world_coords[:, 2] + np.array(mass_centers)[:,1])
plt.show()

# Saving to a new tracking file
df_modified = pd.DataFrame(modified_world_coords)
original_df = pd.read_csv(tracking_file, sep='\t', header=None)
original_df[[12, 13, 14]] = df_modified
original_df.to_csv(modified_tracking_file, sep='\t', index=False, header=False)