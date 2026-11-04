import adsk.core, adsk.fusion, json
LIST = 'F:/Research/ASPS/top polish/_hidden_for_shot.json'
def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); n = 0
    for t in json.load(open(LIST)):
        for e in d.findEntityByToken(t): e.isLightBulbOn = True; n += 1
    print('restored', n)
