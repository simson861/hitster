"""Builds index.html, sw.js and version.json for GitHub Pages from the artifact page hitlinie.html.

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
<div class="update-bar" id="update-bar" role="status" hidden>
  <span>Neue Version verfügbar. Dein Spielstand bleibt erhalten.</span>
  <button class="btn primary small" id="update-reload">Neu laden</button>
</div>
{body_part.strip()}
<style>
/* the bar sits above the app in the page flow and pushes it down instead of covering the header */
body {{ display: flex; flex-direction: column; }}
#app {{ flex: 1; min-height: 0; width: 100%; height: auto; }}
.update-bar {{
  display: flex; align-items: center; gap: 12px; flex: none;
  padding-block: 10px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  background: var(--ink-3); border-bottom: 2px solid var(--spot); font-size: 15px; font-weight: 600;
  animation: up .25s ease;
}}
.update-bar span {{ flex: 1; min-width: 0; }}
.update-bar .btn {{ flex: none; }}
</style>
<script>
// Pages build id; version.json on the server holds the id of the latest deploy.
const BUILD = '{build}';
const updateBar = document.getElementById('update-bar');
async function checkForUpdate() {{
  try {{
    const res = await fetch('version.json', {{ cache: 'no-store' }});
    if (!res.ok) return;
    const {{ build }} = await res.json();
    if (build && build !== BUILD) updateBar.hidden = false;
  }} catch (e) {{}} // offline: nothing to compare against
}}
document.getElementById('update-reload').addEventListener('click', async () => {{
  try {{ await (await navigator.serviceWorker?.getRegistration())?.update(); }} catch (e) {{}}
  location.reload();
}});
addEventListener('load', () => {{
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js', {{ updateViaCache: 'none' }}).catch(() => {{}});
  checkForUpdate();
}});
// the home-screen app often stays open for days, so check again whenever it comes back to the front
document.addEventListener('visibilitychange', () => {{ if (!document.hidden) checkForUpdate(); }});
setInterval(checkForUpdate, 15 * 60 * 1000);
</script>
</body>
</html>
"""

(root / 'index.html').write_text(page, encoding='utf-8')
sw = (root / 'sw.template.js').read_text(encoding='utf-8')
(root / 'sw.js').write_text(sw.replace('__BUILD__', build), encoding='utf-8')
(root / 'version.json').write_text(f'{{"build": "{build}"}}\n', encoding='utf-8')
print(f'built index.html, sw.js and version.json ({build})')
