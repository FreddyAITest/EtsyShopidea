#!/usr/bin/env python3
"""Robust Junk Journal image generator using Pollinations.ai.
- 768x768 resolution (good balance of speed/quality)
- 5s delay between requests to avoid rate limiting
- 3 retries per image with backoff
- Sequential processing for reliability
"""

import urllib.request
import urllib.parse
import time
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from generate_junk_journals import THEMES, create_pdf_from_images, generate_etsy_listing

BASE_DIR = Path(__file__).parent
DATE_STR = "2026-04-25"

def download_image(prompt, output_path, seed, max_retries=3):
    """Download a single image from Pollinations.ai with retries."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&seed={seed}&nologo=true"
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read()
            
            if len(data) < 5000:
                if attempt < max_retries - 1:
                    time.sleep(10 + attempt * 5)
                continue
            
            # Save and verify
            with open(output_path, 'wb') as f:
                f.write(data)
            try:
                img = Image.open(output_path)
                img.verify()
                return True
            except Exception:
                Path(output_path).unlink(missing_ok=True)
                if attempt < max_retries - 1:
                    time.sleep(10 + attempt * 5)
                continue
                
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait = 60 + attempt * 30
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif attempt < max_retries - 1:
                time.sleep(10 + attempt * 5)
            continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(10 + attempt * 5)
            continue
    
    return False


def process_package(idx, theme):
    """Process a single package: download images, create PDF, create listing."""
    theme_slug = theme["name"].lower().replace(" ", "_")
    pkg_dir = BASE_DIR / f"{DATE_STR}_{theme_slug}"
    img_dir = pkg_dir / "Original_Bilder"
    img_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}", flush=True)
    print(f"Package {idx+1}/10: {theme['name']}", flush=True)
    print(f"{'='*60}", flush=True)
    
    generated = []
    prompts = theme["prompts"]
    
    for j, prompt in enumerate(prompts):
        img_path = img_dir / f"{theme_slug}_{j+1:02d}.jpg"
        
        # Skip if already exists and valid
        if img_path.exists() and img_path.stat().st_size > 5000:
            try:
                img = Image.open(str(img_path))
                img.verify()
                generated.append(img_path)
                print(f"  [{j+1:2d}/{len(prompts)}] SKIP (exists)", flush=True)
                continue
            except Exception:
                img_path.unlink(missing_ok=True)
        
        seed = 42 + j + (idx * 100)
        print(f"  [{j+1:2d}/{len(prompts)}] {prompt[:50]}...", flush=True)
        
        success = download_image(prompt, str(img_path), seed)
        if success:
            generated.append(img_path)
            print(f"  [{j+1:2d}/{len(prompts)}] ✓ Downloaded", flush=True)
        else:
            print(f"  [{j+1:2d}/{len(prompts)}] ✗ FAILED", flush=True)
        
        # Rate limit delay
        time.sleep(5)
    
    # Create PDF
    pdf_path = pkg_dir / f"{theme_slug}_junk_journal.pdf"
    if generated:
        print(f"  Creating PDF...", flush=True)
        create_pdf_from_images(generated, str(pdf_path), theme["name"])
    
    # Create Etsy listing
    listing = generate_etsy_listing(theme)
    listing_path = pkg_dir / "etsy_listing.json"
    with open(listing_path, 'w') as f:
        json.dump(listing, f, indent=2)
    
    # Create README
    readme_path = pkg_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(f"# {theme['name']} - Junk Journal Ephemera Pack\n\n")
        f.write(f"{theme['description']}\n\n")
        f.write(f"## Contents\n\n")
        f.write(f"- {len(generated)} unique AI-generated images\n")
        f.write(f"- PDF compilation (A4 format)\n")
        f.write(f"- Individual image files (768x768 JPG)\n")
        f.write(f"- Etsy listing metadata\n\n")
        f.write(f"## Files\n\n")
        f.write(f"- `Original_Bilder/` - Individual image files\n")
        f.write(f"- `{pdf_path.name}` - PDF compilation\n")
        f.write(f"- `etsy_listing.json` - Etsy listing metadata\n")
    
    print(f"  Package done: {len(generated)}/{len(prompts)} images", flush=True)
    return {"theme": theme["name"], "generated": len(generated), "total": len(prompts)}


def main():
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else len(THEMES)
    
    print("Junk Journal Package Generator", flush=True)
    print(f"Processing packages {start_idx+1} to {end_idx}", flush=True)
    
    results = []
    for i in range(start_idx, min(end_idx, len(THEMES))):
        result = process_package(i, THEMES[i])
        results.append(result)
    
    print(f"\n{'='*60}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    for r in results:
        print(f"  {r['theme']}: {r['generated']}/{r['total']}", flush=True)
    
    total = sum(r["generated"] for r in results)
    print(f"\n  Total: {total} images across {len(results)} packages", flush=True)


if __name__ == "__main__":
    main()