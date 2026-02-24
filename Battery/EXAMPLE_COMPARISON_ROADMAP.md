# LSTC 공식 예제 기반 개선 로드맵

## 분석 개요

LSTC 공식 배터리 예제 13종을 우리 모델(Stacked + Wound)과 비교 분석한 결과입니다.

**분석 대상 예제:**

| # | 폴더 | 접근법 | 핵심 시나리오 |
| --- | ------ | -------- | ------------- |
| 1 | basic/ | Solid | 단순 방전 |
| 2 | basic_thermal/ | Solid | Joule heating 연성 |
| 3 | basic_socshift/ | Solid | SOC shift |
| 4 | basic_exothermal/ | Solid | 내부 단락 + 발열 반응 |
| 5 | tshell_extshort/ | TShell | 외부 단락 (10셀) |
| 6 | tshell_intshort/ | TShell | 내부 단락 (10셀, 구 충격) |
| 7 | tshell_cylindrical/ | TShell | 원통형 셀 |
| 8 | batmac_circuits/ | BatMac | Randles 회로 차수 비교 |
| 9 | batmac_table/ | BatMac | SOC/온도 의존 회로 파라미터 |
| 10 | batmac_intshort/ | BatMac | 10셀 구 충격 내부 단락 |
| 11 | batmac_nail/ | BatMac | 10셀 네일 관통 |
| 12 | batmac_cylinder/ | BatMac | 원통형 BatMac |
| 13 | meshless/ | Meshless | 메쉬리스 회로 연구 |

**우리 모델:** EM_RANDLES_SOLID (77개 키워드, mm/ton/s 단위계)

---

## 🔴 CRITICAL (P0) — 시뮬레이션 실패 또는 잘못된 결과를 유발하는 버그

### P0-1. `*DEFINE_FUNCTION` 5001 (내부단락) 함수 시그니처 완전 오류

**현재 우리 모델 (10_define_curves.k):**

```c

float short_resistance(float ero, float temp, float vmstress, float soc)

```

**LSTC 공식 시그니처 (batmac_nail/em.k — 20인수 완전판):**

```c

float resistance_short_randle(
    float time,         // 1: 시간
    float x_sep,        // 2: 분리막 중심 X
    float y_sep,        // 3: 분리막 중심 Y
    float z_sep,        // 4: 분리막 중심 Z
    float x_sen,        // 5: 분리막 요소 노드 중심 X
    float y_sen,        // 6: 분리막 요소 노드 중심 Y
    float z_sen,        // 7: 분리막 요소 노드 중심 Z
    float x_ccp,        // 8: 양극 CC 중심 X
    float y_ccp,        // 9: 양극 CC 중심 Y
    float z_ccp,        // 10: 양극 CC 중심 Z
    float x_ccn,        // 11: 음극 CC 중심 X
    float y_ccn,        // 12: 음극 CC 중심 Y
    float z_ccn,        // 13: 음극 CC 중심 Z
    float pres,         // 14: 압력
    float rho,          // 15: 밀도
    float vmstress,     // 16: von Mises 응력
    float cond,         // 17: 전도도
    float temp,         // 18: 온도
    float efstrain,     // 19: 유효 변형률
    float ero           // 20: 침식 플래그
)

```

**예제별 시그니처 변형:**

- `basic_exothermal`: 13인수 (time, x_sep~z_ccn)
- `batmac_intshort`: 14인수 (time, efstrain, x_sep~z_ccn)
- `batmac_nail`: 20인수 (위 전체)

**문제점:** LS-DYNA는 위치 기반으로 인수를 전달합니다. 우리 함수의 `ero`에는 실제로 `time`이, `temp`에는 `x_sep`이, `vmstress`에는 `y_sep`이, `soc`에는 `z_sep`이 전달됩니다. **모든 변수가 엉뚱한 값을 받게 되어 단락 저항 계산이 완전히 틀립니다.**

**수정 방안:**

