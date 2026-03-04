# LS-DYNA SLURM Job Submission Guide

> **Purpose**: 다른 AI 또는 개발자가 이 문서만 읽고 LS-DYNA 시뮬레이션을 SLURM 클러스터에
> 자동 제출·모니터링·결과 확인할 수 있도록 작성한 가이드.
>
> **클러스터**: 2-node SLURM (node001, node002), Apptainer 컨테이너 기반
> **검증일**: 2026-02-26, 수백 건의 job 제출 이력으로 검증

---

## 1. 클러스터 환경 요약

### 1.1 하드웨어

| 파티션 | 노드 | CPU | RAM | 용도 |
|--------|------|-----|-----|------|
| `normal*` (기본) | node001, node002 | 2 cores | 4 GB | 계산 |
| `viz` | viz-node001, viz-node002 | 2 cores | 3.5 GB | 후처리 |

**제약**:
- 노드당 CPU = **2개** → `ncpu=2`, `--nodes=1`
- RAM = **4 GB** (실질 사용 가능 ~9 GB — swap 포함으로 추정, 실측 기반)
- `/home/koopark`는 **compute node에서 접근 불가** → 모든 데이터는 `/data/` 아래에

### 1.2 파일시스템

```
/data/          ← 공유 스토리지 (login + compute 모두 접근 가능)
/shared/        ← 공유 스토리지 (추가)
/home/koopark/  ← login node만 접근 가능 ⚠️ compute node에서 접근 불가!
/opt/apptainers/← Apptainer SIF 파일 (compute node에 존재)
```

**핵심 규칙**: k-file, config, 결과물 모두 `/data/` 하위에 위치해야 함.

### 1.3 Apptainer 컨테이너 상세

LS-DYNA는 Apptainer (구 Singularity) 컨테이너 안에서 실행됨.
컨테이너 이미지(SIF)는 **compute node 로컬 디스크**에 존재 (login node에는 없음).

#### 1.3.1 사용 가능한 SIF 파일

compute node (`node001`, `node002`)의 `/opt/apptainers/`에 3개 SIF:

| SIF 파일명 | 크기 | Precision | Compiler | MPI | 주 용도 |
|-----------|------|-----------|----------|-----|---------|
| `LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif` | 973 MB | Single (32-bit) | AOCC 4.2.0 | OpenMPI 4.0.5 | **일반 explicit** |
| `LSDynaBasic_ifort2022_impilatest_mpp_d.sif` | 1.48 GB | Double (64-bit) | ifort 2022 | Intel MPI 2021.17 | **implicit, CMS, eigenvalue** |
| `LSDynaBasic_ifort2022_impilatest_mpp_s.sif` | 1.40 GB | Single (32-bit) | ifort 2022 | Intel MPI 2021.17 | (미사용, SP-Intel) |

**SIF 이름 규칙**: `LSDynaBasic_{compiler}_{mpi}_mpp_{precision}.sif`
- `_s` = Single precision, `_d` = Double precision
- `mpp` = Massively Parallel Processing (MPI 병렬)

#### 1.3.2 SIF 내부의 LS-DYNA 버전

각 SIF에는 여러 LS-DYNA 버전이 포함되어 있으며, symlink로 선택 가능:

**SP SIF (aocc420_ompi4.0.5)** 내부:
```
/opt/ls-dyna/
├── lsdyna           → R16.1.1 (기본 symlink)
├── lsdyna_R16.1.1   → ls-dyna_mpp_s_R16_1_1_x64_centos79_aocc420_avx2_openmpi4.0.5
├── lsdyna_R16.1.0   → ls-dyna_mpp_s_R16_1_0_x64_centos79_aocc420_avx2_openmpi4.0.5
├── lsdyna_R16.0.0   → ls-dyna_mpp_s_R16_0_0_x64_centos79_aocc420_avx2_openmpi4.0.5
├── lsdyna_R15.0.2   → ls-dyna_mpp_s_R15_0_2_x64_centos79_aocc400_avx2_openmpi4.0.5
├── ls-dyna_mpp_s_R16_1_1_x64_centos79_aocc420_avx2_openmpi4.0.5      (실 바이너리)
├── ls-dyna_mpp_s_R16_1_0_x64_centos79_aocc420_avx2_openmpi4.0.5
├── ls-dyna_mpp_s_R16_0_0_x64_centos79_aocc420_avx2_openmpi4.0.5
└── ls-dyna_mpp_s_R15_0_2_x64_centos79_aocc400_avx2_openmpi4.0.5
```

