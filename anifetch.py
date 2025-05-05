import subprocess
import os
import pathlib
import argparse
import shutil
import time
import json

def print_verbose(*msg):
    if args.verbose:
        print(*msg)

# TODO: cache arguments + filename
# also, add support for fastfetch
# when caching, tell the user that its caching so they know why its slow
# also allow the user to provide their own frames if they want as well.

st = time.time()

GAP = 2
PAD_LEFT = 4

parser = argparse.ArgumentParser(
    prog="Anifetch",
    description="Allows you to use neofetch with video in terminal(using chafa).",
)
parser.add_argument("-b","--benchmark", default=False, help="For testing. Runs Anifetch without actually starting the animation.", action="store_true")
parser.add_argument(
    "-f",
    "--filename",
    required=True,
    help="Specify a file via this argument.",
    type=str
)
parser.add_argument("-w","-W", "--width", default=40, help="Width of the chafa animation.", type=int)
parser.add_argument("-H", "--height", default=20, help="Height of the chafa animation.", type=int)
parser.add_argument("-v", "--verbose", default=False, action="store_true")
parser.add_argument(
    "-r", "--framerate", default=10, help="Sets the framerate when extracting frames from ffmpeg.", type=int
)
parser.add_argument("-pr","--playback-rate", default=10, help="Sets the playback rate of the animation. Not to be confused with the 'framerate' option. This basically sets for how long the script will wait before rendering new frame, while the framerate option affects how many frames are generated via ffmpeg.")
parser.add_argument("-s","--sound", help="Optional. Will playback a sound file while displaying the animation.", type=str)
parser.add_argument(
    "-fr",
    "--force-render",
    default=False,
    action="store_true",
    help="Disabled by default. Anifetch saves the filename to check if the file has changed, if the name is same, it won't render it again. If enabled, the video will be forcefully rendered, whether it has the same name or not. Please note that it only checks for filename, if you changed the framerate then you'll need to force render.",
)
parser.add_argument("-c","--chafa-arguments",default="--symbols ascii --fg-only", help="Specify the arguments to give to chafa. For more informations, use 'chafa --help'")
parser.add_argument("-ff", "--fast-fetch", default=False, help="Add this argument if you want to use fastfetch instead. Note than fastfetch will be run with '--logo none'.", action="store_true")

args = parser.parse_args()



if not pathlib.Path("/tmp").exists():
    os.mkdir("/tmp")
if not pathlib.Path("/tmp/anifetch/").exists():
    os.mkdir("/tmp/anifetch")
if not pathlib.Path("/tmp/anifetch/video").exists():
    os.mkdir("/tmp/anifetch/video")
if not pathlib.Path("/tmp/anifetch/output").exists():
    os.mkdir("/tmp/anifetch/output")

if not pathlib.Path(args.filename).exists():
    print("Couldn't find file", pathlib.Path(args.filename))
    raise FileNotFoundError(args.filename)


# print(args._get_kwargs())
# [ ('filename', 'example.mp4'), ('width', 40), ('height', 20), ('verbose', False), ('framerate', 10), ('sound', 'bad-apple.mp3'), ('force_render', False), ('chafa_arguments', '--symbols ascii --fg-only') ]
args_dict = {key:value for key, value in args._get_kwargs()}

# check cache
old_filename = ""
should_update = False
try:
    if args.force_render:
        should_update = True
    else:
        with open("/tmp/anifetch/cache.json", "r") as f:
            data = json.load(f)
        for key, value in args_dict.items():
            try:
                cached_value = data[key]
            except KeyError:
                should_update = True
                break
            print_verbose(f"comparing cached and given value. cached: {cached_value} given: {value}")
            if value != cached_value:  # check if all options match
                print_verbose("Value didnt match cached value", "val:",value,"cache:", cached_value)
                print_verbose(f"key:{key}")
                if key not in ("playback_rate","verbose", "fast_fetch","benchmark"):  # These arguments don't invalidate the cache.
                    should_update = True
                    print_verbose("IT SHOULD BE FRIGGEN UPDATED")
except FileNotFoundError:
    should_update = True

print_verbose(f"Will use cache:{not should_update}",)

with open("/tmp/anifetch/cache.json", "w") as f:
    json.dump(args_dict, f)



WIDTH = args.width
HEIGHT = args.height


# put cached frames here
frames: list[str] = []

