
from matplotlib import pyplot as plt


def show(slices, start, col=5, cmap=None, aspect=6):
   rows = -(-len(slices)//col)
   fig, axes = plt.subplots(rows, col, figsize=(15,2*rows))
   # Flatten the axes array to simplify indexing
   axes = axes.flatten()
   for i, slice in enumerate(slices):
       axes[i].imshow(slice.T, cmap=cmap, origin="lower", aspect=aspect)
       axes[i].set_title(f'Slice {start - i*5}')  # Set titles if desired
   # Adjust layout to prevent overlap of titles
   plt.tight_layout()

def show_slices(data, start, end, lap, col=5, cmap=None, aspect=6):
   """ Function to display row of image slices """
   it = 0
   slices = []
   for slice in range(start, 0, -lap):
       it += 1
       slices.append(data[:, slice, :])
       if it==end: break
   show(slices, start, col, cmap, aspect)
    