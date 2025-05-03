# anifetch - neofetch but animated.

This is a small tool built with neofetch, ffmpeg and chafa. It allows you to use neofetch while having animations.

## How to Install

if you don't have ffmpeg, download it here: [ffmpeg download](https://www.ffmpeg.org/download.html))

Clone the git repo.

`git clone https://github.com/Notenlish/anifetch`

You don't need to setup an venv or install any python modules.

## How to Use It

Your neofetch logo file should only include a single character for the ascii art. Anifetch will attempt to find it and replace it with the chafa animation output. An example logo file can be found in `example-logo.txt`.

An example neofetch config can be found here: `example-config.conf`

Simply place your video/gif file in the project folder. There's an already included test file called `video.mp4`, you can use that if you want.

Then run `python3 anifetch.py -f [filename] --framerate 10 --width 40 --height 20`.

Here's an example command: `python3 anifetch.py -f "video.mp4" -W 40 -H 20 -r 10 -fr`

Run `python3 anifetch.py --help` if you need help.

## Notes

Anifetch attempts to cache ffmpeg output so that it doesn't need to render them again when you run it with the same file. However, if the name of the file is the same, but it's contents has changed, it won't re-render it. In that case, you will need to add `--force-render` as an argument to `anifetch.py` so that it re-renders it. You only have to do this once when you change the file.

## Credits

Neofetch: [Neofetch](https://github.com/dylanaraps/neofetch)

I got the base neofetch config from here, spesifically the Bejkon 2 config file: [Neofetch Themes by Chick2D](https://github.com/Chick2D/neofetch-themes)
