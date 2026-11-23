'''
DTW알고리즘에대한 대략적 설명입니다

INPUT = 시간수열 = 시간 흐름에따라 순서대로 기록된 데이터를 말함
e.g 음성데이터에경우 같은 "사과"를 말하더라도 말하는 속도에 따라 음성데이터 패턴이 다르게 존재하게된다.

그래서 DTW는 뭘 하는가? -> 위같은 예시처럼 같은 패턴이지만 속도가달라 다르다고 판명될수있는 데이터를 
속도로인한 오차를 보정하며 유사도를 측정하는 알고리즘이다.

HOW? -> 일단 DP와 백트레이싱.
자세한건 공유한 영상 봐주세요. 글로설명하는거보다 바로 이해가 됩니다.


@psudo code
int DTWDistance(s: array [1..n], t: array [1..m]) {
    DTW := array [0..n, 0..m]
    
    for i := 0 to n
        for j := 0 to m
            DTW[i, j] := infinity
    DTW[0, 0] := 0
    
    for i := 1 to n
        for j := 1 to m
            cost := d(s[i], t[j])
            DTW[i, j] := cost + minimum(DTW[i-1, j  ],    // insertion
                                        DTW[i  , j-1],    // deletion
                                        DTW[i-1, j-1])    // match
    return DTW[n, m]
}
'''

import sys
from util import print_matrix

def backtracing():
    # TODO : 구현2 : 완성된 DTW행렬을 받아 백트레이싱하여 데이터 매핑정보 출력
    pass

def DTWdist(s,t):
    dtw = []
    #dtw 배열 초기화요
    for i in range(len(s)+1):
        dtw.append([])
        for j in range(len(t)+1):
            dtw[i].append(float('inf'))
    dtw[0][0] = 0
    print("--- 초기화된 거리행렬 ---")
    print_matrix(dtw)
    #거리 행렬 만들고요
    for i in range(1,len(s)+1):
        for j in range(1,len(t)+1):
            dtw[i][j] = abs(s[i-1] - t[j-1])
    print("--- 실제 거리행렬 ---")
    print_matrix(dtw)

    #누적 비용 행렬 만들기
    for i in range(1,len(s)+1):
        for j in range(1,len(t)+1):
            dtw[i][j] = dtw[i][j] + min(dtw[i-1][j],dtw[i][j-1],dtw[i-1][j-1])    
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

    
        
    
    