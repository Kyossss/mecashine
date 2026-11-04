import base64,sys,os
D=sys.argv[1]
def b64(n): return base64.b64encode(open(os.path.join(D,n),'rb').read()).decode()
W=1600
out=[]
def panel(img,iw,ih,x0,y0,scale,labels,title):
    s=[f'<image href="data:image/png;base64,{b64(img)}" x="{x0}" y="{y0}" width="{iw*scale:.0f}" height="{ih*scale:.0f}"/>']
    for (px,py,lx,ly,text,anchor) in labels:
        X=x0+px*scale; Y=y0+py*scale
        s.append(f'<line x1="{X:.0f}" y1="{Y:.0f}" x2="{lx}" y2="{ly}" stroke="#111" stroke-width="2"/>')
        s.append(f'<circle cx="{X:.0f}" cy="{Y:.0f}" r="6" fill="#111"/>')
        lines=text.split('|'); w=max(len(l) for l in lines)*10.5+20; h=len(lines)*24+12
        rx=lx-w if anchor=='end' else (lx-w/2 if anchor=='middle' else lx)
        ry=ly-h/2
        s.append(f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{w:.0f}" height="{h}" fill="#fff" stroke="#111" stroke-width="1.5" rx="4"/>')
        for i,l in enumerate(lines):
            s.append(f'<text x="{rx+w/2:.0f}" y="{ry+28+i*24:.0f}" text-anchor="middle">{l}</text>')
    s.append(f'<text x="{W/2}" y="{y0+ih*scale+40:.0f}" text-anchor="middle" font-weight="bold">{title}</text>')
    return s
# panel a: full (2090x1033)
sa=0.62; xa=170; ya=60
la=[(691,353,260,90,'Slat conveyor belt','middle'),
    (493,401,140,640,'Conveyor belt servo','middle'),
    (1303,356,820,40,'Side polisher|(pincer jaws and brushes)','middle'),
    (1303,41,1280,30,'Side-jaw servo|(rack and pinion)','start'),
    (1579,449,1590,250,'Top polisher|(servo-lifted roller carriage)','end'),
    (1411,509,820,660,'Shoe (test model)','middle'),
    (1782,780,1440,700,'Base plate','start')]
out+=panel('full_c.png',2090,1033,xa,ya,sa,la,'(a) Full assembly')
# panel b: close (1970x1356)
sb=0.58; xb=330; yb=ya+1033*sa+110
lb=[(840,121,180,yb+40,'Side-jaw servo|(rack and pinion)','middle'),
    (590,416,170,yb+260,'Pincer arm|with side brush','middle'),
    (620,856,170,yb+560,'Shoe (test model)','middle'),
    (990,856,1100,yb+780,'Side brush motor','start'),
    (1300,186,1460,yb+60,'Top roller|carriage','middle'),
    (1520,576,1460,yb+420,'Carriage lift rack','middle'),
    (300,1256,170,yb+760,'Slat conveyor','middle')]
out+=panel('close_c.png',1970,1356,xb,yb,sb,lb,'(b) Close-up of the side and top polishing stations')
H=int(yb+1356*sb+70)
html=f'''<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0;background:#fff}}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif" font-size="18">
{chr(10).join(out)}
</svg></body></html>'''
open(os.path.join(D,'fig3.html'),'w',encoding='utf-8').write(html)
print(W,H)