**DP SIF (ifort2022_impilatest)** 내부:
```
/opt/ls-dyna/
├── lsdyna           → R16.1.1 (기본 symlink)
├── lsdyna_R16.1.1   → ls-dyna_mpp_d_R16_1_1_x64_centos79_ifort190_avx2_intelmpi-2018
├── lsdyna_R15.0.2   → ls-dyna_mpp_d_R15_0_2_x64_centos79_ifort190_avx2_intelmpi-2018
└── (R16.0.0, R16.1.0 없음 — DP SIF는 R15와 R16.1.1만)
```

**SP-Intel SIF (ifort2022_impilatest_s)** 내부:
```
/opt/ls-dyna/
├── lsdyna           → R16.1.1
├── lsdyna_R16.1.1   → ls-dyna_mpp_s_R16_1_1_x64_centos79_ifort190_avx2_intelmpi-2018
└── lsdyna_R15.0.2   → ls-dyna_mpp_s_R15_0_2_x64_centos79_ifort190_avx2_intelmpi-2018
```

#### 1.3.3 LS-DYNA 버전 선택

config.json의 `lsdyna_path` 필드로 버전 선택:

```json
"lsdyna_path": "/opt/ls-dyna/lsdyna_R16.1.1"    // R16.1.1 (기본, 권장)
"lsdyna_path": "/opt/ls-dyna/lsdyna_R16.1.0"    // R16.1.0 (SP SIF만)
"lsdyna_path": "/opt/ls-dyna/lsdyna_R16.0.0"    // R16.0.0 (SP SIF만)
"lsdyna_path": "/opt/ls-dyna/lsdyna_R15.0.2"    // R15.0.2
"lsdyna_path": "/opt/ls-dyna/lsdyna"             // SIF 기본값 (= R16.1.1)
```

**버전 호환성**:

| 버전 | SP SIF | DP SIF | SP-Intel SIF | 비고 |
|------|--------|--------|-------------|------|
| R16.1.1 | ✅ | ✅ | ✅ | **현재 사용 중**, 모든 SIF에 있음 |
| R16.1.0 | ✅ | ❌ | ❌ | SP SIF에만 |
| R16.0.0 | ✅ | ❌ | ❌ | SP SIF에만 |
| R15.0.2 | ✅ | ✅ | ✅ | 구버전, 모든 SIF에 있음 |

#### 1.3.4 MPI 환경 (SIF 내부)

**SP SIF — OpenMPI 4.0.5**:
```
/opt/openmpi/bin/mpirun     ← MPI 실행 파일
/opt/openmpi/lib/           ← MPI 라이브러리
```
- SLURM 통합: `--mca plm ^slurm --mca btl ^openib` 필수
- LD_LIBRARY_PATH: `/opt/openmpi/lib`

**DP SIF — Intel MPI 2021.17**:
```
/opt/intel/oneapi/mpi/2021.17/bin/mpirun   ← MPI 실행 파일
/opt/intel/oneapi/mpi/2021.17/lib/         ← MPI 라이브러리
/opt/intel/oneapi/mpi/2021.7.1/            ← 구버전 (미사용)
/opt/intel/oneapi/mpi/latest/              ← symlink → 2021.17
```
- SLURM 통합: `--mca` 인자 불필요 (Intel MPI는 자체 방식)
- `lsdyna_apptainer_mpiargs`: `""` (빈 문자열이어야 함!)
- FI_PROVIDER=tcp, I_MPI_FABRICS=ofi 환경변수 필요

#### 1.3.5 Apptainer 실행 구조

```
apptainer exec                    # 컨테이너 안에서 명령 실행
    --bind /data:/data            # Host /data → Container /data
    --bind /shared:/shared        # Host /shared → Container /shared
    --bind /host/LSTC_FILE:/opt/ls-dyna_license/LSTC_FILE  # 라이선스
    --env LSTC_FILE=...           # 환경변수
    --env FI_PROVIDER=tcp
    /opt/apptainers/XXX.sif       # SIF 이미지 경로
    <MPI command>                 # 컨테이너 내부에서 실행
        <LS-DYNA binary>          # 역시 컨테이너 내부 경로
        i=model.k memory=500m
```

**핵심 이해**:
1. `--bind`로 호스트 파일시스템을 컨테이너에 마운트
2. 모든 경로(`lsdyna_path`, `mpirun`, k-file 등)는 **컨테이너 내부 경로**
3. k-file이 `/data/` 아래에 있어야 bind mount를 통해 접근 가능
4. `/home/koopark/`는 bind되지 않으므로 컨테이너에서 접근 불가

#### 1.3.6 새 SIF 추가 시 config.json 작성법

새 Apptainer SIF를 빌드하거나 추가할 때:

