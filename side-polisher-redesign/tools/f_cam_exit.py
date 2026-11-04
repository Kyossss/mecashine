import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get(); app.userInterface.activeSelections.clear()
    v = app.activeViewport; cam = v.camera
    cam.target = adsk.core.Point3D.create(132, -5, 19.0)
    cam.eye = adsk.core.Point3D.create(132 + 25, -60, 45)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1); cam.isFitView = False; cam.viewExtents = 22
    v.camera = cam; v.refresh(); print('ok')
