import adsk.core
def run(_c):
    ui = adsk.core.Application.get().userInterface
    out = []
    for c in ui.commandDefinitions:
        try:
            if 'olor' in c.id or 'olor' in c.name: out.append(c.id + ' | ' + c.name)
        except Exception: pass
    print('\n'.join(out))
