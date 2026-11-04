import adsk.core, adsk.fusion, json
# Temporarily hide the bodies on the near (-y) side of the top station for a side screenshot; their tokens go to a file so f_restore_near.py puts them back.
LIST = 'F:/Research/ASPS/top polish/_hidden_for_shot.json'
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    hid = []
    def consider(b):
        if not b.isLightBulbOn or b.name.startswith('REF'): return
        B = b.boundingBox
        if B.maxPoint.y * 10 < -35 and B.maxPoint.x * 10 > 1030 and B.minPoint.x * 10 < 1210 and B.maxPoint.z * 10 > 230:
            b.isLightBulbOn = False; hid.append(b.entityToken)
    for b in root.bRepBodies: consider(b)
    def walk(o):
        if not o.isLightBulbOn: return
        for b in o.bRepBodies: consider(b)
        for c in o.childOccurrences: walk(c)
    for o in root.occurrences: walk(o)
    json.dump(hid, open(LIST, 'w')); print('hid', len(hid))
