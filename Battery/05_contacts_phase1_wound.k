*KEYWORD
*TITLE
Li-ion Cell - Contacts Phase 1: Mechanical Only (Wound)
$
$
$ ============================================================
$ Phase 1: 임팩터 + 자기접촉만
$ ============================================================
$
$
$ ============================================================
$ 1. 임팩터 ↔ 파우치 충돌
$ ============================================================
$
*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID
$      CID     TITLE
         1Impactor to Pouch
$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
       100       101         2         2         0         0         1         1
$       FS        FD        DC        VC       VDC    PENCHK        BT        DT
      0.30      0.20       0.0       0.0       0.0         2       0.0  1.0E+20
$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0
$
$ ============================================================
$ 2. 셀 내부 자기접촉
$ ============================================================
$
*CONTACT_AUTOMATIC_SINGLE_SURFACE_ID
$      CID     TITLE
         2Cell Internal Self-Contact
$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
       102         0         2         0         0         0         0         0
$       FS        FD        DC        VC       VDC    PENCHK        BT        DT
      0.20      0.15       0.0       0.0       0.0         2       0.0  1.0E+20
$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0
$ Optional Card A:
$     SOFT    SOFSCL    LCIDAB    MAXPAR     SBOPT     DEPTH     BSORT    FRCFRQ
         2       0.1         0     1.375         4         5         0         1
$
*END
