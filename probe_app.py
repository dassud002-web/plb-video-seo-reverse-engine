import subprocess
import time
import urllib.request

proc = subprocess.Popen(
    ['/c/Python314/python.exe', '/c/Users/Admin/Desktop/google-project/story_forge/app.py'],
    cwd='/c/Users/Admin/Desktop/google-project',
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(5)

for path in ['/', '/api/recent', '/api/diagnostics']:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:5050{path}', timeout=5) as r:
            body = r.read(300)
            print(path, '->', r.status, repr(body[:120]))
    except Exception as e:
        print(path, '-> ERROR', repr(str(e)[:200]))

time.sleep(1)
proc.terminate()
try:
    out, _ = proc.communicate(timeout=6)
except subprocess.TimeoutExpired:
    proc.kill()
    out, _ = proc.communicate()
print('--- app stdout/stderr tail ---')
print(out[-1200:])
