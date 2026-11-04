import adsk.core
# Perspective side view across the belt at the top station (world cm).
def run(_c):
    app = adsk.core.Application.get(); v = app.activeViewport
    cam = v.camera
    cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    cam.isSmoothTransition = False
    cam.target = adsk.core.Point3D.create(68.0, 3.0, 24.0)
    cam.eye = adsk.core.Point3D.create(20.0, -75.0, 85.0)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
    cam.isFitView = False
    cam.perspectiveAngle = 0.3
    v.camera = cam; v.refresh()
    c2 = v.camera; print('eye', [round(x, 1) for x in c2.eye.asArray()], 'target', [round(x, 1) for x in c2.target.asArray()], 'type', c2.cameraType)
