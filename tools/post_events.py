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


def sheet_keys():
    """回讀試算表事件分頁，回傳 (公司, 事件類型) 集合。

    ⚠️ 端點偶爾會回 HtmlService 的重導頁 HTML 而不是 JSON，但**資料其實已寫入**。
    2026-09-10 就因為把 HTML 當成失敗而重送，在事件分頁造成 2 列重複。
    一律先回讀再決定是否 POST；回讀失敗就回傳 None（代表無法判斷，照舊送）。
    """
    try:
        req = urllib.request.Request(BASE + "?list=records",
                                     headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read().decode('utf-8-sig', errors='replace'))
        rows = j.get('records') or j.get('rows') or []
        # 欄序：建檔時間, 公司, 代號, 事件日, 事件類型, 摘要, ...
        # 用摘要前 40 字當指紋：事件日回讀時帶時區位移不可靠，摘要則是逐則唯一。
        return {(str(x[1]), str(x[4]), str(x[5])[:40]) for x in rows if len(x) > 5}
    except Exception as ex:
        print("[回讀 list=records 失敗，改為直接 POST]", ex)
        return None


posted = sheet_keys()
failed = []
added = 0
for e in events:
    key = (e['company'], e['eventDate'], e['eventType'])
    if key in seen:
        print(f"[SKIP 已存在] {key}")
        continue
    if posted is not None and (e['company'], e['eventType'], str(e.get('summary'))[:40]) in posted:
        print(f"[SKIP 試算表已有] {e['company']} / {e['eventType']}")
        records.append(e)
        seen.add(key)
        added += 1
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
