#!/usr/bin/env python3
"""Builds docs/assets/index.html from the manifest and the word pack.

Run from the project root: python3 tool/build_asset_library.py
"""
import collections
import html
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs/assets/index.html')
REL = '../../'
INK, OFFWHITE = '#23272B', '#F7F4FF'
esc = html.escape

PALETTE = [
    ('Deep purple', '#2B1452', 'deepPurple'), ('Indigo', '#3D1F7A', 'indigo'), ('Deep navy', '#0F0A1F', 'deepNavy'),
    ('Violet', '#7C4DFF', 'violet'), ('Electric blue', '#4FC3F7', 'electricBlue'), ('Warm yellow', '#FFD54F', 'warmYellow'),
    ('Coral', '#FF6B8A', 'coral'), ('Off-white', '#F7F4FF', 'offWhite'), ('Card dark', '#1C1333', 'cardDark'),
    ('Civilian accent', '#5C6BC0', 'civilian'), ('Imposter accent', '#E53935', 'imposter'),
    ('Cream (added)', '#FFF1D6', 'cream'), ('Wood (added)', '#A9713E', 'wood'), ('Wood dark (added)', '#6E4321', 'woodDark'),
]
WEIGHTS = [(400, 'Regular'), (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')]
SCALE = [('displayLarge', 44, 900, 'Find the Imposter'), ('display', 36, 900, 'Pass to Priya'), ('headline', 28, 800, 'Who’s playing?'),
         ('title', 22, 800, 'Show hint to imposter'), ('button', 20, 800, 'Hide & pass'), ('body', 16, 600, 'Best with 4–10 players'), ('label', 14, 700, 'Player 3 of 6')]

SECTIONS = [('palette', 'Palette'), ('type', 'Type'), ('backgrounds', 'Backgrounds'), ('art', 'Mascots & UI art'),
            ('components', 'Components'), ('icon', 'Icon & splash'), ('words', 'Word pack'), ('status', 'Status')]

CSS = r"""
@font-face{font-family:'Nunito App';font-weight:400;src:url('../../assets/fonts/Nunito/Nunito-Regular.ttf')}
@font-face{font-family:'Nunito App';font-weight:600;src:url('../../assets/fonts/Nunito/Nunito-SemiBold.ttf')}
@font-face{font-family:'Nunito App';font-weight:700;src:url('../../assets/fonts/Nunito/Nunito-Bold.ttf')}
@font-face{font-family:'Nunito App';font-weight:800;src:url('../../assets/fonts/Nunito/Nunito-ExtraBold.ttf')}
@font-face{font-family:'Nunito App';font-weight:900;src:url('../../assets/fonts/Nunito/Nunito-Black.ttf')}
:root{--desk:#E8ECEF;--sheet:#FFFFFF;--ink:#23272B;--muted:#5C666F;--pencil-blue:#1C6DD0;--mark:#D92D20;--rule:#C6CED5;
--display:'Patrick Hand','Chalkboard SE','Comic Sans MS',cursive;--body:'Nunito',system-ui,sans-serif;--app:'Nunito App',system-ui,sans-serif;
--deep:#2B1452;--indigo:#3D1F7A;--navy:#0F0A1F;--violet:#7C4DFF;--blue:#4FC3F7;--yellow:#FFD54F;--coral:#FF6B8A;--off:#F7F4FF;--card:#1C1333;--civ:#5C6BC0;--imp:#E53935;--cream:#FFF1D6;--wood:#A9713E;--wood2:#6E4321}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--desk);color:var(--ink);font:16px/1.5 var(--body)}
.safe-strip{position:fixed;inset:0 0 auto 0;height:env(safe-area-inset-top);background:var(--desk);z-index:30}
.wrap{max-width:1500px;margin:0 auto;display:grid;gap:40px;grid-template-columns:minmax(0,1fr);
padding:calc(24px + env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) calc(48px + env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left))}
h1,h2,h3{font-family:var(--display);font-weight:400;margin:0;line-height:1.1}
h1{font-size:clamp(44px,8vw,76px)}
h2{font-size:clamp(34px,5vw,46px)}
h3{font-size:26px;margin-bottom:12px}
.lead{color:var(--muted);max-width:65ch;margin:10px 0 0;font-size:18px}
nav{position:sticky;top:env(safe-area-inset-top);z-index:20;background:var(--desk);display:flex;gap:10px;flex-wrap:wrap;padding:12px 0;border-bottom:2px dashed var(--rule)}
nav a{font:21px/1.2 var(--display);color:var(--ink);text-decoration:none;background:#fff;border:1.5px solid var(--ink);border-radius:12px;padding:6px 14px;white-space:nowrap}
nav a:hover,nav a:focus-visible{background:#FFEC99;outline:2px solid var(--pencil-blue);outline-offset:1px}
@media (max-width:700px){nav{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}nav::-webkit-scrollbar{display:none}}
section{scroll-margin-top:calc(84px + env(safe-area-inset-top));min-width:0}
section>p{color:var(--muted);margin:6px 0 20px}
.board{display:grid;gap:24px}
.board.wide{grid-template-columns:minmax(0,1fr)}
.board.two{grid-template-columns:repeat(auto-fill,minmax(min(100%,560px),1fr))}
.board.four{grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr))}
.sheet{margin:0;background:var(--sheet);padding:18px;border-radius:6px;box-shadow:0 1px 0 var(--rule),0 3px 10px rgba(35,39,43,.10);min-width:0}
.cap{font-family:var(--display);font-size:24px;line-height:1.2;margin-top:12px}
.meta{color:var(--muted);font-size:14px;overflow-wrap:anywhere;margin:4px 0 0}
code{font-size:.92em}
details{margin-top:8px}
summary{cursor:pointer;color:var(--pencil-blue);font-family:var(--display);font-size:20px}
details p{font-size:14px;color:var(--muted);margin:6px 0 0}
.swatch{height:96px;border-radius:6px;border:1.5px solid var(--ink)}
.ratio{display:flex;gap:14px;flex-wrap:wrap;font-size:14px;margin-top:4px}
.spec{font-family:var(--app);color:var(--ink);overflow-wrap:anywhere;line-height:1.2}
.row{display:flex;justify-content:space-between;gap:16px;align-items:baseline;border-bottom:1px solid var(--rule);padding:12px 0;flex-wrap:wrap}
.row small{color:var(--muted);font-family:var(--body)}
.phone{position:relative;aspect-ratio:1080/2340;border:3px solid var(--ink);border-radius:30px;overflow:hidden;background:#000}
.phone img{position:absolute;inset:0;width:100%;height:100%;display:block}
.safe{position:absolute;border:2px solid var(--blue);background:rgba(79,195,247,.16)}
.checker{background-color:#fff;background-image:linear-gradient(45deg,#D5DBE0 25%,transparent 25%,transparent 75%,#D5DBE0 75%),linear-gradient(45deg,#D5DBE0 25%,transparent 25%,transparent 75%,#D5DBE0 75%);background-size:24px 24px;background-position:0 0,12px 12px;border-radius:6px;padding:12px;display:flex;justify-content:center;align-items:center;min-height:190px}
.checker img{max-width:100%;max-height:300px;display:block}
.stage{background:linear-gradient(var(--deep),var(--indigo));border-radius:8px;padding:28px 16px;display:flex;flex-wrap:wrap;gap:22px;justify-content:center;align-items:center;font-family:var(--app);min-height:220px}
.wood{position:relative;margin-top:60px;background:linear-gradient(var(--wood),#8e5c30);border:4px solid var(--navy);border-radius:14px;padding:16px 34px;color:var(--cream);font-weight:900;font-size:26px;text-align:center}
.wood::before,.wood::after{content:"";position:absolute;bottom:100%;width:8px;height:60px;background:repeating-linear-gradient(-30deg,var(--wood) 0 6px,var(--wood2) 6px 10px)}
.wood::before{left:18%}.wood::after{right:18%}
.candy{min-height:56px;min-width:150px;padding:0 26px;border-radius:24px;border:3px solid var(--navy);font:800 20px var(--app);display:flex;align-items:center;justify-content:center;box-shadow:inset 0 5px 0 rgba(255,255,255,.45),0 6px 0 var(--navy)}
.candy.p{background:var(--yellow);color:var(--deep)}
.candy.s{background:var(--violet);color:var(--off)}
.candy.d{background:#6f6888;color:#D8D3E6;box-shadow:none;border-style:dashed}
.candy.x{background:#E5B93D;color:var(--deep);box-shadow:inset 0 3px 0 rgba(0,0,0,.14),0 2px 0 var(--navy);transform:translateY(4px)}
.pill{background:var(--cream);color:var(--deep);border-radius:999px;padding:5px;font-weight:800}
.pill span{display:block;border:2px dashed var(--wood);border-radius:999px;padding:7px 18px}
.card{width:170px;height:238px;border-radius:18px;border:4px solid var(--navy);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:12px;overflow:hidden}
.card img{width:100%;height:100%;object-fit:cover}
.card.back{padding:0}
.card.civ{background:var(--card);color:var(--off);border-color:var(--civ)}
.card.imp{background:var(--card);color:var(--off);border-color:var(--imp)}
.card small{font-weight:700;opacity:.8}
.card b{font-weight:900;font-size:34px;line-height:1.1;margin-top:6px}
.card.imp b{color:var(--imp);font-size:26px}
.card.imp img{width:92px;height:92px;object-fit:contain}
.burst{width:150px;height:150px;background:var(--yellow);clip-path:polygon(50% 0,59% 30%,85% 15%,70% 41%,100% 50%,70% 59%,85% 85%,59% 70%,50% 100%,41% 70%,15% 85%,30% 59%,0 50%,30% 41%,15% 15%,41% 30%)}
.icons{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end}
.icons figure{margin:0;text-align:center;font-size:14px;color:var(--muted)}
.icons img{display:block;border-radius:18%}
.big{width:1024px;max-width:100%;height:auto;display:block;border-radius:6px}
.mask{position:relative;width:192px;height:192px;overflow:hidden}
.mask img{position:absolute;inset:0;width:100%;height:100%;border-radius:0}
.mask.circle{border-radius:50%}.mask.squircle{border-radius:32%}.mask.round{border-radius:14%}
.mask i{position:absolute;inset:17%;border:2px dashed var(--yellow);border-radius:50%}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font:400 20px var(--display)}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tfoot td{font-weight:700;border-top:2px solid var(--ink)}
.badge{display:inline-block;border-radius:999px;padding:1px 10px;font-size:13px;font-weight:700;border:1.5px solid}
.badge.placeholder{color:#8A5A00;background:#FFF4D6;border-color:#8A5A00}
.badge.final{color:#116B3A;background:#E5F7EC;border-color:#116B3A}
"""


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def section(id_, title, intro, body):
    return f'<section id="{id_}"><h2>{esc(title)}</h2><p>{esc(intro)}</p>{body}</section>\n'


def palette():
    cards = ''
    for name, hex_, token in PALETTE:
        cards += (f'<div class="sheet"><div class="swatch" style="background:{hex_}"></div><div class="cap">{esc(name)}</div>'
                  f'<p class="meta"><code>{hex_}</code> · <code>AppColors.{token}</code></p>'
                  f'<div class="ratio"><span>vs off-white <b>{contrast(hex_, OFFWHITE):.1f}:1</b></span><span>vs ink <b>{contrast(hex_, INK):.1f}:1</b></span></div></div>')
    return section('palette', 'Palette', 'Spec colours plus three added for wood and stitching. Ratios are WCAG contrast.', f'<div class="board four">{cards}</div>')


def typography():
    weights = ''.join(f'<div class="row"><span class="spec" style="font-weight:{w};font-size:30px">Find the Imposter</span><small>{w} · Nunito-{n}.ttf</small></div>' for w, n in WEIGHTS)
    scale = ''.join(f'<div class="row"><span class="spec" style="font-weight:{w};font-size:{s}px">{esc(t)}</span><small><code>{k}</code> · {s} / {w}</small></div>' for k, s, w, t in SCALE)
    return section('type', 'Type', 'Nunito, bundled with the app so nothing downloads at runtime.',
                   f'<div class="board two"><div class="sheet"><h3>Weights</h3>{weights}</div><div class="sheet"><h3>Display scale</h3>{scale}</div></div>')


def backgrounds(assets):
    out = ''
    for a in assets:
        if a['type'] != 'background':
            continue
        overlays = ''.join(f'<div class="safe" style="left:{s["x"]*100:.1f}%;top:{s["y"]*100:.1f}%;width:{s["w"]*100:.1f}%;height:{s["h"]*100:.1f}%"></div>' for s in a['safe_areas'])
        out += (f'<div class="sheet"><div class="phone"><img src="{REL}{a["path"]}" alt="{a["id"]} placeholder">{overlays}</div>'
                f'<div class="cap">{a["id"]}</div><p class="meta"><code>{a["path"]}</code><br>{a["size_px"]} · used on {", ".join(a["used_on"])}</p>'
                f'<details><summary>Generation prompt</summary><p>{esc(a["generation_prompt"])}</p></details></div>')
    return section('backgrounds', 'Backgrounds', 'Each placeholder in a phone frame. The blue overlay marks where UI sits.', f'<div class="board four">{out}</div>')


def art(assets):
    out = ''
    for a in assets:
        if a['type'] not in ('mascot', 'ui'):
            continue
        extra = ''
        if 'center_slice_1x' in a:
            c = a['center_slice_1x']
            extra = f'<br>9-slice centre at 1x: left {c["left"]}, top {c["top"]}, right {c["right"]}, bottom {c["bottom"]}'
        if a.get('tiles'):
            extra = '<br>Tiles vertically'
        src = a['variants'][1] if a.get('variants') else a['path']
        out += (f'<div class="sheet"><div class="checker"><img src="{REL}{src}" alt="{a["id"]} placeholder"></div><div class="cap">{a["id"]}</div>'
                f'<p class="meta"><code>{a["path"]}</code><br>{a["size_px"]}{extra}</p>'
                f'<details><summary>Generation prompt</summary><p>{esc(a["generation_prompt"])}</p></details></div>')
    return section('art', 'Mascots & UI art', 'Shown on a checkerboard so transparency is visible.', f'<div class="board four">{out}</div>')


def components():
    def sheet(title, body, note):
        return f'<div class="sheet"><div class="stage">{body}</div><div class="cap">{title}</div><p class="meta">{note}</p></div>'

    bear = f'{REL}assets/images/mascot/imposter_bear.png'
    back = f'{REL}assets/images/ui/card_back.png'
    body = (sheet('WoodSign', '<div class="wood">Pass to Priya</div>', 'In the app this uses the 9-slice image and rope tile. CSS recreation here.')
            + sheet('CandyButton', '<div class="candy p">Primary</div><div class="candy s">Secondary</div><div class="candy d">Disabled</div><div class="candy x">Pressed</div>', 'At least 56 dp tall. Drawn in code.')
            + sheet('StitchedPill', '<div class="pill"><span>Best with 4–10 players</span></div><div class="pill"><span>Player 3 of 6</span></div><div class="pill"><span>Hint: Cheesy</span></div>', 'Cream label with dashed stitching. Drawn in code.')
            + sheet('SecretRevealCard', f'<div class="card back"><img src="{back}" alt="Card back"></div><div class="card civ"><small>The secret word</small><b>Pizza</b></div><div class="card imp"><img src="{bear}" alt="Imposter bear"><b>IMPOSTER</b><small>Hint: Cheesy</small></div>', 'Back, civilian front and imposter front. The front is drawn in code.')
            + sheet('SparkBurst', '<div class="burst" role="img" aria-label="Spark burst"></div>', 'Scale and fade on reveal. Removed when animations are off.'))
    return section('components', 'Components', 'HTML and CSS recreations in the real palette.', f'<div class="board two">{body}</div>')


def icons():
    p = f'{REL}assets/images/icon'
    sizes = ''.join(f'<figure><img src="{p}/app_icon.png" width="{s}" height="{s}" alt="App icon at {s} pixels">{s}</figure>' for s in (48, 96, 192))
    masks = ''.join(f'<figure><div class="mask {m}"><img src="{p}/app_icon_background.png" alt=""><img src="{p}/app_icon_foreground.png" alt="Adaptive icon, {m} mask"><i></i></div>{m}</figure>' for m in ('circle', 'squircle', 'round'))
    body = (f'<div class="board two"><div class="sheet"><h3>Launcher sizes</h3><div class="icons">{sizes}</div></div>'
            f'<div class="sheet"><h3>Adaptive masks</h3><div class="icons">{masks}</div><p class="meta">Dashed circle: the central 66 % that every mask keeps.</p></div>'
            f'<div class="sheet"><h3>1024 px</h3><img class="big" src="{p}/app_icon.png" alt="App icon at 1024 pixels"></div>'
            f'<div class="sheet"><h3>Splash logo</h3><div class="checker"><img src="{p}/splash_logo.png" alt="Splash logo" style="max-height:520px"></div></div></div>')
    return section('icon', 'Icon & splash', 'How the icon holds up at launcher sizes and under Android masks.', body)


def words():
    with open(os.path.join(ROOT, 'assets/data/imposter_words.json'), encoding='utf-8') as f:
        data = json.load(f)
    diffs = ['easy', 'medium', 'hard']
    by = collections.Counter((e['category'], e['difficulty']) for e in data)
    cats = sorted({e['category'] for e in data})
    rows = ''.join(f'<tr><td>{c}</td>' + ''.join(f'<td class="n">{by[(c, d)] or "–"}</td>' for d in diffs) + f'<td class="n">{sum(by[(c, d)] for d in diffs)}</td></tr>' for c in cats)
    totals = [sum(1 for e in data if e['difficulty'] == d) for d in diffs]
    foot = '<tfoot><tr><td>Total</td>' + ''.join(f'<td class="n">{t}</td>' for t in totals) + f'<td class="n">{len(data)}</td></tr></tfoot>'
    table = f'<div class="scroll"><table><thead><tr><th>Category</th><th class="n">Easy</th><th class="n">Medium</th><th class="n">Hard</th><th class="n">Total</th></tr></thead><tbody>{rows}</tbody>{foot}</table></div>'
    sample = random.Random(20261111).sample(data, 10)
    srows = ''.join(f'<tr><td><code>{e["id"]}</code></td><td>{esc(e["word"])}</td><td>{esc(e["hint"])}</td><td>{e["category"]}</td></tr>' for e in sample)
    stable = f'<div class="scroll"><table><thead><tr><th>ID</th><th>Word</th><th>Hint</th><th>Category</th></tr></thead><tbody>{srows}</tbody></table></div>'
    india = sum(1 for e in data if 'india' in e['tags'])
    return section('words', 'Word pack', f'{len(data)} entries, {india} of them India-familiar. Built and validated by tool/build_words.dart.',
                   f'<div class="board two"><div class="sheet"><h3>Counts</h3>{table}</div><div class="sheet"><h3>10 random samples</h3>{stable}</div></div>')


def status(assets):
    c = collections.Counter(a['status'] for a in assets)
    rows = ''.join(f'<tr><td><code>{a["id"]}</code></td><td>{a["type"]}</td><td><code>{a["path"]}</code></td><td>{a["size_px"]}</td><td><span class="badge {a["status"]}">{a["status"]}</span></td></tr>' for a in assets)
    return section('status', 'Status', f'{c["placeholder"]} placeholder, {c["final"]} final.',
                   f'<div class="sheet scroll"><table><thead><tr><th>ID</th><th>Type</th><th>Path</th><th>Size</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>')


def main():
    with open(os.path.join(ROOT, 'docs/assets/manifest.json'), encoding='utf-8') as f:
        assets = json.load(f)['assets']
    nav = ''.join(f'<a href="#{k}">{esc(t)}</a>' for k, t in SECTIONS)
    body = palette() + typography() + backgrounds(assets) + art(assets) + components() + icons() + words() + status(assets)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Imposter Asset Library</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&family=Patrick+Hand&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="safe-strip"></div>
<main class="wrap">
<header><h1>Find the Imposter — Assets</h1>
<p class="lead">Every colour, font, image and word the app ships with. Illustrations are placeholders at final size and path, so finals can replace them with no code changes.</p></header>
<nav aria-label="Sections">{nav}</nav>
{body}</main></body></html>
'''
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
