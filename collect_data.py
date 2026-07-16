#!/usr/bin/env python3
"""국내주식 일봉 데이터 수집 (FinanceDataReader / 네이버 금융 기반).

GitHub Actions에서 매주 자동 실행되어 data/ 를 최신으로 갱신한다.
로컬 실행:  pip install finance-datareader && python3 collect_data.py
"""
import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "data"


def collect(top_n: int, years: int, delay: float) -> None:
    import FinanceDataReader as fdr

    start = (datetime.now() - timedelta(days=365 * years)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y%m%d")

    # 시가총액 상위 종목 (KOSPI + KOSDAQ)
    targets = []
    for market in ("KOSPI", "KOSDAQ"):
        df = fdr.StockListing(market)
        df = df.sort_values("Marcap", ascending=False).head(top_n)
        for _, row in df.iterrows():
            targets.append((row["Code"], row["Name"], market))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for f in OUT_DIR.glob("*.json"):
        f.unlink()

    index = []
    for i, (code, name, market) in enumerate(targets):
        try:
            df = fdr.DataReader(code, start)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {code} {name}: {e}")
            continue
        df = df[(df["Open"] > 0) & (df["Volume"] > 0)]
        if len(df) < 400:  # 표시 300 + 진행 50 + 여유
            print(f"[skip] {code} {name}: 데이터 부족 ({len(df)}봉)")
            continue
        candles = [
            {
                "t": d.strftime("%Y-%m-%d"),
                "o": int(r["Open"]),
                "h": int(r["High"]),
                "l": int(r["Low"]),
                "c": int(r["Close"]),
                "v": int(r["Volume"]),
            }
            for d, r in df.iterrows()
        ]
        (OUT_DIR / f"{code}.json").write_text(
            json.dumps({"code": code, "name": name, "market": market, "candles": candles},
                       ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        index.append({"code": code, "name": name, "market": market, "n": len(candles)})
        print(f"[{i+1}/{len(targets)}] {code} {name}: {len(candles)}봉")
        time.sleep(delay)

    (OUT_DIR / "index.json").write_text(
        json.dumps({"real": True, "updated": end, "stocks": index}, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n완료: {len(index)}종목 → {OUT_DIR}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--top", type=int, default=100)
    p.add_argument("--years", type=int, default=12)
    p.add_argument("--delay", type=float, default=0.3)
    args = p.parse_args()
    collect(args.top, args.years, args.delay)
