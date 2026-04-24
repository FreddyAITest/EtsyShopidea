#!/usr/bin/env python3
"""
Victorian Botanical Ephemera - Junk Journal Digital Product Generator
Creates 10 DIN A4 (2480x3508 px) pages at 300 DPI, then compiles into PDF.
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- Config ---
WIDTH = 2480   # DIN A4 at 300 DPI
HEIGHT = 3508  # DIN A4 at 300 DPI
DPI = 300
OUTPUT_DIR = "2026-04-25_Victorian_Botanical_Ephemera"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "Original_Bilder")
PDF_PATH = os.path.join(OUTPUT_DIR, "Produkt.pdf")
LISTING_PATH = os.path.join(OUTPUT_DIR, "Etsy_Listing_Info.txt")

os.makedirs(IMAGES_DIR, exist_ok=True)

# --- Color Palette (Victorian Ephemera) ---
PARCHMENT = (245, 235, 220)
AGED_PAPER = (235, 225, 205)
DARK_INK = (45, 35, 30)
SEPIA = (120, 90, 60)
SEPIA_LIGHT = (180, 150, 120)
ROSE_RED = (160, 60, 70)
ROSE_PINK = (190, 110, 120)
FERN_GREEN = (80, 110, 65)
FERN_DARK = (50, 75, 40)
GOLD = (180, 150, 60)
GOLD_DARK = (140, 110, 30)
NAVY = (30, 45, 80)
CREAM = (255, 248, 235)
BROWN = (100, 70, 40)
BROWN_LIGHT = (160, 130, 90)
WAX_RED = (150, 30, 30)


def make_parchment(w, h):
    """Create a parchment-colored background with aged texture."""
    img = Image.new('RGB', (w, h), PARCHMENT)
    draw = ImageDraw.Draw(img)
    # Add random foxing spots (aging marks)
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(5, 50)
        opacity = random.randint(10, 40)
        color = (max(0, PARCHMENT[0] - random.randint(5, 30)),
                 max(0, PARCHMENT[1] - random.randint(5, 30)),
                 max(0, PARCHMENT[2] - random.randint(5, 20)))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    # Add subtle coffee stain
    for _ in range(8):
        cx = random.randint(200, w-200)
        cy = random.randint(200, h-200)
        rx = random.randint(100, 300)
        ry = random.randint(80, 250)
        stain_color = (AGED_PAPER[0]-15, AGED_PAPER[1]-15, AGED_PAPER[2]-10)
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=stain_color)
    # Rounded aged border
    draw.rectangle([0, 0, w-1, 30], fill=PARCHMENT)
    draw.rectangle([0, h-30, w-1, h-1], fill=PARCHMENT)
    draw.rectangle([0, 0, 30, h-1], fill=PARCHMENT)
    draw.rectangle([w-30, 0, w-1, h-1], fill=PARCHMENT)
    return img


def add_ornate_border(draw, w, h, margin=80, color=DARK_INK):
    """Draw a decorative Victorian-style border."""
    # Outer rectangle
    draw.rectangle([margin, margin, w-margin, h-margin], outline=color, width=4)
    # Inner rectangle
    inner = margin + 20
    draw.rectangle([inner, inner, w-inner, h-inner], outline=color, width=2)
    # Corner flourishes
    corners = [(margin, margin), (w-margin, margin), (margin, h-margin), (w-margin, h-margin)]
    for cx, cy in corners:
        draw.ellipse([cx-15, cy-15, cx+15, cy+15], outline=color, width=2)
        draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=color)
    # Side diamonds
    for i in range(1, 6):
        y = margin + i * (h - 2*margin) // 6
        draw.polygon([(margin-12, y), (margin, y-8), (margin+12, y), (margin, y+8)], outline=color, width=1)
        draw.polygon([(w-margin-12, y), (w-margin, y-8), (w-margin+12, y), (w-margin, y+8)], outline=color, width=1)


def draw_rose(draw, cx, cy, size, color=ROSE_RED, leaves=True):
    """Draw a stylized vintage rose."""
    # Petals (concentric circles with rotation effect)
    for i in range(7):
        angle = i * (360/7)
        rad = math.radians(angle)
        px = cx + int(size * 0.4 * math.cos(rad))
        py = cy + int(size * 0.4 * math.sin(rad))
        r = int(size * 0.5)
        draw.ellipse([px-r, py-r, px+r, py+r], outline=color, width=2)
    # Center
    draw.ellipse([cx-size//3, cy-size//3, cx+size//3, cy+size//3], fill=ROSE_PINK, outline=color, width=2)
    draw.ellipse([cx-size//6, cy-size//6, cx+size//6, cy+size//6], fill=color)
    # Leaves
    if leaves:
        for side in [-1, 1]:
            lx = cx + side * size
            ly = cy + size//2
            points = [(lx, ly), (lx + side*size//2, ly - size//3), (lx + side*size, ly)]
            draw.polygon(points, fill=FERN_GREEN, outline=FERN_DARK, width=2)
            # Leaf veins
            draw.line([(lx, ly), (lx + side*size//2, ly - size//6)], fill=FERN_DARK, width=1)


def draw_fern_frond(draw, sx, sy, length, angle=0, color=FERN_GREEN, dark=FERN_DARK):
    """Draw a fern frond."""
    rad = math.radians(angle)
    ex = sx + int(length * math.cos(rad))
    ey = sy + int(length * math.sin(rad))
    # Main stem
    draw.line([(sx, sy), (ex, ey)], fill=dark, width=3)
    # Pinnae (side leaves)
    num_pinnae = 12
    for i in range(num_pinnae):
        t = (i + 1) / (num_pinnae + 1)
        px = int(sx + t * (ex - sx))
        py = int(sy + t * (ey - sy))
        pinna_len = int(length * 0.3 * (1 - abs(2*t - 1)))
        for side_angle in [angle - 60, angle + 60]:
            prad = math.radians(side_angle)
            pex = px + int(pinna_len * math.cos(prad))
            pey = py + int(pinna_len * math.sin(prad))
            draw.line([(px, py), (pex, pey)], fill=color, width=2)
            # Smaller sub-pinnae
            for j in range(3):
                st = (j + 1) / 4
                spx = int(px + st * (pex - px))
                spy = int(py + st * (pey - py))
                draw.ellipse([spx-4, spy-4, spx+4, spy+4], fill=color)


def draw_butterfly(draw, cx, cy, size, color1=SEPIA, color2=GOLD):
    """Draw a vintage butterfly specimen."""
    # Body
    draw.line([(cx, cy-size//2), (cx, cy+size//2)], fill=DARK_INK, width=3)
    # Head
    draw.ellipse([cx-5, cy-size//2-5, cx+5, cy-size//2+5], fill=DARK_INK)
    # Antennae
    draw.line([(cx, cy-size//2), (cx-size//3, cy-size)], fill=DARK_INK, width=2)
    draw.line([(cx, cy-size//2), (cx+size//3, cy-size)], fill=DARK_INK, width=2)
    # Wings
    for side in [-1, 1]:
        # Upper wing
        points = [
            (cx, cy - size//4),
            (cx + side * size, cy - size//2),
            (cx + side * size*3//4, cy),
            (cx, cy)
        ]
        draw.polygon(points, fill=color1, outline=DARK_INK, width=2)
        # Wing spots
        draw.ellipse([cx + side*size//2, cy-size//3, cx + side*size//2+15, cy-size//3+15], fill=color2)
        # Lower wing
        points = [
            (cx, cy),
            (cx + side * size*3//4, cy),
            (cx + side * size*5//8, cy + size//2),
            (cx, cy + size//4)
        ]
        draw.polygon(points, fill=color2, outline=DARK_INK, width=2)


def draw_wax_seal(draw, cx, cy, size, color=WAX_RED):
    """Draw a wax seal with ribbon."""
    # Seal circle
    draw.ellipse([cx-size, cy-size, cx+size, cy+size], fill=color)
    draw.ellipse([cx-size+8, cy-size+8, cx+size-8, cy+size-8], outline=(120, 20, 20), width=2)
    # Inner design - stylized letter
    draw.ellipse([cx-size//2, cy-size//2, cx+size//2, cy+size//2], outline=(120, 20, 20), width=2)
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", size)
    except:
        font = ImageFont.load_default()
    draw.text((cx-size//4, cy-size//3), "V", fill=(120, 20, 20), font=font)
    # Ribbon tails
    for dx in [-size//2, size//2]:
        points = [
            (cx+dx, cy+size),
            (cx+dx-size//3, cy+size+size),
            (cx+dx+size//3, cy+size+size),
        ]
        draw.polygon(points, fill=(180, 40, 40))


def add_vintage_text(draw, text, cx, cy, size, color=DARK_INK, center=True):
    """Draw vintage-style text."""
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", size)
    except:
        font = ImageFont.load_default()
    if center:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        cx = cx - tw // 2
    draw.text((cx, cy), text, fill=color, font=font)


def add_title_banner(draw, text, y, w, color=DARK_INK):
    """Draw a decorative title banner."""
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    # Banner shape
    bx1 = (w - tw) // 2 - 80
    bx2 = (w + tw) // 2 + 80
    draw.rectangle([bx1, y, bx2, y+100], fill=CREAM, outline=color, width=3)
    # Decorative ends
    draw.polygon([(bx1-40, y+50), (bx1, y+20), (bx1, y+80)], fill=CREAM, outline=color)
    draw.polygon([(bx2+40, y+50), (bx2, y+20), (bx2, y+80)], fill=CREAM, outline=color)
    draw.text(((w - tw)//2, y+15), text, fill=color, font=font)


def draw_vintage_key(draw, cx, cy, size, color=BROWN):
    """Draw a decorative vintage key."""
    # Key head (oval/bow)
    draw.ellipse([cx-size, cy-size, cx+size, cy+size//2], outline=color, width=3)
    draw.ellipse([cx-size+15, cy-size+15, cx+size-15, cy+size//2-15], outline=color, width=2)
    # Shaft
    shaft_top = cy + size//2
    shaft_bottom = cy + size * 2
    draw.line([(cx, shaft_top), (cx, shaft_bottom)], fill=color, width=4)
    # Bit (teeth)
    draw.line([(cx, shaft_bottom), (cx+size//2, shaft_bottom)], fill=color, width=3)
    draw.line([(cx, shaft_bottom-size//3), (cx+size//3, shaft_bottom-size//3)], fill=color, width=3)
    draw.line([(cx+size//3, shaft_bottom-size//3), (cx+size//3, shaft_bottom)], fill=color, width=2)


def draw_postage_stamp(draw, x, y, w, h, value, color=SEPIA):
    """Draw a vintage postage stamp."""
    # Perforated edges
    draw.rectangle([x, y, x+w, y+h], fill=CREAM, outline=color, width=2)
    # Perforations (small ticks along edges)
    for i in range(0, w, 12):
        draw.line([(x+i, y-4), (x+i, y+4)], fill=color, width=2)
        draw.line([(x+i, y+h-4), (x+i, y+h+4)], fill=color, width=2)
    for i in range(0, h, 12):
        draw.line([(x-4, y+i), (x+4, y+i)], fill=color, width=2)
        draw.line([(x+w-4, y+i), (x+w+4, y+i)], fill=color, width=2)
    # Inner frame
    draw.rectangle([x+20, y+20, x+w-20, y+h-20], outline=color, width=1)
    # Profile silhouette (simplified)
    profile_cx = x + w//2
    profile_cy = y + h//2 - 20
    draw.ellipse([profile_cx-40, profile_cy-50, profile_cx+40, profile_cy+30], fill=color)
    # Value text
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()
    draw.text((x + w//2 - 20, y + h - 55), value, fill=color, font=font)


# ============================================================
# PAGE 1: Botanical Rose
# ============================================================
def page_01_rose():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Rosa Centifolia", 150, WIDTH)
    # Main rose
    draw_rose(draw, WIDTH//2, 1000, 280)
    # Secondary smaller roses
    draw_rose(draw, 600, 1800, 140, color=(140, 80, 80))
    draw_rose(draw, 1880, 1900, 160, color=(170, 80, 90))
    # Stems and leaves
    draw.line([(WIDTH//2, 1280), (WIDTH//2, 2200)], fill=FERN_DARK, width=3)
    draw.line([(600, 1940), (500, 2300)], fill=FERN_DARK, width=2)
    draw.line([(1880, 2060), (1950, 2400)], fill=FERN_DARK, width=2)
    # Leaf decorations
    for i in range(5):
        y = 2300 + i * 160
        lx = WIDTH//2 + (100 if i % 2 == 0 else -100)
        draw_fern_frond(draw, WIDTH//2, y, 120, angle=90 if i % 2 == 0 else -90, color=FERN_GREEN)
    # Label
    try:
        small_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48)
    except:
        small_font = ImageFont.load_default()
    draw.text((WIDTH//2 - 250, HEIGHT - 300), "Plate I — Rosa Centifolia", fill=SEPIA, font=small_font)
    return img


# ============================================================
# PAGE 2: Fern Specimen
# ============================================================
def page_02_fern():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Filix Mas", 150, WIDTH)
    # Multiple fern fronds
    draw_fern_frond(draw, 800, 400, 800, angle=75, color=FERN_GREEN, dark=FERN_DARK)
    draw_fern_frond(draw, 1240, 500, 750, angle=90, color=FERN_GREEN, dark=FERN_DARK)
    draw_fern_frond(draw, 1680, 600, 700, angle=100, color=(90, 120, 70), dark=(60, 80, 45))
    # Spore detail box
    draw.rectangle([300, 2600, 1000, 3200], outline=FERN_DARK, width=2)
    draw.text((420, 2620), "Sori Detail (x40)", fill=FERN_DARK, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 40))
    # Draw spore clusters
    for _ in range(20):
        sx = random.randint(320, 980)
        sy = random.randint(2700, 3180)
        r = random.randint(8, 18)
        draw.ellipse([sx-r, sy-r, sx+r, sy+r], outline=FERN_DARK, width=1)
        draw.arc([sx-r-4, sy-r-4, sx+r+4, sy+r+4], 0, 180, fill=FERN_GREEN, width=2)
    # Label
    draw.text((WIDTH//2-250, HEIGHT-300), "Plate II — Aspidium Filix-mas", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 3: Old World Map Fragment
# ============================================================
def page_03_map():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Carta Marina", 150, WIDTH)
    # Grid lines (latitude/longitude)
    for i in range(1, 8):
        y = 350 + i * 400
        draw.line([(120, y), (WIDTH-120, y)], fill=(180, 160, 130), width=1)
    for i in range(1, 5):
        x = 350 + i * 450
        draw.line([(x, 350), (x, HEIGHT-350)], fill=(180, 160, 130), width=1)
    # Compass rose (center)
    cx, cy = WIDTH//2, 1800
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        length = 200 if angle % 90 == 0 else 140
        ex = cx + int(length * math.cos(rad))
        ey = cy + int(length * math.sin(rad))
        draw.line([(cx, cy), (ex, ey)], fill=NAVY, width=2 if angle % 90 == 0 else 1)
    # N marker
    draw.text((cx-10, cy-250), "N", fill=NAVY, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 60))
    # Simplified coastline
    coast_points = [
        (200, 500), (400, 600), (600, 480), (900, 700), (1200, 550),
        (1500, 650), (1800, 500), (2100, 600), (2300, 450)
    ]
    for i in range(len(coast_points)-1):
        draw.line([coast_points[i], coast_points[i+1]], fill=SEPIA, width=3)
    coast2 = [
        (300, 2200), (500, 2400), (800, 2300), (1100, 2500),
        (1400, 2350), (1700, 2550), (2000, 2400), (2200, 2600)
    ]
    for i in range(len(coast2)-1):
        draw.line([coast2[i], coast2[i+1]], fill=SEPIA, width=3)
    # Place names
    for name, x, y in [("Londinium", 500, 800), ("Roma", 1400, 1200), ("Constantinopolis", 1800, 1600)]:
        draw.text((x, y), name, fill=DARK_INK, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 44))
    # Sea monster
    mx, my = 700, 1400
    draw.arc([mx-80, my-40, mx+80, my+40], 0, 180, fill=NAVY, width=3)
    draw.arc([mx-80, my, mx+80, my+80], 180, 360, fill=NAVY, width=3)
    draw.line([(mx+80, my+20), (mx+120, my+10)], fill=NAVY, width=2)
    draw.line([(mx+120, my+10), (mx+140, my+30)], fill=NAVY, width=2)
    # Label
    draw.text((WIDTH//2-250, HEIGHT-300), "Plate III — Carta Marina Fragment", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 4: Vintage Postage Stamps
# ============================================================
def page_04_stamps():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Timbres Postaux", 150, WIDTH)
    # 6 stamps in a 3x2 grid
    stamps = [
        ("1d", (250, 400)), ("2d", (850, 400)), ("3d", (1450, 400)),
        ("5d", (250, 1100)), ("10d", (850, 1100)), ("1s", (1450, 1100)),
    ]
    colors = [SEPIA, NAVY, ROSE_RED, FERN_GREEN, BROWN, GOLD_DARK]
    for idx, (val, (x, y)) in enumerate(stamps):
        draw_postage_stamp(draw, x, y, 500, 550, val, colors[idx])
    # Stamp collection label at bottom
    draw.rectangle([300, 1900, WIDTH-300, 3200], outline=SEPIA, width=2)
    draw.text((400, 1950), "Collection Notes", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 50))
    # Ruled lines for writing
    for y_line in range(2100, 3100, 80):
        draw.line([(350, y_line), (WIDTH-350, y_line)], fill=BROWN_LIGHT, width=1)
    # Label
    draw.text((WIDTH//2-300, HEIGHT-300), "Plate IV — Victorian Postage Stamps", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 5: Handwritten Letter Fragment
# ============================================================
def page_05_letter():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    # Header - decorative monogram
    draw.ellipse([WIDTH//2-80, 150, WIDTH//2+80, 310], outline=DARK_INK, width=3)
    try:
        font_init = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 100)
    except:
        font_init = ImageFont.load_default()
    draw.text((WIDTH//2-30, 165), "E", fill=DARK_INK, font=font_init)
    # Date line
    draw.text((300, 450), "March 14th, 1887", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 52))
    # Simulated cursive text lines
    lines = [
        "My Dearest Elizabeth,",
        "",
        "I write to you from the gardens of",
        "Hartfield, where the roses bloom in",
        "profusion and the air carries the",
        "sweetest fragrance of jasmine & rose.",
        "",
        "It has been three months since our",
        "last correspondence, and I confess",
        "that each day apart feels longer than",
        "the last. The botanical specimens I",
        "collected during our walk through the",
        "conservatory have been pressed and",
        "mounted with great care.",
        "",
        "I enclose herein a small illustration",
        "of the Rosa Centifolia that so captured",
        "your attention. It is my sincere hope",
        "that this find you in good health &",
        "spirits.",
        "",
        "With the warmest regards,",
        "Your devoted friend,",
        "E.M.",
    ]
    try:
        cursive_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 46)
    except:
        cursive_font = ImageFont.load_default()
    y_pos = 650
    for line in lines:
        # Simulate ink variation
        brightness = random.randint(-10, 10)
        ink_color = (max(0, DARK_INK[0]+brightness), max(0, DARK_INK[1]+brightness), max(0, DARK_INK[2]+brightness))
        draw.text((300, y_pos), line, fill=ink_color, font=cursive_font)
        y_pos += 70
    # Wax seal at bottom
    draw_wax_seal(draw, WIDTH//2, 3200, 80)
    # Label
    draw.text((WIDTH//2-250, HEIGHT-200), "Plate V — Epistolary Fragment", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 6: Victorian Calling Card
# ============================================================
def page_06_calling_card():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Carte de Visite", 150, WIDTH)
    # Multiple calling cards
    cards = [
        (400, 500, "Lady Ashworth", "42 Grosvenor Square"),
        (1400, 500, "Miss E. Harrington", "The Laurels, Bath"),
        (400, 1400, "Capt. J. Blackwood", "Royal Navy (Ret.)"),
        (1400, 1400, "Dr. A. Pemberton", "Fellow, Royal Society"),
    ]
    bg_colors = [(255, 250, 240), (245, 240, 230), (250, 245, 235), (240, 235, 225)]
    try:
        name_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 44)
        sub_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 32)
    except:
        name_font = sub_font = ImageFont.load_default()
    for idx, (cx, cy, name, subtitle) in enumerate(cards):
        cw, ch = 600, 700
        # Card background
        draw.rectangle([cx, cy, cx+cw, cy+ch], fill=bg_colors[idx], outline=DARK_INK, width=3)
        draw.rectangle([cx+15, cy+15, cx+cw-15, cy+ch-15], outline=SEPIA, width=1)
        # Corner decorations
        for corner_x, corner_y in [(cx+30, cy+30), (cx+cw-30, cy+30), (cx+30, cy+ch-30), (cx+cw-30, cy+ch-30)]:
            draw.ellipse([corner_x-8, corner_y-8, corner_x+8, corner_y+8], fill=DARK_INK)
        # Name
        bbox = draw.textbbox((0, 0), name, font=name_font)
        tw = bbox[2] - bbox[0]
        draw.text((cx + (cw-tw)//2, cy + 200), name, fill=DARK_INK, font=name_font)
        # Decorative line
        draw.line([(cx+80, cy+300), (cx+cw-80, cy+300)], fill=GOLD, width=2)
        # Subtitle
        bbox2 = draw.textbbox((0, 0), subtitle, font=sub_font)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((cx + (cw-tw2)//2, cy + 350), subtitle, fill=SEPIA, font=sub_font)
        # Floral decoration at top
        draw_rose(draw, cx+cw//2, cy+100, 40, color=GOLD, leaves=False)
    # Bottom section - blank card for journaling
    draw.rectangle([400, 2400, WIDTH-400, 3200], outline=SEPIA, width=2)
    draw.text((500, 2450), "Notes & Reflections", fill=SEPIA, font=name_font)
    for y_line in range(2600, 3150, 70):
        draw.line([(450, y_line), (WIDTH-450, y_line)], fill=BROWN_LIGHT, width=1)
    # Label
    draw.text((WIDTH//2-300, HEIGHT-200), "Plate VI — Cartes de Visite", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 7: Antique Keys
# ============================================================
def page_07_keys():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Ancient Keys", 150, WIDTH)
    # Draw 4 different keys
    draw_vintage_key(draw, 600, 800, 120, color=BROWN)
    draw_vintage_key(draw, 1800, 700, 150, color=DARK_INK)
    draw_vintage_key(draw, 700, 2000, 100, color=SEPIA)
    draw_vintage_key(draw, 1700, 1900, 130, color=(80, 60, 30))
    # Key ring at top
    draw.ellipse([WIDTH//2-150, 2400, WIDTH//2+150, 2700], outline=DARK_INK, width=4)
    draw.arc([WIDTH//2-150, 2400, WIDTH//2+150, 2700], 200, 340, fill=DARK_INK, width=3)
    # Key labels
    try:
        label_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 36)
    except:
        label_font = ImageFont.load_default()
    draw.text((500, 1200), "Skeleton Key, c. 1780", fill=SEPIA, font=label_font)
    draw.text((1650, 1100), "Church Door Key, c. 1650", fill=SEPIA, font=label_font)
    draw.text((500, 2400), "Cabinet Key, c. 1820", fill=SEPIA, font=label_font)
    draw.text((1550, 2300), "Desk Key, c. 1750", fill=SEPIA, font=label_font)
    # Decorative chain links
    for y in range(2800, 3200, 60):
        draw.ellipse([WIDTH//2-20, y, WIDTH//2+20, y+40], outline=DARK_INK, width=2)
    # Label
    draw.text((WIDTH//2-250, HEIGHT-200), "Plate VII — Antique Keys", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 8: Butterfly Specimen
# ============================================================
def page_08_butterfly():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Lepidoptera", 150, WIDTH)
    # Main large butterfly
    draw_butterfly(draw, WIDTH//2, 900, 350, color1=SEPIA, color2=GOLD)
    # Smaller specimens
    draw_butterfly(draw, 600, 1500, 180, color1=(100, 70, 120), color2=GOLD_DARK)
    draw_butterfly(draw, 1880, 1600, 150, color1=FERN_GREEN, color2=ROSE_PINK)
    # Pins (entomological style)
    draw.line([(WIDTH//2, 550), (WIDTH//2, 700)], fill=(180, 180, 180), width=3)
    draw.line([(600, 1320), (600, 1400)], fill=(180, 180, 180), width=2)
    draw.line([(1880, 1440), (1880, 1520)], fill=(180, 180, 180), width=2)
    # Specimen labels
    try:
        label_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 36)
    except:
        label_font = ImageFont.load_default()
    draw.text((WIDTH//2-200, 1400), "Papilio machaon", fill=DARK_INK, font=label_font)
    draw.text((420, 1800), "Vanessa atalanta", fill=DARK_INK, font=label_font)
    draw.text((1700, 1900), "Aglais io", fill=DARK_INK, font=label_font)
    # Collection notes area
    draw.rectangle([300, 2200, WIDTH-300, 3200], outline=SEPIA, width=2)
    draw.text((400, 2250), "Specimen Notes", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 48))
    for y_line in range(2400, 3100, 70):
        draw.line([(350, y_line), (WIDTH-350, y_line)], fill=BROWN_LIGHT, width=1)
    # Label
    draw.text((WIDTH//2-300, HEIGHT-200), "Plate VIII — Lepidoptera Collection", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 9: Apothecary Labels
# ============================================================
def page_09_apothecary():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Apothecary", 150, WIDTH)
    # Apothecary jar labels in a grid
    labels = [
        ("LAVANDULA", "Lavender\nEssential Oil", SEPIA),
        ("ROSA DAMASCENA", "Rose\nWater", ROSE_RED),
        ("CINNAMOMUM", "Cinnamon\nBark Extract", BROWN),
        ("ARTEMISIA", "Wormwood\nTincture", FERN_GREEN),
        ("HYDRARGYRUM", "Calomel\nPowder", NAVY),
        ("CAMPHORA", "Camphor\nResin", GOLD_DARK),
    ]
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 36)
        desc_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Oblique.ttf", 28)
    except:
        title_font = desc_font = ImageFont.load_default()
    positions = [
        (200, 500), (900, 500), (1600, 500),
        (200, 1600), (900, 1600), (1600, 1600),
    ]
    for idx, ((px, py), (name, desc, color)) in enumerate(zip(positions, labels)):
        lw, lh = 550, 700
        # Label background
        draw.rectangle([px, py, px+lw, py+lh], fill=CREAM, outline=color, width=3)
        draw.rectangle([px+12, py+12, px+lw-12, py+lh-12], outline=color, width=1)
        # Decorative corners
        for cx, cy in [(px+25, py+25), (px+lw-25, py+25), (px+25, py+lh-25), (px+lw-25, py+lh-25)]:
            draw.line([(cx, cy), (cx+20, cy)], fill=color, width=2)
            draw.line([(cx, cy), (cx, cy+20)], fill=color, width=2)
        # Title
        bbox = draw.textbbox((0, 0), name, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text((px + (lw-tw)//2, py + 100), name, fill=color, font=title_font)
        # Separator
        draw.line([(px+60, py+160), (px+lw-60, py+160)], fill=color, width=2)
        # Mortar & pestle symbol (simplified)
        mx, my = px + lw//2, py + 280
        draw.ellipse([mx-50, my-30, mx+50, my+30], outline=color, width=2)
        draw.line([(mx+30, my-50), (mx+60, my-80)], fill=color, width=3)
        # Description
        for i, line in enumerate(desc.split('\n')):
            bbox = draw.textbbox((0, 0), line, font=desc_font)
            tw2 = bbox[2] - bbox[0]
            draw.text((px + (lw-tw2)//2, py + 400 + i*50), line, fill=DARK_INK, font=desc_font)
        # Dosage line
        draw.text((px+30, py+lh-80), f"Dr. Pemberton, Apothecary", fill=BROWN_LIGHT, font=desc_font)
    # Label
    draw.text((WIDTH//2-300, HEIGHT-200), "Plate IX — Apothecary Labels", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# PAGE 10: Wax Seal & Ribbon
# ============================================================
def page_10_wax_seal():
    img = make_parchment(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    add_ornate_border(draw, WIDTH, HEIGHT)
    add_title_banner(draw, "Seals & Ribbons", 150, WIDTH)
    # Large wax seal centerpiece
    draw_wax_seal(draw, WIDTH//2, 1100, 250)
    # Decorative text around seal
    try:
        seal_font = ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 40)
    except:
        seal_font = ImageFont.load_default()
    draw.text((WIDTH//2-180, 1450), "Correspondence Seal", fill=DARK_INK, font=seal_font)
    # Ribbon swatches
    ribbon_colors = [ROSE_RED, NAVY, FERN_GREEN, GOLD_DARK, BROWN]
    ribbon_names = ["Crimson Silk", "Navy Moiré", "Evergreen Grosgrain", "Gold Satin", "Velvet Brown"]
    for i, (color, name) in enumerate(zip(ribbon_colors, ribbon_names)):
        rx = 350 + (i % 3) * 600
        ry = 1800 + (i // 3) * 600
        # Ribbon body
        for fold in range(30):
            offset = fold * 15
            brightness = 20 if fold % 2 == 0 else -20
            rc = tuple(max(0, min(255, c + brightness)) for c in color)
            draw.rectangle([rx, ry+offset, rx+450, ry+offset+15], fill=rc)
        # Ribbon ends (V-cut)
        draw.polygon([(rx+450, ry), (rx+550, ry+15), (rx+450, ry+30)], fill=color)
        draw.polygon([(rx-100, ry+450), (rx, ry+465), (rx-100, ry+480)], fill=color)
        # Label
        draw.text((rx+50, ry+490), name, fill=color, font=seal_font)
    # Smaller seals collection
    small_seals = [(500, 2800, 70), (800, 2900, 60), (1100, 2850, 80),
                   (1400, 2900, 65), (1700, 2800, 75), (2000, 2850, 55)]
    for sx, sy, sr in small_seals:
        draw_wax_seal(draw, sx, sy, sr)
    # Label
    draw.text((WIDTH//2-250, HEIGHT-200), "Plate X — Seals & Ribbons", fill=SEPIA, font=ImageFont.truetype("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf", 48))
    return img


# ============================================================
# Generate all pages and save
# ============================================================
print("Generating 10 Victorian Botanical Ephemera pages...")
generators = [
    ("01_Rosa_Centifolia", page_01_rose),
    ("02_Filix_Mas", page_02_fern),
    ("03_Carta_Marina", page_03_map),
    ("04_Timbres_Postaux", page_04_stamps),
    ("05_Epistolary_Fragment", page_05_letter),
    ("06_Cartes_de_Visite", page_06_calling_card),
    ("07_Ancient_Keys", page_07_keys),
    ("08_Lepidoptera", page_08_butterfly),
    ("09_Apothecary", page_09_apothecary),
    ("10_Seals_Ribbons", page_10_wax_seal),
]

images = []
for name, gen_func in generators:
    print(f"  Generating: {name}...")
    random.seed(42 + generators.index((name, gen_func)))
    img = gen_func()
    filepath = os.path.join(IMAGES_DIR, f"{name}.png")
    img.save(filepath, "PNG", dpi=(DPI, DPI))
    images.append(img)
    print(f"    Saved: {filepath} ({img.size[0]}x{img.size[1]})")

# Compile PDF
print("\nCompiling PDF...")
images[0].save(
    PDF_PATH,
    "PDF",
    resolution=DPI,
    save_all=True,
    append_images=images[1:],
)
print(f"  PDF saved: {PDF_PATH}")

# Etsy Listing Info
listing_info = """TITLE: Victorian Botanical Ephemera - Junk Journal Pages - Digital Download - Printable Vintage Decorative Paper - A4 300 DPI - 10 Pages

