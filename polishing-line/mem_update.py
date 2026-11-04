p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-electronics.md'
s = open(p, encoding='utf-8').read()
old = s[s.index('- Artifact: Polishing Line page'):s.index('\n', s.index('- Artifact: Polishing Line page'))]
new = (r"- Artifact: Polishing Line page https://claude.ai/artifact/Ve2pz8CmpsZD1u3NoRPdes (tabs: Logic and model, Wiring and assembly, Control board). "
       r"Current source (since 2026-10-23): F:\Research\ASPS\polishing-line\polishing-line.html (publish polishing-line.publish.html = same without the wrapper; "
       r"update_side.js rebuilt the side station from the CAD; test_render.js renders frames to PNG in Node). "
       r"The old copies and generators (gen.js, board.js, wrap.js) were in the main convo's Temp scratchpad, which Windows temp cleanup is deleting; "
       r"if they're gone, rebuild from the live page with Artifact read.")
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-cad.md'
s = open(p, encoding='utf-8').read()
s = s.replace("- Open: demo artifact update.",
              r"- Polishing Line page (2026-10-23): side station in the simulation rebuilt from the CAD (yarn brushes, arms, rails, guide blocks, 145x120 reflector, open = full retraction, reading 2a+10.9 = 194 mm); source F:\Research\ASPS\polishing-line\, see [[mecashine-electronics]].")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
