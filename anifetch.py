import subprocess
import os
import pathlib
import argparse
import shutil
import time

st = time.time()

GAP = 2
PAD_LEFT = 4

parser = argparse.ArgumentParser(
    prog="Anifetch",
    description="Allows you to use neofetch with video in terminal(using chafa).",
)
parser.add_argument(
    "-f",
    "--filename",
    default="your-animation.gif",
    help="Default is your-animation.gif, you can specify a different file via this argument.",
    type=str
)
parser.add_argument("-w","-W", "--width", default=40, help="Width of the chafa animation.", type=int)
parser.add_argument("-H", "--height", default=20, help="Height of the chafa animation.", type=int)
parser.add_argument("-v", "--verbose", default=False, action="store_true")
parser.add_argument(
    "-r", "--framerate", default=10, help="sets the framerate of the chafa animation.", type=int
)
parser.add_argument(
    "-fr",
    "--force-render",
    default=False,
    action="store_true",
    help="Disabled by default. Anifetch saves the filename to check if the file has changed, if the name is same, it won't render it again. If enabled, the video will be forcefully rendered, whether it has the same name or not. Please note that it only checks for filename, if you changed the framerate then you'll need to force render.",
)
parser.add_argument("-c","--chafa-arguments",default="--symbols ascii --fg-only", help="Specify the arguments to give to chafa. For more informations, use 'chafa --help'")

args = parser.parse_args()


def print_verbose(*msg):
    if args.verbose:
        print(*msg)


# Get Neofetch Output
neo_output = subprocess.check_output(["neofetch"], shell=True, text=True).splitlines()
for i, line in enumerate(neo_output):
    line = line[4:]  # i forgot what this does, but its important iirc.
    neo_output[i] = line

neo_output.pop(0)
neo_output.pop(0)
neo_output.pop(0)
neo_output.pop(-1)

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

# check old file
old_filename = ""
try:
    with open("/tmp/anifetch/filename", "r") as f:
        old_filename = f.read()

        if args.filename == old_filename:
            should_update = args.force_render
        else:
            should_update = True
except FileNotFoundError:
    should_update = True

with open("/tmp/anifetch/filename", "w") as f:
    f.write(args.filename)


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

# modifying template to account for the width of the chafa animation.
chafa_rows = frames[0].splitlines()
template = []
for y, neo_line in enumerate(neo_output):
    output = ""
    try:
        chafa_line = chafa_rows[y]
    except IndexError:
        chafa_line = ""

    width_to_offset = GAP + WIDTH

    # I have no idea why this is the way it is.
    output = f"{(PAD_LEFT+ (GAP*2) ) * " "}{' ' * width_to_offset}{neo_line}\n"
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

print(f"It took {time.time() - st} seconds.")

try:
    subprocess.call(["bash", script_path, str(args.framerate), str(TOP), str(LEFT), str(RIGHT), str(BOTTOM)], text=True)
except KeyboardInterrupt:
    pass

# subprocess.call(["bash", "anifetch.sh"], text=True)