# cache is invalid, re-render
if should_update:
    print_verbose("SHOULD RENDER WITH CHAFA")

    # delete all old frames
    shutil.rmtree("/tmp/anifetch/video")
    os.mkdir("/tmp/anifetch/video")

    stdout = None if args.verbose else subprocess.DEVNULL
    stderr = None if args.verbose else subprocess.STDOUT

    subprocess.call(
        [
            "ffmpeg",
            "-i",
            f"{args.filename}",
            '-vf',
            f"fps={args.framerate}",
            "/tmp/anifetch/video/%05d.png",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    # If the new anim frames is shorter than the old one, then in /output there will be both new and old frames. Empty the directory to fix this.
    shutil.rmtree("/tmp/anifetch/output")
    os.mkdir("/tmp/anifetch/output")

    print_verbose("Emptied the output folder.")

    # get the frames
    animation_files = os.listdir(pathlib.Path("/tmp/anifetch/video"))
    animation_files.sort()
    for i, f in enumerate(animation_files):
        print_verbose(f"- Frame: {f}")

        # f = 00001.png
        path = pathlib.Path("/tmp/anifetch/video") / f
        chafa_cmd = [
            "chafa",
            *args.chafa_arguments.split(" "),
            # "--color-space=rgb",
            f"--size={WIDTH}x{HEIGHT}",
            path.as_posix(),
        ]
        # print("CHAFA", " ".join(chafa_cmd))
        frame = subprocess.check_output(
            chafa_cmd,
            text=True,
        )

        with open((pathlib.Path("/tmp/anifetch/output") / f).with_suffix(".txt"), "w") as file:
            file.write(frame)

        # if wanted aspect ratio doesnt match source, chafa makes width as high as it can, and adjusts height accordingly.
        # AKA: even if I specify 40x20, chafa might give me 40x11 or something like that.
        if i == 0:
            HEIGHT = len(frame.splitlines())
        frames.append(frame)
else:
    # just use cached
    for filename in os.listdir("/tmp/anifetch/output"):
        path = pathlib.Path("/tmp/anifetch/output") / filename
        with open(path, "r") as file:
            frame = file.read()
            frames.append(frame)
    HEIGHT = len(frames[0].splitlines())

print_verbose("-----------")


# Get the fetch output(neofetch/fastfetch)
if not args.fast_fetch:
    # Get Neofetch Output
    fetch_output = subprocess.check_output(["neofetch"], shell=True, text=True).splitlines()
    for i, line in enumerate(fetch_output):
        line = line[4:]  # i forgot what this does, but its important iirc.
        fetch_output[i] = line

    fetch_output.pop(0)
    fetch_output.pop(0)
    fetch_output.pop(0)
    fetch_output.pop(-1)
else:
    fetch_output = subprocess.check_output(["fastfetch","--logo","none","--pipe", "false"], text=True).splitlines()


# modifying template to account for the width of the chafa animation.
chafa_rows = frames[0].splitlines()
template = []
for y, fetch_line in enumerate(fetch_output):
    output = ""
    try:
        chafa_line = chafa_rows[y]
    except IndexError:
        chafa_line = ""

    width_to_offset = GAP + WIDTH

    # I have no idea why this is the way it is.
    output = f"{(PAD_LEFT+ (GAP*2) ) * " "}{' ' * width_to_offset}{fetch_line}\n"
    template.append(output)

# writing the tempate to a file.
with open("/tmp/anifetch/template.txt", "w") as f:
    f.writelines(template)
    # I just need to move this down, and also apply that padding thingy(for lines that dont have chafa anim)
    # so basically repeat what I have done but this time its for layout.
    # If I do this then I can get rid of the layout padding code on the last part. because the layout will already be fixed.
print_verbose("Template updated")

# for defining the positions of the cursor, that way I can set cursor pos and only redraw a portion of the text, not the entire text.
TOP = 2
LEFT = PAD_LEFT
RIGHT = WIDTH + PAD_LEFT
BOTTOM = HEIGHT# + TOP

script_dir = os.path.dirname(__file__)
script_path = os.path.join(script_dir, "loop-cursor.sh")

# print(args.framerate, TOP, LEFT, RIGHT, BOTTOM)
# raise SystemExit


RIGHT = WIDTH + PAD_LEFT
BOTTOM = HEIGHT# + TOP


if not args.benchmark:
    try:
        if args.sound:
            subprocess.Popen(["play",args.sound], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.call(["bash", script_path, str(args.playback_rate), str(TOP), str(LEFT), str(RIGHT), str(BOTTOM)], text=True)
    except KeyboardInterrupt:
        # Reset the terminal in case it doesnt render the user inputted text after Ctrl+C
        subprocess.call(["stty","sane"])
else:
    print(f"It took {time.time() - st} seconds.")

# subprocess.call(["bash", "anifetch.sh"], text=True)
