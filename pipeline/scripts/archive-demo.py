"""Archive only the checked static output and the Sites identity, never source or runtime."""
from pathlib import Path
import tarfile,json,hashlib,subprocess
root=Path(__file__).resolve().parents[1]
manifest=root/'.openai/hosting.json'
if not manifest.is_file() or not (root/'dist/index.html').is_file():raise SystemExit('Site identity and static build required')
settings=json.loads(manifest.read_text())
latest=json.loads((root/'artifacts/demo-latest.json').read_text())
release=Path(latest['directory']).resolve()
if not release.is_relative_to((root/'artifacts/demo-releases').resolve()):raise SystemExit('Unexpected release location')
subprocess.run(['node',str(root/'scripts/prepare-demo.mjs'),'--verify',str(release)],cwd=root,check=True,stdout=subprocess.DEVNULL)
site=release/'site'
if settings.get('static')!={'directory':'dist'}:raise SystemExit('Expected static dist hosting')
archive=root/'artifacts/wow-forever-sites.tar.gz'
archive.parent.mkdir(exist_ok=True)
def safe_mode(info):
 if info.issym() or info.islnk():raise ValueError('Symlinks are not allowed in deployment archives')
 info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o755 if info.isdir() else 0o644
 return info
with tarfile.open(archive,'w:gz') as tar:
 tar.add(manifest,arcname='.openai/hosting.json',filter=safe_mode)
 tar.add(site,arcname='dist',filter=safe_mode)
print(json.dumps({'archive':str(archive),'project_id':settings['project_id'],'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
