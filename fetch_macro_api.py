"""
自動抓取匯率/替代指標與示例通膨資料占位：
- 匯率：利用 exchangerate.host (免費) 取得 ARSUSD 即期
- 平行匯率：示例用 (官方匯率 * 1.18) 占位，請手動替換為實際平行市場數值
- 通膨 CPI YoY：需人工填值（INDEC 網頁），此處占位 None
- 儲備：BCRA 未提供簡易 JSON，需人工回填；此處占位 None
"""
import requests, datetime, csv
from pathlib import Path

out = Path("/workspaces/argentina/data/argentina_macro.csv")
out.parent.mkdir(exist_ok=True)

rows = []
if out.exists():
    import pandas as pd
    rows = pd.read_csv(out).to_dict(orient="records")

def get_official_fx():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=ARS", timeout=10)
        return round(r.json()["rates"]["ARS"], 4)
    except Exception as e:
        print("官方匯率抓取失敗:", e)
        return None

today = datetime.date.today()
year, month = today.year, today.month
official = get_official_fx()
if official is None and rows:
    official = float(rows[-1]["official_fx"])
parallel = round(official * 1.18, 4) if official else ""   # 占位，改為真實平行匯率可手動覆蓋
cpi_yoy = ""       # 手動填 INDEC 最新年增率
reserves = ""      # 手動填 BCRA 月底儲備（十億美元）

exists = any(int(r["year"])==year and int(r["month"])==month for r in rows)
if not exists:
    rows.append({"year":year,"month":month,"official_fx":official,"parallel_fx":parallel,
                 "cpi_yoy":cpi_yoy,"reserves_usd_billion":reserves})
else:
    for r in rows:
        if int(r["year"])==year and int(r["month"])==month:
            r["official_fx"]=official; r["parallel_fx"]=parallel
            break

with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["year","month","official_fx","parallel_fx","cpi_yoy","reserves_usd_billion"])
    w.writeheader()
    for r in rows: w.writerow(r)

print("更新資料 ->", out)