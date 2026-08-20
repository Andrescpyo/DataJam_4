"""
Script para recuperar metadatos y recursos desde URLs indicadas.
Guarda respuestas en `data/raw/metadata/`.
Ejecutar localmente en un equipo con conexión a Internet.
"""
import json
import re
from pathlib import Path

import requests

OUT_DIR = Path('data/raw/metadata')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(s):
    return re.sub(r'[^0-9a-zA-Z-_\.]+', '_', s)


def fetch_and_save(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except Exception as e:
        return {'url': url, 'error': str(e)}
    info = {
        'url': url,
        'status_code': r.status_code,
        'headers': dict(r.headers)
    }
    content_type = r.headers.get('Content-Type','')
    fname = sanitize_filename(url)
    if 'application/json' in content_type or r.text.strip().startswith('{') or r.text.strip().startswith('['):
        try:
            data = r.json()
            (OUT_DIR / (fname + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2))
            info['saved'] = str(OUT_DIR / (fname + '.json'))
        except Exception as e:
            (OUT_DIR / (fname + '.txt')).write_text(r.text)
            info['saved'] = str(OUT_DIR / (fname + '.txt'))
            info['parse_error'] = str(e)
    else:
        (OUT_DIR / (fname + '.html')).write_text(r.text)
        info['saved'] = str(OUT_DIR / (fname + '.html'))
    (OUT_DIR / (fname + '.meta.json')).write_text(json.dumps(info, ensure_ascii=False, indent=2))
    return info


def fetch_batch(urls):
    results = []
    for u in urls:
        print('Fetching', u)
        results.append(fetch_and_save(u))
    summary = {'count': len(results), 'results': results}
    (OUT_DIR / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print('Usage: python fetch_metadata.py <url1> <url2> ...')
        urls = []
    if urls:
        s = fetch_batch(urls)
        print('Done. Summary written to', OUT_DIR / 'summary.json')
