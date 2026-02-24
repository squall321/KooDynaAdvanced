*KEYWORD
*TITLE
Li-ion Cell - EM Randles Circuit (Wound Model)
$
$ ============================================================
$ EM + Randles 분포 회로 — 와인딩형(Flat Wound / Jellyroll)
$
$ 와인딩형은 연속 나선 구조이므로 단일 EM_RANDLES_SOLID로 정의.
$ PID 체계: 2001(Al CC), 2002(NMC), 2003(Sep), 2004(Graphite), 2005(Cu CC)
$
$ 전략:
$   - 단일 Randles 회로 → 전체 젤리롤 대표
$   - 분리막 erosion → EM_RANDLES_SHORT → 내부 단락
$   - Joule heating → 열솔버 → 온도 피드백
$   - 열폭주: EM_RANDLES_EXOTHERMIC_REACTION
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== EM SOLVER CONTROL ====================
$
*EM_CONTROL
$    EMSOL     NUMLS              DIMTYPE    NPERIO            NCYLFEM   NCYLBEM
         3        50                    3         0                  1         0
$
$ EMSOL=3: Resistive heating (배터리 단락 줄열에 적합)
$
*EM_CONTROL_COUPLING
$    THCPL     SMCPL     THLCID    SMLCID   THCPLFL   SMCPLFL
         2         0          0         0         0         0
$
$ THCPL=2: Element-level Joule heating (Randles 배터리에 권장)
$ SMCPL=1: Lorentz force → 구조 연성
$
*EM_CONTROL_TIMESTEP
$   TSTYPE   DTCONST      LCID    FACTOR     TSMIN     TSMAX     RLCSF    MECATS
         5     0.001         0       1.0   1.0E-06       1.0       0.0         1
$
$ TSTYPE=5: EM 시간스텝 = 열 시간스텝 (동기화)
$
*EM_CONTROL_CONTACT
$     EMCT    CCONLY     CTYPE     DTYPE      EPS1      EPS2      EPS3        D0
         1         0         0         0     0.001     0.001     0.001       0.0
$
$ EM 접촉: 도체 간 접촉 감지 활성화
$
*EM_CONTROL_EROSION
$ 삭제된 요소를 EM 계산에서 제거
$ Card 1: ECTRL (1=ON: 침식 요소를 EM 행렬에서 제거)
         1
$
$ ==================== EM MATERIAL CONDUCTIVITY ====================
$
$ *EM_MAT_001 Card1: MID MTYPE SIGMA SIGY SIGZ EOSID AOPT MACF
$ MTYPE=2: isotropic conductor  |  MTYPE=1: non-conductor (insulator)
$ Field8=MACF (NOT RANDLETYPE). Part roles set by EM_RANDLES_SOLID.
$
*EM_MAT_001
$      MID     MTYPE     SIGMA
         1         2  3.77e+04
$ MID 1: Al CC, conductor, sigma=3.77e4 S/mm
*EM_MAT_001
         2         2  5.96e+04
$ MID 2: Cu CC, conductor, sigma=5.96e4 S/mm
*EM_MAT_001
         3         1
$ MID 3: NMC cathode, non-conductor
*EM_MAT_001
         4         1
$ MID 4: Graphite anode, non-conductor
*EM_MAT_001
         5         1
$ MID 5: PE separator, non-conductor
*EM_MAT_001
         6         1
$ MID 6: Pouch, EM inactive
*EM_MAT_001
         7         1
$ MID 7: PCM/Impactor, EM inactive
*EM_MAT_001
         8         1
$ MID 8: Electrolyte, non-conductor
$
$ ==================== SOC/온도 의존 Randles TABLE ====================
$
$ ▶ TABLE 8001~8006: SOC×온도 2D 보간 (R0/R1/C1 충전·방전)
$   EM_RANDLES_SOLID에서 음수 값으로 참조
$
$ TABLE 8001: R0 충전 (SOC, Temperature) → R0CHA
*DEFINE_TABLE
$     TBID
      8001
$           Temperature(K)    LCID
              273.15         8011
              298.15         8012
              323.15         8013
              373.15         8014
              473.15         8015
$
*DEFINE_CURVE
      8011
$           SOC        R0CHA(Ohm) at 273K (0°C)
            0.0        0.060
            0.2        0.050
            0.5        0.045
            0.8        0.050
            1.0        0.060
*DEFINE_CURVE
      8012
$           SOC        R0CHA(Ohm) at 298K (25°C)
            0.0        0.035
            0.2        0.030
            0.5        0.028
            0.8        0.030
            1.0        0.035
*DEFINE_CURVE
      8013
$           SOC        R0CHA(Ohm) at 323K (50°C)
            0.0        0.025
            0.2        0.020
            0.5        0.018
            0.8        0.020
            1.0        0.025
