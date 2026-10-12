# KokoRoom website

The existing GitHub Pages site publishes `main` at https://kokoroom.app.
The home page, privacy policy and terms are available in Korean (`ko`),
Japanese (`ja`), Simplified Chinese (`zh-CN`), Traditional Chinese (`zh-TW`)
and English (`en`).

## Updating content

- `_content/`: complete translated privacy/terms bodies and shared UI copy.
- `_templates/`: the original landing and legal page layouts.
- `assets/site.js`: language routing and a local language preference only.
- `assets/site.css`: shared navigation and responsive adjustments.
- Generated HTML and `sitemap.xml` are checked in for static hosting.

After changing a source, regenerate and validate with Python 3 and Node.js:

```sh
python3 _scripts/build.py
python3 _scripts/check.py
node --test _scripts/language.test.cjs
python3 -m http.server 8765 --bind 127.0.0.1
```

Check the preview in a browser before committing. Pushing `main` updates the
live website through the repository's existing GitHub Pages configuration.
`CNAME` and existing asset URLs must remain available.

## Language behavior

The original `/`, `/privacy/` and `/terms/` routes remain valid. They select
`?lang=` first, a manually saved preference next, then a supported browser
language, with English as fallback. Localized URLs remain in their explicit
language. Switching languages keeps the current document and section anchor.
Without JavaScript, all localized pages and language links still work, and
the original routes display a complete English document.

The only new browser storage is `kokoroom.language`, saved when a visitor
selects a language. No website analytics or third-party script is added.
Source directories are excluded from the published site by `_config.yml`.

## Privacy notice scope

The October 12, 2026 update documents the optional analytics behavior only for
app versions that offer “Help improve the app.” Older app behavior is identified
separately. Stable anchors include `#analytics-consent`, `#analytics-retention`
and the existing `#deletion`. Keep these aligned across all five translations.

Publishing this website does not deploy an app or change Firebase/GA settings.
The retention notice preserves the October 6 published settings: two months for
event data, fourteen months for user data, renewed on new activity. Do not claim
that a proposed reduction has been applied without verifying the live setting.
Existing service terms, account deletion and store subscription instructions
are preserved; the new language versions do not expand collection permissions.
