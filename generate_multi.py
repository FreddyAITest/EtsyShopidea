#!/usr/bin/env python3
"""
Junk Journal Image Generator - Multi-backend resilient version.
Uses Animagine XL 3.1 + cosxl HF Spaces with GPU quota management,
and Pollinations.ai as fallback (one-at-a-time).

Usage:
  python3 generate_multi.py                  # Generate all themes
  python3 generate_multi.py --theme 0         # Generate only theme 0
  python3 generate_multi.py --theme 0 --limit 5
  python3 generate_multi.py --check           # Check progress
  python3 generate_multi.py --pdfs-only      # Build PDFs from existing images
"""

import os
import sys
import json
import time
import shutil
import random
import argparse
from pathlib import Path
from datetime import date, datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

PROJECT_DIR = Path(__file__).parent.resolve()
DATE_PREFIX = f"{date.today().strftime('%Y-%m-%d')}_"
A4_W, A4_H = 2480, 3508
GEN_SIZE = 1024

# ---------------------------------------------------------------------------
# Backend configuration
# ---------------------------------------------------------------------------
BACKENDS = [
    {
        "name": "animagine",
        "space": "cagliostrolab/animagine-xl-3.1",
        "cooldown": 120,    # seconds to wait after quota exhaustion
        "max_retries": 3,
    },
    {
        "name": "cosxl",
        "space": "multimodalart/cosxl",
        "cooldown": 120,
        "max_retries": 2,
    },
]

