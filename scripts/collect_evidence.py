"""Read-only public HTTP collector. Stores evidence, never approves offers or trades.

Usage: python3 scripts/collect_evidence.py research/DATE-urls.json research/DATE-http.json
Input is a JSON array of public HTTPS URLs. Output must be a new repository file.
Respect terminal approvals; do not run by another route if execution is blocked.
"""
import concurrent.futures
import datetime
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    products, errors = [], []

    def walk(node):
        if isinstance(node, dict):
            kind = node.get('@type', [])
            if kind == 'Product' or isinstance(kind, list) and 'Product' in kind:
                products.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            walk(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    text = '\n'.join(line.strip() for line in soup.get_text('\n').splitlines() if line.strip())
    return {'title': title, 'products': products, 'parse_errors': errors, 'text': text}


def fetch(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only public HTTPS URLs without embedded credentials are allowed')
    result = subprocess.run(['curl', '--silent', '--show-error', '--location', '--max-time', '35',
                             '--proto', '=https', '--proto-redir', '=https', '--max-filesize', '8000000',
                             '--write-out', '\nHTTP_META:%{http_code} %{url_effective}', url],
                            text=True, capture_output=True, timeout=40)
    body, _, meta = result.stdout.rpartition('\nHTTP_META:')
    return {'url': url, 'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'http': meta, 'exit_code': result.returncode, 'error': result.stderr,
            **parse_html(body)}


def main():
    source, target = map(lambda p: (ROOT / p).resolve(), sys.argv[1:3])
    if not source.is_relative_to(ROOT) or not target.is_relative_to(ROOT):
        raise ValueError('Input and output must be inside repository')
    if target.exists():
        raise FileExistsError('Evidence is append-only; choose a new output filename')
    urls = list(dict.fromkeys(json.loads(source.read_text())))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            try:
                item = future.result()
            except Exception as exc:
                item = {'url': futures[future], 'error': str(exc), 'exit_code': -1}
            results.append(item)
            print(item['url'], item.get('http', ''), item['exit_code'], flush=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
