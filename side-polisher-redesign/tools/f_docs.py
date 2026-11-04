import adsk.core
def run(_c):
    app = adsk.core.Application.get()
    print('active:', app.activeDocument.name)
    for d in app.documents: print('open:', d.name, '| saved' if d.isSaved else '| unsaved', '| modified' if d.isModified else '')
