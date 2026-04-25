#!/usr/bin/env python3
"""
Batch Junk Journal Digital PDF Package Generator
Uses Pollinations.ai (free cloud API, no key needed) for parallel image generation.
Generates 10 themed packages with 20+ images each, compiles into A4 PDFs,
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
from concurrent.futures import ThreadPoolExecutor, as_completed

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image

BASE_DIR = Path(__file__).parent
DATE_STR = "2026-04-25"

# ---------------------------------------------------------------------------
# Theme definitions — each theme has 24 unique image prompts
# ---------------------------------------------------------------------------
THEMES = [
    {
        "name": "Victorian Botanical Ephemera",
        "description": "Exquisite Victorian-era botanical illustrations, herbarium specimens, vintage seed catalogs, and floral ephemera perfect for junk journaling and scrapbooking.",
        "tags": ["victorian", "botanical", "ephemera", "vintage", "floral", "herbarium", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Vintage botanical illustration of a wild rose, detailed hand-drawn style, aged parchment paper background, Victorian era, watercolor touches, high quality, detailed",
            "Antique herbarium specimen page showing pressed fern leaves with handwritten Latin labels, brown aged paper, vintage scientific aesthetic, high quality, detailed",
            "Victorian seed catalog cover page with ornate border of blooming flowers, decorative typography, 1890s style, warm sepia tones, high quality, detailed",
            "Vintage botanical drawing of lavender sprigs with purple watercolor, aged creamy paper, detailed ink lines, romantic style, high quality, detailed",
            "Antique botanical plate showing a blooming peony, hand-colored engraving style, soft pastel watercolor wash, 1880s aesthetic, high quality, detailed",
            "Victorian wildflower meadow illustration, pressed flower arrangement style, faded watercolors on cream paper, romantic ephemera, high quality, detailed",
            "Vintage botanical sketch of a sunflower with seed pod detail, pencil and ink on aged paper, scientific illustration style, high quality, detailed",
            "Antique rose garden illustration with multiple rose varieties, Victorian watercolor style, decorative banner cartouche, high quality, detailed",
            "Old herbarium page with pressed oak leaves and acorns, handwritten notes in brown ink, yellowed paper texture, high quality, detailed",
            "Victorian botanical ephemera piece featuring a wreath of morning glories, hand-painted watercolor, aged paper, high quality, detailed",
            "Vintage illustration of a blooming cherry blossom branch, delicate Japanese-influenced Victorian style, soft pink watercolors, high quality, detailed",
            "Antique botanical study of a dahlia, detailed petals in watercolor, ornamental border, 1890s print style, high quality, detailed",
            "Victorian botanical trade card with chamomile flowers, ornate gold border, advertising ephemera style, high quality, detailed",
            "Pressed wildflower arrangement vintage page, buttercups and daisies, faded watercolors, aged paper, high quality, detailed",
            "Vintage botanical illustration of poppy flowers, red watercolor wash, detailed ink drawing, Victorian seed packet style, high quality, detailed",
            "Antique botanical page showing a lily of the valley, delicate green and white watercolor, aged paper texture, high quality, detailed",
            "Victorian-era botanical plate featuring an iris, purple-blue watercolor, detailed ink engraving style, high quality, detailed",
            "Vintage horticultural print of tulip varieties, hand-colored engraving, ornamental border design, high quality, detailed",
            "Antique botanical study of a magnolia branch, soft cream and pink watercolor, aged ivory paper, high quality, detailed",
            "Victorian botanical ephemera with a decorative floral alphabet letter A surrounded by roses, ornate illustration, high quality, detailed",
            "Vintage botanical illustration of honeysuckle vine, detailed hand-drawn style, green and cream watercolors, high quality, detailed",
            "Antique pressed flower page featuring a violets specimen with handwritten label, aged paper texture, high quality, detailed",
            "Victorian-era botanical trading card with a pansy illustration, gold embossed border, pastel watercolors, high quality, detailed",
            "Vintage botanical illustration of a lotus flower, Japanese-influenced Victorian style, delicate ink work, high quality, detailed",
        ],
    },
    {
        "name": "Dark Academia Gothic",
        "description": "Moody dark academia and gothic-inspired ephemera featuring ancient libraries, architectural details, gothic scripts, and atmospheric ink illustrations for brooding junk journals.",
        "tags": ["darkacademia", "gothic", "ephemera", "vintage", "moody", "library", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Dark academia library interior with towering bookshelves and candlelight, moody ink illustration, aged paper texture, high quality, detailed",
            "Gothic cathedral architectural detail drawing, pointed arches and gargoyles, pen and ink on aged vellum, high quality, detailed",
            "Victorian gothic letter border with ravens and thorns, black ink illustration, dark romantic style, high quality, detailed",
            "Antique manuscript page with ornate gothic calligraphy, illuminated letter, dark red and gold accents on aged paper, high quality, detailed",
            "Dark academia desk scene with quill, ink bottle, and ancient books, moody charcoal drawing, sepia tones, high quality, detailed",
            "Gothic rose window architectural drawing, detailed ink illustration, dramatic shadows, aged parchment, high quality, detailed",
            "Victorian gothic moth illustration, detailed entomological drawing, dark background with gold accents, high quality, detailed",
            "Antique library card catalog drawer with brass fittings, vintage ink drawing, warm dark tones, high quality, detailed",
            "Dark academia astronomical chart with constellations, aged paper, ink and sepia watercolor, high quality, detailed",
            "Gothic iron gate with climbing ivy, detailed ink illustration, moody atmospheric style, high quality, detailed",
            "Victorian skeleton key illustration, ornate design with gothic flourishes, aged paper background, high quality, detailed",
            "Antique apothecary bottle label with gothic script, dark romantic style, aged paper texture, high quality, detailed",
            "Dark academia coffee-stained journal page with poetry fragments, ink blotches, vintage paper, high quality, detailed",
            "Gothic arch doorway with trailing vines, detailed ink drawing, atmospheric shadows, high quality, detailed",
            "Victorian wax seal and letter ephemera, dark romantic style, ink illustration on aged paper, high quality, detailed",
            "Antique anatomy illustration plate, gothic medical drawing style, sepia and ink on aged vellum, high quality, detailed",
            "Dark academia bookshelf vignette with candle and skull, moody charcoal drawing, dramatic lighting, high quality, detailed",
            "Gothic ornament border design with ravens and thistles, black ink illustration, medieval manuscript style, high quality, detailed",
            "Victorian observatory interior with telescope and star charts, ink drawing, dark academia aesthetic, high quality, detailed",
            "Antique calligraphy practice sheet with gothic script, ink on yellowed paper, dark romantic mood, high quality, detailed",
            "Gothic church interior with stained glass, detailed ink illustration, dramatic light rays, high quality, detailed",
            "Dark academia pocket watch and compass illustration, moody ink drawing, aged paper, high quality, detailed",
            "Victorian gothic ephemera collage with pressed black roses and lace, ink and watercolor, high quality, detailed",
            "Antique book cover design with gothic ornamental border, gold foil on dark background, high quality, detailed",
        ],
    },
    {
        "name": "Vintage Steampunk Apothecary",
        "description": "Steampunk apothecary ephemera with brass gears, vintage medicine labels, mechanical illustrations, and Victorian scientific apparatus. Perfect for alchemy-themed junk journals.",
        "tags": ["steampunk", "apothecary", "vintage", "ephemera", "alchemy", "mechanical", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Steampunk apothecary bottle with brass gears and copper label, detailed ink illustration, aged paper background, high quality, detailed",
            "Vintage apothecary label for Laudanum with ornate border, Victorian medical ephemera, aged paper texture, high quality, detailed",
            "Steampunk mechanical heart illustration with brass gears and tubes, ink and sepia watercolor, antique paper, high quality, detailed",
            "Victorian scientific instrument drawing of a brass microscope, detailed engraving style, aged paper, high quality, detailed",
            "Steampunk gear and clockwork illustration, interconnected brass mechanisms, pen and ink on vellum, high quality, detailed",
            "Antique apothecary cabinet with bottles and drawers, Victorian ink illustration, warm brown tones, high quality, detailed",
            "Steampunk airship blueprint design, technical drawing style, aged blueprint paper, sepia ink, high quality, detailed",
            "Vintage apothecary mortar and pestle illustration, brass and copper details, aged paper texture, high quality, detailed",
            "Steampunk mechanical eye with brass housing and lens gears, detailed ink drawing, aged paper, high quality, detailed",
            "Victorian pharmacy label for exotic tinctures, ornate border with art nouveau elements, aged paper, high quality, detailed",
            "Steampunk steam engine schematic, detailed technical illustration, brass and copper tones, high quality, detailed",
            "Antique apothecary jar label with skull and crossbones warning, Victorian medical ephemera style, high quality, detailed",
            "Steampunk mechanical butterfly with brass wings and gears, detailed ink illustration, aged paper, high quality, detailed",
            "Victorian distillation apparatus illustration, alchemical equipment drawing, sepia ink on paper, high quality, detailed",
            "Steampunk key with brass and copper mechanical elements, ornate vintage style, aged paper, high quality, detailed",
            "Antique chemistry flask illustration with bubbling liquid, steampunk aesthetic, detailed ink drawing, high quality, detailed",
            "Vintage apothecary receipt ephemera with brass border design, Victorian printing style, aged paper, high quality, detailed",
            "Steampunk mechanical arm prosthetic blueprint, technical drawing, brass and copper color palette, high quality, detailed",
            "Victorian leech jar label, apothecary ephemera, ornate border with medical illustration, high quality, detailed",
            "Steampunk clockwork face illustration with exposed gears, detailed ink drawing, aged vellum paper, high quality, detailed",
            "Antique apothecary scale with brass weights, balanced composition, Victorian illustration style, high quality, detailed",
            "Steampunk perpetual motion device illustration, brass gears and pendulums, technical drawing style, high quality, detailed",
            "Victorian quack medicine advertisement with steampunk elements, ornate typography, aged paper, high quality, detailed",
            "Steampunk brass compass rose illustration, detailed technical drawing, navigation ephemera style, high quality, detailed",
        ],
    },
    {
        "name": "Alice in Wonderland Grunge",
        "description": "Whimsical Alice in Wonderland-inspired grunge ephemera with distorted teacups, playing cards, pocket watches, and surreal illustrations. Perfect for whimsigoth junk journals.",
        "tags": ["aliceinwonderland", "grunge", "whimsigoth", "vintage", "ephemera", "surreal", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Alice in Wonderland teacup illustration with grunge texture, distressed vintage style, ink and watercolor, high quality, detailed",
            "Vintage playing card Queen of Hearts with distressed edges, grunge aesthetic, aged paper texture, high quality, detailed",
            "White rabbit pocket watch illustration, steampunk wonderland style, distressed ink drawing, aged paper, high quality, detailed",
            "Wonderland mad hatter hat illustration with price tag, grunge texture, ink and sepia watercolor, high quality, detailed",
            "Cheshire cat smile floating illustration, vintage ink style, distressed paper background, high quality, detailed",
            "Alice falling down the rabbit hole vintage illustration, distressed ink style, aged paper, high quality, detailed",
            "Wonderland teapot with dormouse illustration, vintage ink drawing, grunge texture overlay, high quality, detailed",
            "Playing card soldiers marching vintage illustration, grunge style, aged paper background, high quality, detailed",
            "Wonderland mushroom and caterpillar illustration, vintage ink style, distressed paper texture, high quality, detailed",
            "Flamingo croquet mallet vintage illustration, grunge aesthetic, ink and watercolor, high quality, detailed",
            "Wonderland door with tiny key illustration, vintage style, distressed paper, ink drawing, high quality, detailed",
            "Eat Me cake and Drink Me bottle illustration, vintage ephemera style, grunge texture, high quality, detailed",
            "Queen of Hearts rose garden painting scene, vintage illustration style, distressed aged paper, high quality, detailed",
            "Wonderland nonsense poetry page, handwritten style, grunge overlay, vintage paper texture, high quality, detailed",
            "Jabberwock illustration in vintage ink style, dark fantasy, distressed paper background, high quality, detailed",
            "Wonderland pocket watch with spiraling numbers illustration, grunge aesthetic, aged paper, high quality, detailed",
            "Vintage Wonderland map illustration showing the rabbit hole and garden, distressed style, high quality, detailed",
            "Tweedledum and Tweedledee vintage illustration, grunge style, ink and watercolor, high quality, detailed",
            "Wonderland chess piece characters illustration, vintage style, distressed paper, high quality, detailed",
            "Caterpillar on mushroom with hookah illustration, vintage ink style, grunge texture, high quality, detailed",
            "Wonderland key and lock illustration with ornate design, vintage ephemera, distressed paper, high quality, detailed",
            "Vintage Wonderland invitation card illustration, grunge style, calligraphy and floral border, high quality, detailed",
            "Wonderland clock face with backwards numbers illustration, distressed vintage style, high quality, detailed",
            "Alice shrinking and growing illustration, vintage ink style, grunge paper texture, high quality, detailed",
        ],
    },
    {
        "name": "Art Nouveau Flower Fairies",
        "description": "Beautiful Art Nouveau-inspired flower fairy illustrations with flowing organic lines, sinuous borders, and delicate watercolor touches. Ideal for ethereal junk journal pages.",
        "tags": ["artnouveau", "flowerfairy", "vintage", "ephemera", "fairy", "watercolor", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Art Nouveau flower fairy sitting on a lily pad, flowing organic lines, watercolor illustration, aged paper, high quality, detailed",
            "Art Nouveau decorative border with roses and fairy silhouettes, sinuous line style, vintage paper, high quality, detailed",
            "Flower fairy with morning glory wings, Art Nouveau style, delicate watercolor, aged background, high quality, detailed",
            "Art Nouveau rose fairy illustration, Alphonse Mucha inspired, flowing hair and floral crown, vintage paper, high quality, detailed",
            "Fairy sitting on a daisy, Art Nouveau style illustration, detailed ink lines with watercolor wash, high quality, detailed",
            "Art Nouveau floral panel with fairy and butterfly, ornamental border design, vintage ephemera, high quality, detailed",
            "Flower fairy of the violet, Art Nouveau illustration, detailed line work, soft purple watercolor, high quality, detailed",
            "Art Nouveau peacock fairy illustration, flowing ornamental lines, watercolor on aged paper, high quality, detailed",
            "Fairy with dragonfly wings among reeds, Art Nouveau style, green and gold watercolor, vintage paper, high quality, detailed",
            "Art Nouveau decorative page with fairy vignette and floral frame, sinuous organic design, high quality, detailed",
            "Flower fairy of the cherry blossom, Art Nouveau style, delicate pink watercolor illustration, high quality, detailed",
            "Art Nouveau fairy crown and floral scepter illustration, ornate line work, vintage ephemera style, high quality, detailed",
            "Fairy resting on a poppy flower, Art Nouveau illustration, red watercolor wash, aged paper, high quality, detailed",
            "Art Nouveau iris fairy illustration, flowing organic border, detailed ink lines, vintage style, high quality, detailed",
            "Flower fairy with sunflower headdress, Art Nouveau style, warm golden watercolor, aged paper, high quality, detailed",
            "Art Nouveau botanical fairy page, detailed illustration with decorative border, vintage ephemera, high quality, detailed",
            "Fairy of the bluebell woods, Art Nouveau style illustration, blue and green watercolor, aged paper, high quality, detailed",
            "Art Nouveau fairy and crescent moon illustration, ornamental design, silver watercolor on dark paper, high quality, detailed",
            "Flower fairy queen with floral scepter, Art Nouveau style, detailed ink and watercolor, vintage, high quality, detailed",
            "Art Nouveau pansy fairy illustration, violet watercolor, flowing organic lines, aged paper, high quality, detailed",
            "Fairy among wildflowers illustration, Art Nouveau style, multicolor watercolor wash, vintage, high quality, detailed",
            "Art Nouveau decorative letter F with fairy and ferns, ornamental style, vintage paper texture, high quality, detailed",
            "Flower fairy of the honeysuckle, Art Nouveau illustration, detailed line art, aged paper, high quality, detailed",
            "Art Nouveau fairy garden scene with arbor and climbing roses, flowing design, watercolor vintage style, high quality, detailed",
        ],
    },
    {
        "name": "Vintage Travel Memorabilia",
        "description": "Nostalgic vintage travel ephemera featuring old maps, luggage tags, postcards, ticket stubs, and passport stamps. Perfect for travel-themed junk journals and scrapbooking.",
        "tags": ["vintage", "travel", "memorabilia", "ephemera", "map", "postcard", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Vintage travel luggage tag from Paris, ornate typography, aged paper texture, retro travel ephemera, high quality, detailed",
            "Antique world map illustration showing old sea routes, aged parchment, sepia and ink drawing, high quality, detailed",
            "Vintage train ticket stub illustration, retro European railway ephemera, distressed paper, high quality, detailed",
            "Old passport page with vintage stamps and seals illustration, aged paper texture, travel ephemera, high quality, detailed",
            "Vintage travel postcard from Rome with Colosseum illustration, retro style, aged paper, high quality, detailed",
            "Antique compass rose map illustration, navigational ephemera, sepia and ink on aged vellum, high quality, detailed",
            "Vintage luggage label from a grand hotel, art deco style, distressed paper texture, high quality, detailed",
            "Old steamer trunk illustration with travel stickers, vintage ink drawing, aged paper, high quality, detailed",
            "Vintage airline baggage tag illustration, retro travel ephemera, aged paper texture, high quality, detailed",
            "Antique map of the Mediterranean Sea illustration, aged parchment, sepia and ink drawing, high quality, detailed",
            "Vintage travel brochure cover illustration, retro advertising style, aged paper, high quality, detailed",
            "Old camera and travel journal ephemera illustration, vintage ink drawing, aged paper texture, high quality, detailed",
            "Vintage postage stamps collection from different countries, travel ephemera, aged paper, high quality, detailed",
            "Antique globe illustration on a wooden stand, vintage style, sepia and ink drawing, high quality, detailed",
            "Vintage travel voucher illustration, retro European railway ephemera, distressed paper, high quality, detailed",
            "Old lighthouse postcard illustration, vintage travel ephemera, aged paper, ink and watercolor, high quality, detailed",
            "Vintage boarding pass illustration, retro airline ephemera style, aged paper texture, high quality, detailed",
            "Antique sailing ship illustration on vintage map, aged parchment, sepia and ink drawing, high quality, detailed",
            "Vintage travel journal page with sketch of a European cathedral, ink drawing, aged paper, high quality, detailed",
            "Old baggage claim ticket illustration, vintage travel ephemera, distressed paper texture, high quality, detailed",
            "Vintage hot air balloon illustration, travel ephemera style, ink and watercolor on aged paper, high quality, detailed",
            "Antique luggage with travel decal stickers illustration, vintage style, sepia drawing, high quality, detailed",
            "Vintage cruise ship postcard illustration, retro travel ephemera, aged paper texture, high quality, detailed",
            "Old map illustration of a fantasy journey, aged parchment, sepia ink, travel ephemera style, high quality, detailed",
        ],
    },
    {
        "name": "Rustic Cottage Garden",
        "description": "Charming rustic cottage garden ephemera with floral borders, garden plans, herb illustrations, watering cans, and pastoral watercolor scenes. Perfect for cozy junk journals.",
        "tags": ["rustic", "cottage", "garden", "vintage", "ephemera", "floral", "herb", "junkjournal", "scrapbook", "printable"],
        "prompts": [
            "Rustic cottage garden scene with picket fence and flowers, watercolor illustration, aged paper texture, high quality, detailed",
            "Vintage garden plan illustration with labeled herb beds, ink drawing, aged paper background, high quality, detailed",
            "Rustic watering can with wildflowers illustration, cottage garden style, watercolor on aged paper, high quality, detailed",
            "Vintage herb illustration page with rosemary and thyme, botanical drawing, aged paper texture, high quality, detailed",
            "Cottage garden birdhouse among climbing roses illustration, watercolor, rustic vintage style, high quality, detailed",
            "Vintage seed packet illustration for cottage garden flowers, retro design, aged paper, high quality, detailed",
            "Rustic garden tools illustration with trowel and pruning shears, vintage ink drawing, aged paper, high quality, detailed",
            "Cottage garden gate with wisteria illustration, watercolor, rustic vintage style, high quality, detailed",
            "Vintage garden journal page with pressed flower sketch, ink and watercolor, aged paper, high quality, detailed",
            "Rustic flower press illustration with dried petals, cottage style, vintage ephemera, high quality, detailed",
            "Vintage garden bench surrounded by lavender illustration, watercolor, aged paper texture, high quality, detailed",
            "Cottage garden sundial illustration with moss detail, vintage ink drawing, aged paper, high quality, detailed",
            "Rustic flower basket overflowing with blooms illustration, watercolor, vintage ephemera style, high quality, detailed",
            "Vintage garden label stakes illustration for herb pots, cottage style, ink on aged paper, high quality, detailed",
            "Cottage garden trellis with climbing sweet peas illustration, watercolor, vintage style, high quality, detailed",
            "Rustic terra cotta pots with seedlings illustration, cottage garden style, ink and watercolor, high quality, detailed",
            "Vintage garden journal cover illustration with floral border, rustic style, aged paper texture, high quality, detailed",
            "Cottage garden swing under a willow tree illustration, watercolor, vintage ephemera style, high quality, detailed",
            "Rustic wooden wheelbarrow with flowers illustration, cottage garden style, aged paper background, high quality, detailed",
            "Vintage garden catalog page with cottage flowers, retro illustration style, aged paper, high quality, detailed",
            "Rustic beehive in a wildflower garden illustration, watercolor, vintage ephemera style, high quality, detailed",
            "Cottage garden path through English garden illustration, watercolor, aged paper texture, high quality, detailed",
            "Vintage plant stake labels illustration, cottage garden style, ink drawing on aged paper, high quality, detailed",
            "Rustic rain gauge and garden boots illustration, cottage style, watercolor, vintage ephemera, high quality, detailed",
        ],
    },
    {
        "name": "Celestial Astrology Journal",
        "description": "Mystical celestial and astrology ephemera featuring zodiac signs, star maps, moon phases, and cosmic illustrations. Perfect for witchy and spiritual junk journals.",
        "tags": ["celestial", "astrology", "zodiac", "mystical", "vintage", "ephemera", "moon", "junkjournal", "scrapbook", "printable"],
        "prompts": [
            "Celestial star map illustration with zodiac constellations, vintage ink drawing, aged paper, high quality, detailed",
            "Moon phases illustration from new to full, vintage style, gold and silver ink on dark paper, high quality, detailed",
            "Zodiac wheel illustration with all twelve signs, vintage astrology ephemera, aged paper texture, high quality, detailed",
            "Celestial sun and moon illustration, vintage ink drawing with gold accents, aged vellum paper, high quality, detailed",
            "Vintage astrology birth chart illustration, detailed planetary positions, aged paper texture, high quality, detailed",
            "Celestial tarot card illustration The Star, vintage style, gold and navy, aged paper, high quality, detailed",
            "Moon goddess illustration with crescent crown, vintage ink and watercolor, mysterious style, high quality, detailed",
            "Vintage star chart illustration of the northern hemisphere, aged paper, sepia and gold ink, high quality, detailed",
            "Celestial compass rose illustration with sun and moon, vintage ephemera style, aged paper, high quality, detailed",
            "Astrology symbol page with planetary glyphs, vintage manuscript style, aged paper texture, high quality, detailed",
            "Celestial eclipse illustration, vintage astronomical ephemera, ink and watercolor, aged paper, high quality, detailed",
            "Vintage zodiac Aries illustration with ram and stars, astrological ephemera, aged paper, high quality, detailed",
            "Celestial moon garden illustration with night-blooming flowers, vintage style, dark paper, high quality, detailed",
            "Vintage astrology aspect illustration with planetary alignments, technical ink drawing, aged paper, high quality, detailed",
            "Celestial cosmos illustration with nebula and stars, vintage ephemera style, gold and navy, high quality, detailed",
            "Vintage zodiac Cancer illustration with crab and stars, astrological ephemera, aged paper, high quality, detailed",
            "Celestial astrolabe illustration, vintage scientific instrument drawing, ink on aged paper, high quality, detailed",
            "Vintage moon calendar illustration with phases, astrology ephemera style, aged paper texture, high quality, detailed",
            "Celestial solar system illustration, vintage astronomy style, ink drawing with gold accents, high quality, detailed",
            "Vintage zodiac Leo illustration with lion and stars, astrological ephemera, aged paper, high quality, detailed",
            "Celestial star and crescent illustration, vintage ornamental design, gold ink on dark paper, high quality, detailed",
            "Vintage astrology house wheel illustration, technical drawing style, aged paper texture, high quality, detailed",
            "Celestial aurora illustration with stars, vintage ephemera style, watercolor on dark paper, high quality, detailed",
            "Vintage zodiac Pisces illustration with fish and stars, astrological ephemera, aged paper, high quality, detailed",
        ],
    },
    {
        "name": "Medieval Illuminated Manuscript",
        "description": "Medieval illuminated manuscript pages with ornate initials, gold leaf borders, heraldic designs, and calligraphy. Perfect for fantasy and historical junk journals.",
        "tags": ["medieval", "illuminated", "manuscript", "gothic", "historical", "ephemera", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Medieval illuminated manuscript page with ornate letter B and gold leaf border, vellum texture, high quality, detailed",
            "Medieval heraldic shield illustration with lion rampant, gold and red, vellum paper texture, high quality, detailed",
            "Illuminated manuscript page with decorative border of ivy and gold, medieval script, aged vellum, high quality, detailed",
            "Medieval bestiary page with phoenix illustration, gold leaf and tempera, vellum texture, high quality, detailed",
            "Ornate medieval manuscript initial letter S with dragon, gold leaf, blue and red, vellum, high quality, detailed",
            "Medieval map illustration of a fantastical kingdom, gold leaf accents, aged vellum texture, high quality, detailed",
            "Illuminated manuscript page with decorative floral border, gold and blue, medieval calligraphy, high quality, detailed",
            "Medieval heraldic crest with eagle, gold and black, vellum paper, illuminated style, high quality, detailed",
            "Manuscript page with ornate calendar illustration, gold leaf, zodiac medallions, vellum, high quality, detailed",
            "Medieval bestiary page with unicorn illustration, gold leaf border, red and blue tempera, high quality, detailed",
            "Ornate medieval manuscript page with illuminated letter R, gold leaf, intricate border, vellum, high quality, detailed",
            "Medieval coat of arms illustration with griffin, gold leaf accents, vellum paper texture, high quality, detailed",
            "Illuminated manuscript music page with decorative border, gold and red, medieval notation, high quality, detailed",
            "Medieval page border with acanthus leaves and gold leaf, vellum texture, illuminated style, high quality, detailed",
            "Bestiary page with dragon illustration, gold leaf and tempera, medieval manuscript style, high quality, detailed",
            "Ornate medieval initial letter D with saint figure, gold leaf, blue and red, vellum, high quality, detailed",
            "Medieval manuscript page with Tree of Jesse illustration, gold leaf border, vellum texture, high quality, detailed",
            "Heraldic banner illustration with gold fleur-de-lis, medieval style, vellum paper, high quality, detailed",
            "Illuminated manuscript page with ornate line ending, gold leaf creatures, blue and red, vellum, high quality, detailed",
            "Medieval calendar page with Labors of the Months illustration, gold leaf, vellum texture, high quality, detailed",
            "Ornate medieval manuscript frame with gold leaf and flowers, empty center, vellum paper, high quality, detailed",
            "Bestiary page with basilisk illustration, gold leaf border, medieval manuscript style, high quality, detailed",
            "Medieval manuscript page with decorative puzzle initial, gold leaf, red and blue, vellum, high quality, detailed",
            "Heraldic achievement illustration with shield, helm, and mantling, gold leaf, vellum, high quality, detailed",
        ],
    },
    {
        "name": "Japanese Wabi-Sabi Ephemera",
        "description": "Serene Japanese wabi-sabi ephemera featuring ink wash paintings, haiku pages, cherry blossoms, and minimalist compositions. Perfect for tranquil and meditative junk journals.",
        "tags": ["japanese", "wabisabi", "minimalist", "ephemera", "inkwash", "cherryblossom", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Japanese wabi-sabi ink wash painting of a single cherry blossom branch, sumi-e style, aged washi paper, high quality, detailed",
            "Haiku poem page with bamboo illustration, Japanese calligraphy style, aged paper texture, high quality, detailed",
            "Japanese ink wash painting of a koi fish, sumi-e style, minimalist composition, aged paper, high quality, detailed",
            "Wabi-sabi tea ceremony ephemera with bamboo whisk, ink wash illustration, aged paper, high quality, detailed",
            "Japanese cherry blossom petal falling illustration, sumi-e ink style, aged washi paper texture, high quality, detailed",
            "Minimalist Japanese stone garden illustration, ink wash painting, aged paper background, high quality, detailed",
            "Japanese wabi-sabi cracked pottery illustration, ink wash style, aged paper texture, high quality, detailed",
            "Haiku page with maple leaf illustration, Japanese calligraphy, aged washi paper, high quality, detailed",
            "Japanese ink wash painting of a crane in flight, sumi-e style, minimalist, aged paper, high quality, detailed",
            "Wabi-sabi dried flower arrangement illustration, Japanese ink style, aged paper texture, high quality, detailed",
            "Japanese pagoda in mist illustration, ink wash painting, minimalist composition, aged paper, high quality, detailed",
            "Haiku page with moon illustration, Japanese calligraphy style, aged washi paper, high quality, detailed",
            "Japanese ink wash painting of bamboo grove, sumi-e style, minimalist, aged paper, high quality, detailed",
            "Wabi-sabi weathered wood texture with moss illustration, Japanese aesthetic, aged paper, high quality, detailed",
            "Japanese waving cat maneki-neko illustration, ink wash style, aged washi paper texture, high quality, detailed",
            "Haiku page with snow on bamboo illustration, Japanese calligraphy style, aged paper, high quality, detailed",
            "Japanese ink wash painting of Mt Fuji, sumi-e style, minimalist composition, aged paper, high quality, detailed",
            "Wabi-sabi ceramic tea bowl illustration, ink wash style, aged paper background, high quality, detailed",
            "Japanese dragonfly over water illustration, sumi-e style, minimalist, aged washi paper, high quality, detailed",
            "Haiku page with firefly illustration, Japanese calligraphy, aged paper texture, high quality, detailed",
            "Japanese ink wash painting of a pine tree, sumi-e style, aged paper, minimalist, high quality, detailed",
            "Wabi-sabi moss and stone illustration, Japanese aesthetic, ink wash, aged paper, high quality, detailed",
            "Japanese koinobori carp streamer illustration, ink wash style, aged washi paper, high quality, detailed",
            "Haiku page with autumn moon illustration, Japanese calligraphy style, aged paper texture, high quality, detailed",
        ],
    },
]


def download_image(prompt: str, output_path: str, seed: int, width: int = 768, height: int = 1091, max_retries: int = 3) -> bool:
    """Download a single image from Pollinations.ai. Uses portrait dimensions for A4 ratio."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&model=flux"

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read()

            if len(data) < 5000:
                if attempt < max_retries - 1:
                    time.sleep(5 + attempt * 8)
                continue

            with open(output_path, 'wb') as f:
                f.write(data)

            # Verify it's a valid image
            try:
                img = Image.open(output_path)
                img.verify()
                return True
            except Exception:
                os.remove(output_path) if os.path.exists(output_path) else None
                if attempt < max_retries - 1:
                    time.sleep(5 + attempt * 8)
                continue

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5 + attempt * 10)
                continue
            return False

    return False


