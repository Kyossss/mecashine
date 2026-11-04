import adsk.core, adsk.fusion
# Read-only: the bodies in 'Spray station (Claude)' now, and the component's features, to see what the user changed on a post.
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); root = d.rootComponent
    occs = [o for o in root.allOccurrences if 'Spray' in o.component.name]
    for o in occs:
        c = o.component; print('OCC', o.fullPathName, 'bodies', c.bRepBodies.count, 'sketches', c.sketches.count)
        for b in c.bRepBodies: print('  ', b.name, '| vis' if b.isLightBulbOn else '| hidden', round(b.volume, 3), 'cm3 faces', b.faces.count, bb(b.boundingBox))
        f = c.features
        for coll in ('extrudeFeatures', 'filletFeatures', 'chamferFeatures', 'combineFeatures', 'holeFeatures', 'moveFeatures', 'mirrorFeatures', 'baseFeatures', 'splitBodyFeatures', 'pressPullFeatures' if hasattr(f, 'pressPullFeatures') else 'extrudeFeatures', 'shellFeatures'):
            try:
                col = getattr(f, coll)
                if col.count: print('  ', coll, col.count, [x.name for x in col][:12])
            except Exception as e: pass
        for sk in c.sketches: print('   sketch', sk.name, 'plane', sk.referencePlane.objectType if sk.referencePlane else None, 'profiles', sk.profiles.count, 'curves', sk.sketchCurves.count)
    # timeline items after the spray station was made
    tl = d.timeline; names = []
    for i in range(max(0, tl.count - 25), tl.count):
        it = tl.item(i)
        try: names.append('%d %s %s' % (i, it.name, it.entity.objectType.split('::')[-1] if it.entity else ''))
        except Exception: names.append('%d %s' % (i, it.name))
    print('timeline tail:\n  ' + '\n  '.join(names))
