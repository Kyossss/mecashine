import adsk.core, adsk.fusion
# Open "Conveyor assembly 2" (ASPS - Design V3) in a new tab, read-only use; report what it contains.
def run(_c):
    app = adsk.core.Application.get()
    df = app.data.findFileById('urn:adsk.wipprod:dm.lineage:1Dg4jld7Qu-LRRLIx02NgQ')
    doc = app.documents.open(df, True)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    print('opened', doc.name, 'version', df.versionNumber)
    print([o.name for o in root.occurrences if '(Claude)' in o.component.name])
