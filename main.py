'''
DTW알고리즘에대한 대략적 설명입니다

INPUT = 시간수열 = 시간 흐름에따라 순서대로 기록된 데이터를 말함
e.g 음성데이터에경우 같은 "사과"를 말하더라도 말하는 속도에 따라 음성데이터 패턴이 다르게 존재하게된다.

그래서 DTW는 뭘 하는가? -> 위같은 예시처럼 같은 패턴이지만 속도가달라 다르다고 판명될수있는 데이터를 
속도로인한 오차를 보정하며 유사도를 측정하는 알고리즘이다.

HOW? -> 일단 DP와 백트레이싱.
자세한건 공유한 영상 봐주세요. 글로설명하는거보다 바로 이해가 됩니다.


@pseudo code
int DTWDistance(s: array [1..n], t: array [1..m]) {
    DTW := array [0..n, 0..m]
    
    for i := 0 to n
        for j := 0 to m
            DTW[i, j] := infinity
    DTW[0, 0] := 0
    
    for i := 1 to n
        for j := 1 to m
            cost := d(s[i], t[j])
            DTW[i, j] := cost + minimum(DTW[i-1, j  ],    
                                        DTW[i  , j-1],    
                                        DTW[i-1, j-1])    
    return DTW[n, m]
}
'''

import sys
from util import print_matrix, print_plot

def backtracing(dtw, s, t, verbose=True):
    # 구현2 : 누적비용행렬 오른쪽 아래 (n,m)에서 시작해서 (1,1)까지 거꾸로 따라감
    # 대각선, 위, 왼쪽 중에 제일 작은 칸으로 이동 (값이 같으면 대각선 먼저)
    # 0번 행/열이 inf라서 끝에 닿으면 알아서 벽 타고 (1,1)로 감
    i, j = len(s), len(t)
    path = [(i-1, j-1)]  # s, t 인덱스로 저장 (0부터)
    while i > 1 or j > 1:
        diag = dtw[i-1][j-1]
        up = dtw[i-1][j]
        left = dtw[i][j-1]
        if diag <= up and diag <= left:
            i, j = i-1, j-1
        elif up <= left:
            i = i-1
        else:
            j = j-1
        path.append((i-1, j-1))
    path.reverse()  # 뒤에서부터 넣었으니까 뒤집어줌

    if verbose:
        print("--- 백트레이싱 경로 ---")
        # 경로에 있는 칸은 [ ]로 표시
        on_path = set(path)
        for r in range(len(s)):
            line = []
            for c in range(len(t)):
                if (r, c) in on_path:
                    line.append(f"[{dtw[r+1][c+1]:5.1f}]")
                else:
                    line.append(f" {dtw[r+1][c+1]:5.1f} ")
            print(" ".join(line))
        print()
        print("--- 매핑 결과 ---")
        for a, b in path:
            print(f"s[{a}]={s[a]:g}  <->  t[{b}]={t[b]:g}")
        print("경로 길이 :", len(path))
        print()

    return path

def DTWdist(s,t, verbose=True):
    # verbose=False면 행렬 출력 안함 (실행시간 잴 때 출력하는 시간까지 같이 재지는거 막으려고 추가)
    dtw = []
    # dtw 배열 초기화: 크기는 (len(s) + 1) x (len(t) + 1)
    # 0번 행과 0번 열은 경계 조건 처리(i-1, j-1 참조 및 시작점 고정)를 위한 inf 패딩 영역
    for i in range(len(s)+1):
        dtw.append([])
        for j in range(len(t)+1):
            dtw[i].append(float('inf'))
    # (0, 0)만 0으로 설정하여 (1, 1)의 누적 비용이 dtw[1][1] 자체 거리값에서 시작되도록 함
    dtw[0][0] = 0
    if verbose:
        print("--- 초기화된 거리행렬 ---")
        print_matrix(dtw)

    # 거리 행렬 만들기 (패딩인 0번 행/열은 건너뛰고 1..len 범위만 채움)
    # dtw는 1-based(패딩 포함), s/t는 0-based이므로 s[i-1], t[j-1]로 접근
    for i in range(1,len(s)+1):
        for j in range(1,len(t)+1):
            dtw[i][j] = abs(s[i-1] - t[j-1])
    if verbose:
        print("--- 실제 거리행렬 ---")
        print_matrix(dtw)

    # 누적 비용 행렬 만들기 (현재 거리 + 인접 3방향 누적 비용의 최솟값)
    # dtw[i-1][j]: 위(insertion), dtw[i][j-1]: 왼쪽(deletion), dtw[i-1][j-1]: 대각선 왼쪽 위(match)
    for i in range(1,len(s)+1):
        for j in range(1,len(t)+1):
            dtw[i][j] = dtw[i][j] + min(dtw[i-1][j],dtw[i][j-1],dtw[i-1][j-1])    
    if verbose:
        print("--- 누적 비용 행렬 ---")
        print_matrix(dtw)

    return dtw


''' 실행 명령어 $ py .\main.py .\data\sample1.txt .\data\sample2.txt '''
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <file1.txt> <file2.txt>")
        sys.exit(1)
    #비교할 시계열 데이터 2개 받습니다. 
    file1, file2 = sys.argv[1], sys.argv[2]

    #배열로 변환하고요 - 공백을 구분자로 사용했습니다.
    with open(file1, "r") as f:
        s = list(map(float, f.read().split()))
    with open(file2, "r") as f:
        t = list(map(float, f.read().split()))

    #DTW 시행
    dtw = DTWdist(s,t)

    #누적거리행렬의 끝값(오른쪽밑)이 곧 최종거리이며 0에 가까울수로 유사한것.
    print(dtw[-1][-1])
    print()

    #백트레이싱 (구현2)
    path = backtracing(dtw, s, t)
    print_plot(s, t, dtw, path, title=f"{file1} vs {file2}", save_path="results/plot.png")

    
        
    
    