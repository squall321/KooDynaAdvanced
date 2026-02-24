# 리튬이온 파우치 배터리 크러시 해석 — 티어별 메시 밀도 로드맵

> **프로젝트**: LS-DYNA R16 기반 멀티피직스(구조-열-전기) 연성 해석
> **단위**: mm, ton(1e-3 kg), s, N, MPa, mJ
> **대상**: 스마트폰/태블릿 파우치 배터리 셀 (70 × 140 mm)
> **작성일**: 2026-02-17 (업데이트)
> **YAML 설정**: battery_config.yaml (tier_definitions 참조)

---

## 1. 개요

본 문서는 배터리 충격 시뮬레이션의 **티어별 메시 해상도 전략**을 정의합니다.
각 티어는 **목적**, **요소 수**, **실행 시간**, **하드웨어 요구사항**이 명확히 구분됩니다.

**핵심 트레이드오프**:

- **해상도 ↑** → 물리적 정확도 ↑, 예측 신뢰도 ↑
- **요소 수 ↑** → 타임스텝 ↓, 실행 시간 ↑, 메모리 ↑, 비용 ↑

---

## 2. 시간적분 안정 조건 (Explicit Solver)

LS-DYNA explicit 솔버의 안전 시간증분:

$$\Delta t \leq \frac{L_{\min}}{c} \cdot SF$$

여기서:

- $L_{\min}$: 최소 요소 특성 길이
- $c = \sqrt{E/\rho}$: 탄성파 전파 속도
- $SF = 0.9$: 안전 계수 (`TSSFAC`)

**대표 재료 음속**:

| 재료 | $E$ (MPa) | $\rho$ (ton/mm³) | $c$ (mm/µs) |
| --- | --- | --- | --- |
| Al CC | 70,000 | 2.7e-6 | 5.09 |
| Cu CC | 119,000 | 8.96e-6 | 3.64 |
| NMC 양극 | 500 | 2.5e-6 | 0.45 |
| Graphite 음극 | 1,000 | 1.35e-6 | 0.86 |
| PE 분리막 | 1,000 | 0.95e-6 | 1.03 |

> **핵심**: 두께 방향 요소가 가장 작으므로 $L_{\min}$을 지배.
> 솔리드 전극 코팅이 두께 방향 최소이고, 셸(CC/분리막)은 면내 크기 지배.

---

## 3. 티어 정의 (70 × 140 mm 셀 기준)

### 🔧 Tier -1: 디버깅/교육용 (Ultra-Coarse)

> **목적**: k-file 구문 검증, 접촉 디버깅, 솔버 실행 확인
> **환경**: 워크스테이션 (1-4 코어), 수 초~분 이내

| 파라미터 | Stacked | Wound |
| --- | --- | --- |
| 면내 메시 | **5.0 mm** | **5.0 mm** |
| 두께 방향 | 코팅 1요소 | 코팅 1요소 |
| 단위셀/와인딩 수 | 5 | 5 |
| **총 요소 수** | **~6,000** | **~23,000** |
| 타임스텝 (Δt) | ~9.0 µs | ~9.0 µs |
| **Phase 1 실행시간** (4코어) | **2초** | **8초** |
| **Phase 3 실행시간** (4코어) | **20초** | **1.3분** |
| 메모리 | <1 GB | <1 GB |

**사용 사례**:

- ✅ k-file 문법 검증
- ✅ 접촉/경계조건 디버깅
- ✅ 에너지 균형 확인
- ✅ 질량 스케일링 효과 확인
- ✅ 학습/교육용 데모

**한계**:

- ❌ 정량적 응력/변형 예측 불가
- ❌ 분리막 파단 판정 불가

---

### 🛠 Tier 0: 개발/검증용 (Baseline)

> **목적**: 거시적 기계 응답 (하중-변위 커브), 파라미터 스터디
> **환경**: 워크스테이션 (4-8 코어), 수 분~시간

| 파라미터 | Stacked | Wound |
| --- | --- | --- |
| 면내 메시 | **2.5 mm** | **2.5 mm** |
| 두께 방향 | 코팅 1요소 | 코팅 1요소 |
| 단위셀/와인딩 수 | 15 | 15 |
| **총 요소 수** | **~57,000** | **~210,000** |
| 타임스텝 (Δt) | ~4.0 µs | ~4.0 µs |
| **Phase 1 실행시간** (4코어) | **42초** | **2.6분** |
| **Phase 3 실행시간** (4코어) | **7분** | **26분** |
| 메모리 | 1-2 GB | 2-3 GB |

**사용 사례**:

- ✅ 개발 단계 빠른 DOE
- ✅ 재료 파라미터 민감도 분석
- ✅ 거시적 응답 검증
- ✅ 임팩터 형상/속도 최적화