*DEFINE_CURVE
      8014
$           SOC        R0CHA(Ohm) at 373K (100°C)
            0.0        0.015
            0.2        0.012
            0.5        0.010
            0.8        0.012
            1.0        0.015
*DEFINE_CURVE
      8015
$           SOC        R0CHA(Ohm) at 473K (200°C)
            0.0        0.010
            0.2        0.008
            0.5        0.006
            0.8        0.008
            1.0        0.010
$
$ TABLE 8002: R0 방전 → R0DIS
*DEFINE_TABLE
      8002
              273.15         8021
              298.15         8022
              323.15         8023
              373.15         8024
              473.15         8025
$
*DEFINE_CURVE
      8021
            0.0        0.065
            0.2        0.055
            0.5        0.050
            0.8        0.055
            1.0        0.065
*DEFINE_CURVE
      8022
            0.0        0.040
            0.2        0.035
            0.5        0.032
            0.8        0.035
            1.0        0.040
*DEFINE_CURVE
      8023
            0.0        0.030
            0.2        0.025
            0.5        0.022
            0.8        0.025
            1.0        0.030
*DEFINE_CURVE
      8024
            0.0        0.018
            0.2        0.015
            0.5        0.012
            0.8        0.015
            1.0        0.018
*DEFINE_CURVE
      8025
            0.0        0.012
            0.2        0.010
            0.5        0.008
            0.8        0.010
            1.0        0.012
$
$ TABLE 8003: R1 충전 → R10CHA
*DEFINE_TABLE
      8003
              273.15         8031
              298.15         8032
              323.15         8033
              373.15         8034
              473.15         8035
$
*DEFINE_CURVE
      8031
            0.0        0.040
            0.5        0.035
            1.0        0.040
*DEFINE_CURVE
      8032
            0.0        0.025
            0.5        0.020
            1.0        0.025
*DEFINE_CURVE
      8033
            0.0        0.018
            0.5        0.015
            1.0        0.018
*DEFINE_CURVE
      8034
            0.0        0.010
            0.5        0.008
            1.0        0.010
*DEFINE_CURVE
      8035
            0.0        0.006
            0.5        0.005
            1.0        0.006
$
$ TABLE 8004: R1 방전 → R10DIS
*DEFINE_TABLE
      8004
              273.15         8041
              298.15         8042
              323.15         8043
              373.15         8044
              473.15         8045
$
*DEFINE_CURVE
      8041
            0.0        0.050
            0.5        0.040
            1.0        0.050
*DEFINE_CURVE
      8042
            0.0        0.030
            0.5        0.025
            1.0        0.030
*DEFINE_CURVE
      8043
            0.0        0.022
            0.5        0.018
            1.0        0.022
*DEFINE_CURVE
      8044
            0.0        0.012
            0.5        0.010
            1.0        0.012
*DEFINE_CURVE
      8045
            0.0        0.008
            0.5        0.006
            1.0        0.008
$
$ TABLE 8005: C1 충전 → C10CHA
*DEFINE_TABLE
      8005
              273.15         8051
              298.15         8052
              323.15         8053
              373.15         8054
              473.15         8055
$
*DEFINE_CURVE
      8051
            0.0        600.0
            0.5        800.0
            1.0        600.0
*DEFINE_CURVE
      8052
            0.0        800.0
            0.5       1000.0
            1.0        800.0
*DEFINE_CURVE
      8053
            0.0       1000.0
            0.5       1200.0
            1.0       1000.0
*DEFINE_CURVE
      8054
            0.0       1200.0
            0.5       1500.0
            1.0       1200.0
*DEFINE_CURVE
      8055
            0.0       1500.0
            0.5       2000.0
            1.0       1500.0
$
$ TABLE 8006: C1 방전 → C10DIS
*DEFINE_TABLE
      8006
              273.15         8061
              298.15         8062
              323.15         8063
              373.15         8064
              473.15         8065
$
*DEFINE_CURVE
      8061
            0.0        600.0
            0.5        800.0
            1.0        600.0
*DEFINE_CURVE
      8062
            0.0        800.0
            0.5       1000.0
            1.0        800.0
*DEFINE_CURVE
      8063
            0.0       1000.0
            0.5       1200.0
            1.0       1000.0
*DEFINE_CURVE
      8064
            0.0       1200.0
            0.5       1500.0
            1.0       1200.0
*DEFINE_CURVE
      8065
            0.0       1500.0
            0.5       2000.0
            1.0       1500.0
