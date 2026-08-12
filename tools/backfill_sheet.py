"""把 records.json 裡尚未進 Google 試算表的事件列補寫回去。

背景：需求軌跡原本跑在 Claude 雲端 routine，沙箱的 egress proxy 擋掉
script.google.com，POST 寫入連續多日失敗，事件只進了 repo 的 records.json，
試算表「事件紀錄」分頁停在 2026-08-09。2026-08-13 排程搬回本機 DT（無網路限制）後
用本腳本補齊。

判重鍵＝(公司, 事件日期, 事件類型)，與每日排程的判重規則一致。
預設為乾跑（只列出要補什麼），加 --write 才真的寫入。
"""
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

BASE = ("https://script.google.com/macros/s/"
        "AKfycbzmlpV1fpt1RWxVwZj8teUHWw4fs4zpix_3JqCVGX4SeMPIp5Di6_6m_YDRZn4fBQ4/exec")
TOKEN = "muju-trace-2026"
REPO = Path(__file__).resolve().parent.parent
WRITE = '--write' in sys.argv

FIELDS = ['company', 'ticker', 'eventDate', 'eventType', 'summary',
          'reading', 'label', 'entry', 'priority', 'related', 'sources']


def norm_date(v):
    """把事件日期正規化成 'YYYY-MM-DD'（無日者回 'YYYY-MM'）以便兩邊比對。

    兩端格式不一致，直接字串比會全部誤判成「缺少」：
      · 試算表：ISO 時間戳且為 UTC，民國年會補成四位 —— '0114-05-18T15:54:00.000Z'
        實際代表 114/05/19。注意民國年被當成西元 114 年序列化，Google 對這種
        古早年份套用的是台北 LMT（+8:06）而非 +8:00，所以不能寫死加 8 小時。
        儲存格都是「日期型」（當地 00:00），故改用加 12 小時取最近一天，
        對 +8:00 與 +8:06 兩種偏移都正確。
      · records.json：民國 '114/05/19' 與西元 '2026/05/26' 混用，另有 '2026/01' 這種只到月的
    年份 ≤ 200 一律視為民國年，+1911 轉西元。
    """
    s = str(v).strip()
    if not s:
        return ''
    if 'T' in s:                                   # 試算表的 ISO 時間戳（UTC）
        try:
            dt = datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=12)
        except ValueError:
            return s
        y, m, d = dt.year, dt.month, dt.day
    else:                                          # records.json 的 114/05/19 或 2026/05/26
        parts = [p for p in s.replace('-', '/').split('/') if p]
        if len(parts) < 2:
            return s
        try:
            y, m = int(parts[0]), int(parts[1])
            d = int(parts[2]) if len(parts) > 2 else 0
        except ValueError:
            return s
    if y <= 200:                                   # 民國年
        y += 1911
    return f"{y:04d}-{m:02d}-{d:02d}" if d else f"{y:04d}-{m:02d}"


def key(r):
    """判重鍵＝(公司, 正規化事件日期, 事件類型)，與每日排程的判重規則一致。
    本地 records.json 是物件，試算表回傳的是列陣列
    （欄序：紀錄日期|公司名稱|股票代號|事件日期|事件類型|…），兩種都要吃。"""
    if isinstance(r, dict):
        company, date, etype = (r.get('company', ''), r.get('eventDate', ''),
                                r.get('eventType', ''))
    else:
        company = r[1] if len(r) > 1 else ''
        date = r[3] if len(r) > 3 else ''
        etype = r[4] if len(r) > 4 else ''
    return (str(company).strip(), norm_date(date), str(etype).strip())


local = json.loads((REPO / 'docs/data/records.json').read_text(encoding='utf-8'))
print(f"records.json：{len(local)} 筆")

r = requests.get(f"{BASE}?list=records", timeout=60)
r.raise_for_status()
remote = r.json()
if isinstance(remote, dict):
    remote = remote.get('records') or remote.get('data') or []
print(f"試算表現有：{len(remote)} 筆")

have = {key(x) for x in remote}
missing = [x for x in local if key(x) not in have]
print(f"\n待補：{len(missing)} 筆\n")
for x in missing:
    print(f"  · {x.get('recordDate','')} | {x.get('company')} {x.get('ticker','')} "
          f"| {x.get('eventDate')} | {x.get('eventType')}")

if not missing:
    print("\n沒有要補的，結束。")
    sys.exit(0)

if not WRITE:
    print("\n（乾跑模式。確認無誤後加 --write 實際寫入）")
    sys.exit(0)

print("\n開始寫入…")
ok = fail = 0
for x in missing:
    body = {'token': TOKEN}
    for f in FIELDS:
        body[f] = x.get(f, '')
    try:
        resp = requests.post(BASE, json=body, timeout=60,
                             allow_redirects=True)
        text = resp.text[:120].replace('\n', ' ')
        if resp.status_code == 200:
            ok += 1
            print(f"  ✅ {x.get('company')} {x.get('eventDate')} → {text}")
        else:
            fail += 1
            print(f"  ❌ {x.get('company')} HTTP {resp.status_code} → {text}")
    except Exception as e:
        fail += 1
        print(f"  ❌ {x.get('company')} 例外：{e}")
    time.sleep(1.5)      # Apps Script 有配額，放慢一點

print(f"\n完成：成功 {ok} 筆、失敗 {fail} 筆")
