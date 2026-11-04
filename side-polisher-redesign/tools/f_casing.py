import adsk.core, adsk.fusion
# Casing box of the real prototype, 500 x 295 x 185 mm, on the floor beside the board on the reflector (+y) side, flush with the board edge,
# near end level with the board's entry end. Positions on the lid are estimates from the top-down photo.
# Your TFT occurrence and its frame bodies (Body111, Body112) are copied into the lid; the originals are hidden, not changed.
CM = 0.1
X0, X1 = 200.0, 700.0           # along the board
Y0, Y1 = 175.0, 470.0           # board edge at y 175, box 295 wide
Z0, Z1 = 109.0, 294.0           # floor (underside of the board) to the lid, 185 high
WALL = 9.0                      # painted plywood
TFT_X, BTN_X = 392.0, 300.0     # TFT centre and the two buttons, along x
YC = (Y0 + Y1) / 2
def P(x, y, z): return adsk.core.Point3D.create(x * CM, y * CM, z * CM)
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    if [o for o in root.occurrences if o.component.name == 'Casing box (Claude)']: raise Exception('component already exists')
    tm = adsk.fusion.TemporaryBRepManager.get()
    X, Y, Z = adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0), adsk.core.Vector3D.create(0, 0, 1)
    def box(x0, x1, y0, y1, z0, z1):
        return tm.createBox(adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), X, Y, (x1 - x0) * CM, (y1 - y0) * CM, (z1 - z0) * CM))
    # TFT stack as it is now: frame Body111 x 383..473, y 209..339, bottom z 395; module footprint x 400..456, y 225..323
    frame = [b for b in root.bRepBodies if b.name in ('Body111', 'Body112')]
    tft = [o for o in root.occurrences if o.component.name.startswith('TFT SPI Serial LCD Module')]
    if len(frame) != 2 or len(tft) != 1: raise Exception('TFT parts not found %d %d' % (len(frame), len(tft)))
    dx, dy, dz = TFT_X - 428.0, YC - 274.0, Z1 - 395.0
    shell = box(X0, X1, Y0, Y1, Z0, Z1)
    tm.booleanOperation(shell, box(X0 + WALL, X1 - WALL, Y0 + WALL, Y1 - WALL, Z0 + WALL, Z1 - WALL), adsk.fusion.BooleanTypes.DifferenceBooleanType)
    tm.booleanOperation(shell, box(400 + dx - 0.5, 456 + dx + 0.5, 225 + dy - 0.5, 323 + dy + 0.5, Z1 - WALL - 1, Z1 + 1), adsk.fusion.BooleanTypes.DifferenceBooleanType)   # TFT window
    btns = []
    for yb in (YC - 20, YC + 20):
        tm.booleanOperation(shell, tm.createCylinderOrCone(P(BTN_X, yb, Z1 - WALL - 1), 6.2 * CM, P(BTN_X, yb, Z1 + 1), 6.2 * CM), adsk.fusion.BooleanTypes.DifferenceBooleanType)
        b = tm.createCylinderOrCone(P(BTN_X, yb, Z1 - WALL - 6), 6 * CM, P(BTN_X, yb, Z1), 6 * CM)
        tm.booleanOperation(b, tm.createCylinderOrCone(P(BTN_X, yb, Z1), 8 * CM, P(BTN_X, yb, Z1 + 7), 8 * CM), adsk.fusion.BooleanTypes.UnionBooleanType)
        btns.append(b)
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); comp = occ.component; comp.name = 'Casing box (Claude)'
    bf = comp.features.baseFeatures.add(); bf.startEdit()
    comp.bRepBodies.add(shell, bf); [comp.bRepBodies.add(b, bf) for b in btns]
    bf.finishEdit()
    names = ['Casing box 500x295x185', 'Button red', 'Button black']
    for b, n in zip(comp.bRepBodies, names): b.name = n
    # copies of your TFT frame bodies, moved onto the lid
    oc = adsk.core.ObjectCollection.create()
    for b in frame:
        c = b.copyToComponent(occ); c.name = 'TFT frame ' + b.name; oc.add(c)
    mi = comp.features.moveFeatures.createInput2(oc)
    mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(dx * CM), adsk.core.ValueInput.createByReal(dy * CM), adsk.core.ValueInput.createByReal(dz * CM), True)
    comp.features.moveFeatures.add(mi)
    # a second instance of your TFT component, placed in the lid; the original instance is hidden
    m = tft[0].transform2.copy() if hasattr(tft[0], 'transform2') else tft[0].transform.copy()
    t = m.translation; t.add(adsk.core.Vector3D.create(dx * CM, dy * CM, dz * CM)); m.translation = t
    new = root.occurrences.addExistingComponent(tft[0].component, m)
    tft[0].isLightBulbOn = False
    for b in frame: b.isLightBulbOn = False
    def bb(B): return [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)]
    for b in comp.bRepBodies: print(b.name, bb(b.boundingBox))
    print('TFT now', bb(new.boundingBox))
