import random

import numpy as np


def _grid_shape(image, segment_size):
    height, width = image.shape[:2]
    cols = width // segment_size
    rows = height // segment_size
    return cols, rows


def create_index_list(image, segment_size):
    cols, rows = _grid_shape(image, segment_size)
    if cols == 0 or rows == 0:
        height, width = image.shape[:2]
        raise ValueError(
            f"segment_size ({segment_size}) is larger than the image ({width}x{height})"
        )
    return list(range(cols * rows))


def shuffle_index_list(index_list):
    shuffled = index_list.copy()
    random.shuffle(shuffled)
    return shuffled


def reconstruct_image(image, index_list, segment_size):
    cols, rows = _grid_shape(image, segment_size)
    output = np.zeros_like(image)

    for position, source_index in enumerate(index_list):
        destination_y, destination_x = position // cols, position % cols
        source_y, source_x = source_index // cols, source_index % cols

        destination_cell = output[
            destination_y * segment_size:(destination_y + 1) * segment_size,
            destination_x * segment_size:(destination_x + 1) * segment_size,
        ]
        source_cell = image[
            source_y * segment_size:(source_y + 1) * segment_size,
            source_x * segment_size:(source_x + 1) * segment_size,
        ]
        destination_cell[:] = source_cell

    return output
