import urllib.request
import json

for path in ['/', '/api/recent', '/api/diagnostics']:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:5050{path}', timeout=6) as r:
            body = r.read()
            print(path, '->', r.status, 'bytes=', len(body), repr(body[:150]))
    except Exception as e:
        print(path, '-> ERROR', repr(str(e)[:200]))