**한계**:

- ⚠️ 층별 응력 구배 해상도 부족
- ⚠️ 분리막 파단 개시점 부정확
- ⚠️ ISC 위치 예측 저정밀

---

### 🏭 Tier 0.5: 프로덕션/규격 시험용 (Production)

> **목적**: 업계 표준 해석, 안전 규격 시험 (EUCAR, UL 2580)
> **환경**: 소규모 클러스터 (128-256 코어), 수 시간~일

| 파라미터 | Stacked | Wound |
| --- | --- | --- |
| 면내 메시 | **0.5 mm** | **0.5 mm** |
| 두께 방향 | 코팅 1요소 | 코팅 1요소 |
| 단위셀/와인딩 수 | 20 | 15 |
| **총 요소 수** | **~1,800,000** | **~4,000,000** |
| 타임스텝 (Δt) | ~1.0 µs | ~1.0 µs |
| **Phase 1 실행시간** (4코어) | **1.5시간** | **3.3시간** |
| **Phase 3 실행시간** (8코어) | **15시간** | **1.4일** |
| 메모리 | 10-20 GB | 20-40 GB |

**사용 사례**:

- ✅ 최종 설계 검증
- ✅ OEM 제출용 시뮬레이션 보고서
- ✅ 안전 규격 충족 증명
- ✅ 실험 결과와 비교 검증

**업계 표준**: 대부분의 OEM/배터리 제조사가 이 수준에서 해석 수행

---

### 🔬 Tier 1: 층별 해상도 (Layer-Resolved)

> **목적**: 두께 방향 응력 구배 포착, 개별 층 좌굴/변형 모드
> **환경**: 대규모 HPC 클러스터 (수천~만 코어), 일~주 단위
> **연구 논문급**

| 파라미터 | Stacked | Wound |
| --- | --- | --- |
| 면내 메시 | **0.1 mm** | **0.1 mm** |
| 두께 방향 | **코팅 3요소** | **코팅 3요소** |
| 단위셀/와인딩 수 | 22 | 15 |
| **총 예상 요소** | **~200M** (2억) | **~500M** (5억) |
| 타임스텝 (Δt) | ~0.3 µs | ~0.3 µs |
| **Phase 1 실행시간** (추정) | **일 단위** | **일 단위** |
| **Phase 3 실행시간** (추정) | **주 단위** | **주 단위** |
| 메모리 | 수백 GB | ~1 TB |

**돌파점**:

- ✅ 전극 코팅 **through-thickness 응력/변형 구배** 포착
- ✅ 개별 CC/분리막 층의 **좌굴(wrinkling)** 모사
- ✅ 분리막 **국소 변형 집중** → ISC 개시점 정밀 예측
- ✅ 열 핫스팟 위치 고정밀 식별
- ✅ **논문급 결과물**: 개별 층 해상도 풀셀 크러시 해석

---

### 🧪 Tier 2: 입자 클러스터 스케일 (Particle-Cluster)

> **목적**: 2차 입자 (30-50µm) 수준 거동 포착, CC 파단 메커니즘
> **환경**: 최대 규모 HPC 클러스터 (수만 코어), 주~월 단위
> **첨단 연구용**

| 파라미터 | Stacked | Wound |
| --- | --- | --- |
| 면내 메시 | **0.05 mm** (50 µm) | **0.05 mm** |
| 두께 방향 | **코팅 5요소** | **코팅 5요소** |
| CC/분리막 | **솔리드 2요소** | **솔리드 2요소** |
| 단위셀/와인딩 수 | 25 | 15 |
| **총 예상 요소** | **~2B** (20억) | **~5B** (50억) |
| 타임스텝 (Δt) | ~0.1 µs | ~0.1 µs |
| **Phase 1 실행시간** (추정) | **주 단위** | **주 단위** |
| **Phase 3 실행시간** (추정) | **월 단위** | **월 단위** |
| 메모리 | 수 TB | 수 TB |

**돌파점**:

- ✅ **활물질 2차 입자 클러스터 (30-50µm)** 수준 해상도
- ✅ CC 파단 개시/전파 메커니즘 직접 모사
- ✅ 분리막 **기공 폐쇄(pore closure)** 패턴 간접 포착
- ✅ 다층 간 **층간 미끄러짐(delamination)** 정밀 모사
- ✅ **단일 셀 내 ISC 전류 경로** 고해상도 맵핑

---

## 4. 티어별 비교 요약표

