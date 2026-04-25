#!/usr/bin/env python3
"""
Junk Journal Image Generator using cosxl HF Space (cloud compute via gradio_client).
Generates 1024x1024 images, upscales to A4 300 DPI, creates PDFs & Etsy listings.

Usage: python3 generate_cosxl.py [--theme THEME_INDEX] [--limit N]
  --theme  : only generate for one theme (0-9)
  --limit  : only generate N images per theme (default 20)
  --skip   : skip themes that already have enough images
"""

import os
import sys
import json
import time
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import date

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from gradio_client import Client

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATE_STR = str(date.today())
A4_WIDTH = 2480
A4_HEIGHT = 3508

# Quality suffix to improve output
QUALITY_SUFFIX = ", high quality, detailed, professional illustration, junk journal ephemera"

# ---------------------------------------------------------------------------
# Theme definitions — 10 themes, 24 prompts each
# ---------------------------------------------------------------------------
THEMES = [
    {
        "name": "Victorian Botanical Ephemera",
        "slug": "victorian_botanical_ephemera",
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
        "slug": "dark_academia_gothic",
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
        "slug": "vintage_steampunk_apothecary",
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
        "slug": "alice_in_wonderland_grunge",
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
        "slug": "art_nouveau_flower_fairies",
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
        "slug": "vintage_travel_memorabilia",
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
        "slug": "rustic_cottage_garden",
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
        "slug": "celestial_astrology_journal",
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
        "slug": "medieval_illuminated_manuscript",
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
        "slug": "japanese_wabi-sabi_ephemera",
        "description": "Serene Japanese wabi-sabi ephemera featuring ink wash paintings, minimalist botanical sketches, haiku calligraphy, and imperfect beauty elements for meditative junk journal pages.",
        "tags": ["japanese", "wabisabi", "minimalist", "inkwash", "calligraphy", "ephemera", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Japanese wabi-sabi ink wash painting of a single cherry blossom branch, minimalist sumi-e style on aged washi paper",
            "Vintage Japanese haiku calligraphy on aged paper, brush ink characters with simple bamboo illustration",
            "Wabi-sabi kintsugi repaired bowl illustration, Japanese ink drawing with gold repair lines, aged paper",
            "Japanese minimalist ink wash of bamboo grove in rain, sumi-e style on textured washi paper",
            "Vintage Japanese tea ceremony ephemera with chawan illustration, wabi-sabi aesthetic, sepia ink on aged paper",
            "Wabi-sabi dried leaf and moss arrangement, Japanese nature sketch style, muted ink on cream paper",
            "Japanese ink wash painting of a single koi fish, minimalist sumi-e style on aged washi paper",
            "Vintage Japanese postcard with Mount Fuji ink illustration, faded sepia tones on aged paper",
            "Wabi-sabi weathered stone in moss garden, Japanese ink sketch style, muted tones on textured paper",
            "Japanese brush calligraphy with simple pine branch, wabi-sabi style on aged paper",
            "Vintage Japanese matcha whisk and bowl illustration, minimalist ink drawing on cream paper",
            "Wabi-sabi cracked pottery with gold repair, Japanese kintsugi illustration, gold and ink on aged paper",
            "Japanese ink wash of a quiet temple gate in snow, minimalist sumi-e style on textured washi paper",
            "Vintage Japanese envelope with red seal, wabi-sabi ephemera, muted tones on aged paper",
            "Wabi-sabi arrangement of three river stones, Japanese ink sketch, minimalist style on cream paper",
            "Japanese ink wash painting of persimmon branches, sumi-e style, warm muted tones on aged washi paper",
            "Vintage Japanese poem card with calligraphy and simple flower, wabi-sabi aesthetic, aged paper texture",
            "Wabi-sabi weathered wooden gate with moss, Japanese ink illustration, muted colors on textured paper",
            "Japanese minimalist ink wash of rain on a pond, sumi-e style, grey tones on aged washi paper",
            "Vintage Japanese stamp with crane illustration, wabi-sabi ephemera, red and sepia on aged paper",
            "Wabi-sabi fallen autumn leaf on weathered stone, Japanese ink sketch, warm muted tones on cream paper",
            "Japanese ink wash painting of a thatched roof cottage, minimalist sumi-e style, aged washi paper",
            "Vintage Japanese incense package with calligraphy, wabi-sabi style ephemera, muted tones on aged paper",
            "Wabi-sabi Zen garden raked sand and rocks, Japanese ink illustration, minimalist style on textured paper",
        ],
    },
]


