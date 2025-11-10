import pathlib, datetime
base = pathlib.Path("/workspaces/argentina")
report = base/"報告_阿根廷經濟改革與匯率_整合版.md"
sources = {
    "PDF主檔": base/"_main_pdf.txt",
    "第一章": base/"阿根廷經濟改革對匯率的影響_第一章擴充完整版.txt",
    "第二章": base/"阿根廷經濟改革對匯率的影響_第二章擴充完整版.txt",
    "第三章": base/"阿根廷經濟改革對匯率的影響_第三章擴充完整版.txt",
    "第四章": base/"阿根廷經濟改革對匯率的影響_第四章擴充完整版.txt",
    "第五章": base/"阿根廷經濟改革對匯率的影響_第五章擴充完整版.txt",
}
def read(p):
    for enc in ("utf-8","latin-1"):
        try: return p.read_text(encoding=enc)
        except: pass
    return ""
def excerpt(txt, n):
    lines=[l for l in txt.splitlines() if l.strip()]
    out,tot=[],0
    for l in lines:
        if tot+len(l)>n: break
        out.append(l); tot+=len(l)+1
    return "\n".join(out)
if not report.exists(): raise SystemExit("找不到報告骨架")
tpl = report.read_text(encoding="utf-8").replace("日期：{{DATE}}", f"日期：{datetime.date.today().isoformat()}")
data = {k: read(v) for k,v in sources.items()}
inject = {
    "PDF摘要": excerpt(data["PDF主檔"],1200),
    "CH1": excerpt(data["第一章"],1600),
    "CH2": excerpt(data["第二章"],1600),
    "CH3": excerpt(data["第三章"],1600),
    "CH4": excerpt(data["第四章"],1400),
    "CH5": excerpt(data["第五章"],1400),
}
for tag,val in inject.items():
    tpl = tpl.replace(f"[占位:{tag}]", val)
report.write_text(tpl, encoding="utf-8")
print("已整合 ->", report)

import pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
data_path=Path("/workspaces/argentina/data/argentina_macro.csv")
fig_dir=Path("/workspaces/argentina/fig"); fig_dir.mkdir(exist_ok=True)
df=pd.read_csv(data_path)
df["date"]=pd.to_datetime(df[["year","month"]].assign(day=1))
for c in ["official_fx","parallel_fx","cpi_yoy","reserves_usd_billion"]:
    df[c]=pd.to_numeric(df[c], errors="coerce")
df=df.sort_values("date")
df["fx_premium_pct"]=(df["parallel_fx"]-df["official_fx"])/df["official_fx"]*100
plt.style.use("seaborn-v0_8-whitegrid")
# 圖1
fig,ax1=plt.subplots(figsize=(8.2,4))
ax1.plot(df["date"],df["official_fx"],label="官方匯率",color="#1f77b4")
ax1.plot(df["date"],df["parallel_fx"],label="平行匯率",color="#d62728")
ax2=ax1.twinx(); ax2.bar(df["date"],df["fx_premium_pct"],width=20,color="#ff7f0e",alpha=0.35,label="匯差%")
ax1.set_ylabel("ARS/USD"); ax2.set_ylabel("匯差%"); ax1.set_title("官方 vs 平行匯率與匯差")
h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax1.legend(h1+h2,l1+l2,loc="upper left"); fig.autofmt_xdate(); fig.savefig(fig_dir/"fig_fx.png",dpi=150); plt.close(fig)
# 圖2
fig,ax1=plt.subplots(figsize=(8.2,4))
ax1.plot(df["date"],df["cpi_yoy"],marker="o",label="CPI年增率",color="#2ca02c")
ax2=ax1.twinx(); ax2.plot(df["date"],df["official_fx"],label="官方匯率",color="#1f77b4",linestyle="--")
ax1.set_ylabel("CPI年增率%"); ax2.set_ylabel("ARS/USD"); ax1.set_title("通膨與官方匯率")
h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax1.legend(h1+h2,l1+l2,loc="upper right"); fig.autofmt_xdate(); fig.savefig(fig_dir/"fig_infl_fx.png",dpi=150); plt.close(fig)
# 圖3
fig,ax=plt.subplots(figsize=(8.2,4))
ax.plot(df["date"],df["reserves_usd_billion"],marker="o",color="#9467bd")
ax.set_ylabel("國際儲備 十億美元"); ax.set_title("國際儲備走勢")
fig.autofmt_xdate(); fig.savefig(fig_dir/"fig_reserves.png",dpi=150); plt.close(fig)
print("圖表輸出於", fig_dir)