$
$ ==================== RANDLES CIRCUIT (WOUND — 단일) ====================
$
$ 와인딩형은 연속 나선으로 모든 레이어가 동일 PID를 공유
$ → 단일 EM_RANDLES_SOLID로 전체 젤리롤 표현
$
*EM_RANDLES_SOLID
$ Card 1: RDLID, RDLTYPE, RDLAREA, CCPPART, CCNPART, SEPPART, PELPART, NELPART
$  RDLID   RDLTYPE   RDLAREA   CCPPART   CCNPART   SEPPART   PELPART   NELPART
       1         1         2      2001      2005      2003      2002      2004
$
$ RDLTYPE=1: 1st order Randles (R0 + R1||C1)
$ RDLAREA=2: 전체 셀 면적 대비 스케일링 (Ω)
$ CCPPART=2001: Al 집전체 Part (wound)
$ CCNPART=2005: Cu 집전체 Part (wound)
$ SEPPART=2003: PE 분리막 Part (wound)
$ PELPART=2002: NMC 양극 Part (wound)
$ NELPART=2004: Graphite 음극 Part (wound)
$
$ Card 2: Q, CQ, SOCINIT, SOCTOU
$        Q        CQ   SOCINIT    SOCTOU
       2.6    2.78E-2       0.5     -2001
$
$ Q=2.6 Ah (스마트폰 배터리 용량 2600mAh = 2.6Ah)
$ CQ=1/36 (SI 단위: SOC %/s 변환인자, Vol_III p.518)
$ SOCINIT=0.5 (50% 충전 상태)
$ SOCTOU=-2001: 로드커브 2001 (OCV vs SOC)
$
$ Card 3: R0CHA, R0DIS, R10CHA, R10DIS, C10CHA, C10DIS
$ ▶ 음수값 = TABLE ID 참조 (SOC×온도 2D 보간)
$    R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS
     -8001     -8002     -8003     -8004     -8005     -8006
$
$ R0, R1, C1: SOC×온도 의존 TABLE (08_em_randles.k에 정의)
$
$ Card 5: Thermal coupling
$     TEMP    FRTHER    R0TOTH      DUDT     TEMPU
    298.15         1         1     -2002         1
$
$ FRTHER=1: 열솔버 온도 사용
$ R0TOTH=1: R0 줄열 → 열솔버에 추가
$ DUDT=-2002: 로드커브 2002 (가역열 dU/dT vs SOC)
$ TEMPU=1: Kelvin
$
$ Card 6: SOC Shift (LSTC basic_socshift 패턴)
$  USESOCS   TAUSOCS  SICSLCID
         1    1000.0     -2004
$
$ ==================== INTERNAL SHORT CIRCUIT ====================
$
*EM_RANDLES_SHORT
$  AREATYPE   FUNCTID
         2      5001
$
$ AREATYPE=2: 전체 셀 면적 대비 스케일링
$ FUNCTID=5001: LSTC 20인수 공식 시그니처
$   양수 반환 = 단락 저항(Ω), 음수 반환 = 단락 없음
$
$ ==================== EXOTHERMIC REACTION (열폭주) ====================
$
*EM_RANDLES_EXOTHERMIC_REACTION
$  AREATYPE   FUNCTID
         2      5002
$
$ FUNCTID=5002: LSTC 10인수 공식 시그니처
$   exothermic_reaction_randle(time, temp, SOC, emdt, ocv, curr, volt, r0, vc, H_ex)
$
$ ==================== TAB ISOPOTENTIAL (동전위면) ====================
$
$ 와인딩형: 단일 Randles → 양극탭/음극탭 각 1개
$
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         1         2         1         5
$ setType=2: Part set, setId=1: Al CC (PID 2001)
$ randType=5: Randles 양극 탭
*EM_ISOPOTENTIAL
         2         2         2         1
$ randType=1: Randles 음극 탭 (PID 2005)
$
$ ==================== ISOPOTENTIAL CONNECTIONS ====================
$
$ --- 외부 부하 저항 ---
*EM_ISOPOTENTIAL_CONNECT
$   connId  connType  isoId1  isoId2     val      lcid
         1         2       1       2    0.05
$ connType=2: R=0.05Ω 외부 부하
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
         2         3       2       0     0.0
$ connType=3: 음극탭 → 접지 (기준 전위)
$
$ ==================== SET_PART for ISOPOTENTIAL ====================
$
*SET_PART_LIST
$      SID
         1
$     PID1
      2001
*SET_PART_LIST
         2
      2005
$
$ ==================== EM OUTPUT ====================
$
*EM_OUTPUT
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         4         4         4         4                                       0
$      mf2       gmv                                            randle
                                                                     0
$
$ ==================== EM DATABASE ====================
$
*EM_DATABASE_GLOBALENERGY
$       DT
     0.010
$
*EM_DATABASE_PARTDATA
$       DT
     0.010
$
*EM_DATABASE_CIRCUIT
$       DT
     0.010
$
*EM_DATABASE_ELOUT
$       DT
     0.100
$
*END
