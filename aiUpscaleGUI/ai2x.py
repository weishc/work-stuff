import os
import subprocess
import glob
import shutil


tempDir = r'D:\BT\edited\temp'
outDir = r'D:\BT\edited\out'

path = r'D:\BT\edited\*.mp4'
dirPath = os.path.dirname(path)

for i in glob.glob(path):
    srcVid = i
    tempPath = os.path.join(tempDir, 'frame%08d.jpg')
    outPath = os.path.join(outDir, 'frame%08d.jpg')
    fname = os.path.basename(i).split('.')[0]
    mergePath = os.path.join(dirPath, '2x', fname+'.mp4')

    cmd = r'ffmpeg -i {} -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 {}'.format(
        srcVid, tempPath)
    os.system(cmd)

    cmd2 = r'C:\Users\Weish\Downloads\realesrgan\ai2x -i {} -o {} -n realesr-animevideov3 -s 2 -f jpg'.format(
        tempDir, outDir)
    os.system(cmd2)

    cmd3 = r'ffmpeg -f image2 -framerate 24/1 -i {} -i {} -map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -r 24 -pix_fmt yuv420p {}'.format(
        outPath, i, mergePath)
    os.system(cmd3)

import io


cmd = r"ffmpeg -i C:\Users\Weish\Desktop\report_video\a.mp4 -f null -"
process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, universal_newlines=True)
for line in process.stdout:
        if line.startswith('  Stream #0:0(und): Video:'):
            file_info = line.split(',')
            res = file_info[4].split(' ')[1]
            fps = file_info[-2].split(' ')[1]
            print ('resolution: ' + res)
            print ('fps: ' + fps)