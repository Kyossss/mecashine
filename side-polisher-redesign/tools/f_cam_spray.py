import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get(); app.userInterface.activeSelections.clear()
    v = app.activeViewport; cam = v.camera
    cam.target = adsk.core.Point3D.create(68.0, 0, 23.5)
    cam.eye = adsk.core.Point3D.create(68.0 - 38, -45, 23.5 + 30)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1); cam.isFitView = False; cam.viewExtents = 17
    v.camera = cam; v.refresh(); print('ok')
