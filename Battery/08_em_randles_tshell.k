*KEYWORD
*TITLE
Li-ion Cell - EM Randles TShell (복합 두꺼운 셸)
$
$ ============================================================
$ EM_RANDLES_TSHELL 접근법 — LSTC tshell_intshort 패턴
$
$ 장점:
$   - 층별 상세(CCP/양극/분리막/음극/CCN)를 단일 요소로 표현
$   - 솔리드 대비 5~20배 빠른 계산
$   - PART_COMPOSITE_TSHELL (elform=5) 사용
$   - 층간 역학적/전기화학적 상호작용 유지
$   - EM_MAT_001 randletype 필드 활용
$
$ vs EM_RANDLES_SOLID:
$   - SOLID: 5개 Part × n_uc → 많은 접촉/메쉬
$   - TSHELL: 1개 PART_COMPOSITE_TSHELL × n_uc → 적은 접촉
$
$ 단위계: mm, ton(1e3 kg), s, N, MPa, mJ
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
*EM_CONTROL_COUPLING
$    THCPL     SMCPL     THLCID    SMLCID   THCPLFL   SMCPLFL
         2         0          0         0         0         0
$
*EM_CONTROL_TIMESTEP
$   TSTYPE   DTCONST      LCID    FACTOR     TSMIN     TSMAX     RLCSF    MECATS
         5     0.001         0       1.0   1.0E-06       1.0       0.0         1
$
*EM_CONTROL_CONTACT
$     EMCT    CCONLY     CTYPE     DTYPE      EPS1      EPS2      EPS3        D0
         1         0         0         0     0.001     0.001     0.001       0.0
$
*EM_CONTROL_EROSION
         1
$
$ ==================== EM MATERIAL (TShell 전용) ====================
$
$ TShell에서 각 층의 EM 역할은 randletype 필드로 지정:
$   randletype=1: CCP (Al 집전체) — 양극 CC
$   randletype=2: Positive electrode (양극 활물질)
$   randletype=3: Separator (분리막)
$   randletype=4: Negative electrode (음극 활물질)
$   randletype=5: CCN (Cu 집전체) — 음극 CC
$
*EM_MAT_001
$      MID     MTYPE     SIGMA     EOSID                              RANDLETYPE
        11         2     3.77e4                                                1
$ MID 11: Al CC, mtype=2(도체), σ=3.77e4 S/mm, randletype=1(CCP)
*EM_MAT_001
        12         1                                                           2
$ MID 12: 양극 활물질, mtype=1(비도체), randletype=2
*EM_MAT_001
        13         1                                                           3
$ MID 13: 분리막, mtype=1(비도체), randletype=3
*EM_MAT_001
        14         1                                                           4
$ MID 14: 음극 활물질, mtype=1(비도체), randletype=4
*EM_MAT_001
        15         2     5.96e4                                                5
$ MID 15: Cu CC, mtype=2(도체), σ=5.96e4 S/mm, randletype=5(CCN)
$
$ --- 임팩터 도체 (비배터리) ---
*EM_MAT_001
         1         2     1.0e4
$ 임팩터 (강체) 전도도
*EM_MAT_001
         2         2     1.0e4
$
$ ==================== PART_COMPOSITE_TSHELL ====================
$
$ TShell: elform=5, 다층 복합 셸
$ 각 층: (MID, THICKNESS, B, ITHID) × 2 per line
$
$ 단일 단위셀 기준 층 구성 (두께는 mm):
$   MID 11(Al CC):    0.015 mm
$   MID 12(양극):     0.070 mm
$   MID 13(분리막):   0.025 mm
$   MID 14(음극):     0.080 mm
$   MID 15(Cu CC):    0.010 mm
$
$ 10회 반복 와인딩 = 50층 (Al/양극/분리막/음극/Cu × 10)
$ ITHID=1: 열 재료 ID (별도 정의 필요)
$
$ Cell 1: 5 unit cells × 5 layers = 25 layers
*PART_COMPOSITE_TSHELL
$                                                                         title
TShell Cell 1
$     PID    ELFORM      SHRF    UNUSED    UNUSED      HGID    UNUSED    TSHEAR
      4001         5     0.833                             0                   0
$    MID1    THICK1        B1    ITHID1      MID2    THICK2        B2    ITHID2
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1
$
$ Cell 2
*PART_COMPOSITE_TSHELL
TShell Cell 2
      4002         5     0.833                             0                   0
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1
$
$ Cell 3
*PART_COMPOSITE_TSHELL
TShell Cell 3
      4003         5     0.833                             0                   0
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1
$
$ Cell 4
*PART_COMPOSITE_TSHELL
TShell Cell 4
      4004         5     0.833                             0                   0
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1
$
$ Cell 5
*PART_COMPOSITE_TSHELL
TShell Cell 5
      4005         5     0.833                             0                   0
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1        12    0.0700     0.000         1
        13    0.0250     0.000         1        14    0.0800     0.000         1
        15    0.0100     0.000         1        14    0.0800     0.000         1
        13    0.0250     0.000         1        12    0.0700     0.000         1
        11    0.0150     0.000         1
