#!/bin/zsh --no-rcs
# Regenerate docs/images/demo.gif, the README animation, from the workflow's real answers.
# Needs Xcode's swiftc and ffmpeg (Homebrew). Refresh rates first so the numbers are current:
#   /usr/bin/python3 calculate.py --refresh && tools/demo/make.sh
set -e
here=${0:A:h}
root=${here:h:h}
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

/usr/bin/python3 "$here/storyboard.py" > "$work/board.json"
swiftc -O -o "$work/render" "$here/render.swift"
"$work/render" "$work/board.json" "$work"

mkdir -p "$root/docs/images"
scale="scale=1000:-1:flags=lanczos"
ffmpeg -v error -f concat -safe 0 -i "$work/frames.ffconcat" -vf "$scale,palettegen=stats_mode=full" -y "$work/palette.png"
ffmpeg -v error -f concat -safe 0 -i "$work/frames.ffconcat" -i "$work/palette.png" \
    -lavfi "${scale}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" \
    -fps_mode vfr -loop 0 -y "$root/docs/images/demo.gif"
ls -l "$root/docs/images/demo.gif"
