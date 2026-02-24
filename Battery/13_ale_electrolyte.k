*KEYWORD
*TITLE
Li-ion Cell - ALE/SPH Electrolyte Model (C14)
$
$ ============================================================
$ C14: ALE/SPH 전해질 유체 거동 모델
$   - 기존 MAT_ELASTIC(MID=8) 고체 → ALE 유체로 대체
$   - 전해질 유동, 누출, 가스 혼합 시뮬레이션
$
$ 물리:
$   - EC:DMC 1:1 + LiPF6 전해질
$   - 상온 밀도 1.20 g/cm³, 점도 ~3 mPa·s
$   - 열분해 시 가스 발생 → 2상 유동
$
$ 사용:
$   1. generate_mesh_*.py에서 electrolyte ELFORM=11(ALE) 생성
$   2. Phase 3 main에서 *INCLUDE 13_ale_electrolyte.k
$   3. 04_materials.k의 MID=8을 이 파일의 ALE 재료로 교체
$
$ 단위: mm, ton(1e3 kg), s, N, MPa, mJ
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== 세그먼트 세트 정의 ====================
$
$ 전해질 인접 전극면 세그먼트 셋 (Lagrange-ALE 커플링용)
$ 전극코팅(NMC/Graphite) + 집전체(Al/Cu) 외면 → ALE 전해질과 결합
$ SET_SEGMENT_GENERAL PART 옵션: 다수 파트 외면 자동 생성
$
$ ※ 주의: 실제로는 전해질 버퍼에 접하는 면만 필요하나,
$   전체 전극 파트 외면으로 근사. 추후 BOX 옵션으로 정밀화 가능
$
*SET_SEGMENT_GENERAL
$      SID       DA1       DA2       DA3       DA4
       504       0.0       0.0       0.0       0.0
$   OPTION        E1        E2        E3        E4        E5        E6        E7
      PART        10        11        12        13
$
$ SID=504: 파우치(10,11,12) + 전해질 버퍼(13) 인접면
$ LSTRSTYP=2 (segment set) 로 CONSTRAINED_LAGRANGE_IN_SOLID에서 참조
$
$ ================================================================
$ 1. ALE 재료 정의 — 전해질 (유체)
$    MAT_NULL + EOS: Newtonian 전해질 유체
$ ================================================================
$
$ --- MID 18: 전해질 ALE 유체 ---
$ MAT_NULL: 점성 유체 (편차응력 없음, EOS로 압력 정의)
*MAT_NULL
$      MID        RO        PC        MU      TEROD    CEROD      YM        PR
        18 1.200E-06       0.0   3.0E-09       0.0       0.0       0.0     0.0
$ RO = 1.20e-6 ton/mm³ (= 1.20 g/cm³)
$ MU = 3.0e-9 MPa·s (= 3.0e-3 Pa·s = 3 mPa·s: 전해질 점도)
$
$ --- EOS 18: 선형 다항식 EOS (약압축성 유체) ---
$ P = C0 + C1*μ + C2*μ² + C3*μ³ + (C4 + C5*μ + C6*μ²)*E
$ μ = ρ/ρ₀ - 1 (체적변화율)
$ 약압축성: C0=0, C1=K (체적탄성계수), C2-C6=0
*EOS_LINEAR_POLYNOMIAL
$    EOSID        C0        C1        C2        C3        C4        C5        C6
        18       0.0    2000.0       0.0       0.0       0.0       0.0       0.0
$       E0        V0
       0.0       1.0
$ C1 = 2000 MPa (= 2 GPa, 전해질 체적탄성계수)
$ 실제 유기 용매: K ≈ 1.5~2.5 GPa
$
$ ================================================================
$ 2. ALE 가스 재료 — 분해 가스 (2상 유동 시)
$ ================================================================
$
$ --- MID 19: 분해 가스 (이상기체 근사) ---
*MAT_NULL
$      MID        RO        PC        MU      TEROD    CEROD
        19 1.0E-09       0.0   2.0E-11       0.0       0.0
