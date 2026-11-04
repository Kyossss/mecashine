import adsk.core, adsk.fusion
# Side view (looking across the belt) of the top polisher with the REF beam cone and yarn envelope see-through, for the screenshot.
def run(_c):
    app = adsk.core.Application.get(); app.userInterface.activeSelections.clear()
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]
    for b in occ.component.bRepBodies:
        if b.name.startswith('REF'): b.isLightBulbOn = True; b.opacity = 0.35
    v = app.activeViewport; cam = v.camera
    cam.target = adsk.core.Point3D.create(110.5, 0, 38.0); cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.eye = adsk.core.Point3D.create(110.0, -150, 40.0)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1); cam.isFitView = False; cam.viewExtents = 14
    v.camera = cam; v.refresh(); print('ok')
