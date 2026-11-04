import adsk.core, adsk.fusion, json, base64, array
# Read-only: display meshes of everything visible in front of and around the side station (x 640..990), for the spray proposal page.
# Frame: x - 780 (the proposed spray arch), z above the belt (Fusion z - 217), 0.1 mm units. The shoe and the base board are drawn by the page.
OUT = 'F:/Research/ASPS/spray-proposal/station-mesh.json'
X0, X1 = 640, 990
def enc(b):
    calc = b.meshManager.createMeshCalculator(); calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.LowQualityTriangleMesh); m = calc.calculate()
    c = m.nodeCoordinatesAsFloat; pts = array.array('h')
    for i in m.nodeIndices: pts.extend((int(round(c[3 * i] * 100)) - 7800, int(round(c[3 * i + 1] * 100)), int(round(c[3 * i + 2] * 100)) - 2170))
    return base64.b64encode(pts.tobytes()).decode()
def kind(top, name):
    n = (top + '/' + name).lower()
    for k, v in (('reflector', 'reflector'), ('yarn tie', 'disc'), ('brush core', 'core'), ('608zz', 'bearing'), ('guide rail', 'rail'), ('guide block', 'block'), ('flange clamp', 'block'),
                 ('tof sensor', 'sensor'), ('sensor bracket', 'sensbr'), ('arm frame', 'arm'), ('rack', 'rack'), ('gear', 'pinion'), ('servo', 'servo'), ('carriage', 'car'),
                 ('motor holder', 'motor'), ('drive', 'core'), ('bar', 'core'), ('idler', 'core'), ('tie disc', 'disc'), ('tof bracket', 'sensbr'), ('tof board', 'sensor'),
                 ('foot bracket', 'foot'), ('conveyor real length', 'belt'), ('conveyor belt system', 'conveyor')):
        if k in n: return v
    return 'frame'
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    out = {}
    def take(b, top):
        if not b.isLightBulbOn or b.faces.count == 0: return
        B = b.boundingBox
        if B.maxPoint.x * 10 < X0 or B.minPoint.x * 10 > X1 or B.maxPoint.z * 10 < 130 or abs(B.minPoint.y * 10) > 320: return
        if b.name in ('Body160', 'Body58'): return
        out[top + '/' + b.name] = {'kind': kind(top, b.name), 'm': enc(b)}
    def walk(o, top):
        if not o.isLightBulbOn or o.component.name.startswith('FMB_Shoes'): return
        for b in o.bRepBodies: take(b, top)
        for c in o.childOccurrences: walk(c, top + '/' + c.component.name if top.endswith('(Claude)') else top)
    for b in root.bRepBodies: take(b, 'root')
    for o in root.occurrences: walk(o, o.component.name)
    import os; os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'))
    ks = {}
    for v in out.values(): ks[v['kind']] = ks.get(v['kind'], 0) + 1
    print(len(out), 'bodies', ks, os.path.getsize(OUT), 'bytes')
