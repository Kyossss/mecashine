p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-cad.md'
s = open(p, encoding='utf-8').read()
add = (r"- Top polisher proposal (2026-10-24, proposal only, user said not to put it in Fusion): roller rebuilt like the side brushes (side core top part as drive end, 109 mm hex bar, 12 tie discs, "
       r"idler end with a 608ZZ on the carriage's 8 mm pin; 52 mm yarn, carriage top plate is 29 mm above the axis, 3 mm clear). Top ToF moved 44 mm downstream of the roller, same height: "
       r"46-50 mm from the shoe while polishing vs 11-12 now; needs 2 new M3 holes in the carriage top plate; side-to-top sensor spacing 240 -> 328 mm. "
       r"Page https://claude.ai/artifact/Mf7vMJgdsLAfcSebb2GhQ6, files F:\Research\ASPS\top-roller-proposal\. Top station bodies in Fusion are root bodies: Body85 core, Body67 carriage, Body68 motor holder, Body70 sensor bracket. "
       r"Read Fusion with read-only scripts through tools\frun.js when the MCP link is down.")
s = s.replace("\n\n**Why:**", "\n" + add + "\n\n**Why:**", 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
