# -*- coding: utf-8 -*-
"""依公司代號抓 mops_scan 結果中的重訊全文。
用法：python tools/mops_fetch.py <掃描json> <代號1> <代號2> ...
"""
import sys, io, json, re, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = sys.argv[1]
want = set(sys.argv[2:])
with open(path, encoding='utf-8') as f:
    d = json.load(f)


def strip_html(h):
    h = re.sub(r'(?is)<(script|style).*?</\1>', '', h)
    h = re.sub(r'(?i)<br\s*/?>', '\n', h)
    h = re.sub(r'(?i)</(tr|div|p|table)>', '\n', h)
    h = re.sub(r'(?i)</td>', ' | ', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n\s*\n+', '\n', h)
    return h.strip()


seen = set()
for r in d['rows']:
    cid = str(r.get('COMPANY_ID', '')).strip()
    if cid not in want:
        continue
    link = r.get('HYPERLINK') or ''
    m = re.search(r"href=['\"]([^'\"]+)['\"]", link) or re.search(r"(https?://\S+)", link)
    url = m.group(1) if m else link
    url = url.replace('&amp;', '&')
    if url in seen:
        continue
    seen.add(url)
    print("=" * 70)
    print(f"{cid} {r.get('COMPANY_NAME')} | {r.get('CDATE')} {r.get('CTIME')}")
    print("主旨:", r.get('SUBJECT', '').replace('\n', ' '))
    print("URL:", url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        print("-" * 60)
        print(strip_html(html)[:6000])
    except Exception as e:
        print("[抓取失敗]", e)
    time.sleep(1)
