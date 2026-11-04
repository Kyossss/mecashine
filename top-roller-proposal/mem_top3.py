p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-cad.md'
s = open(p, encoding='utf-8').read()
i = s.index('- Top polisher proposal (2026-10-24'); j = s.index('\n', i)
new = (r"- Top polisher proposal (2026-10-24, proposal only, not in Fusion), v3 after user feedback: carriage far wall and motor-side mount 15 mm longer (roller axis 186 instead of 201), "
       r"8 mm pin replaced by a 608ZZ pocket in the far wall with an 8 mm axle on the roller's idler end; roller like the side brushes (side core top part as drive end, 109 mm hex bar, 12 tie discs, 52 mm yarn, 18 mm under the top plate); "
       r"top ToF stays IN FRONT of the roller (user's choice), 48 mm before the axis and 20 mm higher on a new bracket using the existing 2 holes: 41-42 mm from the shoe vs 10-12 now; "
       r"parked brush over the tallest shoe 20 mm (large, 139 mm tall); home reading 246 mm. Page https://claude.ai/artifact/Mf7vMJgdsLAfcSebb2GhQ6, files F:\Research\ASPS\top-roller-proposal\. "
       r"Top station bodies in Fusion are root bodies: Body85 core, Body67 carriage (far wall y 71..88, pin y 51..71), Body68 motor holder, Body70 sensor bracket. Read Fusion with read-only scripts through tools\frun.js when the MCP link is down.")
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
