*KEYWORD
*TITLE
Li-ion Cell - Control Keywords
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$ ==================== Termination ====================
$
*CONTROL_TERMINATION
$   ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
     60.00         0       0.0       0.0      0.00
$
$ ==================== Solution ====================
$
*CONTROL_SOLUTION
$     SOTEFP    SOLVE     NL_EIGP     DC_IRE
         1         0         0         0
$
$ ==================== Timestep ====================
$
*CONTROL_TIMESTEP
$   DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS     LCTM     ERODE     MS1ST
       0.0      0.90         0       0.0 -1.00E-06         0         1         0
$
$ ==================== Hourglass ====================
$
*CONTROL_HOURGLASS
$      IHQ        QH
         5      0.05
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
$ ==================== Thermal Solver ====================
$
*CONTROL_THERMAL_SOLVER
$     APTS    SOLVER       GPT      ETEFP     FWORK
         1        12         0         0      0.90
$
*CONTROL_THERMAL_TIMESTEP
$       TS       TIP       ITS      TMIN      TMAX       DTA       LCC      LCTM
       0.0       0.5       0.0   1.0E-06      0.01       0.0         0         0
$
*CONTROL_THERMAL_NONLINEAR
$    REFMAX     TOLRF       DCP
        50   1.0E-04       0.5
$
$ ==================== Solid Refinement ====================
$
*CONTROL_REFINE_SOLID
$       ID      TYPE      NLVL      IBOX    IELOUT
       102         0         2         0         0
$   NTOTRF    NCYCRF    CRITRF     VALRF     BEGRF     ENDRF     LAYRF
      5000     0.001         3      25.0       0.0  1.0E+20         1
$    MAXRM    NCYCRM    CRITRM     VALRM     BEGRM     ENDRM
      1000     0.005         3      10.0      -0.10  1.0E+20
$
*END