```json
{
  "lsdyna_path": "<SIF 내부 LS-DYNA 바이너리 경로>",
  "ncpu": 2,
  "memory": "<precision에 따라: SP=2000m, DP=500m>",
  "partition": "normal",
  "lsdyna_apptainer_sif": "/opt/apptainers/<새 SIF 파일명>.sif",
  "lsdyna_apptainer_bind": "/data:/data,/shared:/shared<,추가 bind mount>",
  "lsdyna_apptainer_mpirun": "<SIF 내부 mpirun 경로>",
  "lsdyna_apptainer_mpiargs": "<OpenMPI면 --mca ..., Intel MPI면 빈 문자열>",
  "lsdyna_apptainer_env": {
    "LSTC_FILE": "/opt/ls-dyna_license/LSTC_FILE",
    "<MPI fabric 설정>": "<값>"
  }
}
```

**확인 명령**:
```bash
# SIF 내부 LS-DYNA 바이너리 확인
ssh node001 "apptainer exec /opt/apptainers/NEW.sif ls /opt/ls-dyna/"

# SIF 내부 MPI 확인
ssh node001 "apptainer exec /opt/apptainers/NEW.sif which mpirun"
ssh node001 "apptainer exec /opt/apptainers/NEW.sif ls /opt/intel/oneapi/mpi/"

# 테스트 실행 (인터랙티브)
ssh node001 "apptainer exec --bind /data:/data /opt/apptainers/NEW.sif \
    /opt/ls-dyna/lsdyna i=/data/test/model.k memory=100m"
```

### 1.4 라이선스

LS-DYNA 라이선스 파일은 bind mount로 컨테이너 내부에 매핑:
```
Host:      /data/level_study/_license/LSTC_FILE
Container: /opt/ls-dyna_license/LSTC_FILE
```

- SP SIF: bind 없이도 SIF 내장 라이선스로 동작 (경우에 따라)
- DP SIF: 반드시 외부 라이선스 bind mount 필요 → config의 `lsdyna_apptainer_bind`에 포함
- 라이선스 서버 IP: `192.168.122.1` (LSTC_FILE 내부에 기록)
- 라이선스 오류 시: "LSTC License file not found" 또는 hang (무한 대기)

---

## 2. 핵심 파일 3개

전체 제출 시스템은 **3개 파일**로 구성됨:

### 2.1 `run.sh` — 마스터 제출 스크립트

**위치**: `/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh`

**하는 일**:
1. config.json 파싱 (python3 json)
2. `slurm_dyna.sh` (SLURM batch script) 동적 생성
3. `sbatch` 제출
4. Job ID 출력

**사용법**:
```bash
bash /path/to/run.sh <input.k> [config.json]
```
- `input.k`: LS-DYNA 입력 파일 (절대경로 또는 상대경로)
- `config.json`: 생략 시 run.sh 디렉토리의 config.json 사용
- **작업 디렉토리** = input.k가 있는 폴더 (결과물도 여기에 생성)

**전체 소스** (116줄):
```bash
#!/bin/bash
set -e

INPUT_FILE="$1"
CONFIG_FILE="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/config.json}"

# 입력 검증
if [ -z "$INPUT_FILE" ]; then
    echo "사용법: $0 <input.k> [config.json]"
    exit 1
fi
[ -f "$INPUT_FILE" ] || { echo "오류: $INPUT_FILE 없음"; exit 1; }
[ -f "$CONFIG_FILE" ] || { echo "오류: $CONFIG_FILE 없음"; exit 1; }

INPUT_FILE="$(realpath "$INPUT_FILE")"
CONFIG_FILE="$(realpath "$CONFIG_FILE")"
WORK_DIR="$(dirname "$INPUT_FILE")"
INPUT_NAME="$(basename "$INPUT_FILE")"

# config.json 파싱 (python3 json)
LSDYNA_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['lsdyna_path'])")
NCPU=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('ncpu', 4))")
MEMORY=$(python3 -c "import json; mem=json.load(open('$CONFIG_FILE')).get('memory','2000m'); print(str(mem)+'m' if str(mem).isdigit() else str(mem))")
PARTITION=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('partition','normal'))")
SIF=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_sif',''))")
BIND=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_bind','/data:/data,/shared:/shared'))")
MPIRUN_CMD=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_mpirun','mpirun'))")
MPIRUN_ARGS=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_mpiargs','--mca plm ^slurm --mca btl ^openib'))")
ENV_ARGS=$(python3 -c "
import json
env = json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_env', {})
for k,v in env.items():
    print(f'--env {k}={v}', end=' ')
")

# slurm_dyna.sh 생성
SLURM_SCRIPT="$WORK_DIR/slurm_dyna.sh"
JOB_NAME="dyna_${INPUT_NAME%.*}"

cat > "$SLURM_SCRIPT" << SLURM_EOF
#!/bin/bash
#SBATCH --job-name=$JOB_NAME
#SBATCH --partition=$PARTITION
#SBATCH --ntasks=$NCPU
#SBATCH --nodes=1
#SBATCH --output=$WORK_DIR/slurm_%j.out
#SBATCH --error=$WORK_DIR/slurm_%j.err
#SBATCH --chdir=$WORK_DIR

apptainer exec --bind $BIND \\
    $ENV_ARGS $SIF \\
    $MPIRUN_CMD $MPIRUN_ARGS -np $NCPU \\
    $LSDYNA_PATH i=$INPUT_NAME memory=$MEMORY
SLURM_EOF

chmod +x "$SLURM_SCRIPT"
JOB_ID=$(sbatch "$SLURM_SCRIPT" | awk '{print $NF}')
echo "Job 제출 완료: $JOB_ID"
echo "상태 확인: squeue -j $JOB_ID"
echo "로그: $WORK_DIR/slurm_${JOB_ID}.out"
```

