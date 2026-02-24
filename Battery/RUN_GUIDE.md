# LS-DYNA 배터리 충격-열폭주 해석 실행 가이드

## 🆕 YAML 설정 기반 워크플로우 (2026-02-17 업데이트)

모든 파라미터가 `battery_config.yaml`에서 중앙 관리됩니다.
자세한 사용법은 **[YAML_GUIDE.md](YAML_GUIDE.md)** 참조.

### Quick Start (YAML 기반)

```bash

# 1. YAML 파일 확인

python -c "import yaml; yaml.safe_load(open('battery_config.yaml', 'r', encoding='utf-8')); print('✓ OK')"

# 2a. Tier 0 (15 UC) 전체 생성: mesh + contacts + EM Randles

python generate_all_tiers.py --tier 0 --type stacked

# 2b. 또는 개별 생성:

python generate_mesh_stacked.py --tier 0
python generate_contacts.py --tier 0 --type stacked --phase all
python generate_em_randles.py --tier 0

```

### 실행 가능한 모델 준비 및 실행 (3단계)

생성된 파일은 티어별 이름을 가지지만, main 파일은 범용 이름을 기대합니다.
`prepare_run.py`를 사용하여 실행 환경을 준비하세요:

```bash

# Step 1: 원하는 티어의 파일 생성

python generate_all_tiers.py --tier -1 --type stacked

# Step 2: 실행 파일 준비 (생성된 파일명 → main이 찾는 파일명)

python prepare_run.py --tier -1 --type stacked --phase 1

# 출력 예시:

#   LS-DYNA 실행 파일 준비 (Tier -1.0, stacked)

#   [Stacked] Phase [1]

#     ✓ Mesh: 02_mesh_stacked_tier-1_0.k → 02_mesh_stacked_tier-1.k

#     ✓ Contacts P1: 05_contacts_phase1_tier-1.k → 05_contacts_phase1.k

#

#   ✓ 준비 완료!

#   실행 명령:

#     ls-dyna i=01_main_phase1_stacked.k ncpu=4 memory=2000m

# Step 3: LS-DYNA 실행

ls-dyna i=01_main_phase1_stacked.k ncpu=4 memory=2000m

```

**파일 준비 내용**:

- Mesh: `02_mesh_stacked_tier-1_0.k` → `02_mesh_stacked_tier-1.k`
- Contacts: `05_contacts_phase1_tier-1.k` → `05_contacts_phase1.k`
- EM Randles: `08_em_randles_tier-1.k` → `08_em_randles.k` (Phase 3만)

**Phase별 실행**:

```bash

# Phase 1 (구조만, 5ms)

python prepare_run.py --tier -1 --type stacked --phase 1
ls-dyna i=01_main_phase1_stacked.k ncpu=4

# Phase 2 (구조-열 연성, 10ms)

python prepare_run.py --tier -1 --type stacked --phase 2
ls-dyna i=01_main_phase2_stacked.k ncpu=4

# Phase 3 (구조-열-전기 연성, 20ms)

python prepare_run.py --tier -1 --type stacked --phase 3
ls-dyna i=01_main_phase3_stacked.k ncpu=8 memory=4000m

```

### 해석 시간 예측

```bash

# 전체 티어 비교

python estimate_runtime.py --all

# 특정 티어 추정

python estimate_runtime.py --tier -1 --phase 1 --ncpu 1
python estimate_runtime.py --tier 0 --phase 3 --ncpu 8 --type wound

# 출력 예시 (Tier -1, Phase 1, 1 core):

#   요소 수: 6,000

#   종료 시간: 5.0 ms

#   시간스텝: 9.0 µs

#   총 스텝: 555

#   ⏱ 예상 실행 시간: 2.0초

```

**대략적인 실행 시간 (Intel Xeon E5-2690 v4, 4 코어 기준)**:

- **Tier -1 (디버깅)**: 초~분 (Phase 1), 분 (Phase 3)
- **Tier 0 (개발/검증)**: 분~시간 (Phase 1), 시간 (Phase 3)
- **Tier 0.5 (프로덕션)**: 시간~일 (Phase 1), 일~주 (Phase 3)
- **Tier 1+ (연구)**: 일~주 (Phase 1), 주~월 (Phase 3) — HPC 필수

---

## 티어별 상세 비교

### 📊 티어 선택 가이드

