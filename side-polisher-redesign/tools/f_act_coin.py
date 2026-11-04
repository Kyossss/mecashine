import adsk.core
def run(_c):
    app = adsk.core.Application.get()
    [d for d in app.documents if d.name.startswith('Coin dispenser test fit')][0].activate(); print('active', app.activeDocument.name)