### 2.2 `config.json` — 솔버 환경 설정

**Explicit (Single Precision)** — 일반 explicit dynamics:
```json
{
  "lsdyna_path": "/opt/ls-dyna/lsdyna_R16.1.1",
  "mpi_path": "mpirun",
  "ncpu": 2,
  "memory": "2000m",
  "partition": "normal",
  "lsdyna_apptainer_sif": "/opt/apptainers/LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif",
  "lsdyna_apptainer_bind": "/data:/data,/shared:/shared",
  "lsdyna_apptainer_env": {
    "LSTC_FILE": "/opt/ls-dyna_license/LSTC_FILE",
    "FI_PROVIDER": "tcp",
    "I_MPI_FABRICS": "ofi",
    "LD_LIBRARY_PATH": "/opt/openmpi/lib"
  }
}
```

**Implicit (Double Precision)** — eigenvalue, CMS, implicit dynamics:
```json
{
  "lsdyna_path": "/opt/ls-dyna/lsdyna_R16.1.1",
  "mpi_path": "/opt/intel/oneapi/mpi/2021.17/bin/mpirun",
  "ncpu": 2,
  "memory": "500m",
  "partition": "normal",
  "lsdyna_apptainer_sif": "/opt/apptainers/LSDynaBasic_ifort2022_impilatest_mpp_d.sif",
  "lsdyna_apptainer_bind": "/data:/data,/shared:/shared,/data/level_study/_license/LSTC_FILE:/opt/ls-dyna_license/LSTC_FILE",
  "lsdyna_apptainer_mpirun": "/opt/intel/oneapi/mpi/2021.17/bin/mpirun",
  "lsdyna_apptainer_mpiargs": "",
  "lsdyna_apptainer_env": {
    "LSTC_FILE": "/opt/ls-dyna_license/LSTC_FILE",
    "FI_PROVIDER": "tcp",
    "I_MPI_FABRICS": "ofi"
  }
}
```

**SP vs DP 차이점 (Apptainer 관점 포함)**:

| 항목 | Single Precision (SP) | Double Precision (DP) |
|------|----------------------|----------------------|
| **SIF** | `LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif` | `LSDynaBasic_ifort2022_impilatest_mpp_d.sif` |
| **컴파일러** | AOCC 4.2.0 (AMD) | ifort 2022 (Intel) |
| **SIF 크기** | 973 MB | 1.48 GB |
| **MPI** | OpenMPI 4.0.5 | Intel MPI 2021.17 |
| **SIF 내 MPI 경로** | `/opt/openmpi/bin/mpirun` (또는 `mpirun`) | `/opt/intel/oneapi/mpi/2021.17/bin/mpirun` |
| **mpiargs** | `--mca plm ^slurm --mca btl ^openib` | `""` (빈 문자열 — Intel MPI는 --mca 불가!) |
| **memory** | `2000m` (8 bytes/word → 16 GB) | `500m` (16 bytes/word → 8 GB) |
| **bind** | `/data:/data,/shared:/shared` | + `/data/level_study/_license/LSTC_FILE:/opt/ls-dyna_license/LSTC_FILE` |
| **환경변수** | + `LD_LIBRARY_PATH=/opt/openmpi/lib` | (불필요) |
| **포함 버전** | R15.0.2, R16.0.0, R16.1.0, **R16.1.1** | R15.0.2, **R16.1.1** |
| **기본 lsdyna** | → R16.1.1 | → R16.1.1 |

**흔한 실수**:
- DP SIF에 OpenMPI `--mca` 인자 전달 → 에러 (Intel MPI는 --mca 모름)
- SP SIF로 implicit 실행 → Error 60022 (DP 필요)
- DP SIF에 `memory=2000m` → OOM (16 bytes/word × 2000M = 32 GB > 노드 RAM)
- SP SIF의 d3eigv를 DP SIF에서 읽기 → 정밀도 불일치 (반대도 동일)

