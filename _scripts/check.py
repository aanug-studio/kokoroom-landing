"""Check generated static documents, translation parity and navigation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import re
from build import ROOT, UI, LANGUAGES

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.assets=[]; self.tags=[]; self.languages=[]; self.lang=None
        self.stack=[]
        self.feed(source)
        assert not self.stack,self.stack
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);self.tags.append(tag)
        if tag=='html':self.lang=attrs.get('lang')
        if 'id' in attrs:self.ids.append(attrs['id'])
        if 'data-language' in attrs:self.languages.append(attrs['data-language'])
        if tag=='a':self.links.append(attrs['href'])
        if tag in ['img','script'] and 'src' in attrs:self.assets.append(attrs['src'])
        if tag=='link' and attrs.get('rel') in ['stylesheet','icon']:self.assets.append(attrs['href'])
        if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.stack[-1]==tag:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        assert self.stack and self.stack[-1]==tag,(tag,self.stack[-4:])
        self.stack.pop()

pages=[ROOT/locale/(page+'/' if page else '')/'index.html' for locale in LANGUAGES for page in ['', 'privacy', 'terms']]
pages += [ROOT/(page+'/' if page else '')/'index.html' for page in ['', 'privacy', 'terms']]
parsed={p:Document(p.read_text()) for p in pages}
for p,d in parsed.items():
    assert len(d.ids)==len(set(d.ids)),p
    assert set(d.languages)==set(LANGUAGES),p
    assert d.lang in [x['lang'] for x in UI.values()],p
    for asset in d.assets:
        assert asset.startswith('/assets/'),(p,asset)
        assert (ROOT/urlsplit(asset).path[1:]).is_file(),(p,asset)
    for href in d.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        dest=(ROOT/u.path.lstrip('/')/'index.html') if u.path else p
        assert dest in parsed,(p,href)
        if u.fragment:assert unquote(u.fragment) in parsed[dest].ids,(p,href)
    assert '<<<<<<<' not in p.read_text(),p
for doc in ['privacy','terms']:
    base=(ROOT/'_content'/f'{doc}.en.html').read_text()
    base_ids=re.findall('id="([^"]+)"',base)
    base_links=re.findall('href="([^"]+)"',base)
    units=lambda s:re.findall(r'<(h1|h2|h3|p|li|dt|dd)(?:\s[^>]*)?>',s)
    for locale in LANGUAGES:
        text=(ROOT/'_content'/f'{doc}.{locale}.html').read_text()
        assert re.findall('id="([^"]+)"',text)==base_ids,(doc,locale)
        assert re.findall('href="([^"]+)"',text)==base_links,(doc,locale)
        assert units(text)==units(base),(doc,locale)
        d=parsed[ROOT/locale/doc/'index.html']
        assert d.tags.count('h1')==1
        if doc=='privacy':assert {'analytics-consent','analytics-retention','deletion','legacy-analytics'}<=set(d.ids)
        if doc=='terms':assert all('article-'+str(i) in d.ids for i in range(1,19))
assert '登出或' not in (ROOT/'_content/privacy.zh-TW.html').read_text()
print('PASS: 18 pages, 5 locales, complete legal structures, preserved links, stable anchors and local assets.')
