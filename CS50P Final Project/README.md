#### Video Demo:  https://youtu.be/guO7QSQRYvE
#### Description:
### What will your software do? What features will it have? 
For my CS50P final project, I decided to make a GUI for a command line tool called
 "**Real-ESRGAN ncnn Vulkan**".
Credit:https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan

This tool can only upscale the image with AI. But I will make it also able to upscale the video. To archive that, I have to convert the video to image sequence first via **FFmpeg**.
I use **Qt Designer** and **PySide6** to create the graphical user interface.
### How will it be executed?
The program first checks if the requirements are met:
1. FFmpeg installed and placed in PATH
2. Place the program in the same folder as Real-ESRGAN.
3. Do we have all the ai models we need in the "models" folder?

If not, the program quits and displays the error messages.

Then check that the input file and output folder are set correctly.
If not, the program displays the warning messages.

Then check if the input file and the output folder are set correctly, then convert the input video file to the image sequence using ffmpeg and upscale it with Real-ESRGAN ncnn Vulkan executable files.
To capture the process for the process bar and be able to abort at any time, I used subprocess.Popen to read the terminal output line by line.

Last step, convert the upscaled image sequence back to video with the original frame range and frame rate. To get the original frame range and frame rate, I used ffprobe, which is part of FFmpge. It allows me to get what I need from the input video file.
### What new skills will you need to acquire? What topics will you need to research?
I learned how to executing command in Python for operating the FFmpeg and Real-ESRGAN and create GUI with Qt Designer and PySide6 for my program.