$ RO = 1e-9 ton/mm³ (≈ 1 kg/m³, 기체)
$ MU = 2e-11 (기체 점도 ~20 µPa·s)
$
*EOS_LINEAR_POLYNOMIAL
$    EOSID        C0        C1        C2        C3        C4        C5        C6
        19       0.0       0.0       0.0       0.0     0.400       0.0       0.0
$       E0        V0
 2.5E-04       1.0
$ C4 = γ-1 = 0.4 (이상기체, γ=1.4)
$ E0 = P₀/(γ-1) = 0.1/0.4 = 0.25 MPa → E0 = 2.5e-4 mJ/mm³
$
$ ================================================================
$ 3. ALE 요소 정의 (ELFORM=11: 1-point ALE)
$ ================================================================
$
$ --- ALE 전해질용 SECTION_SOLID ---
$ 기존 전해질(MID=8) 파트를 이 섹션으로 대체
*SECTION_SOLID_ALE
$    SECID    ELFORM       AET
        18        11         1
$ ELFORM=11: 1-point ALE (3D solid)
$ AET=1: multi-material group
$
$ ================================================================
$ 4. ALE 다성분 그룹 정의
$    전해질 + 가스 2상 시스템
$ ================================================================
$
$ Per Vol_I p.587 (R16): ALE_MULTI-MATERIAL_GROUP
$   Card: SID, IDTYPE, GPNAME
$
*ALE_MULTI-MATERIAL_GROUP
$      SID    IDTYPE
        18         1
$ SID=18: 전해질 ALE part ID
$ IDTYPE=1: part ID type
$
$ ※ 가스 추가 시:
$*ALE_MULTI-MATERIAL_GROUP
$       19          1        0
$
$ ================================================================
$ 5. ALE 참조 시스템 — 메시 이동 제어
$    PRTYPE=1: Lagrange follower (전해질은 구조 따라감)
$    자유 표면이 필요하면 PRTYPE=4 (smoothing)
$ ================================================================
$
$ Per Vol_I p.604 (R16): ALE_REFERENCE_SYSTEM_GROUP
$   Card 1: SID, STYPE, PRTYPE, PRID, BCTRAN, BCEXP, BCROT, ICR/NID
$   Card 2: XC, YC, ZC, EXPLIM, EFAC, (blank), FRCPAD, IEXPND
$
*ALE_REFERENCE_SYSTEM_GROUP
$ Card 1:
$      SID     STYPE    PRTYPE      PRID    BCTRAN     BCEXP     BCROT  ICR/NID
        18         1         1         0         0         0         0         0
$ Card 2:
$       XC        YC        ZC    EXPLIM      EFAC              FRCPAD  IEXPND
       0.0       0.0       0.0       0.0       0.0                 0.1       0
$ SID=18: 전해질 파트 ID
$ STYPE=1: 파트 ID type
$ PRTYPE=1: Lagrange 추종 (전해질이 셀과 함께 변형)
$
$ ================================================================
$ 6. Lagrange-ALE 커플링
$    구조 솔리드 ↔ ALE 전해질 인터페이스
$ ================================================================
$
$ Per Vol_I pp.990-1003 (R16): CONSTRAINED_LAGRANGE_IN_SOLID
$   Card 1: LSTRSID, ALESID, LSTRSTYP, ALESTYP, NQUAD, CTYPE, DIREC, MCOUP
$   Card 2: START, END, PFAC, FRIC, FRCMIN, NORM, NORMTYP, DAMP
$   Card 3 (required): K, HMIN, HMAX, ILEAK, PLEAK, LCIDPOR, NVENT, IBLOCK
$
*CONSTRAINED_LAGRANGE_IN_SOLID
$ Card 1:
$ LSTRSID    ALESID  LSTRSTYP   ALESTYP     NQUAD     CTYPE     DIREC     MCOUP
       504        18         2         1         2         4         1         0
$ Card 2:
$    START       END      PFAC      FRIC    FRCMIN      NORM   NORMTYP      DAMP
       0.0   1.0E+20       0.1       0.0       0.3         0         0       0.0
