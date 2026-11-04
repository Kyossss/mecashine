# Spray page v7 text: universal IR mount, the printed parts and the screws.
p = 'F:/Research/ASPS/spray-proposal/spray.html'; s = open(p, encoding='utf-8').read()
def rep(x, y):
    global s
    assert s.count(x) == 1, (s.count(x), x[:70]); s = s.replace(x, y)
a = s.index('    <h2>IR sensor provision and bursts</h2>'); b = s.index('    <h2>How much polish</h2>')
s = s[:a] + '''    <h2>Universal IR mount</h2>
    <ul>
      <li><b>A small shelf on the far post,</b> 26 mm before the nozzles, looking across the belt. It's drawn with your FC-51 / MH-B module on it; switch it off with "Show FC-51".</li>
      <li><b>Height:</b> the shelf bolts into a 45 mm vertical slot in the post, so the sensor can sit anywhere from about 25 to 70 mm above the belt. It's drawn at 40 mm. The heel plate is under 35 mm, so the sensor won't see it.</li>
      <li><b>Reach:</b> the module's M3 hole sits in a 12 mm slot along the shelf. That moves the LEDs from 6 to 18 mm outside the heel plate's edge. This type of sensor only sees black leather up close, so keep it near the shoe.</li>
      <li><b>Other sensors:</b> two zip-tie slots across the shelf hold any board that doesn't fit the M3 hole.</li>
      <li><b>Bursts</b> only on the polishing pass: the first as soon as the sensor sees the shoe, then one 0.4 s burst every few seconds while it still does.</li>
    </ul>

    <h2>Printed parts and screws</h2>
    <table>
      <thead><tr><th>Part</th><th>Qty</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Nozzle post (mirrored pair)</td><td class="v">1 + 1</td><td>32.5 cm³ solid, about 15 g each at normal infill. Prints lying on its side.</td></tr>
        <tr><td>IR shelf</td><td class="v">1</td><td>7 cm³. Prints flat.</td></tr>
        <tr><td>M3 × 20 + nut</td><td class="v">2</td><td>Elbow lug to post, nut in the post's pocket</td></tr>
        <tr><td>M3 × 12 + nut</td><td class="v">2</td><td>IR shelf to post (1), sensor to shelf (1)</td></tr>
        <tr><td>M3 to the board</td><td class="v">4</td><td>Two per foot. Length depends on the board's thickness.</td></tr>
      </tbody>
    </table>
    <p class="small">The foot has two 30 mm slots running across the belt direction, so it can meet holes 39 to 69 mm outside the belt edge. Its two slots are 23 mm apart along the belt.</p>

''' + s[b:]
rep('''      <li><b>Board holes:</b> which existing holes are near x 680 (about 480 mm from the entry edge), their spacing, and how far they are from the belt edge. The view assumes two holes 20 mm apart, 56 mm outside the belt edge.</li>''',
    '''      <li><b>Board holes:</b> which existing holes are near x 680 (about 480 mm from the entry edge), their spacing along the belt, how far they are from the belt edge, and the board's thickness.</li>''')
rep('The posts, elbows, IR provision and spray are drawn by this page. The hose is left out.', 'The posts and IR shelf are CAD parts made for this proposal; the elbows, nozzles, screws, FC-51 and spray are drawn by this page. The hose is left out.')
open(p, 'w', encoding='utf-8').write(s); print('ok')
