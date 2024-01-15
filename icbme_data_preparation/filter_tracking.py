import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import find_peaks


def remove_baseline(z, sample_rate):
    # Perform Fast Fourier Transform
    z_fft = np.fft.fft(z)

    # Generate frequency bins
    frequencies = np.fft.fftfreq(len(z), 1 / sample_rate)

    # Filter out frequencies below 0.1 Hz by setting corresponding magnitudes to zero
    z_fft[frequencies < 0.1] = 0

    # Perform inverse Fourier Transform to get the filtered signal back in time domain
    z_filtered = np.fft.ifft(z_fft)

    # Plot original and filtered data in the time domain
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.title("Original Signal")
    plt.plot(z)

    plt.subplot(2, 1, 2)
    plt.title("Filtered Signal")
    plt.plot(np.real(z_filtered))

    plt.tight_layout()
    plt.show()

    # Plot histogram in the frequency domain for the filtered data
    plt.figure()
    plt.bar(frequencies, np.abs(z_fft))
    plt.title("Fourier Transform - Frequency Domain (Filtered)")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Magnitude")
    plt.show()

    return np.real(z_filtered)

# Specify the path to your file
file_path = 'tracking.csv'

# Read only the 15th column (0-based indexing). If you mean the 15th column in 1-based indexing, use `usecols=[14]`.
data = pd.read_csv(file_path, sep='\t', usecols=[14])
# Extract the values of the column for easier processing
z = data.iloc[:, 0].values

sample_rate = 33.3

z = remove_baseline(z, sample_rate)

z -= z.min()

z_original = z.copy()

# Find the local maxima with a minimum distance of 20 between peaks
peaks, peak_info = find_peaks(z, distance=2 * sample_rate, prominence=0.5)

peaks_values = z[peaks]

filter_range = 0.5

# Adjust values based on the 80% rule
for i in range(len(z)):
    # Find the closest peak to the current point
    closest_peak = np.argmin(np.abs(peaks - i))
    closest_peak_value = peaks_values[closest_peak]

    threshold = closest_peak_value - filter_range * peak_info['prominences'][closest_peak]
    # If the current value is equal to or greater than 80% of the closest peak's value
    if z[i] >= threshold:
        z[i] = threshold

# Plot the modified column
plt.figure(figsize=(10, 6))
plt.plot(z_original, ".", label='Original z', markersize=4)
plt.plot(z, label='Filtered z')
plt.plot(peaks, z_original[peaks], "x", label='Peaks')
plt.title('Modified Column 15 with Local Peaks')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.show()



