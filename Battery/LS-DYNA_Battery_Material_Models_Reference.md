# LS-DYNA Material Models for Battery Cell Modeling

## Complete Reference from Vol II – R16 (03/21/25)

---

## Table of Contents

1. [MAT_HONEYCOMB (MAT_026)](#1-mat_honeycomb-mat_026) – Jellyroll/Electrode Stack
2. [MAT_CRUSHABLE_FOAM (MAT_063)](#2-mat_crushable_foam-mat_063) – Separator/Jellyroll
3. [MAT_FU_CHANG_FOAM (MAT_083)](#3-mat_fu_chang_foam-mat_083) – Rate-Dependent Foam
4. [MAT_SIMPLIFIED_RUBBER/FOAM (MAT_181)](#4-mat_simplified_rubberfoam-mat_181) – Pouch Material
5. [MAT_LAMINATED_COMPOSITE_FABRIC (MAT_058)](#5-mat_laminated_composite_fabric-mat_058) – Electrode Layers
6. [MAT_PLASTIC_KINEMATIC (MAT_003)](#6-mat_plastic_kinematic-mat_003) – Aluminum/Copper Foils
7. [MAT_PIECEWISE_LINEAR_PLASTICITY (MAT_024)](#7-mat_piecewise_linear_plasticity-mat_024) – General Metals
8. [MAT_NULL (MAT_009)](#8-mat_null-mat_009) – ALE/SPH Electrolyte
9. [MAT_THERMAL_ISOTROPIC (and TD variants)](#9-mat_thermal_isotropic-and-variants) – Thermal Properties
10. [MAT_ADD_EROSION](#10-mat_add_erosion) – Failure Criteria

---

## 1. MAT_HONEYCOMB (MAT_026)

**Battery Application:** Jellyroll / electrode stack modeling (anisotropic compressible behavior)

### Description

Material Type 26. Major use is for honeycomb and foam materials with **real anisotropic behavior**. A nonlinear elastoplastic material behavior can be defined separately for all normal and shear stresses. These are considered to be **fully uncoupled**. Available for **solid elements** and **thick shell formulations 3, 5, and 7**.

### Card 1 — Basic Properties

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification (unique) | none |
| RO | Mass density | none |
| E | Young's modulus for **compacted** honeycomb material | none |
| PR | Poisson's ratio for **compacted** honeycomb material | none |
| SIGY | Yield stress for **fully compacted** honeycomb | none |
| VF | Relative volume at which honeycomb is fully compacted | none |
| MU | Material viscosity coefficient (default 0.05 recommended) | 0.05 |
| BULK | Bulk viscosity flag (0.0 = not used [recommended], 1.0 = active) | 0.0 |

### Card 2 — Load Curves

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| LCA | Load curve ID for σ_aa vs. relative volume or volumetric strain | none |
| LCB | Load curve ID for σ_bb (default = LCA) | LCA |
| LCC | Load curve ID for σ_cc (default = LCA) | LCA |
| LCS | Load curve ID for shear stress (default = LCA) | LCA |
| LCAB | Load curve ID for σ_ab (default = LCS) | LCS |
| LCBC | Load curve ID for σ_bc (default = LCS) | LCS |
| LCCA | Load curve ID for σ_ca (default = LCS) | LCS |
| LCSR | Load curve ID for strain-rate effects (scale factor vs. strain rate) | optional |

### Card 3 — Elastic Moduli (Uncompressed) & Material Axes

| Variable | Description |
| ---------- | ------------- |
| EAAU | Elastic modulus E_aau in uncompressed configuration |
| EBBU | Elastic modulus E_bbu in uncompressed configuration |
| ECCU | Elastic modulus E_ccu in uncompressed configuration |
| GABU | Shear modulus G_abu in uncompressed configuration |
| GBCU | Shear modulus G_bcu in uncompressed configuration |
| GCAU | Shear modulus G_cau in uncompressed configuration |
| AOPT | Material axes option (0=element nodes, 1=point, 2=vectors, 3=vector+normal, 4=cylindrical, <0=CID) |
| MACF | Material axes change flag for solids |

### Card 4 — Point/Vector Definitions

| Variable | Description |
| ---------- | ------------- |
| XP, YP, ZP | Coordinates of point P for AOPT = 1 and 4 |
| A1, A2, A3 | Components of vector **a** for AOPT = 2 |

### Card 5 — Directions & Failure

| Variable | Description |
| ---------- | ------------- |
| D1, D2, D3 | Components of vector **d** for AOPT = 2 |
| TSEF | Tensile strain at element failure (element will erode) |
| SSEF | Shear strain at element failure (element will erode) |
| V1, V2, V3 | Components of vector **v** for AOPT = 3 and 4 |

### Key Usage Notes for Battery Modeling

- **Elastic moduli vary linearly** from uncompressed values to fully compacted values at VF:
  - E_aa = E_aau + β(E − E_aau), where β = max[min((1−V)/(1−VF), 1), 0]
- **Stress components are fully uncoupled** — an a-component of strain generates resistance only in the local a-direction.
- Load curves define **magnitude of average stress** as material changes density (relative volume).
- Curves can be defined as function of **relative volume V** or **volumetric strain ε_V = 1 − V**.
- **Unloading** is based on the interpolated Young's moduli (must provide unloading tangent that exceeds loading tangent).
- **Strain-rate effects**: optional scale factor via LCSR curve.
- Set μ (MU) to small number (0.02–0.10) to prevent spurious pressures.
- For fully compacted material: elastic-perfectly plastic, von Mises yield with pressure from bulk modulus.

---

## 2. MAT_CRUSHABLE_FOAM (MAT_063)

**Battery Application:** Separator / jellyroll homogenized modeling

### Description

Material Type 63. Models crushable foam with optional damping and tension cutoff. **Unloading is fully elastic**. Tension is treated as elastic-perfectly-plastic at the tension cut-off value. A modified version (*MAT_MODIFIED_CRUSHABLE_FOAM) includes strain rate effects. Setting MODEL = 1 or 2 invokes alternative formulations with an **elliptical yield surface in p-q space**.

### Card 1 — Basic Properties

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification | none |
| RO | Mass density | none |
| E | Young's modulus. For MODEL=0, affects contact stiffness but otherwise unused; the final slope of LCID determines elastic stiffness. For MODEL=1/2, used as Young's modulus. | none |
| PR | (Elastic) Poisson's ratio | none |
| LCID | MODEL=0: Load curve ID – yield stress vs. volumetric strain γ. MODEL≥1: Load curve, table, or 3D table for uniaxial yield stress vs. equivalent plastic strain (with optional rate dependence) | none |
| TSC | Tensile stress cutoff (MODEL=0 only). Nonzero positive value strongly recommended. | 0.0 |
| DAMP | Rate sensitivity via damping coefficient (0.05–0.50 recommended, MODEL=0 only) | 0.10 |
| MODEL | 0=Original, 1=Elliptical yield surface symmetric, 2=Elliptical yield surface asymmetric | 0 |

### Card 2 — Optional (MODEL = 1 or 2)

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| PRP | Plastic Poisson's ratio (ranges -1 to 0.5) | 0.0 |
| K | Ratio of σ_c0 (initial uniaxial yield) to p_c0 (initial hydrostatic yield) | 0.0 |
| RFILTF | Rate filtering parameter (0.0 ≤ RFILTF < 1.0) | 0.0 |
| BVFLAG | Bulk viscosity deactivation (0=active, 1=no bulk viscosity) | 0.0 |
| SRCRT | Critical stretch ratio for high compression regime | 0.0 |
| ESCAL | Scale factor for high compression stiffness (multiple of E) | 0.0 |
| KT | Ratio of p_t (hydrostatic tension yield) to p_c0 (MODEL=2 only) | 0.0 |

### Key Usage Notes for Battery Modeling

- **Volumetric strain**: γ = 1 − V (relative volume ratio)
- **MODEL = 0**: Original approach — yield stress vs. volumetric strain, elastic unloading, tension cutoff
- **MODEL = 1**: Symmetric elliptical yield: F = √(q² + α²p²) − Y_s = 0, with isotropic hardening
  - k = σ_c0/p_c0 describes shape (0=von Mises to <3)
  - Separate elastic (PR) and plastic (PRP) Poisson's ratios
- **MODEL = 2**: Asymmetric elliptical yield with volumetric hardening, parameter KT shifts the ellipse
- Rate dependence available for MODEL 1/2 via table LCID (strain rate → load curve of yield stress vs. plastic strain)
- Strain rate filtering: exponential smoothing ε̇_avg = RFILTF × ε̇ᵢ₋₁_avg + (1−RFILTF) × ε̇ᵢ_cur
- In place of effective plastic strain in d3plot, **integrated volumetric strain** (ln of relative volume) is output.

---

## 3. MAT_FU_CHANG_FOAM (MAT_083)

**Battery Application:** Rate-dependent jellyroll foam behavior, separator with hysteresis

### Description

Material Type 83. Rate effects can be modeled in **low and medium density foams**. Hysteretic unloading behavior is a function of rate sensitivity. Based on unified constitutive equations for foam materials by Chang [1995]. Improvements permit: drop tower test curves to be directly input, choice of principal or volumetric strain rates, load curves in tension, and volumetric behavior via load curve.

### Options

- `DAMAGE_DECAY` — Mullin's effect with damage decay back to zero
- `LOG_LOG_INTERPOLATION` — Log-log interpolation of strain rate table
- `PATH_DEPENDENT` — Incremental update of 2nd Piola-Kirchhoff stresses

### Card 1 — Basic Properties

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification | none |
| RO | Mass density | none |
| E | Young's modulus | none |
| KCON | Optional Young's modulus for sound speed computation (affects time step, contact, hourglass, damping) | none |
| TC | Tension cut-off stress | 10²⁰ |
| FAIL | Failure option: 0=stress remains at cutoff, 1=reset to zero, 2=erode element | none |
| DAMP | Viscous coefficient (0.05–0.50 recommended) | 0.05 |
| TBID | Table ID for nominal stress vs. strain at given strain rates. Can be positive or negative. For PATH_DEPENDENT: 3D table for nominal stress as f(volumetric change, strain rate, nominal strain) | none |

### Card 2 — Flags

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| BVFLAG | Bulk viscosity: <1.0=off (recommended), ≥1.0=on | 0.0 |
| SFLAG | Strain rate flag: 0=true constant, 1=engineering | 0.0 |
| RFLAG | Strain rate evaluation: 0=first principal, 1=principal per direction, 2=volumetric | 0.0 |
| TFLAG | Tensile stress: 0=linear (follows E), 1=input via load curves (negative values) | 0.0 |
| PVID | Optional load curve ID: pressure vs. volumetric strain | 0.0 |
| SRAF | Strain rate averaging flag (see options below) | 0.0 |
| REF | Reference geometry (0=off, 1=on) | 0.0 |
| HU | Hysteretic unloading factor (0.0–1.0) | 0.0 |

### Card 3a (DAMAGE_DECAY option)

| Variable | Description |
| ---------- | ------------- |
| MINR | Minimum strain rate of interest |
| MAXR | Maximum strain rate of interest |
| SHAPE | Shape factor for unloading |
| BETAT | Decay constant for damage in tension: e^(−BETAT×t) |
| BETAC | Decay constant for damage in compression: e^(−BETAC×t) |

### Card 3b (Standard — no DAMAGE_DECAY)

| Variable | Description |
| ---------- | ------------- |
| D0, N0, N1, N2, N3 | Material constants for Fu Chang formulation |
| C0, C1, C2 | Material constants |

### Card 4 (Standard)

| Variable | Description |
| ---------- | ------------- |
| C3, C4, C5 | Material constants |
| AIJ, SIJ | Material constants |
| MINR | Minimum strain rate of interest |
| MAXR | Maximum strain rate of interest |
| SHAPE | Shape factor for unloading |

### Card 5 — Optional Unloading

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| EXPON | Exponent for unloading (active when HU≠0) | 1.0 |
| RIULD | Rate-independent unloading flag (0=off, 1=on) | 0.0 |

### Key Usage Notes for Battery Modeling

- **TBID > 0 (recommended)**: Input stress-strain curves directly from experiments at discrete strain rates. Material constants on Cards 3/4 can be left blank.
- **Bulk viscosity off** (BVFLAG < 1) is recommended to avoid unexpected volumetric response.
- **Engineering strain rate** (SFLAG=1) allows drop tower constant-velocity curves to be used directly.
- **Strain rate evaluation**: RFLAG=2 (volumetric) improves multiaxial response.
- **Hysteretic unloading** (HU between 0 and 1): HU=0 gives maximum hysteresis, HU=1 gives no dissipation.
- **SHAPE** factor: <1 reduces energy dissipation, >1 increases it.
- **Triaxial correlation**: input hydrostatic test data via PVID for improved multiaxial loading response.
- **Strain rate averaging**: multiple options to reduce noise. SRAF < 0 uses exponential moving average.

---

## 4. MAT_SIMPLIFIED_RUBBER/FOAM (MAT_181)

**Battery Application:** Pouch material, soft packing, rubber gaskets

### Description

Material Type 181. Provides a rubber and foam model specified with a **single uniaxial load curve** or a **family of uniaxial curves at discrete strain rates**. Hysteretic unloading may optionally be modeled. Specifying **Poisson's ratio > 0.0 and < 0.49 activates foam formulation**. Can be used with both **shell and solid** elements.

### Options

- `WITH_FAILURE` — strain-based failure surface for incompressible polymers
- `LOG_LOG_INTERPOLATION` — log-log strain rate interpolation

### Card 1 — Basic Properties

| Variable | Description |
| ---------- | ------------- |
| MID | Material identification |
| RO | Mass density |
| KM | Linear bulk modulus |
| MU | Damping coefficient (0.05–0.50 recommended, default 0.10) |
| G | Shear modulus for frequency-independent damping (250–1000× SIGF) |
| SIGF | Limit stress for frequency-independent frictional damping |
| REF | Reference geometry (0=off, 1=on) |
| PRTEN | Tensile Poisson's ratio for shells (optional) |

### Card 2 — Curve/Table Definition

| Variable | Description |
| ---------- | ------------- |
| SGL | Specimen gauge length |
| SW | Specimen width |
| ST | Specimen thickness |
| LC/TBID | Load curve ID or table ID: force vs. actual gauge length change. If SGL=SW=ST=1.0, curve = engineering stress vs. engineering strain. Table defines family of curves at discrete strain rates. |
| TENSION | Rate effects treatment: -1=tension+compression loading only, 0=compression only, 1=identical in both |
| RTYPE | Strain rate type: 0=true, 1=engineering |
| AVGOPT | Averaging option: <0=time window, 0=simple avg 12 steps, 1=running avg |
| PR | Poisson's ratio: ≤0.0 = incompressible rubber (Ogden), 0.0–0.49 = foam (Hill), ≥0.49 = incompressible rubber (Ogden) |

### Card 3 — Failure (WITH_FAILURE option)

| Variable | Description |
| ---------- | ------------- |
| K | Controls volume enclosed by failure surface (>0 to activate) |
| GAMA1 | Failure parameter Γ₁ |
| GAMA2 | Failure parameter Γ₂ |
| EH | Damage parameter h (small number for damage initiation range) |

**Failure criterion**: f(I₁, I₂, I₃) = (I₁−3) + Γ₁(I₁−3)² + Γ₂(I₂−3) = K

### Card 4 — Optional Parameters

| Variable | Description |
| ---------- | ------------- |
| LCUNLD | Load curve for unloading (force vs. actual length). Must cover same range as loading curve. |
| HU | Hysteretic unloading factor (0–1, default 1.0 = no dissipation) |
| SHAPE | Shape factor for unloading |
| STOL | Tolerance in stability check |
| VISCO | Viscoelastic flag: 0=elastic, 1=viscoelastic (solids only) |
| HISOUT | History output flag (1=principal strains to history vars 25-27) |

### Card 5 — Viscoelastic Constants (up to 12 cards, solids only when VISCO=1)

| Variable | Description |
| ---------- | ------------- |
| Gi | Shear relaxation modulus for ith term |
| BETAi | Decay constant for ith term |
| VFLAG | 0=standard viscoelasticity, 1=instantaneous elastic stress formulation |

### Key Usage Notes for Battery Modeling

- **For pouch material**: use shell elements with PR ≤ 0 (rubber) or PR between 0.49–0.50.
- **For foam packing**: set 0 < PR < 0.49 to activate Hill strain-energy function (foam formulation).
- **Curves should cover complete range** including both compressive (negative) and tensile (positive) regimes.
- **Hysteretic unloading**: HU < 1 provides energy dissipation. SHAPE factor tunes the hysteresis loop shape.
- **Viscoelasticity** (solids): convolution integral formulation with Prony series terms (Gi, BETAi).
- **Stability check**: use STOL to detect unstable stress-strain response; use smooth, continuously differentiable curves.

---

## 5. MAT_LAMINATED_COMPOSITE_FABRIC (MAT_058)

**Battery Application:** Electrode layers (anode/cathode), layered composite stack

### Description

Material Type 58. Depending on the failure surface type, can model **composite materials with unidirectional layers, complete laminates, and woven fabrics**. Implemented for **shell, thick shell, and solid** elements. The `SOLID` keyword option enables solid elements.

### Card Summary (7 core cards + optional rate-dependence cards)

### Card 1 — Elastic Properties

| Variable | Description |
| ---------- | ------------- |
| MID | Material identification |
| RO | Mass density |
| EA | E_a, Young's modulus – longitudinal direction. If <0: load curve or table ID for nonlinear stress-strain. |
| EB | E_b, Young's modulus – transverse direction. If <0: load curve or table ID. |
| EC | E_c, Young's modulus – normal direction (thick shells/solids). If <0: load curve or table ID (solids only). |
| PRBA | ν_ba, Poisson's ratio |
| TAU1 | τ₁, stress limit of first nonlinear shear part (for FS = -1) |
| GAMMA1 | γ₁, strain limit of first nonlinear shear part |

### Card 2 — Shear & Stress Limits

| Variable | Description |
| ---------- | ------------- |
| GAB | G_ab, shear modulus ab-direction. If <0: load curve or table ID. |
| GBC | G_bc, shear modulus cb-direction. If <0: load curve or table ID (solids only). |
| GCA | G_ca, shear modulus ca-direction. If <0: load curve or table ID (solids only). |
| SLIMT1 | Minimum stress limit factor after max stress (fiber tension) |
| SLIMC1 | Minimum stress limit factor after max stress (fiber compression) |
| SLIMT2 | Minimum stress limit factor after max stress (matrix tension) |
| SLIMC2 | Minimum stress limit factor after max stress (matrix compression) |
| SLIMS | Minimum stress limit factor after max stress (shear) |

### Card 3 — Options & Failure

| Variable | Description |
| ---------- | ------------- |
| AOPT | Material axes option (0,1,2,3,4, or <0 for CID) |
| TSIZE | Time step for automatic element deletion (activates crashfront) |
| ERODS | Maximum effective strain for element layer failure (>0: volume-preserving calc, <0: full strain tensor) |
| SOFT | Softening reduction factor for crashfront strength |
| FS | **Failure surface type**: 1=smooth quadratic (laminates/fabrics), 0=smooth b-direction/limiting a-direction (UD only), -1=faceted with independent damage evolution (laminates/fabrics) |
| EPSF | Damage initiation transverse shear strain |
| EPSR | Final rupture transverse shear strain |
| TSMD | Transverse shear maximum damage (default 0.90) |

### Card 4 — Point/Vector & Poisson's Ratios

| Variable | Description |
| ---------- | ------------- |
| XP, YP, ZP | Point P for AOPT = 1, 4 |
| A1, A2, A3 | Vector **a** for AOPT = 2 |
| PRCA | ν_ca (default = PRBA) |
| PRCB | ν_cb (default = PRBA) |

### Card 5 — Vectors & Failure Curves

| Variable | Description |
| ---------- | ------------- |
| V1, V2, V3 | Vector **v** for AOPT = 3, 4 |
| D1, D2, D3 | Vector **d** for AOPT = 2 |
| BETA | Material rotation angle about c-axis (degrees) |
| LCDFAIL | Load curve ID for orientation-dependent failure strains (5 values for shells, 9 for solids) |

### Card 6 — Strain at Strength

| Variable | Description |
| ---------- | ------------- |
| E11C | Strain at longitudinal compressive strength, a-axis (positive) |
| E11T | Strain at longitudinal tensile strength, a-axis |
| E22C | Strain at transverse compressive strength, b-axis |
| E22T | Strain at transverse tensile strength, b-axis |
| GMS | Engineering shear strain at shear strength, ab-plane |

### Card 7 — Strength Values

| Variable | Description |
| ---------- | ------------- |
| XC | Longitudinal compressive strength (positive value) |
| XT | Longitudinal tensile strength |
| YC | Transverse compressive strength, b-axis (positive value) |
| YT | Transverse tensile strength, b-axis |
| SC | Shear strength, ab-plane |

### Cards 8.1–8.3 (SOLID option only)

Additional strength/strain/limit values for c-axis and out-of-plane shear (ZC, ZT, SC23, SC31, etc.)

### Cards 9–12 (Optional strain rate dependence)

Load curve IDs defining strengths, strains, and shear parameters as functions of strain rate. Available for both shells and solids.

### Key Usage Notes for Battery Modeling

- **FS = 1** (smooth quadratic): best for complete laminates and fabrics — treats all directions similarly.
- **FS = -1** (faceted): independent damage evolution in each direction — tension/compression have different failure surfaces. Best for detailed electrode layer modeling.
- **Stress limits (SLIMxx)**: range 0.0–1.0. SLIMC = 1.0 recommended for compression (elastoplastic-like). Small SLIMT for tensile failure. Avoid dropping to zero; use 0.05–0.10.
- **ERODS** controls element layer failure at maximum effective strain.
- **Nonlinear shear** (FS = -1): define via TAU1/GAMMA1 three-point curve.
- **Rate dependence** via Cards 9–12 for dynamic battery crush simulations.
- Damage parameters written as first three additional element history variables.

---

## 6. MAT_PLASTIC_KINEMATIC (MAT_003)

**Battery Application:** Aluminum casing, copper/aluminum current collector foils

### Description

Material Type 3. Models **isotropic and kinematic hardening plasticity** with optional rate effects. Very **cost-effective**. Available for beam (Hughes-Liu and Truss), shell, and solid elements.

### Card 1 — Basic Properties

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification | none |
| RO | Mass density | none |
| E | Young's modulus | none |
| PR | Poisson's ratio | none |
| SIGY | Yield stress | none |
| ETAN | Tangent modulus (slope of bilinear stress-strain curve) | 0.0 |
| BETA | Hardening parameter, 0 < β' < 1. β'=0 → kinematic, β'=1 → isotropic | 0.0 |

### Card 2 — Rate Effects & Failure

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| SRC | Strain rate parameter C (Cowper-Symonds). If zero, no rate effects. | 0.0 |
| SRP | Strain rate parameter p (Cowper-Symonds). If zero, no rate effects. | 0.0 |
| FS | Effective plastic strain for eroding elements | 10²⁰ |
| VP | Formulation for rate effects: 0=scale yield stress, 1=viscoplastic (recommended) | 0.0 |

### Cowper-Symonds Strain Rate Model

Scales yield stress by factor: **1 + (ε̇/C)^(1/p)**

Where ε̇ is the strain rate. A fully viscoplastic formulation (VP=1) incorporates this within the yield surface.

### Hardening

- **β' = 0**: Pure kinematic hardening (Bauschinger effect)
- **β' = 1**: Pure isotropic hardening
- **0 < β' < 1**: Combined hardening

### History Variables

| # | Description |
| --- | ------------- |
| 1 | Back stress component xx |
| 2 | Back stress component yy |
| 3 | Back stress component xy |
| 4 | Back stress component yz |
| 5 | Back stress component zx |

### Key Usage Notes for Battery Modeling

- **Extremely cost-effective** — ideal for thin metallic foil components where simple plasticity suffices.
- For **isotropic hardening only** (β'=1), MAT_012 (*MAT_ISOTROPIC_ELASTIC_PLASTIC) is more efficient for solids but less accurate for shells.
- **Typical values for Al foil**: E ≈ 70 GPa, PR ≈ 0.33, SIGY ≈ 30–100 MPa
- **Typical values for Cu foil**: E ≈ 117 GPa, PR ≈ 0.34, SIGY ≈ 60–250 MPa
- **Cowper-Symonds parameters** for aluminum: C ≈ 6500/s, p ≈ 4; for copper: C ≈ 6500/s, p ≈ 4

---

## 7. MAT_PIECEWISE_LINEAR_PLASTICITY (MAT_024)

**Battery Application:** General metals — casing, tabs, busbars, structural components

### Description

Material Type 24. **Elasto-plastic material with arbitrary stress vs. strain curve** and arbitrary strain rate dependency. Failure based on plastic strain or minimum time step size.

### Options

- `LOG_INTERPOLATION` — logarithmic strain rate interpolation in table
- `STOCHASTIC` — spatially varying yield/failure
- `MIDFAIL` — failure checked only at shell mid-plane
- `2D` — actual plane stress (transverse shear not in yield condition)

### Card 1 — Basic Properties

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification | none |
| RO | Mass density | none |
| E | Young's modulus | none |
| PR | Poisson's ratio | none |
| SIGY | Yield stress (ignored if LCSS > 0, except Remark 1a) | none |
| ETAN | Tangent modulus (ignored if LCSS > 0) | 0.0 |
| FAIL | Failure flag: <0=user subroutine, 0=no failure, >0=effective plastic strain to failure | 10²¹ |
| TDEL | Minimum time step for automatic element deletion | 0.0 |

### Card 2 — Rate Effects & Curves

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| C | Strain rate parameter C (Cowper-Symonds) | 0.0 |
| P | Strain rate parameter p | 0.0 |
| LCSS | **Load curve ID or Table ID**: Load curve = effective stress vs. effective plastic strain. Table = family of curves at discrete strain rates (see *DEFINE_TABLE). | 0 |
| LCSR | Load curve ID for strain rate scaling (scale factor vs. strain rate) | 0 |
| VP | Rate formulation: -1=C-S with deviatoric rate, 0=scale yield (default), 1=viscoplastic, 3=filtered total rates | 0.0 |

### Cards 3–4 — Stress-Strain Points (if LCSS not used)

| Variable | Description |
| ---------- | ------------- |
| EPS1–EPS8 | Effective plastic strain values (first must be zero) |
| ES1–ES8 | Corresponding yield stress values |

### Three Options for Strain Rate Effects

1. **Cowper-Symonds** (C, P parameters): scales yield by 1 + (ε̇/C)^(1/p)
2. **Scale factor curve** (LCSR): direct scale factor vs. strain rate
3. **Table of curves** (LCSS as table): stress-strain curve per strain rate — most general

### Viscoplastic Formulation (VP=1)

- If SIGY > 0: σ_y = σ_y^s(ε_eff_p) + SIGY × (ε̇_eff_p/C)^(1/p)
- If SIGY = 0: σ_y = σ_y^s(ε_eff_p) × [1 + (ε̇_eff_p/C)^(1/p)]

### Filtered Strain Rates (VP=3)

ε̇ⁿ_avg = C × ε̇ⁿ⁻¹_avg + (1−C) × ε̇ⁿ

### Key Usage Notes for Battery Modeling

- **Most versatile metal model** — define arbitrary hardening curves from experimental data.
- **Table definition (LCSS)** is the most general approach for rate-dependent metals.
- For **implicit calculations** with severe hardening: set IACC=1 on *CONTROL_ACCURACY.
- Failure with implicit: damage initiates at FAIL and element erodes at FAIL + 0.01.
- **LOG_INTERPOLATION** recommended when strain rates span orders of magnitude.
- Can use *DEFINE_TABLE_XD with VP=3 for yield stress depending on up to 7 history variables.

---

## 8. MAT_NULL (MAT_009)

**Battery Application:** ALE/SPH electrolyte modeling

### Description

Material Type 9.

- For **solids and thick shells**: allows equations of state without computing deviatoric stresses. Optionally defines viscosity. Erosion in tension and compression is possible.
- For **beams and shells**: completely bypassed in element processing; only mass is computed and added to nodes. Young's modulus and Poisson's ratio set contact stiffness only.

### Card 1

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification | none |
| RO | Mass density | none |
| PC | Pressure cutoff (≤ 0.0). Must be defined for cavitation. | 0.0 |
| MU | Dynamic viscosity μ (optional) [Pa·s in SI] | 0.0 |
| TEROD | Relative volume V/V₀ for erosion in tension (>1 typically). 0=inactive. | 0.0 |
| CEROD | Relative volume V/V₀ for erosion in compression (<1 typically). 0=inactive. | 0.0 |
| YM | Young's modulus (null beams/shells only) | 0.0 |
| PR | Poisson's ratio (null beams/shells only) | 0.0 |

### Deviatoric Viscous Stress

σ'_ij = 2μ ε̇'_ij

Where ε̇'_ij is the deviatoric strain rate and μ is dynamic viscosity.

### Key Usage Notes for Battery Modeling

- **Must be used with an equation of state** (e.g., *EOS_LINEAR_POLYNOMIAL, *EOS_GRUNEISEN) for solids/thick shells.
- **No yield strength** — behaves in a fluid-like manner. Ideal for electrolyte.
- **Pressure cutoff (PC)**: define as small negative number to allow "numerical cavitation" when material undergoes excessive dilatation.
- **Hourglass control**: null materials have no shear stiffness. Set QM small (10⁻⁶ to 10⁻⁴), IHQ = 1.
- **For ALE electrolyte**: pair with *EOS_LINEAR_POLYNOMIAL for liquid behavior.
- **For SPH electrolyte**: can also use *MAT_SPH_INCOMPRESSIBLE_FLUID as alternative.

---

## 9. MAT_THERMAL_ISOTROPIC (and Variants)

**Battery Application:** Thermal properties for coupled structural/thermal analysis, thermal runaway

### 9a. MAT_THERMAL_ISOTROPIC (MAT_T01)

Thermal Material Type 1. Defines **constant isotropic thermal properties**.

| Variable | Description |
| ---------- | ------------- |
| TMID | Thermal material identification (independent of structural MID, linked via *PART) |
| TRO | Thermal density (0.0 = default to structural density) |
| TGRLC | Thermal generation rate: >0 = load curve ID (rate vs. time), 0 = constant TGMULT, <0 = |TGRLC| is curve ID (rate vs. temperature). Units: W/m³ in SI. |
| TGMULT | Thermal generation rate multiplier (0.0 = no heat generation) |
| TLAT | Phase change temperature |
| HLAT | Latent heat |
| HC | Specific heat |
| TC | Thermal conductivity |

### 9b. MAT_THERMAL_ISOTROPIC_TD (MAT_T03)

Thermal Material Type 3. **Temperature-dependent** isotropic properties (2–8 data points).

| Variable | Description |
| ---------- | ------------- |
| TMID | Thermal material identification |
| TRO | Thermal density |
| TGRLC | Thermal generation rate (same options as T01) |
| TGMULT | Thermal generation rate multiplier |
| TLAT | Phase change temperature |
| HLAT | Latent heat |
| T1–T8 | Temperature points (2–8 required) |
| C1–C8 | Specific heat at T1–T8 |
| K1–K8 | Thermal conductivity at T1–T8 |

### 9c. MAT_THERMAL_ISOTROPIC_PHASE_CHANGE (MAT_T09)

Thermal Material Type 9. **Temperature-dependent isotropic properties with phase change** (e.g., electrolyte vaporization, thermal runaway).

| Variable | Description |
| ---------- | ------------- |
| TMID | Thermal material identification |
| TRO | Thermal density |
| TGRLC, TGMULT | Thermal generation rate options |
| T1–T8 | Temperature points |
| C1–C8 | Specific heat at temperatures |
| K1–K8 | Thermal conductivity at temperatures |
| SOLT | Solid temperature T_S (must be < T_L) |
| LIQT | Liquid temperature T_L (must be > T_S) |
| LH | Latent heat |

**Phase change enhanced specific heat:**
c(T) = m[1 − cos 2π((T−T_S)/(T_L−T_S))], for T_S < T < T_L

Where m is chosen so that ∫c(T)dT from T_S to T_L = latent heat λ.

### 9d. MAT_THERMAL_ISOTROPIC_TD_LC (MAT_T10)

Thermal Material Type 10. **Temperature (and/or history variable and/or external variable) dependent** isotropic properties defined via **load curves**. Most flexible variant.

| Variable | Description |
| ---------- | ------------- |
| TMID | Thermal material identification |
| TRO | Thermal density |
| TGRLC | Thermal generation rate (supports functions of history variables via TGHSV) |
| TGMULT | Thermal generation rate multiplier |
| TLAT | Phase change temperature |
| HLAT | Latent heat |
| HCLC | Load curve ID: specific heat vs. temperature (or history variable) |
| TCLC | Load curve ID: thermal conductivity vs. temperature (or history variable) |
| HCHSV | History variable number for specific heat dependence |
| TCHSV | History variable number for conductivity dependence |
| TGHSV | History variable number for heat generation dependence |

### Key Usage Notes for Battery Modeling

- **TMID** is independent of structural MID — linked through *PART card.
- **Thermal generation rate (TGRLC/TGMULT)**: use for Joule heating, exothermic reaction heat generation. Units W/m³ in SI.
- **MAT_T03 (TD)** recommended for most battery components — properties vary with temperature (specific heat, conductivity).
- **MAT_T09 (Phase Change)** essential for thermal runaway modeling — captures latent heat of electrolyte vaporization or material phase transitions.
- **MAT_T10 (TD_LC)** most flexible — can couple thermal properties to **mechanical history variables** (e.g., damage state, state of charge via *LOAD_EXTERNAL_VARIABLE).
- Also consider **MAT_THERMAL_ORTHOTROPIC_TD** for components with directional thermal conductivity (e.g., jellyroll with different in-plane vs. through-thickness conductivity).

---

## 10. MAT_ADD_EROSION

**Battery Application:** Failure criteria for any material model (short circuit detection, cell rupture)

### Description

Provides a way of **including failure in material models that do not natively support it**. Can also be applied to models that already have failure criteria. LS-DYNA applies each failure criterion **independently**. Upon satisfaction of a sufficient number (NCS) of specified criteria, the element is deleted.

Applies to: 2D continuum, beam (formulations 1, 11), 3D shell (including isogeometric), 3D thick shell, 3D solid (including isogeometric), and SPH elements.

### Card 1 — Primary Failure Criteria

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MID | Material identification to apply erosion | none |
| EXCL | Exclusion number (0.0 recommended). Criteria set to this value are not invoked. | 0.0 |
| MXPRES | Maximum pressure at failure, P_max | 0.0 (excluded) |
| MNEPS | Minimum principal strain at failure, ε_min | 0.0 (excluded) |
| EFFEPS | Max effective strain at failure. If negative, |EFFEPS| is effective plastic strain at failure. | 0.0 (excluded) |
| VOLEPS | Volumetric strain at failure (positive=tension, negative=compression) | 0.0 (excluded) |
| NUMFIP | Number/percentage of failed integration points before element deletion (default 1) | 1.0 |
| NCS | Number of failure conditions to satisfy simultaneously before failure (default 1) | 1.0 |

### Card 2 — Additional Failure Criteria

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| MNPRES | Minimum pressure at failure, P_min | none |
| SIGP1 | Maximum principal stress at failure, σ_max. If <0: load curve ID (σ_max vs. ε̇_eff). | none |
| SIGVM | Equivalent stress at failure. If <0: load curve ID (σ̄_max vs. ε̇_eff). | none |
| MXEPS | Maximum principal strain at failure, ε_max. If <0: load curve ID. | none |
| EPSSH | Tensorial shear strain at failure, γ_max/2 | none |
| SIGTH | Threshold stress σ₀ (for Tuler-Butcher criterion) | none |
| IMPULSE | Stress impulse for failure K_f (Tuler-Butcher) | none |
| FAILTM | Failure time. >0: active always. <0: inactive during dynamic relaxation. | none |

### Card 3 — Damage Model

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| IDAM | Damage model flag (0=none, nonzero=GISSMO/DIEM for backward compat.) | 0 |
| LCREGD | Load curve ID for element-size-dependent regularization factors | 0.0 |

### Card 4 — Additional Criteria

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| LCFLD | Forming Limit Diagram (load curve or table: minor vs. major engineering strains in %). Shell elements only. | 0.0 |
| NSFF | Number of time steps for stress fade-out (LCFLD criterion). Default 10. | 0.0 |
| EPSTHIN | Thinning strain at failure for shells. >0: individual per IP, <0: averaged from thickness change. | 0.0 |
| ENGCRT | Critical energy for nonlocal failure criterion | 0.0 |
| RADCRT | Critical radius for nonlocal failure criterion | 0.0 |
| LCEPS12 | Load curve: in-plane shear strain limit vs. element size | 0 |
| LCEPS13 | Load curve: through-thickness shear strain limit vs. element size | 0 |
| LCEPSMX | Load curve: in-plane major strain limit vs. element size | 0 |

### Card 5 — Additional Options

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| DTEFLT | Time period for low-pass filter on effective strain rate (when SIGP1/SIGVM/MXEPS < 0) | — |
| VOLFRAC | Volume fraction required to fail before element deleted (for higher-order solids). Default 0.5. | 0.5 |
| MXTMP | Maximum temperature at failure | none |
| DTMIN | Minimum time step size at failure | none |

### Supported Failure Criteria Summary

| Criterion | Condition | Parameter |
| ----------- | ----------- | ----------- |
| Max pressure | P ≥ P_max | MXPRES |
| Min principal strain | ε₃ ≤ ε_min | MNEPS |
| Max effective strain | ε_eff ≥ EFFEPS | EFFEPS |
| Volumetric strain | ε_vol ≥ VOLEPS | VOLEPS |
| Min pressure | P ≤ P_min | MNPRES |
| Max principal stress | σ₁ ≥ σ_max | SIGP1 |
| Equivalent stress | σ̄ ≥ σ̄_max | SIGVM |
| Max principal strain | ε₁ ≥ ε_max | MXEPS |
| Max shear strain | γ₁ ≥ γ_max/2 | EPSSH |
| Tuler-Butcher impulse | ∫[max(0,σ₁−σ₀)]² dt ≥ K_f | SIGTH, IMPULSE |
| Forming Limit Diagram | Major/minor strains exceed FLD | LCFLD |
| Thinning strain | Thickness strain exceeds limit | EPSTHIN |
| Max temperature | T ≥ T_max | MXTMP |
| Min time step | Δt ≤ Δt_min | DTMIN |
| Failure time | t ≥ t_fail | FAILTM |

### Key Usage Notes for Battery Modeling

- **Short circuit detection**: use VOLEPS or EPSTHIN to detect when separator crushes to failure thickness.
- **Cell rupture**: use MXPRES or SIGP1 for pressure-based failure of casing.
- **Thermal failure**: MXTMP criterion enables element deletion when temperature exceeds thermal runaway threshold.
- **Combined criteria**: set NCS > 1 to require multiple criteria simultaneously (e.g., strain AND temperature).
- **NUMFIP**: controls how many integration points must fail before element deletion — useful for through-thickness failure modeling in shells.
- **Prefer *MAT_ADD_DAMAGE_GISSMO** for progressive damage over *MAT_ADD_EROSION's IDAM field.
- **Element-size regularization** (LCREGD): compensates for mesh-size dependence of failure criteria.
- **To disable all erosion**: use *CONTROL_MAT.

---

## Quick Reference: Battery Component → Material Model Mapping

| Battery Component | Primary Material Model | Alternative | Element Type |
| ------------------- | ---------------------- | ------------- | -------------- |
| Jellyroll (homogenized) | MAT_026 (Honeycomb) | MAT_063 (Crushable Foam) | Solid |
| Jellyroll (detailed) | MAT_083 (Fu Chang Foam) | MAT_063 MODEL=1/2 | Solid |
| Separator | MAT_063 (Crushable Foam) | MAT_083 (Fu Chang Foam) | Solid |
| Electrode layers | MAT_058 (Laminated Composite) | MAT_024 (Piecewise Linear) | Shell/Solid |
| Anode (graphite on Cu foil) | MAT_058 + MAT_003 | MAT_024 | Shell |
| Cathode (oxide on Al foil) | MAT_058 + MAT_003 | MAT_024 | Shell |
| Aluminum foil | MAT_003 (Plastic Kinematic) | MAT_024 | Shell |
| Copper foil | MAT_003 (Plastic Kinematic) | MAT_024 | Shell |
| Aluminum casing | MAT_024 (Piecewise Linear) | MAT_003 | Shell/Solid |
| Pouch laminate | MAT_181 (Simplified Rubber) | MAT_024 | Shell |
| Electrolyte (ALE) | MAT_009 (Null) + EOS | — | Solid (ALE) |
| Electrolyte (SPH) | MAT_009 (Null) + EOS | MAT_SPH_INCOMPRESSIBLE | SPH |
| All components (thermal) | MAT_T03 (Isotropic TD) | MAT_T10 (TD_LC) | All |
| Thermal runaway | MAT_T09 (Phase Change) | MAT_T10 (TD_LC) | All |
| Failure/erosion overlay | MAT_ADD_EROSION | MAT_ADD_DAMAGE_GISSMO | All |
