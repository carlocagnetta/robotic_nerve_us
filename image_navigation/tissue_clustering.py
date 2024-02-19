from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, HDBSCAN
from scipy.ndimage import label
import numpy as np

class Tissues:

    def __init__(self, tissues_dict: dict):
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


    def find_clusters(self, tissue_value: int, slice: np.ndarray) -> list[dict]:
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
    

    def cluster_iter(self, slice: np.ndarray) -> dict:
        """ Find clusters of all tissues in a slice
        :param tissues: dictionary of tissues and their values
        :param slice: image slice to cluster
        :return: dictionary of tissues and their clusters
        """
        # store clsuters of tissues in a dict
        tissues_clusters = {}
        
        tissues = self.tissues_dict

        for tissue in tissues:
            print(f"Finding {tissue} clusters, with value {tissues[tissue]}:")
            tissues_clusters[tissue] = (self.find_clusters(tissues[tissue], slice))

            print(f"Found {len(tissues_clusters[tissue])} clusters\n")
        print("---------------------------------------\n")     
        return tissues_clusters

# TODO: move this functions into the class        
def find_DBSCAN_clusters(label: int, slice: np.array, eps: float, min_samples: int) -> None:
        
    # binary filter for the label
    binary_mask = (slice == label)

    # Check if there are tissues with given label
    if np.all(binary_mask == False):
        print("No tissues to cluster. Please set values using set_values method.")
        return []
    
    # find label positions, upon which clustering wil be defined
    label_positions = np.array(list(zip(*np.where(binary_mask))))

    # define clusterer
    clusterer = DBSCAN(eps=eps, min_samples=min_samples)

    # find cluster prediction
    labels = clusterer.fit_predict(label_positions)
    n_labels = len(np.unique(labels)) - 1 # noise cluster has label -1, we dont take it into account
    print(f"Found {n_labels} clusters")

    # Extract clusters and their centers
    cluster_data = []

    for label in range(n_labels):
        label_to_pos_array = label_positions[labels == label] # get positions of each cluster
        cluster_centers = np.mean(label_to_pos_array, axis=0) # mean of each column
        # Save both the cluster and center under the same key
        cluster_data.append({'cluster': label_to_pos_array,
                            'center': cluster_centers})

    return cluster_data

# TODO: set different parameters for each tissue
def DBSCAN_cluster_iter(tissues: dict, slice: np.ndarray, eps: float, min_samples: int) -> dict:
    # store clsuters of tissues in a dict
    tissues_clusters = {}

    for tissue in tissues:
        print(f"Finding {tissue} clusters, with value {tissues[tissue]}:")
        # find clusters for each tissue
        tissues_clusters[tissue] = (self.find_DBSCAN_clusters(tissues[tissue], slice, eps, min_samples))

        # print the identified clusters and their centers
        for index, data in enumerate(tissues_clusters[tissue]):
            print(f"Center of {tissue} cluster {index}: {data['center']}")
    print("---------------------------------------\n")     
    return tissues_clusters