p = r'C:/Users/kyo/.claude/projects/f--Research/memory/mecashine-cad.md'
s = open(p, encoding='utf-8').read()
add = (r"- Top polisher implemented in Fusion (2026-10-24): component 'Top polisher redesign (Claude)' (20 bodies): copy of Body67 split at z443, lower part moved -15 and refilled, pin cut out + 608ZZ pocket; "
       r"Body68 copy moved -15; roller parts, 12 tie discs, 608ZZ, new ToF bracket (tab under the top plate into the 2 blind holes, extruded along y so it prints on its side) and board stand-in. "
       r"Originals Body67/68/85/70 hidden, not deleted. Files in F:\Research\ASPS\top polish\ (top_polish.py, print\ STLs, fusion\ STEPs, tools for the Fusion stages in side-polisher-redesign\tools\f_top_stage1/2.py). "
       r"User asked for exports of a new subsystem to go in their own folder (here 'top polish').")
s = s.replace("\n\n**Why:**", "\n" + add + "\n\n**Why:**", 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