```c

float resistance_short_randle(
    float time,
    float x_sep, float y_sep, float z_sep,
    float x_sen, float y_sen, float z_sen,
    float x_ccp, float y_ccp, float z_ccp,
    float x_ccn, float y_ccn, float z_ccn,
    float pres, float rho, float vmstress,
    float cond, float temp, float efstrain,
    float ero)
{
    $ 침식 기반 단락 판별
    if (ero > 0.5) {
        $ 분리막 침식됨 → 단락 발생
        $ CC간 거리로 단락 유형 판별
        float distCC = sqrt(
            pow(x_ccp-x_ccn, 2.) + pow(y_ccp-y_ccn, 2.) + pow(z_ccp-z_ccn, 2.)
        );

        $ 온도 보정
        float R_base;
        if (distCC < 0.05) {
            R_base = 0.0001;   $ Al-Cu (금속↔금속)
        } else if (distCC < 0.15) {
            R_base = 0.001;    $ Al-An 또는 Ca-Cu
        } else {
            R_base = 0.010;    $ Ca-An (일반적)
        }

        float R_short = R_base * exp(-0.002 * (temp - 298.15));
        if (R_short < 0.00001) R_short = 0.00001;

        $ 응력 기반 면적 확장
        if (vmstress > 50.0) {
            R_short = R_short * 50.0 / vmstress;
        }

        return R_short;
    }
    return -1.0;  $ 음수 = 단락 없음 (LSTC 규약)
}

```

**핵심 변경사항:**

1. 함수 시그니처를 20인수 LSTC 공식 형식으로 교체
2. "단락 없음" 반환값: `0.0` → `-1.0` (LSTC 규약. 양수=단락저항, 음수=단락없음)
3. `ero > 0.5` 기반 판별 (침식 플래그 활용)
4. CC간 거리 기반 단락 유형 분류 (LSTC 예제 패턴)

**영향 파일:** `10_define_curves.k`, `10_define_curves_phase1.k`, `10_define_curves_phase2.k`

---

### P0-2. `*DEFINE_FUNCTION` 5002 (발열반응) 함수 시그니처 순서 오류

**현재 우리 모델:**

```c

float exotherm_heat(float temp, float soc, float time, float H_ex)

```

**LSTC 공식 시그니처 (basic_exothermal/em.k — 10인수 확장판):**

```c

float exothermic_reaction_randle(
    float time,     // 1: 시간
    float temp,     // 2: 온도
    float SOC,      // 3: 충전 상태
    float emdt,     // 4: EM 시간스텝
    float ocv,      // 5: 개방 회로 전압
    float curr,     // 6: 전류
    float volt,     // 7: 전압
    float r0,       // 8: R0 저항
    float vc,       // 9: 커패시터 전압
    float H_ex      // 10: 누적 발열량
)

```

**또는 간략판 (batmac_nail/em.k — 4인수):**

```c

float exothermic_reaction_randle(float time, float temp, float SOC, float H_ex)

```

**문제점:** 우리 함수는 `(temp, soc, time, H_ex)` 순서인데, LS-DYNA는 `(time, temp, SOC, H_ex)` 순서로 전달합니다. 첫 번째 인수 `temp`에 실제로는 `time` 값이 들어갑니다:

- 우리 `temp` ← 실제값: `time` (예: 0.005초) → **온도 조건이 모두 틀림**
- 우리 `soc` ← 실제값: `temp` (예: 298K) → **SOC가 298%??**
- 우리 `time` ← 실제값: `SOC` (예: 0.5) → 미사용이라 영향 적음
- 우리 `H_ex` ← 실제값: `H_ex` → **위치가 같아 정상** (4인수 버전 기준)

실제로 시뮬레이션 시 temp=0.005(s)이므로 모든 온도 트리거(353K, 393K 등)가 절대 발동하지 않으며, **열폭주 모델이 완전히 비활성화**됩니다.

**수정 방안 (10인수 확장판 권장):**

```c

float exothermic_reaction_randle(
    float time, float temp, float SOC, float emdt,
    float ocv, float curr, float volt, float r0,
    float vc, float H_ex)
{
    float R_gas = 8.314;
    float total_q = 0.0;

    $ ... 기존 5단계 Arrhenius 로직 유지 ...
    $ (temp, SOC 변수명 수정 후 동일 로직)

    $ 누적 발열량 제한 (열폭주 소진)
    float H_max = 1.0e5;
    if (H_ex > H_max) return 0.0;

    return total_q;
}

```

**영향 파일:** `10_define_curves.k`, `10_define_curves_phase1.k`, `10_define_curves_phase2.k`

---

### P0-3. EM_MAT_001 — 전극 Material Type 오류

**현재 우리 모델 (04_materials.k):**

