import sys
import os
import subprocess
import widget
import time

from PySide6 import QtWidgets


def main():
    if not (check_ffmpeg() and check_Real_ESRGAN_ncnn_Vulkan()):
        print("Missing required files, see requirement.txt and README.MD for more information.")
        print("This window will close after 5 seconds")
        print("5")
        time.sleep(1)
        print("4")
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        sys.exit()
    app = QtWidgets.QApplication(sys.argv)

    window = widget.Widget()
    window.show()

    app.exec()


def check_ffmpeg():
    sys_env = os.environ.get("PATH")
    usr_env = os.getenv("PATH")
    in_sys = [i for i in sys_env.split(";") if "ffmpeg" in i]
    in_usr = [i for i in usr_env.split(";") if "ffmpeg" in i]
    return len(in_sys) > 0 or len(in_usr) > 0


def check_Real_ESRGAN_ncnn_Vulkan():
    requirement = ["realesrgan-ncnn-vulkan.exe", "vcomp140.dll", "vcomp140d.dll"]
    return all([i in os.listdir() for i in requirement])


def check_models():
    try:
        models = os.listdir("models")
    except FileNotFoundError:
        return False
    bin_ = [i for i in models if i.startswith("realesr") and i.endswith(".bin")]
    parm = [i for i in models if i.startswith("realesr") and i.endswith(".param")]
    return (len(bin_) == len(parm) == 5)


def get_fps(video_fpath):
    cmd1 = "ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1"
    cmd2 = " -show_entries stream=r_frame_rate {}".format(video_fpath)
    process = subprocess.Popen(
        cmd1 + cmd2,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    fps = [i for i in process.stdout]
    return fps[0]


def get_frame_count(video_fpath):
    cmd1 = "ffprobe -v error -select_streams v:0 -count_packets -show_entries"
    cmd2 = " stream=nb_read_packets -of csv=p=0 {}".format(video_fpath)
    process = subprocess.Popen(
        cmd1 + cmd2,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    frame_count = [i for i in process.stdout]
    return frame_count[0]


if __name__ == "__main__":
    main()
