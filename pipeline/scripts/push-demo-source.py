"""Standard Git transport fallback when the installed Sites helper is unavailable.
Credential JSON is accepted only on hidden stdin, never in a file or arguments.
This script does not publish, change access, or handle DNS.
"""
import sys,json,os,subprocess,termios
from pathlib import Path
from urllib.parse import urlsplit

root=Path(__file__).resolve().parents[1]
settings=None
if sys.stdin.isatty():
 settings=termios.tcgetattr(sys.stdin.fileno())
 hidden=settings.copy();hidden[3]&=~termios.ECHO
 termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,hidden)
print('Ready for credential JSON on stdin (input is hidden).',flush=True)
try:
 value=json.loads(sys.stdin.readline())
finally:
 if settings is not None:termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,settings)
credential=value.get('credential',value)
token=credential.get('token')
remote=credential.get('remote_url','')
branch=credential.get('branch','')
parsed=urlsplit(remote)
if not isinstance(token,str) or not token or any(c in token for c in '\r\n'):
 raise SystemExit('Missing or invalid credential')
if parsed.scheme!='https' or parsed.username or parsed.password or not parsed.hostname:
 raise SystemExit('A credential-free HTTPS repository URL is required')
if credential.get('auth_mode')!='http_extra_header':raise SystemExit('Unsupported Git authentication mode')
if not branch or branch.startswith('-') or any(c.isspace() for c in branch):raise SystemExit('Invalid source branch')
manifest=json.loads((root/'.openai/hosting.json').read_text())
if manifest['project_id'] not in parsed.path:raise SystemExit('Repository does not match the local Site identity')
if manifest.get('static')!={'directory':'dist'}:raise SystemExit('Unexpected hosting configuration')
env=os.environ.copy()
slot=int(env.get('GIT_CONFIG_COUNT','0'))
env.update({'GIT_CONFIG_COUNT':str(slot+1),f'GIT_CONFIG_KEY_{slot}':'http.extraHeader',f'GIT_CONFIG_VALUE_{slot}':'Authorization: Bearer '+token,'GIT_TERMINAL_PROMPT':'0','GIT_TRACE':'0','GIT_CURL_VERBOSE':'0'})
def git(*args,timeout=45):
 try:result=subprocess.run(['git',*args],cwd=root,env=env,capture_output=True,text=True,timeout=timeout)
 except subprocess.TimeoutExpired:raise RuntimeError('Git operation timed out; retry after checking remote state')
 if result.returncode:
  # Never echo untrusted transport output or an authorization header.
  message=result.stderr.replace(token,'[redacted]')
  safe='\n'.join(line for line in message.splitlines() if not any(x in line.lower() for x in ['authorization:','bearer ','extraheader']))
  raise RuntimeError('Git operation failed: '+safe[:1600])
 return result.stdout.strip()
try:
 if git('status','--porcelain'):raise RuntimeError('Commit validated local changes before source synchronization')
 head=git('rev-parse','HEAD')
 existing=git('remote')
 if 'sites' in existing.splitlines():
  if git('remote','get-url','sites')!=remote:raise RuntimeError('Existing Sites remote differs; refusing to replace it')
 else:git('remote','add','sites',remote)
 current=git('ls-remote','--heads','sites',f'refs/heads/{branch}')
 if current:
  remote_sha=current.split()[0]
  if remote_sha!=head:
   git('fetch','--no-tags','sites',f'refs/heads/{branch}:refs/remotes/sites/{branch}')
   if subprocess.run(['git','merge-base','--is-ancestor',remote_sha,head],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
    raise RuntimeError('The source branch has different history; preserve and inspect it before merging')
 git('push','sites',f'{head}:refs/heads/{branch}',timeout=60)
 verified=git('ls-remote','--heads','sites',f'refs/heads/{branch}').split()[0]
 if verified!=head:raise RuntimeError('Remote source state does not match the validated local revision')
 print(json.dumps({'project_id':manifest['project_id'],'commit_sha':head,'branch':branch,'pushed':True}),flush=True)
except Exception as error:
 print(str(error).replace(token,'[redacted]'),file=sys.stderr)
 raise SystemExit(1)
