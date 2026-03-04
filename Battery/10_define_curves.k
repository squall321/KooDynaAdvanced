*KEYWORD
*TITLE
Li-ion Cell - Load Curves (Phase 3: Full Coupled)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ ELECTRODE CRUSH CURVES
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
$ IMPACTOR VELOCITY CURVE
$ ============================================================
$
*DEFINE_CURVE_TITLE
Impactor Velocity vs Time
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      3001         0         1         1       0.0       0.0         0
               0            1000
           0.005            1000
           0.006               0
            0.01               0
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
$ EXTERNAL DISCHARGE CURRENT
$ ============================================================
$
*DEFINE_CURVE_TITLE
External Discharge Current vs Time
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
      2003         0         1         1       0.0       0.0         0
               0               0
           0.001             1.3
               5             1.3
              10               0
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
    float distCC, distSEP, R_base, R_short;

    if (ero < 0.5) { return -1.0; }

    distCC = sqrt(
        pow((x_ccp - x_ccn), 2.0) +
        pow((y_ccp - y_ccn), 2.0) +
        pow((z_ccp - z_ccn), 2.0));

    distSEP = sqrt(
        pow((x_sep - x_sen), 2.0) +
        pow((y_sep - y_sen), 2.0) +
        pow((z_sep - z_sen), 2.0));

    if (distCC < 0.05) {
        R_base = 0.0001;
    } else if (distCC < 0.15) {
        R_base = 0.001;
    } else {
        R_base = 0.010;
    }

    R_short = R_base * exp(-0.002 * (temp - 298.15));
    if (R_short < 0.00001) { R_short = 0.00001; }

    if (vmstress > 50.0) {
        R_short = R_short * 50.0 / vmstress;
    }

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
    float H_max, R_gas, total_q, q1, q2, q3, q4, q5;

    H_max = 1.0e5;
    if (H_ex > H_max) { return 0.0; }

    R_gas = 8.314;
    total_q = 0.0;

    if (temp > 353.0) {
        q1 = 1.67e15 * 257000.0 * exp(-135000.0 / (R_gas * temp));
        total_q = total_q + q1;
    }

    if (temp > 393.0) {
        q2 = SOC * 2.5e13 * 155000.0 * exp(-90000.0 / (R_gas * temp));
        total_q = total_q + q2;
    }

    if (temp > 423.0) {
        q3 = 5.0e12 * 180000.0 * exp(-110000.0 / (R_gas * temp));
        total_q = total_q + q3;
    }

    if (temp > 473.0) {
        q4 = (1.0 - SOC) * 6.67e13 * 115000.0 * exp(-100000.0 / (R_gas * temp));
        total_q = total_q + q4;
    }

    if (temp > 523.0) {
        q5 = 1.0e14 * 60000.0 * exp(-150000.0 / (R_gas * temp));
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
