# ANSYS LS-DYNA R16 Keyword Manual 종합 요약 (RAG Reference)

> **버전**: R16 (2025.03)  
> **구성**: Vol I (일반 키워드, 257K줄), Vol II (재료모델, 164K줄), Vol III (멀티피직스, 52K줄)  
> **작성 목적**: 고급 기능 예제 제작을 위한 키워드 구조 이해 및 RAG 검색용

---

## 1. 전체 입력 구조 (Vol I — Getting Started)

### 1.1 키워드 입력 기본 규칙
- LS-DYNA 입력은 **키워드 기반**, `*KEYWORD`로 시작
- `*` = 키워드 시작 (반드시 1열), `$` = 주석
- 입력은 **순서 무관** (`*END` 제외)
- **자유 형식**(쉼표 구분) 또는 **고정 형식**(I8, I10, E16.0 등) 모두 지원
- `*INCLUDE`로 파일 분할 가능 (서브파일 재귀적 허용)
- 대소문자 무관 (case insensitive)

### 1.2 핵심 연결 구조 (Entity Relationship)
```
*NODE           → NID, X, Y, Z (절점 좌표 정의)
*ELEMENT_SHELL  → EID, PID, N1, N2, N3, N4 (요소 연결성)
*PART           → PID, SID, MID, EOSID, HGID (파트 = 섹션+재료+EOS+Hourglass 통합)
*SECTION_SHELL  → SID, ELFORM, SHRF, NIP, PROPT (요소 공식, 적분점)
*MAT_xxx        → MID, RO, E, PR, ... (재료 상수)
*EOS_xxx        → EOSID (상태방정식, 솔리드 일부 재료 전용)
*HOURGLASS      → HGID, IHQ, QH (아워글라스 제어)
```

### 1.3 단위 시스템 (일관된 단위 사용 필수)
| 시스템 | 질량 | 길이 | 시간 | 힘 | 응력 | 에너지 |
|--------|------|------|------|-----|------|--------|
| SI | kg | m | s | N | Pa | J |
| mm-ton | ton (1000kg) | mm | s | N | MPa | N·mm |
| mm-kg-ms | kg | mm | ms | kN | GPa | kN·mm |
| mm-g-ms | g | mm | ms | N | MPa | N·mm |

---

## 2. 주요 키워드 카테고리 (Vol I)

### 2.1 *CONTACT — 접촉 인터페이스 (Chapter 11)

#### 접촉 알고리즘 분류
| 분류 | 설명 |
|------|------|
| **Penalty** | 관통 노드에 접촉 스프링 부여 → 접촉력으로 관통 감소 |
| **Constraint** | 관통 노드를 표면에 강제 구속 (운동학적 구속) |
| **Node-to-Segment** | 대부분의 기본 접촉. 노드가 세그먼트 관통 검사 |
| **Segment-to-Segment** | SOFT=2 또는 Mortar. 세그먼트 간 관통 검사 |

#### 접촉 유형 7대 카테고리
1. **One-way** (비대칭): SURFA 노드만 SURFB 세그먼트 관통 검사
   - `NODES_TO_SURFACE`, `ONE_WAY_SURFACE_TO_SURFACE`, `FORMING_xxx`
2. **Two-way** (대칭): 양방향 검사 → `SURFACE_TO_SURFACE`
3. **Single surface** (자기접촉): SURFA만 입력 → `AUTOMATIC_SINGLE_SURFACE`
4. **Tied** (접합): 슬라이딩/분리 없음 → `TIED_SURFACE_TO_SURFACE`
5. **Mortar**: 세그먼트 기반, implicit에 특화 → `MORTAR`
6. **Constraint**: CONSTRAINT 포함, 구속 기반
7. **Sliding only**: 미끄럼만 허용, 분리 불가

#### OPTION1 접미어 의미
- `AUTOMATIC`: 양면 검출, 세그먼트 방향 무관 → **충돌 해석에 필수**
- `ERODING`: 요소 삭제 시 접촉면 갱신
- `TIEBREAK`: 파괴 가능한 접합 → 파괴 후 일반 접촉으로 전환
- `SMOOTH`: 곡면 피팅, 접촉 노이즈 감소
- `FORMING`: 금속 성형 전용 (tooling에 연결 메시 불필요)
- `INTERFERENCE`: 압입(간섭) 모델링
- `DRAWBEAD`: 드로우비드 시뮬레이션

#### 핵심 파라미터
| Card | 파라미터 | 설명 |
|------|----------|------|
| Mandatory 1 | SURFA/SURFB (=SSID/MSID) | 접촉 표면 정의 |
| Mandatory 1 | SSTYP/MSTYP | 표면 타입 (0=세그먼트셋, 1=쉘셋, 2=파트셋, 3=파트ID, 4=노드셋) |
| Mandatory 2 | FS, FD | 정/동마찰계수 |
| Mandatory 2 | SFS, SFM | 페널티 스케일 팩터 |
| Mandatory 3 | SST, MST | 접촉 두께 오프셋 |
| Optional A | SOFT | 페널티 알고리즘 (0=기본, 1=소프트, 2=seg-to-seg) |
| Optional A | SBOPT, DEPTH | 검색 옵션, 검색 깊이 |
| OPTION2 | THERMAL, THERMAL_FRICTION | 열 접촉 옵션 |
| OPTION4 | OFFSET, BEAM_OFFSET | 오프셋 연결 |

#### 대표적 접촉 유형 선택 가이드
| 상황 | 추천 접촉 |
|------|-----------|
| 일반 충돌 | `AUTOMATIC_SINGLE_SURFACE` 또는 `AUTOMATIC_SURFACE_TO_SURFACE` |
| 금속 성형 | `FORMING_ONE_WAY_SURFACE_TO_SURFACE` |
| 비호환 메시 접합 | `TIED_SURFACE_TO_SURFACE_OFFSET` |
| 파괴 가능 접합 (접착) | `AUTOMATIC_xxx_TIEBREAK` |
| 요소 삭제 있는 관통 | `ERODING_SURFACE_TO_SURFACE` |
| Implicit 해석 | `AUTOMATIC_SURFACE_TO_SURFACE_MORTAR` |
| 에어백 자기접촉 | `AIRBAG_SINGLE_SURFACE` |

---

### 2.2 *CONTROL — 전역 제어 (Chapter 12)

#### 가장 중요한 CONTROL 키워드

