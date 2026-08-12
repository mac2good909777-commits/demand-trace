"""檢查 BASE?list=records 實際回傳的結構與內容，確認判重鍵怎麼對。一次性。"""
import json
import requests

BASE = ("https://script.google.com/macros/s/"
        "AKfycbzmlpV1fpt1RWxVwZj8teUHWw4fs4zpix_3JqCVGX4SeMPIp5Di6_6m_YDRZn4fBQ4/exec")

r = requests.get(f"{BASE}?list=records", timeout=60)
data = r.json()
print(f"型別: {type(data).__name__}")
if isinstance(data, dict):
    print(f"keys: {list(data.keys())}")
    data = data.get('data') or data.get('records') or []
print(f"筆數: {len(data)}\n")
for i, row in enumerate(data):
    if isinstance(row, list):
        print(f"[{i}] ({len(row)} 欄) {row[:6]}")
    else:
        print(f"[{i}] {json.dumps(row, ensure_ascii=False)[:200]}")
