import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import *

override_audio_rate = 0
with_scale = False
targetsize = 10

def select_file():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    filename = filedialog.askopenfilename(initialdir=application_path, filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.gif *.gifv *.webm *.ogv *.opus *.mpeg *.3gp *.wmv")])
    videopath.delete(0, tk.END)
    videopath.insert(0, filename)

def run_script():
    targetsize = int(targetmb.get())
    input_video = Path(videopath.get())
    override_audio_rate = int(audio_rate.get())
    with_scale = scale.get()
    if with_scale:
        scale_width = int(vidwidth.get())
        scale_height = int(vidheight.get())
    progress_label.config(text="Calculating...")
    if not input_video.is_file():
        tk.messagebox.showerror("Video Missing", f"file {input_video} does not exist")
        return
    if input_video.stat().st_size < (targetsize - 1) * 10 ** 6:
        tk.messagebox.showerror("Small file", f"file {input_video} is small enough")
        return
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    cur_path = Path(input_video.parent)
    name = input_video.stem
    output_name = cur_path / Path(f"{name}_small.mp4")
    ffmpeg_path = dir_path / Path("./ffmpeg/bin/ffmpeg.exe")
    ffprobe_path = dir_path / Path("./ffmpeg/bin/ffprobe.exe")
    duration_probe = f"{PureWindowsPath(ffprobe_path)} -v error -show_entries format=duration -of csv=p=0 \"{input_video}\""
    duration = int(subprocess.check_output(duration_probe, shell=True).decode().strip().split('.')[0])
    original_audio_rate_probe = f"{PureWindowsPath(ffprobe_path)} -v error -select_streams a:0 -show_entries stream=bit_rate -of csv=p=0 \"{input_video}\""
    original_audio_rate_temp = subprocess.check_output(original_audio_rate_probe, shell=True)
    if original_audio_rate_temp.decode() != '':
        if original_audio_rate_temp.decode().strip() == "N/A":
            original_audio_rate = 128
        else:
            original_audio_rate = int(int(original_audio_rate_temp.decode().strip())/1024)
        if override_audio_rate != 0:
            original_audio_rate = override_audio_rate
        target_minsize = (original_audio_rate * duration) / 8192
        is_minsize = target_minsize < targetsize
        if not is_minsize:
            tk.messagebox.showerror("File too small", f"file {input_video} is too small (usually cause audio takes too much room)")
            print(f"Target size {(targetsize - 1)}MB is too small!")
            print(f"Try values larger than {round(target_minsize, 2)}MB")
            return
        vbitrate = int((targetsize * 8192) / (1.048576 * duration)) - original_audio_rate
    else:
        vbitrate = int((targetsize * 8192) / (1.048576 * duration))
        original_audio_rate = 0
    if with_scale:
        first_pass = f"{PureWindowsPath(ffmpeg_path)} -y -i \"{input_video}\" -c:v libx264 -vf \"scale={scale_width}:{scale_height}\" -b:v {vbitrate}k -pass 1 -passlogfile temp.temp -an -f mp4 NUL"
        second_pass = f"{PureWindowsPath(ffmpeg_path)} -y -i \"{input_video}\" -c:v libx264 -vf \"scale={scale_width}:{scale_height}\" -b:v {vbitrate}k -pass 2 -passlogfile temp.temp -c:a aac -b:a {original_audio_rate}k \"{output_name}\""
    else:
        first_pass = f"{PureWindowsPath(ffmpeg_path)} -y -i \"{input_video}\" -c:v libx264 -b:v {vbitrate}k -pass 1 -passlogfile temp.temp -an -f mp4 NUL"
        second_pass = f"{PureWindowsPath(ffmpeg_path)} -y -i \"{input_video}\" -c:v libx264 -b:v {vbitrate}k -pass 2 -passlogfile temp.temp -c:a aac -b:a {original_audio_rate}k \"{output_name}\""
    print(f"converting {input_video.name}: duration = {duration}, vbitrate = {vbitrate}")
    print(f"with_scale={with_scale}, override_audio_rate={override_audio_rate}, original_audio_rate={original_audio_rate}, target_minsize={target_minsize}, is_minsize={is_minsize}")
    subprocess.call(first_pass, shell=True)
    subprocess.call(second_pass, shell=True)
    Path("temp.temp-0.log").unlink()
    Path("temp.temp-0.log.mbtree").unlink()
    output_path = Path(output_name)
    print(PureWindowsPath(output_path.parent))
    progress_label.config(text="Done!")
    
def scale_toggle():
    state = "normal" if scale.get() else "disabled"
    vidwidth.config(state=state)
    vidheight.config(state=state)

root = tk.Tk()
root.title("Discord Video Resizer")

ttk.Label(root, text="Target size in MB (whole integer)").grid(row=0, column=0, padx=5, pady=5)
targetmb = ttk.Entry(root)
targetmb.grid(row=0, column=1, padx=5, pady=5)
targetmb.insert(0, "10")

ttk.Label(root, text="Input Video Path").grid(row=1, column=0, padx=5, pady=5)
videopath = ttk.Entry(root, width=50)
videopath.grid(row=1, column=1, padx=5, pady=5)
ttk.Button(root, text="Browse", command=select_file).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(root, text="Force Audio Rate (0 = don't force, 32 64 128 good options)").grid(row=2, column=0, padx=5, pady=5)
audio_rate = ttk.Entry(root)
audio_rate.grid(row=2, column=1, padx=5, pady=5)
audio_rate.insert(0, "0")

scale = tk.BooleanVar()
scale_check = tk.Checkbutton(root, text="Enable specifying video scale", variable=scale, command=scale_toggle)
scale_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

ttk.Label(root, text="Video Width").grid(row=4, column=0, padx=5, pady=5)
vidwidth = ttk.Entry(root, state="disabled")
vidwidth.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(root, text="Video Height").grid(row=5, column=0, padx=5, pady=5)
vidheight = ttk.Entry(root, state="disabled")
vidheight.grid(row=5, column=1, padx=5, pady=5)

run_button = ttk.Button(root, text="Run", command=run_script)
run_button.grid(row=6, column=0, columnspan=2, pady=10)

progress_label = ttk.Label(root, text="")
progress_label.grid(row=7, column=0, columnspan=2, pady=5)

root.mainloop()


