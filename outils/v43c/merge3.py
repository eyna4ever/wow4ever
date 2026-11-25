"""Fusion à trois voies au niveau des balises HTML (git merge-file sur une ligne par balise).
base = page générée avant l'ajout (dist v43c-before), theirs = page générée après l'ajout (dist v43c), ours = page v43b en ligne.
Renvoie (texte, nb_conflits)."""
import re, subprocess, tempfile, os
def _enc(s): return ''.join(t.replace('\\', '\\\\').replace('\n', '\\n') + '\n' for t in re.split(r'(?=<)', s))
def _dec(s):
    out = []
    for line in s.split('\n')[:-1]:
        out.append(re.sub(r'\\(\\|n)', lambda m: '\\' if m.group(1) == '\\' else '\n', line))
    return ''.join(out)
def merge3(ours, base, theirs):
    with tempfile.TemporaryDirectory() as d:
        p = {k: os.path.join(d, k) for k in ('o', 'b', 't')}
        for k, v in (('o', ours), ('b', base), ('t', theirs)): open(p[k], 'w', encoding='utf-8').write(_enc(v))
        r = subprocess.run(['git', 'merge-file', '-p', '--no-diff3', p['o'], p['b'], p['t']], capture_output=True, text=True, encoding='utf-8')
        if r.returncode < 0 or r.returncode > 127: raise RuntimeError(r.stderr)
        if r.returncode: return None, r.returncode
        return _dec(r.stdout), 0