$
$ ==================== SET_PART for RANDLES ====================
$
*SET_PART_LIST
         1
      4001
*SET_PART_LIST
         2
      4002
*SET_PART_LIST
         3
      4003
*SET_PART_LIST
         4
      4004
*SET_PART_LIST
         5
      4005
$
$ ==================== RANDLES CIRCUITS (TSHELL) ====================
$
$ EM_RANDLES_TSHELL:
$   Card 1: RDLID, RDLTYPE, RDLAREA, PSID
$     PSID = Part Set ID (PART_COMPOSITE_TSHELL의 PID)
$   이후 Card 동일 (Q, R0/R1/C1, Thermal, SOC Shift)
$
$ R0/R1/C1 → TABLE 참조 (08_em_randles.k의 TABLE 8001~8006 공유)
$
$ --- Cell 1 ---
*EM_RANDLES_TSHELL
$ RDLID  RDLTYPE  RDLAREA  PSID
       1         1         2         1
$      Q        CQ   SOCINIT    SOCTOU
     2.6    2.78E-2       0.5     -2001
$ R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS
  -8001     -8002     -8003     -8004     -8005     -8006
$  TEMP  FROMTHERM  R0TOTHERM      DUDT     TEMPU
298.15         1         1     -2002         1
$ USESOCS   TAUSOCS  LCIDSOCS
       1    1000.0     -2004
$
$ --- Cell 2 ---
*EM_RANDLES_TSHELL
       2         1         2         2
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 3 ---
*EM_RANDLES_TSHELL
       3         1         2         3
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 4 ---
*EM_RANDLES_TSHELL
       4         1         2         4
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 5 ---
*EM_RANDLES_TSHELL
       5         1         2         5
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ ==================== TAB ISOPOTENTIAL ====================
$
$ TShell: 각 셀의 음극탭(randType=1) + 양극탭(randType=5)
$ 탭 노드는 SET_NODE_LIST로 지정 (메쉬에서 정의)
$
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         1         2        11         1
$ Cell 1 음극탭 (Cu 표면 노드)
*EM_ISOPOTENTIAL
         2         2        12         1
*EM_ISOPOTENTIAL
         3         2        13         1
*EM_ISOPOTENTIAL
         4         2        14         1
*EM_ISOPOTENTIAL
         5         2        15         1
$
*EM_ISOPOTENTIAL
        11         2        21         5
$ Cell 1 양극탭 (Al 표면 노드)
*EM_ISOPOTENTIAL
        12         2        22         5
*EM_ISOPOTENTIAL
        13         2        23         5
*EM_ISOPOTENTIAL
        14         2        24         5
*EM_ISOPOTENTIAL
        15         2        25         5
$
$ --- 외부 단자 ---
*EM_ISOPOTENTIAL
        21         2        31
*EM_ISOPOTENTIAL
        22         2        32
$
$ ==================== SET_PART for ISOPOTENTIAL ====================
$
*SET_PART_LIST
        11
      4001
*SET_PART_LIST
        12
      4002
*SET_PART_LIST
        13
      4003
*SET_PART_LIST
        14
      4004
*SET_PART_LIST
        15
      4005
*SET_PART_LIST
        21
      4001
*SET_PART_LIST
        22
      4002
*SET_PART_LIST
        23
      4003
*SET_PART_LIST
        24
      4004
*SET_PART_LIST
        25
      4005
*SET_PART_LIST
        31
      4100
*SET_PART_LIST
        32
      4200
$
$ ==================== ISOPOTENTIAL CONNECTIONS ====================
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
$   connId  connType  isoId1  isoId2     val      lcid
         1         3      22                  0.0
$ 음극 외부 단자 → 접지
$
$ --- 외부 부하 저항 (선택적) ---
$*EM_ISOPOTENTIAL_CONNECT
$         2         2      21      22    0.05
$$ R=0.05Ω 외부 부하
$
$ ==================== SHORT CIRCUIT ====================
$
*EM_RANDLES_SHORT
$  AREATYPE   FUNCTID
         2      5001
$
$ AREATYPE=2: 전체 셀 면적 대비 스케일링
$ AREATYPE=3: TShell 전용 면적 유형 (LSTC tshell_intshort 패턴)
$ LCID=5001: 20인수 LSTC 시그니처 (10_define_curves.k)
$
$ ==================== EXOTHERMIC REACTION (열폭주) ====================
$
*EM_RANDLES_EXOTHERMIC_REACTION
$  AREATYPE   FUNCTID
         2      5002
$
$ FUNCTID=5002: LSTC 10인수 공식 시그니처
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
