import json,sys
p=sys.argv[1]; out=[]
lines=open(p,encoding='utf-8').readlines()
start=None
for i,l in enumerate(lines):
    if 'major remodeling' in l and start is None: start=i
for l in lines[start:start+400]:
    d=json.loads(l)
    c=d.get('message',{}).get('content')
    if not isinstance(c,list): continue
    for x in c:
        if not isinstance(x,dict): continue
        if x.get('type')=='tool_use' and x.get('name') in ('AskUserQuestion',):
            out.append('ASK '+json.dumps(x['input'])[:4000])
        if x.get('type')=='tool_result':
            s=json.dumps(x.get('content'))
            if 'answer' in s.lower() and ('kit' in s.lower() or 'pillar' in s.lower()): out.append('RES '+s[:3000])
        if x.get('type')=='image': out.append('IMAGE in '+d['type'])
open('ask.txt','w',encoding='utf-8').write('\n\n'.join(out))
