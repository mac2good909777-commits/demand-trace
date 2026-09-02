# -*- coding: utf-8 -*-
"""把 tmp/new_events.json 逐筆 POST 到 Apps Script，並 append 到 records.json（含去重）。"""
import sys, io, os, json, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = r"C:\Claude\projects\demand-trace"
BASE = "https://script.google.com/macros/s/AKfycbzmlpV1fpt1RWxVwZj8teUHWw4fs4zpix_3JqCVGX4SeMPIp5Di6_6m_YDRZn4fBQ4/exec"
TOKEN = "muju-trace-2026"

with open(os.path.join(REPO, 'tmp', 'new_events.json'), encoding='utf-8') as f:
    events = json.load(f)
rec_path = os.path.join(REPO, 'docs', 'data', 'records.json')
with open(rec_path, encoding='utf-8') as f:
    records = json.load(f)

seen = {(r.get('company'), r.get('eventDate'), r.get('eventType')) for r in records}
failed = []
added = 0
for e in events:
    key = (e['company'], e['eventDate'], e['eventType'])
    if key in seen:
        print(f"[SKIP 已存在] {key}")
        continue
    payload = dict(e)
    payload['token'] = TOKEN
    payload.pop('recordDate', None)
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(BASE, data=body,
                                 headers={'Content-Type': 'application/json',
                                          'User-Agent': 'Mozilla/5.0'})
    ok = False
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                resp = r.read().decode('utf-8', errors='replace')
            print(f"[POST OK] {e['company']} -> {resp[:160]}")
            ok = True
            break
        except Exception as ex:
            print(f"[POST 重試{attempt+1}] {e['company']}: {ex}")
            time.sleep(4)
    if not ok:
        failed.append(e['company'])
    records.append(e)
    seen.add(key)
    added += 1
    time.sleep(1)

with open(rec_path, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=1)
print(f"\nrecords.json 新增 {added} 筆，總計 {len(records)} 筆")
if failed:
    print("⚠️ POST 失敗（需記入待同步）:", failed)
