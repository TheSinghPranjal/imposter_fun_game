#!/usr/bin/env python3
"""Generates placeholder art in assets/images and docs/assets/manifest.json.

Run from the project root: python3 tool/generate_assets.py
Requires Pillow. Assets marked "final" in the manifest are never overwritten.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'docs/assets/manifest.json')
IMG = 'assets/images'

DEEP, INDIGO, NAVY = '#2B1452', '#3D1F7A', '#0F0A1F'
VIOLET, BLUE, YELLOW, CORAL = '#7C4DFF', '#4FC3F7', '#FFD54F', '#FF6B8A'
OFFWHITE, CARD, CIVILIAN, IMPOSTER = '#F7F4FF', '#1C1333', '#5C6BC0', '#E53935'
WOOD, WOOD_DARK, CREAM = '#A9713E', '#6E4321', '#FFF1D6'
BEAR, BEAR_DARK = '#9C6B45', '#6B4429'


def font(size, weight='Black'):
    return ImageFont.truetype(os.path.join(ROOT, f'assets/fonts/Nunito/Nunito-{weight}.ttf'), size)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h, top, bottom):
    a, b = rgb(top), rgb(bottom)
    col = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col.putpixel((0, y), tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return col.resize((w, h)).convert('RGBA')


def glow(img, shape_fn, blur):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shape_fn(ImageDraw.Draw(layer))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def dashed_rect(d, box, color, width=6, dash=34, gap=22):
    x0, y0, x1, y1 = box
    for a, b, horizontal, fixed in ((x0, x1, True, y0), (x0, x1, True, y1), (y0, y1, False, x0), (y0, y1, False, x1)):
        p = a
        while p < b:
            q = min(p + dash, b)
            d.line([(p, fixed), (q, fixed)] if horizontal else [(fixed, p), (fixed, q)], fill=color, width=width)
            p = q + gap


def bear(d, cx, cy, r, body=BEAR, sleepy=True):
    """A simple round bear head."""
    ow = max(4, int(r * .07))
    out = NAVY
    for sx in (-1, 1):
        ex, ey, er = cx + sx * r * .72, cy - r * .72, r * .36
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=body, outline=out, width=ow)
        d.ellipse([ex - er * .5, ey - er * .5, ex + er * .5, ey + er * .5], fill=CREAM)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body, outline=out, width=ow)
    d.ellipse([cx - r * .48, cy + r * .02, cx + r * .48, cy + r * .72], fill=CREAM)
    d.ellipse([cx - r * .17, cy + r * .1, cx + r * .17, cy + r * .32], fill=out)
    for sx in (-1, 1):
        ex, ey = cx + sx * r * .42, cy - r * .2
        if sleepy:
            d.arc([ex - r * .17, ey - r * .12, ex + r * .17, ey + r * .17], 200, 340, fill=out, width=ow)
        else:
            d.ellipse([ex - r * .1, ey - r * .1, ex + r * .1, ey + r * .1], fill=out)
    d.arc([cx - r * .22, cy + r * .24, cx + r * .22, cy + r * .58], 25, 155, fill=out, width=ow)


def bear_body(d, cx, top, r, h, color=BEAR):
    d.rounded_rectangle([cx - r, top, cx + r, top + h], radius=int(r * .8), fill=color, outline=NAVY, width=max(4, int(r * .07)))


def stars(d, w, h, n, seed, y_max=1.0):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.randint(0, w), rnd.randint(0, int(h * y_max)), rnd.randint(2, 7)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice([OFFWHITE, YELLOW, BLUE]))


def tag(img, name, center_y=130):
    """Writes the asset name on a chip near the top edge."""
    d = ImageDraw.Draw(img)
    f = font(38)
    label = f'PLACEHOLDER  {name}'
    w = d.textlength(label, font=f)
    W = img.width
    d.rounded_rectangle([(W - w) / 2 - 28, center_y - 38, (W + w) / 2 + 28, center_y + 38], radius=30, fill=NAVY, outline=YELLOW, width=4)
    d.text((W / 2, center_y), label, font=f, fill=YELLOW, anchor='mm')


def safe(img, areas):
    d = ImageDraw.Draw(img)
    f = font(32, 'Bold')
    W, H = img.size
    for x, y, w, h in areas:
        box = (x * W, y * H, (x + w) * W, (y + h) * H)
        dashed_rect(d, box, YELLOW)
        d.text((box[0] + 22, box[1] + 18), 'UI SAFE AREA', font=f, fill=YELLOW)


def small_tag(img, name, xy=None, size=None):
    d = ImageDraw.Draw(img)
    size = size or max(9, img.width // 34)
    f = font(size, 'Bold')
    xy = xy or (img.width / 2, img.height - size * 1.2)
    d.text(xy, name, font=f, fill=OFFWHITE, anchor='mm', stroke_width=max(1, size // 8), stroke_fill=NAVY)


# ------------------------------------------------------------ backgrounds
W, H = 1080, 2340


def bg_home(areas):
    img = gradient(W, H, NAVY, INDIGO)
    d = ImageDraw.Draw(img)
    stars(d, W, H, 90, 1, .55)
    glow(img, lambda g: g.ellipse([140, 240, 940, 1040], fill=rgb(VIOLET) + (120,)), 90)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([130, 240, 950, 590], radius=40, fill=WOOD, outline=NAVY, width=12)
    d.text((540, 360), 'FIND THE', font=font(100), fill=CREAM, anchor='mm')
    d.text((540, 480), 'IMPOSTER', font=font(120), fill=YELLOW, anchor='mm')
    for cx, cy, r in ((280, 930, 150), (800, 930, 150), (540, 840, 190)):
        bear_body(d, cx, cy + r * .6, r * 1.05, 520)
        bear(d, cx, cy, r, sleepy=cx != 800)
    d.rectangle([0, 1320, W, H], fill=DEEP)
    return img


def bg_players(areas):
    img = gradient(W, H, DEEP, INDIGO)
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    for i in range(10):
        x = i * 120
        d.polygon([(x, 60), (x + 110, 60), (x + 55, 190)], fill=rnd.choice([CORAL, YELLOW, BLUE, VIOLET]), outline=NAVY)
    for cx in (-20, W + 20):
        glow(img, lambda g, c=cx: g.ellipse([c - 260, 1000, c + 260, 1520], fill=rgb(YELLOW) + (120,)), 80)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 2120, W, H], fill=WOOD_DARK)
    return img


def bg_pass(areas):
    img = gradient(W, H, NAVY, DEEP)
    glow(img, lambda g: g.polygon([(460, 0), (620, 0), (1010, 1500), (70, 1500)], fill=rgb(YELLOW) + (95,)), 40)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([430, 2000, 650, 2290], radius=30, fill=CARD, outline=OFFWHITE, width=8)
    for x0, x1 in ((-60, 430), (650, 1140)):
        d.rounded_rectangle([x0, 2060, x1, 2240], radius=85, fill=BEAR, outline=NAVY, width=10)
    return img


def bg_turn(areas):
    img = gradient(W, H, NAVY, INDIGO)
    glow(img, lambda g: g.ellipse([130, 300, 950, 1900], fill=rgb(YELLOW) + (90,)), 90)
    d = ImageDraw.Draw(img)
    for x0, s in ((0, 1), (W, -1)):
        for i in range(4):
            a = x0 + s * i * 42
            d.rectangle([min(a, a + s * 42), 0, max(a, a + s * 42), H], fill=CORAL if i % 2 else IMPOSTER)
    d.rectangle([0, 0, W, 76], fill=IMPOSTER)
    d.rectangle([0, 2200, W, H], fill=WOOD_DARK)
    return img


def bg_ready(areas):
    img = gradient(W, H, INDIGO, VIOLET)
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(190):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        if .12 * W < x < .88 * W and .25 * H < y < .75 * H:
            continue
        s = rnd.randint(14, 34)
        d.rounded_rectangle([x, y, x + s, y + s * 2], radius=5, fill=rnd.choice([CORAL, YELLOW, BLUE, OFFWHITE]))
    return img


def bg_round(areas):
    img = gradient(W, H, NAVY, DEEP)
    d = ImageDraw.Draw(img)
    stars(d, W, H, 40, 6, .3)
    glow(img, lambda g: g.ellipse([120, 860, 960, 1620], fill=rgb(YELLOW) + (110,)), 80)
    d = ImageDraw.Draw(img)
    for cx, r in ((230, 120), (540, 135), (850, 120)):
        bear_body(d, cx, 1210, r * 1.1, 240)
        bear(d, cx, 1130, r)
    d.ellipse([70, 1360, W - 70, 1600], fill=WOOD, outline=NAVY, width=12)
    d.rectangle([0, 1590, W, H], fill=DEEP)
    return img


# ------------------------------------------------------------ transparent art
def mascot_settings():
    img = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bear_body(d, 300, 330, 165, 240)
    bear(d, 300, 240, 165)
    cx, cy = 480, 430
    for i in range(8):
        a = i / 8 * math.tau
        x, y = cx + 76 * math.cos(a), cy + 76 * math.sin(a)
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=BLUE, outline=NAVY, width=5)
    d.ellipse([cx - 72, cy - 72, cx + 72, cy + 72], fill=BLUE, outline=NAVY, width=7)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=NAVY)
    small_tag(img, 'settings_bear', (250, 560), 30)
    return img


def mascot_imposter():
    img = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([130, 320, 470, 590], radius=70, fill=CARD, outline=NAVY, width=8)
    d.polygon([(300, 330), (205, 330), (300, 520)], fill=INDIGO, outline=NAVY)
    d.polygon([(300, 330), (395, 330), (300, 520)], fill=INDIGO, outline=NAVY)
    bear(d, 300, 240, 160, sleepy=False)
    d.rounded_rectangle([90, 120, 510, 160], radius=18, fill=IMPOSTER, outline=NAVY, width=7)
    d.rounded_rectangle([170, 30, 430, 135], radius=30, fill=IMPOSTER, outline=NAVY, width=7)
    small_tag(img, 'imposter_bear', (300, 560), 30)
    return img


def wood_sign(scale):
    w, h = 360 * scale, 120 * scale
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3 * scale, 3 * scale, w - 3 * scale, h - 3 * scale], radius=20 * scale, fill=WOOD, outline=NAVY, width=4 * scale)
    for y in (40, 80):
        d.line([(10 * scale, y * scale), (w - 10 * scale, y * scale)], fill=WOOD_DARK, width=2 * scale)
    small_tag(img, 'wood_sign', (23 * scale, 16 * scale), 6 * scale)
    return img


def rope(scale):
    w, h = 16 * scale, 120 * scale
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2 * scale, 0, w - 2 * scale, h], fill=WOOD, outline=None)
    for y in range(-20, 140, 20):
        d.line([(2 * scale, (y + 12) * scale), (w - 2 * scale, y * scale)], fill=WOOD_DARK, width=3 * scale)
    d.line([(2 * scale, 0), (2 * scale, h)], fill=NAVY, width=scale)
    d.line([(w - 2 * scale, 0), (w - 2 * scale, h)], fill=NAVY, width=scale)
    return img


def card_back():
    w, h = 900, 1260
    img = gradient(w, h, INDIGO, DEEP)
    d = ImageDraw.Draw(img)
    for y in range(0, h + 120, 120):
        for x in range((y // 120 % 2) * 60, w + 120, 120):
            d.text((x, y), '?', font=font(52), fill=VIOLET, anchor='mm')
    d.rounded_rectangle([28, 28, w - 28, h - 28], radius=56, outline=YELLOW, width=12)
    d.ellipse([230, 410, 670, 850], fill=CARD, outline=YELLOW, width=12)
    d.text((450, 630), '?', font=font(300), fill=YELLOW, anchor='mm')
    small_tag(img, 'card_back', (450, 1190), 38)
    return img


def spark():
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(16):
        a = i / 16 * math.tau - math.pi / 2
        r = 118 if i % 2 == 0 else 44
        pts.append((128 + r * math.cos(a), 128 + r * math.sin(a)))
    d.polygon(pts, fill=YELLOW, outline=NAVY)
    d.ellipse([100, 100, 156, 156], fill=OFFWHITE)
    small_tag(img, 'spark', (128, 128), 16)
    return img


def icon_face(d, c, r):
    bear(d, c, c, r, sleepy=False)
    d.text((c + r * .95, c - r * .95), '?', font=font(int(r * .95)), fill=YELLOW, anchor='mm', stroke_width=int(r * .06), stroke_fill=NAVY)


def app_icon():
    img = gradient(1024, 1024, VIOLET, DEEP)
    icon_face(ImageDraw.Draw(img), 512, 280)
    small_tag(img, 'app_icon', (512, 960), 38)
    return img.convert('RGB')


def icon_fg():
    img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    icon_face(ImageDraw.Draw(img), 512, 215)
    return img


def icon_bg():
    return gradient(1024, 1024, VIOLET, DEEP).convert('RGB')


def splash_logo():
    img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bear(d, 512, 410, 250)
    d.text((512, 790), 'Find the Imposter', font=font(96), fill=YELLOW, anchor='mm', stroke_width=5, stroke_fill=NAVY)
    small_tag(img, 'splash_logo', (512, 930), 34)
    return img


# ------------------------------------------------------------ prompts
STYLE = ('Style: original cartoon illustration, thick soft dark outlines, chunky rounded shapes, gentle cel shading, '
         'friendly sleepy-eyed lazy bears as the cast.')
PALETTE = ('Palette: deep purple #2B1452, indigo #3D1F7A, deep navy #0F0A1F, violet #7C4DFF, electric blue #4FC3F7, '
           'warm yellow #FFD54F, coral #FF6B8A, wood #A9713E.')
NEG = 'Negatives: no text or lettering{extra}, no photorealism, no scary or adult content, no existing brands or copyrighted characters, no busy detail inside safe areas.'


def prompt(subject, composition, safe_text, lighting, extra=''):
    return ' '.join([f'Subject: {subject}', f'Composition: {composition}', f'Safe area: {safe_text}', PALETTE,
                     f'Lighting: {lighting}', STYLE, NEG.format(extra=extra)])


BGS = [
    ('home_background', bg_home, [(.06, .60, .88, .39)], ['home', 'error'],
     prompt('three lazy bears lounging together at a cosy night party beneath a hanging wooden logo board that reads "Find the Imposter".',
            'portrait 9:19.5, 1080x2340. Logo in the top quarter, bears in the middle band, one bear glancing suspiciously sideways.',
            'bottom 40 % must be a calm, dark, low-detail floor for buttons and a banner.',
            'warm lamp glow on the bears, violet haze behind, soft vignette.', ' except the logo')),
    ('players_background', bg_players, [(.08, .07, .84, .89)], ['playerSetup', 'configuration'],
     prompt('a cosy party room at night with bunting along the ceiling and warm lamps on both side walls.',
            'portrait 9:19.5, 1080x2340. Decoration hugs the outer edges and top, with a wooden floor at the very bottom.',
            'central column, 84 % wide and 89 % tall, must stay calm for the sign and the player list.',
            'warm side lamps falling off to a soft indigo centre.')),
    ('pass_phone_background', bg_pass, [(.10, .26, .80, .59)], ['passPhone'],
     prompt('two bear paws at the bottom of the frame handing a smartphone from one to the other.',
            'portrait 9:19.5, 1080x2340. Paws and phone in the bottom 15 %, a spotlight cone falling from the top centre.',
            'centre band from 26 % to 85 % of the height must stay calm for a hanging sign and a button.',
            'one soft yellow spotlight against a dark navy room.')),
    ('your_turn_background', bg_turn, [(.14, .08, .72, .87)], ['readyToReveal', 'revealing', 'revealed'],
     prompt('an empty theatre stage with heavy coral-red curtains drawn to both sides and a wooden stage floor.',
            'portrait 9:19.5, 1080x2340. Curtains occupy the outer 15 % on each side, with no characters.',
            'centre column, 72 % wide, must stay calm for a large card.',
            'a round warm spotlight centred on the stage, darkness behind.')),
    ('ready_background', bg_ready, [(.12, .25, .76, .50)], ['allRevealed'],
     prompt('a joyful celebration scene of confetti and streamers bursting in from the edges.',
            'portrait 9:19.5, 1080x2340. Confetti concentrated around the border and thinning toward the centre.',
            'centre rectangle, 76 % wide and 50 % tall, must stay calm for a sign and a button.',
            'bright violet to indigo glow, sparkling highlights.')),
    ('round_background', bg_round, [(.08, .08, .84, .27), (.08, .69, .84, .28)], ['roundReady'],
     prompt('a group of lazy bears gathered around a round wooden table, talking and eyeing each other with suspicion.',
            'portrait 9:19.5, 1080x2340. Table and bears in the band from 38 % to 66 % of the height.',
            'the top band for a sign and the bottom band for two buttons and a banner must stay calm.',
            'warm pendant lamp over the table, night sky above.')),
]

OTHER = [
    # id, path, type, size, format, used_on, fn, prompt, extra
    ('settings_bear', f'{IMG}/mascot/settings_bear.png', 'mascot', '600x600', 'png', ['settings'], mascot_settings,
     prompt('a lazy bear holding a wrench and a large gear, looking pleased with itself.', 'centred full-body sticker on a transparent background, 600x600.',
            'keep a 5 % transparent margin on all sides.', 'soft even light with a warm rim.'), {}),
    ('imposter_bear', f'{IMG}/mascot/imposter_bear.png', 'mascot', '600x600', 'png', ['revealed'], mascot_imposter,
     prompt('a sneaky bear in a dark trench coat and red brimmed hat, eyes darting sideways.', 'centred bust on a transparent background, 600x600.',
            'keep a 5 % transparent margin on all sides.', 'moody top light with a coral rim.'), {}),
    ('card_back', f'{IMG}/ui/card_back.png', 'ui', '900x1260', 'png', ['readyToReveal', 'revealing'], card_back,
     prompt('the back of a mysterious playing card: a repeating pattern of question marks with one big glowing question mark in a central medallion.',
            'symmetrical, with a yellow rounded inner border, 900x1260.', 'centre circle stays clear because a progress ring is drawn over it.', 'soft inner glow.', ' except question marks'), {}),
    ('spark', f'{IMG}/ui/spark.png', 'ui', '256x256', 'png', ['revealed', 'allRevealed'], spark,
     prompt('a chunky cartoon spark burst star.', 'centred on a transparent background, 256x256.', 'none.', 'bright flat yellow with a white core.'), {}),
    ('app_icon', f'{IMG}/icon/app_icon.png', 'icon', '1024x1024', 'png', ['launcher'], app_icon,
     prompt('a lazy bear face with one suspicious eyebrow raised and a glowing question mark beside it.', 'centred and bold, legible at 48 px, 1024x1024, fully opaque.',
            'keep all key shapes inside the central 80 %.', 'violet glow behind the head.', ' except the question mark'), {}),
    ('app_icon_foreground', f'{IMG}/icon/app_icon_foreground.png', 'icon', '1024x1024', 'png', ['launcher'], icon_fg,
     prompt('the same bear face and question mark as the app icon, isolated.', 'transparent background, 1024x1024.',
            'all content inside the central 66 %, for Android adaptive masks.', 'matching the app icon.', ' except the question mark'), {}),
    ('app_icon_background', f'{IMG}/icon/app_icon_background.png', 'icon', '1024x1024', 'png', ['launcher'], icon_bg,
     prompt('a plain violet to deep purple gradient.', 'full-bleed, opaque, 1024x1024.', 'none.', 'flat.'), {}),
    ('splash_logo', f'{IMG}/icon/splash_logo.png', 'icon', '1024x1024', 'png', ['splash'], splash_logo,
     prompt('a lazy bear face above the words "Find the Imposter" in chunky rounded letters.', 'centred on a transparent background, 1024x1024.',
            'keep a 10 % transparent margin.', 'flat with a soft yellow rim.', ' except the logo'), {}),
]

DENSITY = [
    ('wood_sign', 'wood_sign.png', wood_sign, '360x120 @1x, 720x240 @2x, 1080x360 @3x',
     ['error', 'playerSetup', 'configuration', 'passPhone', 'readyToReveal', 'revealing', 'revealed', 'allRevealed', 'roundReady'],
     prompt('a warm wooden hanging sign board made of horizontal planks.', 'front view, empty face, transparent surroundings, 360x120 at 1x plus 2x and 3x.',
            'the centre must be plain enough to stretch and hold text. Corners stay within 40 px horizontally and 36 px vertically at 1x.', 'soft top light.'),
     {'center_slice_1x': {'left': 40, 'top': 36, 'right': 320, 'bottom': 84}}),
    ('rope', 'rope.png', rope, '16x120 @1x, 32x240 @2x, 48x360 @3x',
     ['error', 'playerSetup', 'configuration', 'passPhone', 'readyToReveal', 'revealing', 'revealed', 'allRevealed', 'roundReady'],
     prompt('a thick twisted rope, vertical.', 'transparent surroundings, tiles seamlessly top to bottom, 16x120 at 1x plus 2x and 3x.', 'none.', 'soft side light.'),
     {'tiles': 'vertical'}),
]


def load_status():
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, encoding='utf-8') as f:
        return {e['id']: e['status'] for e in json.load(f)['assets']}


def save(img, path, fmt):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if fmt == 'webp':
        img.convert('RGB').save(full, 'WEBP', quality=82, method=6)
    else:
        img.save(full, 'PNG', optimize=True)


def main():
    status = load_status()
    assets = []
    written = 0

    def entry(id_, path, type_, size, fmt, used, prompt_text, extra=None, default='placeholder'):
        assets.append({'id': id_, 'path': path, 'type': type_, 'size_px': size, 'format': fmt, 'used_on': used,
                       'status': status.get(id_, default), 'generation_prompt': prompt_text, **(extra or {})})

    for id_, fn, areas, used, text in BGS:
        path = f'{IMG}/backgrounds/{id_}.webp'
        if status.get(id_) != 'final':
            img = fn(areas)
            safe(img, areas)
            tag(img, id_)
            save(img, path, 'webp')
            written += 1
        entry(id_, path, 'background', '1080x2340', 'webp', used, text, {'safe_areas': [dict(zip('xywh', a)) for a in areas]})

    for id_, path, type_, size, fmt, used, fn, text, extra in OTHER:
        if status.get(id_) != 'final':
            save(fn(), path, fmt)
            written += 1
        entry(id_, path, type_, size, fmt, used, text, extra)

    for id_, filename, fn, size, used, text, extra in DENSITY:
        paths = [f'{IMG}/ui/{filename}', f'{IMG}/ui/2.0x/{filename}', f'{IMG}/ui/3.0x/{filename}']
        if status.get(id_) != 'final':
            for scale, path in zip((1, 2, 3), paths):
                save(fn(scale), path, 'png')
            written += 1
        entry(id_, paths[0], 'ui', size, 'png', used, text, {'variants': paths[1:], **extra})

    weights = [('Regular', 400), ('SemiBold', 600), ('Bold', 700), ('ExtraBold', 800), ('Black', 900)]
    for name, weight in weights:
        entry(f'nunito_{weight}', f'assets/fonts/Nunito/Nunito-{name}.ttf', 'font', '-', 'ttf', ['all'], None, {'weight': weight}, 'final')
    entry('nunito_licence', 'assets/fonts/Nunito/OFL.txt', 'font', '-', 'txt', ['all'], None, None, 'final')
    entry('imposter_words', 'assets/data/imposter_words.json', 'data', '900 entries', 'json', ['splash'], None, None, 'final')

    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump({'assets': assets}, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'{written} assets generated, {len(assets)} manifest entries')


if __name__ == '__main__':
    main()
