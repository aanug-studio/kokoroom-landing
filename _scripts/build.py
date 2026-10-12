"""Build 15 localized static pages and 3 backwards-compatible entry pages."""
from pathlib import Path
from html import escape
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]
UI = json.loads((ROOT / '_content/ui.json').read_text())
LANGUAGES = ['ko', 'ja', 'zh-CN', 'zh-TW', 'en']
ORIGIN = 'https://kokoroom.app'

def path(locale, page):
    return '/' + locale + '/' + (page + '/' if page else '')

def menu(locale, page):
    current = UI[locale]
    links = ''.join(
        '<li><a data-language="' + language + '" href="' + path(language, page) + '" lang="' + UI[language]['lang'] + '" hreflang="' + UI[language]['lang'] + '"' + (' aria-current="true"' if language == locale else '') + '>' + UI[language]['name'] + '</a></li>'
        for language in LANGUAGES
    )
    chevron = '<svg class="language-chevron" viewBox="0 0 20 20" width="20" height="20" aria-hidden="true" focusable="false"><path d="m5.5 7.75 4.5 4.5 4.5-4.5" /></svg>'
    return '<nav class="language-nav" aria-label="' + current['language'] + '"><details class="language-menu"><summary><span class="language-label">' + current['language'] + '</span><span>' + current['name'] + '</span>' + chevron + '</summary><ul>' + links + '</ul></details></nav>'

def build(locale, page, generic=False):
    ui = UI[locale]
    template = (ROOT / '_templates' / ('legal.html' if page else 'home.html')).read_text()
    template = template.replace('<html lang="en">', '<html lang="' + ui['lang'] + '" data-locale="' + locale + '" data-page="' + page + '" data-generic="' + str(generic).lower() + '">')
    template = re.sub(r'(?<=["\'])\.?\.?/?assets/', '/assets/', template)
    template = template.replace('KokoRoom home', ui['home']).replace('Legal and contact links', ui['legalLinks']).replace('Legal links', ui['legalLinks'])
    if page:
        start = template.index('          <header class="document-header">')
        end = template.index('\n        </article>', start)
        content = (ROOT / '_content' / f'{page}.{locale}.html').read_text().rstrip()
        if page == 'privacy':
            shortcuts = '<nav class="policy-shortcuts" aria-label="' + ui['privacy'] + '"><a href="#analytics-consent">' + ui['analytics'] + '</a><a href="#deletion">' + ui['deletion'] + '</a></nav>'
            content = content.replace('          </header>', shortcuts + '\n          </header>', 1)
        else:
            content = content.replace('          </header>', '<p class="effective-date translation-note">' + ui['translation'] + '</p>\n          </header>', 1)
        template = template[:start] + content + template[end:]
        # The original privacy template's footer current-page marker is reassigned.
        template = template.replace(' aria-current="page"', '')
        template = template.replace('href="/' + page + '/"', 'href="/' + page + '/" aria-current="page"')
        template = template.replace('          </a>\n        </div>', '          </a>\n' + menu(locale, page) + '\n        </div>', 1)
        template = template.replace('Privacy Policy | KokoRoom', escape(ui[page]) + ' | KokoRoom')
        template = template.replace('content="KokoRoom Privacy Policy"', 'content="' + escape(ui[page] + ' | KokoRoom', quote=True) + '"')
        # Footer only: body translations already have their own wording.
        before, footer = template.split('      <footer', 1)
        footer = footer.replace('>Contact<', '>' + ui['contact'] + '<').replace('>Terms of Service<', '>' + ui['terms'] + '<').replace('>Privacy Policy<', '>' + ui['privacy'] + '<')
        template = before + '      <footer' + footer
    else:
        template = template.replace('{{tagline}}', escape(ui['tagline'])).replace('{{description}}', escape(ui['description'], quote=True))
        template = template.replace('KokoRoom landing hero', ui['hero']).replace('KokoRoom app icon', ui['icon']).replace('Download links', ui['downloads'])
        template = template.replace('Download on the App Store', ui['apple']).replace('Get it on Google Play', ui['google'])
        template = template.replace('>Contact us<', '>' + ui['contactUs'] + '<').replace('>Terms of Service<', '>' + ui['terms'] + '<').replace('>Privacy Policy<', '>' + ui['privacy'] + '<')
        template = template.replace('    <main class="page">', '    <main class="page">\n<header class="home-header">' + menu(locale, page) + '</header>')
    for destination in ['privacy', 'terms', '']:
        original = '/' + (destination + '/' if destination else '')
        template = template.replace('href="' + original + '"', 'href="' + path(locale, destination) + '"')
    canonical = path(locale, page)
    metadata = '<link rel="canonical" href="' + ORIGIN + canonical + '" />\n'
    for language in LANGUAGES:
        metadata += '<link rel="alternate" hreflang="' + UI[language]['lang'] + '" href="' + ORIGIN + path(language, page) + '" />\n'
    metadata += '<link rel="alternate" hreflang="x-default" href="' + ORIGIN + '/' + (page + '/' if page else '') + '" />\n'
    metadata += '<link rel="stylesheet" href="/assets/site.css" />\n<script src="/assets/site.js" defer></script>\n'
    template = template.replace('  </head>', metadata + '  </head>')
    # New HTML must not pick up an older cached style after a Pages deployment.
    for asset in re.findall(r'href="(/assets/[^"?]+\.css)"', template):
        version = hashlib.sha256((ROOT / asset[1:]).read_bytes()).hexdigest()[:10]
        template = template.replace('href="' + asset + '"', 'href="' + asset + '?v=' + version + '"')
    target = ROOT / (page if generic else locale + ('/' + page if page else '')) / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template)

if __name__ == '__main__':
    for locale in LANGUAGES:
        for page in ['', 'privacy', 'terms']:
            build(locale, page)
    for page in ['', 'privacy', 'terms']:
        build('en', page, generic=True)
    urls = [ORIGIN + path(locale, page) for locale in LANGUAGES for page in ['', 'privacy', 'terms']]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + url + '</loc></url>' for url in urls) + '</urlset>\n')
    print('Built 18 pages and sitemap.')