**config.json 필드 상세**:

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `lsdyna_path` | string | ✅ | — | 컨테이너 내부 LS-DYNA 바이너리 경로 |
| `ncpu` | int | — | 4 | MPI 프로세스 수 (이 클러스터: 2 고정) |
| `memory` | string | — | "2000m" | LS-DYNA 메모리. 숫자만 쓰면 m 자동 추가 |
| `partition` | string | — | "normal" | SLURM 파티션 |
| `lsdyna_apptainer_sif` | string | ✅ | — | Apptainer SIF 절대경로 |
| `lsdyna_apptainer_bind` | string | — | "/data:/data,/shared:/shared" | Bind mount |
| `lsdyna_apptainer_mpirun` | string | — | "mpirun" | MPI 실행 파일 경로 |
| `lsdyna_apptainer_mpiargs` | string | — | "--mca plm ^slurm ..." | MPI 추가 인자 |
| `lsdyna_apptainer_env` | object | — | {} | 환경변수 key-value |

### 2.3 `run_all.sh` 또는 Python orchestrator — 일괄 제출

**패턴 A: 단순 루프 (Example 09, 143건)**
```bash
#!/bin/bash
set -e
OUTPUT_BASE="/data/my_study"
RUN_SH="/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh"
CONFIG="$(dirname $0)/config.json"
KFILE_DIR="$(dirname $0)/kfiles"

for kfile_path in "$KFILE_DIR"/*.k; do
    name="$(basename "${kfile_path%.k}")"
    mkdir -p "$OUTPUT_BASE/$name"
    cp "$kfile_path" "$OUTPUT_BASE/$name/"
    bash "$RUN_SH" "$OUTPUT_BASE/$name/$(basename $kfile_path)" "$CONFIG"
    sleep 1
done
```

**패턴 B: 선택적 제출 (Example 13, phase별)**
```bash
#!/bin/bash
RUN_SH="/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh"
CONFIG_SP="$(dirname $0)/config_explicit.json"
CONFIG_DP="$(dirname $0)/config_implicit.json"
DATA_DIR="/data/my_study"

submit_job() {
    local kfile="$1" config="$2" workdir="$3"
    mkdir -p "$workdir"
    cp "$kfile" "$workdir/"
    (cd "$workdir" && bash "$RUN_SH" "$(basename $kfile)" "$config")
}

case "$1" in
    phase0) submit_job "kfiles/phase0.k" "$CONFIG_SP" "$DATA_DIR/phase_0" ;;
    phase1) submit_job "kfiles/phase1.k" "$CONFIG_DP" "$DATA_DIR/phase_1" ;;
    *) echo "Usage: $0 {phase0|phase1}" ;;
esac
```

**패턴 C: Python 기반 (DOE, 동적 파라미터)**
```python
import os, subprocess, shutil

DATA_DIR = "/data/my_study"
RUN_SH = "/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh"

def submit(kfile_path, config_path, work_dir):
    """제출 후 Job ID 반환."""
    os.makedirs(work_dir, exist_ok=True)
    shutil.copy2(kfile_path, work_dir)
    kname = os.path.basename(kfile_path)
    r = subprocess.run(
        ["bash", RUN_SH, kname, config_path],
        cwd=work_dir, capture_output=True, text=True
    )
    # Job ID 파싱
    for line in r.stdout.splitlines():
        if "squeue -j" in line:
            return line.split("-j")[1].strip()
    return None
```

---

## 3. 제출 절차 (Step by Step)

### 3.1 새 프로젝트 셋업

```bash
# 1. /data/ 하위에 프로젝트 디렉토리 생성
mkdir -p /data/my_project/case_001

# 2. k-file을 해당 디렉토리에 복사
cp /path/to/model.k /data/my_project/case_001/

# 3. config.json 준비 (적절한 템플릿 복사)
#    - Explicit: config_explicit.json
#    - Implicit: config_implicit.json
cp config_explicit.json /data/my_project/case_001/config.json

# 4. 제출
bash /home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh \
    /data/my_project/case_001/model.k \
    /data/my_project/case_001/config.json
```

### 3.2 제출 후 디렉토리 구조

```
/data/my_project/case_001/
├── model.k              # 입력 파일
├── config.json          # 솔버 설정
├── slurm_dyna.sh        # run.sh가 자동 생성한 SLURM 스크립트
├── slurm_12345.out      # SLURM stdout (LS-DYNA 출력)
├── slurm_12345.err      # SLURM stderr
├── d3hsp               # LS-DYNA 로그 (에러/경고 확인)
├── d3plot              # 가시화 결과
├── binout              # 시계열 데이터 (glstat, matsum 등)
├── d3eigv              # (implicit eigenvalue 시) 고유모드
├── d3mode              # (CMS 시) CMS 모드
├── glstat              # 에너지 히스토리 (ASCII)
├── rcforc              # 접촉력 히스토리
├── eigout              # (eigenvalue 시) 고유값 목록
└── messag              # MPI 메시지 로그
```