```lsdyna

$ NMC 양극 (MID=3)
*EM_MAT_001
   3    4    -6003    0    ← mtype=4 (도체)로 설정
$ Graphite 음극 (MID=4)
*EM_MAT_001
   4    4    -6004    0    ← mtype=4 (도체)로 설정

```

**LSTC 공식 예제 ALL (basic, tshell, batmac):**

```lsdyna

$ 전극 (NMC, Graphite)
*EM_MAT_001
   2    1              ← mtype=1 (비도체: Randles가 전기화학 처리)
*EM_MAT_001
   4    1              ← mtype=1
$ CC (Al, Cu)
*EM_MAT_001
   1    2    5.88e7    ← mtype=2 (도체: σ 명시)
*EM_MAT_001
   5    2    3.70e7    ← mtype=2

```

**문제점:**

- `EM_RANDLES_SOLID`는 전극의 전기화학을 Randles 등가회로로 처리합니다
- 전극을 mtype=4 (도체)로 설정하면 EM 솔버가 전극 내 전류 흐름을 **이중으로** 계산합니다
  - Randles 회로: 전기화학 반응으로 전류 계산
  - FEM 솔버: σ에 의한 체적 전류 계산 (이것이 추가됨)
- 에너지 보존이 깨지고, Joule heating이 과대평가됩니다
- LSTC 예제에서 전극은 **항상** mtype=1 (비도체)

**수정 방안:**

```lsdyna

$ NMC 양극 → mtype=1 (Randles 전용)
*EM_MAT_001
$      MID     MTYPE     SIGMA     EOSID
         3         1         0         0
$ Graphite 음극 → mtype=1 (Randles 전용)
*EM_MAT_001
         4         1         0         0

```

> **참고:** CC (MID 1, 2)의 mtype=4는 EMSOL=3에서 유효하지만, 공식 예제는 mtype=2를 사용합니다. 호환성을 위해 mtype=2로 변경 권장.

**영향 파일:** `04_materials.k`, `04_materials_tempdep.k`

---

### P0-4. `*EM_ISOPOTENTIAL` / `*EM_ISOPOTENTIAL_CONNECT` 완전 누락

**현재 우리 모델:** 없음 (0개)

**LSTC 공식 예제:**

- `basic/`: 4× ISOPOTENTIAL + 1× CONNECT (R=0.05Ω)
- `basic_exothermal/`: 4× ISOPOTENTIAL + 1× CONNECT
- `tshell_intshort/`: 22× ISOPOTENTIAL + CONNECT
- `batmac_intshort/`: 42× ISOPOTENTIAL + 22× CONNECT
- `batmac_nail/`: 42× ISOPOTENTIAL + 22× CONNECT

**역할:**

1. `*EM_ISOPOTENTIAL`: 탭(tab) 표면의 노드를 동전위면으로 설정 → 전류 수집점 정의
2. `*EM_ISOPOTENTIAL_CONNECT`: 탭 간 연결 (외부 저항, 전압원, 전류원, 접지)

**연결 유형 (connType):**

| connType | 의미 | 예제 사용 |
| ---------- | ------ | --------- |
| 1 | 전압원 (V) | 직렬 연결 (V=0) |
| 2 | 저항 (R, Ω) | 외부 부하 (R=0.05Ω) |
| 3 | 접지 (V=0) | 기준 전위 |
| 4 | 전류원 (I) | 충/방전 전류 |
| 5 | Meshless 연결 | (Meshless 전용) |

**문제점:** `*EM_CIRCUIT`은 전역 회로를 정의하지만, 개별 탭의 전위면과 외부 연결을 정의하지 않습니다. ISOPOTENTIAL 없이는:

- 전류 수집점이 정의되지 않아 전류 분포가 비현실적
- 다중 셀의 직/병렬 연결이 불가능
- 외부 부하 저항 연결이 물리적으로 올바르지 않음

**수정 방안 (08_em_randles.k에 추가):**

```lsdyna

$ ==================== ISOPOTENTIAL (탭 동전위면) ====================
$
$ --- Stacked: 각 unit cell의 양극/음극 탭 ---
$ Unit Cell 0
*EM_ISOPOTENTIAL
$    isoId   setType     setId
         1         2         1    $ Al CC 탭 (양극)
*EM_ISOPOTENTIAL
         2         2         2    $ Cu CC 탭 (음극)
$ ... Unit Cell 1~4 반복 ...
$
$ ==================== ISOPOTENTIAL CONNECT ====================
$
$ --- 외부 부하 연결 ---
*EM_ISOPOTENTIAL_CONNECT
$  connId  connType  isoId1  isoId2     val
       1         2       1       2     0.05    $ R=0.05Ω 외부 저항
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
       2         3       2       0     0.0     $ Cu CC → 접지

```

