import json,sys
p=sys.argv[1]
out=[]
for line in open(p,encoding='utf-8'):
    try: d=json.loads(line)
    except: continue
    t=d.get('type')
    if d.get('isCompactSummary') or (t=='summary'):
        out.append(('SUMMARY',str(d.get('message',{}).get('content',d.get('summary')))[:20000]))
        continue
    if t not in('user','assistant'): continue
    c=d.get('message',{}).get('content')
    if isinstance(c,str): txt=c
    else:
        txt=' '.join(x.get('text','') for x in (c or []) if isinstance(x,dict) and x.get('type')=='text')
    if txt.strip(): out.append((t,txt))
json.dump(out,open('msgs.json','w',encoding='utf-8'))
print(len(out), sum(1 for o in out if o[0]=='SUMMARY'))
