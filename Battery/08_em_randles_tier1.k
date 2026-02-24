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
$ --- Randles for Unit Cells 2~21 (동일 패턴) ---
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
*EM_RANDLES_SOLID
       6         1         2      1051      1055      1053      1052      1054
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
       7         1         2      1061      1065      1063      1062      1064
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
       8         1         2      1071      1075      1073      1072      1074
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
       9         1         2      1081      1085      1083      1082      1084
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      10         1         2      1091      1095      1093      1092      1094
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      11         1         2      1101      1105      1103      1102      1104
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      12         1         2      1111      1115      1113      1112      1114
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      13         1         2      1121      1125      1123      1122      1124
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      14         1         2      1131      1135      1133      1132      1134
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      15         1         2      1141      1145      1143      1142      1144
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      16         1         2      1151      1155      1153      1152      1154
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      17         1         2      1161      1165      1163      1162      1164
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      18         1         2      1171      1175      1173      1172      1174
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      19         1         2      1181      1185      1183      1182      1184
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      20         1         2      1191      1195      1193      1192      1194
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      21         1         2      1201      1205      1203      1202      1204
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
*EM_RANDLES_SOLID
      22         1         2      1211      1215      1213      1212      1214
       2.6    2.78E-2       0.5     -2001
     -8001     -8002     -8003     -8004     -8005     -8006
    298.15         1         1     -2002         1
         1    1000.0     -2004
$
$ --- Total Randles circuits: 22 (RDLID 1~22) ---
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
$ 22 unit cells → 양극/음극 각 22개 = 44 ISOs
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
*EM_ISOPOTENTIAL
        11         2        11         5
$ UC5 Al CC (PID 1051)
*EM_ISOPOTENTIAL
        12         2        12         1
$ UC5 Cu CC (PID 1055)
*EM_ISOPOTENTIAL
        13         2        13         5
$ UC6 Al CC (PID 1061)
*EM_ISOPOTENTIAL
        14         2        14         1
$ UC6 Cu CC (PID 1065)
*EM_ISOPOTENTIAL
        15         2        15         5
$ UC7 Al CC (PID 1071)
*EM_ISOPOTENTIAL
        16         2        16         1
$ UC7 Cu CC (PID 1075)
*EM_ISOPOTENTIAL
        17         2        17         5
$ UC8 Al CC (PID 1081)
*EM_ISOPOTENTIAL
        18         2        18         1
$ UC8 Cu CC (PID 1085)
*EM_ISOPOTENTIAL
        19         2        19         5
$ UC9 Al CC (PID 1091)
*EM_ISOPOTENTIAL
        20         2        20         1
$ UC9 Cu CC (PID 1095)
*EM_ISOPOTENTIAL
        21         2        21         5
$ UC10 Al CC (PID 1101)
*EM_ISOPOTENTIAL
        22         2        22         1
$ UC10 Cu CC (PID 1105)
*EM_ISOPOTENTIAL
        23         2        23         5
$ UC11 Al CC (PID 1111)
*EM_ISOPOTENTIAL
        24         2        24         1
$ UC11 Cu CC (PID 1115)
*EM_ISOPOTENTIAL
        25         2        25         5
$ UC12 Al CC (PID 1121)
*EM_ISOPOTENTIAL
        26         2        26         1
$ UC12 Cu CC (PID 1125)
*EM_ISOPOTENTIAL
        27         2        27         5
$ UC13 Al CC (PID 1131)
*EM_ISOPOTENTIAL
        28         2        28         1
$ UC13 Cu CC (PID 1135)
*EM_ISOPOTENTIAL
        29         2        29         5
$ UC14 Al CC (PID 1141)
*EM_ISOPOTENTIAL
        30         2        30         1
$ UC14 Cu CC (PID 1145)
*EM_ISOPOTENTIAL
        31         2        31         5
$ UC15 Al CC (PID 1151)
*EM_ISOPOTENTIAL
        32         2        32         1
$ UC15 Cu CC (PID 1155)
*EM_ISOPOTENTIAL
        33         2        33         5
$ UC16 Al CC (PID 1161)
*EM_ISOPOTENTIAL
        34         2        34         1
$ UC16 Cu CC (PID 1165)
*EM_ISOPOTENTIAL
        35         2        35         5