**시간 스텝 제어 — `*CONTROL_TIMESTEP`**
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| DTINIT | 초기 시간스텝 (0=자동) | 0.0 |
| TSSFAC | 시간스텝 스케일 팩터 | 0.9 |
| ISDO | 셸 특성길이 계산법 (0,1,2) | 0 |
| TSLIMT | 셸 최소 시간스텝 (강성 스케일링) | 0.0 |
| DT2MS | 질량 스케일링 (양수=준정적, 음수=조건부) | 0.0 |
| ERODE | 시간스텝 기반 요소 삭제 플래그 | 0 |
| MS1ST | 질량 스케일링 옵션 (0=지속, 1=초기만) | 0 |

**아워글라스 제어 — `*CONTROL_HOURGLASS`**
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| IHQ | 아워글라스 타입 (1-10) | 1 |
| QH | 아워글라스 계수 | 0.1 |
- IHQ=1-3: 점성(viscous), IHQ=4-5: 강성(stiffness)
- 권장: IHQ=4 또는 5 (강성 기반, 더 효과적)

**셸 요소 제어 — `*CONTROL_SHELL`**
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| WRPANG | 와핑 경고 각도 | 20.0 |
| ESORT | 삼각형 자동 분류 | 1 |
| ISTUPD | 두께 갱신 (0=없음, 1=막응력, 4=탄성 제외) | 0 |
| THEORY | 기본 셸 공식 (2=BT) | 2 |
| BWC | 와핑 강성 (1=BWC, 2=BT) | 2 |
| MITER | 평면응력 소성 (1=3회 반복, 2=완전 반복) | 1 |
| INTGRD | 두께 적분 규칙 (0=Gauss, 1=Lobatto) | 0 |
| LAMSHT | 적층 셸 이론 (3=박판, 4=후판, 5=모두) | 0 |

**접촉 제어 — `*CONTROL_CONTACT`**
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| SLSFAC | 페널티 스케일 팩터 | 0.1 |
| RWPNAL | 강체벽 페널티 | 0.0 |
| ISLCHK | 초기 관통 검사 | 1 |
| SHLTHK | 접촉에 셸 두께 고려 | 0 |
| OTEFP | 외부 에지 관통 검사 | 0 |

**Implicit 해석 제어 — `*CONTROL_IMPLICIT_xxx`**
| 키워드 | 역할 |
|--------|------|
| `CONTROL_IMPLICIT_GENERAL` | implicit 활성화 (IMFLAG=1) |
| `CONTROL_IMPLICIT_AUTO` | 자동 시간스텝 제어 |
| `CONTROL_IMPLICIT_DYNAMICS` | 동적 implicit (Newmark 등) |
| `CONTROL_IMPLICIT_SOLUTION` | 비선형 수렴 기준 (NSOLVR, ILIMIT) |
| `CONTROL_IMPLICIT_SOLVER` | 선형 방정식 솔버 선택 |
| `CONTROL_IMPLICIT_EIGENVALUE` | 고유치 해석 |
| `CONTROL_IMPLICIT_BUCKLE` | 좌굴 해석 |
| `CONTROL_IMPLICIT_STABILIZATION` | 수렴 안정화 |

**기타 중요 CONTROL**
| 키워드 | 핵심 역할 |
|--------|-----------|
| `CONTROL_ENERGY` | 에너지 균형 옵션 (HGEN, RWEN, SLNTEN, RYLEN) |
| `CONTROL_BULK_VISCOSITY` | Q1, Q2: 체적 점성 (충격파) |
| `CONTROL_SOLID` | 솔리드 요소 옵션 |
| `CONTROL_TERMINATION` | ENDTIM(종료시간), ENDCYC, ENDMAS |
| `CONTROL_ADAPTIVE` | 적응적 메시 재분할 |
| `CONTROL_ALE` | ALE 멀티머티리얼 제어 |
| `CONTROL_DYNAMIC_RELAXATION` | 준정적 선하중 (수렴 기준 DRTOL) |
| `CONTROL_FORMING_xxx` | 성형 해석 제어 (autocheck, trimming 등) |
| `CONTROL_MPP_xxx` | MPP 병렬 분해 및 제어 |
| `CONTROL_SPH` | SPH 입자법 제어 |
| `CONTROL_UNITS` | 단위 시스템 정의 |

---

### 2.3 *SECTION — 요소 섹션 정의 (Chapter 41)

#### 셸 요소 공식 (ELFORM) — `*SECTION_SHELL`
| ELFORM | 이름 | 적분 | 특성 |
|--------|------|------|------|
| 1 | Hughes-Liu | 완전 | 정확, 느림 |
| **2** | **Belytschko-Tsay** | **1점** | **기본값, 가장 빠름, 아워글라스 필요** |
| 3 | BCIZ 삼각형 | — | 비추천 |
| 4 | C0 삼각형 | — | 일반 삼각형 |
| 5 | BT 멤브레인 | 1점 | 막 요소 |
| 6 | S/R Hughes-Liu | 선택적 축소 | — |
| 7 | S/R 공회전 HL | 선택적 축소 | — |
| 8 | Belytschko-Leviathan | — | — |
| 9 | 완전적분 BT 멤브레인 | 완전 | — |
| 10 | Belytschko-Wong-Chiang | 1점 | 와핑 강성 포함 |
| 11 | 고속 Hughes-Liu | 공회전 | — |
| 12 | 평면응력 (xy) | — | 2D |
| 13 | 평면변형률 (xy) | — | 2D |
| 14 | 축대칭 솔리드 (y축) | 면적가중 | 2D |
| 15 | 축대칭 솔리드 (y축) | 체적가중 | 2D |
| **16** | **완전적분 셸** | **2×2** | **매우 빠른 완전적분, 아워글라스 없음** |
| 17 | DKT 삼각형 | — | 이산 Kirchhoff, 좋은 굽힘 |
| 18 | DK 선형 (4각/3각) | — | 6DOF, 고유치/정적 |
| 20 | C0 선형 4절점 | 드릴링 | 6DOF, 고유치/정적 |
| 25 | BT 두께 신축 | 1점 | 두께 방향 변형 포함 |
| 26 | 완전적분 두께 신축 | 2×2 | 두께 방향 변형 포함 |
| 27 | C0 삼각형 두께 신축 | — | 두께 방향 변형 포함 |

