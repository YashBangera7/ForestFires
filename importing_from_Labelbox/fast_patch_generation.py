"""
Script created by Gary Diana to quickly generate image patches and masks (with any size and stride) using images downloaded
with importing_from_Labelbox/fast_download_Images_and_masks.py. Just specify your stride, patch size, and set the directories
for your environment! Tensorflow is used to perform the patch generation.
"""

import os
import sys

nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from multiprocessing import Pool
from functools import partial
from os.path import isdir
import tensorflow as tf
import random
import logging
import datetime
import time
import argparse


def count_smoky_pixels(mask_array):
    return mask_array.sum() // 255


def process_image_tuple(img_tuple, patch_size, stride, threshold, image_sample_rate=1):
    result_list = []
    img_stem = img_tuple[0]

    temp_mask = np.array(Image.open(img_tuple[2]))

    full_image_smoky_pixels = count_smoky_pixels(temp_mask)

    if (image_sample_rate != 1) and (random.random() > image_sample_rate):
        result_list = [(img_stem, full_image_smoky_pixels, np.nan, np.nan, np.nan)]

    else:
        temp_image = np.array(Image.open(img_tuple[1]))

        if (full_image_smoky_pixels >= threshold):
            image_patches = tf.image.extract_patches(np.array([temp_image]),
                                                     sizes=[1, PATCH_SIZE[0], PATCH_SIZE[1], 1],
                                                     strides=[1, STRIDE[0], STRIDE[1], 1],
                                                     rates=[1, 1, 1, 1],
                                                     padding='VALID')

            image_patches = np.array(tf.reshape(image_patches,
                                                [image_patches.shape[1] * image_patches.shape[2], PATCH_SIZE[0],
                                                 PATCH_SIZE[1], 3]))

            mask_patches = tf.image.extract_patches(np.expand_dims(np.expand_dims(temp_mask, axis=2), axis=0),
                                                    sizes=[1, PATCH_SIZE[0], PATCH_SIZE[1], 1],
                                                    strides=[1, STRIDE[0], STRIDE[1], 1],
                                                    rates=[1, 1, 1, 1],
                                                    padding='VALID')

            mask_patches = np.array(
                tf.reshape(mask_patches, [mask_patches.shape[1] * mask_patches.shape[2], PATCH_SIZE[0], PATCH_SIZE[1]]))

            for i in range(image_patches.shape[0]):
                image_patch = image_patches[i]
                mask_patch = mask_patches[i]
                smoky_pixels_patch_pct = float(count_smoky_pixels(mask_patch)) / float(len(mask_patch.flatten()))
                Image.fromarray(image_patch).save(str(patch_image_out_path) + "/" + img_stem + "_" + str(i) + ".png")
                Image.fromarray(mask_patch).save(str(patch_mask_out_path) + "/" + img_stem + "_" + str(i) + ".png")
                result_list += [(img_stem, full_image_smoky_pixels,
                                 str(patch_image_out_path) + "/" + img_stem + "_" + str(i) + ".png",
                                 str(patch_mask_out_path) + "/" + img_stem + "_" + str(i) + ".png",
                                 smoky_pixels_patch_pct)]

        else:
            result_list = [(img_stem, full_image_smoky_pixels, np.nan, np.nan, np.nan)]

    return pd.DataFrame(result_list, columns=["original_image_stem", "full_image_smoky_pixels", "patch_image",
                                              "patch_mask", "smoky_pixel_pct"])


