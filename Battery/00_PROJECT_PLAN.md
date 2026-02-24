# 리튬이온 파우치 배터리 셀 — 측면 충격 발화 멀티피직스 시뮬레이션

## 프로젝트 개요

스마트폰 크기 리튬이온 파우치 셀의 **각 층(집전체/전극/분리막)을 모두 명시적으로 모델링**하고,
**스택형(Stacked)과 와인딩형(Wound/Jellyroll)** 두 가지 구조를 모두 구현한다.
측면 임팩터로 충격 → 내부 단락(ISC) → 줄열/전기화학 열폭주 → 발화까지의
**구조-전기-열 멀티피직스** 연성 해석을 LS-DYNA R16으로 수행한다.

---

## 1. 셀 사양 (설계변수)

| 파라미터 | Stacked | Wound (Jellyroll) | 비고 |
| ---------- | --------- | ------------------- | ------ |
| 전체 크기 (W×H×T) | 70×140×5 mm | 70×140×5 mm | 스마트폰 크기 |
| 양극 집전체 (Al) | 12 µm | 12 µm | MAT_024 |
| 양극 코팅 (NMC) | 65 µm ×2면 | 65 µm ×2면 | MAT_063/HONEYCOMB |
| 분리막 (PE) | 20 µm | 20 µm | MAT_024 + 파괴 |
| 음극 코팅 (Graphite) | 70 µm ×2면 | 70 µm ×2면 | MAT_063/HONEYCOMB |
| 음극 집전체 (Cu) | 8 µm | 8 µm | MAT_024 |
| 전해질 | 코팅 내 함침 | 코팅 내 함침 | 열물성만 반영 |
| 단위셀 두께 | ~330 µm | ~330 µm | Al+양극+분리막+음극+Cu |
| 적층 수 | **15단위셀** ≈ 4.95mm | 연속 와인딩 | 설계변수 |
| 파우치 | 153 µm (Al-라미네이트) | 153 µm | MAT_024 |
| 탭 (양극/음극) | Al 0.2mm / Ni 0.2mm | 동일 | MAT_024 |

### 와인딩 구조 특이사항

- 연속 시트가 긴 타원형으로 권취 (flattened jellyroll)
- 코너 R = 1~2mm, 직선부 ≈ 셀 폭
- Python으로 와인딩 경로 좌표 생성 → 노드 맵핑

---

## 2. 모델링 전략

### 2.1 요소 선택

| 구성 요소 | 요소 타입 | ELFORM | 이유 |
| ----------- | ----------- | -------- | ------ |
| Al/Cu 집전체 | Shell | 2 (BT) | 얇은 금속박 (8-12µm), 면내 거동 지배 |
| 전극 코팅 (NMC/Graphite) | Solid | 1 (정축소) | 두께 방향 압축 거동 핵심 |
| 분리막 (PE) | Shell | 16 (완전적분) | 파괴 판정 정확도 필요 |
| 파우치 | Shell | 2 (BT) | 알루미늄 라미네이트 |
| 임팩터 | Shell (Rigid) | 2 | MAT_020 강체 |
| 탭 | Shell | 2 | 얇은 금속 |

### 2.2 메시 전략

- **면내**: 0.5mm 균일 메시 (충돌 영역 0.25mm 리파인 가능)
- **두께**: 집전체 1요소(셸), 전극 코팅 2~3요소(솔리드), 분리막 1요소(셸)
- 총 요소 수 추정: ~5~8M (자원 빵빵하므로 OK)
- Python 스크립트로 노드/요소 자동 생성

### 2.3 Stacked vs Wound 구조

**Stacked (적층형):**

```text

[파우치 상]
[Al집전체] ─┐
[NMC 양극]  │ 단위셀 ×15
[분리막]    │ (반복 적층)
[Graphite]  │
[Cu집전체] ─┘
[파우치 하]

```

**Wound (와인딩형):**

```text

[파우치]
┌─────────────────────────┐
│  ╭───────────────────╮  │
│  │  ╭─────────────╮  │  │  연속 권취
│  │  │             │  │  │  (flattened oval)
│  │  ╰─────────────╯  │  │
│  ╰───────────────────╯  │
└─────────────────────────┘
[파우치]

```

---

## 3. 재료 모델 배정

### 3.1 구조 재료 (*MAT)

