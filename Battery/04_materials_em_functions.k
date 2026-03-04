*KEYWORD
*TITLE
Li-ion Cell - EM Conductivity Functions (Phase 3 Only)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ EM CONDUCTIVITY FUNCTIONS (C-style)
$ ============================================================
$
$ FUNCTID 6001: Al CC
*DEFINE_FUNCTION
      6001
float sigma_al(float x, float y, float z, float temp)
{
    // Al CC: sigma = sigma0 / (1 + alpha*(T-298))
    float sigma0 = 3.5000E+07;
    float alpha  = 0.0038;
    float T_ref  = 298.15;
    float ratio  = 1.0 + alpha * (temp - T_ref);
    if (ratio < 0.1) ratio = 0.1;
    return sigma0 / ratio;
}
$
$ FUNCTID 6002: Cu CC
*DEFINE_FUNCTION
      6002
float sigma_cu(float x, float y, float z, float temp)
{
    // Cu CC: sigma = sigma0 / (1 + alpha*(T-298))
    float sigma0 = 5.9600E+07;
    float alpha  = 0.0039;
    float T_ref  = 298.15;
    float ratio  = 1.0 + alpha * (temp - T_ref);
    if (ratio < 0.1) ratio = 0.1;
    return sigma0 / ratio;
}
$
$ FUNCTID 6003: NMC Cathode
*DEFINE_FUNCTION
      6003
float sigma_nmc(float x, float y, float z, float temp)
{
    // NMC Cathode: sigma = sigma0 / (1 + alpha*(T-298))
    float sigma0 = 5.0000E-01;
    float alpha  = 0.001;
    float T_ref  = 298.15;
    float ratio  = 1.0 + alpha * (temp - T_ref);
    if (ratio < 0.1) ratio = 0.1;
    return sigma0 / ratio;
}
$
$ FUNCTID 6004: Graphite Anode
*DEFINE_FUNCTION
      6004
float sigma_gr(float x, float y, float z, float temp)
{
    // Graphite Anode: sigma = sigma0 / (1 + alpha*(T-298))
    float sigma0 = 3.0000E+04;
    float alpha  = 0.0005;
    float T_ref  = 298.15;
    float ratio  = 1.0 + alpha * (temp - T_ref);
    if (ratio < 0.1) ratio = 0.1;
    return sigma0 / ratio;
}
$
$ FUNCTID 6005: Separator (insulator)
*DEFINE_FUNCTION
      6005
float sigma_sep(float x, float y, float z, float temp)
{
    // Separator (insulator): constant
    return 1.0000E-10;
}
$
$ FUNCTID 6008: Electrolyte
*DEFINE_FUNCTION
      6008
float sigma_elyte(float x, float y, float z, float temp)
{
    // Electrolyte: sigma = sigma0 / (1 + alpha*(T-298))
    float sigma0 = 1.0000E+00;
    float alpha  = 0.02;
    float T_ref  = 298.15;
    float ratio  = 1.0 + alpha * (temp - T_ref);
    if (ratio < 0.1) ratio = 0.1;
    return sigma0 / ratio;
}
$
*END
