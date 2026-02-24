# LS-DYNA R16 리튬이온 배터리 멀티피직스 시뮬레이션 — 기술 문서

> **프로젝트**: 파우치형 리튬이온 배터리 셀 측면 충격 → 내부 단락 → 열폭주 해석
> **솔버**: LS-DYNA R16 (MPP)
> **단위계**: mm, ton(10³ kg), s, N, MPa, mJ
> **최종 갱신**: 2026-02-19 (P0~P3 전항목 완료)

---

## 목차

1. [프로젝트 개요 및 해석 시나리오](#1-프로젝트-개요-및-해석-시나리오)
2. [파일 구조 및 모듈 관계도](#2-파일-구조-및-모듈-관계도)
3. [물리 모델링 — 구조](#3-물리-모델링--구조)
4. [물리 모델링 — 열](#4-물리-모델링--열)
5. [물리 모델링 — 전기화학 (EM Randles)](#5-물리-모델링--전기화학-em-randles)
6. [멀티피직스 연성](#6-멀티피직스-연성)
7. [재료 모델 상세](#7-재료-모델-상세)
8. [내부 단락 (ISC) 모델링](#8-내부-단락-isc-모델링)
9. [열폭주 모델링](#9-열폭주-모델링)
10. [벤팅 및 가스 발생](#10-벤팅-및-가스-발생)
11. [접촉 및 계면 처리](#11-접촉-및-계면-처리)
12. [메쉬 및 기하 모델](#12-메쉬-및-기하-모델)
13. [EM 모델 변형 (Solid / BatMac / TShell)](#13-em-모델-변형-solid--batmac--tshell)
14. [YAML 기반 파라메트릭 제어](#14-yaml-기반-파라메트릭-제어)
15. [해석 가능성 평가 및 검증 현황](#15-해석-가능성-평가-및-검증-현황)
16. [키워드 커버리지 — LSTC 공식 예제 대비](#16-키워드-커버리지--lstc-공식-예제-대비)

---

## 1. 프로젝트 개요 및 해석 시나리오

### 1.1 목적

리튬이온 파우치 배터리 셀이 측면 충격을 받아 **분리막 파손 → 내부 단락 → 줄 발열 → 열폭주 → 가스 벤팅**에 이르는 전 과정을 단일 LS-DYNA 해석으로 모사합니다.

### 1.2 3-Phase 해석 흐름

```text
Phase 1 (0~5 ms)          Phase 2 (5 ms~60 s)        Phase 3 (60 s~)
━━━━━━━━━━━━━━━━━        ━━━━━━━━━━━━━━━━━━━        ━━━━━━━━━━━━━━━━
측면 충격                  내부 단락 + 줄열            열폭주 + 벤팅
• 임팩터 5 m/s            • 분리막 erosion 감지       • Arrhenius 5단계
• 구조 변형               • Randles → 저항 대체       • 가스 발생
• 분리막 파괴             • I²R 줄열 발생             • 파우치 팽창/파열
                          • 열 확산                   • 전해질 분출

[구조만]                  [구조-열-EM 연성]           [구조-열-EM-ALE-Chemistry]
```

### 1.3 핵심 물리

| 물리 현상 | LS-DYNA 키워드 | 파일 |
| ----------- | --------------- | ------ |
| 고속 충격 + 대변형 | MAT_JOHNSON_COOK, MAT_CRUSHABLE_FOAM | 04_materials.k |
| 분리막 파괴 (erosion) | MAT_ADD_EROSION, CONTROL_TIMESTEP(ERODE=1) | 04_materials.k, 07_control*.k |
| 전기화학 등가회로 | EM_RANDLES_SOLID/BATMAC/TSHELL | 08_em_randles*.k |
| 내부 단락 저항 | EM_RANDLES_SHORT_ID + DEFINE_FUNCTION | 10_define_curves.k |
| 줄 발열 (I²R) | EM_RANDLES → R0TOTHERM | 08_em_randles*.k |
| 열폭주 (Arrhenius) | EM_RANDLES_EXOTHERMIC_REACTION | 10_define_curves.k |
| 열 전도/대류/복사 | CONTROL_THERMAL_SOLVER, BOUNDARY_CONVECTION/RADIATION | 06_boundary_loads*.k |
| 가스 벤팅 | AIRBAG_SIMPLE_AIRBAG_MODEL | 12_venting.k |
| 전해질 유동 | ALE (SECTION_SOLID_ALE, CLIS) | 13_ale_electrolyte.k |

---

## 2. 파일 구조 및 모듈 관계도

### 2.1 마스터 인클루드 구조

```text
01_main.k (마스터)
 ├── 02_mesh_stacked.k         ← 메쉬 (노드/요소/파트/섹션/세트)
 ├── 04_materials.k            ← 구조+열+EM 재료 (MID 1~8, TMID 101~108)
 ├── 04_materials_tempdep.k    ← 온도의존 테이블/함수 (TABLE 4003~4004, FUNC 6001~6002)
 ├── 05_contacts.k             ← 접촉 (ASTS, ASS, TIED_THERMAL×24, ERODING)
 ├── 06_boundary_loads.k       ← 경계조건 (SPC, 임팩터, 대류/복사, 초기온도)
 ├── 07_control.k              ← 솔버 제어 (시간스텝, 열/구조/EM 연성)
 ├── 08_em_randles.k           ← 전기화학 (TABLE, RANDLES, ISOPOTENTIAL, CIRCUIT)
 ├── 09_database.k             ← 출력 제어 (D3PLOT, GLSTAT, MATSUM)
 └── 10_define_curves.k        ← 커브/함수 (OCV, dU/dT, ISC함수, 열폭주함수)

선택적 추가:
 ├── 12_venting.k              ← Phase 3: 가스 벤팅
 └── 13_ale_electrolyte.k      ← Phase 3: ALE 전해질
```

### 2.2 Phase별 파일 변형

| 파일 | Phase 1 | Phase 2 | 비고 |
| ------ | --------- | --------- | ------ |
| 01_main | 01_main_phase1_stacked.k | 01_main_phase2_stacked.k | Phase별 include 조합 |
| 05_contacts | 05_contacts_phase1.k | 05_contacts_phase2.k | Phase 2에서 TIED_THERMAL 추가 |
| 06_boundary | 06_boundary_loads_phase1.k | 06_boundary_loads_phase2.k | Phase 2에서 열 BC 추가 |
| 07_control | 07_control_phase1.k | 07_control_phase2.k | Phase 2에서 열솔버 활성 |
| 09_database | 09_database_phase1.k | 09_database_phase2.k | Phase 2에서 열출력 추가 |

### 2.3 EM 모델 변형 파일

| 모델 유형 | 파일 | 적용 대상 |
| ----------- | ------ | ----------- |
| EM_RANDLES_SOLID | 08_em_randles.k | 적층형 (Stacked) 파우치 셀 |
| EM_RANDLES_SOLID | 08_em_randles_wound.k | 원통형 (Wound/Cylindrical) 셀 |
| EM_RANDLES_SOLID | 08_em_randles_tier-1.k | Tier-1 간소화 (5 UC) |
| EM_RANDLES_BATMAC | 08_em_randles_batmac.k | BatMac 매크로 모델 |
| EM_RANDLES_TSHELL | 08_em_randles_tshell.k | 두꺼운 셸 (TShell) 모델 |

---

## 3. 물리 모델링 — 구조

### 3.1 요소 유형

| 부품 | 요소 타입 | ELFORM | 비고 |
| ------ | ---------- | -------- | ------ |
| Al CC (12µm) | Shell | 2 (Belytschko-Lin-Tsay) | 박판 → 셸 적합 |
| Cu CC (8µm) | Shell | 2 | 〃 |
| NMC 양극 (70µm) | Solid | 1 (Const. stress) | 다공질 압축 거동 |
| Graphite 음극 (80µm) | Solid | 1 | 〃 |
| PE 분리막 (25µm) | Solid | 1 | Erosion 대상 |
| 파우치 (115µm) | Shell | 2 | Al-laminate 복합 |
| 전해질 | Solid | 1 | 기공 충진 |

### 3.2 구조 재료 모델

```text
Al CC (MID=1)      → MAT_015 Johnson-Cook + MAT_ADD_EROSION
                     σ = (90 + 125·εₚ^0.22)(1 + 0.014·ln(ε̇*))(1 - T*^1.0)
                     JC 손상: D1=0.13, D2=0.13, D3=-1.50, D4=0.011

Cu CC (MID=2)      → MAT_015 Johnson-Cook + MAT_ADD_EROSION
                     σ = (200 + 292·εₚ^0.31)(1 + 0.025·ln(ε̇*))(1 - T*^1.09)
                     JC 손상: D1=0.54, D2=4.89, D3=-3.03, D4=0.014

NMC 양극 (MID=3)  → MAT_063 Crushable Foam
                     비선형 압축: LCID=-4003 (온도의존 TABLE)
                     TSC=2.0 MPa (인장 파괴 강도)

Graphite (MID=4)   → MAT_063 Crushable Foam
                     비선형 압축: LCID=-4004 (온도의존 TABLE)
                     TSC=1.5 MPa (인장 파괴 강도)

PE 분리막 (MID=5)  → MAT_024 Piecewise Linear Plasticity
                     σ_y=15 MPa, E_tan=500 MPa, FAIL=0.6
                     Cowper-Symonds: C=100, P=4 (변형률속도 강화)
                     + MAT_ADD_EROSION: SIGVM=25, SIGP1=30, MXEPS=0.6

파우치 (MID=6)     → MAT_024 + MAT_ADD_EROSION
                     σ_y=40 MPa, E_tan=800 MPa
                     파열 기준: MXPRS=0.6 MPa, MXEPS=0.20

임팩터 (MID=7)     → MAT_020 Rigid
                     강재: ρ=7.85e-6 ton/mm³, E=210 GPa

전해질 (MID=8)     → MAT_001 Elastic
                     E=100 MPa, ν=0.45 (준액상 근사)
```

### 3.3 손상 및 파괴

| 부품 | 모델 | 파괴 기준 | 의미 |
| ------ | ------ | ----------- | ------ |
| Al CC | JC 손상 (D1~D5) | 누적 등가 소성 변형률 | 집전체 관통 파괴 |
| Cu CC | JC 손상 (D1~D5) | 〃 | 〃 |
| 분리막 | GISSMO + ADD_EROSION | von Mises>25 / σ₁>30 / ε>0.6 | **내부 단락 트리거** |
| 파우치 | ADD_EROSION | MXPRS>0.6 / MXEPS>0.20 | 벤팅 트리거 |

> **핵심**: 분리막이 erosion으로 삭제되면 EM 솔버가 `ero` 변수를 통해 감지하고, `DEFINE_FUNCTION 5001`이 단락 저항을 반환하여 Randles 회로를 저항으로 대체합니다.

---

## 4. 물리 모델링 — 열

### 4.1 열 재료

| TMID | 부품 | ρ (ton/mm³) | Cp (mJ/ton·K) | k (mW/mm·K) | 비고 |
| ------ | ------ | ------------- | ---------------- | ------------- | ------ |
| 101 | Al CC | 2.70e-6 | 903 | 0.238 | 등방 |
| 102 | Cu CC | 8.96e-6 | 385 | 0.398 | 등방 |
| 103 | NMC 양극 | 2.50e-6 | 700 | 3.0/3.0/1.5 | **이방성** (면내/두께) |
| 104 | Graphite 음극 | 1.35e-6 | 700 | 5.0/5.0/2.0 | **이방성** (면내/두께) |
| 105 | PE 분리막 | 0.95e-6 | 1900 | 0.33×10⁻³ | 상변화: T_lat=403K, H_lat=145 kJ/kg |
| 106 | 파우치 | 2.10e-6 | 1200 | 0.50×10⁻³ | 등방 유효 |
| 108 | 전해질 | 1.20e-6 | 2050 | 0.60×10⁻³ | 등방 |

### 4.2 열 경계조건

| 유형 | 키워드 | 파라미터 | 적용면 |
| ------ | -------- | ---------- | -------- |
| 자연 대류 | BOUNDARY_CONVECTION_SET | h = 5.0e-6 mW/(mm²·K), T∞ = 298.15K | 파우치 외면 |
| 복사 | BOUNDARY_RADIATION_SET | σ = 5.67e-14 (Stefan-Boltzmann, mW 단위), T∞ = 298.15K | 파우치 외면 |
| 초기 온도 | INITIAL_TEMPERATURE_SET | T₀ = 298.15K (25°C) | 전체 |

### 4.3 열원

| 열원 | 메커니즘 | 구현 |
| ------ | --------- | ------ |
| 기계적 일 → 열 | FWORK=0.9 (90% 변환) | CONTROL_THERMAL_SOLVER |
| 줄열 (I²R) | R0TOTHERM=1 | EM_RANDLES Card 5 |
| 가역열 (dU/dT) | DUDT=-2002 (커브 참조) | EM_RANDLES Card 5 |
| 열폭주 (Arrhenius) | FUNCTID=5002 | EM_RANDLES_EXOTHERMIC_REACTION |

### 4.4 열 이방성 (전극)

전극 코팅은 입자 적층 구조로 인해 면내(in-plane)와 두께방향(through-plane) 열전도도가 크게 다릅니다:

```text
NMC 양극:   k_in-plane = 3.0 W/(m·K)    k_through = 1.5 W/(m·K)    비율 2:1
Graphite:   k_in-plane = 5.0 W/(m·K)    k_through = 2.0 W/(m·K)    비율 2.5:1
```

MAT_THERMAL_ORTHOTROPIC (TMID 103, 104)으로 구현. AOPT=0, a=(0,0,1), d=(1,0,0)으로 두께방향 = Z축 정렬.

### 4.5 분리막 상변화

PE 분리막의 용융(130°C / 403K)을 잠열(latent heat)로 모사:

- `TLAT = 403.0` (용융점, K)
- `HLAT = 145000.0` (잠열, J/kg = mJ/ton)
- 결정도 ~50%: ΔH = 0.5 × 290 kJ/kg ≈ 145 kJ/kg

분리막 용융 시 열용량이 급증하여 온도 상승을 지연시키는 효과를 모사합니다.

---

## 5. 물리 모델링 — 전기화학 (EM Randles)

### 5.1 Randles 등가회로

```text
       R₀          R₁
   ───/\/\/──┬──/\/\/──┬── V_terminal
             │         │
            ─┤─       ─┤─
          C_dl│       C₁│
            ─┤─       ─┤─
             │         │
   ──────────┴─────────┴──

   V_oc(SOC) = OCV 커브 (LCID 2001)
   V_terminal = V_oc - I·R₀ - V_RC₁
```

- **RDLTYPE=1**: 1차 Randles (R₀ + R₁∥C₁)
- R₀: 옴 저항 (전해질 이온 전도, 접합 저항)
- R₁∥C₁: 전하 이동 저항 + 이중층 커패시턴스

### 5.2 SOC 및 온도 의존성 — 2D TABLE 보간

R₀, R₁, C₁은 SOC와 온도 모두에 의존합니다. DEFINE_TABLE을 통한 2D 보간:

```text
TABLE 8001 (R0_charge):
  T=253K → CURVE 8011: R0(SOC) = [0.050, 0.045, ..., 0.050] Ω
  T=273K → CURVE 8012: R0(SOC) = [0.035, 0.032, ..., 0.038] Ω
  T=298K → CURVE 8013: R0(SOC) = [0.025, 0.022, ..., 0.028] Ω
  T=318K → CURVE 8014: R0(SOC) = [0.020, 0.018, ..., 0.022] Ω
  T=333K → CURVE 8015: R0(SOC) = [0.018, 0.016, ..., 0.020] Ω

같은 구조가 TABLE 8001~8006까지 6개:
  8001: R0 충전 / 8002: R0 방전
  8003: R1 충전 / 8004: R1 방전
  8005: C1 충전 / 8006: C1 방전
```

RANDLES Card 3에서 **음수 TABLE ID**로 참조: `-8001, -8002, -8003, -8004, -8005, -8006`

### 5.3 OCV (Open Circuit Voltage)

LCID 2001: NMC/Graphite 풀셀 OCV vs SOC

```text
SOC    OCV (V)
0.00   3.000    ← 완전 방전
0.10   3.480
0.30   3.650
0.50   3.750    ← 초기 상태 (SOCINIT=0.5)
0.70   3.870
0.90   4.080
1.00   4.200    ← 완전 충전
```

### 5.4 가역열 (Reversible Heat)

LCID 2002: dU/dT vs SOC (V/K)

전기화학 반응의 엔트로피 변화에 의한 가역적 발열/흡열:

- `Q_rev = I · T · dU/dT`
- 양수 → 발열, 음수 → 흡열
- 전형적 범위: ±0.3 mV/K

### 5.5 SOC Shift

SOC shift 모델은 셀 내 SOC 불균일을 모사합니다:

- `USESOCS=1`: 활성화
- `TAUSOCS=1000 s`: 완화 시간 상수 (diffusion timescale)
- `SICSLCID=-2004`: shift 커브

물리적 의미: 전극 두께 방향의 리튬 농도 구배로 인해 국소적 SOC가 전체 평균과 다를 수 있음. 이 차이가 국소적 과전압을 유발하여 열 불균일성을 증가시킵니다.

### 5.6 동전위면 (ISOPOTENTIAL) 및 회로 연결

```text
[양극 CC 표면] ──── ISOPOTENTIAL (randType=5) ────┐
                                                     ├── CONNECT (ground)
[음극 CC 표면] ──── ISOPOTENTIAL (randType=1) ────┘

셀 간 직렬 연결:
  Cell 1 양극 ─── CONNECT (V=0, connType=1) ─── Cell 2 음극
  Cell 2 양극 ─── CONNECT (V=0, connType=1) ─── Cell 3 음극
  ...
  Cell 5 양극 ─── CONNECT (R=0.05Ω, connType=2) ─── 외부 단자
  접지: 외부 음극 ─── CONNECT (connType=3)
```

- `randType=5`: 양극(positive) 탭 → Randles 회로의 양극 전위면
- `randType=1`: 음극(negative) 탭 → Randles 회로의 음극 전위면
- `setType=2`: Part Set으로 표면 지정

---

## 6. 멀티피직스 연성

### 6.1 연성 구조

```text
          ┌─────────────┐
          │  구조 솔버   │ ← 변형, 응력, erosion
          └──────┬──────┘
                 │ FWORK=0.9 (기계적 일→열)
                 │ erosion 정보 → EM 솔버
          ┌──────▼──────┐
          │   열 솔버    │ ← 온도 분포
          └──────┬──────┘
                 │ FRTHER=1 (온도→EM)
                 │ DUDT (가역열)
          ┌──────▼──────┐
          │  EM 솔버     │ ← 전류, 전압, SOC
          └──────┬──────┘
                 │ R0TOTHERM=1 (줄열→열)
                 │ EXOTHERMIC (열폭주→열)
          ┌──────▼──────┐
          │   열 솔버    │ (피드백 루프)
          └─────────────┘
```

### 6.2 EM→열 연성 키워드

```text
*EM_CONTROL_COUPLING
  THCPL=2    ← 열-EM 양방향 연성 (EM→열: 줄열 전달, 열→EM: 온도 의존 파라미터)
  SMCPL=1    ← 구조-EM 단방향 연성 (변형 → 요소 면적 변화 반영)
```

### 6.3 열→구조 피드백

```text
*MAT_ADD_THERMAL_EXPANSION
  MID=1~8 각 재료에 CTE 지정:
    Al CC:    23.1e-6 /K
    Cu CC:    16.5e-6 /K
    NMC:      10.0e-6 /K
    Graphite: 5.0e-6 /K
    분리막:   100.0e-6 /K  ← PE 고분자 큰 열팽창
    파우치:   23.0e-6 /K
    전해질:   100.0e-6 /K

→ 열팽창에 의한 내부 구속 응력 → 추가 변형/파괴 촉진
```

---

## 7. 재료 모델 상세

### 7.1 Johnson-Cook 구성 방정식 (Al/Cu 집전체)

$$\sigma = \underbrace{(A + B\varepsilon_p^N)}_{\text{strain hardening}} \underbrace{(1 + C\ln\dot{\varepsilon}^*)}_{\text{rate sensitivity}} \underbrace{(1 - T^{*M})}_{\text{thermal softening}}$$

여기서 $T^* = (T - T_r) / (T_m - T_r)$

| 파라미터 | Al CC (MID=1) | Cu CC (MID=2) | 단위 |
| ---------- | -------------- | -------------- | ------ |
| A (항복) | 90 | 200 | MPa |
| B (경화) | 125 | 292 | MPa |
| N (경화지수) | 0.22 | 0.31 | — |
| C (속도감도) | 0.014 | 0.025 | — |
| M (열연화) | 1.0 | 1.09 | — |
| T_m (융점) | 933 | 1356 | K |
| T_r (기준온도) | 298.15 | 298.15 | K |
| ε₀ (기준변형률속도) | 1.0 | 1.0 | /s |

### 7.2 Johnson-Cook 손상 모델

$$D = \sum \frac{\Delta\varepsilon_p}{\varepsilon_f(\sigma^*, \dot{\varepsilon}^*, T^*)}$$

$$\varepsilon_f = (D_1 + D_2 e^{D_3 \sigma^*})(1 + D_4 \ln\dot{\varepsilon}^*)(1 + D_5 T^*)$$

D=1 도달 시 요소 삭제 (erosion).

### 7.3 Crushable Foam (전극 코팅)

NMC 양극(MID=3)과 Graphite 음극(MID=4)은 다공질 복합 재료로, 압축 시 비선형 응력-체적변형률 관계를 보입니다:

| 체적변형률 | NMC 응력 (MPa) | Graphite 응력 (MPa) |
| ----------- | --------------- | ------------------- |
| 5% | 5 | 8 |
| 10% | 15 | 22 |
| 20% | 70 | 100 |
| 30% | 250 | 400 |
| 40% | 1000 | 1500 |
| 50% | 4000 | 5000 |

**온도 의존**: DEFINE_TABLE 4003/4004에서 온도별 스케일링. 고온에서 강도 저하.

### 7.4 Piecewise Linear Plasticity + Cowper-Symonds (분리막)

$$\sigma_y' = \sigma_y \left(1 + \left(\frac{\dot{\varepsilon}}{C}\right)^{1/P}\right)$$

- C=100 /s, P=4: PE 고분자의 변형률속도 강화
- FAIL=0.6: 등가 소성 변형률 60%에서 파괴
- TSC=15 MPa: 인장 컷오프

### 7.5 EM 재료

| MID | 부품 | mtype | σ — 정확 모드 (기본) | σ — 단순 모드 | 이론 |
| ----- | ------ | ------- | -------------------- | ------------- | ------ |
| 1 | Al CC | 2 (도체) | -6001 (T-dep) | -6001 | FEM 전류분포 계산 |
| 2 | Cu CC | 2 (도체) | -6002 (T-dep) | -6002 | 〃 |
| 3 | NMC | 1 | -6003 (T-dep, 0.5 S/m) | 0 | 전극 전자전도도 |
| 4 | Graphite | 1 | -6004 (T-dep, 3e4 S/m) | 0 | 〃 |
| 5 | 분리막 | 1 | -6005 (≈1e-10, 절연) | 0 | 전기 절연 |
| 6 | 파우치 | 1 | 1e-10 (고정) | 1e-10 | 전기 절연 |
| 7 | 임팩터 | 1 | 0 | 0 | EM 도메인 밖 |
| 8 | 전해질 | 1 | 0 (고정) | 0 | 이온전도 ≠ 전자전도 |

**모드 전환** (`generate_materials.py`):

```bash
python generate_materials.py                          # 정확 모드 (기본)
python generate_materials.py --em-sigma-simplified    # 단순 모드
```

단순 모드 사용 조건: EM_RANDLES 회로만으로 전극 전기화학을 완전히 모델링하고,
전극 내 전자 수송 해상도가 불필요한 경우.

**mtype 설명**:

- `mtype=1`: EM 솔버가 이 Part를 직접 계산하지 않음 (SIGMA=0) 또는 온도함수로 직접 계산.
- `mtype=2`: FEM으로 전류밀도 분포를 직접 계산. 집전체 (Al/Cu)에만 적용.

**온도 의존 전도도** (DEFINE_FUNCTION 6001–6005):

```text
σ_Al(T)  = 3.50e7 / (1 + 0.0038·(T-298.15))   [S/m]  → FUNCTID 6001
σ_Cu(T)  = 5.96e7 / (1 + 0.0039·(T-298.15))   [S/m]  → FUNCTID 6002
σ_NMC(T) = 5.00e-1 / (1 + 0.001·(T-298.15))   [S/m]  → FUNCTID 6003
σ_Gr(T)  = 3.00e4  / (1 + 0.0005·(T-298.15))  [S/m]  → FUNCTID 6004
σ_Sep    = 1.00e-10 (상수)                      [S/m]  → FUNCTID 6005
```

고온에서 전기 저항 증가 → 전류 분포 변화 + 추가 줄열.

---

## 8. 내부 단락 (ISC) 모델링

### 8.1 트리거 메커니즘

```text
충격 → 분리막 대변형 → MAT_ADD_EROSION 기준 충족 → 요소 삭제
                                                          │
                                                          ▼
                              EM 솔버: ero 변수 감지 (ero>0.5)
                                                          │
                                                          ▼
                              DEFINE_FUNCTION 5001 반환: R_short (양수)
                                                          │
                                                          ▼
                              해당 Randles 회로 → 저항 R_short로 대체
                                                          │
                                                          ▼
                              I = V_oc / R_short → I²R 줄열 발생
```

### 8.2 4가지 ISC 유형

LSTC 공식 침식 플래그(Vol_III p.515):

- `ero = 1`: CCP(양극CC) 침식
- `ero = 10`: CCN(음극CC) 침식
- `ero = 100`: 분리막 침식
- `ero = 1000`: 양극 활물질 침식
- `ero = 10000`: 음극 활물질 침식
- 복합: 합산 (예: `ero = 10001` → CCN + 음극 동시 침식)

```text
우리 DEFINE_FUNCTION 5001의 ISC 유형 판별:

CC간 거리(distCC) 기반:
  distCC < 0.05 mm → Type 4: Al-Cu (금속↔금속), R = 0.1 mΩ (최위험)
  distCC < 0.15 mm → Type 2/3: Al-An or Ca-Cu, R = 1 mΩ
  distCC ≥ 0.15 mm → Type 1: Ca-An (가장 일반), R = 10 mΩ

추가 보정:
  온도 보정: R = R_base · exp(-0.002·(T-298.15))  → 고온 시 저항↓
  응력 보정: vmstress > 50MPa 시 R ∝ 50/vmstress  → 고압축 시 접촉면적↑ → 저항↓
  최소 제한: R ≥ 0.01 mΩ (수치 안정)
```

### 8.3 EM_RANDLES_SHORT_ID

R16에서 도입된 개선된 SHORT 키워드:

```lsdyna
*EM_RANDLES_SHORT_ID
$  SHORTID      TYPE  AREATYPE      LCID
         1                   2      5001
```

- `SHORTID=1`: 각 RANDLES Card 7에서 참조하는 단락 ID
- `AREATYPE=2`: 전체 셀 면적 대비 스케일링 (Ω 단위)
- `LCID=5001`: 단락 저항 함수 ID

vs 이전 `*EM_RANDLES_SHORT`:

- SHORT_ID는 셀별로 다른 단락 함수를 지정 가능 (SHORTID로 구분)
- 우리 모델은 전 셀에 동일한 SHORTID=1 적용 (동일 물리)

---

## 9. 열폭주 모델링

### 9.1 5단계 Arrhenius 반응 체인

$$\dot{Q} = A_i \cdot H_i \cdot \exp\left(-\frac{E_{a,i}}{R \cdot T}\right)$$

| 단계 | 반응 | $T_{onset}$ | $E_a$ (kJ/mol) | $A$ (/s) | $H$ (kJ/mol) | SOC 의존 |
| ------ | ------ | ------------ | ---------------- | ---------- | ------------- | ---------- |
| 1 | SEI 분해 | 353K (80°C) | 135 | 1.67×10¹⁵ | 257 | — |
| 2 | 음극-전해질 | 393K (120°C) | 90 | 2.5×10¹³ | 155 | ∝ SOC |
| 3 | 전해질 분해 | 423K (150°C) | 110 | 5.0×10¹² | 180 | — |
| 4 | 양극 분해 | 473K (200°C) | 100 | 6.67×10¹³ | 115 | ∝ (1-SOC) |
| 5 | 바인더(PVDF) | 523K (250°C) | 150 | 1.0×10¹⁴ | 60 | — |

### 9.2 SOC 의존성

- **2단계** (음극-전해질): 발열량 ∝ SOC. 완전충전(SOC=1.0) 시 리튬화 graphite 양이 최대 → 최대 발열.
- **4단계** (양극 분해): 발열량 ∝ (1-SOC). 완전충전 시 탈리튬화 NMC 양이 최대 → 산소 방출 극대.

### 9.3 누적 제한

```c
float H_max = 1.0e5;
if (H_ex > H_max) return 0.0;
```

총 누적 발열이 $10^5$ mJ에 도달하면 반응 정지 (에너지 소진). 물리적으로는 반응물 고갈에 대응합니다.

### 9.4 LSTC 공식 예제 대비

| 특성 | LSTC basic_exothermal | 우리 모델 |
| ------ | --------------------- | ----------- |
| 인수 | 4개 (time, temp, SOC, H_ex) | **10개** (LSTC 공식 시그니처 준수) |
| 반응 단계 | 1단계 (단순 조건) | **5단계 Arrhenius** |
| SOC 의존 | 없음 | ✅ (2,4단계) |
| 반응물 소진 | 없음 | ✅ (H_max) |

---

## 10. 벤팅 및 가스 발생

가스 팽창 시나리오 (`01_main_gas_*.k`)에 통합. `12_venting.k` + `16_gas_generation_standalone.k` 포함.

### 10.1 AIRBAG 모델

```text
*AIRBAG_SIMPLE_AIRBAG_MODEL
  SID=503  (SET_SEGMENT_GENERAL: Parts 10+11+12 파우치 내면)
  Cv=723 J/kg/K, Cp=1004 J/kg/K (CO2 근사)
  T=298.15 K (유입 가스 온도)
  LCID=-12010  → FUNCTID 12010 호출 (온도 기반 Arrhenius 가스 발생율)
  AREA=-12003  → LCID 12003 (벤팅 면적 vs 절대압력)
  PE=0.1 MPa (대기압), RO=1.0e-9 ton/mm³
```

LCID 음수 표기 규칙 (LS-DYNA R16): `LCID < 0` → `|LCID|` 번호의 DEFINE_FUNCTION 호출.
FUNCTID 12010 인수 순서: `(float time, float temp, float pressure, float volume)`.

파우치 내부를 밀폐 가스 공간으로 처리. 전해질 분해 가스 발생 시:

- 파우치 내압 상승
- 파우치 팽창 (구조 연성)
- MXPRS=0.6 MPa 초과 시 파열 (MAT_ADD_EROSION)

### 10.2 벤팅 로직

1. 외부 열플럭스 = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011] → 온도 상승
   - q_conv(t): 강제대류, BOUNDARY_HEAT_SET HLCID=9010, 시간 이력 커브
   - q_rad(T): Stefan-Boltzmann 복사, BOUNDARY_HEAT_SET HLCID=-9011, ε·σ·(T⁴−T_amb⁴)
2. T > 353 K (80°C): SEI 분해 → 가스 발생 시작 (FUNCTID 12010, Ea=60 kJ/mol)
3. T > 423 K (150°C): 전해질 분해 → 급격한 가스 발생 (Ea=80 kJ/mol)
4. 파우치 내압 > 0.3 MPa (게이지 0.2 MPa): 안전밸브 개방 시작 (LCID 12003)
5. 내압 > 1.0 MPa: 최대 벤팅 면적 2 mm² → 파우치 파열

### 10.3 관련 LCID/FUNCTID 요약

| ID | 유형 | 파일 | 역할 |
| -- | ---- | ---- | ---- |
| 9010 | LCID | `10_define_curves_gas.k` | 강제대류 열플럭스 q_conv(t) vs 시간 (5000 W/m²), HLCID=9010 |
| 9011 | FUNCTID | `16_gas_generation_standalone.k` | **복사 열플럭스** q_rad(T)=ε·σ·(T⁴−T_amb⁴) [mJ/(s·mm²)], HLCID=-9011로 연결 |
| 12001 | LCID | `12_venting.k` | 가스 발생율 vs 시간 (placeholder, 미사용) |
| 12003 | LCID | `12_venting.k` | 벤팅 출구 면적 vs 절대압력 |
| 12005 | LCID | `12_venting.k` | 가스 온도 vs 시간 (보조) |
| 12010 | FUNCTID | `12_venting.k` | **AIRBAG 연결** — 온도 기반 가스 발생율 (4-arg: time, temp, pressure, volume) |

> 총 열플럭스: q_total = q_conv(t) + q_rad(T). 두 개의 BOUNDARY_HEAT_SET이 SID=3 세그먼트에 합산 적용됨.
> FUNCTID 9011: HLCID가 음수이면 LS-DYNA가 해당 FUNCTID를 (time, temp) 인수로 호출하여 절대 열플럭스를 반환받음.
> FUNCTID 12010: AIRBAG LCID=-12010, (time, temp, pressure, volume) 4인수 규약으로 가스 발생율 [kg/s] 반환.

---

## 11. 접촉 및 계면 처리

### 11.1 접촉 유형 요약

| CID | 유형 | 서피스 | 목적 |
| ----- | ------ | -------- | ------ |
| 1 | AUTOMATIC_SURFACE_TO_SURFACE | 임팩터 ↔ 파우치 | 충격 |
| 2 | AUTOMATIC_SINGLE_SURFACE (SOFT=2) | 셀 내부 | 자기접촉 |
| 301~324 | TIED_SURFACE_TO_SURFACE_THERMAL | 층간 (Al↔NMC, NMC↔Sep, ...) | **열전달** |
| 401 | ERODING_SURFACE_TO_SURFACE | 분리막 영역 | 침식 후 접촉 |
| 501~502 | TIED_SURFACE_TO_SURFACE | 파우치 ↔ 스택 | 접합 |
| 601~602 | TIED_NODES_TO_SURFACE | PCM ↔ 탭 | 집전 |

### 11.2 TIED THERMAL 접촉의 열전도도

| 계면 | 열전도도 (mW/mm·K) | 물리적 근거 |
| ------ | ------------------- | ------------- |
| CC ↔ 전극 | 100. | 얇은 바인더 층 경유 |
| 전극 ↔ 분리막 | 50. | 전해질 함침 계면 |
| UC간 (Cu ↔ Al) | 80. | 전해질 함침 + 약간의 공극 |

### 11.3 Mortar 대안

`05_contacts_mortar.k`에 Mortar 기반 접촉 대안 구현:

- `CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_MORTAR_ID`: 대변형에 강건
- `CONTACT_AUTOMATIC_SINGLE_SURFACE_MORTAR_ID`: 침투 방지 향상
- TIED_THERMAL은 penalty 유지 (변형 작아 mortar 불필요)

---

## 12. 메쉬 및 기하 모델

### 12.1 파우치 셀 제원

| 항목 | 값 |
| ------ | --- |
| 셀 타입 | 파우치 (pouch) |
| 치수 | 약 100 × 50 × (단위셀×N_uc) mm |
| 용량 | 2.6 Ah (2600 mAh) |
| 공칭 전압 | 3.7 V (NMC/Graphite) |
| 초기 SOC | 50% |

### 12.2 단위셀 구성

```text
         ┌──────────────────────┐  ←  Al CC (12µm)     PID x001
         ├──────────────────────┤  ←  NMC 양극 (70µm)    PID x002
         ├──────────────────────┤  ←  PE 분리막 (25µm)    PID x003
         ├──────────────────────┤  ←  Graphite 음극 (80µm) PID x004
         └──────────────────────┘  ←  Cu CC (8µm)        PID x005

         x = 10 × UC번호: UC00→1001~1005, UC01→1011~1015, ...
```

### 12.3 메쉬 계층 (Tier)

| Tier | 단위셀 수 | EM 파일 | 용도 |
| ------ | ---------- | --------- | ------ |
| -1 (개발) | 5 | 08_em_randles_tier-1.k | 디버깅, 빠른 검증 |
| 0 (기본) | 20 | 08_em_randles.k | 기본 프로덕션 |
| 0.5 (현재 메쉬) | 20 | 02_mesh_stacked.k | 4.3M 라인 메쉬 |
| 1 (고해상도) | 50+ | generate_*.py로 생성 | 수렴 검증 |

### 12.4 Part ID 체계

```text
1001~1005: UC00 (Al, NMC, Sep, Graphite, Cu)
1011~1015: UC01
1021~1025: UC02
  ...
1191~1195: UC19 (20개 단위셀)

10, 11, 12: 파우치 (상면, 하면, 측면)
13: 전해질
30, 31: PCM (양극/음극 탭)
100: 임팩터
```

---

## 13. EM 모델 변형 (Solid / BatMac / TShell)

### 13.1 3가지 접근법 비교

| 항목 | EM_RANDLES_SOLID | EM_RANDLES_BATMAC | EM_RANDLES_TSHELL |
| ------ | ----------------- | ------------------- | ------------------- |
| **요소** | 5개 Part/UC (CC, 전극, 분리막) | 1개 Part/셀 (하나의 솔리드) | 1개 PART_COMPOSITE_TSHELL/셀 |
| **기하 해상도** | 각 층 개별 모델링 | 셀 레벨 lumped | 층별 속성은 유지하되 1요소 |
| **EM 재료** | EM_MAT_001 (mtype=1,2) | **EM_MAT_006** (mtype=5, σP/σN) | EM_MAT_001 + **randletype** |
| **계산 비용** | 높음 (5×요소, 24+접촉) | 낮음 (1×요소, 접촉 최소) | 중간 (1×복합셸) |
| **ISC 정밀도** | 높음 (층별 erosion 감지) | 중간 (셀 단위) | 높음 (층별 randletype) |
| **적합 시나리오** | 상세 단위셀 해석 | 모듈/팩 레벨 | 빠른 셀 레벨 해석 |

### 13.2 BatMac 고유 키워드

```lsdyna
*EM_MAT_006
$  MID  MTYPE  SIGMAP  SIGMAN
  3001      5     500     500
```

- `mtype=5`: BatMac 전용. 셀 내부를 등방 전도체로 취급
- `SIGMAP`: 양극 방향 전도도 (S/mm)
- `SIGMAN`: 음극 방향 전도도 (S/mm)

### 13.3 TShell 고유 키워드

```lsdyna
*PART_COMPOSITE_TSHELL
TShell Cell 1
  4001    5    0.833    ...    0    0
$ MID1  THICK1  B1  ITHID1  MID2  THICK2  B2  ITHID2
    11  0.0150  0.  1       12    0.0700  0.  1
    13  0.0250  0.  1       14    0.0800  0.  1
    15  0.0100  0.  1       ...
```

- `ELFORM=5`: PART_COMPOSITE_TSHELL 전용 두꺼운 셸
- `SHRF=0.833`: 전단 보정 계수 (5/6)
- 층별 `randletype`: 1(CCP), 2(양극), 3(분리막), 4(음극), 5(CCN)

### 13.4 파일별 ISOPOTENTIAL/CONNECT 구성

| 파일 | ISO 수 | CONNECT 수 | 특이사항 |
| ------ | -------- | ----------- | ---------- |
| Stacked (5UC) | 10+2=12 | 4+1+1=6 | 5셀 직렬+외부+접지 |
| Wound (1UC) | 1+1=2 | 1+1=2 | 단일 셀 |
| Tier-1 (5UC) | 10+2=12 | 4+1+1=6 | Stacked과 동일 |
| BatMac (5셀) | 10+2=12 | 4+1+1+1+5=12 | SET_PART 기반 |
| TShell (5셀) | 10+2=12 | 접지만 1 | 간소화 |

---

## 14. YAML 기반 파라메트릭 제어

### 14.1 구조

```yaml
battery_config.yaml:
  cell:          # 셀 제원 (치수, 용량, 전압)
  materials:     # 8개 구조재료 파라미터
  thermal:       # 열재료 파라미터
  mesh:          # 메쉬 해상도, 단위셀 수
  em:            # EM 솔버 파라미터
    randles:     # Randles 회로 파라미터 (Q, CQ, SOC 등)
    table_ids:   # TABLE ID 매핑 (-8001~-8006)
    soc_shift:   # SOC Shift 파라미터
    isopotential:# ISOPOTENTIAL 파라미터
  contacts:      # 접촉 파라미터
  control:       # 솔버 제어
  impactor:      # 임팩터 제원
  tiers:         # 메쉬 계층 정의
```

### 14.2 생성 스크립트

| 스크립트 | 입력 | 출력 | 기능 |
| --------- | ------ | ------ | ------ |
| generate_mesh_stacked.py | YAML | 02_mesh_stacked*.k | 적층형 메쉬 생성 |
| generate_mesh_wound.py | YAML | 03_mesh_wound*.k | 원통형 메쉬 생성 |
| generate_em_randles.py | YAML | 08_em_randles*.k | EM Randles 생성 |
| generate_contacts.py | YAML | 05_contacts*.k | 접촉 생성 |
| generate_all_tiers.py | YAML | 전체 tier 파일 | 다단계 메쉬 생성 |
| prepare_run.py | YAML + tier | 실행 디렉토리 | 실행 준비 + 동기화 |

---

## 15. 해석 가능성 평가 및 검증 현황

### 15.1 키워드 정확성 (감사 결과)

| 항목 | 상태 | 비고 |
| ------ | ------ | ------ |
| EM_RANDLES_SOLID Card 구조 (7 Cards) | ✅ | Card1~7 모두 정상 |
| TABLE 8001~8006 정의 + 30개 하위 CURVE | ✅ | SOC×Temperature 2D 보간 |
| EM_MAT mtype (CC=2, 전극/분리막=1) | ✅ | LSTC 규약 완전 일치 |
| ISOPOTENTIAL randType (5=양극, 1=음극) | ✅ | 5개 EM 파일 일관 |
| EM_RANDLES_SHORT_ID | ✅ | 구 SHORT → SHORT_ID 전면 업그레이드 |
| DEFINE_FUNCTION 5001 (20인수 LSTC 시그니처) | ✅ | 4모드 ISC + 온도/응력 보정 |
| DEFINE_FUNCTION 5002 (10인수 LSTC 시그니처) | ✅ | 5단계 Arrhenius |
| CONNECT 직렬/외부/접지 배선 | ✅ | connType = 1/2/3 정확 |
| EM_OUTPUT, EM_DATABASE | ✅ | 5개 EM 파일 모두 포함 |

### 15.2 알려진 제한/주의사항

| 번호 | 항목 | 상세 | 영향 |
| ------ | ------ | ------ | ------ |
| 1 | **UC 수 불일치** | 메쉬=20UC, EM/접촉=5UC | `prepare_run.py --tier`로 동기화 필요 |
| 2 | SOC shift 커브 단위 | 0~100 범위 (% vs 분수?) | 추후 LSTC 매뉴얼 확인 필요 |
| 3 | TABLE 공유 | wound/batmac/tshell이 stacked의 TABLE 참조 | 별도 실행 시 TABLE 파일 include 필요 |
| 4 | FUNC 5003 (두께→저항) | 정의되었으나 미참조 | 참조용 템플릿 (기능 영향 없음) |
| 5 | 경계 DOF/YAML 방향 불일치 | DOF=1(X) vs YAML z-direction | 실제 DOF 우선, YAML은 메타 정보 |

### 15.3 해석 실행 절차

```text
1. python prepare_run.py --tier -1    # Tier-1 (5UC) 동기화
2. ls-dyna i=01_main_phase1_stacked.k # Phase 1: 순수 기계
3. 결과 검증 (변형, erosion 확인)
4. ls-dyna i=01_main_phase2_stacked.k # Phase 2: 열-EM 연성
5. 결과 검증 (온도, 전류, SOC, 단락 시점)
6. Phase 3: venting/ALE 추가 (선택)
```

### 15.4 검증 수행 이력

| 차수 | 내용 | 결과 |
| ------ | ------ | ------ |
| 감사 1~7 | 55건 수정 (하드코딩, YAML 통합, 키워드 오류) | 완료 |
| P0 (Critical) | 함수 시그니처, mtype, return 규약, ISOPOTENTIAL | 4/4 완료 |
| P1 (High) | TABLE R0/R1/C1, CC mtype=2, EM_CIRCUIT, 일관성 | 4/4 완료 |
| P2 (Medium) | FUNC_TAB, SOC Shift, BatMac, TShell, Erosion | 5/5 완료 |
| P3 (Low) | Implicit, Mortar, SHORT_ID, randType, fromTherm | 5/5 완료 |
| 최종 감사 | UC0 SHORTID 누락 버그, EM_MAT MID=7 누락 | 수정 완료 |

---

## 16. 키워드 커버리지 — LSTC 공식 예제 대비

### 16.1 LSTC 13개 예제 vs 우리 모델

| 키워드 | basic | exoth | socshift | tshell | batmac | 우리 모델 |
| -------- | ------- | ------- | ---------- | -------- | -------- | ----------- |
| EM_RANDLES_SOLID | ✅ | ✅ | ✅ | — | — | ✅ |
| EM_RANDLES_TSHELL | — | — | — | ✅ | — | ✅ |
| EM_RANDLES_BATMAC | — | — | — | — | ✅ | ✅ |
| EM_RANDLES_SHORT_ID | — | — | — | ✅ | ✅ | ✅ |
| EM_RANDLES_EXOTHERMIC | — | ✅ | — | — | ✅ | ✅ |
| EM_ISOPOTENTIAL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EM_ISOPOTENTIAL_CONNECT | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EM_MAT_001 (mtype=1) | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| EM_MAT_001 (mtype=2) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EM_MAT_005 (aniso) | — | — | — | — | ✅ | ✅ |
| EM_MAT_006 (BatMac) | — | — | — | — | ✅ | ✅ |
| DEFINE_TABLE (SOC×T) | — | — | — | — | ✅ | ✅ |
| DEFINE_FUNCTION_TAB | — | — | — | ✅ | ✅ | ✅ |
| CONTROL_IMPLICIT | — | — | — | — | ✅ | ✅ (opt) |
| CONTACT_MORTAR | — | — | — | — | ✅ | ✅ (opt) |

### 16.2 우리 모델만의 고급 기능

LSTC 예제에는 없지만 우리 모델에는 포함된 물리:

| # | 기능 | 물리적 의미 |
| --- | ------ | ------------ |
| 1 | **Johnson-Cook (CC)** | 변형률속도 + 온도 연화 + 손상: 실제 충격 조건 반영 |
| 2 | **Crushable Foam (전극)** | 다공질 전극의 비선형 압축: 정확한 변형 거동 |
| 3 | **Cowper-Symonds (분리막)** | 고분자 변형률속도 강화: 고속충격 시 분리막 강도 증가 |
| 4 | **GISSMO (분리막)** | 일반화 손상: 변형 이력 의존 파괴 |
| 5 | **MAT_ADD_THERMAL_EXPANSION** | 7개 재료 열팽창: 열에 의한 내부 구속 응력 |
| 6 | **MAT_THERMAL_ORTHOTROPIC** | 전극 이방성 열전도: 면내 vs 두께방향 |
| 7 | **분리막 상변화** | TLAT/HLAT: PE 용융 잠열 → 온도 상승 지연 |
| 8 | **5단계 Arrhenius** | SEI→음극-전해질→전해질→양극→바인더 순차 반응 |
| 9 | **4모드 ISC** | Ca-An / Al-An / Ca-Cu / Al-Cu 분류 + 거리/온도/응력 보정 |
| 10 | **AIRBAG 벤팅** | 전해질 분해 가스 + 파우치 팽창/파열 모사 |
| 11 | **온도의존 전도도** | CC 전도도 σ(T): 고온 시 줄열 증가 피드백 |
| 12 | **적응 메쉬** | CONTROL_REFINE_SOLID: 국소 세분화 (단락 영역) |
| 13 | **SOC×T 2D TABLE** | R0/R1/C1이 SOC와 온도 모두에 의존 (6개 TABLE, 30개 CURVE) |

---

## 부록 A: 단위 환산표

| 물리량 | SI 단위 | LS-DYNA (mm/ton/s) | 변환 |
| -------- | --------- | ------------------- | ------ |
| 길이 | m | mm | ×10³ |
| 질량 | kg | ton (10³ kg) | ×10⁻³ |
| 시간 | s | s | 1 |
| 힘 | N | N | 1 |
| 응력 | Pa | MPa | ×10⁻⁶ |
| 에너지 | J | mJ | ×10³ |
| 밀도 | kg/m³ | ton/mm³ | ×10⁻¹² |
| 전기전도도 | S/m | S/mm | ×10⁻³ |
| 열전도도 | W/(m·K) | mW/(mm·K) | ×10⁻³ |
| 비열 | J/(kg·K) | mJ/(ton·K) | 1 |
| 열전달계수 | W/(m²·K) | mW/(mm²·K) | ×10⁻⁶ |

## 부록 B: ID 번호 체계

```text
Material IDs:      1~8 (구조), 101~108 (열)
Part IDs:          1001~1195 (셀), 10~12(파우치), 30~31(PCM), 100(임팩터)
Section IDs:       1~3 (셸/솔리드)
Function IDs:      5001~5003 (ISC/열폭주/두께→R)
                   6001~6008 (온도의존 전도도)
TABLE IDs:         4003~4004 (전극 압축), 8001~8006 (Randles R/C)
Curve IDs:         1001~1002 (전극 압축)
                   2001~2004 (OCV, dU/dT, 외부전류, SOC shift)
                   3001 (임팩터 속도)
                   8011~8065 (TABLE 하위 커브)
Contact IDs:       1~2(충격/자기접촉), 301~324(TIED THERMAL), 401(ERODING)
                   501~502(파우치-스택), 601~602(PCM-탭)
ISO IDs:           1~5(음극탭), 6~10(양극탭), 11~12(외부단자)
CONNECT IDs:       1~4(직렬), 5(외부부하), 6(접지)
SET IDs:           1~2(SPC/임팩터), 102(내부접촉), 103~104(erosion), 503(벤팅)
```

---

*이 문서는 LS-DYNA R16 배터리 시뮬레이션 프로젝트의 전체 모델링 이론 및 구현 내역을 기술합니다.*
*LSTC 공식 13개 예제 대비 전수 검증 완료.*