| PID | 구성요소 | MAT 키워드 | 핵심 물성 |
| ----- | ---------- | ----------- | ----------- |
| 1 | Al 집전체 | MAT_024 | ρ=2.7e-6, E=70GPa, ν=0.33, σy=90MPa |
| 2 | Cu 집전체 | MAT_024 | ρ=8.96e-6, E=119GPa, ν=0.34, σy=200MPa |
| 3 | NMC 양극 코팅 | MAT_063 (CRUSHABLE_FOAM) | ρ=2.5e-6, E=0.5GPa, σy~10MPa, 압축커브 |
| 4 | Graphite 음극 코팅 | MAT_063 (CRUSHABLE_FOAM) | ρ=1.35e-6, E=1.0GPa, σy~15MPa, 압축커브 |
| 5 | PE 분리막 | MAT_024 + MAT_ADD_EROSION | ρ=0.95e-6, E=1.0GPa, σy=15MPa, FAIL=0.6 |
| 6 | 파우치 (Al-lam) | MAT_024 | ρ=2.1e-6, E=40GPa, σy=40MPa |
| 7 | 임팩터 | MAT_020 (RIGID) | ρ=7.85e-6, E=210GPa |
| 8 | 탭 (Al) | MAT_024 | = PID 1 물성 |
| 9 | 탭 (Ni) | MAT_024 | ρ=8.9e-6, E=200GPa, σy=380MPa |

### 3.2 열 재료 (*MAT_THERMAL)

| TMID | 구성요소 | MAT 키워드 | HC (J/kg·K) | TC (W/m·K) |
| ------ | ---------- | ----------- | ------------- | ------------ |
| 101 | Al 집전체 | MAT_THERMAL_ISOTROPIC | 903 | 238 |
| 102 | Cu 집전체 | MAT_THERMAL_ISOTROPIC | 385 | 398 |
| 103 | NMC 양극 | MAT_THERMAL_ORTHOTROPIC | 700 | k1=1.5, k2=1.5, k3=30 |
| 104 | Graphite 음극 | MAT_THERMAL_ORTHOTROPIC | 700 | k1=1.0, k2=1.0, k3=25 |
| 105 | PE 분리막 | MAT_THERMAL_ISOTROPIC | 1900 | 0.33 |
| 106 | 파우치 | MAT_THERMAL_ISOTROPIC | 1200 | 0.16 |
| 107 | 전해질(함침) | (코팅 TC에 통합) | — | — |

### 3.3 EM 재료 (*EM_MAT)

| EMMID | 구성요소 | EM_MAT | MTYPE | σ (S/m) |
| ------- | ---------- | -------- | ------- | --------- |
| 201 | Al 집전체 | EM_MAT_001 | 4 (도체) | 3.77e7 |
| 202 | Cu 집전체 | EM_MAT_001 | 4 (도체) | 5.96e7 |
| 203 | NMC 양극 | EM_MAT_001 | 1 (절연체) | 10 |
| 204 | Graphite 음극 | EM_MAT_001 | 4 (도체) | 1000 |
| 205 | PE 분리막 | EM_MAT_001 | 1 (절연체) | 1e-6 |
| 206 | 파우치 | EM_MAT_001 | 1 (절연체) | 1e-10 |
| 207 | 전해질 (유효) | EM_MAT_001 | 1 (절연체) | 1.0 |

---

## 4. 멀티피직스 연성 전략

### 4.1 해석 흐름 (3단계)

```text

Phase 1: 구조 충격 (Explicit)        0 ~ 5 ms
  ├── 측면 임팩터 → 셀 변형
  ├── 분리막 파괴 감지 (*MAT_ADD_EROSION)
  └── 내부 단락 위치/면적 결정

Phase 2: 전기-열 연성 (EM+Thermal)   5 ms ~ 60 s
  ├── *EM_RANDLES_SOLID: 분포 Randles 회로
  ├── 단락 → 줄열 발생 (*EM_RANDLES_SHORT)
  ├── 열전달 → 온도 상승
  └── 온도 피드백 → 전기화학 파라미터 변화

Phase 3: 열폭주 (Thermal Runaway)    60 s ~
  ├── *EM_RANDLES_EXOTHERMIC_REACTION
  ├── SEI 분해, 전극-전해질 반응, 분리막 용융
  └── 가스 생성 → 팽창 (구조 연성)

```

