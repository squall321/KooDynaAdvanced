*KEYWORD
*TITLE
Li-ion Cell - Temperature-Dependent Material Data
$ DEFINE_TABLE (crush), DEFINE_CURVE (GISSMO), DEFINE_FUNCTION (EM sigma)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ TEMPERATURE-DEPENDENT CRUSH (TABLE -> CURVES)
$ ============================================================
$
$ TABLE 4003: NMC crush vs Temperature
*DEFINE_TABLE
$    TBID      SPTS
      4003
$      Temperature(K)   LCID
               298.0      4031
               373.0      4032
               473.0      4033
$
*DEFINE_CURVE_TITLE
NMC Crush @ 298K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4031         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            5.00
               0.100           15.00
               0.150           35.00
               0.200           70.00
               0.250          130.00
               0.300          250.00
               0.350          500.00
               0.400         1000.00
               0.450         2000.00
               0.500         4000.00
$
*DEFINE_CURVE_TITLE
NMC Crush @ 373K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4032         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            3.50
               0.100           10.50
               0.150           24.50
               0.200           49.00
               0.250           91.00
               0.300          175.00
               0.350          350.00
               0.400          700.00
               0.450         1400.00
               0.500         2800.00
$
*DEFINE_CURVE_TITLE
NMC Crush @ 473K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4033         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            2.00
               0.100            6.00
               0.150           14.00
               0.200           28.00
               0.250           52.00
               0.300          100.00
               0.350          200.00
               0.400          400.00
               0.450          800.00
               0.500         1600.00
$
$ TABLE 4004: Graphite crush vs Temperature
*DEFINE_TABLE
$    TBID      SPTS
      4004
$      Temperature(K)   LCID
               298.0      4041
               373.0      4042
               473.0      4043
$
*DEFINE_CURVE_TITLE
Graphite Crush @ 298K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4041         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            8.00
               0.100           22.00
               0.150           50.00
               0.200          100.00
               0.250          200.00
               0.300          400.00
               0.350          800.00
               0.400         1500.00
               0.450         3000.00
               0.500         5000.00
$
*DEFINE_CURVE_TITLE
Graphite Crush @ 373K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4042         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            5.20
               0.100           14.30
               0.150           32.50
               0.200           65.00
               0.250          130.00
               0.300          260.00
               0.350          520.00
               0.400          975.00
               0.450         1950.00
               0.500         3250.00
$
*DEFINE_CURVE_TITLE
Graphite Crush @ 473K
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      4043         0       1.0       1.0       0.0       0.0         0
               0.000            0.00
               0.050            2.80
               0.100            7.70
               0.150           17.50
               0.200           35.00
               0.250           70.00
               0.300          140.00
               0.350          280.00
               0.400          525.00
               0.450         1050.00
               0.500         1750.00
$
$
$ ============================================================
$ GISSMO DAMAGE CURVE
$ ============================================================
$
*DEFINE_CURVE_TITLE
GISSMO Critical Strain vs Triaxiality
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      7001         0       1.0       1.0       0.0       0.0         0
              -0.333            1.20
               0.000            0.80
               0.333            0.55
               0.667            0.35
               1.000            0.25
$
*END
