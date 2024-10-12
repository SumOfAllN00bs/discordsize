# Main executable
Located in /dist/ is the program discordsize_exe.exe that will re-encode a video to about 10 mbs to fit in discord.
Change audio rate and video width and height to affect the quality output if needed

# Individual python script
Re-encode a video to the target size in MB.
arguments that are optional are still positional, so you'll need to specify audiorate
in order to specify the width,height
optional = [], Format: python discordsize.py VIDEO [audiorate in kb] [width,height]
```bash
python discordsize.py meme_video_lol_among_us.mp4 128 1920,1080
```

# Build the executable
```bash
pip install pyinstaller
pyinstaller --add-data=ffmpeg:ffmpeg --onefile .\discordsize_exe.py
```
