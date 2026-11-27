def print_matrix(matrix):
    '''
    행렬을 포맷에 맞게 출력하는 함수
    '''
    for row in matrix:
        print(" ".join(f"{x:6.1f}" for x in row))
    print()


def print_plot(s, t, dtw, path, title="DTW", save_path=None, show=True):
    '''
    구현3 : 발표자료용 그래프 그리기

    s, t      : 비교한 두 시계열 (list)
    dtw       : DTWdist()가 반환한 누적 비용 행렬 ((n+1) x (m+1), 0번 행/열은 inf 패딩)
    path      : backtracing()이 반환한 경로 [(i, j), ...] (0-based)
    save_path : 지정하면 png로 저장 (예: "results/plot.png")
    show      : True면 창 띄워서 보여줌
    '''
    # matplotlib는 그래프 그릴 때만 필요하니까 함수 안에서 import
    # (print_matrix만 쓸 때는 matplotlib 없어도 돌아가게)
    import matplotlib.pyplot as plt

    dist = dtw[-1][-1]
    # 0번 행/열(inf 패딩) 빼고 실제 누적 비용만 가져옴
    cost = [row[1:] for row in dtw[1:]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5),
                                   gridspec_kw={"width_ratios": [1.6, 1]})
    fig.suptitle(f"{title}  (DTW distance = {dist:.2f})", fontsize=14)

    # ---------- (1) 두 시계열 매칭 그래프 ----------
    # 두 그래프가 겹치면 연결선이 안 보여서 t를 아래로 내려서 그림
    gap = (max(max(s), max(t)) - min(min(s), min(t))) * 1.2 or 1
    t_shift = [v - gap for v in t]

    # 경로에 있는 (i, j) 쌍끼리 회색 선으로 연결
    for i, j in path:
        ax1.plot([i, j], [s[i], t_shift[j]], color="gray", linewidth=0.6, alpha=0.6)
    ax1.plot(range(len(s)), s, "o-", color="#257de0", markersize=3, label="s")
    ax1.plot(range(len(t)), t_shift, "o-", color="#f47230", markersize=3,
             label="t (shifted down)")
    ax1.set_title("Point-to-point alignment")
    ax1.set_xlabel("time index")
    ax1.set_yticks([])
    ax1.legend(loc="upper right")

    # ---------- (2) 누적 비용 행렬 + 백트레이싱 경로 ----------
    im = ax2.imshow(cost, origin="lower", cmap="viridis", aspect="auto")
    fig.colorbar(im, ax=ax2, label="cumulative cost")
    pi = [i for i, _ in path]
    pj = [j for _, j in path]
    ax2.plot(pj, pi, color="#ec4647", linewidth=2, label="warping path")
    ax2.set_title("Cumulative cost matrix")
    ax2.set_xlabel("t index (j)")
    ax2.set_ylabel("s index (i)")
    ax2.legend(loc="upper left")

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print("그래프 저장 :", save_path)
    if show:
        plt.show()
    plt.close(fig)
