# 구현2 : data 폴더에 있는 샘플 데이터 만드는 코드
# 원본은 UCR/UEA 시계열 데이터 아카이브인데, sktime 패키지 안에 .ts 파일로 들어있어서
# pip로 패키지 파일(휠)만 받아서 필요한 것만 꺼내 씀 (설치는 안 함)
# 실행 : py .\tools\make_datasets.py

import glob
import math
import os
import subprocess
import sys
import tempfile
import zipfile

DATA_DIR = "data"
FILES = {
    "GunPoint": "GunPoint/GunPoint_TRAIN.ts",
    "ItalyPowerDemand": "ItalyPowerDemand/ItalyPowerDemand_TRAIN.ts",
    "BasicMotions": "BasicMotions/BasicMotions_TRAIN.ts",
    "JapaneseVowels": "JapaneseVowels/JapaneseVowels_TRAIN.ts",
}


def download(tmp):
    # 버전 고정해야 누가 돌려도 똑같은 데이터 나옴
    subprocess.run([sys.executable, "-m", "pip", "download", "sktime==1.3.0", "--no-deps", "-q", "-d", tmp], check=True)
    wheel = glob.glob(os.path.join(tmp, "sktime-*.whl"))[0]
    paths = {}
    with zipfile.ZipFile(wheel) as z:
        for name, rel in FILES.items():
            p = os.path.join(tmp, name + ".ts")
            with open(p, "wb") as f:
                f.write(z.read("sktime/datasets/data/" + rel))
            paths[name] = p
    return paths


def read_ts(path):
    # .ts 파일 읽기. 한 줄 = 샘플 하나, ':'로 차원 구분, 맨 끝이 라벨
    rows = []
    started = False
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("@data"):
            started = True
            continue
        if not started:
            continue
        *dims, label = line.split(":")
        rows.append(([[float(x) for x in d.split(",")] for d in dims], label))
    return rows


def take(rows, label, k):
    # 라벨이 같은 것 중 앞에서부터 k개 (첫 번째 차원만)
    return [r[0][0] for r in rows if r[1] == label][:k]


def save(name, seq):
    with open(os.path.join(DATA_DIR, name + ".txt"), "w") as f:
        f.write(" ".join(f"{v:.4f}".rstrip("0").rstrip(".") for v in seq))


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        p = download(tmp)
        gun = read_ts(p["GunPoint"])             # 1 = 총 뽑기, 2 = 가리키기
        power = read_ts(p["ItalyPowerDemand"])   # 1 = 겨울(10~3월), 2 = 여름(4~9월)
        motion = read_ts(p["BasicMotions"])      # 가속도 x축만 사용
        vowel = read_ts(p["JapaneseVowels"])     # 라벨 = 화자 번호

        g1, g2 = take(gun, "1", 2), take(gun, "2", 1)
        w, s = take(power, "1", 2), take(power, "2", 1)
        walk, run = take(motion, "Walking", 2), take(motion, "Running", 1)
        v1, v2 = take(vowel, "1", 2), take(vowel, "2", 1)

    save("gunpoint_gun1", g1[0])
    save("gunpoint_gun2", g1[1])
    save("gunpoint_point1", g2[0])
    save("power_winter1", w[0])
    save("power_winter2", w[1])
    save("power_summer1", s[0])
    save("motion_walking1", walk[0])
    save("motion_walking2", walk[1])
    save("motion_running1", run[0])
    save("vowel_spk1_a", v1[0])
    save("vowel_spk1_b", v1[1])
    save("vowel_spk2_a", v2[0])

    # 직접 만든 사인파 (같은 모양인데 속도만 다른 것 / 옆으로 밀린 것)
    save("warp_base", [math.sin(2 * math.pi * k / 39) for k in range(40)])
    save("warp_slow", [math.sin(2 * math.pi * ((k / 59) ** 1.6)) for k in range(60)])
    save("warp_shift", [math.sin(2 * math.pi * k / 39 - 0.6) for k in range(40)])

    print("data 폴더에 15개 저장 완료")
