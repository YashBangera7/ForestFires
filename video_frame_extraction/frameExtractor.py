import os, re, shutil

os.chdir('/home/tiago/Desktop/Sintecsys/videos2/')

mp4 = list()
ffmpeg = 'ffmpeg -i "{}" -r 1/1 -qscale:v 1 "{}"/$filename%03d.jpg'

for root, dirs, files in os.walk('.'):
    for f in files:
        if re.match(r'.+\.dav$', f, re.DOTALL) is not None:
            fullpath = "{}/{}".format(root,f)
            
            # rename = re.sub(r'(^\./)', '', fullpath)
            # rename = re.sub(r'\s', '_', rename) 
            # rename = re.sub(r'/', '_', rename)         
            # os.system( 'mv "{}" "{}"'.format(fullpath, rename) )

            f2 = re.sub(r'\.dav$', '_jpeg', fullpath, 0, re.DOTALL)
            print(f2)
            os.mkdir(f2)
            os.system( ffmpeg.format(fullpath,f2) )

            