#### 셸 섹션 핵심 파라미터
| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| ELFORM | 요소 공식 (위 표 참조) | 2 (BT) |
| SHRF | 전단 보정 계수 (5/6 권장) | 1.0 |
| NIP | 두께 적분점 수 | 2 |
| PROPT | 출력 옵션 | 0 |
| T1-T4 | 각 절점 두께 | 0.0 |
| NLOC | 참조면 위치 (-1=하면, 0=중앙, 1=상면) | 0 |

#### 솔리드 요소 공식 — `*SECTION_SOLID`
| ELFORM | 이름 | 적분점 | 비고 |
|--------|------|--------|------|
| 1 | 정축소적분 | 1점 | 기본, 아워글라스 필요 |
| 2 | 완전적분 | 2×2×2=8 | 정확, 느림, 체적잠금 가능 |
| 3 | 2차 8점 | 2×2×2 | — |
| 4 | S/R 4절점 테트라 | — | 노달 회전 |
| 10 | 1점 테트라 | 1 | 기본 테트라 |
| 13 | 1점 5절점 테트라 | 1 | 노달 회전 |
| -1 | 완전적분 S/R | 8점 | 체적잠금 방지 |
| -2 | 완전적분 S/R | 8점 | 변형 |

#### 빔 요소 — `*SECTION_BEAM`
| ELFORM | 이름 |
|--------|------|
| 1 | Hughes-Liu (기본) |
| 2 | Belytschko-Schwer 적분 빔 |
| 3 | 트러스 |
| 4 | Belytschko-Schwer 결과력 빔 |
| 6 | 이산 빔 (스프링/댐퍼) |
| 9 | 관 (tubular) |

---

### 2.4 *ELEMENT — 요소 정의 (Chapter 19)

| 키워드 | 용도 | 핵심 입력 |
|--------|------|-----------|
| `ELEMENT_SHELL` | 셸 요소 | EID, PID, N1-N4 |
| `ELEMENT_SOLID` | 솔리드 요소 | EID, PID, N1-N8 |
| `ELEMENT_BEAM` | 빔 요소 | EID, PID, N1-N3 (N3=방향노드) |
| `ELEMENT_TSHELL` | 두꺼운 셸 | EID, PID, N1-N8 (3D 응력) |
| `ELEMENT_DISCRETE` | 스프링/댐퍼 | EID, PID, N1, N2 |
| `ELEMENT_SPH` | SPH 입자 | EID, PID, NID |
| `ELEMENT_MASS` | 집중 질량 | EID, NID, MASS |
| `ELEMENT_SEATBELT` | 시트벨트 | 슬립링, 리트랙터 등 |
| `ELEMENT_INERTIA` | 관성 요소 | NID, CID, 관성텐서 |

---

### 2.5 *BOUNDARY — 경계조건 (Chapter 5)

| 키워드 | 용도 |
|--------|------|
| `BOUNDARY_SPC_SET` | 절점 구속 (DOFX,Y,Z,RX,RY,RZ) |
| `BOUNDARY_PRESCRIBED_MOTION_xxx` | 변위/속도/가속도 시간이력 부과 |
| `BOUNDARY_PRESCRIBED_ACCELEROMETER_RIGID` | 강체 가속도계 |
| `BOUNDARY_TEMPERATURE_SET` | 온도 경계 |
| `BOUNDARY_CONVECTION_SET` | 대류 열전달 |
| `BOUNDARY_RADIATION_xxx` | 복사 열전달 |
| `BOUNDARY_FLUX_SET` | 열유속 경계 |
| `BOUNDARY_NON_REFLECTING` | 비반사 경계 (무한 매질) |
| `BOUNDARY_AMBIENT` | ALE 주변 조건 |
| `BOUNDARY_PORE_FLUID` | 공극 유체 경계 |
| `BOUNDARY_ACOUSTIC_xxx` | 음향 경계 |
| `BOUNDARY_CYCLIC` | 주기 대칭 경계 |
| `BOUNDARY_SLIDING_PLANE` | 미끄럼 평면 |

---

### 2.6 *LOAD — 하중 (Chapter 33)

| 키워드 | 용도 |
|--------|------|
| `LOAD_NODE_SET` | 절점 하중 (힘, 모멘트) |
| `LOAD_SEGMENT_SET` | 세그먼트 분포 압력 |
| `LOAD_SHELL_SET` | 셸 분포 하중 |
| `LOAD_BODY_xxx` | 체적력 (중력, 관성력) |
| `LOAD_RIGID_BODY` | 강체 하중 |
| `LOAD_BLAST_ENHANCED` | 폭발 하중 (CONWEP) |
| `LOAD_THERMAL_xxx` | 열 하중 (binout, d3plot, 상수, 커브) |
| `LOAD_SEISMIC_SSI` | 지진 하중 (SSI) |
| `LOAD_MOVING_PRESSURE` | 이동 압력 |
| `LOAD_BEAM` | 빔 분포 하중 |

---

### 2.7 *DEFINE — 정의 (Chapter 17)

| 키워드 | 용도 | 핵심 |
|--------|------|------|
| `DEFINE_CURVE` | **로드커브** (시간-값 관계) | **가장 핵심적인 입력 도구** |
| `DEFINE_TABLE` | 커브의 테이블 | 변형률속도별 σ-ε 등 |
| `DEFINE_TABLE_2D/3D` | 2D/3D 테이블 | 다변수 의존 |
| `DEFINE_COORDINATE_SYSTEM` | 좌표계 | 재료 방향, 경계조건 |
| `DEFINE_COORDINATE_VECTOR` | 벡터 기반 좌표계 | — |
| `DEFINE_VECTOR` | 벡터 정의 | — |
| `DEFINE_FUNCTION` | 수학 함수 | 파라메트릭 입력 |
| `DEFINE_BOX` | 공간 영역 | 적응, 접촉 제한 등 |
| `DEFINE_TRANSFORMATION` | 기하 변환 | 이동, 회전, 스케일 |
| `DEFINE_FRICTION` | 마찰 모델 | — |
| `DEFINE_CURVE_FUNCTION` | 수식 기반 커브 | sin, cos, exp 등 |
| `DEFINE_DE_xxx` | 이산요소(DEM) | 입자 주입, 본딩 등 |
| `DEFINE_SPH_xxx` | SPH | 주입, 메시, 활성 영역 |

---

### 2.8 *DATABASE — 출력 제어 (Chapter 16)

