# YAML 설정 기반 시뮬레이션 가이드

## 개요

모든 배터리 시뮬레이션 파라미터가 `battery_config.yaml` 파일에 중앙집중식으로 관리됩니다.

- **재료 물성**: 밀도, 영률, 열전도도, 비열 등
- **기하학적 치수**: 각 층 두께, 셀 크기, 탭 위치
- **메시 파라미터**: 요소 크기, 티어별 UC 수
- **EM Randles**: Q, R0, R1, C1, SOC
- **접촉 파라미터**: 마찰계수, 열전도도
- **솔버 제어**: 시간스텝, 종료시간 등

## 주요 장점

1. **추적성**: 어떤 물성을 왜 사용했는지 YAML 주석에 명시
2. **재현성**: 동일한 YAML = 동일한 시뮬레이션 결과
3. **버전 관리**: Git으로 설정 변경 이력 추적
4. **손쉬운 수정**: 코드 변경 없이 YAML만 수정하면 됨
5. **문서화**: YAML 자체가 실행 가능한 문서

## 사용법

### 1. YAML 파일 확인

```bash

# YAML 파일 존재 및 파싱 확인

python -c "import yaml; c = yaml.safe_load(open('battery_config.yaml', 'r', encoding='utf-8')); print('✓ YAML loaded')"

```

### 2. 메시 생성 (YAML 기반)

#### 적층형 (Stacked)

```bash

# Tier -1 (디버깅, 5 UC)

python generate_mesh_stacked.py --config battery_config.yaml --tier -1

# Tier 0 (베이스라인, 15 UC)

python generate_mesh_stacked.py --tier 0

# Tier 0.5 (프로덕션, 20 UC)

python generate_mesh_stacked.py --tier 0.5

# 사용자 정의 메시 크기

python generate_mesh_stacked.py --tier 0 --mesh-size 5.0

# 출력 파일명 지정

python generate_mesh_stacked.py --tier 0 --output custom_mesh.k

```

#### 와인딩형 (Wound)

```bash

# Tier -1 (디버깅, 5 windings)

python generate_mesh_wound.py --config battery_config.yaml --tier -1

# Tier 0 (베이스라인, 15 windings)

python generate_mesh_wound.py --tier 0

# 사용자 정의 메시 크기 (축방향, 경로방향)

python generate_mesh_wound.py --tier 0 --mesh-size-y 2.5 --mesh-size-path 2.0

# 출력 파일명 지정

python generate_mesh_wound.py --tier 0 --output custom_wound.k

```

### 3. Contacts 생성 (YAML 기반)

```bash

# 모든 Phase (1, 2, 3) 생성

python generate_contacts.py --config battery_config.yaml --tier 0 --type stacked --phase all

# 특정 Phase만 생성

python generate_contacts.py --tier -1 --type stacked --phase 1 2

# Wound 모델

python generate_contacts.py --tier 0 --type wound --phase all

```

### 4. EM Randles 생성 (YAML 기반)

```bash

# Tier에서 자동으로 UC 수 결정

python generate_em_randles.py --config battery_config.yaml --tier 0

# 직접 UC 수 지정 (기존 방식도 지원)

python generate_em_randles.py --n-uc 15 --output 08_em_randles_custom.k

```

### 5. 전체 티어 일괄 생성 (YAML 기반)

```bash

# Tier -1, 0, 0.5 일괄 생성 (mesh + contacts + EM Randles)

python generate_all_tiers.py --config battery_config.yaml --tier -1 0 0.5 --type stacked

# 기본값 (Tier 0 제외 Tier 2, stacked + wound)

python generate_all_tiers.py

# 특정 티어만 (Tier 2 포함 옵션)

python generate_all_tiers.py --tier 1 2 --include-tier2

```

## YAML 구조

### 주요 섹션

```yaml

metadata:           # 프로젝트 정보, 버전
units:              # 단위계 정의 (mm, ton, s, N, MPa, mJ)
geometry:           # 기하학적 치수
  stacked:          #   - 적층형 배터리
  wound:            #   - 와인딩형 배터리
impactor:           # 임팩터 설정 (원통/네일)
materials:          # 재료 물성 (8종)
mesh:               # 메시 파라미터
em_randles:         # EM Randles 회로 파라미터
contacts:           # 접촉 파라미터
boundary_conditions: # 경계조건 및 하중
control:            # 솔버 제어 (Phase별)
part_ids:           # PID 체계
material_ids:       # MID 체계
section_ids:        # SID 체계
sets:               # PSET/NSET 체계
load_curves:        # 로드커브 ID
output_files:       # 파일 출력 설정
validation:         # 검증 기준
conversion_factors: # 단위 변환 헬퍼

```

## 물성 수정 예시

### 예시 1: NMC 양극 열전도도 변경

**변경 전 (battery_config.yaml)**:

```yaml

materials:
  nmc_cathode:
    thermal_conductivity: 0.0018  # W/mm·K (1.8 W/m·K)
    description: |
      LiNi₀.₆Mn₀.₂Co₀.₂O₂ (NMC622) + PVDF 바인더 + Carbon black
      다공도: ~30%, 열전도도 매우 낮음 (리튬 이온 배터리 특성)
    source: "Chen et al., J. Electrochem. Soc. 2020"

```

**변경 후 (실험 측정값 적용)**:

```yaml

materials:
  nmc_cathode:
    thermal_conductivity: 0.0022  # W/mm·K (2.2 W/m·K)
    description: |
      LiNi₀.₆Mn₀.₂Co₀.₂O₂ (NMC622) + PVDF 바인더 + Carbon black
      다공도: ~30%, 열전도도 실험 측정값으로 업데이트 (2024-02-17)
    source: "사내 실험 측정, 2024-02-15, 샘플 NMC-2024-015"

```