> **주의:** SET_NODE_LIST 정의 필요 (탭 표면 노드 목록)→ `02_mesh_stacked.k`에 추가.

**영향 파일:** `08_em_randles.k`, `08_em_randles_wound.k`, `02_mesh_stacked.k`, `03_mesh_wound.k`

---

## 🟠 HIGH (P1) — 물리적 정확도에 큰 영향

### P1-1. SOC/온도 의존 회로 파라미터 부재

**현재 우리 모델:** R0, R1, C1 모두 **고정 상수**

```lsdyna

R0CHA=0.030  R0DIS=0.035  R10CHA=0.020  R10DIS=0.025  C10CHA=1000  C10DIS=1000

```

**LSTC batmac_table 예제:** `*DEFINE_TABLE`로 SOC와 온도의 2D 함수

```lsdyna

$ r0cha = -70 → TABLE 70 (음수 = TABLE ID 참조)
*DEFINE_TABLE
70                          $ TABLE ID

  0.    71                  $ T=0°C → CURVE 71
 25.    72                  $ T=25°C → CURVE 72
 50.    74                  $ T=50°C → CURVE 74
100.    75                  $ T=100°C
1000.   76                  $ T=1000°C

*DEFINE_CURVE
71                          $ R0 vs SOC at T=0°C
0, 0.003
100, 0.002

```

**R0 범위:** 0.001~0.004 Ω (온도/SOC에 따라 4배 변동)
**C10 범위:** 6100~12200 F (온도/SOC에 따라 2배 변동)

**문제점:** 실제 배터리에서 R0는 저온에서 크게 증가(~3배), SOC 양 끝에서 증가합니다. 고정값은 특히:

- 저온 시뮬레이션: 내부저항 과소평가 → 발열량 과소평가
- SOC 극단: 전압 거동 부정확
- 온도 상승 시: 저항 감소 효과 미반영

**수정 방안:** Randles 카드에서 R0CHA, R0DIS, R10CHA, R10DIS, C10CHA, C10DIS를 음수 TABLE ID로 대체

**영향 파일:** `08_em_randles.k`, `08_em_randles_wound.k`, `10_define_curves.k`, `battery_config.yaml`

---

### P1-2. CC Material Type — mtype=4 vs mtype=2

**현재:** CC (Al, Cu)에 mtype=4 + FUNCTID(온도의존 σ) 사용
**예제:** EMSOL=3에서도 CC에 mtype=2 + 고정 σ 사용

| 예제 | Al CC σ (S/m) | Cu CC σ (S/m) | mtype |
| ------ | ----------- | ----------- | ------- |
| basic | 5.88e7 | 3.70e7 | 2 |
| tshell_intshort | 6.0e7 | 3.0e7 | 2 |
| batmac_nail | 1.0e6 | 2.0e6 | 4 |

> batmac_nail은 mtype=4를 사용하지만, 이는 CC 탭(MID 100, 200)에 대해서만 적용됨.

**수정 방안:** mtype=4 자체는 EMSOL=3에서 유효하나, 온도의존 FUNCTID와의 호환성 확인 필요. 안전을 위해 mtype=2 + 고정 σ로 변경 권장. 온도의존 전도도는 열적으로 큰 영향이 없음 (CC는 저항이 매우 작아 Joule heating 기여 미미).

**영향 파일:** `04_materials.k`

---

### P1-3. `*EM_RANDLES_SHORT` — return 0.0 vs return -1.0 (단락없음 규약)

**현재 우리 모델:**

```c

if (sep_eroded < 1.0) return 0.0;  // 단락 없음

```

**LSTC 예제 (전부):**

```c

return -1.0;   // 단락 없음 (음수 = no short)
return -0.1;   // 단락 없음 (batmac_intshort)

```

**LS-DYNA 규약:** `resistance_short_randle` 반환값:

- **양수**: 단락 저항 (Ω) → 단락 활성화
- **음수**: 단락 없음
- **0.0**: 0Ω 단락 = **완전 단락** (전위차 0으로 강제) ← 우리 모델이 이것을 반환!