| Tier | 목적 | 요소 수 (Stacked) | 요소 수 (Wound) | Phase 1 실행시간 | 하드웨어 |
| ------ | ------ | ------------------ | ---------------- | ---------------- | ---------- |
| **-1** | 디버깅/교육 | 6K | 23K | 2초 | 워크스테이션 (1-4 코어) |
| **0** | 개발/DOE | 57K | 210K | 42초 | 워크스테이션 (4-8 코어) |
| **0.5** | 프로덕션/규격 | 1.8M | 4.0M | 1.5시간 | 소규모 클러스터 (128-256 코어) |
| **1** | 논문/연구 | 200M | 500M | 일 단위 | 대규모 HPC (수천 코어) |
| **2** | 첨단 연구 | 2B | 5B | 주 단위 | 최대 규모 HPC (수만 코어) |

### 🎯 사용 사례별 권장 티어

| 작업 | 권장 Tier | 이유 |
| ------ | ----------- | ------ |
| k-file 문법 검증 | **Tier -1** | 초 단위 실행, 빠른 반복 |
| 파라미터 민감도 분석 | **Tier 0** | 수십 케이스 하루 내 완료 |
| OEM 제출용 보고서 | **Tier 0.5** | 업계 표준, 실험 비교 가능 |
| 층별 거동 분석 | **Tier 1** | through-thickness 구배 포착 |
| 입자 수준 메커니즘 | **Tier 2** | 최고 정밀도, 새로운 현상 발견 |

### ⚙️ 티어별 특징 상세

#### Tier -1: 디버깅/교육용

```yaml

mesh_size_xy: 5.0 mm
n_cells/winds: 5
timestep: ~9.0 µs

```

**장점**:

- ✅ 초 단위 실행 (Phase 1)
- ✅ 문법 오류 즉시 확인
- ✅ 접촉/경계조건 디버깅

**한계**:

- ❌ 정량적 예측 불가
- ❌ 분리막 파단 판정 불가

#### Tier 0: 개발/검증용

```yaml

mesh_size_xy: 2.5 mm
n_cells/winds: 15
timestep: ~4.0 µs

```

**장점**:

- ✅ 거시적 하중-변위 커브
- ✅ 빠른 DOE (수십 케이스/일)
- ✅ 재료 파라미터 민감도 분석

**한계**:

- ⚠️ 층별 응력 구배 부정확
- ⚠️ ISC 위치 예측 저정밀

#### Tier 0.5: 프로덕션/규격 시험용 ⭐

```yaml

mesh_size_xy: 0.5 mm
n_cells/winds: 20 (stacked) / 15 (wound)
timestep: ~1.0 µs

```

**장점**:

- ✅ 업계 표준 (대부분의 OEM이 사용)
- ✅ 안전 규격 충족 증명 (EUCAR, UL 2580)
- ✅ 실험 결과와 비교 검증 가능
- ✅ 최종 설계 검증

> 현재 업계 대부분이 이 수준에서 운영

#### Tier 1: 층별 해상도 (연구 논문급)

```yaml

mesh_size_xy: 0.1 mm
through_thickness_elements: 3
timestep: ~0.3 µs

```

**돌파점**:

- ✅ 전극 코팅 through-thickness 응력/변형 구배
- ✅ 개별 CC/분리막 층의 좌굴(wrinkling)
- ✅ ISC 개시점 정밀 예측
- ✅ 열 핫스팟 고정밀 식별

**요구 사항**: 대규모 HPC 클러스터 (수천~만 코어)

#### Tier 2: 입자 클러스터 스케일 (첨단 연구)

```yaml

mesh_size_xy: 0.05 mm (50 µm)
through_thickness_elements: 5
timestep: ~0.1 µs

```

**돌파점**:

- ✅ 활물질 2차 입자 클러스터 (30-50µm) 해상도
- ✅ CC 파단 개시/전파 메커니즘 직접 모사
- ✅ 분리막 기공 폐쇄(pore closure) 간접 포착
- ✅ ISC 전류 경로 고해상도 맵핑

**요구 사항**: 최대 규모 HPC (수만 코어) 또는 클라우드

### 📈 정확도 vs 비용 트레이드오프

```text

정확도
  ↑
  │         Tier 2 (입자 클러스터)
  │              ○ 주~월
  │             /
  │      Tier 1 (층별 해상도)
  │          ○ 일~주
  │         /
  │   Tier 0.5 ★ (업계 표준)
  │       ○ 시간~일
  │      /
  │ Tier 0  (개발/DOE)
  │    ○ 분~시간
  │   /
  │Tier -1 (디버깅)
  │  ○ 초~분
  └─────────────────────→ 실행 시간/비용

```

★ **현재 업계 표준** (대부분의 OEM/배터리 제조사)

---

## 티어 커스터마이징

`battery_config.yaml` → `geometry.stacked.tier_definitions`에서:

- `n_cells`: 단위셀 수
- `mesh_size_xy`: 면내 요소 크기
- `through_thickness_elements`: 코팅층 두께 방향 요소 수

변경 후 재생성만 하면 됩니다 (코드 수정 불필요).

**상세 정보**: [TIER_ANALYSIS_ROADMAP.md](TIER_ANALYSIS_ROADMAP.md) 참조


### YAML로 물성 변경하는 법

1. `battery_config.yaml` 열기
2. 해당 파라미터 찾기 (예: `materials → nmc_cathode → thermal_conductivity`)
3. 값 변경 및 `description`/`source`에 이유 기록
4. 파일 저장
5. 스크립트 재실행 (코드 변경 불필요!)

**예시**:

```yaml

materials:
  nmc_cathode:
    thermal_conductivity: 0.0022  # 1.8 → 2.2 W/m·K (실험 측정값)
    description: "2024-02-16 사내 실험 결과 반영"
    source: "Lab Test NMC-2024-015"

```

---

## 프로젝트 구조

```text

Battery/
├── 01_main_phase1_stacked.k    ← Phase 1 시작점 (여기서부터!)
├── 01_main_phase1_wound.k
├── 01_main_phase2_stacked.k
├── 01_main_phase2_wound.k
├── 01_main_phase3_stacked.k
├── 01_main_phase3_wound.k
├── 01_main.k                   ← 원본 (Phase 3 동일)
│
├── 02_mesh_stacked_tier-1.k    ← 6K 요소 (디버깅)
├── 02_mesh_stacked_tier0.k     ← 57K 요소 (기본)
├── 02_mesh_stacked_tier0_5.k   ← 1.8M 요소 (프로덕션)
├── 03_mesh_wound_tier-1.k      ← 18K 요소 (디버깅)
├── 03_mesh_wound_tier0.k       ← 145K 요소 (기본)
├── 03_mesh_wound_tier0_5.k     ← 4.1M 요소 (프로덕션)
│
├── 04_materials.k              ← 공통 (MAT_098 JC + 변형률속도 + GISSMO)
├── 04_materials_tempdep.k      ← 온도 의존 커브/함수 (TABLE, FUNCTION)
├── 05_contacts_phase1.k        ← Phase별 분리
├── 05_contacts_phase2.k
├── 05_contacts.k               ← Phase 3 (전체)
├── 06_boundary_loads_phase1.k
├── 06_boundary_loads_phase2.k  ← 대류+복사 BC
├── 06_boundary_loads.k         ← 대류+복사 BC
├── 07_control_phase1.k
├── 07_control_phase2.k         ← 적응적 메시 포함
├── 07_control.k                ← 적응적 메시 포함
├── 08_em_randles.k             ← Phase 3 전용
├── 08_em_randles_wound.k       ← Phase 3 와인딩 전용
├── 09_database_phase1/2.k
├── 09_database.k
├── 10_define_curves_phase1/2.k
├── 10_define_curves.k          ← 4종 ISC + 5단계 Arrhenius
├── 12_venting.k                ← 전해질 벤팅 (Phase 3 옵션)
├── 13_ale_electrolyte.k        ← ALE/SPH 전해질 (Phase 3 옵션)
│
├── generate_mesh_stacked.py    ← 적층형 메시 생성 (nail 옵션)
├── generate_mesh_wound.py      ← 와인딩 메시 생성 (nail 옵션)
├── generate_all_tiers.py       ← 전 티어 일괄 생성
├── generate_contacts.py        ← 접촉 k-file 생성 (nail 옵션)
├── postprocess_results.py      ← 후처리 자동화
└── convergence_study.py        ← 메시 수렴성 분석

```

## SET ID 매핑 (메시 ↔ 경계/접촉 파일)

### Node Set SID

| SID | 이름 | 용도 |
| ----- | ------ | ------ |
| 1 | `NSET_FIX_BOTTOM_EDGE` | SPC 경계 (하면 고정) |
| 2 | `NSET_IMPACTOR_CENTER` | 임팩터 처방 운동 |
| 3 | `NSET_PCM_POSITIVE_CONTACT` | PCM 접합 (stacked only) |
| 4 | `NSET_PCM_NEGATIVE_CONTACT` | PCM 접합 (stacked only) |
| 1002 | `NSET_STACK_TOP` | 스웰링 BC — 파우치 상면 노드 (`14_intercalation_strain.k`에서 DOF=3 처방 운동) |

### Part Set SID

