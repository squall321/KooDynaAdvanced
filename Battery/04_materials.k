*KEYWORD
*TITLE
Li-ion Pouch Cell Materials (Structural + Thermal + EM)
$ Units: mm, ton(1e3 kg), s, N, MPa, mJ
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ STRUCTURAL MATERIALS
$ ============================================================
$
$--- MID 1: Al CC (Johnson-Cook) ---
*MAT_JOHNSON_COOK
$      MID        RO         G         E        PR       DTF        VP    RATEOP
         1 2.700E-09   26315.8   70000.0      0.33       0.0       0.0       0.0
$        A         B         N         C         M        TM        TR      EPS0
      30.0     500.0      0.22     0.014       1.0     933.0    298.15       1.0
$       CP        PC     SPALL        IT        D1        D2        D3        D4
     900.0       0.0       0.0       0.0      0.00      0.00      0.00     0.000
$       D5                EROD     EFMIN    NUMINT
       0.0                 0.0   1.0E-06         0
$
$--- MID 2: Cu CC (Johnson-Cook) ---
*MAT_JOHNSON_COOK
$      MID        RO         G         E        PR       DTF        VP    RATEOP
         2 8.960E-09   44776.1  120000.0      0.34       0.0       0.0       0.0
$        A         B         N         C         M        TM        TR      EPS0
     200.0     292.0      0.31     0.025       1.1    1356.0    298.15       1.0
$       CP        PC     SPALL        IT        D1        D2        D3        D4
     385.0       0.0       0.0       0.0      0.00      0.00      0.00     0.000
$       D5                EROD     EFMIN    NUMINT
       0.0                 0.0   1.0E-06         0
$
$--- MID 3: NMC Cathode (PLP with crush curve) ---
*MAT_PIECEWISE_LINEAR_PLASTICITY
$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL
         3 2.500E-09       800      0.30       0.0       0.0       0.3       0.0
$        C         P      LCSS      LCSR        VP
       0.0       0.0      1001         0       0.0
$     EPS1      EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$      ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$--- MID 4: Graphite Anode (PLP with crush curve) ---
*MAT_PIECEWISE_LINEAR_PLASTICITY
$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL
         4 1.800E-09       500      0.28       0.0       0.0       0.3       0.0
$        C         P      LCSS      LCSR        VP
       0.0       0.0      1002         0       0.0
$     EPS1      EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$      ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$--- MID 5: PE Separator (PLP) ---
*MAT_PIECEWISE_LINEAR_PLASTICITY
$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL
         5 9.500E-10       300      0.35      20.0      99.0       0.3       0.0
$        C         P      LCSS      LCSR        VP
     100.0       4.0         0         0       0.0
$     EPS1      EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$      ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$--- MID 6: Pouch (Al-laminate) ---
*MAT_PIECEWISE_LINEAR_PLASTICITY
$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL
         6 1.500E-09      2000      0.30      80.0     500.0       0.4       0.0
$        C         P      LCSS      LCSR        VP
    6500.0       4.0         0         0       0.0
$     EPS1      EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
$      ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
*MAT_ADD_EROSION
$      MID    EXCL    MXPRS    MNPRS    SIGP1    SIGVM    MXEPS    EPSSH
         1         0       0.0       0.0       0.0       0.0       0.4      0.0
$   MNEPS   SIGTH    IMPULSE  FATEFP
       0.0       0.0       0.0       0.0
$
*MAT_ADD_EROSION
$      MID    EXCL    MXPRS    MNPRS    SIGP1    SIGVM    MXEPS    EPSSH
         2         0       0.0       0.0       0.0       0.0       0.4      0.0
$   MNEPS   SIGTH    IMPULSE  FATEFP
       0.0       0.0       0.0       0.0
$
$--- MID 7: Impactor (Elastic Steel) ---
*MAT_ELASTIC
$      MID        RO         E        PR        DA        DB  NOT_USED
         7 7.850E-09    210000      0.30       0.0       0.0       0.0
$
$--- MID 8: Electrolyte (Elastic) ---
*MAT_ELASTIC
$      MID        RO         E        PR        DA        DB  NOT_USED
         8 1.200E-09      2000      0.45       0.0       0.0       0.0
$
*MAT_ADD_EROSION
$      MID    EXCL    MXPRS    MNPRS    SIGP1    SIGVM    MXEPS    EPSSH
         8         0       0.0       0.0       0.0       0.0       0.1      0.0
$   MNEPS   SIGTH    IMPULSE  FATEFP
       0.0       0.0       0.0       0.0
$
$
$ ============================================================
$ THERMAL MATERIALS
$ ============================================================
$
$--- TMID 101: Al CC ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       101 2.700E-09         0       0.0       0.0       0.0
$       HC        TC
     900.0   0.20500
$
$--- TMID 102: Cu CC ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       102 8.960E-09         0       0.0       0.0       0.0
$       HC        TC
     385.0   0.40000
$
$--- TMID 103: NMC Cathode (aniso) ---
*MAT_THERMAL_ORTHOTROPIC
$     TMID       TRO     TGRLC    TGMULT      AOPT      TLAT      HLAT
       103 2.500E-09         0       0.0       0.0       0.0       0.0
$       HC        K1        K2        K3
     700.0    0.0030    0.0030    0.0015
$       XP        YP        ZP        A1        A2        A3
       0.0       0.0       0.0       0.0       0.0       1.0
$       D1        D2        D3
       1.0       0.0       0.0
$
$--- TMID 104: Graphite Anode (aniso) ---
*MAT_THERMAL_ORTHOTROPIC
$     TMID       TRO     TGRLC    TGMULT      AOPT      TLAT      HLAT
       104 1.800E-09         0       0.0       0.0       0.0       0.0
$       HC        K1        K2        K3
     700.0    0.0050    0.0050    0.0020
$       XP        YP        ZP        A1        A2        A3
       0.0       0.0       0.0       0.0       0.0       1.0
$       D1        D2        D3
       1.0       0.0       0.0
$
$--- TMID 105: PE Separator ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       105 9.500E-10         0       0.0     403.0  145000.0
$       HC        TC
    1900.0   0.00033
$
$--- TMID 106: Pouch ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       106 1.500E-09         0       0.0       0.0       0.0
$       HC        TC
    1400.0   0.00020
$
$--- TMID 107: Rigid (Steel) ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       107 7.850E-09         0       0.0       0.0       0.0
$       HC        TC
     477.0   0.05190
$
$--- TMID 108: Electrolyte ---
*MAT_THERMAL_ISOTROPIC
$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT
       108 1.200E-09         0       0.0       0.0       0.0
$       HC        TC
    1600.0   0.00060
$
$
$ ============================================================
$ EM MATERIALS -> Phase 3 only, disabled in Phase 1/2
$ ============================================================
$
$ NOTE: EM_MAT_001 disabled for Phase 1 (SP solver, no EM needed)
$
$
$ ============================================================
$ SEPARATOR SHUTDOWN MODEL (GISSMO)
$ ============================================================
$
$ [DISABLED] GISSMO for MID 5 -- triple failure causes premature erosion
$
*END
