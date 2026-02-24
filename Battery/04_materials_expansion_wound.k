*KEYWORD
*TITLE
Li-ion Cell - Thermal Expansion (wound)
$ PID-based *MAT_ADD_THERMAL_EXPANSION — 15 unit cells
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ LAYERED CELL PARTS
$ ============================================================
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
      2001         0   2.3E-05
$ PID 2001: Al CC (CTE=2.3E-05 /K)
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
      2002         0   5.0E-06
$ PID 2002: NMC Cathode (CTE=5.0E-06 /K)
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
      2003         0   2.0E-04
$ PID 2003: PE Separator (CTE=2.0E-04 /K)
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
      2004         0   3.0E-06
$ PID 2004: Graphite Anode (CTE=3.0E-06 /K)
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
      2005         0   1.7E-05
$ PID 2005: Cu CC (CTE=1.7E-05 /K)
$
$
$ ============================================================
$ SPECIAL PARTS
$ ============================================================
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        10         0   2.3E-05
$ PID 10: Pouch Top
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        11         0   2.3E-05
$ PID 11: Pouch Bottom
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        12         0   2.3E-05
$ PID 12: Pouch Side/Wrap
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        13         0   1.0E-04
$ PID 13: Electrolyte
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        20         0   2.3E-05
$ PID 20: Tab Positive (Al)
$
*MAT_ADD_THERMAL_EXPANSION
$      PID      LCID      MULT
        21         0   1.7E-05
$ PID 21: Tab Negative (Cu)
$
$ PCM boards (PID 30,31) and Impactor (PID 100) are RIGID — no CTE
$
*END
