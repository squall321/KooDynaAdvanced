*KEYWORD
*TITLE
Li-ion Cell - Boundary Conditions (Phase 1: Mechanical Only)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== SPC ====================
$
*BOUNDARY_SPC_SET
$     NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
         1         0         1         1         1         1         1         1
$
$ ==================== Impactor ====================
$
*BOUNDARY_PRESCRIBED_MOTION_SET
$     NSID       DOF       VAD      LCID        SF       VID     DEATH     BIRTH
         2         1         0      3001      -1.0         0  1.0E+28       0.0
$
*END
