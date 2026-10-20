"""Take one snapshot of crypto prices and USD/VND, append it to data/prices.csv
and refresh the summary block in README.md.

Standard library only, so the workflow needs no install step.
Exits 0 without touching files when the price API is unreachable.
"""

import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "prices.csv"
README_PATH = ROOT / "README.md"

COINS = [("bitcoin", "BTC"), ("ethereum", "ETH"), ("solana", "SOL")]
FIELDS = ["time_utc", "btc_usd", "eth_usd", "sol_usd", "usd_vnd"]
START, END = "<!-- pulse:start -->", "<!-- pulse:end -->"
VN_TZ = timezone(timedelta(hours=7))
SPARK = "▁▂▃▄▅▆▇█"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "market-pulse/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def fetch_crypto():
    ids = ",".join(cid for cid, _ in COINS)
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    )
    return get_json(url)


def fetch_usd_vnd():
    try:
        return get_json("https://open.er-api.com/v6/latest/USD")["rates"]["VND"]
    except Exception as exc:  # FX is optional; keep the snapshot anyway
        print(f"warn: USD/VND unavailable ({exc})", file=sys.stderr)
        return None


def read_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_row(row):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_file = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def sparkline(values):
    values = [v for v in values if v is not None]
    if len(values) < 2:
        return "—"
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    return "".join(SPARK[round((v - lo) / span * (len(SPARK) - 1))] for v in values)


def fmt_usd(v):
    return f"${v:,.2f}" if v < 1000 else f"${v:,.0f}"


def render_summary(rows, prices, now):
    recent = rows[-40:]
    lines = [
        f"_Cập nhật lần cuối: {now.astimezone(VN_TZ):%d/%m/%Y %H:%M} (giờ VN) · "
        f"{len(rows)} lần ghi_",
        "",
        "| Đồng | Giá | 24h | Gần đây |",
        "|---|---:|---:|---|",
    ]
    for cid, sym in COINS:
        p = prices[cid]
        change = p.get("usd_24h_change") or 0
        trend = sparkline([float(r[f"{sym.lower()}_usd"]) for r in recent if r.get(f"{sym.lower()}_usd")])
        lines.append(f"| {sym} | {fmt_usd(p['usd'])} | {change:+.2f}% | `{trend}` |")
    vnd = rows[-1].get("usd_vnd")
    if vnd:
        lines += ["", f"1 USD ≈ **{float(vnd):,.0f} VND**"]
    return "\n".join(lines)


def update_readme(summary):
    text = README_PATH.read_text(encoding="utf-8")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    README_PATH.write_text(f"{head}{START}\n{summary}\n{END}{tail}", encoding="utf-8")


def main():
    try:
        prices = fetch_crypto()
        if not all(cid in prices for cid, _ in COINS):
            raise ValueError(f"incomplete response: {prices}")
    except Exception as exc:
        print(f"skip: price API unavailable ({exc})", file=sys.stderr)
        return 0

    now = datetime.now(timezone.utc)
    vnd = fetch_usd_vnd()
    row = {
        "time_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "btc_usd": prices["bitcoin"]["usd"],
        "eth_usd": prices["ethereum"]["usd"],
        "sol_usd": prices["solana"]["usd"],
        "usd_vnd": round(vnd, 2) if vnd else "",
    }
    append_row(row)
    rows = read_rows()
    update_readme(render_summary(rows, prices, now))

    btc = prices["bitcoin"]
    msg = (
        f"data: BTC {fmt_usd(btc['usd'])} ({(btc.get('usd_24h_change') or 0):+.1f}%)"
        f" · ETH {fmt_usd(prices['ethereum']['usd'])}"
    )
    msg_file = os.environ.get("COMMIT_MSG_FILE")
    if msg_file:
        Path(msg_file).write_text(msg + "\n", encoding="utf-8")
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
