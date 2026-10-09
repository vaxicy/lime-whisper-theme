# -*- coding: utf-8 -*-
"""lime whisper theme - logo candidates (A-F).

Pure PIL drawing (no AI): every shape is rendered at 2048 px and downsampled to
512 / 256 / 128 so the curves stay smooth at small sizes.

The palette is read from themes/lime-whisper-{light,dark}-color-theme.json, so
re-generating the theme JSON never leaves the logo behind.

Output: store-assets/icon-candidates/ (candidate-a..f*.png + preview-a-f.png).
Nothing here overwrites the shipping assets/icon.png.
"""

import json
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

SS = 2048
SIZES = (512, 256, 128)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = "store-assets/icon-candidates"  # relative on purpose: Pillow + a
# non-ASCII absolute path ("D:\\\u8fc5\u96f7\u4e0b\u8f7d\\...") intermittently
# raises OSError 22 on save(), so every write goes through a relative path.
SAFE_MARGIN = 60


# ---------------------------------------------------------------- palette
def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def read_theme(name):
    path = os.path.join("themes", name)
    if not os.path.exists(path):
        raise SystemExit("theme file not found: %s (run from the project root)" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dig(theme, dotted, default):
    node = theme
    for key in dotted.split("."):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    if isinstance(node, str) and node.startswith("#"):
        return hex_to_rgb(node[:7])
    return default


def load_palette():
    """Every colour comes from a real theme key - no hard-coded duplicates."""
    light = read_theme("lime-whisper-light-color-theme.json")
    dark = read_theme("lime-whisper-dark-color-theme.json")

    def L(dotted, default):
        return dig(light, dotted, default)

    return {
        "CANVAS_LIGHT": L("colors.editor.background", (250, 252, 245)),
        "CANVAS_DARK": dig(dark, "colors.editor.background", (34, 43, 36)),
        "CREAM": L("colors.input.background", (252, 253, 248)),
        "PITH": L("colors.tab.hoverBackground", (234, 253, 180)),
        "LIME_SOFT": dig(dark, "colors.editorCursor.foreground", (234, 253, 180)),
        "LIME": dig(dark, "colors.button.background", (215, 254, 185)),
        "LEMON": dig(dark, "colors.terminal.ansiBrightYellow", (253, 250, 176)),
        "LEAF": L("colors.gitDecoration.addedResourceForeground", (94, 147, 75)),
        "LEAF_DEEP": L("colors.focusBorder", (114, 155, 76)),
        "INK_DEEP": L("colors.editor.foreground", (53, 67, 53)),
        "INK": dig(dark, "colors.editor.foreground", (220, 230, 211)),
        "MINT": dig(dark, "colors.textLink.foreground", (163, 227, 205)),
        "MINT_DEEP": L("colors.textLink.foreground", (56, 121, 106)),
    }


# ---------------------------------------------------------------- helpers
def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def cubic(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (
        u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
        u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
    )


def quad(p0, p1, p2, t):
    u = 1.0 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


def cubic_points(p0, p1, p2, p3, steps):
    return [cubic(p0, p1, p2, p3, i / steps) for i in range(steps + 1)]


def quad_points(p0, p1, p2, steps):
    return [quad(p0, p1, p2, i / steps) for i in range(steps + 1)]


def drop_points(cx, cy, r, h_ratio, shoulder_deg=-18.0, steps=140):
    """Teardrop: round bottom, tapering smoothly to a point on top."""
    sh = math.radians(shoulder_deg)
    apex = (cx, cy - r * h_ratio)
    right = (cx + r * math.cos(sh), cy + r * math.sin(sh))
    left = (cx - r * math.cos(sh), cy + r * math.sin(sh))

    pts = []
    a0, a1 = sh, math.pi - sh
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    # leave the shoulder along the circle tangent so the outline stays smooth
    k = 0.55 * math.dist(left, apex)
    tan_l = (-math.sin(math.pi - sh), math.cos(math.pi - sh))
    ctrl_l = (left[0] + tan_l[0] * k, left[1] + tan_l[1] * k)
    for i in range(1, steps + 1):
        pts.append(quad(left, ctrl_l, apex, i / steps))

    tan_r = (math.sin(sh), -math.cos(sh))
    ctrl_r = (right[0] + tan_r[0] * k, right[1] + tan_r[1] * k)
    for i in range(1, steps + 1):
        pts.append(quad(apex, ctrl_r, right, i / steps))
    return pts


def rotate_pts(pts, cx, cy, angle):
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


def new_layer():
    return Image.new("RGBA", (SS, SS), (0, 0, 0, 0))


def poly_mask(points):
    m = Image.new("L", (SS, SS), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def circle_mask(cx, cy, r):
    m = Image.new("L", (SS, SS), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def ring_mask(cx, cy, r_out, r_in):
    return ImageChops.subtract(circle_mask(cx, cy, r_out), circle_mask(cx, cy, r_in))


def sector_mask(cx, cy, r, a0, a1):
    m = Image.new("L", (SS, SS), 0)
    ImageDraw.Draw(m).pieslice([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=255)
    return m


def stroke_points(points, hw_start, hw_end, bell=False):
    """Closed outline for a polyline; `bell` tapers it to a point at both ends
    (the soft stroke used for the whisper gusts)."""
    n = len(points)
    left, right = [], []
    for i, (x, y) in enumerate(points):
        t = i / (n - 1)
        hw = hw_start * math.sin(math.pi * t) if bell else hw_start + (hw_end - hw_start) * t
        j, k = min(i + 1, n - 1), max(i - 1, 0)
        dx, dy = points[j][0] - points[k][0], points[j][1] - points[k][1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + list(reversed(right))


def linear_grad(c1, c2, angle_deg, small=256):
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    g = Image.new("RGB", (small, small))
    px = g.load()
    for j in range(small):
        y = (j + 0.5) / small - 0.5
        for i in range(small):
            x = (i + 0.5) / small - 0.5
            px[i, j] = mix(c1, c2, x * ux + y * uy + 0.5)
    return g.resize((SS, SS), Image.LANCZOS)


def radial_grad(c1, c2, cx, cy, r, small=256):
    g = Image.new("RGB", (small, small))
    px = g.load()
    for j in range(small):
        y = (j + 0.5) / small * SS - cy
        for i in range(small):
            x = (i + 0.5) / small * SS - cx
            px[i, j] = mix(c1, c2, math.hypot(x, y) / r)
    return g.resize((SS, SS), Image.LANCZOS)


def paint(img, mask, grad):
    layer = grad.convert("RGBA")
    layer.putalpha(mask)
    img.alpha_composite(layer)


def paint_solid(img, mask, color, alpha=255):
    layer = Image.new("RGBA", (SS, SS), color + (alpha,))
    layer.putalpha(mask)
    img.alpha_composite(layer)


# ------------------------------------------------------- shared figure parts
def rind_grad(P):
    return linear_grad(P["LEAF"], mix(P["LEAF"], P["INK_DEEP"], 0.42), 122)


def paint_lime_slice(img, P, cx, cy, r, wedges=8, spin=0.0, clip=None):
    """Flat lime cross-section: deep rind, cream pith, juicy lime wedges."""
    ring = ring_mask(cx, cy, r, r * 0.838)
    pith = circle_mask(cx, cy, r * 0.888)
    flesh_r = r * 0.812
    flesh = circle_mask(cx, cy, flesh_r)
    if clip is not None:
        ring, pith, flesh = (ImageChops.multiply(m, clip) for m in (ring, pith, flesh))

    paint(img, ring, rind_grad(P))
    paint_solid(img, pith, P["CREAM"])
    paint(img, flesh, radial_grad(mix(P["LIME_SOFT"], P["CREAM"], 0.32),
                                  mix(P["LIME_SOFT"], P["LEAF"], 0.46), cx, cy, flesh_r))

    w0, w1 = r * 0.028, r * 0.052
    for i in range(wedges):
        a = math.radians(-90 + spin + i * 360.0 / wedges)
        nx, ny = -math.sin(a), math.cos(a)
        ex, ey = cx + flesh_r * math.cos(a), cy + flesh_r * math.sin(a)
        mem = poly_mask([
            (cx + nx * w0, cy + ny * w0),
            (ex + nx * w1, ey + ny * w1),
            (ex - nx * w1, ey - ny * w1),
            (cx - nx * w0, cy - ny * w0),
        ])
        tip = circle_mask(ex, ey, w1)
        if clip is not None:
            mem = ImageChops.multiply(mem, clip)
            tip = ImageChops.multiply(tip, clip)
        paint_solid(img, mem, P["CREAM"])
        paint_solid(img, tip, P["CREAM"])
    paint_solid(img, circle_mask(cx, cy, w0 * 1.5), P["CREAM"])


def leaf_points(width, height, steps=90):
    """Lanceolate leaf: base at (0, 0), tip at (0, -height)."""
    w = width / 1.48  # the cubic peak half-width lands at ~0.74 * w
    base, tip = (0.0, 0.0), (0.0, -height)
    left = cubic_points(base, (-w * 1.05, -height * 0.14), (-w * 0.92, -height * 0.72), tip, steps)
    right = cubic_points(tip, (w * 0.92, -height * 0.72), (w * 1.05, -height * 0.14), base, steps)
    return left + right


def leaf_mask(cx, cy, width, height, angle=0.0):
    pts = rotate_pts(leaf_points(width, height), 0.0, 0.0, angle)
    return poly_mask([(cx + x, cy + y) for x, y in pts])


def paint_leaf(img, P, cx, cy, width, height, angle=0.0,
               c_from=None, c_to=None, vein_alpha=150):
    c_from = c_from or P["LEAF"]
    c_to = c_to or P["LEAF_DEEP"]
    paint(img, leaf_mask(cx, cy, width, height, angle),
          linear_grad(c_from, c_to, 118))

    steps = 40
    right, left = [], []
    for i in range(steps + 1):
        t = i / steps
        y = -height * (0.03 + 0.93 * t)
        hw = width * 0.026 * (1.0 - 0.68 * t)
        right.append((hw, y))
        left.append((-hw, y))
    rib = rotate_pts(right + list(reversed(left)), 0.0, 0.0, angle)
    paint_solid(img, poly_mask([(cx + x, cy + y) for x, y in rib]), P["CREAM"], vein_alpha)

    # side veins: monotone outwards curves, so the outline never self-folds
    half = width / 2.0
    for k in range(3):
        t = 0.27 + 0.185 * k
        reach = 0.80 - 0.075 * k
        curve = cubic_points(
            (0.05 * half, -height * t),
            (0.42 * half, -height * (t + 0.045)),
            (0.72 * half, -height * (t + 0.115)),
            (reach * half, -height * (t + 0.195)),
            20,
        )
        for sign in (1, -1):
            pts = rotate_pts([(x * sign, y) for x, y in curve], 0.0, 0.0, angle)
            vein = stroke_points(pts, width * 0.014, width * 0.004)
            paint_solid(img, poly_mask([(cx + x, cy + y) for x, y in vein]),
                        P["CREAM"], vein_alpha)


def paint_gusts(img, P, x, y, length, rise, count=3, alphas=(255, 204, 158)):
    """Tapered breeze strokes: a whisper, deliberately not a wifi signal."""
    for i in range(count):
        scale = 1.0 - 0.24 * i
        gx, gy = x + length * 0.12 * i, y + rise * 0.26 * i
        pts = quad_points((gx, gy),
                          (gx + length * 0.55 * scale, gy - rise * 0.12 * scale),
                          (gx + length * scale, gy - rise * scale), 44)
        poly = stroke_points(pts, length * 0.050 * scale, 0.0, bell=True)
        paint_solid(img, poly_mask(poly), P["MINT_DEEP"], alphas[i])


# ------------------------------------------------------------- candidates
def cand_a_lime_slice(P):
    """A - the cross-section on its own: the cleanest read at small sizes."""
    img = new_layer()
    paint_lime_slice(img, P, SS / 2, SS / 2, 900)
    return img


def cand_b_half_fan(P):
    """B - half slice opened like a fan, with a leaf rising behind it."""
    img = new_layer()
    cx, cy, r = SS / 2, SS * 0.735, 900
    paint_leaf(img, P, cx, cy, 470, 1450, angle=24)
    paint_lime_slice(img, P, cx, cy, r, wedges=6, clip=sector_mask(cx, cy, r, 180, 360))
    paint_solid(img, poly_mask([
        (cx - r, cy), (cx + r, cy), (cx + r, cy + r * 0.045), (cx - r, cy + r * 0.045),
    ]), P["LEAF_DEEP"])
    return img


def cand_c_leaf_whisper(P):
    """C - a lime leaf whispering: soft gusts leave the leaf tip."""
    img = new_layer()
    lw, lh, la = 660, 1180, 24
    base_x, base_y = SS * 0.342, SS * 0.898
    tip = (base_x + lh * math.sin(math.radians(la)),
           base_y - lh * math.cos(math.radians(la)))
    paint_leaf(img, P, base_x, base_y, lw, lh, angle=la)
    paint_gusts(img, P, tip[0] + 70, tip[1] + 190, 700, 440)
    return img


def cand_d_lime_drop(P):
    """D - a lime drop: quiet and rounded, with a cream leaf inside."""
    img = new_layer()
    r, ratio = 620, 1.5
    cx = SS / 2
    cy = 130 + r * ratio  # apex lands at y = 130
    drop = poly_mask(drop_points(cx, cy, r, ratio))
    paint(img, drop, radial_grad(P["LIME"], P["LEAF"], cx - r * 0.34, cy - r * 0.44, r * 1.9))
    paint(img, ImageChops.multiply(drop, leaf_mask(cx, cy + r * 0.60, r * 0.86, r * 1.15, 6)),
          linear_grad(P["CREAM"], mix(P["CREAM"], P["LIME_SOFT"], 0.55), 112))
    return img


def cand_e_echo_slice(P):
    """E - a faded echo of the rind behind the slice: the whisper you half see."""
    img = new_layer()
    cx, cy, r = SS * 0.535, SS * 0.535, 745
    ghost = new_layer()
    paint(ghost, ring_mask(cx - 130, cy - 130, r, r * 0.838), rind_grad(P))
    ghost.putalpha(ghost.getchannel("A").point(lambda v: round(v * 0.34)))
    img.alpha_composite(ghost)
    paint_lime_slice(img, P, cx, cy, r, wedges=8, spin=8)
    return img


def cand_f_duo(P):
    """F - slice and leaf overlapping: leaf sprouts from the rind, cream rim."""
    img = new_layer()
    sx, sy, r = SS * 0.38, SS * 0.655, 560
    paint_lime_slice(img, P, sx, sy, r, wedges=8, spin=-6)
    lx, ly = sx + r * 0.707, sy - r * 0.707
    paint_leaf(img, P, lx, ly, 510, 915, angle=32, c_from=P["CREAM"], c_to=P["CREAM"])
    paint_leaf(img, P, lx, ly, 480, 900, angle=32)
    return img


CANDIDATES = [
    ("candidate-a-lime-slice", "A \u00b7 \u9752\u67e0\u5207\u9762", "Lime slice", cand_a_lime_slice),
    ("candidate-b-half-fan", "B \u00b7 \u534a\u67e0\u6247\u53f6", "Half slice + leaf", cand_b_half_fan),
    ("candidate-c-leaf-whisper", "C \u00b7 \u53f6\u8bed\u8f7b\u6ce2", "Leaf + whisper", cand_c_leaf_whisper),
    ("candidate-d-lime-drop", "D \u00b7 \u9752\u67e0\u9732\u73e0", "Lime drop", cand_d_lime_drop),
    ("candidate-e-echo-slice", "E \u00b7 \u67e0\u5f71\u56de\u58f0", "Echo slice", cand_e_echo_slice),
    ("candidate-f-duo", "F \u00b7 \u67e0\u53f6\u4ea4\u53e0", "Slice + leaf duo", cand_f_duo),
]


# ------------------------------------------------------------ verification
def normalize(art, box=1780):
    """Trim to the ink box, scale it to `box` and centre it: every candidate
    ends up optically the same size and centred in the square canvas."""
    art = art.crop(art.getchannel("A").getbbox())
    scale = box / max(art.size)
    art = art.resize((max(1, round(art.width * scale)),
                      max(1, round(art.height * scale))), Image.LANCZOS)
    out = new_layer()
    out.alpha_composite(art, ((SS - art.width) // 2, (SS - art.height) // 2))
    return out


def report(path, art):
    alpha = art.getchannel("A")
    bbox = alpha.getbbox()
    px = alpha.load()
    edges = 0
    for i in range(SS):
        for x, y in ((i, 0), (i, SS - 1), (0, i), (SS - 1, i)):
            if px[x, y] > 8:
                edges += 1
    margin = min(bbox[0], bbox[1], SS - bbox[2], SS - bbox[3]) if bbox else -1
    assert edges == 0, "%s touches the canvas edge (%d px)" % (path, edges)
    assert margin >= SAFE_MARGIN, "%s margin too small: %d px" % (path, margin)
    print("%-34s bbox=%-28s margin=%4d edge_pixels=%d"
          % (os.path.basename(path), bbox, margin, edges))


# ---------------------------------------------------------------- preview
def load_font(size, bold=False):
    names = ("msyhbd.ttc", "msyh.ttc") if bold else ("msyh.ttc", "segoeui.ttf", "arial.ttf")
    for name in names:
        path = os.path.join("C:\\Windows\\Fonts", name)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_preview(icons, P):
    cols, rows = 3, 2
    cell_w, cell_h, gap, pad = 480, 820, 16, 48
    art, title_h = 380, 150

    assert (cell_w - art) % 2 == 0
    width = pad * 2 + cols * cell_w + (cols - 1) * gap
    height = title_h + pad + rows * cell_h + (rows - 1) * gap + pad

    canvas = Image.new("RGB", (width, height), (18, 24, 19))
    dc = ImageDraw.Draw(canvas)
    dc.text((pad, 42), "lime whisper theme \u00b7 logo \u65b9\u6848 A\u2013F",
            font=load_font(52, bold=True), fill=(240, 244, 236))
    dc.text((pad, 108), "\u767d\u5e95\u4e3b\u56fe + 16/32/64/128 px \u7f29\u653e\u68c0\u67e5 + "
                        "\u4e3b\u9898\u6d45\u5e95 / \u6df1\u5e95", font=load_font(24),
            fill=(160, 176, 158))

    f_cn, f_en, f_num, f_band = (load_font(30, bold=True), load_font(20),
                                 load_font(18), load_font(19))
    bands = (
        (P["CANVAS_LIGHT"], "theme light bg  #FAFCF5", (56, 72, 54)),
        (P["CANVAS_DARK"], "theme dark bg  #222B24", (198, 212, 188)),
    )
    band_h = 40
    size_row_cy = 626

    for idx, (stem, cn, en, _fn) in enumerate(CANDIDATES):
        c, r = idx % cols, idx // cols
        x = pad + c * (cell_w + gap)
        y = title_h + pad + r * (cell_h + gap)

        tile = Image.new("RGB", (cell_w, cell_h), (255, 255, 255))
        dt = ImageDraw.Draw(tile)
        big = icons[idx].resize((art, art), Image.LANCZOS)
        tile.paste(big, ((cell_w - art) // 2, 46), big)
        dt.text((cell_w // 2, 492), cn, font=f_cn, fill=(38, 48, 38), anchor="mm")
        dt.text((cell_w // 2, 528), en, font=f_en, fill=(122, 136, 118), anchor="mm")

        assert 492 - art // 2 - 46 > 8
        for size, sx in ((128, 40), (64, 200), (32, 292), (16, 348)):
            small = icons[idx].resize((size, size), Image.LANCZOS)
            tile.paste(small, (sx, size_row_cy - size // 2), small)
            dt.text((sx + size // 2, 706), str(size), font=f_num,
                    fill=(146, 158, 142), anchor="mm")
            assert sx + size <= cell_w - 8

        for i, (bg, label, fg) in enumerate(bands):
            by = cell_h - (len(bands) - i) * band_h
            dt.rectangle([0, by, cell_w, by + band_h], fill=bg)
            ic = icons[idx].resize((26, 26), Image.LANCZOS)
            tile.paste(ic, (26, by + 7), ic)
            dt.text((66, by + band_h // 2), label, font=f_band, fill=fg, anchor="lm")

        assert y + cell_h <= height - pad
        assert x + cell_w <= width - pad
        canvas.paste(tile, (x, y))
    return canvas


def main():
    os.chdir(ROOT)
    P = load_palette()
    os.makedirs(OUT_DIR, exist_ok=True)

    icons = []
    for stem, _cn, _en, fn in CANDIDATES:
        art = normalize(fn(P))
        icons.append(art)
        for size in SIZES:
            suffix = "" if size == SIZES[0] else "-%d" % size
            path = os.path.join(OUT_DIR, "%s%s.png" % (stem, suffix))
            art.resize((size, size), Image.LANCZOS).save(path)
        report(os.path.join(OUT_DIR, "%s.png" % stem), art)

    preview = build_preview(icons, P)
    path = os.path.join(OUT_DIR, "preview-a-f.png")
    preview.save(path)
    print("saved %s %s" % (path, preview.size))


if __name__ == "__main__":
    main()