#### ASCII 출력 (시간 이력)
| 키워드 | 출력 내용 |
|--------|-----------|
| `DATABASE_GLSTAT` | 전역 통계 (에너지, 속도 등) |
| `DATABASE_MATSUM` | 재료별 에너지 합계 |
| `DATABASE_RCFORC` | 접촉 반력 |
| `DATABASE_NODOUT` | 절점 이력 (변위, 속도, 가속도) |
| `DATABASE_ELOUT` | 요소 이력 (응력, 변형률) |
| `DATABASE_RBDOUT` | 강체 데이터 |
| `DATABASE_SPCFORC` | 구속 반력 |
| `DATABASE_JNTFORC` | 조인트 힘 |
| `DATABASE_SLEOUT` | 접촉 에너지 |
| `DATABASE_DEFORC` | 이산 요소 힘 |

#### 바이너리 출력
| 키워드 | 출력 내용 |
|--------|-----------|
| `DATABASE_BINARY_D3PLOT` | 전체 모델 상태 (가시화용) |
| `DATABASE_BINARY_D3THDT` | 시간이력 바이너리 |
| `DATABASE_BINARY_D3DUMP` | 재시작 파일 |
| `DATABASE_BINARY_RUNRSF` | 런타임 재시작 |
| `DATABASE_BINARY_INTFOR` | 인터페이스 힘 |

#### 출력 범위 제어
| 키워드 | 역할 |
|--------|------|
| `DATABASE_EXTENT_BINARY` | 출력 변수 범위 (응력텐서, 변형률, 추가 이력변수, NEIPH, NEIPS 등) |
| `DATABASE_CROSS_SECTION_SET` | 단면력 출력 |
| `DATABASE_HISTORY_xxx` | 특정 노드/요소 이력 |

---

### 2.9 *PART — 파트 정의 (Chapter 37)

```
*PART
$   heading
$   PID     SID     MID     EOSID   HGID    GRAV    ADPOPT  TMID
     1       1       1       0       0       0       0       0
```

| 필드 | 설명 |
|------|------|
| PID | 파트 ID (고유) |
| SID | 섹션 ID → *SECTION_xxx 참조 |
| MID | 재료 ID → *MAT_xxx 참조 |
| EOSID | 상태방정식 ID → *EOS_xxx 참조 |
| HGID | 아워글라스 ID → *HOURGLASS 참조 |
| GRAV | 중력 플래그 |
| ADPOPT | 적응적 메시 옵션 |
| TMID | 열 재료 ID → *MAT_THERMAL_xxx 참조 |

#### 특수 파트 키워드
| 키워드 | 용도 |
|--------|------|
| `PART_COMPOSITE` | 적층 복합재 (각 층별 MID, 두께, 각도, 적분점) |
| `PART_MOVE` | 파트 이동 (좌표 변환) |
| `PART_ANNEAL` | 어닐링 (응력 초기화) |
| `PART_SENSOR` | 센서 기반 파트 활성화 |
| `PART_STACKED_ELEMENTS` | 적층 요소 |
| `PART_ADAPTIVE_FAILURE` | 적응적 파괴 |

---

### 2.10 *INITIAL — 초기조건 (Chapter 28)

| 키워드 | 용도 |
|--------|------|
| `INITIAL_VELOCITY` | 초기 속도 (부분/전체) |
| `INITIAL_VELOCITY_GENERATION` | 병진+회전 속도 생성 |
| `INITIAL_VELOCITY_RIGID_BODY` | 강체 초기 속도 |
| `INITIAL_STRESS_SHELL/SOLID` | 초기 응력 (사전 응력) |
| `INITIAL_STRAIN_SHELL/SOLID` | 초기 변형률 |
| `INITIAL_TEMPERATURE_SET` | 초기 온도 |
| `INITIAL_DETONATION` | 기폭점 (폭약) |
| `INITIAL_VOLUME_FRACTION_GEOMETRY` | ALE 체적분율 (기하학적) |
| `INITIAL_FOAM_REFERENCE_GEOMETRY` | 폼 참조 기하 |
| `INITIAL_VEHICLE_KINEMATICS` | 차량 초기 위치/속도 |

---

### 2.11 *CONSTRAINED — 구속 (Chapter 10)

| 키워드 | 용도 |
|--------|------|
| `CONSTRAINED_NODAL_RIGID_BODY` | 절점 강체 (RBE2 유사) |
| `CONSTRAINED_INTERPOLATION` | 보간 구속 (RBE3 유사) |
| `CONSTRAINED_SPOTWELD` | 스폿용접 (파괴 기준 포함) |
| `CONSTRAINED_JOINT_xxx` | 조인트 (REVOLUTE, SPHERICAL, CYLINDRICAL 등) |
| `CONSTRAINED_EXTRA_NODES` | 강체에 추가 절점 |
| `CONSTRAINED_RIGID_BODIES` | 강체 병합 |
| `CONSTRAINED_BEAM_IN_SOLID` | 솔리드 내 빔 구속 |
| `CONSTRAINED_LAGRANGE_IN_SOLID` | ALE 유체-구조 연성 |
| `CONSTRAINED_SHELL_IN_SOLID` | 솔리드 내 셸 구속 |
| `CONSTRAINED_TIE-BREAK` | 파괴 가능 연결 |
| `CONSTRAINED_LINEAR_xxx` | 선형 구속 방정식 |

---

### 2.12 *DAMPING — 감쇠 (Chapter 15)

| 키워드 | 용도 |
|--------|------|
| `DAMPING_GLOBAL` | 전역 감쇠 |
| `DAMPING_PART_MASS` | 파트별 질량비례 감쇠 |
| `DAMPING_PART_STIFFNESS` | 파트별 강성비례 감쇠 |
| `DAMPING_FREQUENCY_RANGE` | 주파수 범위 감쇠 |
| `DAMPING_RELATIVE` | 파트 간 상대 감쇠 |

---

### 2.13 *SET — 세트 정의 (Chapter 43)

| 키워드 | 용도 |
|--------|------|
| `SET_NODE_LIST` | 절점 세트 |
| `SET_SHELL_LIST` | 셸 요소 세트 |
| `SET_SOLID_LIST` | 솔리드 요소 세트 |
| `SET_SEGMENT` | 세그먼트 세트 |
| `SET_PART_LIST` | 파트 세트 |
| `SET_BEAM_LIST` | 빔 요소 세트 |
| `SET_xxx_GENERAL` | 일반화 세트 (조건 기반) |
| `SET_xxx_ADD` | 세트 합집합 |
| `SET_xxx_INTERSECT` | 세트 교집합 |

