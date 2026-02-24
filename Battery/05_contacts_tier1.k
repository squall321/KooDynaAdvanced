*KEYWORD
*TITLE
Li-ion Cell - Contacts Phase 3: Full Coupled (Stacked, 22 UC)
$
$
$ ============================================================
$ Phase 3: 전체 접촉 (TIED THERMAL, 22 UC)
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
$ 층간 TIED THERMAL 접합 (22 단위셀)
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
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       325Cu UC4 to Al UC5
      1045      1051         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 5 (PID 1051~1055) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       326Al-CC to Cathode UC5
      1051      1052         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       327Cathode to Sep UC5
      1052      1053         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       328Sep to Anode UC5
      1053      1054         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       329Anode to Cu-CC UC5
      1054      1055         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       330Cu UC5 to Al UC6
      1055      1061         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 6 (PID 1061~1065) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       331Al-CC to Cathode UC6
      1061      1062         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       332Cathode to Sep UC6
      1062      1063         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       333Sep to Anode UC6
      1063      1064         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       334Anode to Cu-CC UC6
      1064      1065         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       335Cu UC6 to Al UC7
      1065      1071         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 7 (PID 1071~1075) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       336Al-CC to Cathode UC7
      1071      1072         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       337Cathode to Sep UC7
      1072      1073         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       338Sep to Anode UC7
      1073      1074         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       339Anode to Cu-CC UC7
      1074      1075         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       340Cu UC7 to Al UC8
      1075      1081         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 8 (PID 1081~1085) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       341Al-CC to Cathode UC8
      1081      1082         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       342Cathode to Sep UC8
      1082      1083         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       343Sep to Anode UC8
      1083      1084         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       344Anode to Cu-CC UC8
      1084      1085         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       345Cu UC8 to Al UC9
      1085      1091         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 9 (PID 1091~1095) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       346Al-CC to Cathode UC9
      1091      1092         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       347Cathode to Sep UC9
      1092      1093         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       348Sep to Anode UC9
      1093      1094         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       349Anode to Cu-CC UC9
      1094      1095         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       350Cu UC9 to Al UC10
      1095      1101         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 10 (PID 1101~1105) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       351Al-CC to Cathode UC10
      1101      1102         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       352Cathode to Sep UC10
      1102      1103         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       353Sep to Anode UC10
      1103      1104         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       354Anode to Cu-CC UC10
      1104      1105         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       355Cu UC10 to Al UC11
      1105      1111         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 11 (PID 1111~1115) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       356Al-CC to Cathode UC11
      1111      1112         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       357Cathode to Sep UC11
      1112      1113         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       358Sep to Anode UC11
      1113      1114         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       359Anode to Cu-CC UC11
      1114      1115         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       360Cu UC11 to Al UC12
      1115      1121         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 12 (PID 1121~1125) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       361Al-CC to Cathode UC12
      1121      1122         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       362Cathode to Sep UC12
      1122      1123         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       363Sep to Anode UC12
      1123      1124         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       364Anode to Cu-CC UC12
      1124      1125         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       365Cu UC12 to Al UC13
      1125      1131         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 13 (PID 1131~1135) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       366Al-CC to Cathode UC13
      1131      1132         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       367Cathode to Sep UC13
      1132      1133         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       368Sep to Anode UC13
      1133      1134         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       369Anode to Cu-CC UC13
      1134      1135         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       370Cu UC13 to Al UC14
      1135      1141         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 14 (PID 1141~1145) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       371Al-CC to Cathode UC14
      1141      1142         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       372Cathode to Sep UC14
      1142      1143         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       373Sep to Anode UC14
      1143      1144         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       374Anode to Cu-CC UC14
      1144      1145         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       375Cu UC14 to Al UC15
      1145      1151         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 15 (PID 1151~1155) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       376Al-CC to Cathode UC15
      1151      1152         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       377Cathode to Sep UC15
      1152      1153         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       378Sep to Anode UC15
      1153      1154         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       379Anode to Cu-CC UC15
      1154      1155         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       380Cu UC15 to Al UC16
      1155      1161         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 16 (PID 1161~1165) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       381Al-CC to Cathode UC16
      1161      1162         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       382Cathode to Sep UC16
      1162      1163         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       383Sep to Anode UC16
      1163      1164         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       384Anode to Cu-CC UC16
      1164      1165         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       385Cu UC16 to Al UC17
      1165      1171         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 17 (PID 1171~1175) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       386Al-CC to Cathode UC17
      1171      1172         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       387Cathode to Sep UC17
      1172      1173         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       388Sep to Anode UC17
      1173      1174         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       389Anode to Cu-CC UC17
      1174      1175         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       390Cu UC17 to Al UC18
      1175      1181         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 18 (PID 1181~1185) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       391Al-CC to Cathode UC18
      1181      1182         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       392Cathode to Sep UC18
      1182      1183         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       393Sep to Anode UC18
      1183      1184         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       394Anode to Cu-CC UC18
      1184      1185         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       395Cu UC18 to Al UC19
      1185      1191         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 19 (PID 1191~1195) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       396Al-CC to Cathode UC19
      1191      1192         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       397Cathode to Sep UC19
      1192      1193         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       398Sep to Anode UC19
      1193      1194         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       399Anode to Cu-CC UC19
      1194      1195         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       400Cu UC19 to Al UC20
      1195      1201         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 20 (PID 1201~1205) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       401Al-CC to Cathode UC20
      1201      1202         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       402Cathode to Sep UC20
      1202      1203         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       403Sep to Anode UC20
      1203      1204         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       404Anode to Cu-CC UC20
      1204      1205         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       405Cu UC20 to Al UC21
      1205      1211         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      80.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Unit Cell 21 (PID 1211~1215) ---
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       406Al-CC to Cathode UC21
      1211      1212         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       407Cathode to Sep UC21
      1212      1213         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       408Sep to Anode UC21
      1213      1214         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
      50.0       0.0       0.0       0.0       0.0       0.5         0         0
*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID
       409Anode to Cu-CC UC21
      1214      1215         3         3         0         0         0         0
       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20
       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0
     100.0       0.0       0.0       0.0       0.0       0.5         0         0
$
$ --- Total TIED contacts: 109 (CID 301~409) ---
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
        10      1215         3         3         0         0         0         0
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
