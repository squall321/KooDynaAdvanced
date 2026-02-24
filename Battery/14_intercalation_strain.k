*KEYWORD
*TITLE
Li-ion Intercalation Strain + SEI Swelling BC
$ Swelling scenario: prescribed displacement on electrode stack top
$ n_cells=5, CTE_graphite=0.035, CTE_NMC=0.015
$ d_max(SOC=1) = 0.0343 mm, end_time = 7200 s
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ INTERCALATION + SEI DISPLACEMENT CURVE (LCID 9001)
$ ============================================================
$
$ x = time [s], y = displacement [mm] (Z-direction, stack growth)
$ Displacement = intercalation(SOC) + SEI_growth(t,T_ref=313K)
$ d_max_intercalation = 0.034250 mm at SOC=1.0
$
*DEFINE_CURVE_TITLE
Swelling Displacement vs Time (Intercalation + SEI)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      9001         0         1         1       0.0       0.0         0
               0        0.017125
            3600       0.0342501
            3780       0.0342501
            7200      0.00171264
$
$
$ ============================================================
$ BOUNDARY PRESCRIBED MOTION — STACK TOP (NSID=1002)
$ ============================================================
$
$ NSID=1002: electrode stack top-face node set
$ DOF=3: Z-direction (thickness, stack growth direction)
$ VAD=2: displacement-controlled
$ LCID=9001: swelling displacement curve (above)
$
*BOUNDARY_PRESCRIBED_MOTION_SET
$     NSID       DOF       VAD      LCID        SF       VID     DEATH     BIRTH
      1002         3         2      9001       1.0         0  1.0E+28       0.0
$
*END