---

### 2.14 기타 핵심 키워드

| 키워드 | 용도 |
|--------|------|
| `*AIRBAG_PARTICLE` | 입자 기반 에어백 (CPM, 가장 정교) |
| `*AIRBAG_SIMPLE_AIRBAG_MODEL` | 간단 에어백 |
| `*ALE_MULTI-MATERIAL_GROUP` | ALE 멀티머티리얼 그룹 |
| `*ALE_STRUCTURED_MESH` | 구조적 ALE 메시 |
| `*RIGIDWALL_PLANAR/GEOMETRIC` | 강체벽 |
| `*SENSOR_xxx` | 센서 (접촉, 절점, 요소 기반) |
| `*DEFORMABLE_TO_RIGID` | 변형체↔강체 전환 |
| `*INCLUDE_STAMPED_PART` | 성형 결과 맵핑 |
| `*INCLUDE_TRANSFORM` | 포함+좌표변환+단위변환 |
| `*INTERFACE_SPRINGBACK` | 스프링백 인터페이스 |
| `*FATIGUE` | 피로 수명 예측 |
| `*FREQUENCY_DOMAIN_xxx` | 주파수 영역 해석 (FRF, SSD, 음향) |
| `*IGA_xxx` | 등기하학적 해석 (NURBS) |
| `*RVE_ANALYSIS_FEM` | 대표 체적 요소 해석 |

---

## 3. 재료 모델 (Vol II)

### 3.1 EOS (Equation of State) — 솔리드 요소 전용

| EOS # | 키워드 | 용도 | 핵심 파라미터 |
|-------|--------|------|---------------|
| 1 | `EOS_LINEAR_POLYNOMIAL` | 일반 선형 다항식 | C0-C6, E0, V0 |
| 2 | `EOS_JWL` | 폭약 팽창가스 | A, B, R1, R2, ω |
| 4 | `EOS_GRUNEISEN` | 충격파 (금속) | C, S1, S2, S3, γ0, a |
| 8 | `EOS_TABULATED_COMPACTION` | 다공성 재료 압밀 | 테이블 입력 |
| 9 | `EOS_TABULATED` | 범용 테이블 | p(μ, E) 테이블 |
| 12 | `EOS_IDEAL_GAS` | 이상기체 | Cv, Cp, T0 |
| 14 | `EOS_JWLB` | 폭약 (JWL-B) | 고급 폭약 |
| 15 | `EOS_GASKET` | 가스켓 | 두꺼운 셸 전용 |
| 16 | `EOS_MIE_GRUNEISEN` | Mie-Grüneisen | 고급 충격파 |

**핵심 매개변수 정의:**
- μ = ρ/ρ₀ - 1 (압축비)
- V0 = 초기 상대 체적 (ρ₀/ρ|t=0)
- E0 = 초기 내부 에너지 (체적당)

### 3.2 금속 재료

#### MAT_001: *MAT_ELASTIC (등방 탄성)
- 빔/셸/솔리드 모두 사용
- 파라미터: MID, RO, E, PR, DA(축방향 감쇠), DB(굽힘 감쇠)
- FLUID 옵션: 유체 모델링 (K=체적탄성률, 전단=0)
- 주의: 유한 변형에서 불안정 가능 → 대변형시 MAT_002 사용

#### MAT_003: *MAT_PLASTIC_KINEMATIC (소성 운동학)
- 이동경화(β=0) / 등방경화(β=1) / 혼합경화
- Cowper-Symonds 변형률속도: σ_y × [1 + (ε̇/C)^(1/P)]
- 파괴: FAIL (유효소성변형률 한계)
- 빔/셸/솔리드

#### MAT_009: *MAT_NULL
- 편차응력 = 0 (유체 거동)
- EOS 필수 (압력만 존재)
- PC (캐비테이션 압력), MU (동점성계수)
- 용도: ALE 유체, 비어있는 공간, 공기

#### MAT_015: *MAT_JOHNSON_COOK
- σ = (A + Bε^n)(1 + C·ln(ε̇*))(1 - T*^m)
- 고속변형, 온도연화, 손상 (D1-D5)
- EOS 필수 (솔리드), SPALL (파편화 모델)
- 용도: 폭발 성형, 탄도 관통, 충돌

#### MAT_018: *MAT_POWER_LAW_PLASTICITY
- σ = kε^n
- 성형 해석용, 등방 경화
- SRC/SRP: 변형률속도 파라미터

#### MAT_020: *MAT_RIGID
- 완전 강체 (자유도 제한)
- CMO: 구속 옵션 (0=없음, 1=전역, -1=로컬 구속)
- CON1/CON2: 구속 조건 (4=XYZ고정, 7=RXRYRZ고정)
- ALIAS: 비활성 강체 → 재료 속성은 다른 MID 참조
- 용도: 금형, 강체벽, 더미 관절

#### MAT_024: *MAT_PIECEWISE_LINEAR_PLASTICITY (★가장 범용적★)
- 임의 σ-ε 커브 (LCSS = 로드커브 또는 TABLE ID)
- TABLE: 변형률속도별 σ-ε 커브 → 보간
- C, P: Cowper-Symonds 변형률속도 (LCSS 없을 때)
- FAIL: 유효소성변형률 파괴 기준 (>0), TDEL: 최소 시간스텝 파괴
- VP: 점소성 공식 (0=스케일, 1=점소성)
- 옵션: LOG_INTERPOLATION, STOCHASTIC, MIDFAIL, 2D
- 빔/셸/솔리드/후판셸 모두 사용
- **가장 많이 사용되는 재료 모델**

### 3.3 복합재/직물

