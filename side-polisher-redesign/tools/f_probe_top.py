import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get()
    print('doc', app.activeDocument.name)
