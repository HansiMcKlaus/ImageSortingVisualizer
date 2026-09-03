import argparse
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from io_utils import compile_video, load_image, save_frames
from partitions import create_index_list, reconstruct_image, shuffle_index_list
from sorting import (
    bubble_sort_steps,
    comb_sort_steps,
    heap_sort_steps,
    insertion_sort_steps,
    merge_sort_steps,
    pancake_sort_steps,
    quick_sort_steps,
    radix_sort_steps,
    selection_sort_steps,
    shaker_sort_steps,
)

# Names of sorting algorithms accepted on the command line
SORT_ALGORITHMS = [
    "bubble",
    "comb",
    "heap",
    "insertion",
    "merge",
    "pancake",
    "quick",
    "radix",
    "selection",
    "shaker",
]

SORT_ALGORITHM_FUNCS = {
    "bubble": bubble_sort_steps,
    "comb": comb_sort_steps,
    "heap": heap_sort_steps,
    "insertion": insertion_sort_steps,
    "merge": merge_sort_steps,
    "pancake": pancake_sort_steps,
    "quick": quick_sort_steps,
    "radix": radix_sort_steps,
    "selection": selection_sort_steps,
    "shaker": shaker_sort_steps,
}

FRAMES_DIR = Path("output")


@contextmanager
def timed(label):
    start = time.perf_counter()
    yield
    print(f"{label}: {time.perf_counter() - start:.2f}s")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Visualize sorting algorithms by sorting image pixel segments."
    )
    parser.add_argument(
        "-i", "--image",
        type=str,
        default="test.jpg",
        help="Path to the input image (Default: test.png)",
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        choices=SORT_ALGORITHMS,
        default="insertion",
        help="Sorting algorithm to visualize (Default: insertion)",
    )
    parser.add_argument(
        "-s", "--segment-size",
        type=int,
        default=10,
        help="Size in pixels of each segment/partition to sort (Default: 10)",
    )
    parser.add_argument(
        "-l", "--length",
        type=float,
        default=5.0,
        help="Length of the output video in seconds (Default: 5)",
    )
    parser.add_argument(
        "-f", "--fps",
        type=int,
        default=30,
        help="Framerate of the output video (Default: 30)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to the output video (Default: <algorithm>.mp4)",
    )
    args = parser.parse_args()
    if args.segment_size <= 0:
        parser.error("--segment-size must be a positive integer")
    return args


def sort_image_steps(image, algorithm, segment_size, target_frame_count):
    if algorithm not in SORT_ALGORITHM_FUNCS:
        raise NotImplementedError(f"Sorting algorithm '{algorithm}' is not implemented yet")

    shuffled = shuffle_index_list(create_index_list(image, segment_size))

    # Single-pass, evenly-spaced sampling of a stream whose length we don't know ahead of time.
    # The reservoir is oversampled beyond target_frame_count, resample_steps() then trims it down exactly
    buffer_capacity = target_frame_count * 2
    index_steps = [shuffled.copy()]
    interval = 1
    step_count = 0
    state = shuffled

    for state in SORT_ALGORITHM_FUNCS[algorithm](shuffled):
        step_count += 1
        if step_count % interval == 0:
            index_steps.append(state.copy())
            if len(index_steps) >= buffer_capacity:
                index_steps = index_steps[0::2]
                interval *= 2

    if index_steps[-1] != state:
        index_steps.append(state.copy())

    return resample_steps(index_steps, target_frame_count)


def resample_steps(steps, target_frame_count):
    indices = np.round(np.linspace(0, len(steps) - 1, target_frame_count)).astype(int)
    return [steps[i] for i in indices]


def render_frames(image, index_steps, segment_size):
    return [reconstruct_image(image, step, segment_size) for step in index_steps]


def main():
    args = parse_args()
    target_frame_count = max(1, round(args.length * args.fps))
    video_path = Path(args.output) if args.output else Path(f"{args.algorithm}.mp4")

    with timed("Loading image"):
        image = load_image(args.image)

    with timed("Sorting"):
        index_steps = sort_image_steps(image, args.algorithm, args.segment_size, target_frame_count)

    with timed("Rendering frames"):
        frames = render_frames(image, index_steps, args.segment_size)

    with timed("Saving frames"):
        save_frames(frames, FRAMES_DIR)

    with timed("Compiling video"):
        compile_video(FRAMES_DIR, args.fps, video_path)


if __name__ == "__main__":
    main()
