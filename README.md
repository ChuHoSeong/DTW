# DTW (Dynamic Time Warping)

두 시계열 데이터 간의 유사도(거리)를 Dynamic Time Warping 알고리즘으로 계산하는 프로그램입니다.

## 파일 구성

- `main.py`: 두 텍스트 파일에서 시계열 데이터를 읽어 DTW 거리 행렬과 누적 비용 행렬을 계산하고 출력합니다.
- `util.py`: 행렬을 정렬된 형태로 출력하는 `print_matrix` 유틸리티 함수가 정의되어 있습니다.
- `data/`: 테스트용 샘플 시계열 데이터 파일(`sample1.txt`, `sample2.txt`, `sample3.txt` 등)이 들어 있습니다. 음성, 전력, 가속도, 손동작, 사인파 데이터도 추가했습니다(구현2).
- `experiment.py`: 샘플 비교랑 크기별 실행시간/메모리 측정, 결과는 `results/`에 저장
- `tools/make_datasets.py`: data 폴더의 샘플 데이터 만드는 코드
- `docs/구현2_실험_복잡도.md`: 데이터 설명, 실험 결과, 복잡도 정리

## 입력 파일 형식

공백 또는 줄바꿈으로 구분된 실수/정수 시퀀스를 사용합니다.

```text
1 2 3 4 5
```

## 실행 방법

```powershell
py .\main.py .\data\sample1.txt .\data\sample2.txt
```

## 동작 과정

1. `(len(s) + 1) x (len(t) + 1)` 크기의 행렬을 `inf`로 초기화하고 `(0, 0)`을 `0`으로 설정합니다.
2. 각 시점 쌍 `(i, j)`의 절대 차이 `|s[i-1] - t[j-1]|`로 거리 행렬을 채웁니다.
3. 위, 왼쪽, 대각선 왼쪽 위 중 최솟값을 더해 누적 비용 행렬을 계산합니다.
4. 누적 비용 행렬의 우하단 끝값(`dtw[-1][-1]`)을 최종 DTW 거리로 출력합니다. 값이 0에 가까울수록 두 시계열이 유사합니다.
5. `backtracing()`으로 오른쪽 아래부터 거꾸로 따라가서 어떤 점끼리 매칭됐는지 출력합니다. 경로는 `[(i, j), ...]` 리스트로 반환합니다.

## 실험 실행

```powershell
py .\experiment.py
```


## 참고자료
1.https://en.wikipedia.org/wiki/Dynamic_time_warping
2.https://www.youtube.com/watch?v=ZuipO7MAejQ