**문제점:** 우리 모델은 정상 상태에서 R_short=0.0을 반환 → LS-DYNA가 **항상 완전 단락 상태**로 해석할 수 있음. 이는 시뮬레이션 시작부터 셀 전압이 0V로 붕괴하는 결과를 초래합니다.

**수정:** `return 0.0` → `return -1.0`

**영향 파일:** `10_define_curves.k`

---

### P1-4. `*EM_CIRCUIT` 카드 형식 — Stacked vs Wound 불일치

**Stacked (08_em_randles.k):**

```lsdyna

*EM_CIRCUIT
$  CIRCTYP      LCID       VIN     RLOAD     RSINT      RDMP     LDCRV
         1      2003       0.0       0.0       0.0       0.0         0
$       CL0       IK0      RINT       CKT      KBUS
       0.0       0.0       0.0       0.0         1

```

**Wound (08_em_randles_wound.k):**

```lsdyna

*EM_CIRCUIT
$  CIRCID  CIRCTYP      LCID       R/F       L/A       C/T0        V0        T0
       1         1      2003       0.0       0.0       0.0       0.0       0.0
$ SIDCURR    SIDVIN   SIDVOUT       PID
       0         0         0         0

```

**문제점:** 두 파일의 EM_CIRCUIT 카드 형식이 다릅니다. Stacked는 KBUS=1(버스 연결)을 포함하지만, Wound는 CIRCID를 포함하고 KBUS가 없습니다. LSTC 예제에서는 `*EM_ISOPOTENTIAL_CONNECT`로 외부 연결을 정의하며 `*EM_CIRCUIT`을 사용하지 않습니다.

**수정 방안:** ISOPOTENTIAL 기반 연결로 통일한 후, EM_CIRCUIT 제거 검토

---

## 🟡 MEDIUM (P2) — 기능 부족 / 확장성

### P2-1. `*DEFINE_FUNCTION_TABULATED` 미사용

**LSTC 예제:** 분리막 두께 → 단락 저항 매핑에 사용

```lsdyna

*DEFINE_FUNCTION_TABULATED
502     (thick,res) pair data
resistanceVsThickSep
   0.0     1.e9        $ 정상: 초고저항 (절연)
 2.0e4     1.e9
 2.01e4    1.e-2       $ 관통 시작: 급격히 감소
 3.0e4     1.e-5       $ 완전 관통

```

**활용:** `resistance_short_randle` 함수 내에서 `resistanceVsThickSep(thick)` 호출 → 분리막 변형량에 따른 연속적 저항 변화

우리 모델은 이산적 임계값(ero > 0.5)만 사용 → 실제로는 분리막 두께 감소에 따라 단락 저항이 점진적으로 변화

**추가 위치:** `10_define_curves.k`

---

### P2-2. SOC Shift 지원 부재

**LSTC basic_socshift 예제:**

```lsdyna

*EM_RANDLES_SOLID
$ ...
$# useSocS   tauSocS  sicslcid
         1      1000      -400
*DEFINE_CURVE
400
0, 0.0
100, 10.0

```

- `useSocS=1`: SOC shift 활성화
- `tauSocS=1000`: SOC shift 시간상수 (초)
- `sicslcid=-400`: SOC shift 커브 (SOC vs shift%)

**목적:** 셀 내 SOC 불균형 → local SOC가 global SOC에서 편차 발생, 실제 전극 두께/전해질 농도 불균일 효과 모사

**현재 우리 모델:** `useSocS=0` (비활성화) — 카드 자체가 없거나 0으로 설정

**추가 위치:** `08_em_randles.k`, `battery_config.yaml`

---

### P2-3. BatMac 대안 모델 부재

**LSTC 예제 5건이 BatMac 사용** — 모듈/팩 수준 분석에 필수

| 키워드 | 설명 | 우리 모델 |
| -------- | ------ | ---------- |
| `*EM_RANDLES_BATMAC` | 균질화 매크로 셀 | ❌ 없음 |
| `*EM_MAT_006` | 양극/음극 CC별 별도 σ | ❌ 없음 |
| `*EM_MAT_005` | 이방성 EM 재료 (β, Cm, AOPT) | ❌ 없음 |

BatMac 장점:

- 셀당 1개 Part → multi-cell 모듈(10~100셀) 시뮬레이션 가능
- 솔리드 요소 대비 10~100배 빠른 계산
- 젤리롤 구조의 이방성 전도도 (winding direction vs thickness) 반영

