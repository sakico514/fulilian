"""Pre-process GIFs: remove white/gray background using edge flood-fill.

Flood-fills from all 4 edges to find background-connected pixels, then
makes them transparent. Preserves character interior pixels even if they're
similar in color (e.g., white hair/clothing).
"""

from __future__ import annotations

import os
from collections import deque

from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
THRESHOLD = 100
FRINGE_THRESHOLD = 150  # Wider threshold for anti-alias edge cleanup


def is_background(r, g, b, bg_r, bg_g, bg_b, threshold=THRESHOLD):
    return (
        abs(r - bg_r) < threshold
        and abs(g - bg_g) < threshold
        and abs(b - bg_b) < threshold
    )


def flood_fill_mask(pixels, w, h, bg_r, bg_g, bg_b):
    """Return a set of (x,y) coordinates that are background-connected from edges."""
    visited = set()
    queue = deque()

    for x in range(w):
        queue.append((x, 0))
        queue.append((x, h - 1))
    for y in range(1, h - 1):
        queue.append((0, y))
        queue.append((w - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        r, g, b, _a = pixels[x, y]
        if not is_background(r, g, b, bg_r, bg_g, bg_b):
            continue
        visited.add((x, y))
        queue.extend([
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
        ])
    return visited


def cleanup_fringe(pixels, w, h, bg_r, bg_g, bg_b, passes=3):
    """Remove anti-alias fringe pixels adjacent to transparent areas."""
    for _ in range(passes):
        to_clear = []
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                has_transparent_neighbor = False
                for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                    if 0 <= nx < w and 0 <= ny < h:
                        _ra, _ga, _ba, na = pixels[nx, ny]
                        if na == 0:
                            has_transparent_neighbor = True
                            break
                if has_transparent_neighbor and is_background(r, g, b, bg_r, bg_g, bg_b, FRINGE_THRESHOLD):
                    to_clear.append((x, y))
        for x, y in to_clear:
            pixels[x, y] = (0, 0, 0, 0)


def erode_edges(pixels, w, h, radius=2):
    """Dilate transparency outward by `radius` pixels — eats the outer edge
    of the character to remove any remaining wireframe/outline."""
    for _ in range(radius):
        to_clear = []
        for y in range(h):
            for x in range(w):
                _r, _g, _b, a = pixels[x, y]
                if a == 0:
                    continue
                # Check 8-neighborhood for any transparent pixel
                for nx, ny in [
                    (x+1,y), (x-1,y), (x,y+1), (x,y-1),
                    (x+1,y+1), (x-1,y-1), (x+1,y-1), (x-1,y+1),
                ]:
                    if 0 <= nx < w and 0 <= ny < h:
                        _ra, _ga, _ba, na = pixels[nx, ny]
                        if na == 0:
                            to_clear.append((x, y))
                            break
        for x, y in to_clear:
            pixels[x, y] = (0, 0, 0, 0)


def process_gif(input_path, output_path):
    im = Image.open(input_path)
    frames = []
    durations = []

    # Sample background color from the 4 corners of the first frame
    im.seek(0)
    first = im.convert("RGBA")
    w, h = first.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg_r = bg_g = bg_b = 0
    for x, y in corners:
        r, g, b, _ = first.getpixel((x, y))
        bg_r += r
        bg_g += g
        bg_b += b
    bg_r //= 4
    bg_g //= 4
    bg_b //= 4
    print(f"  Background color: rgb({bg_r},{bg_g},{bg_b})")

    try:
        frame_idx = 0
        while True:
            im.seek(frame_idx)
            frame = im.convert("RGBA")
            pixels = frame.load()
            mask = flood_fill_mask(pixels, w, h, bg_r, bg_g, bg_b)

            # Make background pixels transparent
            for x, y in mask:
                pixels[x, y] = (0, 0, 0, 0)

            # Clean up anti-alias fringe
            cleanup_fringe(pixels, w, h, bg_r, bg_g, bg_b, passes=3)

            # Erode outer edge to kill remaining wireframe
            erode_edges(pixels, w, h, radius=2)

            frames.append(frame.copy())
            durations.append(im.info.get("duration", 100))
            frame_idx += 1
    except EOFError:
        pass

    print(f"  Processed {len(frames)} frames")

    # Save as GIF with transparency
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        transparency=0,
        optimize=False,
    )
    print(f"  Saved: {output_path}")


def main():
    gif_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".gif")]
    print(f"Processing {len(gif_files)} GIFs in {ASSETS_DIR}...\n")

    for gif_file in gif_files:
        input_path = os.path.join(ASSETS_DIR, gif_file)
        output_path = os.path.join(ASSETS_DIR, gif_file)
        print(f"Processing: {gif_file}")
        process_gif(input_path, output_path)

    print("\nDone! All GIFs processed.")


if __name__ == "__main__":
    main()
