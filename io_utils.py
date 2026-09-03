import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image


def load_image(path):
    with Image.open(path) as img:
        image = np.array(img.convert("RGB"))

    # yuv420p (used when encoding the video) requires even width/height
    height, width = image.shape[:2]
    return image[: height - height % 2, : width - width % 2]


def save_image(image, path):
    Image.fromarray(image.astype(np.uint8), "RGB").save(path)


def save_frames(frames, directory):
    directory = Path(directory)
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)

    paths = [directory / f"{i:05d}.png" for i in range(len(frames))]
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        list(executor.map(save_image, frames, paths))

    return directory


def compile_video(frame_dir, fps, output_path):
    frame_pattern = str(Path(frame_dir) / "%05d.png")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-hide_banner", "-loglevel", "error",
            "-framerate", str(fps),
            "-i", frame_pattern,
            "-pix_fmt", "yuv420p",
            str(output_path),
        ],
        check=True,
    )
    return output_path
