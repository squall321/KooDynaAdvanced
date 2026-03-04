*KEYWORD
*TITLE
Li-ion Cell - Control Keywords (Phase 1: Mechanical Only)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$ ==================== Termination ====================
$
*CONTROL_TERMINATION
$   ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
   5.0E-03         0       0.0       0.0      0.10
$
$ ==================== Solution ====================
$
*CONTROL_SOLUTION
$     SOTEFP    SOLVE     NL_EIGP     DC_IRE
         0         0         0         0
$
$ ==================== Timestep ====================
$
*CONTROL_TIMESTEP
$   DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS     LCTM     ERODE     MS1ST
       0.0      0.90         0  1.0E-08       0.0         0         1         0
$
$ ==================== Hourglass ====================
$ Global default only — battery-specific HG via *HOURGLASS + HGID in mesh
$
*CONTROL_HOURGLASS
$      IHQ        QH
         1      0.10
$
$ ==================== Shell ====================
$
*CONTROL_SHELL
$   WRPANG     ESORT    IRNXX    ISTUPD    THEORY       BWC     MITER      PROJ
     20.0         1        -1         1         2         2         1         0
$
$ ==================== Solid ====================
$
*CONTROL_SOLID
$    ESORT    FMATRX      NIPTETS   SWLOCL    PTEFP    NIPTSO
         1         0         0         0         0         0
$
$ ==================== Contact ====================
$
*CONTROL_CONTACT
$   SLSFAC    RWPNAL    ISLCHK    SHLTHK    PENOPT    THKCHG     OTEFP    ENMASS
      0.10       0.0         2         1         1         0         1         0
$   USRSTR    USRFRC     NSBCS    INTERM     XPENE     SSTHK      ECDT   TIEDPRJ
         0         0        10         0       4.0         0         0         0
$
$ ==================== Energy ====================
$
*CONTROL_ENERGY
$     HGEN      RWEN    SLNTEN     RYLEN
         2         2         2         2
$
$ ==================== Bulk Viscosity ====================
$
*CONTROL_BULK_VISCOSITY
$       Q1        Q2      TYPE
      1.50      0.06         1
$
*END
