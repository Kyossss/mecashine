import adsk.core, adsk.fusion
# Hide the gooseneck nozzle (not deleted).
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    b = [b for b in root.bRepBodies if b.name == 'Body109'][0]; b.isLightBulbOn = False; print('hidden', b.name)
