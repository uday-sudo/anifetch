![example](example.png)
# anifetch - neofetch but animated.

This is a small tool built with neofetch, ffmpeg and chafa. It allows you to use neofetch while having animations.

## How to Install

You need `chafa` to be installed. For debian/ubuntu it is `apt install chafa`. [Download Instructions](https://hpjansson.org/chafa/download/)

if you don't have ffmpeg, download it here: [ffmpeg download](https://www.ffmpeg.org/download.html)

Clone the git repo.

```cmd
git clone https://github.com/Notenlish/anifetch
```

You don't need to setup an venv or install any python modules.

## How to Use It

Your neofetch logo file should only include a single character for the ascii art. Anifetch will attempt to find it and replace it with the chafa animation output. An example logo file can be found in `example-logo.txt`

An example neofetch config can be found here: `example-config.conf`

Simply place your video/gif file in the project folder. There's an already included test file called `video.mp4`, you can use that if you want.

Then run `python3 anifetch.py -f [filename] --framerate 10 --width 40 --height 20 -c "[add optional chafa arguments]"`.

Here's an example command: `python3 anifetch.py -f "video.mp4" -r 10 -W 40 -H 20 -c "--symbols wide --fg-only"`

Run `python3 anifetch.py --help` if you need help.

## Creating a Shortcut

Just create an shell alias.

for bash it is: `alias anifetch='your-command'`

## Benchmarks

Here's the benchmark from running each cli 10 times:

| CLI       | Time Taken(total) | Time Taken (avg) |
| --------- | ----------------- | ---------------- |
| anifetch  | 6.357 seconds     | 0.6357 seconds   |
| fastfetch | 0.127 seconds     | 0.127 seconds    |
| neofetch  | 5.869 seconds     | 0.5869 seconds   |

_So, anifetch is only 0.0488 seconds slower than neofetch._

Keep in mind that these results are from running it cached. If you're running it for the first time, or told the cli to re-render it, it will take some time to generate and cache all the frames.

## Notes

Anifetch attempts to cache ffmpeg output so that it doesn't need to render them again when you run it with the same file. However, if the name of the file is the same, but it's contents has changed or the animation size arguments has changed, it won't re-render it. In that case, you will need to add `--force-render` as an argument to `anifetch.py` so that it re-renders it. You have to do this once when you change the file or change the animation size argument.

You should probably make sure that the video's height (in lines) is lower or equal to the height of the neofetch output. Otherwise it will probably give an IndexError.

Also, ffmpeg can generate the the same image for 2 consecutive frames. IDK what would be the best way to solve this issue. I could check the hash of the images but that would add more processing load.

## What's Next

- [ ] Fix the potential IndexError that comes when chafa output in lines is higher than the neofetch output.

- [ ] Add music support

- [ ] Also cache chafa output

- [ ] make it faster

- [ ] Only save the template + animation frames, dont save the animation frames with the layout applied to them.

- [ ] Add fastfetch support.

- [ ] Instead of just caching the filename, cache the width and height as well

- [ ] Seperate frame generation framerate(ffmpeg) and video playback framerate

## Credits

Neofetch: [Neofetch](https://github.com/dylanaraps/neofetch)

I got the base neofetch config from here, spesifically the Bejkon 2 config file: [Neofetch Themes by Chick2D](https://github.com/Chick2D/neofetch-themes)
