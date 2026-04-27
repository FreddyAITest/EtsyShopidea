from PIL import Image, ImageDraw, ImageFont
import os

base = "/home/elias/.paperclip/instances/default/projects/a3a70364-1109-4bd8-9d8b-a49c7f8407f2/3f45e10a-c0e7-4bd5-adeb-1282bf82b9a2/EtsyShopidea"

themes = [
    "victorian_botanical_ephemera",
    "dark_academia_gothic", 
    "vintage_steampunk_apothecary",
    "shabby_chic_romantic",
    "rustic_nature_woodland",
    "vintage_travel_adventure",
    "celestial_moon_stars",
    "french_provincial_cottage",
    "vintage_kitchen_recipe",
    "art_nouveau_belle_epoque",
]

for theme in themes:
    img_dir = os.path.join(base, theme)
    if not os.path.isdir(img_dir):
        print(f"Skipping {theme}: directory not found")
        continue
    
    images = sorted([f for f in os.listdir(img_dir) if f.endswith(".png")])
    if len(images) < 20:
        print(f"Skipping {theme}: only {len(images)} images")
        continue
    
    # Create thumbnail: 3000x2250 (high quality for Etsy)
    thumb_w, thumb_h = 3000, 2250
    thumb = Image.new("RGB", (thumb_w, thumb_h), (255, 255, 255))
    
    # Title bar at top (180px)
    title_h = 180
    title_bar = Image.new("RGB", (thumb_w, title_h), (60, 40, 30))
    
    # Grid: 4 cols x 5 rows below title
    grid_top = title_h + 20
    grid_area_h = thumb_h - grid_top - 20
    grid_area_w = thumb_w - 40
    
    cell_w = grid_area_w // 4
    cell_h = grid_area_h // 5
    
    for idx, img_file in enumerate(images[:20]):
        row = idx // 4
        col = idx % 4
        
        x = 20 + col * cell_w + 5
        y = grid_top + row * cell_h + 5
        w = cell_w - 10
        h = cell_h - 10
        
        img = Image.open(os.path.join(img_dir, img_file))
        img_ratio = img.width / img.height
        cell_ratio = w / h
        
        if img_ratio > cell_ratio:
            new_w = w
            new_h = int(w / img_ratio)
        else:
            new_h = h
            new_w = int(h * img_ratio)
        
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        
        paste_x = x + (w - new_w) // 2
        paste_y = y + (h - new_h) // 2
        
        thumb.paste(img_resized, (paste_x, paste_y))
    
    # Add title text
    draw = ImageDraw.Draw(title_bar)
    display_name = theme.replace("_", " ").title()
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 52)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), display_name, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (thumb_w - text_w) // 2
    draw.text((text_x, 60), display_name, fill=(255, 255, 255), font=font)
    
    thumb.paste(title_bar, (0, 0))
    
    # Save to product directory
    out_dir = os.path.join(base, "products", f"2026-04-27_{theme}")
    thumb.save(os.path.join(out_dir, "thumbnail.jpg"), "JPEG", quality=95)
    # Also save Etsy-optimized version (2000px wide)
    thumb_etsy = thumb.resize((2000, 1500), Image.LANCZOS)
    thumb_etsy.save(os.path.join(out_dir, "thumbnail_etsy.jpg"), "JPEG", quality=90)
    
    print(f"Created thumbnail for {theme}")

print("All thumbnails generated!")