import numpy as np
from PIL import Image, ImageFilter
from collections import deque
SRC=r'C:/Users/RAKESH~1/AppData/Local/Temp/claude/C--Users-RAKESH-KUMAR-DABAS-Desktop-AI-Tutoring-Claude-stuff/7436c029-7c7e-45ba-bb65-3a96254e7c52/images/8.webp'
im=Image.open(SRC).convert('RGB')
c=im.crop((240,12,520,575))
a=np.asarray(c).astype(int); H,W,_=a.shape
mx=a.max(2); mn=a.min(2)
paper=(mx>168)&((mx-mn)<46)
def components(mask):
    lab=np.zeros(mask.shape,int); n=0; sizes={}
    for y in range(H):
        for x in range(W):
            if mask[y,x] and not lab[y,x]:
                n+=1; lab[y,x]=n; dq=deque([(y,x)]); s=0
                while dq:
                    cy,cx=dq.popleft(); s+=1
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<H and 0<=nx<W and mask[ny,nx] and not lab[ny,nx]:
                            lab[ny,nx]=n; dq.append((ny,nx))
                sizes[n]=s
    return lab,sizes
lab,sz=components(paper)
border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])
bg=np.zeros((H,W),bool)
for k,s in sz.items():
    if k in border or s>260: bg|=(lab==k)
fg=~bg
lab2,sz2=components(fg); big=max(sz2,key=sz2.get); fg=lab2==big
al=Image.fromarray(fg.astype(np.uint8)*255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
out=c.convert('RGBA'); out.putalpha(al)
bbox=al.point(lambda v:255 if v>20 else 0).getbbox(); print('bbox',bbox)
out=out.crop(bbox); out=out.resize((out.width*2,out.height*2),Image.LANCZOS)
out.save('assets/neon.png'); print(out.size)
bgd=Image.new('RGBA',out.size,(20,25,90,255)); bgd.alpha_composite(out); bgd.convert('RGB').save('assets/_neon_preview.png')
