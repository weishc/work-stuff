import os
import subprocess
import shutil
import project

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtWidgets import QWidget, QMessageBox
from ai2x_ui import Ui_Form




class Worker(QObject):
    update_progress_sig = Signal(int, int)  # progress order, progress value

    def __init__(self):
        super().__init__()
        self._abort = False

    def abort(self):
        self._abort = True
        return

    def main(self, input_fpath, output_dir, model, scale, tta):
        self._abort = False
        pic_dir = self.video_to_pics(input_fpath)
        if not self._abort:
            scaled_pics_dir = self.upscale(pic_dir, model, scale, tta)
        done = False
        if not self._abort:
            done = self.pics_to_video(scaled_pics_dir, input_fpath, output_dir)
        if done or self._abort:
            shutil.rmtree(pic_dir)

    def video_to_pics(self, input_fpath):
        temp_dirname = os.path.basename(input_fpath) + "Temp"
        temp_path = os.path.dirname(input_fpath)
        pic_dir = os.path.join(temp_path, temp_dirname)
        os.mkdir(pic_dir)
        temp_output_path = os.path.join(pic_dir, "frame%08d.jpg")
        cmd = f"ffmpeg -i {input_fpath} -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 {temp_output_path}"
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in process.stdout:
            if self._abort:
                process.terminate()
            if "frame=" not in line:
                continue
            frame = int(line.split(" fps")[0][7:])
            self.update_progress_sig.emit(0, frame)
        return pic_dir

    def upscale(self, pic_dir, model, scale, tta):
        scaled_pics_dir = os.path.join(pic_dir, "scaled")
        os.mkdir(scaled_pics_dir)
        exe = os.path.join(os.getcwd(), "realesrgan-ncnn-vulkan")
        cmd = f"{exe} -i {pic_dir} -o {scaled_pics_dir} -n {model} -s {scale} -f jpg"
        print (cmd)
        if tta:
            cmd += " -x"
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in process.stdout:
            if self._abort:
                process.terminate()
            if line.startswith("0.00%"):
                self.update_progress_sig.emit(1, 1)
        return scaled_pics_dir

    def pics_to_video(self, scaled_pics_dir, input_fpath, output_dir):
        fps = project.get_fps(input_fpath)
        scaled_pics_path = os.path.join(scaled_pics_dir, "frame%08d.jpg")
        fname = os.path.basename(input_fpath).split(".")[0]
        output_fpath = os.path.join(output_dir, fname + ".mp4")
        cmd = (
            f"ffmpeg -f image2 -framerate {fps} -i {scaled_pics_path} -i {input_fpath} "
            f"-map 0:v:0 -map 1:a:0? -c:a copy -c:v libx264 -r {fps[:2]} -pix_fmt yuv420p {output_fpath}"
        )
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in process.stdout:
            if self._abort:
                process.terminate()
            if "frame=" not in line:
                continue
            frame = int(line.split(" fps")[0][7:])
            self.update_progress_sig.emit(2, frame)
        return True



class Widget(QWidget, Ui_Form):
    # input_fpath,output_dir,model,scale,tta
    send_data_sig = Signal(str, str, str, str, bool)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Video Ai Upscale")

        worker = Worker()
        thread = QThread()
        self.send_data_sig.connect(worker.main)
        worker.update_progress_sig.connect(self.update_progress)
        self.start_button.clicked.connect(self.send_data)
        self.abort_button.clicked.connect(lambda: worker.abort())
        self.abort_button.clicked.connect(self.reset_progress)
        worker.moveToThread(thread)
        thread.start()

        self._thread = thread
        self._worker = worker

    def send_data(self):
        input_fpath = self.input_lineEdit.text()
        if input_fpath == "":
            QMessageBox.warning(
                self, "Input File Is Empty", "Please select the input file."
            )
            return
        output_dir = self.output_lineEdit.text()
        if output_dir == "":
            QMessageBox.warning(
                self, "Output Path Is Empty", "Please specify the output path."
            )
            return
        frame_cnt = int(project.get_frame_count(input_fpath)) * 3
        self.progress_bar.setRange(0, frame_cnt)
        model = self.model_comboBox.currentText()
        scale = self.scale_comboBox.currentText()[0]
        tta = self.tta_checkBox.isChecked()
        self.send_data_sig.emit(input_fpath, output_dir, model, scale, tta)


    def update_progress(self, order, val):
        cur_val = self.progress_bar.value()
        if order == 0:
            self.progress_bar.setValue(val)
        if order == 1:
            self.progress_bar.setValue(cur_val + 1)
        if order == 2:
            self.progress_bar.setValue(cur_val + val)

    def reset_progress(self):
        self.progress_bar.setValue(0)
        QMessageBox.warning(self, "Abort", "Aborted!")
        return
