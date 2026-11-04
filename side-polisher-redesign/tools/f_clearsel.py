import adsk.core
def run(_c):
    adsk.core.Application.get().userInterface.activeSelections.clear(); print('ok')
