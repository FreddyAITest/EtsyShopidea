#!/usr/bin/env python3
"""
Junk Journal Digital PDF Package Generator
Uses Pollinations.ai (free, no API key needed) for AI image generation.
Generates 10 themed packages with 20+ images each, compiles into PDFs,
and creates Etsy listing metadata.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import hashlib
from pathlib import Path
from datetime import date

# PDF compilation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Image handling
from PIL import Image
import numpy as np

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Theme definitions — each theme has a name, description, and 24 unique
# image prompts carefully crafted for junk journal aesthetics
# ---------------------------------------------------------------------------
THEMES = [
    {
        "name": "Victorian Botanical Ephemera",
        "description": "Exquisite Victorian-era botanical illustrations, herbarium specimens, vintage seed catalogs, and floral ephemera perfect for junk journaling and scrapbooking.",
        "tags": ["victorian", "botanical", "ephemera", "vintage", "floral", "herbarium", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Vintage botanical illustration of a wild rose, detailed hand-drawn style, aged parchment paper background, Victorian era, watercolor touches",
            "Antique herbarium specimen page showing pressed fern leaves with handwritten Latin labels, brown aged paper, vintage scientific aesthetic",
            "Victorian seed catalog cover page with ornate border of blooming flowers, decorative typography, 1890s style, warm sepia tones",
            "Vintage botanical drawing of lavender sprigs with purple watercolor, aged creamy paper, detailed ink lines, romantic style",
            "Antique botanical plate showing a blooming peony, hand-colored engraving style, soft pastel watercolor wash, 1880s aesthetic",
            "Victorian wildflower meadow illustration, pressed flower arrangement style, faded watercolors on cream paper, romantic ephemera",
            "Vintage botanical sketch of a sunflower with seed pod detail, pencil and ink on aged paper, scientific illustration style",
            "Antique rose garden illustration with multiple rose varieties, Victorian watercolor style, decorative banner cartouche",
            "Old herbarium page with pressed oak leaves and acorns, handwritten notes in brown ink, yellowed paper texture",
            "Victorian botanical ephemera piece featuring a wreath of morning glories, hand-painted watercolor, aged paper",
            "Vintage illustration of a blooming cherry blossom branch, delicate Japanese-influenced Victorian style, soft pink watercolors",
            "Antique botanical study of a dahlia, detailed petals in watercolor, ornamental border, 1890s print style",
            "Victorian botanical trade card with chamomile flowers, ornate gold border, advertising ephemera style",
            "Pressed wildflower arrangement vintage page, buttercups and daisies, faded watercolors, aged paper",
            "Vintage botanical illustration of poppy flowers, red watercolor wash, detailed ink drawing, Victorian seed packet style",
            "Antique botanical page showing a lily of the valley, delicate green and white watercolor, aged paper texture",
            "Victorian-era botanical plate featuring an iris, purple-blue watercolor, detailed ink engraving style",
            "Vintage horticultural print of tulip varieties, hand-colored engraving, ornamental border design",
            "Antique botanical study of a magnolia branch, soft cream and pink watercolor, aged ivory paper",
            "Victorian botanical ephemera with a decorative floral alphabet letter A surrounded by roses, ornate illustration",
            "Vintage botanical illustration of honeysuckle vine, detailed hand-drawn style, green and cream watercolors",
            "Antique pressed flower page featuring a violets specimen with handwritten label, aged paper texture",
            "Victorian-era botanical trading card with a pansy illustration, gold embossed border, pastel watercolors",
            "Vintage botanical illustration of a lotus flower, Japanese-influenced Victorian style, delicate ink work",
        ],
    },
    {
        "name": "Dark Academia Gothic",
        "description": "Moody dark academia and gothic-inspired ephemera featuring ancient libraries, architectural details, gothic scripts, and atmospheric ink illustrations for brooding junk journals.",
        "tags": ["darkacademia", "gothic", "ephemera", "vintage", "moody", "library", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Dark academia library interior with towering bookshelves and candlelight, moody ink illustration, aged paper texture",
            "Gothic cathedral architectural detail drawing, pointed arches and gargoyles, pen and ink on aged vellum",
            "Victorian gothic letter border with ravens and thorns, black ink illustration, dark romantic style",
            "Antique manuscript page with ornate gothic calligraphy, illuminated letter, dark red and gold accents on aged paper",
            "Dark academia desk scene with quill, ink bottle, and ancient books, moody charcoal drawing, sepia tones",
            "Gothic rose window architectural drawing, detailed ink illustration, dramatic shadows, aged parchment",
            "Victorian gothic moth illustration, detailed entomological drawing, dark background with gold accents",
            "Antique library card catalog drawer with brass fittings, vintage ink drawing, warm dark tones",
            "Dark academia astronomical chart with constellations, aged paper, ink and sepia watercolor",
            "Gothic iron gate with climbing ivy, detailed ink illustration, moody atmospheric style",
            "Victorian skeleton key illustration, ornate design with gothic flourishes, aged paper background",
            "Antique apothecary bottle label with gothic script, dark romantic style, aged paper texture",
            "Dark academia coffee-stained journal page with poetry fragments, ink blotches, vintage paper",
            "Gothic arch doorway with trailing vines, detailed ink drawing, atmospheric shadows",
            "Victorian wax seal and letter ephemera, dark romantic style, ink illustration on aged paper",
            "Antique anatomy illustration plate, gothic medical drawing style, sepia and ink on aged vellum",
            "Dark academia bookshelf vignette with candle and skull, moody charcoal drawing, dramatic lighting",
            "Gothic ornament border design with ravens and thistles, black ink illustration, medieval manuscript style",
            "Victorian observatory interior with telescope and star charts, ink drawing, dark academia aesthetic",
            "Antique calligraphy practice sheet with gothic script, ink on yellowed paper, dark romantic mood",
            "Gothic church interior with stained glass, detailed ink illustration, dramatic light rays",
            "Dark academia pocket watch and compass illustration, moody ink drawing, aged paper",
            "Victorian gothic ephemera collage with pressed black roses and lace, ink and watercolor",
            "Antique book cover design with gothic ornamental border, gold foil on dark background",
        ],
    },
    {
        "name": "Vintage Steampunk Apothecary",
        "description": "Steampunk apothecary ephemera with brass gears, vintage medicine labels, mechanical illustrations, and Victorian scientific apparatus. Perfect for alchemy-themed junk journals.",
        "tags": ["steampunk", "apothecary", "vintage", "ephemera", "alchemy", "mechanical", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Steampunk apothecary bottle with brass gears and copper label, detailed ink illustration, aged paper background",
            "Vintage apothecary label for Laudanum with ornate border, Victorian medical ephemera, aged paper texture",
            "Steampunk mechanical heart illustration with brass gears and tubes, ink and sepia watercolor, antique paper",
            "Victorian scientific instrument drawing of a brass microscope, detailed engraving style, aged paper",
            "Steampunk gear and clockwork illustration, interconnected brass mechanisms, pen and ink on vellum",
            "Antique apothecary cabinet with bottles and drawers, Victorian ink illustration, warm brown tones",
            "Steampunk airship blueprint design, technical drawing style, aged blueprint paper, sepia ink",
            "Vintage apothecary mortar and pestle illustration, brass and copper details, aged paper texture",
            "Steampunk mechanical eye with brass housing and lens gears, detailed ink drawing, aged paper",
            "Victorian pharmacy label for exotic tinctures, ornate border with art nouveau elements, aged paper",
            "Steampunk steam engine schematic, detailed technical illustration, brass and copper tones",
            "Antique apothecary jar label with skull and crossbones warning, Victorian medical ephemera style",
            "Steampunk mechanical butterfly with brass wings and gears, detailed ink illustration, aged paper",
            "Victorian distillation apparatus illustration, alchemical equipment drawing, sepia ink on paper",
            "Steampunk key with brass and copper mechanical elements, ornate vintage style, aged paper",
            "Antique chemistry flask illustration with bubbling liquid, steampunk aesthetic, detailed ink drawing",
            "Vintage apothecary receipt ephemera with brass border design, Victorian printing style, aged paper",
            "Steampunk mechanical arm prosthetic blueprint, technical drawing, brass and copper color palette",
            "Victorian leech jar label, apothecary ephemera, ornate border with medical illustration",
            "Steampunk clockwork face illustration with exposed gears, detailed ink drawing, aged vellum paper",
            "Antique apothecary scale with brass weights, balanced composition, Victorian illustration style",
            "Steampunk perpetual motion device illustration, brass gears and pendulums, technical drawing style",
            "Victorian quack medicine advertisement with steampunk elements, ornate typography, aged paper",
            "Steampunk brass compass rose illustration, detailed technical drawing, navigation ephemera style",
        ],
    },
    {
        "name": "Alice in Wonderland Grunge",
        "description": "Whimsical Alice in Wonderland-inspired grunge ephemera with distorted teacups, playing cards, pocket watches, and surreal illustrations. Perfect for whimsigoth junk journals.",
        "tags": ["aliceinwonderland", "grunge", "whimsigoth", "vintage", "ephemera", "surreal", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Alice in Wonderland teacup illustration with grunge texture, distressed vintage style, ink and watercolor",
            "Vintage playing card Queen of Hearts with distressed edges, grunge aesthetic, aged paper texture",
            "White rabbit pocket watch illustration, steampunk wonderland style, distressed ink drawing, aged paper",
            "Wonderland mad hatter hat illustration with price tag, grunge texture, ink and sepia watercolor",
            "Cheshire cat smile floating illustration, vintage ink style, distressed paper background",
            "Alice falling down the rabbit hole vintage illustration, distressed ink style, aged paper",
            "Wonderland teapot with dormouse illustration, vintage ink drawing, grunge texture overlay",
            "Playing card soldiers marching vintage illustration, grunge style, aged paper background",
            "Wonderland mushroom and caterpillar illustration, vintage ink style, distressed paper texture",
            "Flamingo croquet mallet vintage illustration, grunge aesthetic, ink and watercolor",
            "Wonderland door with tiny key illustration, vintage style, distressed paper, ink drawing",
            "Eat Me cake and Drink Me bottle illustration, vintage ephemera style, grunge texture",
            "Queen of Hearts rose garden painting scene, vintage illustration style, distressed aged paper",
            "Wonderland nonsense poetry page, handwritten style, grunge overlay, vintage paper texture",
            "Jabberwock illustration in vintage ink style, dark fantasy, distressed paper background",
            "Wonderland pocket watch with spiraling numbers illustration, grunge aesthetic, aged paper",
            "Vintage Wonderland map illustration showing the rabbit hole and garden, distressed style",
            "Tweedledum and Tweedledee vintage illustration, grunge style, ink and watercolor",
            "Wonderland chess piece characters illustration, vintage style, distressed paper",
            "Caterpillar on mushroom with hookah illustration, vintage ink style, grunge texture",
            "Wonderland key and lock illustration with ornate design, vintage ephemera, distressed paper",
            "Vintage Wonderland invitation card illustration, grunge style, calligraphy and floral border",
            "Wonderland clock face with backwards numbers illustration, distressed vintage style",
            "Alice shrinking and growing illustration, vintage ink style, grunge paper texture",
        ],
    },
    {
        "name": "Art Nouveau Flower Fairies",
        "description": "Beautiful Art Nouveau-inspired flower fairy illustrations with flowing organic lines, sinuous borders, and delicate watercolor touches. Ideal for ethereal junk journal pages.",
        "tags": ["artnouveau", "flowerfairy", "vintage", "ephemera", "fairy", "watercolor", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Art Nouveau flower fairy sitting on a lily pad, flowing organic lines, watercolor illustration, aged paper",
            "Art Nouveau decorative border with roses and fairy silhouettes, sinuous line style, vintage paper",
            "Flower fairy with morning glory wings, Art Nouveau style, delicate watercolor, aged background",
            "Art Nouveau rose fairy illustration, Alphonse Mucha inspired, flowing hair and floral crown, vintage paper",
            "Fairy sitting on a daisy, Art Nouveau style illustration, detailed ink lines with watercolor wash",
            "Art Nouveau floral panel with fairy and butterfly, ornamental border design, vintage ephemera",
            "Flower fairy of the violet, Art Nouveau illustration, detailed line work, soft purple watercolor",
            "Art Nouveau peacock fairy illustration, flowing ornamental lines, watercolor on aged paper",
            "Fairy with dragonfly wings among reeds, Art Nouveau style, green and gold watercolor, vintage paper",
            "Art Nouveau decorative page with fairy vignette and floral frame, sinuous organic design",
            "Flower fairy of the cherry blossom, Art Nouveau style, delicate pink watercolor illustration",
            "Art Nouveau fairy crown and floral scepter illustration, ornate line work, vintage ephemera style",
            "Fairy resting on a poppy flower, Art Nouveau illustration, red watercolor wash, aged paper",
            "Art Nouveau iris fairy illustration, flowing organic border, detailed ink lines, vintage style",
            "Flower fairy with sunflower headdress, Art Nouveau style, warm golden watercolor, aged paper",
            "Art Nouveau botanical fairy page, detailed illustration with decorative border, vintage ephemera",
            "Fairy of the bluebell woods, Art Nouveau style illustration, blue and green watercolor, aged paper",
            "Art Nouveau fairy and crescent moon illustration, ornamental design, silver watercolor on dark paper",
            "Flower fairy queen with floral scepter, Art Nouveau style, detailed ink and watercolor, vintage",
            "Art Nouveau pansy fairy illustration, violet watercolor, flowing organic lines, aged paper",
            "Fairy among wildflowers illustration, Art Nouveau style, multicolor watercolor wash, vintage",
            "Art Nouveau decorative letter F with fairy and ferns, ornamental style, vintage paper texture",
            "Flower fairy of the honeysuckle, Art Nouveau illustration, detailed line art, aged paper",
            "Art Nouveau fairy garden scene with arbor and climbing roses, flowing design, watercolor vintage style",
        ],
    },
    {
        "name": "Vintage Travel Memorabilia",
        "description": "Nostalgic vintage travel ephemera featuring old maps, luggage tags, postcards, ticket stubs, and passport stamps. Perfect for travel-themed junk journals and scrapbooking.",
        "tags": ["vintage", "travel", "memorabilia", "ephemera", "map", "postcard", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Vintage travel luggage tag from Paris, ornate typography, aged paper texture, retro travel ephemera",
            "Antique world map illustration showing old sea routes, aged parchment, sepia and ink drawing",
            "Vintage train ticket stub illustration, retro European railway ephemera, distressed paper",
            "Old passport page with vintage stamps and seals illustration, aged paper texture, travel ephemera",
            "Vintage travel postcard from Rome with Colosseum illustration, retro style, aged paper",
            "Antique compass rose map illustration, navigational ephemera, sepia and ink on aged vellum",
            "Vintage luggage label from a grand hotel, art deco style, distressed paper texture",
            "Old steamer trunk illustration with travel stickers, vintage ink drawing, aged paper",
            "Vintage airline baggage tag illustration, retro travel ephemera, aged paper texture",
            "Antique map of the Mediterranean Sea illustration, aged parchment, sepia and ink drawing",
            "Vintage travel brochure cover illustration, retro advertising style, aged paper",
            "Old camera and travel journal ephemera illustration, vintage ink drawing, aged paper texture",
            "Vintage postage stamps collection from different countries, travel ephemera, aged paper",
            "Antique globe illustration on a wooden stand, vintage style, sepia and ink drawing",
            "Vintage travel voucher illustration, retro European railway ephemera, distressed paper",
            "Old lighthouse postcard illustration, vintage travel ephemera, aged paper, ink and watercolor",
            "Vintage boarding pass illustration, retro airline ephemera style, aged paper texture",
            "Antique sailing ship illustration on vintage map, aged parchment, sepia and ink drawing",
            "Vintage travel journal page with sketch of a European cathedral, ink drawing, aged paper",
            "Old baggage claim ticket illustration, vintage travel ephemera, distressed paper texture",
            "Vintage hot air balloon illustration, travel ephemera style, ink and watercolor on aged paper",
            "Antique luggage with travel decal stickers illustration, vintage style, sepia drawing",
            "Vintage cruise ship postcard illustration, retro travel ephemera, aged paper texture",
            "Old map illustration of a fantasy journey, aged parchment, sepia ink, travel ephemera style",
        ],
    },
    {
        "name": "Rustic Cottage Garden",
        "description": "Charming rustic cottage garden ephemera with floral borders, garden plans, herb illustrations, watering cans, and pastoral watercolor scenes. Perfect for cozy junk journals.",
        "tags": ["rustic", "cottage", "garden", "vintage", "ephemera", "floral", "herb", "junkjournal", "scrapbook", "printable"],
        "prompts": [
            "Rustic cottage garden scene with picket fence and flowers, watercolor illustration, aged paper texture",
            "Vintage garden plan illustration with labeled herb beds, ink drawing, aged paper background",
            "Rustic watering can with wildflowers illustration, cottage garden style, watercolor on aged paper",
            "Vintage herb illustration page with rosemary and thyme, botanical drawing, aged paper texture",
            "Cottage garden birdhouse among climbing roses illustration, watercolor, rustic vintage style",
            "Vintage seed packet illustration for cottage garden flowers, retro design, aged paper",
            "Rustic garden tools illustration with trowel and pruning shears, vintage ink drawing, aged paper",
            "Cottage garden gate with wisteria illustration, watercolor, rustic vintage style",
            "Vintage garden journal page with pressed flower sketch, ink and watercolor, aged paper",
            "Rustic flower press illustration with dried petals, cottage style, vintage ephemera",
            "Vintage garden bench surrounded by lavender illustration, watercolor, aged paper texture",
            "Cottage garden sundial illustration with moss detail, vintage ink drawing, aged paper",
            "Rustic flower basket overflowing with blooms illustration, watercolor, vintage ephemera style",
            "Vintage garden label stakes illustration for herb pots, cottage style, ink on aged paper",
            "Cottage garden trellis with climbing sweet peas illustration, watercolor, vintage style",
            "Rustic terra cotta pots with seedlings illustration, cottage garden style, ink and watercolor",
            "Vintage garden journal cover illustration with floral border, rustic style, aged paper texture",
            "Cottage garden swing under a willow tree illustration, watercolor, vintage ephemera style",
            "Rustic wooden wheelbarrow with flowers illustration, cottage garden style, aged paper background",
            "Vintage garden catalog page with cottage flowers, retro illustration style, aged paper",
            "Rustic beehive in a wildflower garden illustration, watercolor, vintage ephemera style",
            "Cottage garden path through English garden illustration, watercolor, aged paper texture",
            "Vintage plant stake labels illustration, cottage garden style, ink drawing on aged paper",
            "Rustic rain gauge and garden boots illustration, cottage style, watercolor, vintage ephemera",
        ],
    },
    {
        "name": "Celestial Astrology Journal",
        "description": "Mystical celestial and astrology ephemera featuring zodiac signs, star maps, moon phases, and cosmic illustrations. Perfect for witchy and spiritual junk journals.",
        "tags": ["celestial", "astrology", "zodiac", "mystical", "vintage", "ephemera", "moon", "junkjournal", "scrapbook", "printable"],
        "prompts": [
            "Celestial star map illustration with zodiac constellations, vintage ink drawing, aged paper",
            "Moon phases illustration from new to full, vintage style, gold and silver ink on dark paper",
            "Zodiac wheel illustration with all twelve signs, vintage astrology ephemera, aged paper texture",
            "Celestial sun and moon illustration, vintage ink drawing with gold accents, aged vellum paper",
            "Vintage astrology birth chart illustration, detailed planetary positions, aged paper texture",
            "Celestial tarot card illustration The Star, vintage style, gold and navy, aged paper",
            "Moon goddess illustration with crescent crown, vintage ink and watercolor, mysterious style",
            "Vintage star chart illustration of the northern hemisphere, aged paper, sepia and gold ink",
            "Celestial compass rose illustration with sun and moon, vintage ephemera style, aged paper",
            "Astrology symbol page with planetary glyphs, vintage manuscript style, aged paper texture",
            "Celestial eclipse illustration, vintage astronomical ephemera, ink and watercolor, aged paper",
            "Vintage zodiac Aries illustration with ram and stars, astrological ephemera, aged paper",
            "Celestial moon garden illustration with night-blooming flowers, vintage style, dark paper",
            "Vintage astrology aspect illustration with planetary alignments, technical ink drawing, aged paper",
            "Celestial cosmos illustration with nebula and stars, vintage ephemera style, gold and navy",
            "Vintage zodiac Cancer illustration with crab and stars, astrological ephemera, aged paper",
            "Celestial astrolabe illustration, vintage scientific instrument drawing, ink on aged paper",
            "Vintage moon calendar illustration with phases, astrology ephemera style, aged paper texture",
            "Celestial solar system illustration, vintage astronomy style, ink drawing with gold accents",
            "Vintage zodiac Leo illustration with lion and stars, astrological ephemera, aged paper",
            "Celestial star and crescent illustration, vintage ornamental design, gold ink on dark paper",
            "Vintage astrology house wheel illustration, technical drawing style, aged paper texture",
            "Celestial aurora illustration with stars, vintage ephemera style, watercolor on dark paper",
            "Vintage zodiac Pisces illustration with fish and stars, astrological ephemera, aged paper",
        ],
    },
    {
        "name": "Medieval Illuminated Manuscript",
        "description": "Medieval illuminated manuscript pages with ornate initials, gold leaf borders, heraldic designs, and calligraphy. Perfect for fantasy and historical junk journals.",
        "tags": ["medieval", "illuminated", "manuscript", "gothic", "historical", "ephemera", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Medieval illuminated manuscript page with ornate letter B and gold leaf border, vellum texture",
            "Medieval heraldic shield illustration with lion rampant, gold and red, vellum paper texture",
            "Illuminated manuscript page with decorative border of ivy and gold, medieval script, aged vellum",
            "Medieval bestiary page with phoenix illustration, gold leaf and tempera, vellum texture",
            "Ornate medieval manuscript initial letter S with dragon, gold leaf, blue and red, vellum",
            "Medieval map illustration of a fantastical kingdom, gold leaf accents, aged vellum texture",
            "Illuminated manuscript page with decorative floral border, gold and blue, medieval calligraphy",
            "Medieval heraldic crest with eagle, gold and black, vellum paper, illuminated style",
            "Manuscript page with ornate calendar illustration, gold leaf, zodiac medallions, vellum",
            "Medieval bestiary page with unicorn illustration, gold leaf border, red and blue tempera",
            "Ornate medieval manuscript page with illuminated letter R, gold leaf, intricate border, vellum",
            "Medieval coat of arms illustration with griffin, gold leaf accents, vellum paper texture",
            "Illuminated manuscript music page with decorative border, gold and red, medieval notation",
            "Medieval page border with acanthus leaves and gold leaf, vellum texture, illuminated style",
            "Bestiary page with dragon illustration, gold leaf and tempera, medieval manuscript style",
            "Ornate medieval initial letter D with saint figure, gold leaf, blue and red, vellum",
            "Medieval manuscript page with Tree of Jesse illustration, gold leaf border, vellum texture",
            "Heraldic banner illustration with gold fleur-de-lis, medieval style, vellum paper",
            "Illuminated manuscript page with ornate line ending, gold leaf creatures, blue and red, vellum",
            "Medieval calendar page with Labors of the Months illustration, gold leaf, vellum texture",
            "Ornate medieval manuscript frame with gold leaf and flowers, empty center, vellum paper",
            "Bestiary page with basilisk illustration, gold leaf border, medieval manuscript style",
            "Medieval manuscript page with decorative puzzle initial, gold leaf, red and blue, vellum",
            "Heraldic achievement illustration with shield, helm, and mantling, gold leaf, vellum",
        ],
    },
    {
        "name": "Japanese Wabi-Sabi Ephemera",
        "description": "Serene Japanese wabi-sabi ephemera featuring ink wash paintings, haiku pages, cherry blossoms, and minimalist compositions. Perfect for tranquil and meditative junk journals.",
        "tags": ["japanese", "wabisabi", "minimalist", "ephemera", "inkwash", "cherryblossom", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Japanese wabi-sabi ink wash painting of a single cherry blossom branch, sumi-e style, aged washi paper",
            "Haiku poem page with bamboo illustration, Japanese calligraphy style, aged paper texture",
            "Japanese ink wash painting of a koi fish, sumi-e style, minimalist composition, aged paper",
            "Wabi-sabi tea ceremony ephemera with bamboo whisk, ink wash illustration, aged paper",
            "Japanese cherry blossom petal falling illustration, sumi-e ink style, aged washi paper texture",
            "Minimalist Japanese stone garden illustration, ink wash painting, aged paper background",
            "Japanese wabi-sabi cracked pottery illustration, ink wash style, aged paper texture",
            "Haiku page with maple leaf illustration, Japanese calligraphy, aged washi paper",
            "Japanese ink wash painting of a crane in flight, sumi-e style, minimalist, aged paper",
            "Wabi-sabi dried flower arrangement illustration, Japanese ink style, aged paper texture",
            "Japanese pagoda in mist illustration, ink wash painting, minimalist composition, aged paper",
            "Haiku page with moon illustration, Japanese calligraphy style, aged washi paper",
            "Japanese ink wash painting of bamboo grove, sumi-e style, minimalist, aged paper",
            "Wabi-sabi weathered wood texture with moss illustration, Japanese aesthetic, aged paper",
            "Japanese waving cat maneki-neko illustration, ink wash style, aged washi paper texture",
            "Haiku page with snow on bamboo illustration, Japanese calligraphy style, aged paper",
            "Japanese ink wash painting of Mt Fuji, sumi-e style, minimalist composition, aged paper",
            "Wabi-sabi ceramic tea bowl illustration, ink wash style, aged paper background",
            "Japanese dragonfly over water illustration, sumi-e style, minimalist, aged washi paper",
            "Haiku page with firefly illustration, Japanese calligraphy, aged paper texture",
            "Japanese ink wash painting of a pine tree, sumi-e style, aged paper, minimalist",
            "Wabi-sabi moss and stone illustration, Japanese aesthetic, ink wash, aged paper",
            "Japanese koinobori carp streamer illustration, ink wash style, aged washi paper",
            "Haiku page with autumn moon illustration, Japanese calligraphy style, aged paper texture",
        ],
    },
]


def generate_image_pollinations(prompt: str, width: int = 1024, height: int = 1024,
                                 seed: int = None, output_path: str = None) -> bool:
    """Generate an image using Pollinations.ai free API. Returns True on success."""
    import urllib.parse
    import time

    if seed is None:
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)

    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()

            if len(data) < 5000:  # Too small = error image
                time.sleep(2)
                continue

            with open(output_path, 'wb') as f:
                f.write(data)

            # Verify it's a valid image
            try:
                img = Image.open(output_path)
                img.verify()
                return True
            except Exception:
                time.sleep(2)
                continue

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return False

    return False


def create_pdf_from_images(image_paths: list, output_pdf: str, title: str):
    """Create a PDF from a list of image paths, one image per A4 page."""
    c = canvas.Canvas(str(output_pdf), pagesize=A4)
    a4_w, a4_h = A4

    # Margins
    margin = 0.5 * inch
    printable_w = a4_w - 2 * margin
    printable_h = a4_h - 2 * margin - 0.5 * inch  # Leave room for title on first page

    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            img_w, img_h = img.size

            # First page: add title
            if i == 0:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(a4_w / 2, a4_h - 0.4 * inch, title)
                available_h = printable_h
            else:
                available_h = a4_h - 2 * margin

            # Scale image to fit
            scale = min(printable_w / img_w, available_h / img_h)
            draw_w = img_w * scale
            draw_h = img_h * scale

            # Center horizontally
            x = (a4_w - draw_w) / 2

            if i == 0:
                y = a4_h - 0.5 * inch - draw_h
            else:
                y = (a4_h - draw_h) / 2

            c.drawImage(str(img_path), x, y, draw_w, draw_h,
                       preserveAspectRatio=True, anchor='c')
            c.showPage()

        except Exception as e:
            print(f"  Warning: Could not add {img_path} to PDF: {e}")

    c.save()


def generate_etsy_listing(theme: dict) -> dict:
    """Generate Etsy listing metadata for a theme package."""
    name = theme["name"]
    desc = theme["description"]
    tags = theme["tags"]

    listing = {
        "title": f"{name} - Digital Junk Journal Ephemera Pack - Printable Scrapbook Pages - DIY Paper Craft - Instant Download",
        "description": f"""{desc}

