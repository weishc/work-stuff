import os
import subprocess
import glob
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from ai2x_ui import Ui_Form


class Widget(QWidget, Ui_Form):
    def __init__(self):
        self.abort_signal = 0
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Video Ai Upscale")
        self.start_button.clicked.connect(self.test)
        self.abort_button.clicked.connect(self.test2)

    def test2(self):
        self.abort_signal = 1

    def test(self):
        cmd = r'ffmpeg -i "C:\Users\Weish\Videos\a.mp4" -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 "C:\Users\Weish\Videos\temp\frame%08d.jpg"'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            if 'frame=' not in line:
                continue
            if self.abort_signal == 1:
                process.terminate()
            frame = line.split(' fps')[0][7:]
            print (frame)

    def main(self):
        out_dir = self.output_lineEdit.text()
        pic_dir = self.video_to_pics()
        scaled_pics_dir = self.upscale(pic_dir)
        self.pics_to_video(scaled_pics_dir)

    def video_to_pics(self):
        input_fpath = self.input_lineEdit.text()
        temp_dirname = os.path.basename(self.input_lineEdit.text()) + 'Temp'
        temp_path = os.path.dirname(input_fpath)
        pic_dir = os.path.join(temp_path, temp_dirname)
        os.mkdir(pic_dir)
        temp_output_path = os.path.join(pic_dir, 'frame%08d.jpg')
        cmd = 'ffmpeg -i {} -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 {}'.format(
            input_fpath, temp_output_path)
        os.system(cmd)
        return pic_dir

    def upscale(self, pic_dir):
        model = self.model_comboBox.currentText()
        scale = self.scale_comboBox.currentText()[0]
        scaled_pics_dir = os.path.join(pic_dir, 'scaled')
        os.mkdir(scaled_pics_dir)
        exe = os.path.join(os.getcwd(), 'realesrgan-ncnn-vulkan')
        cmd = '{} -i {} -o {} -n {} -s {} -f jpg'.format(exe,
                                                         pic_dir, scaled_pics_dir, model, scale)
        os.system(cmd)
        return scaled_pics_dir

    def pics_to_video(self, scaled_pics_dir):
        input_fpath = self.input_lineEdit.text()
        fps = self.get_fps(input_fpath)
        output_dir = self.output_lineEdit.text()
        scaled_pics_path = oss.path.join(scaled_pics_dir, 'frame%08d.jpg')
        cmd = (
            'ffmpeg -f image2 -framerate {} -i {} -i {} '.format(
                fps, scaled_pics_path, input_fpath, output_dir) +
            '-map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -r 24 -pix_fmt yuv420p {}'.format(
                output_dir)
        )
        os.system(cmd)

    def get_fps(self, video_fpath):
        cmd1 = 'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1'
        cmd2 = ' -show_entries stream=r_frame_rate {}'.format(video_fpath)
        process = subprocess.Popen(cmd1 + cmd2, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, universal_newlines=True)
        fps = [i for i in process.stdout]               
        return fps[0]

    def get_frame_count(self, video_fpath):
        cmd1 = 'ffprobe -v error -select_streams v:0 -count_packets -show_entries'
        cmd2 = ' stream=nb_read_packets -of csv=p=0 {}'.format(video_fpath)
        process = subprocess.Popen(cmd1 + cmd2, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, universal_newlines=True)
        frame_count = [i for i in process.stdout]               
        return frame_count[0]