### 3.3 job 모니터링

```bash
# 내 모든 job 확인
squeue -u $(whoami)

# 특정 job 상태
squeue -j 12345

# 실시간 로그 보기
tail -f /data/my_project/case_001/slurm_12345.out

# job 취소
scancel 12345

# 완료된 job 히스토리
sacct -j 12345 --format=JobID,State,ExitCode,Elapsed,MaxRSS
```

### 3.4 결과 확인 체크리스트

```bash
# 1. 정상 종료 확인
grep "N o r m a l    t e r m i n a t i o n" d3hsp && echo "OK" || echo "ABNORMAL"

# 2. 에러 확인
grep "E r r o r" d3hsp

# 3. 출력 파일 존재 확인
ls -la binout d3plot d3hsp

# 4. OOM 확인 (SIGNAL 9 = Killed)
grep -i "signal\|killed\|oom" slurm_*.err slurm_*.out

# 5. 시뮬레이션 완료 시간 확인
grep "termination time" d3hsp
```

---

## 4. Python에서 자동화하기

### 4.1 최소 제출 함수

```python
import os
import subprocess
import shutil
import json
import time

RUN_SH = "/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh"

def submit_job(kfile_path, config_path, work_dir):
    """k-file을 work_dir로 복사하고 SLURM 제출. Job ID 반환."""
    os.makedirs(work_dir, exist_ok=True)

    # k-file 복사
    kname = os.path.basename(kfile_path)
    dst = os.path.join(work_dir, kname)
    if os.path.abspath(kfile_path) != os.path.abspath(dst):
        shutil.copy2(kfile_path, dst)

    # config.json도 work_dir에 복사 (run.sh가 realpath로 읽으므로 어디든 OK)
    cfg_dst = os.path.join(work_dir, "config.json")
    shutil.copy2(config_path, cfg_dst)

    # 제출
    result = subprocess.run(
        ["bash", RUN_SH, kname, "config.json"],
        cwd=work_dir,
        capture_output=True, text=True
    )

    # Job ID 파싱
    job_id = None
    for line in result.stdout.splitlines():
        if "squeue -j" in line:
            job_id = line.split("-j")[-1].strip()
            break

    if job_id is None:
        print(f"WARNING: Job ID not found. stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

    return job_id
```

### 4.2 Job 완료 대기

```python
def wait_for_job(job_id, poll_interval=10, timeout=3600):
    """SLURM job 완료까지 대기. 상태 반환."""
    start = time.time()
    while time.time() - start < timeout:
        r = subprocess.run(
            ["squeue", "-j", str(job_id), "-h", "-o", "%T"],
            capture_output=True, text=True
        )
        state = r.stdout.strip()
        if state == "":
            # Job이 squeue에서 사라짐 = 완료
            # sacct로 최종 상태 확인
            r2 = subprocess.run(
                ["sacct", "-j", str(job_id), "--format=State", "-n", "-P"],
                capture_output=True, text=True
            )
            final = r2.stdout.strip().split("\n")[0] if r2.stdout.strip() else "UNKNOWN"
            return final  # "COMPLETED", "FAILED", "CANCELLED", "OUT_OF_ME+"
        time.sleep(poll_interval)
    return "TIMEOUT"
```

### 4.3 d3hsp 파싱

```python
import re

def check_termination(work_dir):
    """d3hsp에서 정상 종료 여부 확인."""
    d3hsp = os.path.join(work_dir, "d3hsp")
    if not os.path.exists(d3hsp):
        return {"status": "NO_D3HSP", "normal": False}

    text = open(d3hsp).read()
    result = {
        "normal": "N o r m a l    t e r m i n a t i o n" in text,
        "has_error": "E r r o r" in text,
        "errors": [],
    }

    # 에러 메시지 추출
    for m in re.finditer(r'\*\*\* Error (\d+).*', text):
        result["errors"].append(m.group(0))

    # 종료 시간
    m = re.search(r'termination time\s*=?\s*([\d.eE+-]+)', text, re.I)
    if m:
        result["end_time"] = float(m.group(1))

    return result
```

### 4.4 Binout 읽기 (COR 계산)