| Tier | 요소 수 (Stacked) | 요소 수 (Wound) | Δt (µs) | Phase 1 (4코어) | Phase 3 (8코어) | 하드웨어 | 목적 |
| ------ | ----------------- | ---------------- | --------- | ---------------- | ---------------- | --------- | ------ |
| **-1** | 6K | 23K | 9.0 | 2초 | 20초 | 워크스테이션 | 디버깅 |
| **0** | 57K | 210K | 4.0 | 42초 | 7분 | 워크스테이션 | 개발/DOE |
| **0.5** | 1.8M | 4.0M | 1.0 | 1.5시간 | 15시간 | 소규모 클러스터 | 프로덕션 |
| **1** | 200M | 500M | 0.3 | 일 | 주 | 대규모 HPC | 논문/연구 |
| **2** | 2B | 5B | 0.1 | 주 | 월 | 최대 규모 HPC | 첨단 연구 |

**Phase 1**: 구조만 (5ms)
**Phase 3**: 구조-열-전기 완전 연성 (20ms)
**실행 시간**: Intel Xeon E5-2690 v4 기준, 실제 성능은 ±30% 변동

---

## 5. 티어 선택 가이드

### 5.1 적층형 (Stacked) — `generate_mesh_stacked.py`

```python

from generate_mesh_stacked import CellDesign, MeshGenerator

# Tier -1: 디버깅

CellDesign(cell_width=45, cell_height=95, mesh_size_xy=5.0, n_unit_cells=5)

# Tier 0: 거시 응답

CellDesign(cell_width=45, cell_height=95, mesh_size_xy=2.5, n_unit_cells=15)

# Tier 0.5: 업계 표준

CellDesign(cell_width=45, cell_height=95, mesh_size_xy=0.5, n_unit_cells=20)

# Tier 1: 층별 해상도

CellDesign(cell_width=45, cell_height=95, mesh_size_xy=0.1, n_unit_cells=20,
           n_elem_cathode_thick=3, n_elem_anode_thick=3)

# Tier 2: 입자 클러스터

CellDesign(cell_width=45, cell_height=95, mesh_size_xy=0.05, n_unit_cells=20,
           n_elem_cathode_thick=5, n_elem_anode_thick=5)

```

### 5.2 와인딩형 (Wound) — `generate_mesh_wound.py`

```python

from generate_mesh_wound import FlatWoundDesign, FlatWoundMeshGenerator

# Tier -1: 디버깅

FlatWoundDesign(cell_width=45, cell_height=95, mesh_size_y=5.0, mesh_size_path=4.0,
                n_winds=5, r_mandrel=1.2)

# Tier 0: 거시 응답

FlatWoundDesign(cell_width=45, cell_height=95, mesh_size_y=2.5, mesh_size_path=2.0,
                n_winds=15, r_mandrel=1.2)

# Tier 0.5: 업계 표준

FlatWoundDesign(cell_width=45, cell_height=95, mesh_size_y=0.5, mesh_size_path=0.5,
                n_winds=20, r_mandrel=1.2)

# Tier 1: 층별 해상도

FlatWoundDesign(cell_width=45, cell_height=95, mesh_size_y=0.1, mesh_size_path=0.1,
                n_winds=20, r_mandrel=1.2,
                n_elem_cathode_thick=3, n_elem_anode_thick=3)

```

---

## 6. YAML 기반 티어 생성 (2026-02-17 업데이트)

모든 티어 설정은 `battery_config.yaml`에 정의되어 있습니다. 코드 수정 없이 YAML 파일만 편집하여 파라미터 변경 가능.

### 빠른 시작

```bash

# Tier -1 디버깅용

python generate_all_tiers.py --tier -1 --type stacked
python prepare_run.py --tier -1 --type stacked --phase 1
ls-dyna i=01_main_phase1_stacked.k ncpu=1

# Tier 0 개발용

python generate_all_tiers.py --tier 0 --type stacked
python prepare_run.py --tier 0 --type stacked --phase 1
ls-dyna i=01_main_phase1_stacked.k ncpu=4

# Tier 0.5 프로덕션

python generate_all_tiers.py --tier 0.5 --type stacked
python prepare_run.py --tier 0.5 --type stacked --phase 3
mpirun -np 256 ls-dyna i=01_main_phase3_stacked.k memory=16000m

```

### 실행 시간 추정

```bash

python estimate_runtime.py --all
python estimate_runtime.py --tier 0.5 --phase 3 --ncpu 256

```

---

## 7. 수렴성 검증

티어 간 결과 비교:

```bash

python convergence_study.py --tiers -1 0 0.5 --phase 1

```

**수렴 판정 기준**:

- Tier 0 → 0.5: <5% 차이 → Tier 0 충분
- Tier 0.5 → 1: <2% 차이 → Tier 0.5 수렴

---

*문서 버전: 2.0 (70×140mm 셀 기준)*
*최종 업데이트: 2026-02-17*
*참조: battery_config.yaml, estimate_runtime.py*