| MAT# | 이름 | 핵심 특성 |
|------|------|-----------|
| 022 | `MAT_COMPOSITE_DAMAGE` | Chang-Chang 파괴 기준, 셸 전용 |
| **054** | `MAT_ENHANCED_COMPOSITE_DAMAGE` | **향상된 Chang-Chang, 적층 셸** |
| **055** | `MAT_ENHANCED_COMPOSITE_DAMAGE` | **= 054 (동일 모델, 입력 형태 다름)** |
| 058 | `MAT_LAMINATED_COMPOSITE_FABRIC` | 적층 직물 복합재 |
| 059 | `MAT_COMPOSITE_FAILURE` | Hashin 파괴 기준 |
| **034** | `MAT_FABRIC` | 에어백/시트벨트 직물 |
| 261 | `MAT_LAMINATED_FRACTURE_DAIMLER_PINHO` | 적층 파괴 (Pinho) |
| 262 | `MAT_LAMINATED_FRACTURE_DAIMLER_CAMANHO` | 적층 파괴 (Camanho) |

### 3.4 고무/폼/점탄성

| MAT# | 이름 | 용도 |
|------|------|------|
| 006 | `MAT_VISCOELASTIC` | 선형 점탄성 |
| 007 | `MAT_BLATZ-KO_RUBBER` | 압축 가능 고무 |
| 027 | `MAT_MOONEY-RIVLIN_RUBBER` | 2파라미터 고무 |
| 057 | `MAT_LOW_DENSITY_FOAM` | 저밀도 폼 |
| 062 | `MAT_VISCOUS_FOAM` | 점성 폼 |
| 063 | `MAT_CRUSHABLE_FOAM` | 압축 폼 (에너지 흡수) |
| 073 | `MAT_FU_CHANG_FOAM` | 변형률속도 의존 폼 |
| 076 | `MAT_GENERAL_VISCOELASTIC` | 일반 점탄성 (Prony급수) |
| 077 | `MAT_OGDEN_RUBBER` | Ogden 고무 |
| 077H | `MAT_HYPERELASTIC_RUBBER` | 초탄성 고무 (범용) |
| 181/183 | `MAT_SIMPLIFIED_RUBBER` | 간소화 고무/폼 |
| 087 | `MAT_CELLULAR_RUBBER` | 셀룰러 고무 |

### 3.5 콘크리트/지반

| MAT# | 이름 | 용도 |
|------|------|------|
| 005 | `MAT_SOIL_AND_FOAM` | 토양/폼 (압력 의존) |
| 014 | `MAT_SOIL_AND_FOAM_FAILURE` | 인장 파괴 추가 |
| 016 | `MAT_PSEUDO_TENSOR` | 콘크리트 (구) |
| 072R3 | `MAT_CONCRETE_DAMAGE_REL3` | 콘크리트 손상 (Release 3) |
| 084 | `MAT_WINFRITH_CONCRETE` | Winfrith 콘크리트 |
| 159 | `MAT_CSCM` | 연속표면 캡 모델 (FHWA) |
| 173 | `MAT_MOHR_COULOMB` | Mohr-Coulomb |
| 193 | `MAT_DRUCKER_PRAGER` | Drucker-Prager |
| 079 | `MAT_HYSTERETIC_SOIL` | 이력 토양 |

### 3.6 이산요소 (스프링/댐퍼/케이블)

| MAT# | 이름 | 특성 |
|------|------|------|
| 066 | `MAT_LINEAR_ELASTIC_DISCRETE_BEAM` | 6DOF 선형 탄성 |
| 067 | `MAT_NONLINEAR_ELASTIC_DISCRETE_BEAM` | 6DOF 비선형 탄성 |
| 068 | `MAT_NONLINEAR_PLASTIC_DISCRETE_BEAM` | 6DOF 비선형 소성 |
| 071 | `MAT_CABLE_DISCRETE_BEAM` | 케이블 (인장만) |
| 069 | `MAT_SID_DAMPER_DISCRETE_BEAM` | SID 댐퍼 |
| 070 | `MAT_HYDRAULIC_GAS_DAMPER` | 유압/가스 댐퍼 |
| 093 | `MAT_ELASTIC_6DOF_SPRING_DISCRETE_BEAM` | 6DOF 탄성 스프링 |
| 095 | `MAT_INELASTIC_6DOF_SPRING_DISCRETE_BEAM` | 6DOF 비탄성 스프링 |

### 3.7 *MAT_ADD — 재료 추가 기능

| 키워드 | 기능 | 핵심 |
|--------|------|------|
| `MAT_ADD_EROSION` | **범용 파괴 기준** | MXPRES, MNPRES, SIGP1, SIGVM, MXEPS, EPSSH, MNEPS 등 |
| `MAT_ADD_DAMAGE_GISSMO` | GISSMO 손상 | 파괴 변형률 커브 + 페이딩 |
| `MAT_ADD_THERMAL_EXPANSION` | 열팽창 | α (열팽창계수) |
| `MAT_ADD_FATIGUE` | 피로 | S-N 또는 ε-N 커브 |
| `MAT_ADD_EROSION` 파괴 기준: | | |
| — MXPRES | 최대 압력 | |
| — MNPRES | 최소 압력 (인장) | |
| — SIGP1 | 최대 주응력 | |
| — SIGVM | 최대 von Mises | |
| — MXEPS | 최대 주변형률 | |
| — EPSSH | 전단 변형률 | |
| — NUMFIP | 파괴 적분점 수 | |

### 3.8 열 재료 — `*MAT_THERMAL_xxx`

| 키워드 | 용도 |
|--------|------|
| `MAT_THERMAL_ISOTROPIC` | 등방 열전도 (TC, HC) |
| `MAT_THERMAL_ORTHOTROPIC` | 이방 열전도 |
| `MAT_THERMAL_ISOTROPIC_TD` | 온도 의존 등방 |
| `MAT_THERMAL_ORTHOTROPIC_TD` | 온도 의존 이방 |
| `MAT_THERMAL_DISCRETE_BEAM` | 이산빔 열 |
| `MAT_THERMAL_CHEMICAL_REACTION` | 화학반응 열 |

---

## 4. 멀티피직스 솔버 (Vol III)

### 4.0 개요
Vol III에는 **5개 주요 솔버**가 있으며, 모두 구조 솔버와 연성 가능:
1. CESE (압축성 유동)
2. DUALCESE (개선된 압축성 유동)
3. ICFD (비압축성 유동)
4. EM (전자기)
5. BATTERY (배터리 전기화학)

### 4.1 *CESE — 압축성 유동 (CE/SE 방법)
- **원리**: Conservation Element/Solution Element (NASA Chang)
- **용도**: 충격파, 폭발파, 캐비테이션, 초음속 제트, 화학반응 유동
- **FSI**: (1) 고정 Euler + 이동 구조, (2) 이동 CESE 메시
- **열전달**: 고체 열솔버와 공액열전달

