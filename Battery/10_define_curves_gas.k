*KEYWORD
*TITLE
Li-ion Cell - Load Curves (Gas Expansion Scenario)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ ELECTRODE CRUSH CURVES (Structural)
$ ============================================================
$
*DEFINE_CURVE_TITLE
NMC Cathode Crush Stress vs Volumetric Strain
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      1001         0         1         1       0.0       0.0         0
               0               0
            0.05               5
             0.1              15
            0.15              35
             0.2              70
            0.25             130
             0.3             250
            0.35             500
             0.4            1000
            0.45            2000
             0.5            4000
$
*DEFINE_CURVE_TITLE
Graphite Anode Crush Stress vs Volumetric Strain
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      1002         0         1         1       0.0       0.0         0
               0               0
            0.05               8
             0.1              22
            0.15              50
             0.2             100
            0.25             200
             0.3             400
            0.35             800
             0.4            1500
            0.45            3000
             0.5            5000
$
$
$ ============================================================
$ EXTERNAL HEAT FLUX CURVE (Gas Scenario)
$ ============================================================
$
*DEFINE_CURVE_TITLE
External Heat Flux vs Time (5000 W/m2 peak)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      9010         0         1         1       0.0       0.0         0
               0               0
              60               5
            3660               5
            3670               0
$
$
$ ============================================================
$ OCV vs SOC
$ ============================================================
$
*DEFINE_CURVE_TITLE
Open Circuit Voltage vs SOC
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      2001         0         1         1       0.0       0.0         0
               0               3
               5             3.3
              10            3.45
              20            3.55
              30             3.6
              40            3.64
              50            3.68
              60            3.75
              70            3.85
              80            3.95
              90            4.08
              95            4.15
             100             4.2
$
$
$ ============================================================
$ dU/dT vs SOC (Entropy Coefficient)
$ ============================================================
$
*DEFINE_CURVE_TITLE
Entropy Coefficient dU/dT vs SOC
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      2002         0         1         1       0.0       0.0         0
               0         -0.0001
              10          -5e-05
              20           5e-05
              30         0.00015
              40         0.00025
              50          0.0003
              60          0.0002
              70          0.0001
              80          -5e-05
              90        -0.00015
             100         -0.0002
$
$
$ ============================================================
$ EXTERNAL CIRCUIT (Gas Scenario: no forced discharge)
$ ============================================================
$
*DEFINE_CURVE_TITLE
Hold Discharge Current vs Time
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      2003         0         1         1       0.0       0.0         0
               0            0.26
            3600            0.26
$
$
$ ============================================================
$ SEPARATOR RESISTANCE CURVE
$ ============================================================
$
*DEFINE_CURVE_TITLE
Separator Thickness vs Short Resistance
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      5003         0         1         1       0.0       0.0         0
               0           0.001
           0.005           0.001
            0.01             0.1
           0.015              10
            0.02           1e+06
               1           1e+09
$
$
$ ============================================================
$ ISC RESISTANCE FUNCTION (FUNCTID 5001)
$ ============================================================
$
$ FUNCTID 5001: ISC resistance function
*DEFINE_FUNCTION
      5001
float resistance_short_randle(float time,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float pres, float rho, float vmstress,
                             float cond, float temp, float efstrain,
                             float ero)
{
    if (ero < 0.5) return -1.0;

    float distCC;
    distCC = sqrt(
        pow((x_ccp - x_ccn), 2.0) +
        pow((y_ccp - y_ccn), 2.0) +
        pow((z_ccp - z_ccn), 2.0));

    float distSEP;
    distSEP = sqrt(
        pow((x_sep - x_sen), 2.0) +
        pow((y_sep - y_sen), 2.0) +
        pow((z_sep - z_sen), 2.0));

    float R_base;
    if (distCC < 0.05)
        R_base = 0.0001;     // Type 4: Al-Cu
    else if (distCC < 0.15)
        R_base = 0.001;      // Type 2/3: Al-An or Ca-Cu
    else
        R_base = 0.010;      // Type 1: Ca-An

    float R_short;
    R_short = R_base * exp(-0.002 * (temp - 298.15));
    if (R_short < 0.00001) R_short = 0.00001;

    if (vmstress > 50.0)
        R_short = R_short * 50.0 / vmstress;

    return R_short;
}
$
$
$ ============================================================
$ EXOTHERMIC REACTION (FUNCTID 5002)
$ ============================================================
$
$ FUNCTID 5002: exothermic reaction (5-stage Arrhenius)
*DEFINE_FUNCTION
      5002
float exothermic_reaction_randle(float time, float temp,
                                 float SOC, float emdt,
                                 float ocv, float curr,
                                 float volt, float r0,
                                 float vc, float H_ex)
{
    float H_max = 1.0e5;
    if (H_ex > H_max) return 0.0;

    float R_gas = 8.314;
    float total_q = 0.0;

    // Stage 1: SEI decomposition (353K+)
    if (temp > 353.0)
    {
        float q1 = 1.67e15 * 257000.0 * exp(-135000.0 / (R_gas * temp));
        total_q = total_q + q1;
    }

    // Stage 2: Anode-electrolyte (393K+)
    if (temp > 393.0)
    {
        float q2 = SOC * 2.5e13 * 155000.0 * exp(-90000.0 / (R_gas * temp));
        total_q = total_q + q2;
    }

    // Stage 3: Electrolyte decomposition (423K+)
    if (temp > 423.0)
    {
        float q3 = 5.0e12 * 180000.0 * exp(-110000.0 / (R_gas * temp));
        total_q = total_q + q3;
    }

    // Stage 4: Cathode decomposition (473K+)
    if (temp > 473.0)
    {
        float q4 = (1.0 - SOC) * 6.67e13 * 115000.0 * exp(-100000.0 / (R_gas * temp));
        total_q = total_q + q4;
    }

    // Stage 5: Binder decomposition (523K+)
    if (temp > 523.0)
    {
        float q5 = 1.0e14 * 60000.0 * exp(-150000.0 / (R_gas * temp));
        total_q = total_q + q5;
    }

    return total_q;
}
$
$
$ ============================================================
$ SOC SHIFT CURVE
$ ============================================================
$
*DEFINE_CURVE_TITLE
SOC Shift vs SOC
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      2004         0         1         1       0.0       0.0         0
               0               0
              50               5
             100              10
$
*END
