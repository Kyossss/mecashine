import adsk.core, adsk.fusion
# Give the spray station component a different component-cycling colour (the viewport shows cycling colours, not appearances).
def run(_c):
    app = adsk.core.Application.get(); ui = app.userInterface
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]
    ui.activeSelections.clear(); ui.activeSelections.add(occ)
    ui.commandDefinitions.itemById('CycleComponentColorCmd').execute()
    print('cycled')
