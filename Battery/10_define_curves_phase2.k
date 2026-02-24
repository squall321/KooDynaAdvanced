*KEYWORD
*TITLE
Li-ion Cell - Load Curves (Phase 2: Thermo-Mechanical)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ ELECTRODE CRUSH CURVES
$ ============================================================
$
*DEFINE_CURVE_TITLE
NMC Cathode Crush Stress vs Volumetric Strain
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      1001         0         1         1       0.0       0.0         0
               0               0
            0.05               5
             0.1              15
            0.15              35
             0.2              70
            0.25             130
             0.3             250
            0.35             500
             0.4            1000
            0.45            2000
             0.5            4000
$
*DEFINE_CURVE_TITLE
Graphite Anode Crush Stress vs Volumetric Strain
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      1002         0         1         1       0.0       0.0         0
               0               0
            0.05               8
             0.1              22
            0.15              50
             0.2             100
            0.25             200
             0.3             400
            0.35             800
             0.4            1500
            0.45            3000
             0.5            5000
$
$
$ ============================================================
$ IMPACTOR VELOCITY CURVE
$ ============================================================
$
*DEFINE_CURVE_TITLE
Impactor Velocity vs Time
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      3001         0         1         1       0.0       0.0         0
               0            1000
           0.005            1000
           0.006               0
            0.01               0
$
*END
