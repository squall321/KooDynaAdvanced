*KEYWORD
*TITLE
Li-ion Cell - Boundary Conditions (Phase 2: Thermo-Mechanical)
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
$ ==================== Segment Set (Pouch exterior) ====================
$
*SET_SEGMENT_GENERAL
$      SID       DA1       DA2       DA3       DA4
         3       0.0       0.0       0.0       0.0
$   OPTION        E1        E2        E3
      PART        10        11        12
$
$ ==================== Convection ====================
$
*BOUNDARY_CONVECTION_SET
$     SSID    PSEROD
         3         0
$    HLCID     HMULT     TLCID     TMULT       LOC
         0   5.0E-06         0    298.15         0
$
$ ==================== Radiation ====================
$
*BOUNDARY_RADIATION_SET
$     SSID      TYPE                                    PSEROD
         3         1                                         0
$    FLCID     FMULT     TLCID     TMULT       LOC
         0 5.670E-14         0    298.15         0
$
$ ==================== Initial Temperature ====================
$
*INITIAL_TEMPERATURE_SET
$     NSID      TEMP       LOC
         0    298.15         0
$
*END