**수정 방안:** 새 파일 `08_em_randles_batmac.k`, `02_mesh_batmac.k` 생성

---

### P2-4. TShell 대안 모델 부재

| 키워드 | 설명 | 우리 모델 |
| -------- | ------ | ---------- |
| `*EM_RANDLES_TSHELL` | 복합 두꺼운 셸 Randles | ❌ 없음 |
| `*PART_COMPOSITE_TSHELL` | 다층 복합 셸 (elform=5) | ❌ 없음 |

TShell 장점:

- 층별 상세 (5층: CCP/양극/분리막/음극/CCN)를 단일 요소로 표현
- 솔리드 대비 5~20배 빠른 계산 (고체 요소 5층 → 두꺼운 셸 1층)
- 층간 역학적/전기화학적 상호작용 유지

**수정 방안:** 새 파일 `08_em_randles_tshell.k`, `02_mesh_tshell.k` 생성

---

### P2-5. `*EM_CONTROL_EROSION` 카드 형식

**현재 우리 모델:**

```lsdyna

*EM_CONTROL_EROSION
$ 삭제된 요소를 EM 계산에서 제거
$ Card 1: ECTRL (1=ON)
         1

```

**LSTC batmac_nail 예제:**

```lsdyna

*EM_CONTROL_EROSION
1

```

형식은 동일하지만, wound 모델에는 이 카드가 없습니다(주석 처리 후 값이 누락).

**영향 파일:** `08_em_randles_wound.k`

---

## 🔵 LOW (P3) — 고급 기능 / 특수 시나리오

### P3-1. Implicit Dynamics 옵션

**LSTC batmac_nail 예제:** 다중 위상 접근법

- Phase 1: Explicit (관통, 0~12ms)
- Phase 2: Implicit (열 이완, 12ms~100s)

```lsdyna

*CONTROL_IMPLICIT_GENERAL
$   IMFLAG        DT      LCID      FORM     NSBS     IGES     DTEFN
         1     0.001         0         0         0         0         0
*CONTROL_IMPLICIT_DYNAMICS
$   IMASS     GAMMA      BETA     TDYBIR    TDYDTH    TDYBUR      IRATE
         1       0.6      0.38       0.0       0.0       0.0         0

```

**목적:** 네일 관통 후 장기간(수십 초~수분) 열전파를 효율적으로 계산. Explicit으로는 비현실적인 계산 시간 필요.

우리 모델은 phase2(07_control_phase2.k)에서 mass scaling을 사용하지만, implicit가 더 정확하고 효율적

**추가 위치:** `07_control_phase2.k`

---

### P3-2. Mortar Contact

| 키워드 | 사용 예제 | 장점 |
| -------- | --------- | ------ |
| `*CONTACT_AUTOMATIC_SINGLE_SURFACE_MORTAR` | batmac_nail | robust 관통 접촉 |
| `*CONTACT_*_MORTAR_THERMAL_ID` | batmac_cylinder | 열 전달 정확도 ↑ |

우리 모델은 표준 AUTOMATIC 접촉 사용 → 관통 시 접촉 안정성 이슈 가능

---

### P3-3. `*EM_RANDLES_SHORT_ID` (Short ID 연결)

**LSTC batmac_nail 예제:**

```lsdyna

*EM_RANDLES_SHORT_ID
$shortId  areaType  functId
    501         3       501

```

`shortId`를 통해 특정 셀/영역의 단락을 개별 제어할 수 있습니다. 우리 모델은 모든 셀에 동일한 단락 함수 적용.

---

### P3-4. `*EM_ISOPOTENTIAL` randType 옵션

**LSTC 예제 발견:**

```lsdyna

*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         5         2         5         5    ← randType=5: Randles 양극 탭
        15         2        15         1    ← randType=1: Randles 음극 탭

```

`randType`: Randles 회로와 탭을 직접 연결하는 옵션

- 5 = positive tab (양극 집전체)
- 1 = negative tab (음극 집전체)
- 6 = winding connection (원통형)

이 옵션으로 EM_CIRCUIT 없이도 외부 회로 연결 가능

---

### P3-5. `fromTherm` 파라미터 활용

**LSTC batmac_nail:**

```lsdyna

*EM_RANDLES_BATMAC
$ ...
$#    temp   frtherm    r0toth      dudt     tempu
      25.0         1         1       0.0         0

```

`fromTherm=1` + `tempu=0` (°C): 열솔버로부터 온도를 읽어 Randles 회로 업데이트