```python
import numpy as np

def read_binout_cor(work_dir, t_start=2.0, t_end=5.0):
    """binout에서 COR 계산."""
    try:
        from lasso.dyna import Binout
    except ImportError:
        from qd.cae.dyna import Binout

    b = Binout(os.path.join(work_dir, "binout"))
    t = b.read('glstat', 'time')
    ke = b.read('glstat', 'kinetic_energy')
    te = b.read('glstat', 'total_energy')

    ke_init = ke[ke > 0][0]
    mask = (t > t_start) & (t < t_end)
    cor = float(np.sqrt(np.mean(ke[mask]) / ke_init))

    te_drift = float((te[-1] - te[1]) / te[1] * 100) if te[1] != 0 else 0.0

    return {"cor": cor, "ke_init": float(ke_init), "te_drift_pct": te_drift}
```

### 4.5 일괄 제출+대기+분석 파이프라인

```python
def run_batch(cases, config_path, poll_interval=15):
    """
    cases: list of dict with keys: name, kfile_path, work_dir
    Returns: list of result dicts
    """
    # 1. 모든 job 제출
    jobs = []
    for case in cases:
        job_id = submit_job(case["kfile_path"], config_path, case["work_dir"])
        jobs.append({"name": case["name"], "job_id": job_id, "work_dir": case["work_dir"]})
        print(f"  Submitted {case['name']}: Job {job_id}")
        time.sleep(1)  # SLURM 부하 방지

    # 2. 모든 job 완료 대기
    print(f"\nWaiting for {len(jobs)} jobs...")
    results = []
    for job in jobs:
        state = wait_for_job(job["job_id"], poll_interval=poll_interval)
        term = check_termination(job["work_dir"])
        result = {
            "name": job["name"],
            "job_id": job["job_id"],
            "slurm_state": state,
            "normal_termination": term.get("normal", False),
            "errors": term.get("errors", []),
        }

        # COR 계산 (가능한 경우)
        if term.get("normal"):
            try:
                cor_data = read_binout_cor(job["work_dir"])
                result.update(cor_data)
            except Exception as e:
                result["cor_error"] = str(e)

        results.append(result)
        status = "OK" if term.get("normal") else state
        print(f"  {job['name']}: {status}")

    return results
```

---

## 5. 반복 제출 시 주의사항

### 5.1 재실행 전 기존 출력 정리

LS-DYNA는 기존 출력 파일이 있으면 **덮어쓰기** 또는 **append** 함.
깨끗한 재실행을 위해:

```bash
# 특정 케이스 정리
cd /data/my_project/case_001
rm -f d3plot* d3hsp d3eigv d3mode binout* glstat matsum rcforc \
      sleout nodout messag eigout status.out adptmp d3dump* scr*

# 또는 k-file과 config만 남기고 전부 삭제
cd /data/my_project/case_001
find . -maxdepth 1 ! -name "*.k" ! -name "config.json" ! -name "run.sh" \
       ! -name "." -exec rm -f {} +
```

Python 함수:
```python
def clean_work_dir(work_dir, keep_patterns=("*.k", "config.json")):
    """LS-DYNA 출력 파일 정리. k-file과 config만 유지."""
    import glob
    keep_files = set()
    for pat in keep_patterns:
        keep_files.update(glob.glob(os.path.join(work_dir, pat)))

    for f in os.listdir(work_dir):
        fp = os.path.join(work_dir, f)
        if os.path.isfile(fp) and fp not in keep_files:
            os.remove(fp)
```

### 5.2 동시 실행 제한

- 클러스터에 **2 노드 × 1 job/node = 최대 2 동시 job**
- 3개 이상 제출하면 대기열(PENDING)에 들어감
- 대량 DOE 시 sleep 1~2초 간격으로 제출하면 SLURM 부하 방지

### 5.3 메모리 설정 가이드

| 솔버 | 모델 규모 | memory 값 | 비고 |
|------|---------|-----------|------|
| SP explicit | ~5K 요소 | 500m | 작은 모델 |
| SP explicit | ~50K 요소 | 2000m | 기본 |
| SP explicit | ~200K+ 요소 | 3000m | 최대 (integer overflow 주의) |
| DP implicit | ~5K 요소 | 300m | 모드 추출 |
| DP implicit | ~50K 요소 | 500m | 기본 |
| DP explicit (CMS) | NMFB<500 | 500m | CMS FRB |
| DP explicit (CMS) | NMFB 500~800 | 800m~1000m | 메모리 집약 |
| DP explicit (CMS) | NMFB>800 | OOM 위험 | 이 클러스터에서 불가 |

**DP memory 계산**: `memory_words × 16 bytes = 실제 RAM 사용`
- 500m → 500M × 16 = 8 GB
- 1000m → 1000M × 16 = 16 GB (노드 RAM 초과 → OOM)

### 5.4 에러 디버깅 흐름

