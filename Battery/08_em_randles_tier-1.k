*KEYWORD
*TITLE
Li-ion Cell - EM Randles Circuit & Electrochemistry
$
$ ============================================================
$ EM + Randles 분포 회로 (EM_RANDLES_SOLID 접근법)
$
$ 전략:
$   - 각 층(CCP, 양극, 분리막, 음극, CCN) 개별 Part 구성
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
$ DIMTYPE=3: 전도 전용 (BEM 없음, SET_SEGMENT/외부 경계 불필요)
$ NCYLBEM=0: BEM 사이클 없음
$
*EM_CONTROL_COUPLING
$    THCPL     SMCPL     THLCID    SMLCID   THCPLFL   SMCPLFL
         2         0          0         0         0         0
$
$ THCPL=2: Element-level Joule heating (Randles 배터리에 권장)
$ SMCPL=0: Lorentz force OFF (배터리 셀에 불필요, BEM 세그먼트 불필요)
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
$ ==================== SOC×Temperature TABLES ====================
$
$ LSTC batmac_table 패턴: R0/R1/C1을 SOC×온도 2D TABLE로 정의
$ RANDLES 카드에서 음수 값 = TABLE ID 참조
$
$ TABLE 8001: R0 충전 → R0CHA
*DEFINE_TABLE
$     TBID
      8001
$           Temperature(K)    LCID
              273.15      8011
              298.15      8012
              323.15      8013
              373.15      8014
              473.15      8015
$
*DEFINE_CURVE
      8011
             0.0            0.06
             0.2            0.05
             0.5           0.045
             0.8            0.05
             1.0            0.06
*DEFINE_CURVE
      8012
             0.0           0.035
             0.2            0.03
             0.5           0.028
             0.8            0.03
             1.0           0.035
*DEFINE_CURVE
      8013
             0.0           0.025
             0.2            0.02
             0.5           0.018
             0.8            0.02
             1.0           0.025
*DEFINE_CURVE
      8014
             0.0           0.015
             0.2           0.012
             0.5            0.01
             0.8           0.012
             1.0           0.015
*DEFINE_CURVE
      8015
             0.0            0.01
             0.2           0.008
             0.5           0.006
             0.8           0.008
             1.0            0.01
$
$ TABLE 8002: R0 방전 → R0DIS
*DEFINE_TABLE
$     TBID
      8002
$           Temperature(K)    LCID
              273.15      8021
              298.15      8022
              323.15      8023
              373.15      8024
              473.15      8025
$
*DEFINE_CURVE
      8021
             0.0           0.065
             0.2           0.055
             0.5            0.05
             0.8           0.055
             1.0           0.065
*DEFINE_CURVE
      8022
             0.0            0.04
             0.2           0.035
             0.5           0.032
             0.8           0.035
             1.0            0.04
*DEFINE_CURVE
      8023
             0.0            0.03
             0.2           0.025
             0.5           0.022
             0.8           0.025
             1.0            0.03
*DEFINE_CURVE
      8024
             0.0           0.018
             0.2           0.015
             0.5           0.012
             0.8           0.015
             1.0           0.018
*DEFINE_CURVE
      8025
             0.0           0.012
             0.2            0.01
             0.5           0.008
             0.8            0.01
             1.0           0.012
$
$ TABLE 8003: R1 충전 → R10CHA
*DEFINE_TABLE
$     TBID
      8003
$           Temperature(K)    LCID
              273.15      8031
              298.15      8032
              323.15      8033
              373.15      8034
              473.15      8035
$
*DEFINE_CURVE
      8031
             0.0            0.04
             0.5           0.035
             1.0            0.04
*DEFINE_CURVE
      8032
             0.0           0.025
             0.5            0.02
             1.0           0.025
*DEFINE_CURVE
      8033
             0.0           0.018
             0.5           0.015
             1.0           0.018
*DEFINE_CURVE
      8034
             0.0            0.01
             0.5           0.008
             1.0            0.01
*DEFINE_CURVE
      8035
             0.0           0.006
             0.5           0.005
             1.0           0.006
$
$ TABLE 8004: R1 방전 → R10DIS
*DEFINE_TABLE
$     TBID
      8004
$           Temperature(K)    LCID
              273.15      8041
              298.15      8042
              323.15      8043
              373.15      8044
              473.15      8045