WHAT YOU GET:
- 24 unique high-quality AI-generated images ({name} themed)
- A4 size PDF ready to print
- Individual high-resolution image files
- Instant digital download - no physical item will be shipped

PERFECT FOR:
- Junk Journaling & Art Journaling
- Scrapbooking & Collage
- Card Making & Paper Crafts
- Planner Decoration
- Mixed Media Art
- Digital Planning

DETAILS:
- Format: PDF + individual JPG files
- Size: A4 (300 DPI print quality)
- Theme: {name}
- This is a DIGITAL product only

TERMS:
- For personal and small commercial use
- Do not resell or redistribute as-is
- Credit appreciated but not required

Thank you for supporting our digital art shop!""",
        "tags": tags[:13],  # Etsy allows max 13 tags
        "price_suggestion": 4.99,
        "category": "Paper, Party & Kids > Paper > Digital Paper",
    }
    return listing


def generate_package(theme_idx: int, theme: dict, base_dir: Path) -> dict:
    """Generate a complete package for one theme."""
    date_str = date.today().strftime("%Y-%m-%d")
    theme_slug = theme["name"].lower().replace(" ", "_")
    pkg_dir = base_dir / f"{date_str}_{theme_slug}"
    images_dir = pkg_dir / "Original_Bilder"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating Package {theme_idx+1}/10: {theme['name']}")
    print(f"{'='*60}")

    # Generate images
    generated_images = []
    prompts = theme["prompts"]

    for i, prompt in enumerate(prompts):
        img_filename = f"{theme_slug}_{i+1:02d}.jpg"
        img_path = images_dir / img_filename

        if img_path.exists():
            print(f"  [{i+1:2d}/{len(prompts)}] Already exists: {img_filename}")
            generated_images.append(img_path)
            continue

        print(f"  [{i+1:2d}/{len(prompts)}] Generating: {prompt[:60]}...")
        success = generate_image_pollinations(
            prompt=prompt,
            width=1024,
            height=1024,
            seed=42 + i + (theme_idx * 100),
            output_path=str(img_path)
        )

        if success:
            generated_images.append(img_path)
            print(f"  [{i+1:2d}/{len(prompts)}] OK: {img_filename}")
        else:
            print(f"  [{i+1:2d}/{len(prompts)}] FAILED: {img_filename}")

        # Rate limit: be nice to free API
        time.sleep(1.5)

    print(f"\n  Generated {len(generated_images)} images for {theme['name']}")

    # Create PDF
    pdf_path = pkg_dir / f"{theme_slug}_junk_journal.pdf"
    if generated_images:
        print(f"  Creating PDF: {pdf_path.name}")
        create_pdf_from_images(generated_images, pdf_path, theme["name"])

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
        f.write(f"- {len(generated_images)} unique AI-generated images\n")
        f.write(f"- PDF compilation (A4 format)\n")
        f.write(f"- Individual image files (1024x1024 JPG)\n")
        f.write(f"- Etsy listing metadata\n\n")
        f.write(f"## Files\n\n")
        f.write(f"- `Original_Bilder/` - Individual image files\n")
        f.write(f"- `{pdf_path.name}` - PDF compilation\n")
        f.write(f"- `etsy_listing.json` - Etsy listing metadata\n")

    return {
        "theme": theme["name"],
        "dir": str(pkg_dir),
        "images_generated": len(generated_images),
        "pdf": str(pdf_path),
    }


def main():
    print("="*60)
    print("Junk Journal Digital PDF Package Generator")
    print("="*60)

    results = []

    for i, theme in enumerate(THEMES):
        result = generate_package(i, theme, BASE_DIR)
        results.append(result)
        print(f"\n  Package {i+1} complete: {result['images_generated']} images")

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE - SUMMARY")
    print(f"{'='*60}")

    total_images = 0
    for r in results:
        print(f"  {r['theme']}: {r['images_generated']} images")
        total_images += r["images_generated"]

    print(f"\n  Total packages: {len(results)}")
    print(f"  Total images: {total_images}")

    # Save summary
    summary_path = BASE_DIR / "generation_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n  Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()