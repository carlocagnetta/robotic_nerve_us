import numpy as np

def padding(original_array: np.ndarray) -> np.ndarray:
    """ Pad an array to make it square
    :param original_array: array to pad
    :return: padded array
    """
    
    # Find the maximum dimension
    max_dim = max(original_array.shape)

    # Calculate padding for each dimension (left and right)
    padding_x_left = (max_dim - original_array.shape[0]) // 2
    padding_x_right = max_dim - original_array.shape[0] - padding_x_left

    padding_y_left = (max_dim - original_array.shape[1]) // 2
    padding_y_right = max_dim - original_array.shape[1] - padding_y_left

    padding_z_left = (max_dim - original_array.shape[2]) // 2
    padding_z_right = max_dim - original_array.shape[2] - padding_z_left

    # Pad the array with zeros
    padded_array = np.pad(original_array, ((padding_x_left, padding_x_right), 
                                        (padding_y_left, padding_y_right), 
                                        (padding_z_left, padding_z_right)), 
                        mode='constant')

    # Verify the shapes
    print("Original Array Shape:", original_array.shape)
    print("Padded Array Shape:", padded_array.shape)

    return padded_array