$
*DEFINE_CURVE
      8041
             0.0            0.05
             0.5            0.04
             1.0            0.05
*DEFINE_CURVE
      8042
             0.0            0.03
             0.5           0.025
             1.0            0.03
*DEFINE_CURVE
      8043
             0.0           0.022
             0.5           0.018
             1.0           0.022
*DEFINE_CURVE
      8044
             0.0           0.012
             0.5            0.01
             1.0           0.012
*DEFINE_CURVE
      8045
             0.0           0.008
             0.5           0.006
             1.0           0.008
$
$ TABLE 8005: C1 충전 → C10CHA
*DEFINE_TABLE
$     TBID
      8005
$           Temperature(K)    LCID
              273.15      8051
              298.15      8052
              323.15      8053
              373.15      8054
              473.15      8055
$
*DEFINE_CURVE
      8051
             0.0             600
             0.5             800
             1.0             600
*DEFINE_CURVE
      8052
             0.0             800
             0.5            1000
             1.0             800
*DEFINE_CURVE
      8053
             0.0            1000
             0.5            1200
             1.0            1000
*DEFINE_CURVE
      8054
             0.0            1200
             0.5            1500
             1.0            1200
*DEFINE_CURVE
      8055
             0.0            1500
             0.5            2000
             1.0            1500
$
$ TABLE 8006: C1 방전 → C10DIS
*DEFINE_TABLE
$     TBID
      8006
$           Temperature(K)    LCID
              273.15      8061
              298.15      8062
              323.15      8063
              373.15      8064
              473.15      8065
$
*DEFINE_CURVE
      8061
             0.0             600
             0.5             800
             1.0             600
*DEFINE_CURVE
      8062
             0.0             800
             0.5            1000
             1.0             800
*DEFINE_CURVE
      8063
             0.0            1000
             0.5            1200
             1.0            1000
*DEFINE_CURVE
      8064
             0.0            1200
             0.5            1500
             1.0            1200
*DEFINE_CURVE
      8065
             0.0            1500
             0.5            2000
             1.0            1500
$
$ ==================== RANDLES CIRCUITS ====================
$
$ R0/R1/C1: 음수 TABLE ID → SOC×Temperature 2D 보간
$   -8001: R0CHA, -8002: R0DIS
$   -8003: R10CHA, -8004: R10DIS
$   -8005: C10CHA, -8006: C10DIS
$
$ --- Randles for Unit Cell 0 ---
*EM_RANDLES_SOLID
$ Card 1: RDLID, RDLTYPE, RDLAREA, CCPPART, CCNPART, SEPPART, PELPART, NELPART
$  RDLID   RDLTYPE   RDLAREA   CCPPART   CCNPART   SEPPART   PELPART   NELPART
       1         1         2      1001      1005      1003      1002      1004
$
$ Card 2: Q, CQ, SOCINIT, SOCTOU
$        Q        CQ   SOCINIT    SOCTOU
       2.6    2.78E-2       0.5     -2001
$
$ Card 3: R0/R1/C1 (TABLE 참조)
$    R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS
     -8001     -8002     -8003     -8004     -8005     -8006
$
$ Card 5: Thermal coupling
$     TEMP    FRTHER    R0TOTH      DUDT     TEMPU
    298.15         1         1     -2002         1
$
$ Card 6: SOC Shift (LSTC basic_socshift 패턴)
$  USESOCS   TAUSOCS  SICSLCID
         1    1000.0     -2004
$
$ --- Randles for Unit Cell 1 ---
*EM_RANDLES_SOLID
$  RDLID   RDLTYPE   RDLAREA   CCPPART   CCNPART   SEPPART   PELPART   NELPART
       2         1         2      1011      1015      1013      1012      1014
$        Q        CQ   SOCINIT    SOCTOU
       2.6    2.78E-2       0.5     -2001
$    R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS
     -8001     -8002     -8003     -8004     -8005     -8006
$     TEMP    FRTHER    R0TOTH      DUDT     TEMPU
    298.15         1         1     -2002         1
$  USESOCS   TAUSOCS  SICSLCID
         1    1000.0     -2004