| SID | 이름 | 내용 |
| ----- | ------ | ------ |
| 100 | `PSET_IMPACTOR` | PID 100 |
| 101 | `PSET_POUCH` | PID 10, 11, 12 |
| 102 | `PSET_ALL_CELL` | 전체 셀 (파우치+전극+전해질) |
| 103 | `PSET_ALL_CATHODE` | 모든 양극 코팅 |
| 104 | `PSET_ALL_ANODE` | 모든 음극 코팅 |
| 105 | `PSET_ALL_SEPARATOR` | 모든 분리막 |
| 106 | `PSET_ALL_AL_CC` | 모든 Al 집전체 |
| 107 | `PSET_ALL_CU_CC` | 모든 Cu 집전체 |
| 108 | `PSET_ELECTROLYTE` | 전해질 |
| 109 | `PSET_PCM` | PCM 보드 (stacked only) |

---

## Phase 1: 순수 구조 해석 (여기서부터 시작!)

### 목적

- 메시/접촉/재료 기본 검증
- 임팩터 충격에 의한 셀 기계적 응답 확인
- 에너지 보존, 안정성 검증

### 설정 요약

| 항목 | 값 |
| ------ | ----- |
| SOTEFP | 0 (구조만) |
| ENDTIM | 5ms |
| DT2MS | -1.0e-5 (보수적) |
| ERODE | 0 (요소 삭제 없음) |
| 접촉 | 임팩터↔파우치 + 자기접촉 |
| 열/EM | OFF |

### 실행 명령

```bash

# SMP (단일 프로세스) — Tier -1 전용

ls-dyna i=01_main_phase1_stacked.k memory=200m

# MPP — Tier 0 이상

mpirun -np 4 ls-dyna i=01_main_phase1_stacked.k memory=500m

```

### 검증 체크리스트

1. **에너지 보존** (glstat 파일)

   ```text
   Total Energy ≈ 일정 (±1% 이내)
   Hourglass Energy / Internal Energy < 5%
   Added Mass < 5% of Total Mass
   ```

2. **접촉 안정성** (rcforc 파일)
   - 임팩터 반력 양의 값 → 접촉 형성 확인
   - 음의 접촉 에너지 없음

3. **변형 패턴** (D3PLOT)
   - 임팩터 관통 위치에서 셀 변형
   - 비물리적 penetration 없음
   - 파우치-셀 스택 분리 없음

4. **질량 스케일링** (glstat)

   ```text
   Added Mass / Total Mass < 5% 목표
   < 10% 허용
   > 10% → DT2MS 줄이기 또는 메시 조정
   ```

---

## Phase 2: 구조-열 연성 해석

### 목적 (Phase 2)

- Phase 1 기계 응답 + 열 솔버 커플링
- 기계적 일 → 열 변환 (frictional heating)
- 분리막 erosion (내부 단락 트리거)
- 온도장 분포 확인

### 설정 요약 (Phase 2)

| 항목 | 값 |
| ------ | ----- |
| SOTEFP | 1 (구조-열 연성) |
| ENDTIM | 10ms |
| FWORK | 0.9 (일→열 90%) |
| ERODE | 1 (분리막 삭제) |
| 접촉 | Phase 1 + TIED THERMAL + ERODING |
| 열 솔버 | Diagonal CG (SOLVER=12) |
| 초기 온도 | 298.15K (25°C) |
| 대류 BC | h=5.0 W/m²K, T∞=298K |
| 복사 BC | σ=5.67e-11, ε=0.9, T∞=298K |
| 적응 메시 | MAXLVL=3, ADPSIZE=0.25 |

### 실행 명령 (Phase 2)

```bash

# SMP

ls-dyna i=01_main_phase2_stacked.k memory=500m

# MPP (Tier 0 이상)

mpirun -np 8 ls-dyna i=01_main_phase2_stacked.k memory=1000m

```

### 검증 체크리스트 (Phase 2)

1. **온도장** (D3PLOT → Temperature contour)
   - 충격 영역에서 미소 온도 상승 (< 5K, frictional only)
   - 균일한 초기 온도 298K
   - 비물리적 음의 온도 없음

2. **분리막 Erosion**
   - 충격 영역에서 분리막 요소 삭제 시작
   - MAT_ADD_EROSION: SIGP1=30MPa 또는 MXEPS=0.6

3. **열 에너지 보존**
   - GLSTAT: Thermal Energy 양의 값
   - Internal Energy + Thermal Energy + ... ≈ Total Energy

---

## Phase 3: 완전 연성 해석 (구조 + 열 + EM)

### 목적 (Phase 3)

- EM Randles 솔버로 전기화학 내부 단락 시뮬레이션
- 줄열 → 열폭주 → 전체 시나리오
- 최종 결과 생산

