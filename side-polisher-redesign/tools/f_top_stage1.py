import adsk.core, adsk.fusion
# Top polisher redesign, stage 1: new component, copy of your carriage with its far wall and motor-side mount 15 mm longer,
# the 8 mm pin removed and a 608ZZ pocket in the far wall. Your original carriage is hidden, not changed.
CM = 0.1   # mm -> cm
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    if [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)']: raise Exception('component already exists')
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); comp = occ.component; comp.name = 'Top polisher redesign (Claude)'
    car0 = [b for b in root.bRepBodies if b.name == 'Body67'][0]
    car = car0.copyToComponent(occ); car.name = 'Carriage (legs +15 mm, 608ZZ pocket)'
    print('copied carriage', round(car.volume, 2), bb(car.boundingBox))
    # split just under the top plate (226 above the belt = Fusion z 443), move the lower part down 15, fill the gap
    pin = comp.constructionPlanes.createInput(); pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(443 * CM))
    plane = comp.constructionPlanes.add(pin); plane.name = 'top polish split z443'
    si = comp.features.splitBodyFeatures.createInput(car, plane, True)
    comp.features.splitBodyFeatures.add(si)
    bodies = [b for b in comp.bRepBodies]
    lower = [b for b in bodies if b.boundingBox.maxPoint.z <= 443 * CM + 1e-4]
    upper = [b for b in bodies if b.boundingBox.minPoint.z >= 443 * CM - 1e-4]
    print('after split', [(b.name, round(b.volume, 2), bb(b.boundingBox)) for b in bodies])
    oc = adsk.core.ObjectCollection.create(); [oc.add(b) for b in lower]
    mi = comp.features.moveFeatures.createInput2(oc); mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(-15 * CM), True)
    comp.features.moveFeatures.add(mi)
    # extrude the lower parts' top faces (now at z 428) back up to 443, joined to them
    for b in lower:
        faces = adsk.core.ObjectCollection.create()
        for f in b.faces:
            g = f.geometry
            if g.objectType.endswith('Plane') and abs(f.boundingBox.maxPoint.z - 428 * CM) < 1e-4 and abs(f.boundingBox.minPoint.z - 428 * CM) < 1e-4: faces.add(f)
        print('lower part', bb(b.boundingBox), 'top faces', faces.count)
        if faces.count == 0: raise Exception('no top faces on a lower part')
        ei = comp.features.extrudeFeatures.createInput(faces, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(15 * CM))
        ei.participantBodies = [b]
        ex = comp.features.extrudeFeatures.add(ei)
        if ex.bodies.item(0).boundingBox.maxPoint.z < 442.9 * CM:   # extruded the wrong way: flip
            ex.deleteMe()
            ei = comp.features.extrudeFeatures.createInput(faces, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(15 * CM)), adsk.fusion.ExtentDirections.NegativeExtentDirection)
            ei.participantBodies = [b]; comp.features.extrudeFeatures.add(ei)
    # join everything back into one carriage
    bodies = [b for b in comp.bRepBodies]
    target = [b for b in bodies if b.boundingBox.maxPoint.z > 443.5 * CM][0]
    tools = adsk.core.ObjectCollection.create(); [tools.add(b) for b in bodies if b != target]
    ci = comp.features.combineFeatures.createInput(target, tools); ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    comp.features.combineFeatures.add(ci)
    car = comp.bRepBodies.item(0); car.name = 'Carriage (legs +15 mm, 608ZZ pocket)'
    print('joined', comp.bRepBodies.count, round(car.volume, 2), bb(car.boundingBox))
    # remove the 8 mm pin and cut the 608ZZ pocket: one tool, 9 mm from y 50 to 71, 22.15 mm from y 71 to 78, on the new axis (z 403)
    tm = adsk.fusion.TemporaryBRepManager.get()
    def cyl(y0, y1, dia):
        return tm.createCylinderOrCone(adsk.core.Point3D.create(113.8, y0 * CM, 40.3), dia / 2 * CM, adsk.core.Point3D.create(113.8, y1 * CM, 40.3), dia / 2 * CM)
    t1 = cyl(50, 71.05, 9.0); t2 = cyl(71, 78, 22.15); tm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.UnionBooleanType)
    bf = comp.features.baseFeatures.add(); bf.startEdit(); tool = comp.bRepBodies.add(t1, bf); bf.finishEdit()
    tool = [b for b in comp.bRepBodies if b != car][0]
    tc = adsk.core.ObjectCollection.create(); tc.add(tool)
    ci = comp.features.combineFeatures.createInput(car, tc); ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    comp.features.combineFeatures.add(ci)
    car = comp.bRepBodies.item(0)
    print('pin out, pocket in', comp.bRepBodies.count, round(car.volume, 2), bb(car.boundingBox))
    car0.isLightBulbOn = False
    print('original carriage hidden')
