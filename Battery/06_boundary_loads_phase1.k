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
*INITIAL_VELOCITY
$     NSID    NSIDEX     BOXID    IRIGID
         2         0         0         0
$       VX        VY        VZ       VRX       VRY       VRZ
   -1000.0       0.0       0.0       0.0       0.0       0.0
$
*END
