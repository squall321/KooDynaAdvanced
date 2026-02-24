*KEYWORD
*TITLE
Li-ion Cell - EM Randles BatMac (균질화 매크로 셀)
$
$ ============================================================
$ EM_RANDLES_BATMAC 접근법 — LSTC batmac_nail/batmac_intshort 패턴
$
$ 장점:
$   - 셀당 1개 Part → multi-cell 모듈(10~100셀) 가능
$   - 솔리드 개별 적층 대비 10~100배 빠른 계산
$   - EM_MAT_006 이방성 전도도 지원
$   - EM_MAT_005 이방성 EM 재료 (β, Cm, AOPT)
$
$ vs EM_RANDLES_SOLID:
$   - SOLID: 각 층(CCP/양극/분리막/음극/CCN) 개별 Part
$   - BATMAC: 전체 셀을 하나의 균질 Part로 표현
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
$ ==================== EM MATERIAL (BatMac 전용) ====================
$
$ --- CC 탭 재료 (mtype=4: 도체, 개별 CC 탭 Part용) ---
$ BatMac에서는 CC 탭도 별도 Part로 모델링 가능
*EM_MAT_001
$      MID     MTYPE     SIGMA     EOSID
       100         4     3.57e4
$ Al CC 탭: σ=3.57e4 S/mm (=3.57e7 S/m)
*EM_MAT_001
       200         4     5.96e4
$ Cu CC 탭: σ=5.96e4 S/mm (=5.96e7 S/m)
$
$ --- BatMac 셀 본체 → EM_MAT_001 mtype=1 (비도체) ---
$ Randles가 전기화학 처리
*EM_MAT_001
$      MID     MTYPE     SIGMA     EOSID
        10         1
$
$ --- EM_MAT_006: 양극/음극 CC별 별도 σ (BatMac 균질셀 전용) ---
$ mtype=5: BatMac 이방성 전도도
$ sigmaP = 양극 CC 방향 전도도, sigmaN = 음극 CC 방향 전도도
$
*PARAMETER
R  sigmaXX     5.0e2
R  sigmaYY     5.0e2
R  sigmaZZ     5.0e2
$ σ = 500 S/mm (균질화된 셀 이방성 전도도)
$
*EM_MAT_006
$      MID     MTYPE    SIGMAP      EOSP    SIGMAN      EOSN
         1         5  &sigmaXX            &sigmaXX
*EM_MAT_006
         2         5  &sigmaXX            &sigmaXX
*EM_MAT_006
         3         5  &sigmaXX            &sigmaXX
*EM_MAT_006
         4         5  &sigmaXX            &sigmaXX
*EM_MAT_006
         5         5  &sigmaXX            &sigmaXX
$
$ ==================== EM_MAT_005: 이방성 EM 재료 (선택적) ====================
$
$ 와인딩 방향 vs 두께 방향 이방성 전도도가 필요할 때
$ β = 전하전달계수, Cm = 이중층 커패시턴스 밀도
$ AOPT=2: 재료 좌표계 지정
$
$*EM_MAT_005
$$  INTRMID     MTYPE   SIGMAXX   SIGMAYY   SIGMAZZ      BETA        CM
$$       40         5  &sigmaXX  &sigmaYY  &sigmaZZ      0.14      0.01
$$ SIGMAXY   SIGMAXZ   SIGMAYX   SIGMAYZ   SIGMAZX   SIGMAZY
$$
$$   EXTRA             SIGMAXXB  SIGMAZZB
$$                     &sigmaXX  &sigmaZZ
$$ SIGMAXYB  SIGMAXZB  SIGMAYXB  SIGMAYZB  SIGMAZXB  SIGMAIZYB
$$
$$    AOPT        XP        YP        ZP        A1        A2        A3      MACF
$$       2.                             0         1
$$      V1        V2        V3        D1        D2        D3
$$                                                1
$
$ ==================== SET_PART (셀 Part 세트) ====================
$
$ BatMac: 각 셀이 하나의 Part → SET_PART 1:1 매핑
*SET_PART_LIST
$      SID
         1
      3001
*SET_PART_LIST
         2
      3002
*SET_PART_LIST
         3
      3003
*SET_PART_LIST
         4
      3004
*SET_PART_LIST
         5
      3005
