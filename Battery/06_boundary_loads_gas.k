*KEYWORD
*TITLE
Li-ion Cell - Boundary Conditions (Gas Expansion Scenario)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$ Scenario: GAS — 임팩터 없음, 스웰링/가스 전용 BC
$
$
$ ==================== SPC ====================
$
*BOUNDARY_SPC_SET
$     NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
         1         0         1         1         1         1         1         1
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
$ ==================== External Heat Flux (Gas Scenario) ====================
$
$ Total: q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011]
$ q_conv_max = 5000 W/m^2 = 5.0000E+00 mJ/(s*mm^2)
$
$ --- 1. Forced convection (time-history) ---
*BOUNDARY_HEAT_SET
$     SSID    PSEROD
         3         0
$    HLCID     HMULT     TLCID     TMULT       LOC
      9010       1.0         0       0.0         0
$
$ --- 2. Radiation correction (temperature-dependent, FUNCTID 9011) ---
$ q_rad(T) = eps*sigma_SB*(T^4 - T_amb^4)  [mJ/(s*mm^2)]
*BOUNDARY_HEAT_SET
$     SSID    PSEROD
         3         0
$    HLCID     HMULT     TLCID     TMULT       LOC
     -9011       1.0         0       0.0         0
$
*END
