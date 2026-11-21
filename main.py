#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

A deterministic program (stdlib + Pillow only, no network) that draws one
invented passport spread — the data page and a visa/stamp page of the
Republic of Talvera, a small island nation that does not exist — and writes
it to /output/entry.png (1024x1024, under 1 MiB).

Every date, stamp and number agrees with every other: the passport was
issued 12 MAR 2023, so no stamp predates it; the Ostara visa is valid
01 MAY - 30 OCT 2023 and the Ostara entry stamp falls inside that window;
the MRZ check digits follow the ICAO 7-3-1 algorithm.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- fonts ---

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------- colours ---

DESK_TOP = (96, 66, 44)
DESK_BOT = (58, 38, 26)
PAGE = (247, 242, 228)
PAGE_EDGE = (214, 203, 178)
INK = (28, 32, 48)
INK_SOFT = (74, 78, 96)
GOLD = (146, 108, 42)
RED = (148, 42, 38)
BLUE = (38, 66, 128)
PURPLE = (96, 52, 128)
GREEN = (34, 96, 58)
SKIN = (238, 195, 157)
SKIN_SH = (222, 172, 128)
HAIR = (74, 50, 38)
JACKET = (44, 62, 85)

# ----------------------------------------------------------------- data ---

COUNTRY = "REPUBLIC OF TALVERA"
SURNAME = "VOSS"
GIVEN = "ELIN MARA"
DOB = "04 JUN 1988"
POB = "PORT MERIDIA, TALVERA"
SEX = "F"
DOC_NO = "TV4829167"
ISSUED = "12 MAR 2023"
EXPIRES = "11 MAR 2033"
AUTHORITY = "MINISTRY OF THE INTERIOR"

# ------------------------------------------------------------ MRZ digits ---

_VALUES = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<")}