$
$ ==================== RANDLES CIRCUITS (BATMAC) ====================
$
$ EM_RANDLES_BATMAC:
$   Card 1: RDLID, RDLTYPE, RDLAREA, CCP/PSID
$     CCP/PSID = Part Set ID (BatMac에서는 셀 Part를 직접 참조)
$   Card 2: Q, CQ, SOCINIT, SOCTOU
$   Card 3: R0/R1/C1 (TABLE 참조 또는 고정값)
$   Card 4: TEMP, FROMTHERM, R0TOTHERM, DUDT
$   Card 5: USESOCS, TAUSOCS, LCIDSOCS
$
$ R0/R1/C1 → TABLE 참조 (08_em_randles.k의 TABLE 8001~8006 공유)
$
$ --- Cell 1 ---
*EM_RANDLES_BATMAC
$ RDLID  RDLTYPE  RDLAREA  CCP/PSID
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
*EM_RANDLES_BATMAC
       2         1         2         2
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 3 ---
*EM_RANDLES_BATMAC
       3         1         2         3
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 4 ---
*EM_RANDLES_BATMAC
       4         1         2         4
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ --- Cell 5 ---
*EM_RANDLES_BATMAC
       5         1         2         5
     2.6    2.78E-2       0.5     -2001
  -8001     -8002     -8003     -8004     -8005     -8006
298.15         1         1     -2002         1
       1    1000.0     -2004
$
$ ==================== TAB ISOPOTENTIAL ====================
$
$ BatMac: 각 셀의 음극탭(randType=1) + 양극탭(randType=5)
$
*EM_ISOPOTENTIAL
$    isoId   setType     setId  randType
         1         2        11         1
$ Cell 1 음극탭
*EM_ISOPOTENTIAL
         2         2        12         1
$ Cell 2 음극탭
*EM_ISOPOTENTIAL
         3         2        13         1
$ Cell 3 음극탭
*EM_ISOPOTENTIAL
         4         2        14         1
$ Cell 4 음극탭
*EM_ISOPOTENTIAL
         5         2        15         1
$ Cell 5 음극탭
$
*EM_ISOPOTENTIAL
        11         2        21         5
$ Cell 1 양극탭
*EM_ISOPOTENTIAL
        12         2        22         5
$ Cell 2 양극탭
*EM_ISOPOTENTIAL
        13         2        23         5
$ Cell 3 양극탭
*EM_ISOPOTENTIAL
        14         2        24         5
$ Cell 4 양극탭
*EM_ISOPOTENTIAL
        15         2        25         5
$ Cell 5 양극탭
$
$ --- 외부 단자 ---
*EM_ISOPOTENTIAL
        91         2        31
$ 양극 외부 단자
*EM_ISOPOTENTIAL
        92         2        32
$ 음극 외부 단자
$
$ ==================== SET_PART for ISOPOTENTIAL ====================
$
$ 음극탭 SET (SID 11~15)
*SET_PART_LIST
        11
      3001
*SET_PART_LIST
        12
      3002
*SET_PART_LIST
        13
      3003
*SET_PART_LIST
        14
      3004
*SET_PART_LIST
        15
      3005
$ 양극탭 SET (SID 21~25)
*SET_PART_LIST
        21
      3001
*SET_PART_LIST
        22
      3002
*SET_PART_LIST
        23
      3003
*SET_PART_LIST
        24
      3004
*SET_PART_LIST
        25
      3005
$ 외부 단자 SET (SID 31~32)
$ 실제 메쉬에서 탭 Part를 생성 시 여기에 해당 PID 기입
*SET_PART_LIST
        31
      3100
*SET_PART_LIST
        32
      3200
$
$ ==================== ISOPOTENTIAL CONNECTIONS ====================
$
$ --- 직렬 연결 (음극탭 → 다음 셀 양극탭) ---
*EM_ISOPOTENTIAL_CONNECT
$   connId  connType  isoId1  isoId2     val      lcid
         1         1       1      12     0.0
$ V=0: Cell 1 음극 → Cell 2 양극 (직렬)
*EM_ISOPOTENTIAL_CONNECT
         2         1       2      13     0.0
$ V=0: Cell 2 음극 → Cell 3 양극
*EM_ISOPOTENTIAL_CONNECT
         3         1       3      14     0.0
*EM_ISOPOTENTIAL_CONNECT
         4         1       4      15     0.0
$
$ --- 외부 부하 저항 ---
*EM_ISOPOTENTIAL_CONNECT
        10         2      91      92    0.05
$ R=0.05Ω 외부 부하
$
$ --- 접지 ---
*EM_ISOPOTENTIAL_CONNECT
        11         3      92       0     0.0
$ 음극 외부 단자 → 접지
$
$ ==================== SHORT CIRCUIT ====================
$
*EM_RANDLES_SHORT
$  AREATYPE   FUNCTID
         2      5001
$
$ AREATYPE=2: 전체 셀 면적 대비 스케일링
$ FUNCTID=5001: 전 셀에 동일 단락 함수 적용
$
$ ==================== EXOTHERMIC REACTION ====================
$
*EM_RANDLES_EXOTHERMIC_REACTION
$  AREATYPE   FUNCTID
         2      5002
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