### 4.2 EM Randles 접근법 선택

**`*EM_RANDLES_SOLID` 모델 채택 이유:**

- 각 층(CCP, 양극, 분리막, 음극, CCN) 개별 Part로 구성 → 물리적 구조 직접 반영
- 분리막 삭제(erosion) 시 자동으로 단락 감지 가능
- 3D 분포 Randles 회로 → 공간적 단락 위치/면적 자연 표현
- 열-기계 fully coupled

### 4.3 핵심 EM 키워드 체인

```text

*EM_CONTROL               → EMSOL=3 (Resistive heating)
*EM_CONTROL_COUPLING      → THCPL=2, SMCPL=1 (열+구조 연성)
*EM_CONTROL_TIMESTEP      → TSTYPE=5 (열 시간스텝 동기화)
*EM_CONTROL_CONTACT       → EMCT=1 (EM 접촉 활성화)
*EM_CONTROL_EROSION       → 삭제 요소 EM에서 제거
*EM_MAT_001 (×7)          → 각 층별 전기 물성
*EM_RANDLES_SOLID          → 분포 Randles 회로
*EM_RANDLES_SHORT          → 내부 단락 조건 (*DEFINE_FUNCTION)
*EM_RANDLES_EXOTHERMIC_REACTION → 열폭주 발열
*EM_CIRCUIT                → 외부 회로 (CIRCTYP=1, 방전전류)
*EM_ISOPOTENTIAL           → 탭 등전위 경계

```

### 4.4 단락 판정 함수 (*DEFINE_FUNCTION)

```text

*DEFINE_FUNCTION
$ 분리막 erosion → 단락 저항
$ ero 변수: 100 = separator eroded
$ 단락 시 접촉 저항 = 0.01 Ω·m²
$ 비단락 시 = 0 (개방)
f(ero, temp, vmstress) =
  if(mod(ero/100, 10) >= 1) then
    0.01 * exp(-0.001 * (temp - 298))   $ 온도 증가 시 저항 감소
  else
    0.0                                  $ 단락 없음
  endif

```

---

## 5. 접촉 정의

| Contact # | 유형 | SURFA | SURFB | 용도 |
| ----------- | ------ | ------- | ------- | ------ |
| 1 | AUTOMATIC_SURFACE_TO_SURFACE | 임팩터 | 파우치 외면 | 충돌 |
| 2 | AUTOMATIC_SINGLE_SURFACE | 전체 셀 | — | 내부 자기접촉 |
| 3 | TIED_SURFACE_TO_SURFACE | 집전체 | 전극 코팅 | 층간 접합 |
| 4 | TIED_SURFACE_TO_SURFACE | 전극 코팅 | 분리막 | 층간 접합 |
| 5 | CONTACT_..._THERMAL | — | — | 열 접촉 (THERMAL 옵션) |
| 6 | ERODING_SURFACE_TO_SURFACE | — | — | 분리막 삭제 후 접촉 갱신 |

**THERMAL 옵션**: 모든 TIED 접촉에 THERMAL 추가 → 층간 열전달
**ERODING**: 분리막 요소 삭제 시 인접 전극 간 직접 접촉 형성

---

## 6. 제어 키워드

### 6.1 구조 제어

```text

*CONTROL_TERMINATION     ENDTIM=60.0 (전체 해석 60초)
*CONTROL_TIMESTEP        TSSFAC=0.9, DT2MS=-1.0e-6 (질량스케일링)
*CONTROL_HOURGLASS       IHQ=5, QH=0.05
*CONTROL_SHELL           ISTUPD=1, THEORY=2
*CONTROL_SOLID           ESORT=1
*CONTROL_CONTACT         SLSFAC=0.1, SHLTHK=1
*CONTROL_ENERGY          HGEN=2, RWEN=2, SLNTEN=2
*CONTROL_BULK_VISCOSITY  Q1=1.5, Q2=0.06

```

### 6.2 열 제어

```text

*CONTROL_SOLUTION        SOTEFP=1 (coupled thermal-structural)
*CONTROL_THERMAL_SOLVER  APTS=1, SOLVER=12, FWORK=0.9
*CONTROL_THERMAL_TIMESTEP DT=1.0e-4, LCTM=auto
*CONTROL_THERMAL_NONLINEAR DRTOL=1.0e-4
*INITIAL_TEMPERATURE_SET  NSID=all, TEMP=298.15 (25°C)

```

