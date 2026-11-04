import adsk.core, adsk.fusion
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    print([o.name for o in root.occurrences][-8:])
