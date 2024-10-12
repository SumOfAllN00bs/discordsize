# Re-encode a video to the target size in MB.
# arguments that are optional are still positional, so you'll need to specify audiorate
# in order to specify the width,height
# optional = [], Format: python discordsize.py VIDEO [audiorate in kb] [width,height]
# python discordsize.py meme_video_lol_among_us.mp4 128 1920,1080

import os
import subprocess
import sys
from pathlib import *

override_audio_rate = 0
with_scale = False

if len(sys.argv) < 2:
    print("Please supply arguments in the following format:")
    print("optional = [], Format: python discordsize.py VIDEO [audiorate in kb] [width,height]")
if len(sys.argv) > 1:
    input_video = Path(sys.argv[1])
if len(sys.argv) > 2:
    override_audio_rate = int(sys.argv[2])
if len(sys.argv) > 3:
    scale_width = int(sys.argv[3].split(',')[0])
    scale_height = int(sys.argv[3].split(',')[1])
    with_scale = True

if not input_video.is_file():
    print(f"file {input_video} does not exist")
    sys.exit()

if input_video.stat().st_size < 7 * 10 ** 6:
    print(f"file {input_video} is small enough")
    sys.exit()

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
    is_minsize = target_minsize < 8

    if not is_minsize:
        print(f"Target size {8}MB is too small!")
        print(f"Try values larger than {round(target_minsize, 2)}MB")
        sys.exit()

    vbitrate = int((8 * 8192) / (1.048576 * duration)) - original_audio_rate
else:
    vbitrate = int((8 * 8192) / (1.048576 * duration))
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