### 설정 요약 (Phase 3)

| 항목 | 값 |
| ------ | ----- |
| SOTEFP | 1 |
| EMSOL | 3 (Resistive heating) |
| ENDTIM | 60s |
| DT2MS | -1.0e-6 |
| 접촉 | 전체 (임팩터+자기+TIED+ERODING+PCM) |
| EM Randles | 단위셀별 회로 모델 |

### 실행 명령 (Phase 3)

```bash

# Tier -1

mpirun -np 16 ls-dyna i=01_main_phase3_stacked.k memory=2000m

# Tier 0

mpirun -np 64 ls-dyna i=01_main_phase3_stacked.k memory=4000m

# Tier 0.5 (프로덕션)

mpirun -np 256 ls-dyna i=01_main_phase3_stacked.k memory=8000m

```

### 검증 체크리스트 (Phase 3)

1. **내부 단락** (EM 출력)
   - 분리막 erosion 시점에서 단락 전류 발생
   - 단락 저항 ~0.01Ω (DEFINE_FUNCTION 5001)
   - 셀 전압 급격히 하강

2. **줄열** (D3THDT)
   - 단락 위치에서 집중 발열
   - 줄열 = I²R

3. **열폭주 시퀀스**
   - SEI 분해: T > 80°C (353K)
   - 전극-전해질: T > 120°C (393K)
   - 양극 분해: T > 200°C (473K)
   - 최고 온도: ~600-800°C 가능

4. **타이밍**
   - 충격: 0~5ms
   - 내부 단락 형성: ~2-5ms
   - 열 축적: 5ms~1s
   - 열폭주 시작: ~1-10s (SOC/단락저항 의존)
   - 최고 온도: ~10-30s

---

## 티어별 실행 가이드

### Tier -1 (디버깅) — 추천 시작점

```text

stacked: ~6K 요소 → 1 코어, 2~5분
wound:   ~18K 요소 → 1 코어, 5~10분

```

- Phase 1부터 순서대로 실행
- 모든 검증 체크리스트 확인 후 다음 Phase

### Tier 0 (기본)

```text

stacked: ~57K 요소 → 4-8 코어, 30분~2시간
wound:   ~145K 요소 → 8-16 코어, 1~4시간

```

- Phase 1에서 메시 파일만 교체:

  ```text
  $ 01_main_phase1_stacked.k 에서:
  *INCLUDE
  02_mesh_stacked_tier0.k    ← tier-1 대신 tier0
  ```

### Tier 0.5 (프로덕션)

```text

stacked: ~1.8M 요소 → 64-256 코어, 6~12시간
wound:   ~4.1M 요소 → 128-512 코어, 12~24시간

```

- MPP 필수
- `memory=` 파라미터 충분히 (8000m 이상)
- `decomp { rcb }` 분해 방식 권장

### Tier 1 (고해상도 연구)

```text

stacked: ~200M 요소 → 44K 코어, ~6시간
wound:   ~500M 요소 → 44K 코어, ~12시간

```

- 3개 through-thickness 요소 → 전극 내 구배 해석
- DT2MS 더 작게: -5.0e-7
- 클러스터 전용

---

## 메시 파일 교체 방법

각 Phase의 main 파일에서 mesh INCLUDE만 교체하면 됩니다:

```text

$ Phase 1, Tier 0, Stacked:
*INCLUDE
02_mesh_stacked_tier0.k    ← 이 줄만 변경

$ Phase 1, Tier 0, Wound:
*INCLUDE
03_mesh_wound_tier0.k      ← 이 줄만 변경

```

**주의**: Tier 변경 시 DT2MS 조정이 필요할 수 있습니다:

| Tier | 최소 요소 크기 | 권장 DT2MS |
| ------ | --------------- | ------------ |
| -1 | ~5mm | -1.0e-5 |
| 0 | ~2.5mm | -5.0e-6 |
| 0.5 | ~0.5mm | -1.0e-6 |
| 1 | ~0.1mm | -5.0e-7 |

---

## 트러블슈팅

### 1. 초기 관통 (Initial Penetration)

```text

*** Warning: Initial penetration in contact X

```

→ ISLCHK=2가 자동 보정. 심각하면 메시 간격 확인.

### 2. 부의 볼륨 (Negative Volume)

```text

*** Error: Negative volume in element XXX

```

→ DT2MS 줄이기, QH 높이기 (0.10), 또는 요소 품질 확인

### 3. 과도한 질량 추가

```text

Added mass ratio > 20%

```