> 우리 모델은 `FRTHER=1` + `TEMPU=1` (K) 사용 — 정상이지만, 예제는 °C를 사용. 단위 일관성 확인 필요.

---

## 단위계 비교

| 항목 | 우리 모델 | LSTC 예제 | 비고 |
| ------ | ---------- | ----------- | ------ |
| 길이 | mm | m | ×1000 |
| 질량 | ton (10³ kg) | kg | ×1000 |
| 시간 | s | s | 동일 |
| 힘 | N | N | 동일 |
| 응력 | MPa | Pa | ×10⁶ |
| 에너지 | mJ | J | ×1000 |
| σ (전도도) | S/mm | S/m | ×1000 |
| Q (용량) | Ah | Ah | 동일 |
| R (저항) | Ω | Ω | 동일 |

> 단위 변환은 이미 우리 모델에 적용되어 있으므로 추가 작업 없음. 단, 새 DEFINE_TABLE 추가 시 단위 주의 필요.

---

## 수정 우선순위 및 작업 계획

### Phase A: Critical Fixes (P0) — 시뮬레이션 정합성 복구

| # | 작업 | 파일 | 예상 소요 |
| --- | ------ | ------ | ---------- |
| A1 | DEFINE_FUNCTION 5001 시그니처 교체 (20인수) | 10_define_curves*.k | 30분 |
| A2 | DEFINE_FUNCTION 5002 시그니처 교체 (시간→온도→SOC→H_ex) | 10_define_curves*.k | 15분 |
| A3 | 전극 EM_MAT_001 mtype 4→1 변경 (MID 3,4) | 04_materials*.k | 10분 |
| A4 | short_resistance return 0.0 → -1.0 수정 | 10_define_curves*.k | 5분 |
| A5 | EM_ISOPOTENTIAL + CONNECT 추가 | 08_em_randles*.k | 45분 |
| A6 | 탭 NODE SET 정의 | 02_mesh*.k, 03_mesh*.k | 30분 |

> Phase A 총 소요: ~2시간

### Phase B: Physics Accuracy (P1) — 물리 정확도 향상

| # | 작업 | 파일 | 예상 소요 |
| --- | ------ | ------ | ---------- |
| B1 | DEFINE_TABLE 기반 R0/R1/C1 (SOC×T) | 10_define_curves*.k | 1시간 |
| B2 | EM_RANDLES_SOLID 카드에 TABLE ID 반영 | 08_em_randles*.k | 30분 |
| B3 | CC mtype 4→2 변경 검토 | 04_materials*.k | 15분 |
| B4 | EM_CIRCUIT 통일/정리 | 08_em_randles*.k | 20분 |
| B5 | YAML 스키마에 TABLE 파라미터 추가 | battery_config.yaml | 30분 |

> Phase B 총 소요: ~2.5시간

### Phase C: Feature Enhancement (P2) — 기능 확장

| # | 작업 | 파일 | 예상 소요 |
| --- | ------ | ------ | ---------- |
| C1 | DEFINE_FUNCTION_TABULATED 추가 (separator thickness→R) | 10_define_curves*.k | 30분 |
| C2 | SOC Shift 지원 (useSocS, tauSocS, sicslcid) | 08_em_randles*.k | 20분 |
| C3 | BatMac 모델 파일 신규 생성 | 08_em_randles_batmac.k | 2시간 |
| C4 | TShell 모델 파일 신규 생성 | 08_em_randles_tshell.k | 2시간 |

> Phase C 총 소요: ~5시간

### Phase D: Advanced (P3) — 고급 기능

| # | 작업 | 파일 | 예상 소요 |
| --- | ------ | ------ | ---------- |
| D1 | Implicit dynamics 옵션 추가 | 07_control_phase2.k | 1시간 |
| D2 | Mortar contact 대안 | 05_contacts*.k | 30분 |
| D3 | EM_RANDLES_SHORT_ID 지원 | 08_em_randles*.k | 20분 |
| D4 | randType 기반 ISOPOTENTIAL 활용 | 08_em_randles*.k | 15분 |

> Phase D 총 소요: ~2시간

---

## 예제별 우리 모델 대비 키워드 커버리지

