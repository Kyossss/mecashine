import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get(); app.userInterface.activeSelections.clear()
    v = app.activeViewport; cam = v.camera
    cam.target = adsk.core.Point3D.create(55, 15, 25.0)
    cam.eye = adsk.core.Point3D.create(55 - 70, -110, 110)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1); cam.isFitView = False; cam.viewExtents = 70
    v.camera = cam; v.refresh(); print('ok')
