#!/usr/bin/env python3
"""
Compress junk journal PDFs for Etsy upload.
Etsy limit: 20MB per file.
Strategy: Re-encode page images as JPEG at quality 85, embed in PDF.
This creates Etsy-ready files while maintaining print quality.
"""
import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import tempfile

base = "/home/elias/.paperclip/instances/default/projects/a3a70364-1109-4bd8-9d8b-a49c7f8407f2/3f45e10a-c0e7-4bd5-adeb-1282bf82b9a2/EtsyShopidea"
products_dir = os.path.join(base, "products")

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
    pkg_dir = os.path.join(products_dir, f"2026-04-27_{theme}")
    source_dir = os.path.join(base, theme)  # Original theme dir with PNGs
    
    # Get sorted list of PNGs
    png_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.png')])
    if len(png_files) < 20:
        print(f"SKIP {theme}: only {len(png_files)} PNGs")
        continue
    
    # Create compressed PDF using reportlab with JPEG-compressed images
    output_path = os.path.join(pkg_dir, "Product_Etsy.pdf")
    
    c = canvas.Canvas(output_path, pagesize=A4)
    page_w, page_h = A4  # 595.27 x 841.89 points
    
    for png_file in png_files[:20]:
        img_path = os.path.join(source_dir, png_file)
        img = Image.open(img_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Compress: resize to max 2000px height for Etsy download quality
        # (still excellent for home printing)
        max_height = 2000
        if img.height > max_height:
            ratio = max_height / img.height
            new_w = int(img.width * ratio)
            img = img.resize((new_w, max_height), Image.LANCZOS)
        
        # Determine JPEG quality to stay under 20MB total
        # With 20 pages at quality 80, each ~800KB = ~16MB total
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        
        # Use reportlab to place the image
        img_byte_count = buf.tell()
        buf.seek(0)
        
        # Save temp JPEG
        temp_jpg = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_jpg.name, format='JPEG', quality=80, optimize=True)
        temp_jpg.close()
        
        # Draw image to fill A4 page
        c.drawImage(temp_jpg.name, 0, 0, width=page_w, height=page_h, 
                     preserveAspectRatio=True, anchor='c')
        c.showPage()
        
        os.unlink(temp_jpg.name)
    
    c.save()
    
    # Check file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"{theme}: Etsy PDF = {size_mb:.1f}MB")
    
    # If still too large, reduce quality
    if size_mb > 20:
        print(f"  WARNING: {size_mb:.1f}MB exceeds 20MB limit - reducing quality")
        # Re-create with lower quality
        c = canvas.Canvas(output_path, pagesize=A4)
        for png_file in png_files[:20]:
            img_path = os.path.join(source_dir, png_file)
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            max_height = 1600  # Smaller
            if img.height > max_height:
                ratio = max_height / img.height
                new_w = int(img.width * ratio)
                img = img.resize((new_w, max_height), Image.LANCZOS)
            
            temp_jpg = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            img.save(temp_jpg.name, format='JPEG', quality=70, optimize=True)
            temp_jpg.close()
            
            c.drawImage(temp_jpg.name, 0, 0, width=page_w, height=page_h,
                        preserveAspectRatio=True, anchor='c')
            c.showPage()
            os.unlink(temp_jpg.name)
        
        c.save()
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  Reduced: {size_mb:.1f}MB")

print("\\nAll Etsy-ready PDFs generated!")