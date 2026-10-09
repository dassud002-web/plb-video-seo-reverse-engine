from pathlib import Path
import re

js = Path('/c/Users/Admin/Desktop/google-project/story_forge/static/js/app.js').read_text(encoding='utf-8', errors='replace')

endpoints = set()
# Find string literals containing /api/
pattern = re.compile(r'["\'](/api/[a-zA-Z0-9/_\-\.]+?)["\']')
for m in pattern.finditer(js):
    g = m.group(1)
    if g and not g.startswith('http'):
        endpoints.add(g)

print('=== ALL /api endpoints referenced in app.js ===')
for e in sorted(endpoints):
    print(' ', e)
print()

# Also check for dropdown/modal references, fetch calls
print('=== fetch/XHR/axios references ===')
for pat in [r'fetch\(\s*["\']([^"\']+)["\']', r'axios\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']', r'XMLHttpRequest']:
    for m in re.finditer(pat, js):
        print(' ', m.group(0)[:80])