$ UC17 Al CC (PID 1171)
*EM_ISOPOTENTIAL
        36         2        36         1
$ UC17 Cu CC (PID 1175)
*EM_ISOPOTENTIAL
        37         2        37         5
$ UC18 Al CC (PID 1181)
*EM_ISOPOTENTIAL
        38         2        38         1
$ UC18 Cu CC (PID 1185)
*EM_ISOPOTENTIAL
        39         2        39         5
$ UC19 Al CC (PID 1191)
*EM_ISOPOTENTIAL
        40         2        40         1
$ UC19 Cu CC (PID 1195)
*EM_ISOPOTENTIAL
        41         2        41         5
$ UC20 Al CC (PID 1201)
*EM_ISOPOTENTIAL
        42         2        42         1
$ UC20 Cu CC (PID 1205)
*EM_ISOPOTENTIAL
        43         2        43         5
$ UC21 Al CC (PID 1211)
*EM_ISOPOTENTIAL
        44         2        44         1
$ UC21 Cu CC (PID 1215)
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
*EM_ISOPOTENTIAL_CONNECT
         6         1      10      11     0.0
$ V=0: UC4 음극 → UC5 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         7         1      12      13     0.0
$ V=0: UC5 음극 → UC6 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         8         1      14      15     0.0
$ V=0: UC6 음극 → UC7 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         9         1      16      17     0.0
$ V=0: UC7 음극 → UC8 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        10         1      18      19     0.0
$ V=0: UC8 음극 → UC9 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        11         1      20      21     0.0
$ V=0: UC9 음극 → UC10 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        12         1      22      23     0.0
$ V=0: UC10 음극 → UC11 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        13         1      24      25     0.0
$ V=0: UC11 음극 → UC12 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        14         1      26      27     0.0
$ V=0: UC12 음극 → UC13 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        15         1      28      29     0.0
$ V=0: UC13 음극 → UC14 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        16         1      30      31     0.0
$ V=0: UC14 음극 → UC15 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        17         1      32      33     0.0
$ V=0: UC15 음극 → UC16 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        18         1      34      35     0.0
$ V=0: UC16 음극 → UC17 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        19         1      36      37     0.0
$ V=0: UC17 음극 → UC18 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        20         1      38      39     0.0
$ V=0: UC18 음극 → UC19 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        21         1      40      41     0.0
$ V=0: UC19 음극 → UC20 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
        22         1      42      43     0.0
$ V=0: UC20 음극 → UC21 양극 (직렬)
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
        23         3      44       0     0.0
$ connType=3: 최종 음극탭 (ISO 44) → 접지 (기준 전위)
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
*SET_PART_LIST
        11
      1051
*SET_PART_LIST
        12
      1055
*SET_PART_LIST
        13
      1061
*SET_PART_LIST
        14
      1065
*SET_PART_LIST
        15
      1071
*SET_PART_LIST
        16
      1075
*SET_PART_LIST
        17
      1081
*SET_PART_LIST
        18
      1085
*SET_PART_LIST
        19
      1091
*SET_PART_LIST
        20
      1095
*SET_PART_LIST
        21
      1101
*SET_PART_LIST
        22
      1105
*SET_PART_LIST
        23
      1111
*SET_PART_LIST
        24
      1115
*SET_PART_LIST
        25
      1121
*SET_PART_LIST
        26
      1125
*SET_PART_LIST
        27
      1131
*SET_PART_LIST
        28
      1135
*SET_PART_LIST
        29
      1141
*SET_PART_LIST
        30
      1145
*SET_PART_LIST
        31
      1151
*SET_PART_LIST
        32
      1155
*SET_PART_LIST
        33
      1161
*SET_PART_LIST
        34
      1165
*SET_PART_LIST
        35
      1171
*SET_PART_LIST
        36
      1175
*SET_PART_LIST
        37
      1181
*SET_PART_LIST
        38
      1185
*SET_PART_LIST
        39
      1191
*SET_PART_LIST
        40
      1195
*SET_PART_LIST
        41
      1201
*SET_PART_LIST
        42
      1205
*SET_PART_LIST
        43
      1211
*SET_PART_LIST
        44
      1215
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