# ---------------------------------------------------------------------------
# Theme definitions (same as before, 10 themes x 24 prompts)
# ---------------------------------------------------------------------------
THEMES = [
    {"name": "Victorian Botanical Ephemera", "slug": "victorian_botanical_ephemera", "description": "Exquisite Victorian-era botanical illustrations, herbarium specimens, vintage seed catalogs, and floral ephemera perfect for junk journaling and scrapbooking.", "tags": ["victorian", "botanical", "ephemera", "vintage", "floral", "herbarium", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 4.99, "prompts": ["Vintage botanical illustration of a wild rose, detailed hand-drawn style, aged parchment paper background, Victorian era, watercolor touches", "Antique herbarium specimen page showing pressed fern leaves with handwritten Latin labels, brown aged paper, vintage scientific aesthetic", "Victorian seed catalog cover page with ornate border of blooming flowers, decorative typography, 1890s style, warm sepia tones", "Vintage botanical drawing of lavender sprigs with purple watercolor, aged creamy paper, detailed ink lines, romantic style", "Antique botanical plate showing a blooming peony, hand-colored engraving style, soft pastel watercolor wash, 1880s aesthetic", "Victorian wildflower meadow illustration, pressed flower arrangement style, faded watercolors on cream paper, romantic ephemera", "Vintage botanical sketch of a sunflower with seed pod detail, pencil and ink on aged paper, scientific illustration style", "Antique rose garden illustration with multiple rose varieties, Victorian watercolor style, decorative banner cartouche", "Old herbarium page with pressed oak leaves and acorns, handwritten notes in brown ink, yellowed paper texture", "Victorian botanical ephemera piece featuring a wreath of morning glories, hand-painted watercolor, aged paper", "Vintage illustration of a blooming cherry blossom branch, delicate Japanese-influenced Victorian style, soft pink watercolors", "Antique botanical study of a dahlia, detailed petals in watercolor, ornamental border, 1890s print style", "Victorian botanical trade card with chamomile flowers, ornate gold border, advertising ephemera style", "Pressed wildflower arrangement vintage page, buttercups and daisies, faded watercolors, aged paper", "Vintage botanical illustration of poppy flowers, red watercolor wash, detailed ink drawing, Victorian seed packet style", "Antique botanical page showing a lily of the valley, delicate green and white watercolor, aged paper texture", "Victorian-era botanical plate featuring an iris, purple-blue watercolor, detailed ink engraving style", "Vintage horticultural print of tulip varieties, hand-colored engraving, ornamental border design", "Antique botanical study of a magnolia branch, soft cream and pink watercolor, aged ivory paper", "Victorian botanical ephemera with a decorative floral alphabet letter A surrounded by roses, ornate illustration", "Vintage botanical illustration of honeysuckle vine, detailed hand-drawn style, green and cream watercolors", "Antique pressed flower page featuring a violets specimen with handwritten label, aged paper texture", "Victorian-era botanical trading card with a pansy illustration, gold embossed border, pastel watercolors", "Vintage botanical illustration of a lotus flower, Japanese-influenced Victorian style, delicate ink work"]},
    {"name": "Dark Academia Gothic", "slug": "dark_academia_gothic", "description": "Moody dark academia and gothic-inspired ephemera featuring ancient libraries, architectural details, gothic scripts, and atmospheric ink illustrations for brooding junk journals.", "tags": ["darkacademia", "gothic", "ephemera", "vintage", "moody", "library", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 5.49, "prompts": ["Dark academia library interior with towering bookshelves and candlelight, moody ink illustration, aged paper texture", "Gothic cathedral architectural detail drawing, pointed arches and gargoyles, pen and ink on aged vellum", "Victorian gothic letter border with ravens and thorns, black ink illustration, dark romantic style", "Antique manuscript page with ornate gothic calligraphy, illuminated letter, dark red and gold accents on aged paper", "Dark academia desk scene with quill, ink bottle, and ancient books, moody charcoal drawing, sepia tones", "Gothic rose window architectural drawing, detailed ink illustration, dramatic shadows, aged parchment", "Victorian gothic moth illustration, detailed entomological drawing, dark background with gold accents", "Antique library card catalog drawer with brass fittings, vintage ink drawing, warm dark tones", "Dark academia astronomical chart with constellations, aged paper, ink and sepia watercolor", "Gothic iron gate with climbing ivy, detailed ink illustration, moody atmospheric style", "Victorian skeleton key illustration, ornate design with gothic flourishes, aged paper background", "Antique apothecary bottle label with gothic script, dark romantic style, aged paper texture", "Dark academia coffee-stained journal page with poetry fragments, ink blotches, vintage paper", "Gothic arch doorway with trailing vines, detailed ink drawing, atmospheric shadows", "Victorian wax seal and letter ephemera, dark romantic style, ink illustration on aged paper", "Antique anatomy illustration plate, gothic medical drawing style, sepia and ink on aged vellum", "Dark academia bookshelf vignette with candle and skull, moody charcoal drawing, dramatic lighting", "Gothic ornament border design with ravens and thistles, black ink illustration, medieval manuscript style", "Victorian observatory interior with telescope and star charts, ink drawing, dark academia aesthetic", "Antique calligraphy practice sheet with gothic script, ink on yellowed paper, dark romantic mood", "Gothic church interior with stained glass, detailed ink illustration, dramatic light rays", "Dark academia pocket watch and compass illustration, moody ink drawing, aged paper", "Victorian gothic ephemera collage with pressed black roses and lace, ink and watercolor", "Antique book cover design with gothic ornamental border, gold foil on dark background"]},
    {"name": "Vintage Steampunk Apothecary", "slug": "vintage_steampunk_apothecary", "description": "Steampunk apothecary ephemera with brass gears, vintage medicine labels, mechanical illustrations, and Victorian scientific apparatus. Perfect for alchemy-themed junk journals.", "tags": ["steampunk", "apothecary", "vintage", "ephemera", "alchemy", "mechanical", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 4.99, "prompts": ["Steampunk apothecary bottle with brass gears and copper label, detailed ink illustration, aged paper background", "Vintage apothecary label for Laudanum with ornate border, Victorian medical ephemera, aged paper texture", "Steampunk mechanical heart illustration with brass gears and tubes, ink and sepia watercolor, antique paper", "Victorian scientific instrument drawing of a brass microscope, detailed engraving style, aged paper", "Steampunk gear and clockwork illustration, interconnected brass mechanisms, pen and ink on vellum", "Antique apothecary cabinet with bottles and drawers, Victorian ink illustration, warm brown tones", "Steampunk airship blueprint design, technical drawing style, aged blueprint paper, sepia ink", "Vintage apothecary mortar and pestle illustration, brass and copper details, aged paper texture", "Steampunk mechanical eye with brass housing and lens gears, detailed ink drawing, aged paper", "Victorian pharmacy label for exotic tinctures, ornate border with art nouveau elements, aged paper", "Steampunk steam engine schematic, detailed technical illustration, brass and copper tones", "Antique apothecary jar label with skull and crossbones warning, Victorian medical ephemera style", "Steampunk mechanical butterfly with brass wings and gears, detailed ink illustration, aged paper", "Victorian distillation apparatus illustration, alchemical equipment drawing, sepia ink on paper", "Steampunk key with brass and copper mechanical elements, ornate vintage style, aged paper", "Antique chemistry flask illustration with bubbling liquid, steampunk aesthetic, detailed ink drawing", "Vintage apothecary receipt ephemera with brass border design, Victorian printing style, aged paper", "Steampunk mechanical arm prosthetic blueprint, technical drawing, brass and copper color palette", "Victorian leech jar label, apothecary ephemera, ornate border with medical illustration", "Steampunk clockwork face illustration with exposed gears, detailed ink drawing, aged vellum paper", "Antique apothecary scale with brass weights, balanced composition, Victorian illustration style", "Steampunk perpetual motion device illustration, brass gears and pendulums, technical drawing style", "Victorian quack medicine advertisement with steampunk elements, ornate typography, aged paper", "Steampunk brass compass rose illustration, detailed technical drawing, navigation ephemera style"]},
    {"name": "Alice in Wonderland Grunge", "slug": "alice_in_wonderland_grunge", "description": "Whimsical Alice in Wonderland-inspired grunge ephemera with distorted teacups, playing cards, pocket watches, and surreal illustrations. Perfect for whimsigoth junk journals.", "tags": ["aliceinwonderland", "grunge", "whimsigoth", "vintage", "ephemera", "surreal", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 5.49, "prompts": ["Alice in Wonderland teacup illustration with grunge texture, distressed vintage style, ink and watercolor", "Vintage playing card Queen of Hearts with distressed edges, grunge aesthetic, aged paper texture", "White rabbit pocket watch illustration, steampunk wonderland style, distressed ink drawing, aged paper", "Wonderland mad hatter hat illustration with price tag, grunge texture, ink and sepia watercolor", "Cheshire cat smile floating illustration, vintage ink style, distressed paper background", "Alice falling down the rabbit hole vintage illustration, distressed ink style, aged paper", "Wonderland teapot with dormouse illustration, vintage ink drawing, grunge texture overlay", "Playing card soldiers marching vintage illustration, grunge style, aged paper background", "Wonderland mushroom and caterpillar illustration, vintage ink style, distressed paper texture", "Flamingo croquet mallet vintage illustration, grunge aesthetic, ink and watercolor", "Wonderland door with tiny key illustration, vintage style, distressed paper, ink drawing", "Eat Me cake and Drink Me bottle illustration, vintage ephemera style, grunge texture", "Queen of Hearts rose garden painting scene, vintage illustration style, distressed aged paper", "Wonderland nonsense poetry page, handwritten style, grunge overlay, vintage paper texture", "Jabberwock illustration in vintage ink style, dark fantasy, distressed paper background", "Wonderland pocket watch with spiraling numbers illustration, grunge aesthetic, aged paper", "Vintage Wonderland map illustration showing the rabbit hole and garden, distressed style", "Tweedledum and Tweedledee vintage illustration, grunge style, ink and watercolor", "Wonderland chess piece characters illustration, vintage style, distressed paper", "Caterpillar on mushroom with hookah illustration, vintage ink style, grunge texture", "Wonderland key and lock illustration with ornate design, vintage ephemera, distressed paper", "Vintage Wonderland invitation card illustration, grunge style, calligraphy and floral border", "Wonderland clock face with backwards numbers illustration, distressed vintage style", "Alice shrinking and growing illustration, vintage ink style, grunge paper texture"]},
    {"name": "Art Nouveau Flower Fairies", "slug": "art_nouveau_flower_fairies", "description": "Beautiful Art Nouveau-inspired flower fairy illustrations with flowing organic lines, sinuous borders, and delicate watercolor touches. Ideal for ethereal junk journal pages.", "tags": ["artnouveau", "flowerfairy", "vintage", "ephemera", "fairy", "watercolor", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 4.99, "prompts": ["Art Nouveau flower fairy sitting on a lily pad, flowing organic lines, watercolor illustration, aged paper", "Art Nouveau decorative border with roses and fairy silhouettes, sinuous line style, vintage paper", "Flower fairy with morning glory wings, Art Nouveau style, delicate watercolor, aged background", "Art Nouveau rose fairy illustration, Alphonse Mucha inspired, flowing hair and floral crown, vintage paper", "Fairy sitting on a daisy, Art Nouveau style illustration, detailed ink lines with watercolor wash", "Art Nouveau floral panel with fairy and butterfly, ornamental border design, vintage ephemera", "Flower fairy of the violet, Art Nouveau illustration, detailed line work, soft purple watercolor", "Art Nouveau peacock fairy illustration, flowing ornamental lines, watercolor on aged paper", "Fairy with dragonfly wings among reeds, Art Nouveau style, green and gold watercolor, vintage paper", "Art Nouveau decorative page with fairy vignette and floral frame, sinuous organic design", "Flower fairy of the cherry blossom, Art Nouveau style, delicate pink watercolor illustration", "Art Nouveau fairy crown and floral scepter illustration, ornate line work, vintage ephemera style", "Fairy resting on a poppy flower, Art Nouveau illustration, red watercolor wash, aged paper", "Art Nouveau iris fairy illustration, flowing organic border, detailed ink lines, vintage style", "Flower fairy with sunflower headdress, Art Nouveau style, warm golden watercolor, aged paper", "Art Nouveau botanical fairy page, detailed illustration with decorative border, vintage ephemera", "Fairy of the bluebell woods, Art Nouveau style illustration, blue and green watercolor, aged paper", "Art Nouveau fairy and crescent moon illustration, ornamental design, silver watercolor on dark paper", "Flower fairy queen with floral scepter, Art Nouveau style, detailed ink and watercolor, vintage", "Art Nouveau pansy fairy illustration, violet watercolor, flowing organic lines, aged paper", "Fairy among wildflowers illustration, Art Nouveau style, multicolor watercolor wash, vintage", "Art Nouveau decorative letter F with fairy and ferns, ornamental style, vintage paper texture", "Flower fairy of the honeysuckle, Art Nouveau illustration, detailed line art, aged paper", "Art Nouveau fairy garden scene with arbor and climbing roses, flowing design, watercolor vintage style"]},
    {"name": "Vintage Travel Memorabilia", "slug": "vintage_travel_memorabilia", "description": "Nostalgic vintage travel ephemera featuring old maps, luggage tags, postcards, ticket stubs, and passport stamps. Perfect for travel-themed junk journals and scrapbooking.", "tags": ["vintage", "travel", "memorabilia", "ephemera", "map", "postcard", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 4.99, "prompts": ["Vintage travel luggage tag from Paris, ornate typography, aged paper texture, retro travel ephemera", "Antique world map illustration showing old sea routes, aged parchment, sepia and ink drawing", "Vintage train ticket stub illustration, retro European railway ephemera, distressed paper", "Old passport page with vintage stamps and seals illustration, aged paper texture, travel ephemera", "Vintage travel postcard from Rome with Colosseum illustration, retro style, aged paper", "Antique compass rose map illustration, navigational ephemera, sepia and ink on aged vellum", "Vintage luggage label from a grand hotel, art deco style, distressed paper texture", "Old steamer trunk illustration with travel stickers, vintage ink drawing, aged paper", "Vintage airline baggage tag illustration, retro travel ephemera, aged paper texture", "Antique map of the Mediterranean Sea illustration, aged parchment, sepia and ink drawing", "Vintage travel brochure cover illustration, retro advertising style, aged paper", "Old camera and travel journal ephemera illustration, vintage ink drawing, aged paper texture", "Vintage postage stamps collection from different countries, travel ephemera, aged paper", "Antique globe illustration on a wooden stand, vintage style, sepia and ink drawing", "Vintage travel voucher illustration, retro European railway ephemera, distressed paper", "Old lighthouse postcard illustration, vintage travel ephemera, aged paper, ink and watercolor", "Vintage boarding pass illustration, retro airline ephemera style, aged paper texture", "Antique sailing ship illustration on vintage map, aged parchment, sepia and ink drawing", "Vintage travel journal page with sketch of a European cathedral, ink drawing, aged paper", "Old baggage claim ticket illustration, vintage travel ephemera, distressed paper texture", "Vintage hot air balloon illustration, travel ephemera style, ink and watercolor on aged paper", "Antique luggage with travel decal stickers illustration, vintage style, sepia drawing", "Vintage cruise ship postcard illustration, retro travel ephemera, aged paper texture", "Old map illustration of a fantasy journey, aged parchment, sepia ink, travel ephemera style"]},
    {"name": "Rustic Cottage Garden", "slug": "rustic_cottage_garden", "description": "Charming rustic cottage garden ephemera with floral borders, garden plans, herb illustrations, watering cans, and pastoral watercolor scenes. Perfect for cozy junk journals.", "tags": ["rustic", "cottage", "garden", "vintage", "ephemera", "floral", "herb", "junkjournal", "scrapbook", "printable"], "price": 4.99, "prompts": ["Rustic cottage garden scene with picket fence and flowers, watercolor illustration, aged paper texture", "Vintage garden plan illustration with labeled herb beds, ink drawing, aged paper background", "Rustic watering can with wildflowers illustration, cottage garden style, watercolor on aged paper", "Vintage herb illustration page with rosemary and thyme, botanical drawing, aged paper texture", "Cottage garden birdhouse among climbing roses illustration, watercolor, rustic vintage style", "Vintage seed packet illustration for cottage garden flowers, retro design, aged paper", "Rustic garden tools illustration with trowel and pruning shears, vintage ink drawing, aged paper", "Cottage garden gate with wisteria illustration, watercolor, rustic vintage style", "Vintage garden journal page with pressed flower sketch, ink and watercolor, aged paper", "Rustic flower press illustration with dried petals, cottage style, vintage ephemera", "Vintage garden bench surrounded by lavender illustration, watercolor, aged paper texture", "Cottage garden sundial illustration with moss detail, vintage ink drawing, aged paper", "Rustic flower basket overflowing with blooms illustration, watercolor, vintage ephemera style", "Vintage garden label stakes illustration for herb pots, cottage style, ink on aged paper", "Cottage garden trellis with climbing sweet peas illustration, watercolor, vintage style", "Rustic terra cotta pots with seedlings illustration, cottage garden style, ink and watercolor", "Vintage garden journal cover illustration with floral border, rustic style, aged paper texture", "Cottage garden swing under a willow tree illustration, watercolor, vintage ephemera style", "Rustic wooden wheelbarrow with flowers illustration, cottage garden style, aged paper background", "Vintage garden catalog page with cottage flowers, retro illustration style, aged paper", "Rustic beehive in a wildflower garden illustration, watercolor, vintage ephemera style", "Cottage garden path through English garden illustration, watercolor, aged paper texture", "Vintage plant stake labels illustration, cottage garden style, ink drawing on aged paper", "Rustic rain gauge and garden boots illustration, cottage style, watercolor, vintage ephemera"]},
    {"name": "Celestial Astrology Journal", "slug": "celestial_astrology_journal", "description": "Mystical celestial and astrology ephemera featuring zodiac signs, star maps, moon phases, and cosmic illustrations. Perfect for witchy and spiritual junk journals.", "tags": ["celestial", "astrology", "zodiac", "mystical", "vintage", "ephemera", "moon", "junkjournal", "scrapbook", "printable"], "price": 5.49, "prompts": ["Celestial star map illustration with zodiac constellations, vintage ink drawing, aged paper", "Moon phases illustration from new to full, vintage style, gold and silver ink on dark paper", "Zodiac wheel illustration with all twelve signs, vintage astrology ephemera, aged paper texture", "Celestial sun and moon illustration, vintage ink drawing with gold accents, aged vellum paper", "Vintage astrology birth chart illustration, detailed planetary positions, aged paper texture", "Celestial tarot card illustration The Star, vintage style, gold and navy, aged paper", "Moon goddess illustration with crescent crown, vintage ink and watercolor, mysterious style", "Vintage star chart illustration of the northern hemisphere, aged paper, sepia and gold ink", "Celestial compass rose illustration with sun and moon, vintage ephemera style, aged paper", "Astrology symbol page with planetary glyphs, vintage manuscript style, aged paper texture", "Celestial eclipse illustration, vintage astronomical ephemera, ink and watercolor, aged paper", "Vintage zodiac Aries illustration with ram and stars, astrological ephemera, aged paper", "Celestial moon garden illustration with night-blooming flowers, vintage style, dark paper", "Vintage astrology aspect illustration with planetary alignments, technical ink drawing, aged paper", "Celestial cosmos illustration with nebula and stars, vintage ephemera style, gold and navy", "Vintage zodiac Cancer illustration with crab and stars, astrological ephemera, aged paper", "Celestial astrolabe illustration, vintage scientific instrument drawing, ink on aged paper", "Vintage moon calendar illustration with phases, astrology ephemera style, aged paper texture", "Celestial solar system illustration, vintage astronomy style, ink drawing with gold accents", "Vintage zodiac Leo illustration with lion and stars, astrological ephemera, aged paper", "Celestial star and crescent illustration, vintage ornamental design, gold ink on dark paper", "Vintage astrology house wheel illustration, technical drawing style, aged paper texture", "Celestial aurora illustration with stars, vintage ephemera style, watercolor on dark paper", "Vintage zodiac Pisces illustration with fish and stars, astrological ephemera, aged paper"]},
    {"name": "Medieval Illuminated Manuscript", "slug": "medieval_illuminated_manuscript", "description": "Medieval illuminated manuscript pages with ornate initials, gold leaf borders, heraldic designs, and calligraphy. Perfect for fantasy and historical junk journals.", "tags": ["medieval", "illuminated", "manuscript", "gothic", "historical", "ephemera", "junkjournal", "scrapbook", "digitalpaper", "printable"], "price": 5.99, "prompts": ["Medieval illuminated manuscript page with ornate letter B and gold leaf border, vellum texture", "Medieval heraldic shield illustration with lion rampant, gold and red, vellum paper texture", "Illuminated manuscript page with decorative border of ivy and gold, medieval script, aged vellum", "Medieval bestiary page with phoenix illustration, gold leaf and tempera, vellum texture", "Ornate medieval manuscript initial letter S with dragon, gold leaf, blue and red, vellum", "Medieval map illustration of a fantastical kingdom, gold leaf accents, aged vellum texture", "Illuminated manuscript page with decorative floral border, gold and blue, medieval calligraphy", "Medieval heraldic crest with eagle, gold and black, vellum paper, illuminated style", "Manuscript page with ornate calendar illustration, gold leaf, zodiac medallions, vellum", "Medieval bestiary page with unicorn illustration, gold leaf border, red and blue tempera", "Ornate medieval manuscript page with illuminated letter R, gold leaf, intricate border, vellum", "Medieval coat of arms illustration with griffin, gold leaf accents, vellum paper texture", "Illuminated manuscript music page with decorative border, gold and red, medieval notation", "Medieval page border with acanthus leaves and gold leaf, vellum texture, illuminated style", "Bestiary page with dragon illustration, gold leaf and tempera, medieval manuscript style", "Ornate medieval initial letter D with saint figure, gold leaf, blue and red, vellum", "Medieval manuscript page with Tree of Jesse illustration, gold leaf border, vellum texture", "Heraldic banner illustration with gold fleur-de-lis, medieval style, vellum paper", "Illuminated manuscript page with ornate line ending, gold leaf creatures, blue and red, vellum", "Medieval calendar page with Labors of the Months illustration, gold leaf, vellum texture", "Ornate medieval manuscript frame with gold leaf and flowers, empty center, vellum paper", "Bestiary page with basilisk illustration, gold leaf border, medieval manuscript style", "Medieval manuscript page with decorative puzzle initial, gold leaf, red and blue, vellum", "Heraldic achievement illustration with shield, helm, and mantling, gold leaf, vellum"]},
]


def get_theme_dir(theme):
    return PROJECT_DIR / f"{DATE_PREFIX}{theme['slug']}"

def get_original_dir(theme):
    return get_theme_dir(theme) / "Original_Bilder"


class ImageGenerator:
    """Multi-backend image generator with automatic failover and quota management."""
    
    def __init__(self):
        self.clients = {}
        self.quota_exhausted = {}  # backend_name -> timestamp when quota was exhausted
        self.request_count = 0
        
    def get_client(self, backend):
        """Get or create a gradio_client for a backend."""
        name = backend["name"]
        if name not in self.clients:
            print(f"  Connecting to {backend['space']}...")
            try:
                self.clients[name] = Client(backend["space"])
                print(f"  Connected to {name}")
            except Exception as e:
                print(f"  Failed to connect to {name}: {e}")
                return None
        return self.clients[name]
    
    def is_backend_available(self, backend):
        """Check if a backend's GPU quota has recovered."""
        name = backend["name"]
        if name in self.quota_exhausted:
            elapsed = time.time() - self.quota_exhausted[name]
            if elapsed < backend["cooldown"]:
                remaining = int(backend["cooldown"] - elapsed)
                return False, remaining
            else:
                # Quota should have recovered
                del self.quota_exhausted[name]
                return True, 0
        return True, 0
    
    def generate_animagine(self, prompt, seed):
        """Generate using Animagine XL 3.1."""
        backend = BACKENDS[0]  # animagine
        available, remaining = self.is_backend_available(backend)
        if not available:
            return None, f"quota_cooldown:{remaining}s"
        
        client = self.get_client(backend)
        if not client:
            return None, "connection_failed"
        
        try:
            result = client.predict(
                prompt,
                "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, blurry, distorted",
                seed,
                GEN_SIZE,  # width
                GEN_SIZE,  # height
                7,         # guidance_scale
                25,        # num_inference_steps
                "DPM++ 2M Karras",  # sampler
                "1024 x 1024",       # aspect_ratio
                "(None)",             # style_preset
                "Standard v3.1",     # quality_tags_presets
                False,               # use_upscaler
                0.7,                 # strength
                1.0,                 # upscale_by
                True,                # add_quality_tags
                api_name="/run"
            )
            gallery = result[0]
            if gallery and len(gallery) > 0:
                img_path = gallery[0]["image"]
                if os.path.exists(img_path):
                    return img_path, None
            return None, "empty_gallery"
        except Exception as e:
            err = str(e)
            if "GPU quota" in err or "exceeded" in err.lower():
                self.quota_exhausted[backend["name"]] = time.time()
                return None, f"quota_exhausted"
            elif "429" in err or "rate" in err.lower():
                return None, "rate_limited"
            else:
                return None, f"error:{err[:80]}"
    
    def generate_cosxl(self, prompt, seed):
        """Generate using cosxl."""
        backend = BACKENDS[1]  # cosxl
        available, remaining = self.is_backend_available(backend)
        if not available:
            return None, f"quota_cooldown:{remaining}s"
        
        client = self.get_client(backend)
        if not client:
            return None, "connection_failed"
        
        try:
            result = client.predict(
                prompt,
                "blurry, low quality, watermark, distorted, worst quality",
                7,        # guidance_scale
                20,       # steps
                api_name="/run_normal"
            )
            # cosxl returns image path directly or as tuple
            if isinstance(result, tuple):
                img_path = result[0] if result else None
            elif isinstance(result, str):
                img_path = result
            else:
                img_path = result
            
            if img_path and os.path.exists(str(img_path)):
                return str(img_path), None
            return None, f"bad_result:{type(result)}"
        except Exception as e:
            err = str(e)
            if "GPU quota" in err or "exceeded" in err.lower():
                self.quota_exhausted[backend["name"]] = time.time()
                return None, "quota_exhausted"
            elif "api_name" in err:
                return None, f"api_mismatch:{err[:60]}"
            else:
                return None, f"error:{err[:80]}"
    
    def generate_pollinations(self, prompt, seed):
        """Fallback: generate using Pollinations.ai (one at a time)."""
        import urllib.request
        import urllib.parse
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
        
        out_path = f"/tmp/pollinations_{seed}_{hash(prompt) % 10000}.jpg"
        
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "image/jpeg,image/png,*/*"
            })
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
                if len(data) < 5000:  # Likely an error response
                    try:
                        err_json = json.loads(data)
                        if "error" in err_json or "message" in err_json:
                            return None, f"pollinations_error:{str(err_json)[:80]}"
                    except:
                        pass
                    return None, f"pollinations_tiny_response:{len(data)}bytes"
                with open(out_path, "wb") as f:
                    f.write(data)
                # Verify it's a valid image
                try:
                    img = Image.open(out_path)
                    if img.size[0] < 512:
                        return None, f"pollinations_too_small:{img.size}"
                    return out_path, None
                except:
                    return None, "pollinations_invalid_image"
        except Exception as e:
            return None, f"pollinations_error:{str(e)[:60]}"
    
    def generate(self, prompt, seed, theme_name=None, idx=None):
        """Try backends in order until one succeeds."""
        self.request_count += 1
        label = f"[{theme_name} #{idx}]" if theme_name else f"[#{self.request_count}]"
        
        # Try Animagine first
        img_path, err = self.generate_animagine(prompt, seed)
        if img_path:
            return img_path, "animagine"
        print(f"    {label} Animagine: {err}")
        
        # Try cosxl
        img_path, err = self.generate_cosxl(prompt, seed)
        if img_path:
            return img_path, "cosxl"
        print(f"    {label} cosxl: {err}")
        
        # Try Pollinations as last resort
        img_path, err = self.generate_pollinations(prompt, seed)
        if img_path:
            return img_path, "pollinations"
        print(f"    {label} Pollinations: {err}")
        
        return None, "all_backends_failed"


def upscale_to_a4(img_path, output_path):
    """Upscale a 1024x1024 image to A4 300 DPI with quality padding."""
    img = Image.open(img_path).convert("RGB")
    
    scale_w = A4_W / img.width
    scale_h = A4_H / img.height
    scale = min(scale_w, scale_h)
    
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    
    canvas = Image.new("RGB", (A4_W, A4_H), (245, 235, 220))
    texture = np.random.randint(235, 250, (A4_H, A4_W, 3), dtype=np.uint8)
    texture_img = Image.fromarray(texture).filter(ImageFilter.GaussianBlur(radius=1))
    canvas = Image.blend(canvas, texture_img, 0.3)
    
    paste_x = (A4_W - new_w) // 2
    paste_y = (A4_H - new_h) // 2
    canvas.paste(img_resized, (paste_x, paste_y))
    
    canvas.save(str(output_path), "JPEG", quality=95, dpi=(300, 300))
    return output_path


def create_pdf(theme, theme_dir):
    """Create a PDF package for a theme."""
    from reportlab.lib.pagesizes import A4 as RL_A4
    from reportlab.pdfgen import canvas as pdf_canvas
    
    upscaled_dir = theme_dir / "Upscaled_A4"
    pdf_path = theme_dir / f"{theme['slug']}_junk_journal_package.pdf"
    
    c = pdf_canvas.Canvas(str(pdf_path), pagesize=RL_A4)
    page_w, page_h = RL_A4
    
    # Title page
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(page_w/2, page_h - 100, theme["name"])
    c.setFont("Helvetica", 14)
    # Wrap description
    desc = theme["description"]
    max_chars = 70
    y = page_h - 130
    while desc:
        line = desc[:max_chars]
        desc = desc[max_chars:]
        c.drawCentredString(page_w/2, y, line)
        y -= 18
    c.setFont("Helvetica", 10)
    upscaled_files = list(upscaled_dir.glob("*.jpg"))
    c.drawCentredString(page_w/2, y - 10, f"{len(upscaled_files)} Original Images | A4 300 DPI | {date.today().strftime('%B %Y')}")
    
    c.showPage()
    
    for img_file in sorted(upscaled_files):
        c.drawImage(str(img_file), 0, 0, width=page_w, height=page_h, preserveAspectRatio=True)
        c.showPage()
    
    c.save()
    print(f"  Created PDF: {pdf_path.name} ({len(upscaled_files)} image pages)")
    return pdf_path


def create_etsy_listing(theme, theme_dir, num_images):
    """Create Etsy listing metadata JSON."""
    listing = {
        "title": f"{theme['name']} - {num_images} Printable Junk Journal Ephemera Images | A4 300 DPI Digital Paper Pack",
        "description": f"""{theme['description']}\n\n📦 WHAT YOU GET:\n- {num_images} high-quality printable images\n- A4 size (210mm x 297mm) at 300 DPI\n- JPEG format, ready to print\n- Instant digital download\n\n✂️ PERFECT FOR:\n- Junk journaling & scrapbooking\n- Collage & mixed media art\n- Planner & bullet journal decoration\n- Card making & paper crafts\n- Print & cut for ephemera packs\n\n📐 DETAILS:\n- File format: JPEG\n- Resolution: 300 DPI\n- Page size: A4 (2480 x 3508 pixels)\n- For personal and small commercial use\n\nThis is a digital product - no physical item will be shipped.""",
        "tags": theme["tags"][:13],
        "price": theme["price"],
        "category": "Craft Supplies > Paper & Printable > Digital Paper",
        "images_count": num_images,
        "theme": theme["name"],
        "slug": theme["slug"],
    }
    
    listing_path = theme_dir / "etsy_listing.json"
    with open(listing_path, "w") as f:
        json.dump(listing, f, indent=2)
    print(f"  Created Etsy listing: {listing_path.name}")
    return listing_path


def check_progress():
    """Check generation progress for all themes."""
    total_images = 0
    for theme in THEMES:
        orig_dir = get_original_dir(theme)
        pngs = len(list(orig_dir.glob("*.png"))) if orig_dir.exists() else 0
        jpgs = len(list(orig_dir.glob("*.jpg"))) if orig_dir.exists() else 0
        total = pngs + jpgs
        total_images += total
        status = "DONE" if total >= 20 else f"{total}/24"
        print(f"  {theme['name']}: {status} images ({pngs} PNG + {jpgs} JPG)")
    print(f"\n  Total: {total_images}/240 images generated")
    return total_images


def main():
    parser = argparse.ArgumentParser(description="Generate junk journal images")
    parser.add_argument("--theme", type=int, help="Theme index (0-9)")
    parser.add_argument("--limit", type=int, help="Limit images per theme")
    parser.add_argument("--check", action="store_true", help="Check progress")
    parser.add_argument("--pdfs-only", action="store_true", help="Build PDFs only")
    args = parser.parse_args()
    
    if args.check:
        check_progress()
        return
    
    themes = [THEMES[args.theme]] if args.theme is not None else THEMES
    limit = args.limit or 24
    
    if args.pdfs_only:
        for theme in themes:
            theme_dir = get_theme_dir(theme)
            orig_dir = get_original_dir(theme)
            num = len(list(orig_dir.glob("*.[jp][np][pg]"))) if orig_dir.exists() else 0
            if num < 20:
                print(f"Skipping {theme['name']}: only {num} images")
                continue
            upscaled_dir = theme_dir / "Upscaled_A4"
            upscaled_dir.mkdir(parents=True, exist_ok=True)
            for img_file in sorted(orig_dir.glob("*.[jp][np][pg]")):
                out_file = upscaled_dir / (img_file.stem + ".jpg")
                if not out_file.exists():
                    upscale_to_a4(img_file, out_file)
            create_pdf(theme, theme_dir)
            create_etsy_listing(theme, theme_dir, num)
        return
    
    print(f"\n{'='*60}")
    print(f"Junk Journal Image Generator - Multi-Backend")
    print(f"Backends: animagine, cosxl, pollinations")
    print(f"{'='*60}")
    
    generator = ImageGenerator()
    
    for theme in themes:
        theme_dir = get_theme_dir(theme)
        orig_dir = get_original_dir(theme)
        orig_dir.mkdir(parents=True, exist_ok=True)
        
        existing = len(list(orig_dir.glob("*.png"))) + len(list(orig_dir.glob("*.jpg")))
        prompts = theme["prompts"][:limit]
        
        if existing >= limit:
            print(f"\n[SKIP] {theme['name']}: already has {existing} images")
            continue
        
        print(f"\n[THEME] {theme['name']}: need {limit - existing} more images ({existing} existing)")
        
        base_seed = hash(theme["name"]) % 100000
        generated = 0
        failed = 0
        
        for idx, prompt in enumerate(prompts):
            # Check both .png and .jpg
            out_png = orig_dir / f"img_{idx+1:02d}.png"
            out_jpg = orig_dir / f"img_{idx+1:02d}.jpg"
            
            if out_png.exists() or out_jpg.exists():
                continue
            
            print(f"\n  [{idx+1}/{len(prompts)}] {prompt[:55]}...")
            
            start = time.time()
            img_path, backend_name = generator.generate(
                prompt, base_seed + idx, theme["name"], idx+1
            )
            elapsed = time.time() - start
            
            if img_path and os.path.exists(img_path):
                # Determine extension from source
                ext = ".png" if img_path.endswith(".png") else ".jpg"
                out_path = orig_dir / f"img_{idx+1:02d}{ext}"
                shutil.copy2(img_path, str(out_path))
                size_kb = os.path.getsize(str(out_path)) / 1024
                print(f"  [{idx+1}/{len(prompts)}] OK via {backend_name} ({size_kb:.0f}KB, {elapsed:.0f}s)")
                generated += 1
                
                # Clean up temp file
                try:
                    if img_path.startswith("/tmp/"):
                        os.remove(img_path)
                except:
                    pass
            else:
                print(f"  [{idx+1}/{len(prompts)}] FAILED ({backend_name})")
                failed += 1
            
            # Rate limiting between requests
            if backend_name == "animagine":
                time.sleep(2)
            elif backend_name == "cosxl":
                time.sleep(2)
            else:
                time.sleep(5)  # Pollinations needs more spacing
        
        # After theme, try to build PDFs if enough images
        total = len(list(orig_dir.glob("*.png"))) + len(list(orig_dir.glob("*.jpg")))
        if total >= 20:
            print(f"\n  Building PDFs for {theme['name']} ({total} images)...")
            upscaled_dir = theme_dir / "Upscaled_A4"
            upscaled_dir.mkdir(parents=True, exist_ok=True)
            for img_file in sorted(orig_dir.glob("*.[jp][np][pg]")):
                out_file = upscaled_dir / (img_file.stem + ".jpg")
                if not out_file.exists():
                    upscale_to_a4(img_file, out_file)
            create_pdf(theme, theme_dir)
            create_etsy_listing(theme, theme_dir, total)
    
    print(f"\n{'='*60}")
    print("Generation Complete!")
    print(f"{'='*60}")
    check_progress()


if __name__ == "__main__":
    main()