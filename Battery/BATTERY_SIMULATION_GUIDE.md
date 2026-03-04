# Li-ion Pouch Cell LS-DYNA Crush Simulation Guide

> LS-DYNA R16.1.1 | AOCC 4.20 + OpenMPI 4.0.5 | Apptainer on SLURM
> Last validated: 2026-03-04

이 문서는 Phase 1 ~ Phase 3 디버깅 과정에서 얻어진 모든 핵심 정보를 정리한 것입니다.
새로운 배터리 모델링 시 AI와 사람이 모두 참조할 수 있도록 작성되었습니다.

---

## 목차

1. [시뮬레이션 개요](#1-시뮬레이션-개요)
2. [요소 정의](#2-요소-정의)
3. [재료 정의](#3-재료-정의)
4. [접촉 정의](#4-접촉-정의)
5. [경계조건 및 하중](#5-경계조건-및-하중)
6. [솔버 제어 파라미터](#6-솔버-제어-파라미터)
7. [Phase별 차이점](#7-phase별-차이점)
8. [실행 환경](#8-실행-환경)
9. [디버깅 이력 및 해결된 에러](#9-디버깅-이력-및-해결된-에러)
10. [핵심 교훈 (Lessons Learned)](#10-핵심-교훈-lessons-learned)

---

## 1. 시뮬레이션 개요

### 1.1 모델 구성

```
Impactor (Steel, MAT_ELASTIC)
    ↓ V = -1000 mm/s
┌────────────────────────┐
│ Pouch (Al-laminate)    │ ← Convection + Radiation (Phase 2+)
│ ┌────────────────────┐ │
│ │ PCM Board (Pos)    │ │
│ │ Al Tab (Pos)       │ │
│ │ ┌────────────────┐ │ │
│ │ │ Unit Cell × N  │ │ │  ← Stacked: N = 3~20 layers
│ │ │  Al CC         │ │ │     Wound: Spiral jellyroll
│ │ │  NMC Cathode   │ │ │
│ │ │  PE Separator  │ │ │
│ │ │  Graphite Anode│ │ │
│ │ │  Cu CC         │ │ │
│ │ └────────────────┘ │ │
│ │ Cu Tab (Neg)       │ │
│ │ PCM Board (Neg)    │ │
│ └────────────────────┘ │
│ Pouch Bottom           │ ← SPC (All DOF fixed)
└────────────────────────┘
```

### 1.2 Phase 구성

| Phase | 해석 유형 | 종료 시간 | 바이너리 | 목적 |
|-------|----------|----------|---------|------|
| 1 | 순수 구조 (Mechanical) | 5 ms | SP | 크러시 거동 검증 |
| 2 | 구조+열 (Thermo-Mechanical) | 10 ms | **DP 필수** | 열 발생/전도 검증 |
| 3 | 구조+열+EM | **0.01 s** | DP | 전기화학-열-기계 완전 커플링 (**tier -1 완료**) |

> **Phase 3 검증 완료 (2026-03-04)**: Stacked 5UC×435circuits, Wound 1UC×4011circuits,
> All-SOLID mesh 필수 (EM solver + TSHELL = segfault, 아래 §9.4 참조)

### 1.3 Tier 구성

| Tier | 요소 크기 | 요소 수 (Stacked) | 파일 크기 | 용도 |
|------|----------|------------------|----------|------|
| -1 | 5 mm | ~13,000 | ~2 MB | 디버깅용 (키워드 검증) |
| 0 | 2.5 mm | ~50,000 | ~10 MB | 중간 검증 |
| 1 | 1 mm | ~1,100,000 | ~180 MB | 본 해석 |

---

## 2. 요소 정의

### 2.1 Section 정의

**Phase 1/2 (구조/열-기계):**

| SID | 키워드 | ELFORM | 적용 대상 | 비고 |
|-----|--------|--------|----------|------|
| 1 | SECTION_SHELL | 2 (Belytschko-Tsay) | Al CC, Cu CC (Stacked), Pouch | NIP=5, QR=0.833 |
| 2 | SECTION_SHELL | 16 (Fully integrated) | PE Separator (Stacked) | NIP=5, 안정성 우선 |
| 3 | **SECTION_TSHELL** | **1 (Reduced integration)** | NMC Cathode, Graphite Anode, Electrolyte | **반드시 ELFORM=1** |
| 4 | SECTION_SOLID | 1 | Impactor, PCM Boards | 8-node brick |
| 5 | SECTION_TSHELL | 1 | Electrolyte Fill (Wound only) | Wound 코어 채움 |
| 6 | SECTION_SHELL | 2 | Pouch Side (Wound) | |

**Phase 3 추가 (EM 커플링 — All-SOLID 필수):**

| SID | 키워드 | ELFORM | 적용 대상 | 비고 |
|-----|--------|--------|----------|------|
| 3 | **SECTION_SOLID** | **1 (8-node hex)** | Al CC, NMC, Sep, Graphite, Cu CC | **TSHELL 대체 — EM segfault 방지** |

> **EM_RANDLES_SOLID 요구사항**: CCP/PEL/SEP/NEL/CCN 5개 층 모두 SOLID 요소여야 함.
> TSHELL 사용 시 `em_BP_fillRandleCircuit`이 0 circuits를 반환하거나 segfault 발생 (§9.4 참조).

### 2.2 TSHELL ELFORM=1을 사용해야 하는 이유

- **ELFORM=5 (Fully integrated)**: 93% 압축 시점에서 요소 역전(inversion)으로 크래시
- **ELFORM=1 (Reduced integration)**: 극심한 변형에도 안정적
- ELFORM=1은 "extruded thin shell" 타입 — z방향 강성이 비연결(uncoupled)
- 크러시 해석에서는 dt가 in-plane 치수에 의존하므로 두께 방향 압축 시에도 dt 급락 방지

> **주의**: ELFORM=1 + Gaussian quadrature일 때 NIP=2는 자동으로 NIP=3으로 변경됨
> (Warning 21287: "formulation 1 does not allow 2 or 4 integration points")

### 2.3 Hourglass 설정 (Per-Part)

| HGID | IHQ | QH | 적용 대상 |
|------|-----|-----|----------|
| 1 | 6 (Belytschko-Bindeman) | 0.05 | TSHELL, SOLID (electrode, impactor) |
| 2 | 4 (Flanagan-Belytschko viscous) | 0.05 | SHELL (CC foils, pouch) |
| 0 | Global default (IHQ=1, QH=0.10) | | Separator, PCM 등 |

---

## 3. 재료 정의

### 3.1 구조 재료

| MID | 이름 | MAT 타입 | 주요 파라미터 | Erosion |
|-----|------|---------|-------------|---------|
| 1 | Al CC | MAT_015 (Johnson-Cook) | A,B,N,C,M, TM, D1-D5=0 | MAT_ADD_EROSION MXEPS=0.4 |
| 2 | Cu CC | MAT_015 (Johnson-Cook) | A=200, B=292, N=0.31, C=0.025 | MAT_ADD_EROSION MXEPS=0.4 |
| 3 | NMC Cathode | MAT_024 (Piecewise Linear) | FAIL=0.3, LCSS=1001 (crush curve) | 내장 FAIL |
| 4 | Graphite Anode | MAT_024 (Piecewise Linear) | FAIL=0.3, LCSS=1002 (crush curve) | 내장 FAIL |
| 5 | PE Separator | MAT_024 | FAIL=0.3, CS_C=100, CS_P=4 | 내장 FAIL |
| 6 | Pouch (Al-lam) | MAT_024 | FAIL=0.4, CS_C=6500, CS_P=4 | 내장 FAIL |
| 7 | Impactor (Steel) | MAT_001 (Elastic) | E, PR만 사용 | 없음 |
| 8 | Electrolyte | MAT_001 (Elastic) | 등방 탄성 | MAT_ADD_EROSION MXEPS=0.1 |

> **주의**: Impactor는 MAT_RIGID가 아닌 **MAT_ELASTIC** 사용 (사용자 요구)
> INITIAL_VELOCITY로 속도 부여, BOUNDARY_PRESCRIBED_MOTION 미사용

### 3.2 열 재료 (Phase 2+)

TMID = MID + 100 규칙. **Phase 2에서는 모든 파트에 TMID > 0 필수.**

| TMID | 이름 | MAT 타입 | HC (J/kg·K) | TC (W/mm·K) | 비고 |
|------|------|---------|------------|------------|------|
| 101 | Al CC | THERMAL_ISOTROPIC | YAML | YAML | |
| 102 | Cu CC | THERMAL_ISOTROPIC | YAML | YAML | |
| 103 | NMC Cathode | **THERMAL_ORTHOTROPIC** | 700 | K1,K2=0.003, K3=0.0015 | 이방성 |
| 104 | Graphite Anode | **THERMAL_ORTHOTROPIC** | 700 | K1,K2=0.005, K3=0.002 | 이방성 |
| 105 | PE Separator | THERMAL_ISOTROPIC | YAML | YAML | TLAT=403K, HLAT=145kJ/kg (상변화) |
| 106 | Pouch | THERMAL_ISOTROPIC | YAML | YAML | |
| 107 | Rigid (Steel) | THERMAL_ISOTROPIC | 477 | 0.0519 | Impactor, PCM, Tab용 |
| 108 | Electrolyte | THERMAL_ISOTROPIC | YAML | YAML | |

### 3.3 온도 의존 크러시 커브

TABLE + DEFINE_CURVE 구조. **반드시 CURVE를 먼저, TABLE을 나중에 작성.**

```
*DEFINE_CURVE
$   LCID=4031   (NMC @ 298K, scale=1.0)
*DEFINE_CURVE
$   LCID=4032   (NMC @ 373K, scale=0.7)
*DEFINE_CURVE
$   LCID=4033   (NMC @ 473K, scale=0.4)
*DEFINE_TABLE
$   TBID=4003   (NMC crush vs T)
$   298.0  → LCID 4031
$   373.0  → LCID 4032
$   473.0  → LCID 4033
```

> **중요**: TABLE이 참조하는 CURVE보다 먼저 나오면 LS-DYNA 파싱 에러 발생.
> `generate_materials.py`에서 CURVE → TABLE 순서 엄수.

### 3.4 열팽창 계수 (CTE)

Phase 2+ 메시에 `*MAT_THERMAL_CTE_LOAD_CURVE_COMP` 또는 직접 CTE 적용:

| MID | 재료 | CTE (1/K) |
|-----|------|-----------|
| 1 | Al | 23.1e-6 |
| 2 | Cu | 16.5e-6 |
| 3 | NMC | 5.0e-6 |
| 4 | Graphite | 3.0e-6 |
| 5 | Separator | 200.0e-6 |
| 6 | Pouch | 23.0e-6 |
| 8 | Electrolyte | 100.0e-6 |

---

## 4. 접촉 정의

### 4.1 Phase 1 접촉 (구조)

| CID | 타입 | Master/Slave | Friction | 비고 |
|-----|------|-------------|----------|------|
| 1 | AUTOMATIC_SURFACE_TO_SURFACE | Impactor ↔ Pouch | fs=0.30, fd=0.20 | SOFT=0, VDC=40, SBOPT=3 |
| 2 | AUTOMATIC_SINGLE_SURFACE | All Cell (Self) | fs=0.20, fd=0.15 | **SOFT=0**, SOFSCL=0.1, VDC=20 |

> **절대 주의**: Self-contact에 **SOFT=2 사용 금지**
> - TSHELL 요소 침식 후 "shell 0 of part 0" dt 에러 발생
> - CPU 시간 81% (SOFT=2) vs 48% (SOFT=0)

### 4.2 Phase 2 추가 접촉 (열)

**Stacked:**

| CID 범위 | 타입 | 연결 | K (W/mm·K) |
|----------|------|------|-----------|
| 301~(4*N_UC) | TIED_SURFACE_TO_SURFACE_THERMAL | UC 내 층간 | 100 (금속), 50 (코팅-분리막), 80 (UC간) |
| 401 | ERODING_SURFACE_TO_SURFACE | Cathode ↔ Anode (분리막 침식 후) | - |
| 501-502 | TIED_NODES_TO_SURFACE | Pouch ↔ Stack | 비열접촉 (HTC=0) |
| 601-602 | TIED_NODES_TO_SURFACE | PCM ↔ Tab | 구조만 |

**Wound:**

| CID | 타입 | 연결 | K (W/mm·K) |
|-----|------|------|-----------|
| 301-304 | TIED_SURFACE_TO_SURFACE_THERMAL | 단일 스파이럴 층간 | 100, 50, 50, 100 |
| 401 | ERODING_SURFACE_TO_SURFACE | Post-separator | - |
| 501-502 | TIED_NODES_TO_SURFACE | Pouch ↔ Jellyroll | 비열접촉 |

### 4.3 CONTROL_CONTACT 설정

```
*CONTROL_CONTACT
$   SLSFAC    RWPNAL    ISLCHK    SHLTHK    PENOPT    THKCHG     OTEFP    ENMASS
      0.10       0.0         2         1         1         0         1         0
$   USRSTR    USRFRC     NSBCS    INTERM     XPENE     SSTHK      ECDT   TIEDPRJ
         0         0        10         0       4.0         0         0         0
```

---

## 5. 경계조건 및 하중

### 5.1 Phase 1 (구조)

```
*BOUNDARY_SPC_SET          → NSID=1 (Bottom pouch, all DOF fixed)
*INITIAL_VELOCITY          → NSID=2 (Impactor), VX=-1000 mm/s
```

### 5.2 Phase 2 추가 (열)

```
*SET_SEGMENT_GENERAL       → SID=3 (Pouch exterior: PID 10, 11, 12)

*BOUNDARY_CONVECTION_SET   → SSID=3
  h = 5.0E-06 W/(mm²·K)   [= 5 W/(m²·K)]
  T∞ = 298.15 K

*BOUNDARY_RADIATION_SET    → SSID=3, TYPE=1
  σ = 5.670E-14            [Stefan-Boltzmann in mm units]
  T∞ = 298.15 K

*INITIAL_TEMPERATURE_SET   → NSID=0 (all nodes), T0 = 298.15 K
```

> **주의**: BOUNDARY_RADIATION_SET에는 **PTYPE=1 (비선형)** 필수
> (CONTROL_THERMAL_SOLVER의 PTYPE 필드)
> PTYPE=0이면 Error 21268 발생

---

## 6. 솔버 제어 파라미터

### 6.1 공통 설정 (모든 Phase)

```
*CONTROL_TERMINATION       → Phase별 ENDTIM (5ms/10ms/60s), ENDMAS=0.10
*CONTROL_SOLUTION          → SOTEFP (Phase1=0, Phase2+=1)
*CONTROL_TIMESTEP          → TSSFAC=0.90, TSLIMT=1.0E-08, ERODE=1
*CONTROL_HOURGLASS         → IHQ=1, QH=0.10 (global default)
*CONTROL_SHELL             → Card 1 + Card 2 (아래 참조)
*CONTROL_SOLID             → ESORT=1
*CONTROL_ENERGY            → HGEN=2, RWEN=2, SLNTEN=2, RYLEN=2
*CONTROL_BULK_VISCOSITY    → Q1=1.50, Q2=0.06, TYPE=1
```

### 6.2 CONTROL_SHELL (매우 중요)

```
*CONTROL_SHELL
$ Card 1:
$   WRPANG     ESORT    IRNXX    ISTUPD    THEORY       BWC     MITER      PROJ
     20.0         1        -1         1         2         2         1         0
$ Card 2:
$ ROTASCL    INTGRD    LAMSHT    CSTYP6    THSHEL
       1.0         0         0         1         1
```

> **THSHEL=1 — TSHELL + 열해석 커플링에 반드시 필요**
> - THSHEL=0 (기본값)으로 Phase 2 실행 시:
>   - Stacked: thermal step 2에서 heap corruption (signal 6)
>   - Wound (np=2): 초기화 중 segfault (signal 11)
> - THSHEL=1 활성화 시 정상 종료 확인

### 6.3 열 솔버 (Phase 2+)

```
*CONTROL_THERMAL_SOLVER
$   ATYPE     PTYPE    SOLVER       GPT       EQH    EQHEAT     FWORK       SBC
         1         1        12 1.0000E-4         0       1.0      0.90       0.0
$   Card 2:
         0       5001.0000E-10 1.0000E-4       1.0                           1.0
```

| 필드 | 값 | 의미 |
|------|---|------|
| ATYPE | 1 | Thermal analysis type |
| **PTYPE** | **1** | Nonlinear (T⁴ radiation 호환). 0이면 Error 21268 |
| SOLVER | 12 | Iterative solver (1-2 iterations/step으로 수렴) |

```
*CONTROL_THERMAL_TIMESTEP
$#      ts       tip       its      tmin      tmax     dtemp      tscp      lcts
         0       0.5  1.00E-05       0.0       0.0       1.0       0.5         0
```

> **필드 순서 매우 중요**:
> - Field 1 (TS): **INTEGER** — 열 시간 단계 플래그 (0=fixed, 1=variable)
> - Field 3 (ITS): **FLOAT** — 실제 초기 열 시간 단계 크기
> - TS에 float 넣으면 Error 10246 ("improperly formatted data")

```
*CONTROL_THERMAL_NONLINEAR
$   REFMAX    CONVTOL       DTVF
        50   1.0E-04       0.5
```

### 6.4 DT2MS (Phase별 차이)

| Phase | DT2MS | 의미 |
|-------|-------|------|
| 1 | 0.0 | 질량 스케일링 없음 (사용자 요구) |
| 2 | -1.00E-05 | Adaptive dt (음수 = 최소 dt 제한) |
| 3 | -1.00E-06 | 더 엄격한 dt 제한 |

---

## 7. Phase별 차이점

### 7.1 종합 비교

| 항목 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| 해석 유형 | 순수 구조 | 구조 + 열 | 구조 + 열 + EM |
| 바이너리 | SP | **DP 필수** | DP 필수 |
| SOTEFP | 0 | 1 | 1 |
| 종료 시간 | 5 ms | 10 ms | **0.01 s** (tier -1 검증) |
| DT2MS | 0.0 | -1.0E-05 | -1.0E-06 |
| TMID | 불필요 | **모든 파트 필수** | 모든 파트 필수 |
| 열 솔버 | 없음 | THSHEL=1, PTYPE=1, SOLVER=12 | 동일 |
| Convection | 없음 | h=5E-6, T∞=298.15 | 동일 |
| Radiation | 없음 | σ=5.67E-14, T∞=298.15 | 동일 |
| Thermal Contact | 없음 | TIED_THERMAL (층간) | 동일, SOFT=0 필수 |
| 초기 온도 | 없음 | 298.15 K 균일 | 동일 |
| Memory | 2000m (SP) | 200m/500m (DP) | **1000m** (EM 추가 메모리) |
| MPI np | 2 | **1** | **1** |
| Electrode 요소 | TSHELL/SHELL | TSHELL/SHELL | **SOLID (All-SOLID 필수)** |
| Isopotential | - | - | SID 201-210 (mesh 파일에서 정의) |
| Refine | 없음 | 없음 | CONTROL_REFINE_SOLID (옵션) |

### 7.2 입력 파일 구성

Phase 1 main file (`01_main_phase1_*.k`):
```
*INCLUDE → 02_mesh_*.k           (메시 + 파트 + 섹션)
*INCLUDE → 04_materials.k         (구조 재료)
*INCLUDE → 05_contacts_phase1_*.k (접촉)
*INCLUDE → 06_boundary_loads_phase1.k (경계조건)
*INCLUDE → 07_control_phase1.k    (솔버 제어)
*INCLUDE → 09_database_phase1.k   (출력)
```

Phase 2 main file (`01_main_phase2_*.k`):
```
*INCLUDE → 02/03_mesh_*.k         (메시)
*INCLUDE → 04_materials.k         (구조 재료)
*INCLUDE → 04_materials_tempdep.k  (온도 의존 재료)
*INCLUDE → 04_materials_expansion_*.k (열팽창)
*INCLUDE → 05_contacts_phase2_*.k (접촉 + 열접촉)
*INCLUDE → 06_boundary_loads_phase2.k (경계조건 + 열)
*INCLUDE → 07_control_phase2.k    (솔버 제어 + 열 솔버)
*INCLUDE → 09_database_phase2.k   (출력)
*INCLUDE → 10_define_curves_phase2.k (온도 의존 커브)
```

---

## 8. 실행 환경

### 8.1 컨테이너

| 컨테이너 | 정밀도 | MPI | Phase | 위치 |
|----------|--------|-----|-------|------|
| `LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif` | SP (928MB) | OpenMPI | Phase 1 | /opt/apptainers/ (compute nodes) |
| `LSDynaBasic_aocc420_ompi4.0.5_mpp_d.sif` | **DP (1.4GB)** | OpenMPI | **Phase 2+** | /opt/apptainers/ (compute nodes) |
| `LSDynaBasic_ifort2022_impilatest_mpp_d.sif` | DP (1.4GB) | Intel MPI | 미사용 | /opt/apptainers/ (compute nodes) |
| `LSDynaBasic_ifort2022_impilatest_mpp_s.sif` | SP (1.4GB) | Intel MPI | 미사용 | /opt/apptainers/ (compute nodes) |

### 8.2 노드 구성

| 노드 | RAM | CPU | 비고 |
|------|-----|-----|------|
| node001 | ~9 GB | 2 cores | Phase 2 stacked 실행 시 segfault 발생 이력 |
| node002 | ~9 GB | 2 cores | Phase 2 양쪽 모델 정상 동작 확인 |

### 8.3 SLURM 스크립트 템플릿

**Phase 1 (SP):**
```bash
#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --nodes=1
#SBATCH --nodelist=node00X

apptainer exec --bind /data:/data,/shared:/shared \
    --env LSTC_FILE=/opt/ls-dyna_license/LSTC_FILE \
    --env FI_PROVIDER=tcp \
    --env I_MPI_FABRICS=ofi \
    --env LD_LIBRARY_PATH=/opt/openmpi/lib \
    /opt/apptainers/LSDynaBasic_aocc420_ompi4.0.5_mpp_s.sif \
    mpirun --mca plm ^slurm --mca btl ^openib -np 2 \
    /opt/ls-dyna/lsdyna_R16.1.1 i=INPUT.k memory=2000m
```

**Phase 2 (DP):**
```bash
#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --nodelist=node002

apptainer exec --bind /data:/data,/shared:/shared \
    --env LSTC_FILE=/opt/ls-dyna_license/LSTC_FILE \
    --env FI_PROVIDER=tcp \
    --env I_MPI_FABRICS=ofi \
    --env LD_LIBRARY_PATH=/opt/openmpi/lib \
    /opt/apptainers/LSDynaBasic_aocc420_ompi4.0.5_mpp_d.sif \
    mpirun --mca plm ^slurm --mca btl ^openib -np 1 \
    /opt/ls-dyna/lsdyna_R16.1.1 i=INPUT.k memory=200m
```

### 8.4 DP Memory 주의사항

DP 바이너리는 1 word = 8 bytes:
- `memory=200m` → 200M × 8B = 1.6 GB (stacked tier -1 적정)
- `memory=500m` → 500M × 8B = 4.0 GB (wound tier -1 적정)
- `memory=2000m` → 2000M × 8B = 16 GB → **Error 70023 (메모리 부족)**

> **memory=500m을 stacked에서 사용하면 segfault 발생** (동시 실행 시 4GB가 노드 여유 메모리 초과)

---

## 9. 디버깅 이력 및 해결된 에러

### 9.1 Phase 1 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| Error 10103 (*CONTROL_TSHELL) | R16에 해당 키워드 없음 | 키워드 제거 |
| "shell 0 of part 0" dt error | Self-contact SOFT=2 + TSHELL 침식 | **SOFT=0으로 변경** |
| 93% 시점 크래시 | TSHELL ELFORM=5 요소 역전 | **ELFORM=1로 변경** |
| "does not reference solid section" | PCM 파트의 SID 미지정 | _get_part_props()에 SID_SOLID_IMPACTOR 추가 |
| *CONTACT_ERODING_SINGLE_SURFACE_ID 포맷 에러 | R16 포맷 비호환 | AUTOMATIC_SINGLE_SURFACE 사용 |

### 9.4 Phase 3 에러 (시간순)

| # | 에러/현상 | 원인 | 해결 |
|---|---------|------|------|
| 1 | `em_BP_fillRandleCircuit` #circuits=0 | Al CC, Sep, Cu CC가 SHELL/TSHELL 요소 → SOLID와 노드 공유 불가 | **전 5개 층 SECTION_SOLID(ELFORM=1)로 변환** + 층간 노드 병합 |
| 2 | EM solver segfault (EMSOL=3 단독) | `*ELEMENT_TSHELL` 존재 시 EM solver 초기화 중 segfault | 전극 전체 TSHELL→SOLID 변환 후 해결 |
| 3 | Error 10246: EOS card malformed | `*EOS_LINEAR_POLYNOMIAL` 9필드를 1줄에 작성 | **2-card format**: Card1=EOSID,C0-C5,E0 / Card2=V0 |
| 4 | Error 10305: EOS not found | 위 10246으로 EOS가 파싱 실패 → EOSID 참조 불가 | Error 10246 수정으로 동시 해결 |
| 5 | Error 20386: MAT_015 requires EOS | Al/Cu CC를 SHELL→SOLID로 변환 시 MAT_015(JC)에 EOS 필수 | `*EOS_LINEAR_POLYNOMIAL` EOSID=11(Al, K=68627MPa), EOSID=12(Cu, K=125000MPa) 추가 |
| 6 | `em_randleSetCircArea2` error=1, inodeFG1=436 | `SET_NODE_GENERAL PART=Al_CC`가 Al CC 양면 노드(내면+외면) 포함 → 내면(cathode와 공유)은 free face 아님 | mesh 생성기가 자유 외부면 노드만 `SET_NODE_LIST`(SID 201-210)로 직접 작성 |

### 9.2 Phase 2 에러 (시간순)

| # | 에러 코드 | 메시지 | 원인 | 해결 |
|---|----------|--------|------|------|
| 1 | Error 10246 | THERMAL_TIMESTEP improperly formatted | Field 1(TS)에 float 입력. TS는 **INTEGER** | TS=0(I), ITS=1E-5를 Field 3으로 이동 |
| 2 | - | Non-ASCII bytes in k-file | em-dash "—", Korean 문자 | ASCII로 교체 (직접적 원인은 아님) |
| 3 | Error 10307 | TMID=0 for PID 20,30,31,100 | Impactor/PCM/Tab에 열재료 미지정 | **TMID=107** 추가 (Steel thermal) |
| 4 | Error 40343 | MPP Thermal not supported in SP | SP 바이너리에서 열해석 불가 | **DP 바이너리**로 전환 |
| 5 | - | License error (MPPDYNA) | DP 라이선스 미포함 | 사용자가 라이선스 수정 |
| 6 | Error 70023 | Failed to allocate 2000000000 words | DP memory=2000m → 16GB > 9GB | memory=200m/500m으로 축소 |
| 7 | Error 21268 | BOUNDARY_RADIATION requires PTYPE>0 | PTYPE=0 (선형)에서 T⁴ 복사 불가 | **PTYPE=1** (비선형) |
| 8 | Signal 6 | malloc(): corrupted top size | **THSHEL=0**에서 TSHELL thermal 메모리 불일치 | **THSHEL=1** |
| 9 | Signal 11 | Segmentation fault (wound np=2) | MPP decomposition + thermal 불안정 | **np=1** |

### 9.3 주의: CONTROL_THERMAL_TIMESTEP 필드 순서

Vol_I.txt line 111963-111998에서 확인:
```
Variable:  TS     TIP     ITS     TMIN    TMAX    DTEMP   TSCP    LCTS
Type:      I      F       F       F       F       F       F       I
Default:   0      1.0     none    ↓       ↓       1.0     0.5     0
```

- **Field 1 (TS)**: INTEGER — 시간 단계 플래그 (0=fixed, 1=variable). 여기에 float을 넣으면 Error 10246
- **Field 3 (ITS)**: FLOAT — 초기 열 시간 단계 크기. 이것이 실제 timestep 값

---

## 10. 핵심 교훈 (Lessons Learned)

### 10.1 TSHELL + 열해석 커플링

1. **THSHEL=1은 필수** — `*CONTROL_SHELL` Card 2에서 활성화
2. THSHEL=0(기본)이면 thermal solver가 TSHELL 요소의 through-thickness DOF를 올바르게 처리하지 못함
3. 이로 인해 heap corruption (메모리 경계 초과 쓰기) 또는 segfault 발생
4. 에러 메시지가 명시적이지 않음 (메모리 관련 시그널만 표시) → 진단 어려움

### 10.2 DP 바이너리 제약

1. Phase 2+는 반드시 DP 바이너리 사용 (SP → Error 40343)
2. DP에서 `memory` 값은 SP의 1/4~1/10 수준으로 설정 (8 bytes/word)
3. **np=1 사용** — np=2에서 MPP decomposition + thermal 불안정
4. node002 사용 권장 (node001에서 stacked 특정 조건 segfault 이력)

### 10.3 키워드 포맷

1. **LS-DYNA는 fixed-format (8-column)** — 필드 위치가 절대적
2. **INTEGER 필드에 FLOAT 입력 불가** — 파싱 에러 (10246)
3. **TABLE은 참조하는 CURVE보다 뒤에** — 그렇지 않으면 참조 에러
4. **Non-ASCII 문자 주의** — 가능하면 주석도 ASCII만 사용

### 10.4 디버깅 원칙

1. **프로젝트 참조 파일 우선 사용**: `LSDyna/Vol_I.txt`, `Vol_II.txt`, `Vol_III.txt`
2. 웹 검색보다 매뉴얼 텍스트 검색이 정확하고 토큰 효율적
3. 한 번에 하나씩 변경하고 결과 확인 (변수 격리)
4. 모든 수동 수정은 반드시 generator 스크립트에 반영
5. 실패한 실행은 `debug_archive`에 백업

### 10.6 Phase 3 핵심 교훈 (EM_RANDLES_SOLID)

1. **All-SOLID 메시 필수**: CCP/PEL/SEP/NEL/CCN 5개 층 전부 SOLID, 층간 노드 병합
2. **Isopotential node set은 자유 외부면 노드만**: SET_NODE_GENERAL PART= 사용 금지. mesh 생성기가 al_bot_grid / cu_top_grid (자유 외부면)만 SID 201-210으로 직접 작성
3. **EOS 필수**: MAT_015(JC)를 SOLID에 쓰면 EOS_LINEAR_POLYNOMIAL 필수. 2-card 포맷 엄수
4. **독립 UC 경계**: 각 UC의 Al CC 하단 / Cu CC 상단은 인접 UC와 독립 노드 (TIED contact으로 연결). 그래야 isopotential FG 노드가 순수 자유면
5. **np=1 고수**: Phase 3도 np=1 (EM solver + MPP decomposition 불안정)
6. **memory=1000m**: EM solver는 Phase 2보다 약 5배 메모리 더 필요

### 10.5 Tier -1 검증 결과

| Phase | Stacked | Wound | 실행 시간 |
|-------|---------|-------|----------|
| Phase 1 | Normal termination | Normal termination | ~2-3 min (SP, np=2) |
| Phase 2 | Normal termination | Normal termination | 6.5 min / 11 min (DP, np=1) |
| **Phase 3** | **Normal termination** | **Normal termination** | **5분 48초 / ~10분 (DP, np=1, 1000m)** |
| Phase 3 circuits | **5UC × 435 circuits** | **1UC × 4011 circuits** | (em_randleSetCircArea2 통과) |

---

## 부록: 상수 참조 (battery_utils.py)

### Part ID (PID)

| PID | 이름 |
|-----|------|
| 10 | POUCH_TOP |
| 11 | POUCH_BOTTOM |
| 12 | POUCH_SIDE |
| 13 | ELECTROLYTE |
| 20 | TAB_POS |
| 21 | TAB_NEG |
| 30 | PCM_POS |
| 31 | PCM_NEG |
| 100 | IMPACTOR |
| 200 | MANDREL_CORE |
| 1000+uc*10+lt | Stacked Unit Cell |
| 2000+lt | Wound Layer |

### Material ID (MID)

| MID | 이름 | TMID |
|-----|------|------|
| 1 | AL | 101 |
| 2 | CU | 102 |
| 3 | NMC | 103 |
| 4 | GRAPHITE | 104 |
| 5 | SEPARATOR | 105 |
| 6 | POUCH | 106 |
| 7 | RIGID | 107 |
| 8 | ELECTROLYTE | 108 |

### Section ID (SID)

| SID | 키워드 | 용도 |
|-----|--------|------|
| 1 | SECTION_SHELL (ELFORM=2) | Al/Cu CC, Pouch |
| 2 | SECTION_SHELL (ELFORM=16) | Separator |
| 3 | SECTION_TSHELL (ELFORM=1) | Cathode, Anode, Electrolyte |
| 4 | SECTION_SOLID (ELFORM=1) | Impactor, PCM |
| 5 | SECTION_TSHELL (ELFORM=1) | Electrolyte Fill (Wound) |
| 6 | SECTION_SHELL (ELFORM=2) | Pouch Side (Wound) |
| 7 | SECTION_SHELL (ELFORM=2) | Cu CC (Wound) |

### Layer Type Codes

| LT | 이름 |
|----|------|
| 1 | AL_CC |
| 2 | CATHODE |
| 3 | SEPARATOR |
| 4 | ANODE |
| 5 | CU_CC |

---

## 11. Phase 2 물리 커버리지 상세

### 11.1 현재 모델링되는 물리 현상

#### 구조 (Mechanical)
| 현상 | 구현 방법 | 상태 |
|------|----------|------|
| 충격 변형 | Impactor → Pouch (V=-1000mm/s) | ✅ 동작 확인 |
| 소성 변형 | Johnson-Cook (Al/Cu), PLP (전극) | ✅ |
| 크러시 응답 | LCSS crush curves (NMC: 1001, Graphite: 1002) | ✅ |
| 요소 침식 | MXEPS (Al/Cu=0.4, Elec=0.1), FAIL (Sep=0.3, 전극=0.3) | ✅ |
| 다층 접촉 | AUTOMATIC_SINGLE_SURFACE (자기접촉, SOFT=0) | ✅ |
| 마찰 | 정적/동적 마찰 (Impactor: 0.30/0.20, Self: 0.20/0.15) | ✅ |

#### 열 (Thermal)
| 현상 | 구현 방법 | 상태 |
|------|----------|------|
| 열전도 | TIED_THERMAL contacts (K=50~100 W/mm·K) | ✅ |
| 이방성 열전도 | THERMAL_ORTHOTROPIC (NMC, Graphite) | ✅ |
| 대류 | BOUNDARY_CONVECTION_SET (h=5E-6, T∞=298.15K) | ✅ |
| 복사 | BOUNDARY_RADIATION_SET (σ=5.67E-14, PTYPE=1) | ✅ |
| 초기 온도 | INITIAL_TEMPERATURE_SET (298.15K 균일) | ✅ |
| 온도 의존 크러시 | TABLE 4003/4004 (298K, 373K, 473K) | ✅ |
| 분리막 상변화 | TLAT=403K (130°C), HLAT=145 kJ/kg | ✅ |
| 열팽창 | MAT_ADD_THERMAL_EXPANSION (CTE 정의) | ✅ |
| 기계적 마찰열 | FWORK=0.90 (마찰 에너지의 90% → 열 변환) | ✅ |
| 소성변형열 | CONTROL_THERMAL_SOLVER의 EQHEAT=1.0 | ✅ |

### 11.2 현재 모델링되지 않는 물리 현상

#### 전기화학 (Phase 3에서 추가 예정)
| 현상 | 필요 키워드 | 현재 상태 |
|------|-----------|----------|
| 내부 단락 (ISC) | EM_RANDLES_SHORT | ❌ 분리막 침식은 추적하지만 ISC 트리거 없음 |
| 줄 발열 (Joule heating) | EM_RANDLES_SOLID + THERMAL_COUPLING=2 | ❌ 전류=0이므로 P=I²R=0 |
| 발열 반응 (Exothermic) | EM_RANDLES_EXOTHERMIC_REACTION | ❌ config에 정의됨(FUNCTID 5002)이나 미활성 |
| SOC 추적 | EM_RANDLES_SOLID + SOC tables | ❌ Q=2.6Ah 정의됨이나 미사용 |
| 전극 전위/과전압 | 전기화학 kinetics | ❌ |
| 전류 분포 | EM solver | ❌ |

#### 화학/물질 변화
| 현상 | 필요 키워드 | 현재 상태 |
|------|-----------|----------|
| 전해질 분해 | Arrhenius kinetics | ❌ Gas scenario에만 정의 |
| SEI 층 분해 | FUNCTID 12010 | ❌ Gas/Swelling scenario에만 정의 |
| 가스 발생 | AIRBAG_SIMPLE | ❌ Standalone 파일만 존재 |
| 분리막 용융/폐쇄 | Porosity model | ❌ 상변화 잠열만 있고, 기공 폐쇄 미모델링 |
| 열폭주 전파 (TR) | Joule + Exothermic + 온도 피드백 | ❌ 전기화학 없이 불가 |

#### 기타
| 현상 | 비고 |
|------|------|
| Lorentz 힘 | 전류=0, 자기장=0 → 힘=0 |
| Tab 접촉 저항 | PCM/Tab은 구조 + 열전도만 (전기 전도 없음) |
| 전해질 유동 | Electrolyte는 MAT_ELASTIC (고체) 처리 |
| Li-ion 확산/삽입 | 전기화학 모듈 없이 불가 |

### 11.3 Phase 2의 의미와 한계

**Phase 2가 답할 수 있는 질문:**
- 크러시 시 셀 내부 온도가 어디까지 올라가는가? (기계적 마찰/소성열만으로)
- 분리막이 어느 시점에 침식되는가?
- 열전도 경로를 통해 온도가 어떻게 확산되는가?
- 외부 대류/복사 냉각의 효과는?
- 온도 의존 크러시 강도 변화가 결과에 미치는 영향은?

**Phase 2가 답할 수 없는 질문:**
- 내부 단락 후 셀 온도가 얼마나 빨리 상승하는가? (Joule heating 없음)
- 열폭주(thermal runaway)가 발생하는가? (발열 반응 없음)
- 가스가 얼마나 빨리 발생하는가? (화학 분해 없음)
- 인접 셀로 열폭주가 전파되는가? (EM 커플링 없음)
- 단락 전류의 크기와 분포는? (EM solver 없음)

> **핵심**: Phase 2는 "기계적 열 생성 + 열전달" 검증 단계.
> ISC/Joule/Exothermic은 Phase 3의 EM_RANDLES 활성화 후 가능.

---

## 12. Phase 3 로드맵 및 시나리오

### 12.1 Phase 3 추가 사항

| 항목 | Phase 2 | Phase 3 (계획) |
|------|---------|---------------|
| EM Solver | OFF | **EM_RANDLES_SOLID** (분산 회로 모델) |
| 내부 단락 | 미구현 | **EM_RANDLES_SHORT** (분리막 침식 트리거) |
| 발열 반응 | 미구현 | **EM_RANDLES_EXOTHERMIC_REACTION** (T>120°C) |
| 종료 시간 | 10 ms | **60 s** (열폭주 관측 시간) |
| DT2MS | -1.0E-05 | **-1.0E-06** (더 엄격한 dt 제한) |
| ENDMAS | 0.10 | **0.0** (시간까지 완주) |
| 요소 세분화 | 없음 | **CONTROL_REFINE_SOLID** (변형 집중부 메시 세분화) |

### 12.2 Phase 3 EM_RANDLES 구성 (config 기준)

```
EM_RANDLES_SOLID:
  - POSITIVE electrode nodes → Al CC
  - NEGATIVE electrode nodes → Cu CC
  - SEPARATOR → PE separator elements
  - INTERNAL nodes → electrolyte

  SOC tables:
    - NMC cathode OCV vs SOC (LCID defined in config)
    - Graphite anode OCV vs SOC (LCID defined in config)
    - Initial SOC = 1.0 (fully charged, worst case)
    - Capacity Q = 2.6 Ah

  Coupling:
    - THERMAL_COUPLING = 2 (element-level Joule heat)
    - STRUCTURAL_COUPLING = 1 (Lorentz forces)
```

### 12.3 Phase 3 발열 반응 모델

```
EM_RANDLES_EXOTHERMIC_REACTION:
  - Activation temperature: 393.15 K (120°C)
  - Heat generation: 5000 W = 5 kW
  - FUNCTID: 5002 (Arrhenius-type curve)
  - Triggered when any element exceeds T_activation
```

### 12.4 독립 시나리오 (Phase와 별도)

| 시나리오 | 물리 현상 | 종료 시간 | 상태 |
|---------|----------|----------|------|
| **Swelling** | 충전 팽창 (intercalation strain) + SEI 성장 | 7200 s (2h) | 코드 프레임워크 존재 |
| **Gas** | 외부 가열 → 가스 발생 → 벤팅 | 3600 s (1h) | 코드 프레임워크 존재 |
| **Impact** (Phase 1→2→3) | 충격 크러시 → ISC → 열폭주 | 5ms→10ms→60s | Phase 2 완료, Phase 3 미착수 |

#### Swelling 시나리오 상세
- Impactor 없음 (자유 팽창)
- Graphite CTE=3.5% / NMC CTE=1.5% (intercalation strain)
- SEI 성장: Ramadass(2004) kinetics
- SOTEFP=1, ERODE=0 (침식 없음)
- DT2MS=-1.0E-06

#### Gas 시나리오 상세
- 외부 열유속: 5000 W/m² (BOUNDARY_HEAT_SET)
- 2-단계 Arrhenius 가스 발생:
  1. SEI 분해 (80°C): FUNCTID 12010
  2. 전해질 분해 (150°C): 별도 Arrhenius
- AIRBAG_SIMPLE for 벤팅 시뮬레이션
- EM_RANDLES + exothermic 포함

### 12.5 Phase 3 현황

| 항목 | 상태 | 비고 |
|------|------|------|
| Phase 1 tier -1 검증 | ✅ 완료 | SP, Normal termination |
| Phase 2 tier -1 검증 | ✅ 완료 | DP, THSHEL=1, Normal termination |
| **Phase 3 tier -1 검증** | ✅ **완료** | All-SOLID mesh, DP, np=1, 1000m, 실제 회로 계산 확인 |
| Phase 1/2/3 tier 0+ | ❌ 미착수 | Fine mesh 단계 |
| Swelling 시나리오 | ❌ 미제출 | 코드 프레임워크 존재 |
| Gas 시나리오 | ❌ 미제출 | 코드 프레임워크 존재 |

---

## 13. 전체 진행 상황 요약

```
Phase 1 (Mechanical Only)
├── tier -1 (debug)
│   ├── Stacked: ✅ Normal termination (SP, np=2, ~2min)
│   └── Wound:   ✅ Normal termination (SP, np=2, ~3min)
├── tier 0 (mid)
│   └── 입력 파일 생성 완료, 미제출
└── tier 1 (fine)
    └── ❌ 미착수

Phase 2 (Thermo-Mechanical)
├── tier -1 (debug)
│   ├── Stacked: ✅ Normal termination (DP, np=1, THSHEL=1, 6.5min)
│   └── Wound:   ✅ Normal termination (DP, np=1, THSHEL=1, 11min)
├── tier 0 (mid)
│   └── ❌ 미착수
└── tier 1 (fine)
    └── ❌ 미착수

Phase 3 (Thermo-Mechanical + EM_RANDLES_SOLID) — 2026-03-04 완료
├── tier -1 (debug)
│   ├── Stacked (case_09): ✅ Normal termination (DP, np=1, 1000m, 5m48s)
│   │   └── 5 UCs × 435 circuits = 2175 circuits (em_randleSetCircArea2 통과)
│   └── Wound   (case_10): ✅ Normal termination (DP, np=1, 1000m, ~10min)
│       └── 1 UC × 4011 circuits (em_randleSetCircArea2 통과)
├── tier 0 (mid)
│   └── ❌ 미착수
└── tier 1 (fine)
    └── ❌ 미착수

독립 시나리오
├── Swelling (case_07): 코드 프레임워크 존재, 미제출
└── Gas (case_08): 코드 프레임워크 존재, 미제출

핵심 아키텍처 변경 (Phase 3 EM 호환)
├── Al CC, Separator, Cu CC: SECTION_SHELL/TSHELL → SECTION_SOLID(ELFORM=1)
├── Cathode, Anode: SECTION_TSHELL → SECTION_SOLID(ELFORM=1)
├── EOS_LINEAR_POLYNOMIAL: Al(EOSID=11), Cu(EOSID=12) 추가 (MAT_015 SOLID 필수)
└── Isopotential node sets (SID 201-210): mesh 생성기가 자유 외부면 노드만 직접 작성
```
