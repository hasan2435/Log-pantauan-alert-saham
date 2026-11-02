#!/usr/bin/env python3
"""
Log Pantau Alert Saham - versi terminal, bisa dijalankan sendiri.
  python3 log_pantau.py            # satu kali scan
  python3 log_pantau.py --loop     # scan tiap 15 menit, Senin-Jumat 09.00-15.00 WIB
Sumber: Yahoo Finance publik IDX (chart 5 menit), bukan feed langsung BEI.
Aturan trigger sama dengan alert WhatsApp: VWAP, AKUM+SCALPING, ARA HUNTER,
SCALPING AWAL. Dedup 1x per ticker per jenis alert per hari (di memori sesi ini).
"""
import json, math, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

WATCHLIST = ["ASLI","FUTR","PTRO","VKTR","PGAS","GOTO","TPIA","CUAN","BRPT",
             "DSSA","BUMI","AADI","ENRG","INDY","MYOH","KINO","LINK","PTIS","SULI","NASI"]
ACCELERATION = ["PACK","PPGL","CASH","CHIP","NANO","WIDI","IDEA","SMKM","RELF","MGLV","KING","KLIN","RUNS","FLMC","IBOS","PLAN","NAYZ","HAJJ","UDNG","FIMP","IPAC","EURO","LUCY","PGJO","AMMS"]
WIB = timezone(timedelta(hours=7))
seen = set()

def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.JK?range=1d&interval=5m"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    meta = res["meta"]; q = res["indicators"]["quote"][0]
    pairs = [(c, v or 0) for c, v in zip(q["close"], q["volume"]) if c is not None]
    closes = [c for c, v in pairs]; vols = [v for c, v in pairs]
    if not closes: return None
    price = closes[-1]; prev = meta.get("chartPreviousClose") or closes[0]
    change = (price - prev) / prev * 100 if prev else 0
    vv = sum(vols); vwap = sum(c*v for c, v in zip(closes, vols)) / vv if vv else price
    avg = sum(vols)/len(vols) if vols else 0
    ratio = (sum(vols[-3:])/3/avg) if avg else 0
    return dict(symbol=symbol, price=price, prev=prev, change=change, vwap=vwap,
                low=min(closes), high=max(closes), vol_ratio=ratio)

def fraction(p):
    return 1 if p < 200 else (5 if p <= 5000 else 25)

def ara_arb(prev, aksel):
    if aksel:
        return (prev+1, prev-1) if prev <= 10 else (math.floor(prev*1.10/fraction(prev))*fraction(prev), math.ceil(prev*0.90/fraction(prev))*fraction(prev))
    pct = 35 if prev <= 200 else (25 if prev <= 5000 else 20)
    return (math.floor(prev*(1+pct/100)/fraction(prev))*fraction(prev),
            math.ceil(prev*0.93/fraction(prev))*fraction(prev))

def signals(s):
    out = []
    if s["price"] > s["vwap"] and s["change"] > 0: out.append("VWAP")
    if s["price"] > s["vwap"] and 2 <= s["change"] < 12 and s["vol_ratio"] > 2: out.append("AKUM+SCALPING")
    ara, _ = ara_arb(s["prev"], s["symbol"] in ACCELERATION)
    if (ara - s["price"]) / s["price"] * 100 <= 10: out.append("ARA HUNTER")
    if 1 <= s["change"] <= 3 and s["price"] > s["vwap"] and s["vol_ratio"] > 2: out.append("SCALPING AWAL")
    if -3 <= s["change"] < 1 and s["price"] >= s["low"] * 1.02 and s["vol_ratio"] > 2: out.append("SCALPING AWAL (rebound)")
    return out

def scan():
    now = datetime.now(WIB)
    print(f"\n=== SCAN {now:%Y-%m-%d %H:%M} WIB — {len(WATCHLIST)} ticker ===")
    found = False
    for sym in WATCHLIST:
        try: s = fetch(sym)
        except Exception as e: print(f"  ! {sym} gagal: {e}"); continue
        if not s: continue
        for sig in signals(s):
            key = (now.date(), sym, sig)
            if key in seen: continue
            seen.add(key); found = True
            print(f"TRIGGER {sym:6} Rp{s['price']:.0f} ({s['change']:+.2f}%) VWAP {s['vwap']:.0f} -> {sig}")
        time.sleep(0.2)
    if not found: print("Tidak ada trigger baru pada scan ini.")
    print("Catatan: screening data publik, bukan rekomendasi pasti.")

if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            now = datetime.now(WIB)
            if now.weekday() < 5 and 9 <= now.hour < 15:
                scan(); time.sleep(900)
            else:
                print(f"{now:%H:%M} WIB di luar jam bursa, cek lagi 5 menit."); time.sleep(300)
    else:
        scan()
