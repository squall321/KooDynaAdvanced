*KEYWORD
*TITLE
Li-ion Cell - Contacts Phase 3: Full Coupled (Stacked, 5 UC)
$
$
$ ============================================================
$ Phase 3: 전체 접촉 (TIED THERMAL, 5 UC)
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
$ 층간 TIED THERMAL 접합 (5 단위셀)
$ ============================================================
$
$
$ --- Unit Cell 0 (PID 1001~1005) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       301Al-CC to Cathode UC0
      1001      1002         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       302Cathode to Sep UC0
      1002      1003         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       303Sep to Anode UC0
      1003      1004         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       304Anode to Cu-CC UC0
      1004      1005         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       305Cu UC0 to Al UC1
      1005      1011         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 1 (PID 1011~1015) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       306Al-CC to Cathode UC1
      1011      1012         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       307Cathode to Sep UC1
      1012      1013         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       308Sep to Anode UC1
      1013      1014         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       309Anode to Cu-CC UC1
      1014      1015         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       310Cu UC1 to Al UC2
      1015      1021         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 2 (PID 1021~1025) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       311Al-CC to Cathode UC2
      1021      1022         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       312Cathode to Sep UC2
      1022      1023         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       313Sep to Anode UC2
      1023      1024         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       314Anode to Cu-CC UC2
      1024      1025         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       315Cu UC2 to Al UC3
      1025      1031         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 3 (PID 1031~1035) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       316Al-CC to Cathode UC3
      1031      1032         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       317Cathode to Sep UC3
      1032      1033         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       318Sep to Anode UC3
      1033      1034         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       319Anode to Cu-CC UC3
      1034      1035         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       320Cu UC3 to Al UC4
      1035      1041         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 4 (PID 1041~1045) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       321Al-CC to Cathode UC4
      1041      1042         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       322Cathode to Sep UC4
      1042      1043         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       323Sep to Anode UC4
      1043      1044         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       324Anode to Cu-CC UC4
      1044      1045         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Total TIED contacts: 24 (CID 301~324) ---
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
$ 파우치 ↔ 셀 스택 접합
$ ============================================================
$
*CONTACT_TIED_SURFACE_TO_SURFACE_ID
       501Pouch Bottom to Stack
        11      1001         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
*CONTACT_TIED_SURFACE_TO_SURFACE_ID
       502Pouch Top to Stack
        10      1045         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
$
$ ============================================================
$ PCM ↔ 탭 접합 (적층형 전용)
$ ============================================================
$
*CONTACT_TIED_NODES_TO_SURFACE_ID
       601PCM Positive to Al Tab
        30       106         3         2         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
$
*CONTACT_TIED_NODES_TO_SURFACE_ID
       602PCM Negative to Cu Tab
        31       107         3         2         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
$
*END
