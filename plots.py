'''
구현3 : 발표자료용 그래프 한 번에 뽑기

results/ 폴더(구현2 결과)를 읽어서 results/plots/ 에 png로 저장합니다.
  1) 각 비교쌍별 DTW 매칭 + 누적비용행렬 그래프   (paths.json 사용)
  2) 같은 종류 vs 다른 종류 DTW 거리 비교          (pairs.csv 사용)
  3) DTW vs 워핑 없는 L1 거리 비교                 (pairs.csv 사용)
  4) 입력 크기별 실행시간 / 메모리                  (timing.csv 사용)

실행 명령어 $ py .\\plots.py
'''

import csv
import json
import os

import matplotlib
matplotlib.use("Agg")  # 창 안 띄우고 파일로만 저장
import matplotlib.pyplot as plt

from main import DTWdist
from util import print_plot

RESULTS = "results"
OUT = os.path.join(RESULTS, "plots")

BLUE = "#257de0"    # same / DTW
ORANGE = "#f47230"  # diff / L1
GRAY = "#666666"


def read_csv(name):
    # utf-8-sig : csv 맨 앞에 BOM(﻿)이 붙어 있어도 제거하고 읽음
    with open(os.path.join(RESULTS, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean_axes(ax):
    # 위/오른쪽 테두리 지우고 격자는 연하게
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", linewidth=0.8)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------
# 1) 비교쌍별 매칭 그래프
# ---------------------------------------------------------------
def plot_all_pairs():
    with open(os.path.join(RESULTS, "paths.json"), encoding="utf-8") as f:
        paths = json.load(f)

    for key, item in paths.items():
        s, t = item["s"], item["t"]
        # 행렬은 json에 없어서 다시 계산 (경로는 저장된 거 그대로 사용)
        dtw = DTWdist(s, t, verbose=False)
        path = [tuple(p) for p in item["path"]]
        print_plot(s, t, dtw, path, title=key.replace("__", " vs "),
                   save_path=os.path.join(OUT, f"pair_{key}.png"), show=False)


# ---------------------------------------------------------------
# 2) 같은 종류 vs 다른 종류 DTW 거리
# ---------------------------------------------------------------
def plot_same_vs_diff(rows):
    datasets = []
    for r in rows:
        if r["dataset"] not in datasets:
            datasets.append(r["dataset"])

    # 데이터셋마다 거리 크기가 너무 달라서(0 ~ 1000) 하나의 축에 그리면
    # 작은 건 안 보임 -> 데이터셋별로 작은 그래프 따로 (y축 각자)
    fig, axes = plt.subplots(1, len(datasets), figsize=(2.3 * len(datasets), 3.8))
    fig.suptitle("DTW distance: same class vs different class", fontsize=13)

    for ax, ds in zip(axes, datasets):
        same = next((float(r["dtw"]) for r in rows
                     if r["dataset"] == ds and r["kind"] == "same"), None)
        diff = next((float(r["dtw"]) for r in rows
                     if r["dataset"] == ds and r["kind"] == "diff"), None)
        vals = [same or 0, diff or 0]
        bars = ax.bar(["same", "diff"], vals, color=[BLUE, ORANGE], width=0.6,
                      edgecolor="white", linewidth=2)
        for b, v in zip(bars, vals):
            ax.annotate(f"{v:g}", (b.get_x() + b.get_width() / 2, v),
                        ha="center", va="bottom", fontsize=9, color="#191919",
                        xytext=(0, 2), textcoords="offset points")
        ax.set_title(ds, fontsize=11)
        ax.set_ylim(0, max(vals) * 1.2 or 1)
        clean_axes(ax)

    axes[0].set_ylabel("DTW distance (lower = more similar)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "same_vs_diff.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------
# 3) DTW vs 워핑 없는 L1 거리
# ---------------------------------------------------------------
def plot_dtw_vs_l1(rows):
    # l1_no_warp 값이 있는 행만 (길이가 같은 쌍만 L1 계산 가능)
    rows = [r for r in rows if r["l1_no_warp"].strip()]
    labels = [f'{r["dataset"]}\n({r["kind"]})' for r in rows]
    # 값 크기가 다 달라서, "L1 대비 DTW가 몇 %인지"로 비교
    ratio = [float(r["dtw"]) / float(r["l1_no_warp"]) * 100 for r in rows]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(labels, ratio, color=BLUE, width=0.6, edgecolor="white", linewidth=2)
    ax.axhline(100, color=GRAY, linestyle="--", linewidth=1)
    ax.text(len(rows) - 0.5, 101, "L1 (no warping) = 100%", ha="right",
            va="bottom", fontsize=9, color=GRAY)
    for b, v in zip(bars, ratio):
        ax.annotate(f"{v:.0f}%", (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=9, color="#191919",
                    xytext=(0, 2), textcoords="offset points")
    ax.set_ylim(0, 115)
    ax.set_ylabel("DTW distance / L1 distance (%)")
    ax.set_title("How much DTW reduces distance by allowing time warping", fontsize=13)
    clean_axes(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dtw_vs_l1.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------
# 4) 실행시간 / 메모리
# ---------------------------------------------------------------
def plot_timing(rows):
    sq = [r for r in rows if r["exp"] == "n=m"]
    fixed = [r for r in rows if r["exp"] != "n=m"]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.2))

    # (a) n = m 일 때 : O(n^2) 확인
    n = [int(r["n"]) for r in sq]
    ms = [float(r["dtw_ms"]) for r in sq]
    # 가장 큰 n 기준으로 c*n^2 기준선 맞춤
    c = ms[-1] / n[-1] ** 2
    ax1.plot(n, ms, "o-", color=BLUE, linewidth=2, markersize=6, label="measured")
    ax1.plot(n, [c * x * x for x in n], "--", color=GRAY, linewidth=1.2,
             label=r"$c \cdot n^2$")
    ax1.set_title("n = m : time grows as O(n²)")
    ax1.set_xlabel("n (= m)")
    ax1.set_ylabel("DTW time (ms)")
    ax1.legend(frameon=False)
    clean_axes(ax1)

    # (b) n = 200 고정, m 증가 : O(m) 선형
    m = [int(r["m"]) for r in fixed]
    ms2 = [float(r["dtw_ms"]) for r in fixed]
    c2 = ms2[-1] / m[-1]
    ax2.plot(m, ms2, "o-", color=BLUE, linewidth=2, markersize=6, label="measured")
    ax2.plot(m, [c2 * x for x in m], "--", color=GRAY, linewidth=1.2,
             label=r"$c \cdot m$")
    ax2.set_title(f"n = {fixed[0]['n']} fixed : time grows linearly in m")
    ax2.set_xlabel("m")
    ax2.set_ylabel("DTW time (ms)")
    ax2.legend(frameon=False)
    clean_axes(ax2)

    # (c) 메모리 vs 행렬 칸 수 (n*m) : O(nm)
    cells = [int(r["n"]) * int(r["m"]) for r in rows]
    mem = [float(r["mem_kb"]) for r in rows]
    ax3.plot(cells, mem, "o", color=BLUE, markersize=7)
    ax3.set_title("Memory grows with matrix size O(nm)")
    ax3.set_xlabel("n × m (number of cells)")
    ax3.set_ylabel("memory (KB)")
    ax3.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    clean_axes(ax3)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "timing.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plot_all_pairs()
    pairs = read_csv("pairs.csv")
    plot_same_vs_diff(pairs)
    plot_dtw_vs_l1(pairs)
    plot_timing(read_csv("timing.csv"))
    print("완료 :", OUT)