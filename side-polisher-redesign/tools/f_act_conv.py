import adsk.core
def run(_c):
    app = adsk.core.Application.get()
    [d for d in app.documents if d.name.startswith('Conveyor assembly 2')][0].activate(); print('ok')
