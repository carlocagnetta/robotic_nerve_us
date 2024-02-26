import numpy as np


class IncompatibleShapeError(Exception):
    pass


def crop_center(img: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    if img.shape == tuple(shape):
        return img
    img_bbox = _validate_and_get_full_image_bbox(img, shape)
    crop_y_pos, crop_x_pos, crop_y_size, crop_x_size = centered_constrained_bbox(
        limiting_bbox=img_bbox, new_bbox_shape=shape
    )
    return img[crop_y_pos : crop_y_pos + crop_y_size, crop_x_pos : crop_x_pos + crop_x_size]


def _validate_and_get_full_image_bbox(
    img: np.ndarray, shape: tuple[int, int]
) -> tuple[int, int, int, int]:
    """
    Helper function for validating input and returning a bounding box containing the full image, i.e.
    (0, 0, img_w, img_h). Useful for processing images with `centered_constrained_bbox`.
    """
    if np.any(np.array(shape) < 0):
        raise ValueError(f"shape cannot contain negative entries.")
    y_size, x_size = img.shape
    new_y_size, new_x_size = shape
    if y_size < new_y_size or x_size < new_x_size:
        raise IncompatibleShapeError(
            f"Center crop shape, {shape}, larger than provided image of shape, {img.shape}"
        )
    return (0, 0) + img.shape


def centered_constrained_bbox(
    limiting_bbox: tuple[int, int, int, int], new_bbox_shape: tuple[int, int]
) -> tuple[int, int, int, int]:
    """
    Returns a bounding box centered on and contained within the limiting bounding box with the specified shape.
    A bounding box is a tuple of type (y_pos, x_pos, y_size, x_size) where (y_pos, x_pos) point to the
    upper left corner.

    Can be interpreted as "center cropping" the input bounding box to the specified shape.

    :param limiting_bbox: Bounding box that new bbox is contained within and centered on
    :param new_bbox_shape: Shape of centered bounding box
    :return: Centered bounding box
    """

    y_pos, x_pos, y_size, x_size = limiting_bbox
    new_y_size, new_x_size = new_bbox_shape

    if np.any(np.array([y_size, x_size, new_y_size, new_x_size]) < 0):
        raise ValueError(
            f"Limiting bounding box shape and new bounding box shape cannot contain negative entries."
        )

    if y_size < new_y_size or x_size < new_x_size:
        raise IncompatibleShapeError(
            f"Requested shape of centered bounding box, {new_bbox_shape}, has to be smaller than provided limiting "
            f"bounding box shape, {limiting_bbox[2:]}"
        )

    # + 1 ensures that this uses the same convention for asymmetric cropping as generally used for convolutions
    # that is if we want to center crop [0, 1, 2, 3, 4] down to length 2 we crop it to [2, 3], i.e. the discarded
    # interval is chosen to be larger on the "left"
    new_y_pos = y_pos + (y_size - new_y_size + 1) // 2
    new_x_pos = x_pos + (x_size - new_x_size + 1) // 2

    return new_y_pos, new_x_pos, new_y_size, new_x_size