```
Job FAILED?
├── slurm_*.err에 "Killed" / "SIGNAL 9" → OOM
│   └─ Fix: memory 줄이기 (DP) 또는 모델 축소
├── d3hsp에 "E r r o r" → LS-DYNA 에러
│   ├─ Error 10246 → k-file 포맷 오류 (필드 폭, 카드 누락)
│   ├─ Error 60022 → implicit에 single precision 사용
│   ├─ Error 60083 → EIGENVALUE + MODES 동시 사용
│   └─ Error 20459 → LOAD_BODY_Z LCID=0
├── d3hsp에 "Warning" → 대부분 무시 가능, 단 에너지 확인
├── 정상종료인데 결과 이상 → 에너지 그래프 확인
│   ├─ TE 발산 → TSSFAC 줄이기
│   ├─ KE=0 (접촉 없음) → CONTACT SSTYP 확인
│   └─ 반중력 → LOAD_BODY_Z SF 부호 확인
└── slurm_*.out 빈 파일 → SIF 경로 또는 라이선스 문제
```

---

## 6. 자주 쓰는 SLURM 명령 요약

```bash
# 제출
sbatch slurm_dyna.sh                    # 직접 제출
bash run.sh model.k config.json         # run.sh 통해 제출

# 모니터링
squeue                                   # 전체 대기열
squeue -u $(whoami)                      # 내 job만
squeue -j 12345                          # 특정 job
squeue -p normal                         # 특정 파티션

# 로그
tail -f slurm_12345.out                  # 실시간 로그
tail -20 slurm_12345.err                 # 에러 마지막 20줄

# 제어
scancel 12345                            # 특정 job 취소
scancel -u $(whoami)                     # 내 모든 job 취소

# 히스토리
sacct -j 12345 --format=JobID,State,ExitCode,Elapsed,MaxRSS
sacct --starttime=2026-02-26 -u $(whoami) --format=JobID,JobName,State,Elapsed
```

---

## 7. 파일 위치 요약

| 파일 | 경로 | 설명 |
|------|------|------|
| **run.sh** | `/home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh` | 마스터 제출 스크립트 |
| **기본 config** | `.../DynaJobSubmit/config.json` | SP 기본 설정 |
| **SP 템플릿** | `Examples/13_cms_study/config_explicit.json` | 검증된 SP 설정 |
| **DP 템플릿** | `Examples/13_cms_study/config_implicit.json` | 검증된 DP 설정 |
| **SIF (SP)** | `/opt/apptainers/LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif` | compute node |
| **SIF (DP)** | `/opt/apptainers/LSDynaBasic_ifort2022_impilatest_mpp_d.sif` | compute node |
| **라이선스** | `/data/level_study/_license/LSTC_FILE` | 라이선스 파일 |
| **데이터 루트** | `/data/` | 모든 시뮬레이션 데이터 |

---

## 8. 빠른 시작 예제

### 8.1 단일 job 제출 (bash)

```bash
# 디렉토리 생성 + k-file 복사
mkdir -p /data/test_run/case01
cp my_model.k /data/test_run/case01/

# SP explicit 제출
bash /home/koopark/claude/KooVirtualMaterialGenerator/DynaJobSubmit/run.sh \
    /data/test_run/case01/my_model.k \
    /home/koopark/claude/KooVirtualMaterialGenerator/Examples/13_cms_study/config_explicit.json

# 결과 확인
tail -f /data/test_run/case01/slurm_*.out
grep "N o r m a l" /data/test_run/case01/d3hsp
```

### 8.2 반복 DOE (Python)

```python
#!/usr/bin/env python3
"""Example: Parameter DOE with automatic submission."""
import os, time

# 위의 submit_job, wait_for_job, check_termination 함수 import

CONFIG = "/path/to/config_explicit.json"
BASE_DIR = "/data/my_doe"

# DOE 파라미터
cases = []
for param_value in [0.1, 0.2, 0.5, 1.0, 2.0]:
    name = f"case_{param_value:.1f}"
    work_dir = os.path.join(BASE_DIR, name)
    kfile = os.path.join(work_dir, f"{name}.k")

    # k-file 생성 (여기에 param_value 반영)
    generate_kfile(kfile, param_value)  # 사용자 정의 함수

    cases.append({"name": name, "kfile_path": kfile, "work_dir": work_dir})

# 일괄 제출 + 대기 + 분석
results = run_batch(cases, CONFIG)

# 결과 출력
for r in results:
    print(f"{r['name']}: COR={r.get('cor','N/A'):.3f}, "
          f"State={r['slurm_state']}, Normal={r['normal_termination']}")
```

---

*Document generated: 2026-02-26*
*Verified with: Examples 02, 06, 08, 09, 12, 13, 14 (수백 건 제출 이력)*
