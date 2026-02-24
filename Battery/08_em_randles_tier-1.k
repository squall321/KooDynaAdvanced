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
$ ==================== RANDLES CIRCUITS ====================
$
$ R0/R1/C1: 음수 TABLE ID → SOC×Temperature 2D 보간
$   -8001: R0CHA, -8002: R0DIS
$   -8003: R10CHA, -8004: R10DIS
$   -8005: C10CHA, -8006: C10DIS
$ TABLE 정의 → 08_em_randles.k 에 포함
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
$
*EM_RANDLES_SHORT
$  AREATYPE   FUNCTID
         2      5001
$
$ AREATYPE=2: 전체 셀 면적 대비 스케일링
$ FUNCTID=5001: LSTC 20인수 공식 시그니처
$   양수 반환 = 단락 저항(Ω), 음수 반환 = 단락 없음
$
$ ==================== EXOTHERMIC REACTION (열폭주) ======================================
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
$ 5 unit cells → 양극/음극 각 5개 = 10 ISOs
$
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         1         2         1         5
$ UC0 Al CC (PID 1001), randType=5: Randles 양극 탭
*EM_ISOPOTENTIAL
         2         2         2         1
$ UC0 Cu CC (PID 1005), randType=1: 음극 탭
*EM_ISOPOTENTIAL
         3         2         3         5
$ UC1 Al CC (PID 1011)
*EM_ISOPOTENTIAL
         4         2         4         1
$ UC1 Cu CC (PID 1015)
*EM_ISOPOTENTIAL
         5         2         5         5
$ UC2 Al CC (PID 1021)
*EM_ISOPOTENTIAL
         6         2         6         1
$ UC2 Cu CC (PID 1025)
*EM_ISOPOTENTIAL
         7         2         7         5
$ UC3 Al CC (PID 1031)
*EM_ISOPOTENTIAL
         8         2         8         1
$ UC3 Cu CC (PID 1035)
*EM_ISOPOTENTIAL
         9         2         9         5
$ UC4 Al CC (PID 1041)
*EM_ISOPOTENTIAL
        10         2        10         1
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
$ ==================== SET_PART for ISOPOTENTIAL ====================
$
*SET_PART_LIST
$      SID
         1
$     PID1
      1001
*SET_PART_LIST
         2
      1005
*SET_PART_LIST
         3
      1011
*SET_PART_LIST
         4
      1015
*SET_PART_LIST
         5
      1021
*SET_PART_LIST
         6
      1025
*SET_PART_LIST
         7
      1031
*SET_PART_LIST
         8
      1035
*SET_PART_LIST
         9
      1041
*SET_PART_LIST
        10
      1045
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
