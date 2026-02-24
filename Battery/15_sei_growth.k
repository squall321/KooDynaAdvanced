*KEYWORD
*TITLE
SEI Growth Model - Irreversible Swelling Component
$ SEI kinetics: delta(t,T) = delta_0 + A*sqrt(t)*exp(-Ea/RT)
$ A_pre=1.50E-06 m/sqrt(s), Ea=40000 J/mol, T_ref=313.15 K
$ At T_ref=313K, t=7200s: delta_SEI~5.03 nm, stack disp~0.000000 mm
$ Note: SEI displacement is already included in 14_intercalation_strain.k LCID 9001.
$ This file provides standalone SEI tracking for aging parameter studies.
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ FUNCTID 7002: SEI Growth Thickness (Arrhenius)
$ ============================================================
$
$ float sei_thickness(float time, float temp) -> SEI thickness [m]
$ Usage: EM_RANDLES_SOLID SEI tracking, aging parameter study
$ Note: for displacement, convert using stack geometry:
$   L_anode(per UC) = 0.1400 mm (both sides)
$   d_SEI(mm) = n_cells * L_an(mm) * (delta_SEI / L_an_m)
$
*DEFINE_FUNCTION
      7002
float sei_growth_thickness(float time, float temp)
{
    float A_pre    = 1.5000E-06;  // m/sqrt(s)
    float Ea       = 4.00E+04;   // J/mol
    float delta_0  = 5.0000E-09;  // m (initial SEI thickness)
    float delta_max = 5.0000E-08; // m (maximum SEI thickness)
    float R_gas    = 8.314;         // J/(mol*K)

    // Safety: use 298K if temperature not physically reasonable
    float T = (temp > 250.0) ? temp : 298.15;

    float delta = delta_0 + A_pre * sqrt(time) * exp(-Ea / (R_gas * T));
    if (delta > delta_max) delta = delta_max;
    if (delta < delta_0)   delta = delta_0;
    return delta;
}
$
$
$ ============================================================
$ LCID 9003: SEI-Only Displacement Reference (T=313K)
$ ============================================================
$
$ Pre-computed at T_ref = 313.15 K (40.0 C)
$ At t=7200s: disp = 0.000000 mm  (delta_SEI ~ 5.03 nm)
$ At t=3600s:  disp = 0.000000 mm
$ This curve is for reference/visualization only.
$ The combined intercalation+SEI curve is in 14_intercalation_strain.k.
$
*DEFINE_CURVE_TITLE
SEI Displacement vs Time (T_ref=313K)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      9003         0         1         1       0.0       0.0         0
               0               0
              60     1.23521e-08
             300     2.76201e-08
             600     3.90607e-08
            1800     6.76551e-08
            3600     9.56788e-08
            7200      1.3531e-07
$
*END