if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(allow_abbrev=False,
                                        description="Creates patches using multiprocessing for high performance.")
    my_parser.add_argument('--in_dir', action='store', type=str, required=True, default=1.0,
                           help="Directory to be used to output patch folders (containing /images and /masks subfolders) and patch_df.parquet file.")
    my_parser.add_argument('--out_dir', action='store', type=str, required=True, default=1.0,
                           help="Directory to be used to output patch folders (containing /images and /masks subfolders) and patch_df.parquet file.")
    my_parser.add_argument('--workers', action='store', type=int, required=False, default=4,
                           help="Number of workers to use in parallel. This should generally be set to the twice the core count, assuming the system is not IO bound.")
    my_parser.add_argument('--s_height', action='store', type=int, required=False, default=128,
                           help="Stride height in pixels")
    my_parser.add_argument('--s_width', action='store', type=int, required=False, default=128,
                           help="Stride width in pixels")
    my_parser.add_argument('--p_height', action='store', type=int, required=False, default=128,
                           help="Height in pixels of patches to be generated")
    my_parser.add_argument('--p_width', action='store', type=int, required=False, default=128,
                           help="Height in pixels of patches to be generated")
    my_parser.add_argument('--smoke_threshold', action='store', type=int, required=False, default=0,
                           help="Minimum Number of smoke pixels in full size image to be considered for patch generation")
    my_parser.add_argument('--sample_rate', action='store', type=float, required=False, default=1.0,
                           help="Sampling rate used to select full size images for patch generation")
    args = my_parser.parse_args()

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    logging.getLogger('tensorflow').setLevel(logging.ERROR)

    PATCH_SIZE = (int(args.p_height), int(args.p_width))
    STRIDE = (int(args.s_height), int(args.s_width))
    SMOKE_THRESHOLD_WHOLE_IMAGE = int(args.smoke_threshold)
    IMAGE_SAMPLE_RATE = float(args.sample_rate)
    num_workers = int(args.workers)

    out_dir = Path(str(args.out_dir))
    in_dir = Path(str(args.in_dir))

    # Define paths for the original images and the new masks
    patch_image_out_base_path = out_dir / "images/"
    patch_mask_out_base_path = out_dir / "masks/"
    patch_image_out_path = patch_image_out_base_path / (str(PATCH_SIZE[0]) + "x" + str(PATCH_SIZE[1]) + "_" +
                                                        str(STRIDE[0]) + "x" + str(STRIDE[1]) +
                                                        "_threshold_" + str(SMOKE_THRESHOLD_WHOLE_IMAGE))

    patch_mask_out_path = patch_mask_out_base_path / (str(PATCH_SIZE[0]) + "x" + str(PATCH_SIZE[1]) + "_" +
                                                      str(STRIDE[0]) + "x" + str(STRIDE[1]) +
                                                      "_threshold_" + str(SMOKE_THRESHOLD_WHOLE_IMAGE))

    # Check for and make and directories that may not exist yet
    if not isdir(out_dir):
        os.mkdir(out_dir)
    if not isdir(patch_image_out_base_path):
        os.mkdir(patch_image_out_base_path)
    if not isdir(patch_mask_out_base_path):
        os.mkdir(patch_mask_out_base_path)
    if not isdir(patch_image_out_path):
        os.mkdir(patch_image_out_path)
    if not isdir(patch_mask_out_path):
        os.mkdir(patch_mask_out_path)

    print("\nLoading and validating original images and masks...")

    # Get names of all existing images in the images directory, and make lists of all image and mask files
    img_stems = set([name.split(".png")[0] for name in os.listdir(in_dir / "images")])
    image_file_list = [str(in_dir / "images") + "/" + str(stem) + ".png" for stem in img_stems]
    mask_file_list = [str(in_dir / "masks") + "/" + str(stem) + ".png" for stem in img_stems]

    # Create tuples containing the base name of the image, and paths for the image and mask
    image_mask_tuples = list(zip(img_stems, image_file_list, mask_file_list))

    print("Identified", str(len(image_mask_tuples)), "image/mask pairs, which will be sampled at a rate of",
          str(IMAGE_SAMPLE_RATE) + ".")

    print("Executing patch generation with", num_workers, "workers...")

    t0 = time.time()

    pool = Pool(num_workers)
    patch_result_df = pd.concat(pool.map(partial(process_image_tuple, patch_size=PATCH_SIZE,
                                                 stride=STRIDE, threshold=SMOKE_THRESHOLD_WHOLE_IMAGE,
                                                 image_sample_rate=IMAGE_SAMPLE_RATE),
                                         image_mask_tuples))

    patch_result_df.reset_index().drop(["index"], axis=1). \
        to_parquet(out_dir / ("patch_df" + str(PATCH_SIZE[0]) + "x" + str(PATCH_SIZE[1]) +
                              "_" + str(STRIDE[0]) + "x" + str(STRIDE[1]) +
                              "_threshold_" + str(SMOKE_THRESHOLD_WHOLE_IMAGE) + ".parquet"))

    t1 = time.time()
    delta_t = t1 - t0
    elapsed_time = str(datetime.timedelta(seconds=round(delta_t)))
    patches_per_second_str = "(" + str(round(float(len(patch_result_df)) / delta_t)) + " patches/second)"

    print("Patch generation complete.", str(len(patch_result_df)), "patches generated in",
          elapsed_time, patches_per_second_str + ".")
    print("Patches are located in", patch_image_out_path)
    print("Masks are located in", patch_mask_out_path, "\n")
