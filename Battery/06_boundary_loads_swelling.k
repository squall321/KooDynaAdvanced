*KEYWORD
*TITLE
Li-ion Cell - Boundary Conditions (Swelling Scenario)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$ Scenario: SWELLING — 임팩터 없음, 스웰링/가스 전용 BC
$
$
$ ==================== SPC ====================
$
*BOUNDARY_SPC_SET
$     NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
         1         0         1         1         1         1         1         1
$
$ ==================== Segment Set (Pouch exterior) ====================
$
*SET_SEGMENT_GENERAL
$      SID       DA1       DA2       DA3       DA4
         3       0.0       0.0       0.0       0.0
$   OPTION        E1        E2        E3
      PART        10        11        12
$
$ ==================== Convection ====================
$
*BOUNDARY_CONVECTION_SET
$     SSID    PSEROD
         3         0
$    HLCID     HMULT     TLCID     TMULT       LOC
         0   5.0E-06         0    298.15         0
$
$ ==================== Radiation ====================
$
*BOUNDARY_RADIATION_SET
$     SSID      TYPE                                    PSEROD
         3         1                                         0
$    FLCID     FMULT     TLCID     TMULT       LOC
         0 5.670E-14         0    298.15         0
$
$ ==================== Initial Temperature ====================
$
*INITIAL_TEMPERATURE_SET
$     NSID      TEMP       LOC
         0    298.15         0
$
$ ==================== Swelling Note ====================
$
$ 임팩터 BC 없음. 인터칼레이션 변형은 14_intercalation_strain.k 에서
$ BOUNDARY_PRESCRIBED_MOTION_SET (NSID=1002, DOF=3, VAD=2) 로 적용됨.
$
*END