| 키워드 | basic | exoth | tshell | batmac | 우리모델 | 상태 |
| -------- | ------- | ------- | -------- | -------- | --------- | ------ |
| EM_CONTROL | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| EM_CONTROL_TIMESTEP | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| EM_CONTROL_COUPLING | — | — | — | — | ✅ | 우리만 |
| EM_CONTROL_CONTACT | — | — | ✅ | — | ✅ | OK |
| EM_CONTROL_EROSION | — | — | — | ✅ | ✅ | OK |
| EM_RANDLES_SOLID | ✅ | ✅ | — | — | ✅ | OK |
| EM_RANDLES_TSHELL | — | — | ✅ | — | ✅ | OK |
| EM_RANDLES_BATMAC | — | — | — | ✅ | ✅ | OK |
| EM_RANDLES_SHORT | — | ✅ | ✅ | ✅ | ✅ | OK (→SHORT_ID) |
| EM_RANDLE_EXOTHERMIC | — | ✅ | — | ✅ | ✅ | OK |
| EM_ISOPOTENTIAL | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| EM_ISOPOTENTIAL_CONNECT | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| EM_MAT_001 (mtype=1) | ✅ | ✅ | ✅ | — | ✅ | OK |
| EM_MAT_001 (mtype=2) | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| EM_MAT_005 | — | — | — | ✅ | ✅ | OK (BatMac) |
| EM_MAT_006 | — | — | — | ✅ | ✅ | OK (BatMac) |
| EM_CIRCUIT | — | — | — | — | ✅ | OK |
| DEFINE_FUNCTION_TAB | — | — | ✅ | ✅ | ✅ | OK |
| DEFINE_TABLE | — | — | — | ✅ | ✅ | OK |
| CONTROL_IMPLICIT | — | — | — | ✅ | ✅ | OK (commented) |
| CONTACT_MORTAR | — | — | — | ✅ | ✅ | OK (별도 파일) |
| MAT_ADD_EROSION | — | — | — | ✅ | ✅ | OK |
| MAT_ADD_GEN_DAMAGE | — | — | — | — | ✅ | 우리만 |
| MAT_ADD_THERMAL_EXP | — | — | — | — | ✅ | 우리만 |
| MAT_JOHNSON_COOK | — | — | — | — | ✅ | 우리만 |
| AIRBAG_SIMPLE | — | — | — | — | ✅ | 우리만 |
| CONTROL_REFINE_SOLID | — | — | — | — | ✅ | 우리만 |
| MAT_THERMAL_ORTHO | — | — | — | — | ✅ | 우리만 |

**범례:** ✅ = 있음/정상, ⚠️ = 있으나 오류, ❌ = 없음, — = 해당 없음

---

## 우리 모델의 강점 (예제 대비)

예제에는 **없지만** 우리 모델에 있는 고급 기능:

1. **MAT_JOHNSON_COOK** — CC의 변형률속도/온도 의존 소성 + JC 손상
2. **MAT_ADD_GENERALIZED_DAMAGE (GISSMO)** — 분리막 일반화 손상
3. **MAT_ADD_THERMAL_EXPANSION** — 7개 재료 열팽창
4. **MAT_THERMAL_ORTHOTROPIC** — 전극 이방성 열전도
5. **AIRBAG_SIMPLE_AIRBAG_MODEL** — 벤팅 모델
6. **CONTROL_REFINE_SOLID** — 적응 메쉬
7. **5단계 Arrhenius 열폭주** — 예제는 단순 조건, 우리는 SEI/음극/전해질/양극/바인더 5단계
8. **4모드 ISC** — 예제는 단순 단락, 우리는 Ca-An/Al-An/Ca-Cu/Al-Cu 분류
9. **Cowper-Symonds 분리막** — 변형률속도 강화 (고속 충격 대응)
10. **온도 의존 전도도 (FUNCTID)** — 예제는 고정 σ, 우리는 온도 함수

> 이들은 모두 물리적으로 우수한 접근이므로 유지합니다. 단, P0 버그 수정이 선행되어야 이 기능들이 올바르게 작동합니다.

---

## 요약

| 등급 | 항목 수 | 핵심 리스크 |
| ------ | -------- | ----------- |
| 🔴 P0 | 4건 | **모두 수정 완료 ✅** |
| 🟠 P1 | 4건 | **모두 수정 완료 ✅** |
| 🟡 P2 | 5건 | **모두 수정 완료 ✅** |
| 🔵 P3 | 5건 | **모두 수정 완료 ✅** |

**전체 완료. 모든 P0~P3 항목이 해결되었습니다.**
