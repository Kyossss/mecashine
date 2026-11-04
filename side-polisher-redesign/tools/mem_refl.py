p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-cad.md'
s = open(p, encoding='utf-8').read()
add = ("- Side ToF reflector (2026-10-22): user measured signal fail with the 45x48 grey plate. New reflector: flat face 145.5 x 120 at local d 7 (shoe clears 4.9), "
       "u 46..191.5 (can't centre on the beam axis u 71.5 because of the arm legs), notch round the rail boss, 0.5 mm L-shaped recess for a white paper insert (136 x 116), "
       "held by the 2 foot end-face M3x12 plus a tab on the leg under the 2 foot-to-arm screws (now M3x20). 82% of the beam on the face, 71% on the insert at full retraction. "
       "Model full retraction is p = -8.5 (arm meets the clamp lip at -9), sensor-to-face 194 mm; the user's ToF reads ~221 there (offset). Clash checks now include p -8.5.\n")
s = s.replace("- Open: demo artifact update.", add + "- Open: demo artifact update.")
open(p, 'w', encoding='utf-8').write(s); print('ok')
