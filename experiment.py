# 구현2 : 샘플 데이터 비교 + 실행시간/메모리 측정
# 실행 : py .\experiment.py   (빠르게 보려면 --quick)
# 결과는 results 폴더에 저장 (pairs.csv, paths.json, timing.csv)

import csv
import json
import math
import os
import random
import sys
import time
import tracemalloc

from main import DTWdist, backtracing

DATA_DIR = "data"
OUT_DIR = "results"

# (이름, 기준, 같은 종류, 다른 종류)
PAIRS = [
    ("toy",      "sample1",         "sample2",         "sample3"),
    ("warp",     "warp_base",       "warp_slow",       "warp_shift"),
    ("vowel",    "vowel_spk1_a",    "vowel_spk1_b",    "vowel_spk2_a"),
    ("power",    "power_winter1",   "power_winter2",   "power_summer1"),
    ("motion",   "motion_walking1", "motion_walking2", "motion_running1"),
    ("gunpoint", "gunpoint_gun1",   "gunpoint_gun2",   "gunpoint_point1"),
]


def load(name):
    with open(os.path.join(DATA_DIR, name + ".txt")) as f:
        return list(map(float, f.read().split()))


def l1_no_warp(s, t):
    # 시간축 안 늘리고 같은 시점끼리만 비교 (길이 같을 때만 가능)
    if len(s) != len(t):
        return ""
    return round(sum(abs(a - b) for a, b in zip(s, t)), 4)


def run_pairs():
    rows = []
    paths = {}
    for name, base, same, diff in PAIRS:
        s = load(base)
        for kind, other in [("same", same), ("diff", diff)]:
            t = load(other)
            dtw = DTWdist(s, t, verbose=False)
            path = backtracing(dtw, s, t, verbose=False)
            rows.append({
                "dataset": name, "kind": kind, "s": base, "t": other,
                "n": len(s), "m": len(t),
                "dtw": round(dtw[-1][-1], 4),
                "l1_no_warp": l1_no_warp(s, t),
                "path_len": len(path),
            })
            paths[base + "__" + other] = {"s": s, "t": t, "path": path}
            print(f"[{name}] {kind}  {base} vs {other} (n={len(s)}, m={len(t)})  DTW={dtw[-1][-1]:.3f}  경로길이={len(path)}")
    return rows, paths


def random_walk(n, seed):
    # 테스트용 랜덤 시계열
    random.seed(seed)
    x = 0
    out = []
    for _ in range(n):
        x += random.gauss(0, 1)
        out.append(x)
    return out


def measure(n, m, repeat=3):
    s = random_walk(n, 1)
    t = random_walk(m, 2)
    dtw_times = []
    back_times = []
    for _ in range(repeat):
        start = time.perf_counter()
        dtw = DTWdist(s, t, verbose=False)
        mid = time.perf_counter()
        backtracing(dtw, s, t, verbose=False)
        end = time.perf_counter()
        dtw_times.append(mid - start)
        back_times.append(end - mid)

    # 메모리는 따로 한 번만 잼 (tracemalloc 켜면 느려져서)
    tracemalloc.start()
    DTWdist(s, t, verbose=False)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    return {
        "n": n, "m": m,
        "dtw_ms": round(sorted(dtw_times)[repeat // 2] * 1000, 3),        # 중앙값
        "backtrack_ms": round(sorted(back_times)[repeat // 2] * 1000, 3),
        "mem_kb": round(peak / 1024, 1),
    }


def get_slope(rows, key):
    # log(시간) = k * log(크기) 에서 k 구하기 (작은 크기는 오차 커서 100 이상만)
    xs = [math.log(r[key]) for r in rows if r[key] >= 100]
    ys = [math.log(r["dtw_ms"]) for r in rows if r[key] >= 100]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # 엑셀에서 한글 안 깨지게
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    os.makedirs(OUT_DIR, exist_ok=True)

    print("=== 샘플 비교 ===")
    pair_rows, paths = run_pairs()
    save_csv(os.path.join(OUT_DIR, "pairs.csv"), pair_rows)
    with open(os.path.join(OUT_DIR, "paths.json"), "w") as f:
        json.dump(paths, f)

    print("\n=== 실행시간 (n = m) ===")
    sizes = [10, 50, 100, 200, 400] if quick else [10, 50, 100, 200, 400, 800, 1600]
    square = []
    for n in sizes:
        r = measure(n, n)
        square.append({"exp": "n=m", **r})
        print(f"n=m={n:5d}  DTW {r['dtw_ms']:9.2f} ms  백트레이싱 {r['backtrack_ms']:6.3f} ms  메모리 {r['mem_kb']:9.1f} KB")

    print("\n=== 실행시간 (n=200 고정, m만 증가) ===")
    fixed = []
    for m in ([50, 100, 200, 400] if quick else [50, 100, 200, 400, 800, 1600]):
        r = measure(200, m)
        fixed.append({"exp": "n=200", **r})
        print(f"m={m:5d}  DTW {r['dtw_ms']:9.2f} ms")

    save_csv(os.path.join(OUT_DIR, "timing.csv"), square + fixed)

    print(f"\nn=m 일 때 시간 ~ n^{get_slope(square, 'n'):.2f}  (이론상 2)")
    print(f"n 고정일 때 시간 ~ m^{get_slope(fixed, 'm'):.2f}  (이론상 1)")
