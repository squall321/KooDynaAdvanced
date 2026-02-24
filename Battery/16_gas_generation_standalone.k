*KEYWORD
*TITLE
Gas Generation Standalone - Thermal-Driven Venting Module
$ Gas expansion scenario: external heat -> gas generation -> venting
$ FUNCTID 9011: radiation heat flux q_rad(T) — connected to BOUNDARY_HEAT_SET (HLCID=-9011)
$ FUNCTID 12010: Arrhenius gas rate — connected to AIRBAG (LCID=-12010 in 12_venting.k)
$ 12_venting.k: AIRBAG_SIMPLE_AIRBAG_MODEL (active)
$ 13_ale_electrolyte.k: ALE electrolyte (optional, see _ale variant)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ FUNCTID 9011: Temperature-Dependent Radiation Heat Flux
$ ============================================================
$
$ q_total = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID -9011]
$ q_rad(T) = eps * sigma_SB * (T^4 - T_amb^4)  [mJ/(s*mm^2)]
$ Connected via second BOUNDARY_HEAT_SET in 06_boundary_loads_gas.k
$
*DEFINE_FUNCTION
      9011
float heat_flux_radiation(float time, float temp)
{
    float T_amb    = 298.15;      // K — ambient reference
    float sigma_SB = 5.670e-14;   // W/(mm^2*K^4) Stefan-Boltzmann
    float eps      = 0.90;         // surface emissivity

    float T = (temp > 200.0) ? temp : T_amb;
    float q_rad = eps * sigma_SB * (T*T*T*T - T_amb*T_amb*T_amb*T_amb);
    if (q_rad < 0.0) q_rad = 0.0;
    return q_rad;  // mJ/(s*mm^2), additional radiation flux
}
$
$
$ ============================================================
$ GAS GENERATION PHYSICS SUMMARY
$ ============================================================
$
$ External heat flux: 5000 W/m^2 = 5.0000E+00 mJ/(s*mm^2)
$ Gas onset temperature: 373.0 K (99.9 C)
$ Arrhenius: A=1.00E+12 1/s, Ea=80000 J/mol (ref)
$ Gas rate: FUNCTID 12010 in 12_venting.k (2-stage SEI+electrolyte, LCID=-12010)
$ Radiation flux: FUNCTID 9011 (this file), connected via HLCID=-9011
$
$ Thermal runaway chain:
$   Forced convection (BOUNDARY_HEAT_SET, LCID 9010)
$   + Radiation correction (BOUNDARY_HEAT_SET, HLCID=-9011, FUNCTID 9011)
$   -> Temperature rise (CONTROL_THERMAL_SOLVER)
$   -> SEI decomposition (T > 353K, FUNCTID 5002 stage 1)
$   -> Anode-electrolyte reaction (T > 393K, stage 2)
$   -> Electrolyte decomposition (T > 423K, stage 3)
$   -> Gas generation (T > T_onset, FUNCTID 12010 via AIRBAG LCID=-12010)
$   -> Pouch inflation (AIRBAG_SIMPLE_AIRBAG_MODEL, 12_venting.k)
$   -> Pouch rupture (yield stress exceeded, MID=6)
$
*END
