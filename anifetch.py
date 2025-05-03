import subprocess
import os
import pathlib
import argparse
import shutil

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

# I could make the caching thing better by saving the name of the input file in /tmp/anifetch. If the filename is different --> should render animation. If the filename is same, but they say --force-render then render animation.

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

# Generate ASCII Video Frames via chafa & ffmpeg
if should_update:
    print_verbose("SHOULD RENDER WITH CHAFA")
    # delete all old frames
    shutil.rmtree("/tmp/anifetch/video")
    os.mkdir("/tmp/anifetch/video")

    # ffmpeg -i your-animation.gif -r 10 /tmp/anifetch/%03d.png
    subprocess.call(
        [
            "ffmpeg",
            "-i",
            f"{args.filename}",
            "-r",
            f"{args.framerate}",
            "/tmp/anifetch/video/%03d.png",
        ],
        stdout=None if not args.verbose else subprocess.DEVNULL,
        stderr=None if not args.verbose else subprocess.STDOUT,
    )

# TODO: I think I'm also supposed to remove the output cache(in case the number of animation frames of the new animation are shorter than the old animation)
# if the new anim frames is shorter than the old one, then in /output there will be both new and old frames.



# get the frames
animation_files = os.listdir(pathlib.Path("/tmp/anifetch/video"))
animation_files.sort()
for i, f in enumerate(animation_files):
    print_verbose(f"STARTING WITH FRAME {f}")
    # f = 001.png
    path = pathlib.Path("/tmp/anifetch/video") / f
    chafa_cmd = [
        "chafa",
        "--format",
        "symbols",
        "--color-space=rgb",
        f"--size={WIDTH}x{HEIGHT}",
        path.as_posix(),
    ]
    # print("CHAFA", " ".join(chafa_cmd))
    frame = subprocess.check_output(
        chafa_cmd,
        text=True,
    )

    # if wanted aspect ratio doesnt match source, chafa makes width as high as it can, and adjusts height accordingly.
    # AKA: even if I specify 40x20, chafa might give me 40x11 or something like that.
    if i == 0:
        HEIGHT = len(frame.splitlines())
    frames.append(frame)

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

    width_to_offset = GAP

    if chafa_line:
        if y == HEIGHT - 1:  # get rid of the empty end frame
            width_to_offset = GAP + WIDTH
    if not chafa_line:
        width_to_offset = GAP + WIDTH

    output = f"{(PAD_LEFT+(GAP*2)) * " "}{' ' * width_to_offset}{neo_line}\n"
    template.append(output)

# writing the tempate to a file.
with open("/tmp/anifetch/template.txt", "w") as f:
    f.writelines(template)
    # I just need to move this down, and also apply that padding thingy(for lines that dont have chafa anim)
    # so basically repeat what I have done but this time its for layout.
    # If I do this then I can get rid of the layout padding code on the last part. because the layout will already be fixed.

# for defining the positions of the cursor, that way I can set cursor pos and only redraw a portion of the text, not the entire text.
TOP = 2
LEFT = PAD_LEFT
RIGHT = WIDTH + PAD_LEFT
BOTTOM = HEIGHT# + TOP

# assuming that the neofetch text is longer vertically
out_frames: list[str] = []
for frame_i, frame in enumerate(frames):
    print_verbose(f"PROCESSING frame {frame_i}")
    width_to_offset = 0
    chafa_rows = frame.splitlines()

    out_frame_arr = []
    for y, neo_line in enumerate(neo_output):
        output = ""
        try:
            chafa_line = chafa_rows[y]
        except IndexError:
            chafa_line = ""

        width_to_offset = GAP
    
        if chafa_line:
            if y == HEIGHT - 1:  # get rid of the empty end frame
                width_to_offset = GAP + WIDTH
        if not chafa_line:
            width_to_offset = GAP + WIDTH #+ PAD_LEFT
        
        output = f"{PAD_LEFT * " "}{chafa_line}{' ' * width_to_offset}{neo_line}"

        out_frame_arr.append(output)

    out_frame: str = "\n".join(out_frame_arr)
    out_frames.append(out_frame)

print_verbose("FINISHED PROCESSING.")


print_verbose("First Frame Preview: ")
print_verbose(out_frames[0])

for i, frame in enumerate(out_frames):
    with open(f"/tmp/anifetch/output/{i}.txt", "w") as file:
        file.write(frame)

print_verbose("WROTE TO /tmp/anifetch/output/ .")

script_dir = os.path.dirname(__file__)
script_path = os.path.join(script_dir, "loop-cursor.sh")

# print(args.framerate, TOP, LEFT, RIGHT, BOTTOM)
# raise SystemExit

try:
    subprocess.call(["bash", script_path, str(args.framerate), str(TOP), str(LEFT), str(RIGHT), str(BOTTOM)], text=True)
except KeyboardInterrupt:
    pass

# subprocess.call(["bash", "anifetch.sh"], text=True)