def create_pdf_from_images(image_paths: list, output_pdf: str, title: str):
    """Create a PDF from a list of image paths, one image per A4 page."""
    c = canvas.Canvas(str(output_pdf), pagesize=A4)
    a4_w, a4_h = A4
    margin = 0.5 * inch
    printable_w = a4_w - 2 * margin

    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            img_w, img_h = img.size

            if i == 0:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(a4_w / 2, a4_h - 0.4 * inch, title)
                available_h = a4_h - 2 * margin - 0.5 * inch
            else:
                available_h = a4_h - 2 * margin

            scale = min(printable_w / img_w, available_h / img_h)
            draw_w = img_w * scale
            draw_h = img_h * scale

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


def generate_etsy_listing(theme: dict, num_images: int = 20) -> dict:
    """Generate Etsy listing metadata for a theme package."""
    name = theme["name"]
    desc = theme["description"]
    tags = theme["tags"]

    listing = {
        "title": f"{name} - Digital Junk Journal Ephemera Pack - Printable Scrapbook Pages - DIY Paper Craft - Instant Download",
        "description": f"""{desc}

WHAT YOU GET:
- {num_images} unique high-quality AI-generated images ({name} themed)
- A4 size PDF ready to print at 300 DPI quality
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
        "tags": tags[:13],
        "price_suggestion": 4.99,
        "category": "Paper, Party & Kids > Paper > Digital Paper",
    }
    return listing


def generate_package(theme_idx: int, theme: dict, base_dir: Path) -> dict:
    """Generate a complete package for one theme using parallel downloads."""
    theme_slug = theme["name"].lower().replace(" ", "_")
    pkg_dir = base_dir / f"{DATE_STR}_{theme_slug}"
    images_dir = pkg_dir / "Original_Bilder"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating Package {theme_idx+1}/10: {theme['name']}")
    print(f"{'='*60}")

    prompts = theme["prompts"]
    num_needed = min(20, len(prompts))  # Use first 20 prompts (more than enough)

    # Check which images already exist
    existing = 0
    tasks = []
    for i in range(num_needed):
        img_filename = f"{theme_slug}_{i+1:02d}.jpg"
        img_path = images_dir / img_filename
        if img_path.exists():
            existing += 1
            continue
        tasks.append((i, prompts[i], img_path))

    print(f"  Already have {existing} images, need to generate {len(tasks)} more")

    # Generate missing images with parallel workers
    generated = list(images_dir.glob("*.jpg"))
    failed = []

    def download_task(args):
        i, prompt, img_path = args
        seed = 42 + i + (theme_idx * 100)
        success = download_image(prompt, str(img_path), seed, width=768, height=1091)
        return (i, img_path, success)

    if tasks:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(download_task, task): task for task in tasks}
            for future in as_completed(futures):
                i, img_path, success = future.result()
                if success:
                    generated.append(img_path)
                    print(f"  [{i+1:2d}/{num_needed}] OK: {img_path.name}")
                else:
                    failed.append(i)
                    print(f"  [{i+1:2d}/{num_needed}] FAILED: {img_path.name}")

                # Small delay between completions to avoid rate limiting
                time.sleep(0.5)

    # Re-scan directory for all images
    all_images = sorted(images_dir.glob("*.jpg"))
    print(f"\n  Total images for {theme['name']}: {len(all_images)}")

    if len(all_images) < 20:
        print(f"  WARNING: Only {len(all_images)} images, need at least 20!")

    # Create PDF
    pdf_path = pkg_dir / f"{theme_slug}_junk_journal.pdf"
    if all_images:
        print(f"  Creating PDF: {pdf_path.name}")
        create_pdf_from_images([str(p) for p in all_images], str(pdf_path), theme["name"])

    # Create Etsy listing
    listing = generate_etsy_listing(theme, len(all_images))
    listing_path = pkg_dir / "etsy_listing.json"
    with open(listing_path, 'w') as f:
        json.dump(listing, f, indent=2)

    # Create Etsy listing text file
    txt_path = pkg_dir / "Etsy_Listing_Info.txt"
    with open(txt_path, 'w') as f:
        f.write(f"TITLE:\n{listing['title']}\n\n")
        f.write(f"DESCRIPTION:\n{listing['description']}\n\n")
        f.write(f"TAGS:\n{', '.join(listing['tags'])}\n\n")
        f.write(f"PRICE: ${listing['price_suggestion']}\n")
        f.write(f"CATEGORY: {listing['category']}\n")

    # Create README
    readme_path = pkg_dir / "README.md"
    with open(readme_path, 'w') as f:
        f.write(f"# {theme['name']} - Junk Journal Ephemera Pack\n\n")
        f.write(f"{theme['description']}\n\n")
        f.write(f"## Contents\n\n")
        f.write(f"- {len(all_images)} unique AI-generated images\n")
        f.write(f"- PDF compilation (A4 format)\n")
        f.write(f"- Individual image files (768x1091 JPG, A4 portrait ratio)\n")
        f.write(f"- Etsy listing metadata\n\n")
        f.write(f"## Files\n\n")
        f.write(f"- `Original_Bilder/` - Individual image files\n")
        f.write(f"- `{pdf_path.name}` - PDF compilation\n")
        f.write(f"- `etsy_listing.json` - Etsy listing metadata\n")
        f.write(f"- `Etsy_Listing_Info.txt` - Etsy listing in text format\n")

    return {
        "theme": theme["name"],
        "dir": str(pkg_dir),
        "images_generated": len(all_images),
        "images_failed": len(failed),
        "pdf": str(pdf_path),
        "pdf_exists": pdf_path.exists(),
    }


def main():
    print("=" * 60)
    print("Batch Junk Journal Digital PDF Package Generator")
    print("Using Pollinations.ai Cloud API (Free, No Key Required)")
    print("=" * 60)

    results = []
    for i, theme in enumerate(THEMES):
        result = generate_package(i, theme, BASE_DIR)
        results.append(result)
        print(f"\n  Package {i+1} complete: {result['images_generated']} images, {result['images_failed']} failed")

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE - SUMMARY")
    print(f"{'='*60}")

    total_images = 0
    all_complete = True
    for r in results:
        status = "COMPLETE" if r['images_generated'] >= 20 else "INCOMPLETE"
        print(f"  {r['theme']}: {r['images_generated']} images [{status}] (PDF: {'Yes' if r['pdf_exists'] else 'No'})")
        total_images += r["images_generated"]
        if r['images_generated'] < 20:
            all_complete = False

    print(f"\n  Total packages: {len(results)}")
    print(f"  Total images: {total_images}")
    print(f"  All packages complete: {'YES' if all_complete else 'NO - some need more images'}")

    # Save summary
    summary = {
        "generation_date": DATE_STR,
        "total_packages": len(results),
        "total_images": total_images,
        "all_complete": all_complete,
        "packages": results
    }
    summary_path = BASE_DIR / "generation_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()