**재생성**:

```bash

# 04_materials.k는 수동 파일이므로 직접 수정 필요

# 또는 materials.k 생성 스크립트 추가 개발

```

### 예시 2: Tier 0 UC 수 변경 (15 → 18)

**변경 전**:

```yaml

geometry:
  stacked:
    stacking:
      tier_definitions:
        tier_0: 15        # 베이스라인

```

**변경 후**:

```yaml

geometry:
  stacked:
    stacking:
      tier_definitions:
        tier_0: 18        # 베이스라인 (실험 결과 반영)

```

**재생성**:

```bash

python generate_mesh_stacked.py --tier 0        # → 18 UC 메시 생성
python generate_contacts.py --tier 0 --phase all # → 18 UC 접촉 생성
python generate_em_randles.py --tier 0          # → 18 EM_RANDLES_SOLID

```

### 예시 3: EM Randles R0 저항 변경

**변경 전**:

```yaml

em_randles:
  circuit_components:
    R0:
      value: 0.030          # Ω (30 mΩ)
      range: [0.030, 0.035]
      description: "직렬 내부 저항 (전해질 + 집전체)"
      source: "EIS 측정 (Electrochemical Impedance Spectroscopy)"

```

**변경 후 (온도 의존성 추가 예정)**:

```yaml

em_randles:
  circuit_components:
    R0:
      value: 0.028          # Ω (28 mΩ)
      range: [0.025, 0.030]
      description: "직렬 내부 저항 (전해질 + 집전체), 25°C 기준"
      source: "EIS 측정 (2024-02-16, T=25°C, SOC=50%)"
      temperature_dependent: true  # 향후 구현 예정

```

## 티어 정의

| Tier | UC 수 | 메시 크기 | 요소 수 (stacked) | 용도 |
| --- | --- | --- | --- | --- |
| -1 | 5 | 5.0 mm | ~6K | 디버깅/검증 |
| 0 | 15 | 2.5 mm | ~57K | 베이스라인 |
| 0.5 | 20 | 0.5 mm | ~1.8M | 프로덕션 |
| 1 | 22 | 0.1 mm | ~200M | 고해상도 |
| 2 | 25 | 0.05 mm | ~2B | 초고해상도 (클러스터) |

## 자동 생성 흐름

```text

battery_config.yaml
        ↓
generate_mesh_stacked.py --tier 0
        ↓
02_mesh_stacked_tier0.k (15 UC)
        ↓
generate_contacts.py --tier 0 --phase all
        ↓
05_contacts_phase1_tier0.k (임팩터+자기접촉)
05_contacts_phase2_tier0.k (74 TIED)
05_contacts_tier0.k        (74 TIED)
        ↓
generate_em_randles.py --tier 0
        ↓
08_em_randles_tier0.k (15 EM_RANDLES_SOLID)

```

## 주의사항

1. **YAML 인코딩**: UTF-8 필수 (한글 주석 포함)
2. **들여쓰기**: 2칸 공백 (YAML 표준)
3. **주석**: `#`로 시작, 각 항목의 근거/출처 명시
4. **단위 일관성**: mm-ton-s-N-MPa-mJ 체계 유지
5. **부동소수점**: 과학적 표기법 지원 (예: 2.70e-9)
6. **Boolean**: `true`/`false` (소문자)

## 버전 관리 Example

```bash

# 초기 커밋

git add battery_config.yaml
git commit -m "feat: Add battery_config.yaml with baseline parameters"

# 물성 변경

# ... battery_config.yaml 수정 ...

git commit -am "fix: Update NMC thermal conductivity (1.8→2.2 W/m·K) based on lab test"

# 기하 변경

git commit -am "feat: Change Tier 0 UC count (15→18) for better convergence"

# 태그로 버전 표시

git tag -a v1.1.0 -m "Release: Updated material properties from lab tests"

```

## 문제 해결

### YAML 파싱 오류

```bash

# YAML 문법 검증

python -c "import yaml; yaml.safe_load(open('battery_config.yaml', 'r', encoding='utf-8'))"

```

**일반적인 오류**:

- 들여쓰기 불일치 (탭/공백 혼용)
- 콜론(`:`) 뒤 공백 누락
- 문자열에 특수문자 (따옴표 필요)
- 리스트 항목 `-` 뒤 공백 누락

### Tier 키 오류

```bash

# Tier -1 → tier_minus1

# Tier 0 → tier_0

# Tier 0.5 → tier_0_5

```

### 파일 생성 실패

```bash

# 권한 확인

ls -l *.k

# 디스크 공간 확인 (Tier 1+ 는 수십 GB)

df -h .

# 로그 확인

python generate_mesh_stacked.py --tier 0 2>&1 | tee mesh_generation.log

```

## 추가 개발 계획

- [ ] `generate_materials.py`: 04_materials.k YAML 기반 자동 생성
- [ ] `generate_control.py`: 07_control.k YAML 기반 자동 생성
- [ ] `generate_curves.py`: 10_define_curves.k YAML 기반 자동 생성
- [ ] 온도 의존 물성 지원 (lookup table)
- [ ] SOC 의존 EM Randles 파라미터
- [ ] 웹 기반 YAML 편집기 (GUI)

## 참고 자료

- [LS-DY NA R16 Manual](LSDyna/RAG_LS-DYNA_R16_Summary.md)
- [Battery Material Models Reference](LS-DYNA_Battery_Material_Models_Reference.md)
- [PROJECT PLAN](00_PROJECT_PLAN.md)
- [RUN GUIDE](RUN_GUIDE.md)
- [COMPLETION SUMMARY](COMPLETION_SUMMARY.md)

---

**작성**: 2026-02-17
**버전**: 1.0.0
**유지보수**: Battery Simulation Team