DESCRIPTION:
Step back in time with this exquisite collection of 10 Victorian Botanical Ephemera pages, perfect for your junk journaling, scrapbooking, and paper crafting projects!

✿ WHAT YOU GET ✿
- 10 high-quality printable pages in DIN A4 format (2480 x 3508 pixels)
- 300 DPI resolution for crisp, professional printing
- Instant digital download — no physical item will be shipped

✿ INCLUDED PAGES ✿
1. Rosa Centifolia — Botanical Rose Illustration
2. Filix Mas — Fern Specimen Plate
3. Carta Marina — Old World Map Fragment
4. Timbres Postaux — Vintage Postage Stamps
5. Epistolary Fragment — Aged Handwritten Letter
6. Cartes de Visite — Victorian Calling Cards
7. Ancient Keys — Antique Key Illustrations
8. Lepidoptera — Butterfly Specimen Collection
9. Apothecary — Victorian Pharmacy Labels
10. Seals & Ribbons — Wax Seals and Ribbon Swatches

✿ PERFECT FOR ✿
- Junk journals and art journals
- Scrapbooking and collage
- Card making and mixed media
- Wedding and event stationery
- Home décor prints
- Planner and bullet journal decoration

✿ PRINTING TIPS ✿
- Print on high-quality paper or cardstock (200gsm+ recommended)
- Use "Actual Size" or 100% scale when printing
- For best results, use a photo-quality printer with original ink cartridges

Please note: This is a DIGITAL product. No physical item will be shipped. Due to the nature of digital downloads, refunds are not available after purchase.

TAGS: printablenotes, junkjournal, vintageprintable, ephemera, botanticalvintage
"""

with open(LISTING_PATH, 'w') as f:
    f.write(listing_info)
print(f"  Listing saved: {LISTING_PATH}")

# Verify quality gate
print("\n=== QUALITY GATE ===")
all_ok = len(images) == 10
for img in images:
    ok = img.size == (2480, 3508)
    all_ok = all_ok and ok
    print(f"  {img.size[0]}x{img.size[1]} {'OK' if ok else 'FAIL'}")
print(f"\nQuality gate: {'PASS' if all_ok else 'FAIL'}")
print(f"\nDone! Product folder: {OUTPUT_DIR}/")