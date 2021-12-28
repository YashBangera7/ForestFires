"""
Script created by Gary Diana to quickly download images and masks.
Special thanks to Serhiy Shekhovtsov for turning my original notebook into this python
file so that it works on both Linux and Windows!
"""

import os
import sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)

from pathlib import Path
import pandas as pd
import numpy as np
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from multiprocessing import Pool
from functools import partial
import datetime
import time
import argparse
import pyarrow


def parallelize(data, func, num_of_processes=4):
    data_split = np.array_split(data, num_of_processes)
    pool = Pool(num_of_processes)
    num_successful_images = np.sum(pool.map(func, data_split))
    pool.close()
    pool.join()
    return num_successful_images


def save_images(rows):
    success_images = 0
    for index, row in rows.iterrows():
        if(row["Labeled Data"] is not None and row["segmentationMaskURL_list"] is not None):
            img = Image.open(BytesIO(requests.get(row["Labeled Data"]).content))
            mask = Image.open(BytesIO(requests.get(row["segmentationMaskURL_list"][0]).content))
            
            mask_fire_smoke = Image.open(BytesIO(requests.get(row["segmentationMaskURL_list"][0]).content))
            mask_other_smoke = Image.open(BytesIO(requests.get(row["segmentationMaskURL_list"][1]).content))

            combined_mask = Image.fromarray(np.max([np.array(mask_fire_smoke).sum(axis=2).astype(np.uint8),
                                                    np.array(mask_other_smoke).sum(axis=2).astype(np.uint8)], axis=0))
            
            img.save(str(img_out_path / str(row["ID"] + ".png")))
            combined_mask.save(str(mask_out_path / str(row["ID"] + ".png")))
            success_images += 1
    return success_images


if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(allow_abbrev=False,
                                        description="Downloads masks and images from Labelbox using multiprocessing for high performance.")
    my_parser.add_argument('--json', action='store', type=str, required=True, default=1.0,
                           help="Labelbox JSON file to be used.")
    my_parser.add_argument('--out_dir', action='store', type=str, required=True, default=1.0,
                           help="Directory to be used to output patch folders (containing /images and /masks subfolders).")
    my_parser.add_argument('--workers', action='store', type=int, required=False, default=4,
                           help="Number of workers to use in parallel. This should generally be set to twice the core count.")
    args = my_parser.parse_args()
    
    # Change this to suit your environment
    output_dir = Path(str(args.out_dir))
    img_out_path = output_dir / "images/"
    mask_out_path = output_dir / "masks/"
    num_of_processes = int(args.workers)
    
    if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)
    if os.path.isdir(img_out_path) == False:
        os.mkdir(img_out_path)
    if os.path.isdir(mask_out_path) == False:
        os.mkdir(mask_out_path)

    print("Creating download queue from", str(args.json) + ".")
    
    label_df = pd.read_json(str(args.json))
    
    label_df["segmentationMaskURL_list"] = label_df["Label"]. \
        apply(lambda x: [x["segmentationMasksByName"]["FiresSmokes"], x["segmentationMasksByName"]["OtherSmokes"]]
              if x is not None and x != "" else None)
    
    skipped_ids = label_df[label_df["segmentationMaskURL_list"] == None]["ID"].tolist()
    if len(skipped_ids) > 0:
        print("Note: the following images will be skipped due to missing data in the JSON:\n\t", skipped_ids)
    else:
        print("Image and mask URLs located for all images.")

    print("Attempting to download", str(len(label_df)), "files using", num_of_processes, "workers...")

    t0 = time.time()
    num_successful_images = parallelize(label_df, save_images, num_of_processes)
    t1 = time.time()
    delta_t = t1 - t0
    elapsed_time = str(datetime.timedelta(seconds=round(delta_t)))
    images_per_second_str = "(" + str(round(float(num_successful_images) / delta_t)) + " images/second)"
    skipped_images = len(label_df) - num_successful_images

    print("Download complete!", str(num_successful_images), "images downloaded in", elapsed_time, images_per_second_str + ".")
    if skipped_images > 0:
        print("Note:",  skipped_images, "were skipped due to missing or bad URLs.")