$ Card 3:
$        K      HMIN      HMAX     ILEAK     PLEAK   LCIDPOR     NVENT    IBLOCK
       0.0       0.0       0.0         2       0.1         0         0         0
$ LSTRSID=504: 전해질 인접 전극면 segment set (generate_mesh_*.py에서 생성)
$ ALESID=18: ALE 전해질 part ID
$ LSTRSTYP=2: segment set, ALESTYP=1: part ID
$ CTYPE=4: penalty coupling (안정적, RIGID 호환)
$ DIREC=1: 양방향 (압축+인장)
$ FRCMIN=0.3: 누출 방지 (0.1~0.3 권장, Vol_I p.994)
$ ILEAK=2: 강한 누출 제어 + 에너지 보존 개선
$
$ ================================================================
$ 7. 초기 ALE 체적 분율
$    전해질 영역 → 100% 액상 (분해 전)
$ ================================================================
$
$ Per Vol_I section 28-136 (R16): INITIAL_VOLUME_FRACTION_GEOMETRY
$   Card 1: FMSID, FMIDTYP, BAMMG, NTRACE
$   전해질 파트 전체를 AMMG 18 (액상 전해질) 100%로 초기화
$   BAMMG=18로 배경 물질 설정 → 추가 container card 불필요
$
*INITIAL_VOLUME_FRACTION_GEOMETRY
$ Card 1: Background ALE mesh fill
$    FMSID   FMIDTYP     BAMMG    NTRACE
        18         1        18         3
$ FMSID=18: 전해질 ALE part ID
$ FMIDTYP=1: part ID type
$ BAMMG=18: 배경 AMMGID=18 (전해질 100%)
$ NTRACE=3: default sampling (7³=343 sampling points/element)
$
$ ================================================================
$ 주의 사항 및 활성화 가이드
$ ================================================================
$
$ [활성화 단계]
$  1. generate_mesh_*.py 수정:
$     - 전해질 파트 ELFORM → 11 (ALE)
$     - 전해질 SECID → 18 (SECTION_SOLID_ALE)
$     - 전해질-전극 인터페이스 세그먼트 셋 생성
$
$  2. 04_materials.k 수정:
$     - MID 8 (MAT_ELASTIC) → MID 18 (MAT_NULL + EOS)
$     - PART 카드에서 EOSID=18 지정
$
$  3. 01_main_phase3_*.k에 *INCLUDE 추가:
$     *INCLUDE
$     13_ale_electrolyte.k
$
$  4. 07_control*.k 추가:
$     *CONTROL_ALE
$     $   DCT     NADV    METH    AFAC    BFAC    CFAC    DFAC    EFAC
$          -1        1       3     0.0     0.0     0.0     0.0     0.0
$     DCT=-1: 반수송 (donor-cell + van Leer limiter)
$     NADV=1: 소재이동 1회/time-step
$     METH=3: van Leer 제한자 (2차 정확도)
$
$ [성능 고려]
$  - ALE 요소는 Lagrange 대비 2~5배 계산 비용
$  - 전해질 요소는 전체의 ~10% (영향 제한적)
$  - 2상 유동 활성 시 추가 비용 증가
$
$ [대안: SPH 접근]
$  ALE 대신 SPH 입자로 전해질 모델링 가능:
$  - *SECTION_SPH (CSLH=1.2, HMIN/HMAX=0.2/2.0)
$  - *CONTROL_SPH (NCBS=1, FORM=0)
$  - 장점: 대변형/파편화 시뮬레이션 용이
$  - 단점: 입자 해상도 의존, 텐서 불안정성
$
$ [SPH 설정 예시 — 주석 해제로 활성화]
$*SECTION_SPH
$$    SECID     CSLH     HMIN     HMAX    SPHINI     DEATH     START
$       118      1.2      0.2      2.0       0.0     1.0E28       0.0
$
$*CONTROL_SPH
$$    NCBS     BOXID      DT     IDIM     FORM    START    MAXV     HATEFP
$        1         0       0       3        0       0.0     0.0       0.0
$
$ FORM=0: Monaghan (표준)
$ IDIM=3: 3D
$
*END