| 키워드 그룹 | 용도 |
|-------------|------|
| `CESE_CONTROL_SOLVER` | 솔버 제어 |
| `CESE_CONTROL_TIMESTEP` | 시간스텝 |
| `CESE_BOUNDARY_xxx` | 경계조건 (FSI, 반사, 비반사, 처방 등) |
| `CESE_INITIAL` | 초기 조건 |
| `CESE_EOS_xxx` | 상태방정식 (이상기체, 인플레이터) |
| `CESE_MAT_xxx` | 유체 물성 |
| `CESE_PART` | 유체 파트 |
| `CESE_DATABASE_xxx` | 출력 제어 |

### 4.2 *DUALCESE — 개선된 압축성 유동
- 정밀도/안정성 개선 버전
- 이상유동(two-phase), 상변화(phase change) 지원
- **REFPROP/COOLPROP** EOS: 산업용 순수/혼합 유체 물성
- 다중 FSI 접근법을 서로 다른 영역에 적용 가능

| 키워드 그룹 | 용도 |
|-------------|------|
| `DUALCESE_CONTROL_SOLVER` | 솔버 제어 |
| `DUALCESE_BOUNDARY_xxx` | 경계조건 (처방, FSI, 반사 등) |
| `DUALCESE_EOS_xxx` | EOS (이상기체, JWL, REFPROP, COOLPROP, NAStiffened) |
| `DUALCESE_SOLVER_xxx` | 솔버 선택 (Euler, Navier-Stokes, 다상) |
| `DUALCESE_INITIAL_xxx` | 초기 조건 (단일/이상/상변화) |
| `DUALCESE_MAT_GAS/LIQUID` | 기체/액체 물성 |
| `DUALCESE_DATABASE_xxx` | 출력 |

### 4.3 *ICFD — 비압축성 유동
- **완전 연성 FSI**: 약연성(explicit) / 강연성(implicit)
- 자유 표면, 이상류 (Level Set), 종 수송
- **난류**: k-ε, k-ω, SST, LES, DES, Spalart-Allmaras 등
- **자동 체적 메시**: `*MESH_xxx`로 표면→테트라 변환
- 적응적 리메싱, 경계층 메시
- 공액열전달 (모놀리식)
- 비뉴턴 유체, 다공성 매체

| 키워드 그룹 | 용도 |
|-------------|------|
| `ICFD_CONTROL_xxx` | 솔버 제어 (FSI, 난류, 시간, 메시 등) |
| `ICFD_BOUNDARY_xxx` | 경계 (FSI, 속도, 압력, 온도, 자유미끄럼, 비미끄럼) |
| `ICFD_MAT` | 유체 물성 (밀도, 점성) |
| `ICFD_PART/PART_VOL` | 경계면/체적 파트 |
| `ICFD_INITIAL_xxx` | 초기 조건 |
| `ICFD_DATABASE_xxx` | 출력 (drag, flux, HTC, residual 등) |
| `ICFD_MODEL_xxx` | 모델 (비뉴턴, 다공성, 점탄성) |
| `ICFD_SOLVER_TOL_xxx` | 수렴 공차 |

### 4.4 *EM — 전자기 솔버
- **Eddy-current** (와전류) 근사: Maxwell 방정식
- **FEM**(도체) + **BEM**(공기/절연체) → 공기 메시 불필요
- 구조 연성: 로렌츠 힘 → 운동방정식
- 열 연성: 줄열(ohmic heating) → 열솔버
- **용도**: 자기 성형, 자기 용접, 유도가열, 링 팽창, 배터리
- **심장 전기생리학**: `EM_EP_xxx` (ten Tusscher, FitzHugh-Nagumo 등)

| 키워드 그룹 | 용도 |
|-------------|------|
| `EM_CONTROL` | 솔버 제어 (NUMLS, ETEFP 등) |
| `EM_CONTROL_COUPLING` | 구조/열 연성 제어 |
| `EM_CONTROL_TIMESTEP` | EM 시간스텝 |
| `EM_BOUNDARY_xxx` | 경계조건 |
| `EM_CIRCUIT_xxx` | 전기회로 (전원, 연결, Rogowski) |
| `EM_MAT_001~006` | EM 물성 (도체, 절연체, 등) |
| `EM_RANDLES_xxx` | 배터리 전기화학 (Randles 회로) |
| `EM_SOLVER_xxx` | 솔버 선택 (FEM, BEM, FEM-BEM) |
| `EM_PERMANENT_MAGNET` | 영구자석 |
| `EM_DATABASE_xxx` | 출력 |

### 4.5 *BATTERY — 배터리 전기화학
- **1D 전기화학 솔버** ↔ 구조/열 솔버 암시적 연성
- 장시간 배터리-구조 상호작용

| 키워드 | 용도 |
|--------|------|
| `BATTERY_ECHEM_CONTROL_SOLVER` | 솔버 제어 |
| `BATTERY_ECHEM_CELL_GEOMETRY` | 셀 기하 |
| `BATTERY_ECHEM_MAT_ANODE` | 음극 물성 |
| `BATTERY_ECHEM_MAT_CATHODE` | 양극 물성 |
| `BATTERY_ECHEM_MAT_ELECTROLYTE` | 전해질 물성 |
| `BATTERY_ECHEM_INITIAL` | 초기 조건 |
| `BATTERY_ECHEM_THERMAL` | 열 연성 |
| `BATTERY_DATABASE_xxx` | 출력 |

### 4.6 지원 키워드

| 키워드 | 용도 |
|--------|------|
| `*MESH_BL` | 경계층 메시 (ICFD용) |
| `*MESH_SIZE` | 메시 크기 |
| `*MESH_VOLUME` | 체적 메시 |
| `*MESH_SURFACE_xxx` | 표면 메시 |
| `*CHEMISTRY_xxx` | 화학반응 모델 (CESE 전용) |
| `*STOCHASTIC_SPRAY_PARTICLES` | 스프레이 입자 |
| `*LSO_xxx` | 멀티피직스 데이터 출력 메커니즘 |

---

## 5. 고급 기능 핵심 포인트 (예제 제작 참조)

