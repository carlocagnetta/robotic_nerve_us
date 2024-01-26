from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, HDBSCAN
from scipy.ndimage import label
import numpy as np

class Tissues:

    def __init__(self, tissues_dict):
        # Initialize an empty tissues dictionary
        self.tissues_dict = tissues_dict


    def set_values(self, tissue_name, values):
        # Set values for a specific tissue
        self.tissues_dict[tissue_name] = values

    def get_values(self, tissue_name):
        # Get values for a specific tissue
        return self.tissues_dict.get(tissue_name, None)
    
    def get_tissues(self):
        # Return the dictionary of the tissues
        return self.tissues_dict 


    def find_clusters(tissue_value: int, slice: np.ndarray) -> list[dict]:
        """ Find clusters of a given tissue in a slice
        :param tissue_value: value of the tissue to cluster
        :param slice: image slice to cluster
        :return: list of clusters and their centers
        """
        # Create a binary mask based on the threshold
        binary_mask = (slice == tissue_value)

        # Check if there are tissues with given label
        if np.all(binary_mask == False):
            print("No tissues to cluster. Please set values using set_values method.")
            return []

        # Label connected components in the binary mask
        labeled_array, num_clusters = label(binary_mask)

        # Extract clusters and their centers
        cluster_data = []
        
        for cluster_label in range(num_clusters):
            cluster_indices = np.where(labeled_array == cluster_label+1)
            # Calculate the center of the cluster
            center_x = np.mean(cluster_indices[0])
            center_y = np.mean(cluster_indices[1])
            center = (center_x, center_y)

            # Save both the cluster and center under the same key
            cluster_data.append({'cluster': np.array(list(zip(cluster_indices[0], cluster_indices[1]))),
                                'center': center})

        return cluster_data
    

    def cluster_iter(tissues: dict, slice: np.ndarray) -> dict:
        """ Find clusters of all tissues in a slice
        :param tissues: dictionary of tissues and their values
        :param slice: image slice to cluster
        :return: dictionary of tissues and their clusters
        """
        # store clsuters of tissues in a dict
        tissues_clusters = {}
        
        for tissue in tissues:
            print(f"Finding {tissue} clusters, with value {tissues[tissue]}:")
            tissues_clusters[tissue] = (find_clusters(tissues[tissue], slice))

            print(f"Found {len(tissues_clusters[tissue])} clusters\n")
        print("---------------------------------------\n")     
        return tissues_clusters
        