"""Builds index.html and sw.js for GitHub Pages from the artifact page hitlinie.html.

Pages serves the repository root of master, so the generated files are committed:
run `python3 build.py` after every change to hitlinie.html.
The artifact is written without <html>/<head>/<body> (the artifact host adds them),
so this wraps it in a full document and links the web-app manifest, icons and service worker.
"""
import hashlib, pathlib

root = pathlib.Path(__file__).parent
src = (root / 'hitlinie.html').read_text(encoding='utf-8')
head_part, body_part = src.split('<style>', 1)
body_part = '<style>' + body_part
build = hashlib.sha1((src + (root / 'sw.template.js').read_text(encoding='utf-8') + pathlib.Path(__file__).read_text(encoding='utf-8')).encode()).hexdigest()[:10]

page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_part.strip()}
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>
:root {{ box-sizing: border-box; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
body {{ margin: 0; }}
[hidden] {{ display: none !important; }}
</style>
</head>
<body>
{body_part.strip()}
<script>
// reload once when an updated service worker takes over, so the new version shows without a second launch
if ('serviceWorker' in navigator) {{
  const hadController = !!navigator.serviceWorker.controller;
  let reloaded = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {{
    if (hadController && !reloaded) {{ reloaded = true; location.reload(); }}
  }});
  addEventListener('load', () => navigator.serviceWorker.register('sw.js', {{ updateViaCache: 'none' }}).catch(() => {{}}));
}}
</script>
</body>
</html>
"""

(root / 'index.html').write_text(page, encoding='utf-8')
sw = (root / 'sw.template.js').read_text(encoding='utf-8')
(root / 'sw.js').write_text(sw.replace('__BUILD__', build), encoding='utf-8')
print(f'built index.html and sw.js ({build})')
