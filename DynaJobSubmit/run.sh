#!/bin/bash
# LS-DYNA 단순 Slurm Job 제출 스크립트
#
# 사용법: ./run.sh /path/to/input.k [config.json]
#
# 입력 파일이 있는 폴더에서 LS-DYNA를 실행하여
# 결과 파일(d3plot, dynain 등)이 해당 폴더에 직접 생성됨

set -e

INPUT_FILE="$1"
CONFIG_FILE="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/config.json}"

# 입력 파일 검증
if [ -z "$INPUT_FILE" ]; then
    echo "사용법: $0 <input.k> [config.json]"
    echo ""
    echo "  input.k      LS-DYNA 입력 파일 경로"
    echo "  config.json   환경 설정 파일 (기본: 스크립트 디렉토리의 config.json)"
    echo ""
    echo "결과 파일은 입력 파일이 있는 폴더에 생성됩니다."
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "오류: 입력 파일을 찾을 수 없습니다: $INPUT_FILE"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "오류: 설정 파일을 찾을 수 없습니다: $CONFIG_FILE"
    exit 1
fi

INPUT_FILE="$(realpath "$INPUT_FILE")"
CONFIG_FILE="$(realpath "$CONFIG_FILE")"
WORK_DIR="$(dirname "$INPUT_FILE")"
INPUT_NAME="$(basename "$INPUT_FILE")"

# config.json 파싱
LSDYNA_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['lsdyna_path'])")
MPI_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('mpi_path','/opt/ompi4.0.5'))")
NCPU=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('ncpu', 4))")
MEMORY=$(python3 -c "import json; mem=json.load(open('$CONFIG_FILE')).get('memory','2000m'); print(str(mem)+'m' if str(mem).isdigit() else str(mem))")
PARTITION=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('partition','normal'))")
# SIF and BIND from apptainer settings
SIF=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_sif','$LSDYNA_PATH'))")
BIND=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_bind','/data:/data,/shared:/shared'))")

# MPI 실행 경로 및 인자 (Intel MPI / OpenMPI 호환)
MPIRUN_CMD=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_mpirun','mpirun'))")
MPIRUN_ARGS=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_mpiargs','--mca plm ^slurm --mca btl ^openib'))")

# Apptainer 환경변수 구성
ENV_ARGS=$(python3 -c "
import json
env = json.load(open('$CONFIG_FILE')).get('lsdyna_apptainer_env', {})
for k,v in env.items():
    print(f'--env {k}={v}', end=' ')
")

# Slurm 스크립트 생성
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

echo "=== LS-DYNA Job Start ==="
echo "Input: $INPUT_FILE"
echo "WorkDir: $WORK_DIR"
echo "CPUs: $NCPU"
echo "Memory: $MEMORY"
date

apptainer exec --bind $BIND \\
    --env LSTC_FILE=/opt/ls-dyna_license/LSTC_FILE \\
    --env FI_PROVIDER=tcp \\
    --env I_MPI_FABRICS=ofi \\
    $ENV_ARGS $SIF \\
    $MPIRUN_CMD $MPIRUN_ARGS -np $NCPU \\
    /opt/ls-dyna/lsdyna_R16.1.1 i=$INPUT_NAME memory=$MEMORY

echo "=== LS-DYNA Job End ==="
date
SLURM_EOF

chmod +x "$SLURM_SCRIPT"

# 제출
echo "=========================================="
echo "LS-DYNA Job 제출"
echo "=========================================="
echo "입력 파일: $INPUT_FILE"
echo "작업 디렉토리: $WORK_DIR"
echo "CPU: $NCPU"
echo "메모리: $MEMORY"
echo "파티션: $PARTITION"
echo "MPI: $MPIRUN_CMD"
echo ""

JOB_ID=$(sbatch "$SLURM_SCRIPT" | awk '{print $NF}')

echo "Job 제출 완료: $JOB_ID"
echo ""
echo "상태 확인: squeue -j $JOB_ID"
echo "로그: $WORK_DIR/slurm_${JOB_ID}.out"
echo "취소: scancel $JOB_ID"
