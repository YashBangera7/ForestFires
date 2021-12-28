""" Remove night images (after 18:00 and before 05:00) """

# Run this script within the folder you want to delete images

import os
import glob

for filename in glob.glob('*.jpeg'):
    if (int(filename.split(' ')[-1].split('-')[0]) >=18) or (int(filename.split(' ')[-1].split('-')[0]) <=5):  
        cwd = os.getcwd()
        fullpath = os.path.join(cwd, filename)
        os.remove(fullpath)