→ DT2MS 줄이기 (절대값 작게) 또는 얇은 요소 확인

### 4. 열 솔버 미수렴

```text

*** Warning: Thermal solver did not converge

```

→ REFMAX 증가 (100), TOLRF 완화 (1e-3), TMAX 줄이기

### 5. EM 솔버 에러

```text

*** Error: EM_RANDLES invalid circuit

```

→ EM_RANDLES_SOLID PID가 메시의 실제 PID와 일치하는지 확인

### 6. GISSMO 수렴 문제

```text

*** Warning: GISSMO damage exceeding limit

```

→ LCSDG 커브 시작값 확인 (strain>0.05), DCRIT 완화 (0.95→0.99)

### 7. 적응 메시 (CONTROL_ADAPTIVE) 에러

```text

*** Error: Adaptive refinement failed

```

→ MAXLVL 줄이기 (3→2), ADPSIZE 키우기 (0.25→0.5), 셸 요소 확인 (ELFORM=2만 지원)

### 8. 네일 관통 시 과도한 침투

```text

*** Warning: Large penetration in contact 402

```

→ SOFT=2 확인, SFS/SFM 높이기 (2.0→5.0), 네일 팁 메시 세분화

### 9. MAT_NULL (ALE 전해질) 불안정

```text

*** Error: Negative volume in ALE element

```

→ CONTROL_ALE DT factor 줄이기 (0.3→0.1), ADVECTION METHOD=3 사용

---

## 후처리 (LS-PrePost)

### Phase 1 확인

```text

File → Open → d3plot
  Post → FriComp → Effective Stress
  Post → FriComp → Displacement X
  History → Global → Total Energy, Kinetic Energy
  History → Misc → Contact Force → CID 1 (Impactor)

```

### Phase 2 추가 확인

```text

  Post → FriComp → Temperature
  Post → FriComp → Effective Plastic Strain → 분리막 erosion 확인

```

### Phase 3 추가 확인

```text

  Post → FriComp → Temperature → 열폭주 이력
  EM 관련 출력은 d3plot의 NEIPH 추가 변수로 확인

```

---

## 빠른 시작 (Quick Start)

```bash

# 1. 가장 간단한 모델로 시작

cd Battery
ls-dyna i=01_main_phase1_stacked.k memory=200m

# 2. 결과 확인 (에너지, 접촉, 변형)

#    glstat, rcforc, d3plot 파일 생성됨

# 3. 자동 후처리

python postprocess_results.py --dir . --all

# 4. Phase 2로 진행

ls-dyna i=01_main_phase2_stacked.k memory=500m

# 5. Phase 3 (전체 연성)

mpirun -np 16 ls-dyna i=01_main_phase3_stacked.k memory=2000m

```

---

## 고도화 기능 사용법

### 네일 관통 시뮬레이션 (B12)

```bash

# 1. 네일 형상 메시 생성

python generate_all_tiers.py --tier -1 --impactor nail

# 2. 네일 전용 접촉 생성 (ERODING CID 402 포함)

python generate_contacts.py --nail --type both --phase all

# 3. 실행

ls-dyna i=01_main_phase1_stacked.k memory=200m

```

네일 설계 파라미터 (`generate_mesh_stacked.py` CellDesign):

| 파라미터 | 기본값 | 설명 |
| --------- | -------- | ------ |
| `impactor_type` | "cylinder" | "nail"로 변경 |
| `nail_tip_length` | 3.0mm | 원추부 길이 |
| `nail_tip_radius` | 0.5mm | 팁 반경 |
| `nail_shaft_radius` | 1.5mm | 축부 반경 |

### 후처리 자동화 (B9)

```bash

# 기본 리포트 (에너지 보존, 피크 반력)

python postprocess_results.py --dir ./results

# 그래프 포함

python postprocess_results.py --dir ./results --all

# 출력: energy_history.png, force_history.png, force_displacement.png

```

### 메시 수렴성 분석 (B10)

```bash

# 3-Tier 비교 (Richardson 외삽 + GCI)

python convergence_study.py \
  --dirs tier-1=./res_t-1 tier0=./res_t0 tier0_5=./res_t05 \
  --outdir ./convergence_output

# 출력: convergence_study.png, gci_chart.png, convergence_data.csv

```

### 전해질 벤팅 (B11)

> **Note:** 벤팅은 별도 **가스 팽창 시나리오** (`01_main_gas_*.k`)를 통해 완전 통합됩니다.
> 아래는 Phase 3에 수동으로 추가하는 방법입니다.

Phase 3 main 파일에서 주석 해제:

```text

$ 01_main_phase3_stacked.k:
*INCLUDE
12_venting.k

```

`12_venting.k` 구조:

| 항목 | 내용 |
| ---- | ---- |
| `*AIRBAG_SIMPLE_AIRBAG_MODEL` | SID=503 파우치 내면 세그먼트, LCID=-12010 (FUNCTID 12010 호출) |
| `FUNCTID 12010` | Arrhenius 가스 발생율 f(time, temp, pressure, volume) |
| `LCID 12003` | 벤팅 출구 면적 vs 절대압력 (safety valve 모델) |
| 개방 압력 | 0.3 MPa(게이지 0.2 MPa)부터 개방, 1.0 MPa 이상 최대 |

필수 보정 항목:

- `SID=503`: 파우치 내면 세그먼트 셋 (메시에 자동 생성됨, Parts 10+11+12)
- `A_sei`, `A_elyte`: Arrhenius 사전지수 (ARC/DSC 실험으로 보정)

### ALE/SPH 전해질 (C14)

Phase 3 main 파일에서 주석 해제:

```text

$ 01_main_phase3_stacked.k:
*INCLUDE
13_ale_electrolyte.k

```

활성화 단계:

1. `generate_mesh_*.py`: 전해질 ELFORM → 11 (ALE)
2. `04_materials.k`: MID 8 → MID 18 (MAT_NULL+EOS)
3. `07_control.k`: `*CONTROL_ALE` 추가

### EM 전극 전도도 모드 전환

`04_materials.k`의 전극 EM_MAT SIGMA 모드:

| 모드 | NMC (MID=3) | Graphite (MID=4) | Separator (MID=5) | 설명 |
| ---- | ----------- | ---------------- | ----------------- | ---- |
| **정확 (기본)** | `-6003` | `-6004` | `-6005` | 온도의존 전자전도도 활성 |
| **단순** | `0` | `0` | `0` | EM_RANDLES 회로만, 전극 직접 도전 없음 |

Al/Cu 집전체 (`-6001`, `-6002`) 및 전해질 (`0`)은 항상 고정.
전해질 `SIGMA=0` 유지 이유: EM 솔버는 전자전류 기준 — 이온전도도와 별개.

```bash
# 기본 (정확 모드, 전극 온도의존 전도도)
python generate_materials.py --config battery_config.yaml

# 단순 모드 (EM_RANDLES만 사용)
python generate_materials.py --config battery_config.yaml --em-sigma-simplified
```

코드에서 직접 호출:

```python
generate_materials(config)                          # 정확 (기본)
generate_materials(config, em_sigma_tempdep=False)  # 단순
```

---

### 가스 팽창 시나리오 (Gas Expansion)

외부 열원 → 온도 상승 → 가스 발생 → 파우치 팽창/파열 시뮬레이션.

**파일 명명 규칙**: `01_main_{scenario}_{model_type}{tier_suf}[_ale].k`

| 변수 | 가능한 값 | 예시 |
| ---- | --------- | ---- |
| `scenario` | `phase1`, `phase2`, `phase3`, `gas`, `swelling` | `gas` |
| `model_type` | `stacked`, `wound` | `stacked` |
| `tier_suf` | `_tier-1`, `_tier0`, `_tier0_5`, `_tier1` | `_tier-1` |
| `_ale` | 생략 또는 `_ale` | `_ale` (ALE 전해질 활성) |

예: `01_main_gas_stacked_tier-1.k`, `01_main_gas_wound_tier-1_ale.k`

**포함 파일 구성**:

| 파일 | 역할 |
| ---- | ---- |
| `06_boundary_loads_gas.k` | SPC + 외부 열플럭스: q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011] |
| `07_control_gas.k` | 열-구조 연성 제어, 긴 해석 시간 (3600s) |
| `10_define_curves_gas.k` | 열플럭스/OCV/엔트로피/Arrhenius 커브 (LCID 9010 포함) |
| `16_gas_generation_standalone.k` | FUNCTID 9011: 복사 열플럭스 q_rad(T)=ε·σ·(T⁴−T_amb⁴), HLCID=-9011로 연결 |
| `12_venting.k` | AIRBAG 팽창 모델, FUNCTID 12010 (가스 발생율) |
| `13_ale_electrolyte.k` | ALE 전해질 (\_ale 변종만 활성) |

**실행**:

```bash
# 전체 모델 생성 (가스 시나리오 포함)
python generate_full_model.py --config battery_config.yaml

# 가스 시나리오만 재생성
python generate_main.py --config battery_config.yaml --scenario gas --type stacked --tier -1

# 실행
ls-dyna i=01_main_gas_stacked_tier-1.k ncpu=4 memory=4000m

# ALE 변종
ls-dyna i=01_main_gas_stacked_tier-1_ale.k ncpu=4 memory=6000m
```

