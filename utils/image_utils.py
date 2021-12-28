"""
Utilities for image work
"""

import cv2
from skimage.metrics import structural_similarity
import numpy as np


def video_iterator(input_path, input_file, frames_per_second):
    step = 0
    ms = 1000 * 1 / frames_per_second * step
    vidcap = cv2.VideoCapture(input_path + "/" + input_file)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, ms)
    success, frame = vidcap.read()
    while success:
        step += 1
        ms = 1000 * 1. / frames_per_second * step
        yield frame
        vidcap.set(cv2.CAP_PROP_POS_MSEC, ms)
        success, frame = vidcap.read()
    vidcap.release()


def rmse(image1, image2, downsample_size, greyscale):    
    img1 = image1
    img2 = image2
    if greyscale:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    if downsample_size is not None:
        img1 = cv2.resize(img1, downsample_size)
        img2 = cv2.resize(img2, downsample_size)
    
    return -np.sqrt(np.square(img1 - img2).mean())


def ssim_score(image1, image2, downsample_size, greyscale):
    img1 = image1
    img2 = image2
    
    if downsample_size is not None:
        img1 = cv2.resize(img1, downsample_size)
        img2 = cv2.resize(img2, downsample_size)
        
    if greyscale:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        return structural_similarity(img1, img2)
    else:
        return structural_similarity(img1, img2, multichannel=True)


def blur_score(image, downsample_size):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if downsample_size is not None:
        img = cv2.resize(img, downsample_size)
    
    return cv2.Laplacian(image, cv2.CV_64F).var()