### 5.1 Explicit/Implicit 전환
- `*CONTROL_IMPLICIT_GENERAL` (IMFLAG=1 활성화)
- `*CONTROL_IMPLICIT_AUTO` (자동 시간스텝)
- `*CONTROL_IMPLICIT_DYNAMICS` (Newmark β법)
- 용도: 준정적 성형 → 동적 충돌, 고유치, 좌굴

### 5.2 적응적 메시 리파인먼트
- `*CONTROL_ADAPTIVE` (ADPTYP, ADPOPT)
- 곡률/응력/변형률 기반 셸 리파인먼트
- `*DEFINE_BOX_ADAPTIVE` (영역 제한)
- `*CONTROL_REFINE_SHELL/SOLID` (셸/솔리드 리파인)

### 5.3 ALE (Arbitrary Lagrangian-Eulerian)
- `*ALE_MULTI-MATERIAL_GROUP` (멀티머티리얼 그룹)
- `*CONSTRAINED_LAGRANGE_IN_SOLID` (유체-구조 연성)
- `*INITIAL_VOLUME_FRACTION_GEOMETRY` (초기 체적분율)
- `*SECTION_SOLID` (ELFORM=11/12: ALE 요소)
- 용도: 폭발-구조, 조류충돌, 연료탱크

### 5.4 SPH (Smoothed Particle Hydrodynamics)
- `*SECTION_SPH` (CSLH, HMIN, HMAX)
- `*CONTROL_SPH` (NCBS, FORM, MEMORY)
- `*DEFINE_SPH_MESH_xxx` (입자 생성)
- `*CONTACT_SPG` (SPH-구조 접촉)
- 용도: 대변형, 파편, 유체 충돌

### 5.5 에어백 시뮬레이션
- `*AIRBAG_PARTICLE` (CPM): 입자 기반, 가장 정교
- `*AIRBAG_HYBRID_CHEMKIN`: 화학 기반 인플레이터
- `*AIRBAG_WANG_NEFSKE`: 열역학적 에어백
- `*AIRBAG_REFERENCE_GEOMETRY`: 접힌 형상 참조

### 5.6 질량 스케일링 (Mass Scaling)
- `DT2MS < 0` in `*CONTROL_TIMESTEP`
- TSSFAC × |DT2MS| = 최소 허용 시간스텝
- MS1ST=0 (지속 추가) vs MS1ST=1 (초기만)
- ENDMAS in `*CONTROL_TERMINATION` (최대 질량 증가 제한)

### 5.7 다단계 해석 (Multi-stage)
- `*INTERFACE_SPRINGBACK` → dynain 파일 출력
- `*INCLUDE_STAMPED_PART` → 성형 → 충돌 맵핑
- Appendix X: 다단계 해석 가이드

### 5.8 사용자 정의 (User-Defined)
- `*MAT_USER_DEFINED_MATERIAL_MODELS` (MAT_041-050)
- Appendix A: Fortran 서브루틴 인터페이스
- 동적/정적 링크 지원

### 5.9 Mortar 접촉 (Implicit 최적화)
- `AUTOMATIC_SURFACE_TO_SURFACE_MORTAR`
- `AUTOMATIC_SINGLE_SURFACE_MORTAR`
- 세그먼트-to-세그먼트, implicit에 최적

### 5.10 피로 해석
- `*FATIGUE` + `*MAT_ADD_FATIGUE`
- `*FATIGUE_LOADSTEP` (하중 단계)
- `*FATIGUE_MEAN_STRESS_CORRECTION` (평균 응력 보정)

---

## 6. 키워드 상호 참조 다이어그램

```
┌─────────────┐     ┌──────────────┐
│  *NODE      │────→│ *ELEMENT_xxx │←──── NID 연결성
│  NID,X,Y,Z  │     │ EID,PID,N1.. │
└─────────────┘     └──────┬───────┘
                           │ PID
                    ┌──────▼───────┐
                    │   *PART      │
                    │ PID,SID,MID, │
                    │ EOSID,HGID,  │
                    │ TMID         │
                    └──┬───┬───┬──┘
          SID ┌────────┘   │   └────────┐ EOSID
    ┌─────────▼──────┐  MID  ┌─────────▼──────┐
    │ *SECTION_xxx   │     │ │  *EOS_xxx      │
    │ SID,ELFORM,NIP │     │ │  EOSID,...     │
    └────────────────┘     │ └────────────────┘
                    ┌──────▼───────┐
                    │  *MAT_xxx   │
                    │  MID,RO,E.. │
                    └──────┬──────┘
                           │ TMID
                    ┌──────▼──────────┐
                    │*MAT_THERMAL_xxx │
                    └─────────────────┘

*DEFINE_CURVE (LCID) ←─── 하중커브, 재료커브, 경계조건에서 참조
*DEFINE_TABLE (TBID) ←─── 다변수 테이블 (변형률속도 등)
*SET_xxx (SID)       ←─── 경계조건, 하중, 접촉에서 참조
*DEFINE_COORDINATE   ←─── 재료 방향, 경계 방향에서 참조
```

---

## 7. 자주 쓰는 최소 입력 데크 구조

```
*KEYWORD
*TITLE
My LS-DYNA Model
$
*CONTROL_TERMINATION
$  ENDTIM
   0.010
$
*CONTROL_TIMESTEP
$  DTINIT  TSSFAC
   0.0     0.90
$
*DATABASE_BINARY_D3PLOT
$  DT
   0.0001
$
*DATABASE_GLSTAT
   0.00001
$
*NODE
$  NID        X         Y         Z
   1       0.000     0.000     0.000
   ...
$
*ELEMENT_SHELL
$  EID   PID   N1   N2   N3   N4
   1      1     1    2    3    4
   ...
$
*PART
$  PID   SID   MID
   1      1     1
$
*SECTION_SHELL
$  SID  ELFORM  SHRF   NIP  PROPT
   1       2    0.833   5     0
$                T1      T2      T3      T4
                1.0     1.0     1.0     1.0
$
*MAT_PIECEWISE_LINEAR_PLASTICITY
$  MID      RO       E        PR     SIGY    ETAN
   1     7.85E-9  210000.   0.30    250.0    1000.
$  C        P      LCSS     LCSR      VP
   0.0     0.0       0        0      0.0
$
*END
```

---

*이 문서는 LS-DYNA R16 매뉴얼 Vol I/II/III에서 추출된 RAG 참조용 요약입니다.*
*고급 예제 제작 시 각 키워드의 상세 파라미터는 원본 매뉴얼에서 확인하세요.*
