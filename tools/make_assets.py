"""Generate the site's period-style GIFs and MIDI file.

All artwork is drawn from scratch here (no copied 90s clip art), using a
limited palette so the results look like they came out of Paint Shop Pro 4.
Run:  python tools/make_assets.py
"""
import math
import os
import random
import struct

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
os.makedirs(IMG, exist_ok=True)

FONTS = "C:/Windows/Fonts/"


def font(name, size):
    try:
        return ImageFont.truetype(FONTS + name, size)
    except OSError:
        return ImageFont.load_default()


def save_gif(frames, name, duration=120, transparent=None):
    path = os.path.join(IMG, name)
    pal = [f.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]
    kwargs = {}
    if transparent is not None:
        kwargs["transparency"] = transparent
    if len(pal) == 1:
        pal[0].save(path, **kwargs)
    else:
        pal[0].save(path, save_all=True, append_images=pal[1:], duration=duration, loop=0, disposal=2)


def save_gif_transparent(frames, name, duration=120):
    """Frames are RGBA; fully transparent pixels become the GIF's transparent index."""
    path = os.path.join(IMG, name)
    out = []
    for f in frames:
        rgb = Image.new("RGB", f.size, (255, 0, 255))
        rgb.paste(f, mask=f.split()[3].point(lambda a: 255 if a > 128 else 0))
        p = rgb.quantize(colors=63, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        pal = p.getpalette()[:63 * 3]
        idx = None
        for i in range(63):
            if pal[i * 3:i * 3 + 3] == [255, 0, 255]:
                idx = i
        out.append((p, idx))
    first, idx = out[0]
    first.save(path, save_all=len(out) > 1, append_images=[o[0] for o in out[1:]],
               duration=duration, loop=0, disposal=2,
               **({"transparency": idx} if idx is not None else {}))


# ---------------------------------------------------------------- backgrounds

def starfield():
    random.seed(7)
    im = Image.new("RGB", (128, 128), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(60):
        x, y = random.randrange(128), random.randrange(128)
        c = random.choice([(255, 255, 255), (204, 204, 204), (153, 153, 153), (255, 255, 153)])
        d.point((x, y), c)
    for _ in range(4):
        x, y = random.randrange(4, 124), random.randrange(4, 124)
        d.line((x - 2, y, x + 2, y), (255, 255, 255))
        d.line((x, y - 2, x, y + 2), (255, 255, 255))
    im.save(os.path.join(IMG, "stars.gif"))


def parchment():
    random.seed(3)
    im = Image.new("RGB", (96, 96), (255, 255, 204))
    px = im.load()
    for y in range(96):
        for x in range(96):
            n = random.randint(-14, 6)
            px[x, y] = (255 + min(n, 0), 255 + min(n, 0), 204 + n)
    im.save(os.path.join(IMG, "parchment.gif"))


def sidebar_bg():
    # Classic "left stripe" background: wide enough that it never repeats horizontally at 1024px.
    im = Image.new("RGB", (1280, 8), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 150, 8), (0, 0, 102))
    for i, c in enumerate([(51, 51, 153), (102, 102, 204), (153, 153, 255)]):
        d.rectangle((151 + i * 3, 0, 153 + i * 3, 8), c)
    im.save(os.path.join(IMG, "sidebar_bg.gif"))


# ---------------------------------------------------------------- rules & bullets

def rainbow_bar():
    w, h = 600, 8
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for x in range(w):
        hue = x / w * 6
        i = int(hue)
        f = hue - i
        r, g, b = [(1, f, 0), (1 - f, 1, 0), (0, 1, f), (0, 1 - f, 1), (f, 0, 1), (1, 0, 1 - f)][i % 6]
        d.line((x, 0, x, h), (int(r * 255), int(g * 255), int(b * 255)))
    d.line((0, 0, w, 0), (255, 255, 255))
    d.line((0, h - 1, w, h - 1), (64, 64, 64))
    im.save(os.path.join(IMG, "rainbow_bar.gif"))


def flame_bar():
    frames = []
    for t in range(4):
        im = Image.new("RGBA", (600, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        random.seed(t)
        for x in range(0, 600, 3):
            hgt = 6 + int(5 * math.sin(x / 9 + t * 1.7)) + random.randint(0, 4)
            d.line((x, 16, x, 16 - hgt), (255, 102, 0, 255), 3)
            d.line((x, 16, x, 16 - hgt // 2), (255, 255, 0, 255), 3)
        frames.append(im)
    save_gif_transparent(frames, "flame_bar.gif", 110)


def ball(color, name):
    im = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 13, 13), (0, 0, 0, 255))
    d.ellipse((1, 1, 12, 12), color + (255,))
    light = tuple(min(255, c + 120) for c in color)
    d.ellipse((3, 3, 6, 6), light + (255,))
    save_gif_transparent([im], name)


def new_badge():
    frames = []
    f = font("arialbd.ttf", 11)
    for fg, bg in [((255, 255, 0), (255, 0, 0)), ((255, 0, 0), (255, 255, 0))]:
        im = Image.new("RGBA", (34, 15), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        pts = []
        for i in range(16):
            r = 17 if i % 2 == 0 else 13
            a = i / 16 * 2 * math.pi
            pts.append((17 + r * math.cos(a), 7.5 + r * 0.45 * math.sin(a)))
        d.polygon(pts, bg + (255,))
        d.text((17, 8), "NEW!", fg + (255,), font=f, anchor="mm")
        frames.append(im)
    save_gif_transparent(frames, "new.gif", 400)


# ---------------------------------------------------------------- animated icons

def under_construction():
    w, h = 120, 122
    frames = []
    f = font("arialbd.ttf", 10)
    for t in range(6):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # diamond sign
        d.polygon([(60, 2), (104, 46), (60, 90), (16, 46)], (0, 0, 0, 255))
        d.polygon([(60, 6), (100, 46), (60, 86), (20, 46)], (255, 204, 0, 255))
        # digger figure
        x0 = 52
        d.ellipse((x0, 24, x0 + 8, 32), (0, 0, 0, 255))
        d.line((x0 + 4, 32, x0 + 2, 48), (0, 0, 0, 255), 3)
        d.line((x0 + 2, 48, x0 - 4, 60), (0, 0, 0, 255), 3)
        d.line((x0 + 2, 48, x0 + 8, 60), (0, 0, 0, 255), 3)
        dig = 4 if t % 2 else -2
        d.line((x0 + 3, 36, x0 + 14, 40 + dig), (0, 0, 0, 255), 3)
        d.line((x0 + 14, 30 + dig, x0 + 14, 58 + dig), (0, 0, 0, 255), 2)
        d.polygon([(x0 + 10, 58 + dig), (x0 + 18, 58 + dig), (x0 + 14, 64 + dig)], (0, 0, 0, 255))
        # dirt pile
        d.pieslice((60, 56, 84, 76), 180, 360, (0, 0, 0, 255))
        # stripes banner
        d.rectangle((0, 108, w - 1, h - 1), (0, 0, 0, 255))
        for i in range(-2, 14):
            x = i * 12 + (t * 4) % 12
            d.polygon([(x, 109), (x + 6, 109), (x - 2, h - 2), (x - 8, h - 2)], (255, 204, 0, 255))
        frames.append(im)
    # text frame flash
    out = []
    for i, im in enumerate(frames):
        im = im.copy()
        d = ImageDraw.Draw(im)
        txt_col = (255, 0, 0, 255) if i % 2 else (0, 0, 0, 255)
        d.rectangle((0, 92, w - 1, 107), (0, 0, 0, 255))
        d.text((60, 100), "UNDER CONSTRUCTION", (255, 255, 0, 255) if i % 2 else (255, 0, 0, 255), font=f, anchor="mm")
        out.append(im)
    save_gif_transparent(out, "construction.gif", 180)


def construction_small():
    frames = []
    f = font("arialbd.ttf", 9)
    for t in range(4):
        im = Image.new("RGB", (88, 31), (0, 0, 0))
        d = ImageDraw.Draw(im)
        for i in range(-2, 12):
            x = i * 10 + (t * 5) % 10
            d.polygon([(x, 0), (x + 5, 0), (x - 3, 31), (x - 8, 31)], (255, 204, 0))
        d.rectangle((8, 4, 79, 26), (0, 0, 0))
        col = (255, 255, 0) if t % 2 else (255, 255, 255)
        d.text((44, 10), "UNDER", col, font=f, anchor="mm")
        d.text((44, 20), "CONSTRUCTION", col, font=f, anchor="mm")
        frames.append(im)
    save_gif(frames, "construction_88.gif", 200)


def spinning_mail():
    frames = []
    n = 10
    for t in range(n):
        im = Image.new("RGBA", (48, 36), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        scale = abs(math.cos(t / n * math.pi * 2))
        hw = max(2, int(20 * scale))
        cx = 24
        face = (255, 255, 255, 255) if math.cos(t / n * math.pi * 2) > 0 else (220, 220, 220, 255)
        d.rectangle((cx - hw, 8, cx + hw, 30), face, (0, 0, 0, 255))
        if hw > 5 and math.cos(t / n * math.pi * 2) > 0:
            d.line((cx - hw, 8, cx, 21, cx + hw, 8), (0, 0, 0, 255), 1)
            d.rectangle((cx + hw - max(2, hw // 4), 10, cx + hw - 2, 15), (255, 0, 0, 255))
        frames.append(im)
    save_gif_transparent(frames, "email.gif", 90)


def fire_text_banner():
    """The big site title, with a cheesy 3D-ish gradient and a glint that sweeps across."""
    w, h = 560, 70
    f = font("impact.ttf", 44)
    text = "THE WORLD WIDE WAYBACK"
    frames = []
    for t in range(12):
        im = Image.new("RGB", (w, h), (0, 0, 0))
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).text((w // 2, h // 2), text, 255, font=f, anchor="mm")
        # drop shadow
        sh = Image.new("L", (w, h), 0)
        ImageDraw.Draw(sh).text((w // 2 + 4, h // 2 + 4), text, 255, font=f, anchor="mm")
        im.paste((102, 0, 153), mask=sh)
        grad = Image.new("RGB", (w, h))
        gd = ImageDraw.Draw(grad)
        for y in range(h):
            k = y / h
            gd.line((0, y, w, y), (255, int(255 - 200 * k), 0))
        gx = int((t / 11) * (w + 120)) - 60
        gd.polygon([(gx, 0), (gx + 24, 0), (gx - 6, h), (gx - 30, h)], (255, 255, 255))
        im.paste(grad, mask=mask)
        frames.append(im)
    save_gif(frames, "title.gif", 110)


def counter_digits():
    f = font("courbd.ttf", 20)
    for n in range(10):
        im = Image.new("RGB", (15, 22), (0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 14, 21), (0, 0, 0), (102, 102, 102))
        d.text((7, 11), str(n), (0, 255, 0), font=f, anchor="mm")
        im.save(os.path.join(IMG, f"digit{n}.gif"))


# ---------------------------------------------------------------- 88x31 buttons

def button(name, top, bottom, bg, fg=(255, 255, 255), accent=None, frames=1):
    out = []
    ft = font("arialbd.ttf", 10)
    fb = font("arial.ttf", 9)
    for t in range(frames):
        im = Image.new("RGB", (88, 31), bg)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 87, 30), None, (255, 255, 255))
        d.line((0, 30, 87, 30), (64, 64, 64))
        d.line((87, 0, 87, 30), (64, 64, 64))
        if accent:
            d.rectangle((2, 2, 26, 28), accent)
            d.ellipse((6, 6, 22, 24), (255, 255, 255) if t % 2 == 0 or frames == 1 else (255, 255, 0))
            tx = 57
        else:
            tx = 44
        d.text((tx, 10), top, fg, font=ft, anchor="mm")
        d.text((tx, 21), bottom, fg if t % 2 == 0 else (255, 255, 0), font=fb, anchor="mm")
        out.append(im)
    save_gif(out, name, 500)


def buttons():
    button("btn_navigator.gif", "NAVIGATOR", "get it NOW!", (0, 51, 102), accent=(0, 102, 153), frames=2)
    button("btn_notepad.gif", "Made with", "NOTEPAD.EXE", (0, 0, 128))
    button("btn_800x600.gif", "Best viewed", "at 800 x 600", (0, 102, 0))
    button("btn_html32.gif", "HTML 3.2", "valid-ish!", (153, 0, 0))
    button("btn_nofx.gif", "NO FRAMES?", "no problem", (102, 0, 102))
    button("btn_webring.gif", "RETRO WEB", "RING MEMBER", (0, 0, 0), fg=(255, 255, 0), frames=2)
    button("btn_wayback.gif", "WORLD WIDE", "WAYBACK", (51, 0, 102), fg=(255, 204, 0))
    button("btn_anybrowser.gif", "ANY BROWSER", "campaign", (51, 51, 51))


def imagemap_menu():
    """One big menu image, split into hot spots with <MAP> on the anatomy page."""
    im = Image.new("RGB", (400, 40), (0, 0, 102))
    d = ImageDraw.Draw(im)
    f = font("arialbd.ttf", 12)
    labels = ["TIMELINE", "COLORS", "THEN/NOW", "LINKS"]
    fills = [(204, 0, 0), (0, 153, 0), (204, 153, 0), (102, 0, 153)]
    for i, (label, fill) in enumerate(zip(labels, fills)):
        x0 = i * 100 + 4
        d.rectangle((x0, 4, x0 + 91, 35), fill, (255, 255, 255))
        d.line((x0, 35, x0 + 91, 35), (0, 0, 0))
        d.line((x0 + 91, 4, x0 + 91, 35), (0, 0, 0))
        d.text((x0 + 46, 20), label, (255, 255, 255), font=f, anchor="mm")
    im.save(os.path.join(IMG, "imagemap.gif"))


# ---------------------------------------------------------------- misc

def spacer():
    im = Image.new("P", (1, 1), 0)
    im.putpalette([255, 255, 255])
    im.save(os.path.join(IMG, "spacer.gif"), transparency=0)


def globe():
    frames = []
    n = 12
    for t in range(n):
        im = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((2, 2, 37, 37), (0, 51, 204, 255), (0, 0, 0, 255))
        for k in range(3):
            phase = (t / n + k / 3) % 1
            x = 2 + phase * 44 - 6
            d.ellipse((x, 9 + k * 7, x + 12, 17 + k * 7), (0, 153, 0, 255))
        # clip to circle
        m = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(m).ellipse((2, 2, 37, 37), 255)
        clipped = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        clipped.paste(im, mask=m)
        ImageDraw.Draw(clipped).ellipse((2, 2, 37, 37), None, (0, 0, 0, 255))
        ImageDraw.Draw(clipped).ellipse((9, 7, 15, 12), (153, 204, 255, 255))
        frames.append(clipped)
    save_gif_transparent(frames, "globe.gif", 100)


def hourglass():
    frames = []
    for t in range(4):
        im = Image.new("RGBA", (20, 28), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((2, 0, 17, 2), (102, 51, 0, 255))
        d.rectangle((2, 25, 17, 27), (102, 51, 0, 255))
        d.polygon([(4, 3), (15, 3), (10, 13), (9, 13)], (255, 255, 255, 255), (0, 0, 0, 255))
        d.polygon([(4, 24), (15, 24), (10, 14), (9, 14)], (255, 255, 255, 255), (0, 0, 0, 255))
        top = 4 - t
        if top > 0:
            d.polygon([(6, 12 - top * 2), (13, 12 - top * 2), (10, 13), (9, 13)], (255, 204, 0, 255))
        d.polygon([(6, 24), (13, 24), (10, 24 - t * 2 - 1), (9, 24 - t * 2 - 1)], (255, 204, 0, 255))
        frames.append(im)
    save_gif_transparent(frames, "hourglass.gif", 300)


# ---------------------------------------------------------------- MIDI

def write_midi():
    """An original, cheerful General MIDI ditty (piano + bass), ~16 bars."""
    tpq = 96

    def vlq(n):
        out = [n & 0x7F]
        n >>= 7
        while n:
            out.insert(0, (n & 0x7F) | 0x80)
            n >>= 7
        return bytes(out)

    def track(events):
        data = b""
        for delta, ev in events:
            data += vlq(delta) + ev
        data += b"\x00\xff\x2f\x00"
        return b"MTrk" + struct.pack(">I", len(data)) + data

    def notes(ch, program, seq, vel=96):
        ev = [(0, bytes([0xC0 | ch, program]))]
        pending = 0
        for pitch, dur in seq:
            if pitch is None:
                pending += dur
                continue
            ev.append((pending, bytes([0x90 | ch, pitch, vel])))
            ev.append((dur, bytes([0x80 | ch, pitch, 0])))
            pending = 0
        return ev

    q, e, h = tpq, tpq // 2, tpq * 2
    C, D, E, F, G, A, B = 72, 74, 76, 77, 79, 81, 83
    melody = [
        (E, e), (G, e), (C + 12, q), (B, e), (A, e), (G, q),
        (A, e), (G, e), (E, q), (D, e), (E, e), (C, q),
        (E, e), (G, e), (A, q), (G, e), (E, e), (D, q),
        (C, e), (D, e), (E, e), (G, e), (C, h),
    ] * 2
    bass_line = [(48, h), (45, h), (41, h), (43, h)] * 4
    tempo = (0, b"\xff\x51\x03" + struct.pack(">I", 500000)[1:])
    t0 = track([tempo] + notes(0, 80, melody, 100))  # GM 81: square lead
    t1 = track(notes(1, 38, bass_line, 90))  # GM 39: synth bass
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, tpq)
    with open(os.path.join(ROOT, "midi", "theme.mid"), "wb") as fh:
        fh.write(header + t0 + t1)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "midi"), exist_ok=True)
    starfield()
    parchment()
    sidebar_bg()
    rainbow_bar()
    flame_bar()
    for c, n in [((255, 0, 0), "ball_red.gif"), ((0, 0, 255), "ball_blue.gif"),
                 ((0, 204, 0), "ball_green.gif"), ((255, 204, 0), "ball_yellow.gif")]:
        ball(c, n)
    new_badge()
    under_construction()
    construction_small()
    spinning_mail()
    fire_text_banner()
    counter_digits()
    buttons()
    imagemap_menu()
    spacer()
    globe()
    hourglass()
    write_midi()
    print("done:", sorted(os.listdir(IMG)))
