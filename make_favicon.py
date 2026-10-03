# Builds favicon set from the trophy art: tilted, with the site's hard offset shadow.
# Usage: python make_favicon.py <trophy.webp|png>
import sys
from PIL import Image, ImageChops
src = Image.open(sys.argv[1]).convert('RGBA')
src = src.crop(src.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
art = src.rotate(-11, resample=Image.BICUBIC, expand=True)           # slant
art = art.crop(art.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())

def tile(S):
    pad = 0.07 * S
    k = min((S - 2 * pad) / art.width, (S - 2 * pad) / art.height)
    t = art.resize((max(1, round(art.width * k)), max(1, round(art.height * k))), Image.LANCZOS)
    off = max(1, round(S * 0.045))
    canvas = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    x, y = (S - t.width) // 2 - off // 2, (S - t.height) // 2 - off // 2
    shadow = Image.new('RGBA', t.size, (11, 17, 64, 255)); shadow.putalpha(t.getchannel('A'))
    canvas.alpha_composite(shadow, (x + off, y + off))
    canvas.alpha_composite(t, (x, y))
    return canvas

# render big, then downsample so small sizes stay crisp
big = tile(1024)
sizes = {'favicon-512.png': 512, 'favicon-192.png': 192, 'apple-touch-icon.png': 180, 'favicon-32.png': 32, 'favicon-16.png': 16}
for name, s in sizes.items():
    img = big.resize((s, s), Image.LANCZOS)
    if name == 'apple-touch-icon.png':                                   # iOS wants an opaque tile
        bg = Image.new('RGBA', (s, s), (233, 235, 247, 255)); bg.alpha_composite(img); img = bg.convert('RGB')
    img.save('assets/' + name)
big.resize((48, 48), Image.LANCZOS).save('favicon.ico', sizes=[(48, 48), (32, 32), (16, 16)])
print('ok')
