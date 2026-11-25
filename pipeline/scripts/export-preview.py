"""Compatibility entry: always export the current shared integration, not the old generic UI."""
from pathlib import Path
import subprocess,shutil
root=Path(__file__).resolve().parents[1]
import os,sys
def output_dir(root):
 """Portable delivery folder: --output-dir <dir>, WOW_FOREVER_OUTPUT_DIR, else <project>/artifacts/deliveries."""
 if '--output-dir' in sys.argv:
  i=sys.argv.index('--output-dir')
  if i+1>=len(sys.argv):raise SystemExit('--output-dir requires a path')
  return Path(sys.argv[i+1]).expanduser().resolve()
 env=os.environ.get('WOW_FOREVER_OUTPUT_DIR')
 return Path(env).expanduser().resolve() if env else root/'artifacts'/'deliveries'
subprocess.run(['node',str(root/'scripts/build-static.mjs')],cwd=root,check=True)
source=root/'artifacts/wow-forever-integre.html'
(root/'preview').mkdir(exist_ok=True)
shutil.copyfile(source,root/'preview/index.html')
output=output_dir(root)
output.mkdir(parents=True,exist_ok=True)
shutil.copyfile(source,output/'wow-forever-integre.html')
shutil.copyfile(source,output/'wow-forever-apercu.html')
print('Current integration exported.')