### 6.3 EM 제어

```text

*EM_CONTROL              EMSOL=3
*EM_CONTROL_COUPLING     THCPL=2, SMCPL=1
*EM_CONTROL_TIMESTEP     TSTYPE=5
*EM_CONTROL_CONTACT      EMCT=1
*EM_CONTROL_EROSION      (활성화)

```

---

## 7. 출력 설정

```text

*DATABASE_BINARY_D3PLOT   DT=1.0e-4 (Phase1), DT=0.1 (Phase2/3)
*DATABASE_GLSTAT          DT=1.0e-5
*DATABASE_MATSUM          DT=1.0e-5
*DATABASE_RCFORC          DT=1.0e-5
*DATABASE_NODOUT          DT=1.0e-5
*DATABASE_ELOUT           DT=1.0e-5
*DATABASE_SLEOUT          DT=1.0e-5
*DATABASE_TPRINT          DT=1.0e-4
*DATABASE_EXTENT_BINARY   NEIPH=24, NEIPS=24, MAXINT=5
*EM_DATABASE_GLOBALDATA   DT=0.01
*EM_DATABASE_PARTDATA     DT=0.01
*EM_DATABASE_RANDLES      DT=0.01
*EM_DATABASE_ELDATA       DT=0.01

```

---

## 8. 파일 구성

```text

Battery/
├── 00_PROJECT_PLAN.md          ← 이 문서
├── 01_main.k                   ← 마스터 입력 (INCLUDE 기반)
├── 02_mesh_stacked.k           ← 적층형 메시 (Python 생성)
├── 03_mesh_wound.k             ← 와인딩형 메시 (Python 생성)
├── 04_materials.k              ← 구조+열+EM 재료 정의
├── 05_contacts.k               ← 접촉 정의
├── 06_boundary_loads.k         ← 경계조건, 하중, 초기조건
├── 07_control.k                ← 제어 키워드 전체
├── 08_em_randles.k             ← EM + Randles 회로 정의
├── 09_database.k               ← 출력 제어
├── 10_define_curves.k          ← 로드커브, 함수 정의
├── generate_mesh_stacked.py    ← 적층형 메시 생성기
├── generate_mesh_wound.py      ← 와인딩형 메시 생성기
└── .venv/                      ← Python 가상환경

```

---

## 9. 개발 순서

1. ✅ 프로젝트 계획 수립
2. 🔲 메시 생성 Python 스크립트 (적층형 우선)
3. 🔲 재료 k파일 (04_materials.k)
4. 🔲 로드커브/함수 정의 (10_define_curves.k)
5. 🔲 EM/Randles 정의 (08_em_randles.k)
6. 🔲 접촉 정의 (05_contacts.k)
7. 🔲 경계/하중 (06_boundary_loads.k)
8. 🔲 제어 키워드 (07_control.k)
9. 🔲 출력 설정 (09_database.k)
10. 🔲 마스터 파일 (01_main.k)
11. 🔲 와인딩형 메시 생성기
12. 🔲 검증 및 디버그

---

## 10. 챌린징 포인트 & 대응

| 과제 | 난이도 | 대응 전략 |
| ------ | -------- | ----------- |
| 수백 층의 얇은 셸+솔리드 연속 메시 | ★★★★★ | Python 자동 생성, 노드 공유 |
| 와인딩 곡선 좌표 생성 | ★★★★ | 나선 방정식 기반 parametric 좌표 |
| 분리막 파괴 → EM 단락 연동 | ★★★★★ | MAT_ADD_EROSION + EM_RANDLES_SHORT + DEFINE_FUNCTION |
| 열폭주 발열 모델링 | ★★★★ | EM_RANDLES_EXOTHERMIC_REACTION + Arrhenius 모델 |
| Explicit→열/EM 시간스케일 차이 | ★★★★★ | 질량스케일링 + 열 TSF + EM TSTYPE=5 |
| 수백만 요소의 접촉 안정성 | ★★★★ | SOFT=2, SBOPT=4, DEPTH=5 |
| 구조-열-EM 3-way 커플링 | ★★★★★ | CONTROL_SOLUTION + EM_CONTROL_COUPLING |
