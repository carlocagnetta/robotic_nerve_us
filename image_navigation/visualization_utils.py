
from matplotlib import pyplot as plt
import numpy as np


def _show(slices, start, lap, col=5, cmap=None, aspect=6):
    """ Function to display row of image slices
     :param slices: list of image slices
     :param start: starting slice number
     :param lap: number of slices to skip
     :param col: number of columns to display
     :param cmap: color map to use
     :param aspect: aspect ratio of each image
     :return: None
     """
    rows = -(-len(slices)//col)
    fig, axes = plt.subplots(rows, col, figsize=(15,2*rows))
    # Flatten the axes array to simplify indexing
    axes = axes.flatten()
    for i, slice in enumerate(slices):
        axes[i].imshow(slice.T, cmap=cmap, origin="lower", aspect=aspect)
        axes[i].set_title(f'Slice {start - i*lap}')  # Set titles if desired
    # Adjust layout to prevent overlap of titles
    plt.tight_layout()


def show_slices(data, start, end, lap, col=5, cmap=None, aspect=6):
    """ Function to display row of image slices
     :param data: 3D image data
     :param start: starting slice number
     :param end: ending slice number
     :param lap: number of slices to skip
     :param col: number of columns to display
     :param cmap: color map to use
     :param aspect: aspect ratio of each image
     :return: None
     """
    it = 0
    slices = []
    for slice in range(start, 0, -lap):
        it += 1
        slices.append(data[:, slice, :])
        if it==end: break
    _show(slices, start, lap, col, cmap, aspect)


def show_cluster_centers(tissue_clusters: dict, slice: np.ndarray) -> None:
    """ Plot the centers of the clusters of all tissues in a slice
     :param tissue_clusters: dictionary of tissues and their clusters
     :param slice: image slice to cluster
     :return: None
     """
    for tissue in tissue_clusters:
        for label, data in enumerate(tissue_clusters[tissue]):
            # plot clusters with different colors
            plt.scatter(*data['center'], color='red', marker='*', s=20) # plot centers

    plt.imshow(slice.T, aspect=6, origin='lower')


def show_clusters(tissue_clusters: dict, slice: np.ndarray) -> None:
    """ Plot the clusters of all tissues in a slice
     :param tissue_clusters: dictionary of tissues and their clusters
     :param slice: image slice to cluster
     :return: None
     """
    # create an empty array for cluster labels
    cluster_labels = slice.copy()

    for tissue in tissue_clusters:
        for label, data in enumerate(tissue_clusters[tissue]):
            # plot clusters with different colors
            cluster_labels[tuple(data['cluster'].T)] = (label + 1)*10
            plt.scatter(*data['center'], color='red', marker='*', s=20) # plot centers
    plt.imshow(cluster_labels.T, aspect=6, origin='lower')


def show_only_clusters(tissue_clusters: dict, slice: np.ndarray) -> None:
    """ Plot only the clusters of all tissues in a slice
     :param tissue_clusters: dictionary of tissues and their clusters
     :param slice: image slice to cluster
     :return: None
     """
    # create an empty array for cluster labels
    cluster_labels = np.ones_like(slice) * 0

    for tissue in tissue_clusters:
        for label, data in enumerate(tissue_clusters[tissue]):
            # plot clusters with different colors
            cluster_labels[tuple(data['cluster'].T)] = (label + 1)*10
            plt.scatter(*data['center'], color='red', marker='*', s=20) # plot centers

    plt.imshow(cluster_labels.T, aspect=6, origin='lower')