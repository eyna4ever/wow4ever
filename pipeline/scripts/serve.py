"""Loopback-only server for the generated static integration. No writes or external calls."""
import argparse
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
parser=argparse.ArgumentParser()
parser.add_argument('--port',type=int,default=3000)
parser.add_argument('--directory',default=str(Path(__file__).resolve().parents[1]/'dist'))
a=parser.parse_args()
folder=Path(a.directory).resolve()
if not (folder/'index.html').is_file():parser.error('Run npm run build:static first')
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; object-src 'none'; base-uri 'self'")
  super().end_headers()
server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(folder)))
print(f'Local preview: http://127.0.0.1:{a.port}/fr/',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
