""" Move files to another folder based on the name of the files."""

# Run this script within the folder you want to move files

import os
import glob
import shutil

def get_dir_name(filename):
    pos1 = filename.rfind('_')
    pos2 = filename.find('.')
    return filename[pos1+1:pos2]

for f in glob.glob('*.jpeg'):
    cwd = os.getcwd()
    dir_name = cwd+'/'+get_dir_name(f)
    
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    
    shutil.move(f, dir_name+'/'+f)