"""Check the generated static site's internal routes, assets and document landmarks."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'public'

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.errors = path, set(), [], []
        self.h1 = self.main = 0
        self.text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id') in self.ids:
            self.errors.append('duplicate ID: ' + a['id'])
        if a.get('id'):
            self.ids.add(a['id'])
        self.h1 += tag == 'h1'
        self.main += tag == 'main'
        if tag == 'img' and 'alt' not in a:
            self.errors.append('image missing alt attribute')
        for key in ('src', 'href', 'poster'):
            if a.get(key): self.links.append(a[key])
        if tag == 'a' and a.get('href') in ('', '#'):
            self.errors.append('placeholder link')

    def handle_data(self, data):
        self.text.append(data)

docs = {}
for path in sorted(DIST.glob('*.html')):
    doc = Document(path)
    doc.feed(path.read_text())
    docs[path] = doc

errors = []
for path, doc in docs.items():
    errors += [path.name + ': ' + e for e in doc.errors]
    if doc.h1 != 1 or doc.main != 1:
        errors.append(path.name + ': requires one h1 and one main')
    for href in doc.links:
        url = urlsplit(href)
        if url.scheme or url.netloc: continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir(): target /= 'index.html'
        if not target.exists(): errors.append(path.name + ': missing ' + href)
        if url.fragment and target in docs and url.fragment not in docs[target].ids:
            errors.append(path.name + ': missing anchor ' + href)

home=(DIST/'index.html').read_text()
home_text=''.join(docs[DIST/'index.html'].text)
for removed in ['id="information"','id="guide"','id="moments"','↗']:
    if removed in home: errors.append('Removed content still present: '+removed)
for required in ['p.b.qの想い','活動紹介','参加案内','グッズ販売','サードプレイス','どちらも大歓迎です']:
    if required not in home_text: errors.append('Missing requested content: '+required)

css = DIST / 'assets/site.css'
for href in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
    if not (css.parent / href).is_file(): errors.append('CSS missing asset: ' + href)

for name in ('hero-v2-desktop', 'hero-v2-mobile'):
    if not (DIST / 'assets' / (name + '.mp4')).is_file(): errors.append('Missing video: ' + name)

def luminance(hex_value):
    rgb = [int(hex_value[i:i+2], 16)/255 for i in (1, 3, 5)]
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(a*b for a, b in zip(rgb, (.2126, .7152, .0722)))
def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return round((hi+.05)/(lo+.05), 2)

report = {'pages': len(docs), 'checked_links_and_assets': sum(len(d.links) for d in docs.values()),
          'contrast': {'red_on_white': contrast('#c01734','#ffffff'),
                       'ink_on_cream': contrast('#414141','#f0eee8'),
                       'muted_on_cream': contrast('#726b69','#f0eee8')},
          'errors': errors}
(ROOT / 'qa/static-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(bool(errors))
