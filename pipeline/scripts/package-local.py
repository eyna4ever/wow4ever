"""Package reviewed public site plus source. Excludes secrets and runtime data."""
from pathlib import Path
import zipfile,shutil,json
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
output=output_dir(root)
output.mkdir(parents=True,exist_ok=True)
standalone=root/'artifacts/wow-forever-integre.html'
if not standalone.is_file():raise SystemExit('Run npm run build:static first')
shutil.copyfile(standalone,output/'wow-forever-integre.html')
shutil.copyfile(standalone,output/'wow-forever-apercu.html')
# Update the old preview entry to the new actual integration so future openings use the latest UI.
(root/'preview').mkdir(exist_ok=True)
(root/'preview/index.html').write_bytes(standalone.read_bytes())
skip={'node_modules','.next','.git','runtime','artifacts','dist','preview','__pycache__','.aws','.codex','.agents'}
def addfile(z,path,name):
 info=zipfile.ZipInfo(str(name))
 info.create_system=3
 info.external_attr=0o100644<<16
 info.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(info,path.read_bytes())
archive=output/'wow-forever-integration.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 addfile(z,standalone,'wow-forever-integre.html')
 z.writestr('OUVRIR-LE-SITE.txt','Ouvrir wow-forever-integre.html dans un navigateur.\nLe dossier site/ est destiné à un serveur HTTP statique.\nLe dossier sources/ contient le projet, sa documentation et ses tests.\nIntégration locale : aucune mise en production, aucune fiche de jeu publiée.\n')
 for p in (root/'dist').rglob('*'):
  if p.is_file() and not p.is_symlink():addfile(z,p,Path('site')/p.relative_to(root/'dist'))
 for p in root.rglob('*'):
  rel=p.relative_to(root)
  if not p.is_file() or p.is_symlink() or any(part in skip for part in rel.parts):continue
  if p.name.startswith('.env') and p.name!='.env.example':continue
  if p.suffix.lower() in ['.pem','.key']:continue
  if rel.parts[0]=='design' and p.suffix.lower()=='.png':continue
  if rel.parts[:3]==('public','wiki','assets') and p.suffix.lower()=='.png':continue
  addfile(z,p,Path('sources')/rel)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(z.namelist()),'standalone':str(output/'wow-forever-integre.html')},indent=2))
