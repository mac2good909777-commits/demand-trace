# -*- coding: utf-8 -*-
"""每日排程 push 前的資料型別檢查。

存在原因（2026-09-07 事故）：
    2026-09-03 的 commit 8e8c462 新增「台塑新智能科技」與「銳澤實業」兩檔時，
    把 locs 與 plan 寫成**字串**而非陣列。docs/index.html 的 locBadges() 執行
    (w.locs || []).map(...)，對字串呼叫 .map 會拋 TypeError，
    整個公司清單的 render 迴圈中斷 → 儀表板只剩頁首與頁尾。
    JSON 本身合法、node --check 也過，所以三輪排程都沒發現，**壞了 4 天**。

用法：
    python3 tools/validate_data.py          # 有錯回傳非 0，並列出公司與欄位
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'docs', 'data')
COMPANIES = os.path.join(REPO, 'docs', 'companies')

# 渲染端會直接呼叫 .map()／.join()／.length 的欄位——型別錯了整頁會死
ARRAY_FIELDS = ('locs', 'plan', 'group')
# 渲染端以物件取值的欄位
OBJECT_FIELDS = ('letters',)
REQUIRED = ('company', 'tier', 'score', 'active')
# 歸類欄位由使用者在儀表板手動設定，排程不得寫入
FORBIDDEN = ('track', 'trackWhy')


def main() -> int:
    errs = []
    warns = []

    wl = json.load(open(os.path.join(DATA, 'watchlist.json'), encoding='utf-8'))
    idx = json.load(open(os.path.join(COMPANIES, 'index.json'), encoding='utf-8'))
    json.load(open(os.path.join(DATA, 'records.json'), encoding='utf-8'))

    seen = set()
    for c in wl:
        co = c.get('company', '(無公司名)')

        for f in REQUIRED:
            if c.get(f) in (None, ''):
                errs.append(f'{co}.{f}：必填欄位為空')

        if co in seen:
            errs.append(f'{co}：watchlist 中重複出現')
        seen.add(co)

        for f in ARRAY_FIELDS:
            v = c.get(f)
            if v is None:
                continue  # 渲染端寫法為 (w.x || [])，null 安全
            if not isinstance(v, list):
                errs.append(
                    f'{co}.{f}：型別為 {type(v).__name__}，必須是 list。'
                    f'渲染端會對它呼叫 .map()，字串會讓整個儀表板停止渲染')
            elif f == 'plan':
                for i, item in enumerate(v):
                    if not isinstance(item, dict) or 'd' not in item or 'w' not in item:
                        errs.append(f'{co}.plan[{i}]：每筆須為 {{"d":日期,"w":說明}}')
            elif f == 'group':
                for i, item in enumerate(v):
                    if not isinstance(item, dict) or 'n' not in item or 'r' not in item:
                        errs.append(f'{co}.group[{i}]：每筆須為 {{"n":公司名,"r":關係說明}}')

        for f in OBJECT_FIELDS:
            v = c.get(f)
            if v in (None, ''):
                # letters 未被 index.html 使用，缺漏不會讓頁面壞掉，但排程規則要求每家都有
                warns.append(f'{co}.{f}：缺開發信範本（第 1／2／3 次版）')
            elif not isinstance(v, dict):
                errs.append(f'{co}.{f}：型別為 {type(v).__name__}，必須是 dict')
            elif set(v) != {'1', '2', '3'}:
                warns.append(f'{co}.{f}：應含 "1"／"2"／"3" 三版，目前為 {sorted(v)}')

        for f in FORBIDDEN:
            if f in c:
                errs.append(f'{co}.{f}：長期追蹤為純人工判斷，排程不得寫入此欄')

        md = c.get('md')
        if not md:
            errs.append(f'{co}.md：未設定，儀表板的公司連結會斷')
        else:
            if not os.path.exists(os.path.join(COMPANIES, md)):
                errs.append(f'{co}.md：檔案不存在 docs/companies/{md}')
            if md not in idx:
                errs.append(f'{co}.md：{md} 未登錄於 docs/companies/index.json')

        if not c.get('locs'):
            warns.append(f'{co}：無 locs，據點地圖與區域徽章會是空的')

    for name, label in ((warns, '警告'), (errs, '錯誤')):
        for m in name:
            print(f'[{label}] {m}')

    print(f'\nwatchlist {len(wl)} 家｜錯誤 {len(errs)}｜警告 {len(warns)}')
    if errs:
        print('\n❌ 有錯誤，請勿 push——這類型別錯誤會讓整個儀表板空白。')
        return 1
    print('✅ 通過')
    return 0


if __name__ == '__main__':
    sys.exit(main())