def _check_digit(text):
    total = 0
    for i, ch in enumerate(text):
        total += _VALUES[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = ("P<TAL" + SURNAME + "<<" + GIVEN.replace(" ", "<")).ljust(44, "<")
    doc = DOC_NO + "<"
    dob = "880604"
    exp = "330311"
    personal = "TALV880604<<<<"
    line2 = (
        doc + _check_digit(doc)
        + "TAL"
        + dob + _check_digit(dob)
        + SEX
        + exp + _check_digit(exp)
        + personal + _check_digit(personal)
    )
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# --------------------------------------------------------------- helpers ---

def star(draw, cx, cy, r, fill):
    """Five-pointed star centred at (cx, cy)."""
    import math

    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def waves(draw, x, y, w, fill, amp=3, step=6):
    """Three small horizontal wavy lines (the sea under the arms)."""
    import math

    for k in range(3):
        pts = []
        for px in range(x, x + w + 1, step):
            pts.append((px, y + k * 8 + amp * math.sin((px - x) / w * math.pi * 2)))
        draw.line(pts, fill=fill, width=2)


def coat_of_arms(draw, cx, cy, s):
    """Small shield-and-star arms for Talvera: a shield, a star, sea waves."""
    w, h = int(52 * s), int(62 * s)
    x0, y0 = cx - w // 2, cy - h // 2
    shield = [
        (x0, y0), (x0 + w, y0), (x0 + w, y0 + h - 16),
        (cx, y0 + h), (x0, y0 + h - 16),
    ]
    draw.polygon(shield, outline=GOLD, width=3)
    draw.polygon(
        [(x0 + 4, y0 + 4), (x0 + w - 4, y0 + 4), (x0 + w - 4, y0 + h - 18),
         (cx, y0 + h - 4), (x0 + 4, y0 + h - 18)],
        outline=(176, 140, 70), width=1,
    )
    star(draw, cx, y0 + int(20 * s), int(11 * s), GOLD)
    waves(draw, x0 + 9, y0 + int(38 * s), w - 18, (58, 96, 140))


def guilloche(draw, box, colour, spacing=7):
    """Fine diagonal line work, like security printing, inside a box."""
    x0, y0, x1, y1 = box
    for d in range(-(y1 - y0), x1 - x0, spacing):
        draw.line([(x0 + d, y1), (x0 + d + (y1 - y0), y0)], fill=colour, width=1)


def portrait(draw, box):
    """Stylised passport portrait: a woman with dark hair, navy jacket."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    # pale blue-grey backdrop with fine security lines (drawn on a layer
    # so the diagonal work cannot spill past the photo's edge)
    bg = Image.new("RGBA", (w, h), (205, 222, 234, 255))
    bgd = ImageDraw.Draw(bg)
    for dd in range(-h, w, 6):
        bgd.line([(dd, h), (dd + h, 0)], fill=(188, 208, 224, 255), width=1)
    draw._image.paste(bg, (x0, y0))
    # shoulders / jacket
    draw.polygon(
        [(x0 + 8, y1), (x0 + 34, y0 + h * 0.66), (cx - 26, y0 + h * 0.60),
         (cx + 26, y0 + h * 0.60), (x1 - 34, y0 + h * 0.66), (x1 - 8, y1)],
        fill=JACKET,
    )
    # white shirt V and collar
    draw.polygon([(cx - 24, y0 + h * 0.60), (cx, y0 + h * 0.86),
                  (cx + 24, y0 + h * 0.60)], fill=(244, 244, 240))
    draw.polygon([(cx - 24, y0 + h * 0.60), (cx - 8, y0 + h * 0.68),
                  (cx, y0 + h * 0.62), (cx + 8, y0 + h * 0.68),
                  (cx + 24, y0 + h * 0.60)], fill=(232, 232, 226))
    # neck
    draw.rectangle([cx - 14, y0 + h * 0.50, cx + 14, y0 + h * 0.63], fill=SKIN_SH)
    # face
    draw.ellipse([cx - 40, y0 + h * 0.10, cx + 40, y0 + h * 0.56], fill=SKIN)
    # ears
    draw.ellipse([cx - 46, y0 + h * 0.30, cx - 36, y0 + h * 0.42], fill=SKIN)
    draw.ellipse([cx + 36, y0 + h * 0.30, cx + 46, y0 + h * 0.42], fill=SKIN)
    # hair: dark bob framing the face, parted in the middle
    draw.pieslice([cx - 46, y0 + h * 0.02, cx + 46, y0 + h * 0.44],
                  180, 360, fill=HAIR)
    draw.polygon([(cx - 46, y0 + h * 0.20), (cx - 34, y0 + h * 0.06),
                  (cx - 30, y0 + h * 0.24)], fill=HAIR)
    draw.polygon([(cx + 46, y0 + h * 0.20), (cx + 34, y0 + h * 0.06),
                  (cx + 30, y0 + h * 0.24)], fill=HAIR)
    # hair falling to the shoulders on both sides
    draw.rectangle([cx - 48, y0 + h * 0.22, cx - 34, y0 + h * 0.62], fill=HAIR)
    draw.rectangle([cx + 34, y0 + h * 0.22, cx + 48, y0 + h * 0.62], fill=HAIR)
    # brows, eyes, nose, mouth
    for sgn in (-1, 1):
        ex = cx + sgn * 17
        ey = y0 + h * 0.32
        draw.line([(ex - 9, ey - 7), (ex + 9, ey - 7)], fill=HAIR, width=2)
        draw.ellipse([ex - 6, ey - 2, ex + 6, ey + 4], fill=(255, 255, 255))
        draw.ellipse([ex - 3, ey - 1, ex + 3, ey + 4], fill=(52, 38, 30))
    draw.line([(cx, y0 + h * 0.34), (cx - 2, y0 + h * 0.43), (cx + 3, y0 + h * 0.44)],
              fill=(196, 146, 104), width=2)
    draw.arc([cx - 9, y0 + h * 0.465, cx + 9, y0 + h * 0.50], 15, 165,
             fill=(158, 74, 66), width=2)
    # soft light from the upper left
    draw.ellipse([cx - 40, y0 + h * 0.10, cx - 6, y0 + h * 0.30],
                 outline=(255, 255, 255), width=0)


def stamp(canvas, x, y, w, h, colour, title, lines, angle=0):
    """A rubber entry/exit stamp, drawn on its own layer and rotated."""
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=8,
                        outline=colour + (255,), width=3)
    d.line([20, 20 + 30, 20 + w, 20 + 30], fill=colour + (255,), width=2)
    d.text((20 + w // 2, 20 + 15), title, font=font(SANS_B, 15),
           fill=colour + (255,), anchor="mm")
    yy = 20 + 44
    for ln in lines:
        d.text((20 + w // 2, yy), ln, font=font(SANS_B, 13),
               fill=colour + (255,), anchor="mm")
        yy += 17
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    canvas.paste(layer, (x - 20, y - 20), layer)


# ------------------------------------------------------------- the spread ---

def draw_spread():
    img = Image.new("RGB", (1024, 1024), DESK_TOP)
    d = ImageDraw.Draw(img, "RGBA")
    # desk: vertical gradient + vignette
    for yy in range(1024):
        t = yy / 1023
        r = int(DESK_TOP[0] + (DESK_BOT[0] - DESK_TOP[0]) * t)
        g = int(DESK_TOP[1] + (DESK_BOT[1] - DESK_TOP[1]) * t)
        b = int(DESK_TOP[2] + (DESK_BOT[2] - DESK_TOP[2]) * t)
        d.line([(0, yy), (1024, yy)], fill=(r, g, b))
    # faint desk grain
    for yy in range(0, 1024, 5):
        d.line([(0, yy), (1024, yy)], fill=(0, 0, 0, 6))
    d.rectangle([0, 0, 1023, 1023], outline=(0, 0, 0, 60), width=24)

    # open passport: two pages with a spine shadow
    LX, RX, TY, BY = 52, 972, 150, 880
    MID = (LX + RX) // 2
    d.rectangle([LX + 6, TY + 10, RX + 6, BY + 10], fill=(0, 0, 0, 90))
    d.rectangle([LX, TY, MID, BY], fill=PAGE)
    d.rectangle([MID, TY, RX, BY], fill=(243, 238, 222))
    d.rectangle([MID - 2, TY, MID + 2, BY], fill=(196, 184, 156))
    d.rectangle([LX, TY, RX, BY], outline=PAGE_EDGE, width=2)
    d.line([LX + 6, TY, LX + 6, BY], fill=(255, 255, 255, 40), width=1)
    d.line([RX - 6, TY, RX - 6, BY], fill=(255, 255, 255, 40), width=1)

    # ======================================================= LEFT: data page
    coat_of_arms(d, LX + 230, TY + 52, 0.9)
    d.text((LX + 230, TY + 96), COUNTRY, font=font(SERIF_B, 25),
           fill=INK, anchor="mm")
    d.text((LX + 230, TY + 122), "P A S S P O R T   ·   P A S S E P O R T",
           font=font(SANS, 12), fill=INK_SOFT, anchor="mm")
    d.line([LX + 24, TY + 140, MID - 24, TY + 140], fill=GOLD, width=2)

    # portrait
    px0, py0, px1, py1 = LX + 24, TY + 158, LX + 174, TY + 348
    portrait(d, (px0, py0, px1, py1))
    d.rectangle([px0, py0, px1, py1], outline=INK_SOFT, width=2)
    d.text((px0 + 75, py1 + 14), "PHOTOGRAPH", font=font(SANS, 9),
           fill=INK_SOFT, anchor="mm")

    # data fields, right of the portrait
    fx = LX + 196
    fields = [
        ("SURNAME / NOM", SURNAME),
        ("GIVEN NAMES / PRÉNOMS", GIVEN),
        ("NATIONALITY / NATIONALITÉ", "TALVERAN"),
        ("DATE OF BIRTH / NÉ(E) LE", DOB),
        ("PLACE OF BIRTH / LIEU DE NAISSANCE", POB),
        ("SEX / SEXE", SEX),
        ("PASSPORT NO. / Nº DU PASSEPORT", DOC_NO),
        ("DATE OF ISSUE / DÉLIVRÉ LE", ISSUED),
        ("DATE OF EXPIRY / EXPIRE LE", EXPIRES),
    ]
    fy = TY + 156
    for label, value in fields:
        d.text((fx, fy), label, font=font(SANS, 9), fill=INK_SOFT)
        d.text((fx, fy + 12), value, font=font(SERIF_B, 15), fill=INK)
        fy += 34
    d.text((fx, fy + 2), "AUTHORITY / AUTORITÉ", font=font(SANS, 9),
           fill=INK_SOFT)
    d.text((fx, fy + 14), AUTHORITY, font=font(SERIF_B, 13), fill=INK)

    # signature strip (left column, below the portrait, clear of the fields)
    d.text((LX + 24, TY + 496), "HOLDER'S SIGNATURE / SIGNATURE DU TITULAIRE",
           font=font(SANS, 9), fill=INK_SOFT)
    sig = Image.new("RGBA", (180, 34), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    sd.line([(6, 24), (26, 10), (44, 26), (58, 8), (74, 24), (92, 12),
             (110, 26), (128, 10), (146, 22), (168, 12)],
            fill=(40, 48, 90, 220), width=2)
    sd.line([(20, 28), (160, 28)], fill=(40, 48, 90, 160), width=1)
    img.paste(sig, (LX + 24, TY + 510), sig)
    d.text((LX + 114, TY + 550), "Elin Mara Voss", font=font(SERIF, 13),
           fill=(40, 48, 90), anchor="mm")
    d.line([LX + 24, TY + 566, LX + 204, TY + 566], fill=INK_SOFT, width=1)

    # machine-readable zone
    mz_y = BY - 96
    d.rectangle([LX + 14, mz_y - 10, MID - 14, BY - 14], fill=(238, 234, 220))
    d.line([LX + 14, mz_y - 10, MID - 14, mz_y - 10], fill=INK_SOFT, width=1)
    l1, l2 = mrz_lines()
    d.text((LX + 24, mz_y + 4), l1, font=font(MONO, 16), fill=INK)
    d.text((LX + 24, mz_y + 30), l2, font=font(MONO, 16), fill=INK)
    d.text((LX + 24, BY - 22), "1", font=font(SANS, 10), fill=INK_SOFT)

    # ================================================ RIGHT: visas & stamps
    d.text((MID + 230, TY + 34), "VISAS", font=font(SERIF_B, 22),
           fill=INK, anchor="mm")
    d.text((MID + 230, TY + 58), "V I S A S   ·   E N T R Y   &   E X I T",
           font=font(SANS, 10), fill=INK_SOFT, anchor="mm")
    d.line([MID + 24, TY + 76, RX - 24, TY + 76], fill=GOLD, width=2)

    # --- Ostara visa sticker (the telling detail)
    vx, vy, vw, vh = MID + 24, TY + 92, 412, 150
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=(232, 240, 226),
                outline=(120, 150, 110), width=2)
    d.rectangle([vx + 6, vy + 6, vx + vw - 6, vy + 34], fill=(46, 92, 60))
    d.text((vx + 12, vy + 20), "VISA — KINGDOM OF OSTARA",
           font=font(SANS_B, 14), fill=(255, 255, 255), anchor="lm")
    d.text((vx + vw - 12, vy + 20), "No. OS-2214-077",
           font=font(SANS, 11), fill=(220, 235, 220), anchor="rm")
    vfields = [
        ("TYPE", "C — SINGLE ENTRY, TOURIST"),
        ("VALID", "01 MAY 2023  —  30 OCT 2023"),
        ("ISSUED", "22 APR 2023, PORT MERIDIA"),
        ("CONDITION", "NO EMPLOYMENT · FISHING PERMITS EXCLUDED"),
    ]
    yy = vy + 46
    for lab, val in vfields:
        d.text((vx + 12, yy), lab, font=font(SANS_B, 10), fill=(46, 92, 60))
        d.text((vx + 92, yy), val, font=font(SANS, 11), fill=INK)
        yy += 21
    d.text((vx + 12, vy + vh - 16),
           "HOLDER MUST REPORT TO THE HARBOURMASTER ON ARRIVAL",
           font=font(SANS, 9), fill=INK_SOFT)

    # --- stamps, all dated after the 12 MAR 2023 issue
    stamp(img, MID + 30, TY + 262, 190, 96, BLUE, "OSTARA",
          ["ARRIVAL · 14 MAY 2023", "PORT OF OSTARA", "★ 14 DAYS ★"], angle=-6)
    stamp(img, MID + 246, TY + 262, 190, 96, PURPLE, "OSTARA",
          ["DEPARTURE · 03 JUN 2023", "PORT OF OSTARA", "★ SEEN ★"], angle=5)
    stamp(img, MID + 30, TY + 378, 190, 96, RED, "KELDOR",
          ["ENTRY · 17 JUN 2023", "KELDOR BORDER POST 4", "★ 15 DAYS ★"],
          angle=4)
    stamp(img, MID + 246, TY + 378, 190, 96, RED, "KELDOR",
          ["EXIT · 02 JUL 2023", "KELDOR BORDER POST 4", "★ SEEN ★"], angle=-5)
    stamp(img, MID + 30, TY + 494, 190, 96, GREEN, "MARINOR",
          ["ARRIVAL · 09 SEP 2024", "FERRY TERMINAL", "★ 15 DAYS ★"],
          angle=-4)
    stamp(img, MID + 246, TY + 494, 190, 96, GREEN, "MARINOR",
          ["DEPARTURE · 24 SEP 2024", "FERRY TERMINAL", "★ SEEN ★"],
          angle=6)

    # --- home return stamp + fee stamp
    stamp(img, MID + 30, TY + 610, 190, 96, BLUE, "TALVERA",
          ["ARRIVAL · 21 OCT 2024", "PORT MERIDIA", "★ WELCOME HOME ★"],
          angle=3)
    fee = Image.new("RGBA", (220, 100), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fee)
    fd.ellipse([10, 10, 210, 90], outline=(148, 42, 38, 255), width=3)
    fd.ellipse([20, 20, 200, 80], outline=(148, 42, 38, 255), width=1)
    fd.text((110, 30), "FEE PAID", font=font(SANS_B, 15),
            fill=(148, 42, 38, 255), anchor="mm")
    fd.text((110, 50), "40 TALERS", font=font(SANS_B, 13),
            fill=(148, 42, 38, 255), anchor="mm")
    fd.text((110, 67), "PORT MERIDIA · 12 MAR 2023",
            font=font(SANS, 8), fill=(148, 42, 38, 255), anchor="mm")
    fee = fee.rotate(-7, resample=Image.BICUBIC, expand=False)
    img.paste(fee, (MID + 236, TY + 606), fee)

    d.text((RX - 24, BY - 22), "2", font=font(SANS, 10), fill=INK_SOFT,
           anchor="rm")

    # caption-free: the spread speaks for itself
    return img


def main():
    img = draw_spread()
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
        img.save(out, format="PNG", optimize=True)
    except OSError:
        os.makedirs("output", exist_ok=True)
        out = "output/entry.png"
        img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
