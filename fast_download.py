#!/usr/bin/env python3
"""Fast parallel Junk Journal image generator using Pollinations.ai.
Uses 2 workers with staggered delays to maximize throughput.
"""

import urllib.request
import urllib.parse
import time
import sys
import json
import os
import hashlib
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
from generate_junk_journals import THEMES, create_pdf_from_images, generate_etsy_listing

BASE_DIR = Path(__file__).parent
DATE_STR = "2026-04-25"

def download_image(prompt, output_path, seed, max_retries=2):
    """Download a single image from Pollinations.ai."""
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
                    time.sleep(8 + attempt * 10)
                continue
            
            with open(output_path, 'wb') as f:
                f.write(data)
            try:
                img = Image.open(output_path)
                img.verify()
                return True
            except Exception:
                Path(output_path).unlink(missing_ok=True)
                if attempt < max_retries - 1:
                    time.sleep(8 + attempt * 10)
                continue
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"    429 rate limit, waiting 90s...", flush=True)
                time.sleep(90)
            elif attempt < max_retries - 1:
                time.sleep(8)
            continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(8)
            continue
    
    return False


def process_all_packages():
    """Process all packages with parallel workers."""
    # Collect all tasks
    tasks = []
    for i, theme in enumerate(THEMES):
        theme_slug = theme["name"].lower().replace(" ", "_")
        pkg_dir = BASE_DIR / f"{DATE_STR}_{theme_slug}"
        img_dir = pkg_dir / "Original_Bilder"
        img_dir.mkdir(parents=True, exist_ok=True)
        
        for j, prompt in enumerate(theme["prompts"][:20]):  # 20 per package
            img_path = img_dir / f"{theme_slug}_{j+1:02d}.jpg"
            
            # Skip if already exists and valid
            if img_path.exists() and img_path.stat().st_size > 5000:
                try:
                    img = Image.open(str(img_path))
                    img.verify()
                    continue  # Already done
                except Exception:
                    img_path.unlink(missing_ok=True)
            
            seed = 42 + j + (i * 100)
            tasks.append((i, j, prompt, str(img_path), seed, theme))
    
    print(f"Total images to download: {len(tasks)}", flush=True)
    
    # Download with 2 workers, 3s stagger between submissions
    completed = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {}
        for task_idx, (pkg_idx, img_idx, prompt, path, seed, theme) in enumerate(tasks):
            future = executor.submit(download_image, prompt, path, seed)
            futures[future] = (pkg_idx, img_idx, prompt, path)
            if task_idx % 2 == 0:  # Stagger starts
                time.sleep(3)
        
        for future in as_completed(futures):
            pkg_idx, img_idx, prompt, path = futures[future]
            success = future.result()
            if success:
                completed += 1
            else:
                failed += 1
            total_done = completed + failed
            if total_done % 10 == 0:
                print(f"  Progress: {total_done}/{len(tasks)} ({completed} OK, {failed} failed)", flush=True)
    
    print(f"\nDownload complete: {completed} OK, {failed} failed out of {len(tasks)}", flush=True)
    
    # Now create PDFs and listings for each package
    print("\nCreating PDFs and listings...", flush=True)
    results = []
    for i, theme in enumerate(THEMES):
        theme_slug = theme["name"].lower().replace(" ", "_")
        pkg_dir = BASE_DIR / f"{DATE_STR}_{theme_slug}"
        img_dir = pkg_dir / "Original_Bilder"
        
        # Collect generated images
        generated = sorted(img_dir.glob("*.jpg"))
        generated = [p for p in generated if p.stat().st_size > 5000]
        
        # PDF
        pdf_path = pkg_dir / f"{theme_slug}_junk_journal.pdf"
        if generated:
            print(f"  Creating PDF for {theme['name']}...", flush=True)
            create_pdf_from_images(generated, str(pdf_path), theme["name"])
        
        # Etsy listing
        listing = generate_etsy_listing(theme)
        listing_path = pkg_dir / "etsy_listing.json"
        with open(listing_path, 'w') as f:
            json.dump(listing, f, indent=2)
        
        # README
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
        
        results.append({"theme": theme["name"], "generated": len(generated), "total": 20})
        print(f"  {theme['name']}: {len(generated)}/20 images", flush=True)
    
    # Summary
    print(f"\n{'='*60}", flush=True)
    print("FINAL SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    for r in results:
        print(f"  {r['theme']}: {r['generated']}/{r['total']}", flush=True)
    total = sum(r["generated"] for r in results)
    print(f"\n  Total: {total} images across {len(results)} packages", flush=True)


if __name__ == "__main__":
    process_all_packages()