# Builds favicon set from the trophy art: tilted, hard offset shadow, on a white rounded-square tile.
# Usage: python make_favicon.py [assets/trophy.png]
import sys
from PIL import Image, ImageDraw
src = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'assets/trophy.png').convert('RGBA')
src = src.crop(src.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
art = src.rotate(-11, resample=Image.BICUBIC, expand=True)           # slant
art = art.crop(art.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())

def tile(S, rounded=True):
    canvas = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    r = round(S * 0.24) if rounded else 0
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((0, 0, S - 1, S - 1), radius=r, fill=(255, 255, 255, 255))   # white tile
    pad = 0.10 * S
    k = min((S - 2 * pad) / art.width, (S - 2 * pad) / art.height)
    t = art.resize((max(1, round(art.width * k)), max(1, round(art.height * k))), Image.LANCZOS)
    off = max(1, round(S * 0.035))
    x, y = (S - t.width) // 2 - off // 2, (S - t.height) // 2 - off // 2
    shadow = Image.new('RGBA', t.size, (11, 17, 64, 255)); shadow.putalpha(t.getchannel('A'))
    canvas.alpha_composite(shadow, (x + off, y + off))
    canvas.alpha_composite(t, (x, y))
    return canvas

# render big, then downsample so small sizes stay crisp
big = tile(1024)
sizes = {'favicon-512.png': 512, 'favicon-192.png': 192, 'favicon-32.png': 32, 'favicon-16.png': 16}
for name, n in sizes.items():
    big.resize((n, n), Image.LANCZOS).save('assets/' + name)
tile(1024, rounded=False).resize((180, 180), Image.LANCZOS).convert('RGB').save('assets/apple-touch-icon.png')   # iOS rounds it itself
big.resize((48, 48), Image.LANCZOS).save('favicon.ico', sizes=[(48, 48), (32, 32), (16, 16)])
print('ok')