def resize_to_a4(img_path, output_path):
    """Resize image to A4 at 300 DPI (2480 x 3508), preserving aspect ratio with warm paper padding."""
    img = Image.open(img_path)

    # Create A4 canvas with warm paper-tone background
    canvas_img = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 250, 240))

    # Calculate scaling to fit within A4 while maintaining aspect ratio
    img_ratio = img.width / img.height
    a4_ratio = A4_WIDTH / A4_HEIGHT

    if img_ratio > a4_ratio:
        new_width = A4_WIDTH
        new_height = int(A4_WIDTH / img_ratio)
    else:
        new_height = A4_HEIGHT
        new_width = int(A4_HEIGHT * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Center on canvas
    x_offset = (A4_WIDTH - new_width) // 2
    y_offset = (A4_HEIGHT - new_height) // 2
    canvas_img.paste(img_resized, (x_offset, y_offset))

    canvas_img.save(str(output_path), 'JPEG', quality=95, dpi=(300, 300))
    return output_path


def create_pdf(theme_slug, image_paths, output_dir):
    """Create a PDF from a list of image paths, each page A4."""
    pdf_path = output_dir / f"{theme_slug}_junk_journal.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    for img_path in image_paths:
        c.drawImage(str(img_path), 0, 0, width=A4[0], height=A4[1])
        c.showPage()
    c.save()
    return pdf_path


def generate_etsy_listing(theme):
    """Generate SEO-optimized Etsy listing info."""
    name = theme["name"]
    slug = theme["slug"]
    desc = theme["description"]
    tags = theme["tags"][:13]

    title = f"{name} Digital Paper Pack - 20 Vintage Junk Journal Pages | Printable A4 300 DPI | Digital Download"

    description = f"""**{name} - Digital Junk Journal Paper Pack**

{desc}

**WHAT YOU GET:**
- 20 unique high-resolution digital images
- A4 size (210mm x 297mm) at 300 DPI - perfect for printing
- PDF compilation + individual JPG files included
- Instant digital download - no physical item will be shipped

**PERFECT FOR:**
- Junk journaling & art journaling
- Scrapbooking & collage
- Card making & mixed media
- Printable crafting projects
- Digital art backgrounds

**IMPORTANT:** This is a DIGITAL product. No physical item will be shipped. Download immediately after purchase.

**TERMS:** Personal and small commercial use. Do not resell or redistribute the digital files.

Thank you for visiting our shop! ♥

**Tags:** {', '.join(tags)}
"""

    return {
        "title": title[:140],
        "description": description,
        "tags": tags
    }


def generate_one_image(client, prompt, attempt=1, max_attempts=3):
    """Generate a single image using cosxl. Returns file path or None on failure."""
    try:
        full_prompt = prompt + QUALITY_SUFFIX
        result = client.predict(
            prompt=full_prompt,
            negative_prompt="blurry, low quality, watermark, text overlay, distorted",
            guidance_scale=7,
            steps=25,
            api_name="/run_normal"
        )
        if result and os.path.exists(result):
            return result
        return None
    except Exception as e:
        if attempt < max_attempts:
            wait_time = attempt * 15
            print(f"    Retry {attempt}/{max_attempts} after error: {e}")
            time.sleep(wait_time)
            return generate_one_image(client, prompt, attempt + 1, max_attempts)
        else:
            print(f"    FAILED after {max_attempts} attempts: {e}")
            return None


def run(skip_existing=False, theme_idx=None, limit=20):
    """Main generation loop."""
    print("=" * 60)
    print("JUNK JOURNAL GENERATOR — cosxl HF Space")
    print("=" * 60)

    # Connect to cosxl
    print("\nConnecting to multimodalart/cosxl HF Space...")
    try:
        client = Client("multimodalart/cosxl")
        print("Connected!")
    except Exception as e:
        print(f"FATAL: Could not connect to cosxl: {e}")
        sys.exit(1)

    # Select themes
    if theme_idx is not None:
        themes_to_process = [(theme_idx, THEMES[theme_idx])]
    else:
        themes_to_process = list(enumerate(THEMES))

    total_generated = 0
    total_failed = 0

    for idx, theme in themes_to_process:
        slug = theme["slug"]
        theme_dir = BASE_DIR / f"{DATE_STR}_{slug}"
        orig_dir = theme_dir / "Original_Bilder"
        a4_dir = theme_dir / "A4_300DPI"
        orig_dir.mkdir(parents=True, exist_ok=True)
        a4_dir.mkdir(parents=True, exist_ok=True)

        # Count existing good images (not 768x768)
        existing_good = 0
        for f in orig_dir.glob("*"):
            if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
                try:
                    img = Image.open(f)
                    if img.width >= 1024 and img.height >= 1024:
                        existing_good += 1
                except:
                    pass

        needed = limit - existing_good
        if skip_existing and needed <= 0:
            print(f"\n[{slug}] Already has {existing_good} quality images — SKIPPING")
            continue

        print(f"\n{'='*50}")
        print(f"[{slug}] Theme {idx+1}/10 — {theme['name']}")
        print(f"  Existing quality images: {existing_good}")
        print(f"  Target: {limit}, Need to generate: {max(0, needed)}")
        print(f"{'='*50}")

        # Generate images
        prompts = theme["prompts"][:max(needed, len(theme["prompts"]))]
        if needed <= 0:
            prompts = []  # Already have enough

        generated_this_theme = 0
        img_num = existing_good + 1

        for pidx, prompt in enumerate(prompts):
            if generated_this_theme >= needed:
                break

            print(f"\n  [{img_num}/{limit}] Generating: {prompt[:70]}...")

            file_path = generate_one_image(client, prompt)
            if file_path is None:
                total_failed += 1
                continue

            # Convert to PNG and save
            try:
                src_img = Image.open(file_path)
                if src_img.mode == 'RGBA':
                    src_img = src_img.convert('RGB')

                # Save original size
                orig_path = orig_dir / f"{slug}_{img_num:02d}.png"
                src_img.save(str(orig_path), 'PNG')

                # Create A4 version
                a4_path = a4_dir / f"{slug}_{img_num:02d}_a4.jpg"
                resize_to_a4(file_path, a4_path)

                generated_this_theme += 1
                total_generated += 1
                img_num += 1

                print(f"    OK -> {orig_path.name} ({src_img.width}x{src_img.height})")

            except Exception as e:
                print(f"    ERROR saving: {e}")
                total_failed += 1

            # Rate limiting — be gentle with free HF Space
            time.sleep(3)

        # Generate PDF and Etsy listing for this theme
        all_a4_images = sorted(a4_dir.glob("*.jpg"))
        if all_a4_images:
            pdf_path = create_pdf(slug, all_a4_images, theme_dir)
            print(f"\n  PDF: {pdf_path.name} ({len(all_a4_images)} pages)")
        else:
            print(f"\n  WARNING: No A4 images found for PDF")

        # Etsy listing
        listing = generate_etsy_listing(theme)
        listing_path = theme_dir / "etsy_listing.json"
        with open(listing_path, 'w') as f:
            json.dump(listing, f, indent=2, ensure_ascii=False)

        # Also save as human-readable text
        info_path = theme_dir / "Etsy_Listing_Info.txt"
        with open(info_path, 'w') as f:
            f.write(f"TITLE:\n{listing['title']}\n\n")
            f.write(f"TAGS:\n{', '.join(listing['tags'])}\n\n")
            f.write(f"DESCRIPTION:\n{listing['description']}\n")

        # README
        readme_path = theme_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(f"# {theme['name']}\n\n")
            f.write(f"{theme['description']}\n\n")
            f.write(f"**Images:** {len(all_a4_images)}\n")
            f.write(f"**Resolution:** A4 300 DPI (2480x3508)\n")
            f.write(f"**Format:** PNG originals + JPG A4 + PDF\n\n")
            f.write(f"Generated: {DATE_STR}\n")

        print(f"  Etsy listing & README written")

    # Summary
    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE")
    print(f"  Total generated: {total_generated}")
    print(f"  Total failed: {total_failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate junk journal images")
    parser.add_argument("--theme", type=int, default=None, help="Theme index (0-9)")
    parser.add_argument("--limit", type=int, default=20, help="Images per theme")
    parser.add_argument("--skip", action="store_true", help="Skip themes with enough images")
    parser.add_argument("--all", action="store_true", help="Generate all 24 prompts per theme")
    args = parser.parse_args()

    limit = 24 if args.all else args.limit
    run(skip_existing=args.skip, theme_idx=args.theme, limit=limit)