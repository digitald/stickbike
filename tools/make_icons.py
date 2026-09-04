"""Generate PWA icons: sky, hill, stick bike. Stdlib only."""
import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"


def png_rgba(path, w, h, pixels):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(pixels[y * w * 4 : (y + 1) * w * 4]) for y in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)


def blend(dst, i, r, g, b, a=255):
    if a >= 250:
        dst[i : i + 4] = bytes((r, g, b, 255))
        return
    t = a / 255
    dst[i] = int(dst[i] * (1 - t) + r * t)
    dst[i + 1] = int(dst[i + 1] * (1 - t) + g * t)
    dst[i + 2] = int(dst[i + 2] * (1 - t) + b * t)
    dst[i + 3] = 255


def disk(px, w, h, cx, cy, rad, rgb, width=None):
    r2 = rad * rad
    inner = (rad - width) ** 2 if width else -1
    x0, x1 = max(0, int(cx - rad - 1)), min(w, int(cx + rad + 2))
    y0, y1 = max(0, int(cy - rad - 1)), min(h, int(cy + rad + 2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r2 and d >= inner:
                aa = 1.0
                if d > (rad - 1) ** 2:
                    aa = max(0, rad - math.sqrt(d))
                blend(px, (y * w + x) * 4, rgb[0], rgb[1], rgb[2], int(255 * aa))


def line(px, w, h, x1, y1, x2, y2, rgb, thick):
    steps = int(max(abs(x2 - x1), abs(y2 - y1), 1) * 2)
    for i in range(steps + 1):
        t = i / steps
        disk(px, w, h, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, thick / 2, rgb)


def render(size):
    w = h = size
    px = bytearray([126, 193, 232, 255] * (w * h))
    ink = (34, 34, 34)
    grass = (165, 201, 106)
    s = size / 512
    # hill
    for y in range(h):
        for x in range(w):
            hill = int(h * 0.62 + math.sin(x / size * 5.2) * 18 * s)
            if y > hill:
                i = (y * w + x) * 4
                px[i : i + 3] = bytes(grass if y > hill + int(8 * s) else (46, 74, 31))
    cx, cy = size * 0.48, size * 0.58
    wr = 38 * s
    disk(px, w, h, cx - 70 * s, cy, wr, ink, width=7 * s)
    disk(px, w, h, cx + 70 * s, cy, wr, ink, width=7 * s)
    line(px, w, h, cx - 70 * s, cy, cx, cy - 58 * s, ink, 8 * s)
    line(px, w, h, cx + 70 * s, cy, cx, cy - 58 * s, ink, 8 * s)
    line(px, w, h, cx, cy - 58 * s, cx - 12 * s, cy - 118 * s, ink, 8 * s)
    disk(px, w, h, cx - 12 * s, cy - 140 * s, 16 * s, ink, width=6 * s)
    line(px, w, h, cx - 12 * s, cy - 100 * s, cx + 48 * s, cy - 72 * s, ink, 7 * s)
    line(px, w, h, cx - 8 * s, cy - 58 * s, cx + 8 * s, cy, ink, 7 * s)
    return px


def main():
    OUT.mkdir(exist_ok=True)
    for size in (192, 512):
        png_rgba(OUT / f"icon-{size}.png", size, size, render(size))
        print("wrote", OUT / f"icon-{size}.png")


if __name__ == "__main__":
    main()
