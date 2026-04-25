#!/usr/bin/env python3
"""
Junk Journal Image Generator using FAL.ai (cloud compute)
Generates high-quality A4-proportioned images for 10 themed packages.
Each package gets 20 images minimum.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import date
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).parent
DATE_STR = str(date.today())

# ---------------------------------------------------------------------------
# Theme definitions — 10 themes, each with 20+ prompts
# Optimized prompts for FAL.ai FLUX model with junk journal aesthetic
# Adding quality boosters for best results
# ---------------------------------------------------------------------------

QUALITY_SUFFIX = ", high quality, detailed, professional, isolated on white parchment background, junk journal ephemera style, print-ready"

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
            "Steampunk apothecary bottle with brass gears and copper fittings, detailed technical illustration, aged paper background",
            "Victorian medicine label with ornate border, apothecary script, sepia tones, vintage pharmaceutical ephemera",
            "Steampunk mechanical heart illustration with visible gears and copper pipes, ink and watercolor on aged paper",
            "Antique alchemy laboratory equipment, distillation apparatus, detailed ink drawing, Renaissance style",
            "Victorian apothecary jar with dried herbs and brass label, ornate illustration, warm brown tones",
            "Steampunk clockwork mechanism exploded diagram, detailed technical drawing, brass and copper tones on parchment",
            "Antique pharmaceutical advertisement with ornate Victorian typography, apothecary bottles, vintage ephemera style",
            "Victorian surgical instrument illustration, detailed pen and ink drawing, sepia tones on aged paper",
            "Steampunk chemistry set with bubbling beakers and copper tubing, detailed illustration, warm amber tones",
            "Antique apothecary shop interior with wooden shelves and glass bottles, vintage illustration style",
            "Victorian patent drawing for a mechanical medical device, detailed ink lines, aged blueprint paper",
            "Steampunk eye mechanical iris illustration, brass and copper details, detailed technical drawing on parchment",
            "Antique herbal remedy label with botanical illustration and gothic script, vintage ephemera, aged paper",
            "Steampunk compass and astrolabe illustration, brass mechanical details, vintage cartographic style",
            "Victorian apothecary trade card with ornate border and medicine bottles, colorful chromolithograph style",
            "Steampunk anatomical illustration with mechanical augmentations, detailed ink drawing, aged vellum background",
            "Antique prescription form with calligraphy, Victorian pharmacy ephemera, sepia ink on aged paper",
            "Steampunk tea blending chart with brass mechanical tea infuser, detailed illustration, warm tones",
            "Victorian microscope illustration with brass and glass details, scientific ephemera style, aged paper",
            "Steampunk pocket watch mechanism with medical symbols, detailed technical drawing, copper tones on parchment",
            "Antique vial label with poison warning and skull, Victorian apothecary ephemera, aged paper",
            "Steampunk furnace and boiler for alchemical processes, detailed pen and ink, warm copper and brass tones",
            "Victorian mortar and pestle with dried herbs illustration, botanical-apothecary ephemera, aged paper",
            "Steampunk prosthetic limb patent drawing, detailed mechanical illustration, aged blueprint paper",
        ],
    },
    {
        "name": "Alice in Wonderland Grunge",
        "slug": "alice_in_wonderland_grunge",
        "description": "Whimsical yet grungy Alice in Wonderland-themed ephemera featuring distorted tea party illustrations, mad hatter graphics, playing card motifs, and surreal Victorian fantasy elements.",
        "tags": ["aliceinwonderland", "grunge", "vintage", "fantasy", "teaparty", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Alice in Wonderland tea party illustration, grunge style, distorted perspective, vintage ink and watercolor on stained paper",
            "Mad Hatter top hat with price tag illustration, Victorian grunge aesthetic, ink sketch on aged paper",
            "Playing card soldiers marching, Alice in Wonderland style, grungy ink illustration, sepia and red tones",
            "White rabbit pocket watch illustration, distorted time, grunge Victorian style, aged paper texture",
            "Cheshire cat smile floating in ornate tree, vintage ink illustration style, sepia and purple tones on stained paper",
            "Alice falling down the rabbit hole illustration, vintage grunge style, mixed media on aged paper",
            "Queen of Hearts playing card design, ornate border, grunge vintage style, red and gold on aged paper",
            "Drink Me bottle with ornate label illustration, Alice in Wonderland ephemera, ink and watercolor on parchment",
            "Caterpillar on mushroom smoking hookah, vintage illustration style, grunge aesthetic, sepia and green tones",
            "Flamingo croquet mallet illustration, whimsical Victorian style, ink drawing on aged paper",
            "Mad Tea Party table setting with mismatched china, vintage grunge illustration, sepia ink on stained paper",
            "Alice size change scene with miniature and giant elements, Victorian illustration, grunge style on aged paper",
            "Jabberwocky illustration, dark fantasy ink drawing, Victorian grunge style on yellowed paper",
            "Looking glass reflection scene, vintage illustration, mirror frame border, grunge ink on aged paper",
            "Tweedledee and Tweedledum illustration, Victorian ink drawing, grunge style on stained paper",
            "Alice's key and tiny door illustration, ornate Victorian style, ink and watercolor on aged parchment",
            "March Hare pocket watch illustration, steampunk-Victorian grunge, sepia tones on aged paper",
            "Garden of live flowers illustration, Alice in Wonderland style, vintage ink on aged paper with stains",
            "Caucus race illustration with dodo bird, vintage Victorian style, grunge ink drawing on yellowed paper",
            "Mock Turtle illustration with soup recipe, Victorian grunge ephemera, ink and watercolor on stained paper",
            "Red Rose garden card soldiers painting roses, Alice in Wonderland, vintage illustration style",
            "Eat Me cake with ornate Victorian label, Alice in Wonderland ephemera, sepia and gold on aged paper",
            "Wonderland map illustration, vintage cartographic style, grunge ink drawing on aged parchment",
            "Griffin and Mock Turtle dance illustration, Victorian ink style, grunge aesthetic on stained paper",
        ],
    },
    {
        "name": "Art Nouveau Flower Fairies",
        "slug": "art_nouveau_flower_fairies",
        "description": "Enchanting Art Nouveau-style flower fairy illustrations with flowing organic lines, delicate color palettes, and whimsical nature spirits for magical junk journal pages.",
        "tags": ["artnouveau", "flowerfairies", "vintage", "ephemera", "whimsical", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Art Nouveau flower fairy perched on a lily pad, flowing organic lines, delicate watercolor on cream paper, Mucha-inspired style",
            "Art Nouveau decorative panel with rose fairy and flowing vines, ornate border, pastel watercolors on aged paper",
            "Flower fairy of the morning glory, Art Nouveau illustration style, delicate ink lines and soft watercolor on parchment",
            "Art Nouveau fairy queen with flower crown and gossamer wings, flowing hair and robes, watercolor on cream paper",
            "Cherry blossom fairy dancing in spring breeze, Art Nouveau style, pink and green watercolors on aged paper",
            "Art Nouveau decorative alphabet letter F with flower fairy, ornate organic border, gold and pastel on parchment",
            "Violet fairy sitting on a leaf, Art Nouveau illustration, purple and green watercolors, sepia ink lines on cream paper",
            "Art Nouveau flower fairy border design with morning glory and fairy silhouettes, decorative ephemera on aged paper",
            "Sunflower fairy with golden wings and flowing dress, Art Nouveau style, warm amber and green watercolors on parchment",
            "Art Nouveau decorative panel with poppy fairy, flowing organic forms, red and green watercolor on aged paper",
            "Iris fairy in flowing Art Nouveau gown with purple wings, ornate illustration on cream paper, gold accents",
            "Art Nouveau flower fairy calling card, ornate border with daisies and fairy, pastel watercolors on aged paper",
            "Lavender fairy with purple wings resting on flower stem, Art Nouveau illustration, soft purple tones on parchment",
            "Art Nouveau decorative page border with fairies and climbing roses, flowing organic lines on aged paper",
            "Bluebell fairy floating above a woodland stream, Art Nouveau style, blue and green watercolors on cream paper",
            "Art Nouveau fairy invitation card with ornate floral border and fairy illustration, gold and pastel on parchment",
            "Rose fairy with flowing Art Nouveau hair and petal dress, romantic illustration, pink watercolors on aged paper",
            "Art Nouveau decorative panel with fern fairy, flowing organic lines, green and brown watercolors on cream paper",
            "Daffodil fairy with golden wings and spring bouquet, Art Nouveau style, yellow and green on aged paper",
            "Art Nouveau flower fairy postcard design, ornate border with fairies and wildflowers, pastel watercolors on parchment",
            "Buttercup fairy dancing in a meadow, Art Nouveau illustration, yellow and green watercolors on cream paper",
            "Art Nouveau decorative header with orchid fairy, flowing organic forms, purple and gold on aged paper",
            "Peony fairy with elaborate flower petal gown, Art Nouveau style, pink and green watercolors on parchment",
            "Art Nouveau fairy page ornament with interweaving flowers and fairy silhouettes, decorative ephemera on cream paper",
        ],
    },
    {
        "name": "Vintage Travel Memorabilia",
        "slug": "vintage_travel_memorabilia",
        "description": "Nostalgic vintage travel ephemera featuring antique maps, luggage labels, passport stamps, postcards, and golden-age travel posters for adventurous junk journal pages.",
        "tags": ["vintage", "travel", "ephemera", "map", "postcard", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Vintage travel luggage label for Paris, Art Deco style illustration, warm sepia and blue tones on aged paper",
            "Antique world map detail showing old trade routes, vintage cartographic style, sepia ink on aged parchment",
            "Vintage ocean liner postcard, 1930s travel poster style, bold colors on aged paper with stamps",
            "Old passport stamp collage illustration, vintage travel ephemera, red and blue ink on yellowed paper",
            "Victorian train ticket illustration with ornate border, sepia tones, travel ephemera on aged paper",
            "Vintage travel journal page with handwritten notes and sketches, sepia ink on cream paper with coffee stains",
            "Antique compass rose illustration, vintage nautical style, detailed ink drawing on aged parchment",
            "Vintage airline poster for a 1950s destination, retro illustration style, bold colors on aged paper",
            "Old steam locomotive travel illustration, Victorian era, detailed ink drawing with sepia wash on aged paper",
            "Vintage luggage trunk with travel stickers illustration, sepia and pastel tones, ephemera on cream paper",
            "Antique postcard from Rome with architectural illustration, vintage travel style, warm tones on aged paper",
            "Vintage travel stamp collection page, various destinations, colorful ink on yellowed paper",
            "Old map of Mediterranean ports, vintage cartographic style, sepia and blue tones on aged parchment",
            "Vintage cruise ship brochure illustration, 1930s Art Deco style, bold colors on cream paper",
            "Antique travel receipt from a grand hotel, Victorian ephemera, sepia ink on aged paper",
            "Vintage hot air balloon travel poster illustration, 19th century style, colorful on aged paper",
            "Old travel diary page with pressed flower and sketch, vintage ephemera, sepia tones on cream paper",
            "Vintage train station platform illustration, Victorian era, ink drawing with sepia wash on aged paper",
            "Antique shipping manifest page, vintage travel ephemera, detailed ink on yellowed paper",
            "Vintage travel advertisement for Orient Express, Art Deco style, gold and sepia on aged paper",
            "Old suitcase with passport and tickets illustration, vintage travel ephemera, sepia tones on cream paper",
            "Vintage lighthouse postcard illustration, nautical travel ephemera, blue and sepia on aged paper",
            "Antique globe illustration with travel routes, vintage cartographic style, sepia ink on parchment",
            "Vintage travel sticker page with various destination labels, colorful ephemera on aged paper",
        ],
    },
    {
        "name": "Rustic Cottage Garden",
        "slug": "rustic_cottage_garden",
        "description": "Charming rustic cottage garden ephemera featuring country flowers, garden tools, herb illustrations, and cozy countryside watercolors for warm, inviting junk journal pages.",
        "tags": ["rustic", "cottage", "garden", "vintage", "flowers", "herbs", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Rustic cottage garden with climbing roses on a stone wall, watercolor illustration, warm tones on aged paper",
            "Vintage garden tool illustration with trowel and watering can, rustic style, ink and watercolor on cream paper",
            "Cottage herb garden illustration with lavender and rosemary, vintage botanical style, watercolor on aged paper",
            "Rustic wooden gate with climbing clematis, country garden watercolor, warm tones on parchment",
            "Vintage seed packet illustration for cottage garden flowers, rustic ephemera style, aged paper",
            "Charming cottage garden path with cobblestones and flowers, watercolor illustration on cream paper",
            "Antique botanical illustration of garden peas and beans, rustic style, ink and watercolor on aged paper",
            "Rustic garden journal page with pressed flowers and notes, vintage ephemera, sepia tones on cream paper",
            "Country cottage window box with geraniums, watercolor illustration, warm colors on aged paper",
            "Vintage garden plan illustration with layout sketches, rustic ephemera style, sepia ink on paper",
            "Rustic watering can with wildflowers spilling out, watercolor illustration, warm tones on parchment",
            "Cottage garden birdhouse with morning glories, vintage watercolor, soft colors on aged paper",
            "Antique plant label stakes illustration, rustic garden ephemera, sepia ink on cream paper",
            "Rustic garden bench surrounded by foxgloves, watercolor illustration, warm tones on aged paper",
            "Vintage harvest basket with garden vegetables, rustic watercolor, warm autumn tones on parchment",
            "Cottage garden border with hollyhocks and delphiniums, watercolor illustration on cream paper",
            "Rustic potting shed interior with garden tools, vintage illustration, warm sepia tones on aged paper",
            "Vintage garden catalog page with sunflower varieties, rustic ephemera, ink and watercolor on aged paper",
            "Country garden with lavender hedge and stone path, watercolor illustration, warm tones on parchment",
            "Rustic garden wreath with dried flowers, vintage ephemera illustration, warm colors on cream paper",
            "Vintage recipe card for lavender lemonade with garden illustration, rustic style, aged paper",
            "Cottage garden beehive with wildflowers, watercolor illustration, warm golden tones on parchment",
            "Antique garden rake and gloves illustration, rustic ephemera, sepia and warm tones on aged paper",
            "Rustic garden bouquet wrapped in twine, vintage watercolor illustration, warm colors on cream paper",
        ],
    },
    {
        "name": "Celestial Astrology Journal",
        "slug": "celestial_astrology_journal",
        "description": "Mystical celestial and astrology ephemera featuring zodiac illustrations, star charts, moon phases, and cosmic decorative elements for enchanting junk journal pages.",
        "tags": ["celestial", "astrology", "zodiac", "vintage", "mystical", "stars", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Celestial star chart illustration with zodiac constellations, vintage astronomical style, gold and navy on aged paper",
            "Vintage moon phases illustration, detailed astronomical drawing, gold and silver on dark navy paper",
            "Art Nouveau zodiac wheel with ornate border, celestial illustration, gold and pastel on aged parchment",
            "Antique astrology birth chart illustration, vintage esoteric style, gold ink on cream paper",
            "Celestial sun and moon illustration with ornate rays, vintage style, gold and blue on aged paper",
            "Vintage constellation map of the northern hemisphere, astronomical ephemera, sepia and gold on parchment",
            "Zodiac sign Leo illustration, Art Nouveau celestial style, gold and warm tones on aged paper",
            "Antique planetary orbit diagram, vintage astronomical ephemera, sepia ink on cream paper",
            "Celestial goddess illustration surrounded by stars, vintage mythology style, gold and blue on aged paper",
            "Vintage tarot card The Star illustration, celestial style, gold and navy on aged parchment",
            "Antique armillary sphere illustration, astronomical instrument drawing, sepia ink on aged paper",
            "Celestial border design with stars and crescent moons, vintage ephemera, gold on cream paper",
            "Vintage astronomy textbook page with solar system diagram, celestial ephemera, sepia tones on aged paper",
            "Zodiac sign Aquarius illustration with water bearer, Art Nouveau celestial style, blue and gold on parchment",
            "Antique celestial globe illustration, vintage cartographic style, gold and navy on aged paper",
            "Celestial moon goddess illustration with star crown, vintage mythology style, silver and gold on cream paper",
            "Vintage observatory instrument illustration, astronomical ephemera, sepia ink on aged paper",
            "Zodiac sign Scorpio illustration with scorpion, Art Nouveau celestial style, gold and deep red on aged parchment",
            "Antique astrolabe illustration, vintage scientific drawing, sepia and gold on cream paper",
            "Celestial sun face illustration with ornate rays, vintage style, gold and warm tones on aged paper",
            "Vintage star atlas page showing major constellations, astronomical ephemera, gold and navy on parchment",
            "Zodiac sign Pisces illustration with flowing fish, Art Nouveau celestial style, blue and gold on aged paper",
            "Antique celestial navigation chart with compass rose, vintage ephemera, sepia and gold on aged paper",
            "Celestial decorative frame with stars, moons, and sun faces, vintage ornamental style, gold on cream paper",
        ],
    },
    {
        "name": "Medieval Illuminated Manuscript",
        "slug": "medieval_illuminated_manuscript",
        "description": "Ornate medieval illuminated manuscript pages featuring gilded borders, Celtic knotwork, heraldic designs, and sacred illustrations for richly detailed junk journal pages.",
        "tags": ["medieval", "illuminated", "manuscript", "gilded", "celtic", "heraldic", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Medieval illuminated manuscript page with ornate gold border, Celtic knotwork, detailed gilded illustration on aged parchment",
            "Illuminated letter B with intertwined dragons, medieval manuscript style, gold leaf and vibrant pigments on vellum",
            "Medieval Book of Hours page with calendar illustration, illuminated border, gold and ultramarine on aged parchment",
            "Celtic knotwork border design with interlocking patterns, medieval manuscript style, gold on aged vellum",
            "Illuminated letter S with medieval floral spirals, gold leaf and red pigments on aged parchment",
            "Medieval heraldic shield with lion rampant, illuminated manuscript style, gold and red on vellum",
            "Bestiary page with phoenix illustration, medieval manuscript style, gold leaf and vibrant colors on aged parchment",
            "Illuminated manuscript page with Virgin and Child miniature, ornate gold border on aged vellum",
            "Medieval decorative page divider with acanthus leaves, illuminated style, gold on aged parchment",
            "Illuminated letter K with peacock, medieval manuscript style, gold leaf and blue pigments on vellum",
            "Medieval calendar page showing Labors of the Month, illuminated manuscript, gold and rich colors on aged parchment",
            "Gothic initial letter R with vine border, medieval manuscript style, gold and green on vellum",
            "Medieval map of Jerusalem illustration, illuminated manuscript style, gold leaf on aged parchment",
            "Illuminated manuscript page with Saint and halo, ornate gold border, red and blue on aged vellum",
            "Medieval decorative marginalia with grotesques and vines, illuminated style, gold and colors on aged parchment",
            "Illuminated letter M with medieval castle, gold leaf and stone colors on vellum",
            "Medieval psalter page with musical notation, illuminated initials, gold and blue on aged parchment",
            "Heraldic crest with griffin and fleur-de-lis, medieval manuscript style, gold and red on vellum",
            "Illuminated manuscript page with Tree of Jesse, ornate gold border, vibrant pigments on aged parchment",
            "Medieval zodiac page with Cancer illustration, illuminated style, gold and blue on vellum",
            "Illuminated letter H with historiated scene, medieval manuscript style, gold leaf on aged parchment",
            "Medieval carpet page design with intricate patterns, illuminated manuscript style, gold and vibrant colors on vellum",
            "Illuminated manuscript page with angel musicians, ornate gold border, rich pigments on aged parchment",
            "Medieval bestiary page with unicorn illustration, gold leaf and pastel on vellum",
        ],
    },
    {
        "name": "Japanese Wabi-Sabi Ephemera",
        "slug": "japanese_wabi-sabi_ephemera",
        "description": "Serene Japanese wabi-sabi ephemera featuring ink wash paintings, minimalist botanical sketches, haiku calligraphy, and imperfect beauty elements for meditative junk journal pages.",
        "tags": ["japanese", "wabisabi", "minimalist", "inkwash", "calligraphy", "ephemera", "junkjournal", "scrapbook", "digitalpaper", "printable"],
        "prompts": [
            "Japanese wabi-sabi ink wash painting of a single cherry blossom branch, minimalist sumi-e style on aged washi paper",
            "Vintage Japanese haiku calligraphy on aged paper, brush ink characters with simple bamboo illustration, wabi-sabi aesthetic",
            "Wabi-sabi kintsugi repaired bowl illustration, Japanese ink drawing with gold repair lines, aged paper texture",
            "Japanese minimalist ink wash of bamboo grove in rain, sumi-e style on textured washi paper",
            "Vintage Japanese tea ceremony ephemera with chawan illustration, wabi-sabi aesthetic, sepia ink on aged paper",
            "Wabi-sabi dried leaf and moss arrangement, Japanese nature sketch style, muted ink on cream paper",
            "Japanese ink wash painting of a single koi fish, minimalist sumi-e style on aged washi paper",
            "Vintage Japanese postcard with Mount Fuji ink illustration, faded sepia tones on aged paper",
            "Wabi-sabi weathered stone in moss garden, Japanese ink sketch style, muted tones on textured paper",
            "Japanese brush calligraphy of the character for peace, with simple pine branch, wabi-sabi style on aged paper",
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

# A4 dimensions at 300 DPI
A4_WIDTH = 2480
A4_HEIGHT = 3508

def create_pdf_from_images(theme_name, image_paths, output_dir):
    """Create a PDF from a list of image paths, each page A4."""
    pdf_path = output_dir / f"{theme_name.replace(' ', '_')}_Product.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    
    for img_path in image_paths:
        # Each image fills the full A4 page
        c.drawImage(str(img_path), 0, 0, width=A4[0], height=A4[1])
        c.showPage()
    
    c.save()
    return pdf_path


def generate_etsy_listing(theme):
    """Generate SEO-optimized Etsy listing info."""
    name = theme["name"]
    slug = theme["slug"]
    desc = theme["description"]
    tags = theme["tags"][:13]  # Etsy allows max 13 tags
    
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
        "title": title[:140],  # Etsy title max 140 chars
        "description": description,
        "tags": tags
    }


def resize_to_a4(img_path, output_path):
    """Resize image to A4 at 300 DPI (2480 x 3508), preserving aspect ratio with padding."""
    img = Image.open(img_path)
    
    # Create A4 canvas (white background)
    canvas_img = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 250, 240))
    
    # Calculate scaling to fit within A4 while maintaining aspect ratio
    img_ratio = img.width / img.height
    a4_ratio = A4_WIDTH / A4_HEIGHT
    
    if img_ratio > a4_ratio:
        # Image is wider relative to A4 - fit to width
        new_width = A4_WIDTH
        new_height = int(A4_WIDTH / img_ratio)
    else:
        # Image is taller relative to A4 - fit to height
        new_height = A4_HEIGHT
        new_width = int(A4_HEIGHT * img_ratio)
    
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Center on canvas
    x_offset = (A4_WIDTH - new_width) // 2
    y_offset = (A4_HEIGHT - new_height) // 2
    canvas_img.paste(img_resized, (x_offset, y_offset))
    
    # Save with high quality
    canvas_img.save(str(output_path), 'JPEG', quality=95, dpi=(300, 300))
    return output_path


if __name__ == "__main__":
    print(f"Configured {len(THEMES)} themes")
    for t in THEMES:
        print(f"  {t['name']}: {len(t['prompts'])} prompts")
    print(f"\nA4 target: {A4_WIDTH}x{A4_HEIGHT} @ 300 DPI")