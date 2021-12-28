# Run this script within the folder you want to process files #

import os
import shutil
import pandas as pd
import matplotlib.image as mpimg
import time

# Specify the minimum intensity for daytime images
MIN_IMG_INTENSITY = 106.4


def get_img_intensity(img_path_file):
    return mpimg.imread(img_path_file).mean()


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def copy_file_into_new_directory(img_path_file, img_dst_file):
    if not os.path.isfile(img_dst_file):
        shutil.copy(img_path_file, img_dst_file)
    else:
        print('File ' + os.path.basename(img_dst_file) + ' already exists in destination folder')


def get_clean_dataframe(df, dir):
    imgs, deteccaos, torres, caras, times_of_day = [], [], [], [], []

    for _, row in df.iterrows():
        img_file, deteccao = row[0], row[1]
        img_file = img_file.replace(':', '-') + '_' + deteccao + '.jpeg'
        img_path_file = dir + '/' + img_file

        if os.path.isfile(img_path_file):

            if get_img_intensity(img_path_file) >= MIN_IMG_INTENSITY:
                copy_file_into_new_directory(img_path_file, DAY_DIR + '/' + img_file)
                times_of_day.append('day')
            else:
                copy_file_into_new_directory(img_path_file, NIGHT_DIR + '/' + img_file)
                times_of_day.append('night')

            torre, cara = row[2][:2], row[2][5:]
            deteccao = 1 if deteccao == 'SIM' else 0
            imgs.append(img_file)
            deteccaos.append(deteccao)
            torres.append(torre)
            caras.append(cara)

    return pd.DataFrame({'img': imgs, 'deteccao': deteccaos, 'torre': torres, 'cara': caras, 'time_of_day': times_of_day})


def main():
    # Read files from csv
    IP_df = pd.read_csv(IP_DIR + '.csv')
    TTG_TUR_df = pd.read_csv(TTG_TUR_DIR + '.csv')

    # Remove non-existent image of day 2018-03-16 06:01:47 from T4
    TTG_TUR_df.drop(4038, inplace=True)

    # Create day and night directories for each dataset
    create_directory(NIGHT_DIR)
    create_directory(DAY_DIR)

    # Get clean dataframes and copy images into day and night directories for each dataset
    IP_df = get_clean_dataframe(IP_df, IP_DIR)
    TTG_TUR_df = get_clean_dataframe(TTG_TUR_df, TTG_TUR_DIR)

    # Merge dataframes
    df = pd.concat([IP_df, TTG_TUR_df]).sort_values(by='img').drop_duplicates().reset_index(drop=True)

    # Export csv file
    df.to_csv('IP_TTG_TUR.csv', index=False)


if __name__ == '__main__':
    start_time = time.time()

    # Dataset directory names
    current_dir = os.getcwd()
    IP_DIR = current_dir + '/IP'
    TTG_TUR_DIR = current_dir + '/TTG_TUR'
    NIGHT_DIR = current_dir + '/IP_TTG_TUR/night'
    DAY_DIR = current_dir + '/IP_TTG_TUR/day'

    if not os.path.isdir(IP_DIR) or \
            not os.path.isdir(TTG_TUR_DIR) or \
            not os.path.isfile(IP_DIR + '.csv') or \
            not os.path.isfile(TTG_TUR_DIR + '.csv'):
        print('Not all dataset files found within this folder')
    else:
        main()
        print(time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