*EM_RANDLES_SOLID
       3         1         2      1021      1025      1023      1022      1024
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
       4         1         2      1031      1035      1033      1032      1034
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
       5         1         2      1041      1045      1043      1042      1044
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
$
$ --- Total Randles circuits: 5 (RDLID 1~5) ---
$
$ ==================== INTERNAL SHORT CIRCUIT ====================
$ (Step 1: ISC 비활성 — Step 2에서 활성화)
$*EM_RANDLES_SHORT
$         2      5001
$
$ ==================== EXOTHERMIC REACTION (열폭주) ====================
$ (Step 3에서 활성화)
$*EM_RANDLES_EXOTHERMIC_REACTION
$         2      5002
$
$ ==================== TAB ISOPOTENTIAL (동전위면) ====================
$
$ 5 unit cells → CCP/CCN 각 5개 = 10 ISOs
$ SETTYPE=2: Node Set (SET_NODE_GENERAL로 Part→Node 변환)
$ RDLTYPE: 1=CCP(Al CC), 5=CCN(Cu CC) — R16 Vol III p.6-105
$
*EM_ISOPOTENTIAL
$    isoId   setType     setId  rdlType
         1         2       201         1
$ UC0 Al CC (PID 1001), rdlType=1: CCP 양극 집전체
*EM_ISOPOTENTIAL
         2         2       202         5
$ UC0 Cu CC (PID 1005), rdlType=5: CCN 음극 집전체
*EM_ISOPOTENTIAL
         3         2       203         1
$ UC1 Al CC (PID 1011)
*EM_ISOPOTENTIAL
         4         2       204         5
$ UC1 Cu CC (PID 1015)
*EM_ISOPOTENTIAL
         5         2       205         1
$ UC2 Al CC (PID 1021)
*EM_ISOPOTENTIAL
         6         2       206         5
$ UC2 Cu CC (PID 1025)
*EM_ISOPOTENTIAL
         7         2       207         1
$ UC3 Al CC (PID 1031)
*EM_ISOPOTENTIAL
         8         2       208         5
$ UC3 Cu CC (PID 1035)
*EM_ISOPOTENTIAL
         9         2       209         1
$ UC4 Al CC (PID 1041)
*EM_ISOPOTENTIAL
        10         2       210         5
$ UC4 Cu CC (PID 1045)
$
$ ==================== ISOPOTENTIAL CONNECTIONS ====================
$
$ --- 외부 부하 저항 ---
*EM_ISOPOTENTIAL_CONNECT
$   connId  connType  isoId1  isoId2     val      lcid
         1         2       1       2    0.05
$ connType=2: R=0.05Ω 외부 부하 (ISO 1 양극 ↔ ISO 2 음극)
$
$ --- 직렬 연결 (UC_n 음극 → UC_{n+1} 양극) ---
*EM_ISOPOTENTIAL_CONNECT
         2         1       2       3     0.0
$ V=0: UC0 음극 → UC1 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         3         1       4       5     0.0
$ V=0: UC1 음극 → UC2 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         4         1       6       7     0.0
$ V=0: UC2 음극 → UC3 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         5         1       8       9     0.0
$ V=0: UC3 음극 → UC4 양극 (직렬)
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
         6         3      10       0     0.0
$ connType=3: 최종 음극탭 (ISO 10) → 접지 (기준 전위)
$
$ ==================== NODE SETS for ISOPOTENTIAL ====================
$ SET_NODE_GENERAL + PART: Part→Node Set 변환
$ SID 범위: 201~210 (메쉬 SET_NODE 1,2와 충돌 방지)
$
*SET_NODE_GENERAL
$      SID
       201
$   OPTION        E1
PART,      1001
*SET_NODE_GENERAL
       202
PART,      1005
*SET_NODE_GENERAL
       203
PART,      1011
*SET_NODE_GENERAL
       204
PART,      1015
*SET_NODE_GENERAL
       205
PART,      1021
*SET_NODE_GENERAL
       206
PART,      1025
*SET_NODE_GENERAL
       207
PART,      1031
*SET_NODE_GENERAL
       208
PART,      1035
*SET_NODE_GENERAL
       209
PART,      1041
*SET_NODE_GENERAL
       210
PART,      1045
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
$    OUTLV
        10
$
*EM_DATABASE_PARTDATA
$    OUTLV
        10
$
*EM_DATABASE_CIRCUIT
$    OUTLV
        10
$
*END