**열 연쇄 반응 흐름**:

```text
외부 열플럭스 = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011]
  (BOUNDARY_HEAT_SET HLCID=9010 + HLCID=-9011, SID=3 세그먼트에 합산)
  → 온도 상승 (CONTROL_THERMAL_SOLVER)
  → SEI 분해 (T > 353 K, FUNCTID 5002 stage 1)
  → 양극-전해질 반응 (T > 393 K, stage 2)
  → 전해질 분해 (T > 423 K, stage 3)
  → 가스 발생 (FUNCTID 12010 via AIRBAG LCID=-12010)
  → 파우치 팽창 (AIRBAG_SIMPLE_AIRBAG_MODEL)
  → 파우치 파열 (내압 > 0.6 MPa, MAT_ADD_EROSION)
```

---

### 스웰링 시나리오 (Swelling)

충방전 인터칼레이션(삽입/탈리) + SEI 성장에 의한 셀 부풀음 시뮬레이션.
임팩터 없음. EM 솔버 없음. 순수 열-구조 해석.

**파일**: `01_main_swelling_{model_type}{tier_suf}.k`
예: `01_main_swelling_stacked_tier-1.k`

**포함 파일 구성**:

| 파일 | 역할 |
| ---- | ---- |
| `06_boundary_loads_swelling.k` | SPC + 열 BC (대류/복사/초기온도), 임팩터 없음 |
| `07_control_swelling.k` | 열-구조 연성, 장시간 (7200s, 2시간 충전) |
| `10_define_curves_swelling.k` | 전극 크러시 커브만 (OCV/전류 커브 없음) |
| `14_intercalation_strain.k` | NSID=1002 처방 운동 — 인터칼레이션 팽창 |
| `15_sei_growth.k` | FUNCTID 7002 SEI 두께 성장, LCID 9003 변위 커브 |

**NSID=1002 (NSET_STACK_TOP)**:
파우치 상면 노드 셋. `14_intercalation_strain.k`에서 DOF=3 방향(Z) 처방 운동으로
인터칼레이션 + SEI 성장에 의한 스웰링을 적용.

```bash
# 스웰링 시나리오 생성
python generate_main.py --config battery_config.yaml --scenario swelling --type stacked --tier -1

# 실행
ls-dyna i=01_main_swelling_stacked_tier-1.k ncpu=4 memory=2000m
```

**변위 커브 해석 (LCID 9001)**:

```text
t=0~3600s (1시간 충전): 인터칼레이션 → 약 3.4% 팽창
t=3600~7200s (추가 사이클): SEI 누적 → 비가역 팽창
```

---

### 고도화 재료 물성 요약

| 고도화 | 키워드 | 파일 |
| -------- | -------- | ------ |
| 온도 연화 (Al/Cu) | MAT_098 (JC: M, TM) | 04_materials.k |
| 온도 의존 크러시 | DEFINE_TABLE 4003/4004 | 04_materials_tempdep.k |
| 변형률속도 | JC C (Al/Cu), Cowper-Symonds (Sep/Pouch) | 04_materials.k |
| 열팽창 | MAT_ADD_THERMAL_EXPANSION ×7 | 04_materials.k |
| 분리막 GISSMO | MAT_ADD_GENERALIZED_DAMAGE | 04_materials.k |
| EM 전도도(T) — 집전체 | DEFINE_FUNCTION 6001-6002 (Al/Cu) | 04_materials_tempdep.k |
| EM 전도도(T) — 전극 (정확 모드) | DEFINE_FUNCTION 6003-6005 (NMC/Gr/Sep) | 04_materials_tempdep.k |
| 복사 BC | BOUNDARY_RADIATION_SET | 06_boundary_loads.k |
| 적응 메시 | CONTROL_ADAPTIVE (MAXLVL=3) | 07_control.k |
| 4종 ISC | DEFINE_FUNCTION 5001 | 10_define_curves.k |
| 5단계 Arrhenius | DEFINE_FUNCTION 5002 | 10_define_curves.k |
| 인터칼레이션 스웰링 | BOUNDARY_PRESCRIBED_MOTION_SET (NSID=1002) | 14_intercalation_strain.k |
| SEI 성장 | DEFINE_FUNCTION 7002 | 15_sei_growth.k |
| AIRBAG 벤팅 | AIRBAG_SIMPLE_AIRBAG_MODEL, FUNCTID 12010 | 12_venting.k |
