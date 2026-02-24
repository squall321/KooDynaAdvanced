*KEYWORD
*TITLE
Li-ion Cell - Contacts Phase 2: Thermo-Mechanical (Wound)
$
$
$ ============================================================
$ Phase 2: 전체 접촉 (TIED THERMAL, 연속나선)
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
$ ============================================================
$ 층간 TIED THERMAL 접합 (와인딩 연속나선)
$ ============================================================
$
$
$ --- Wound Jellyroll (PID 2001~2005, 연속나선) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       301Al-CC to Cathode
      2001      2002         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       302Cathode to Separator
      2002      2003         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       303Separator to Anode
      2003      2004         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       304Anode to Cu-CC
      2004      2005         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Total TIED contacts: 4 (CID 301~304) ---
$
$ ============================================================
$ ERODING 접촉 (분리막 erosion 후)
$ ============================================================
$
*CONTACT_ERODING_SURFACE_TO_SURFACE_ID
$      CID     TITLE
       401Eroding - Separator Region
$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR
       103       104         2         2         0         0         1         1
$       FS        FD        DC        VC       VDC    PENCHK        BT        DT
      0.30      0.20       0.0       0.0       0.0         2       0.0  1.0E+20
$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF
      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0
$     ISYM    EROSOP      IADJ
         0         1         1
$
$ ============================================================
$ 파우치 ↔ 젤리롤 접합
$ ============================================================
$
*CONTACT_TIED_SURFACE_TO_SURFACE_ID
       501Pouch Bottom to Jelly
        11      2001         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
*CONTACT_TIED_SURFACE_TO_SURFACE_ID
       502Pouch Top to Jellyroll
        10      2005         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
$
*END
