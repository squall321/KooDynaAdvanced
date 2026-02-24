# Battery Pouch Cell Simulation — Complete Reference

> **Audience**: AI assistants and engineers continuing development of this project.  
> **Purpose**: Single authoritative reference covering architecture, ID schemes, physics, all applied fixes, and development guidance.  
> **Last updated**: 2026-02 (after Fix 15, 78 files, 0 errors)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Unit System & Solver](#2-unit-system--solver)
3. [Simulation Matrix (30 Run Files)](#3-simulation-matrix-30-run-files)
4. [Physics per Phase](#4-physics-per-phase)
5. [Directory & File Structure](#5-directory--file-structure)
6. [Python Generator Architecture](#6-python-generator-architecture)
7. [ID Scheme Reference](#7-id-scheme-reference)
8. [Mesh Architecture](#8-mesh-architecture)
9. [Material Models](#9-material-models)
10. [EM Circuit Architecture](#10-em-circuit-architecture)
11. [Control Parameters](#11-control-parameters)
12. [Boundary & Loading Conditions](#12-boundary--loading-conditions)
13. [Battery Config Schema (`battery_config.yaml`)](#13-battery-config-schema-battery_configyaml)
14. [All Applied Fixes (1–15)](#14-all-applied-fixes-115)
15. [Known Limitations & Future Work](#15-known-limitations--future-work)
16. [How to Regenerate Files](#16-how-to-regenerate-files)
17. [How to Run a Simulation](#17-how-to-run-a-simulation)
18. [Development Checklist](#18-development-checklist)

---

## 1. Project Overview

**Goal**: LS-DYNA R16 multi-physics simulation of a lithium-ion pouch cell under mechanical abuse (nail penetration / cylinder indentation), with optional thermal and electrochemical coupling.

**Cell types modelled**:
- **Stacked**: Prismatic pouch cell, electrode sheets stacked in Z-direction, 70 × 140 mm footprint.
- **Wound (Jelly-roll)**: Flat wound (stadium cross-section) cell using Archimedean spiral mapping, 60 × 100 mm footprint.

**Solver**: LS-DYNA R16 (double precision recommended), MPP parallel.

**Key solver modules used**:
- Structural: implicit/explicit NLFE
- Thermal: `*CONTROL_THERMAL_SOLVER` (APTS=1, direct)
- Electromagnetic: `*EM_CONTROL` (DIMTYPE=3, Randles equivalent circuit)

---

## 2. Unit System & Solver

| Quantity       | Unit           |
|----------------|----------------|
| Length         | mm             |
| Mass           | tonne (10³ kg) |
| Time           | s              |
| Force          | N              |
| Stress/Pressure| MPa            |
| Energy         | mJ             |
| Temperature    | K              |
| Electrical conductivity | S/mm (Ω⁻¹ mm⁻¹) |

> **Critical**: All numeric values in `.k` files use 10-character fixed-width fields. Scientific notation must fit within 10 characters including sign and exponent (e.g. `3.77e+04` = 8 chars ✓, `3.77e4` = 6 chars BUT adjacent field bleeds on overflow ✗).

---

## 3. Simulation Matrix (30 Run Files)

Entry files live at `Battery/01_main_phaseN_TYPE_tierX.k`.

| Phase | Cell Type | Tier -1 | Tier 0 | Tier 0.5 | Tier 1 | Base |
|-------|-----------|---------|--------|----------|--------|------|
| 1     | Stacked   | ✅ | ✅ | ✅ | ✅ | ✅ |
| 1     | Wound     | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2     | Stacked   | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2     | Wound     | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3     | Stacked   | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3     | Wound     | ✅ | ✅ | ✅ | ✅ | ✅ |

**Tier naming convention**:

| Tier suffix | n_cells | XY mesh (mm) | Purpose |
|-------------|---------|--------------|---------|
| `_tier-1`   | 5       | 5.0          | Ultra-coarse, instant validation |
| `_tier0`    | 15      | 2.5          | Baseline, DOE, quick parametric |
| `_tier0_5`  | 20      | 0.5          | Production / certification (EUCAR, UL 2580) |
| `_tier1`    | 22      | 0.1          | Layer-resolved, fracture mechanics |
| *(base)*    | 15      | 2.5          | Same as tier0; no suffix = default |

---

## 4. Physics per Phase

### Phase 1 — Pure Structural
- Explicit dynamics, quasi-static loading
- Contact: mortar (`*CONTACT_MORTAR_*`) + penalty contacts
- No thermal, no EM
- End time: ~5 ms, DT=auto

### Phase 2 — Thermo-Mechanical (Coupled)
- Phase 1 + `*CONTROL_THERMAL_SOLVER`
- Heat generation from deformation (plastic work → heat via `FWORK`)
- Convection + radiation BCs on outer surface
- `CONTROL_SOLUTION SOTEFP=1` for thermal-structural coupling
- End time: ~5 ms (mechanical) → continued thermal soak

### Phase 3 — Full EM-Thermal-Structural (Randles)
- Phase 2 + `*EM_CONTROL` (DIMTYPE=3)
- Randles equivalent circuit via `*EM_RANDLES_SOLID`
- Internal short circuit via `*EM_RANDLES_SHORT`
- Exothermic reaction via `*EM_RANDLES_EXOTHERMIC_REACTION`
- SOC-dependent tables for R0, R10, C10 (charge & discharge)
- End time: **60 s** (allows thermal runaway propagation)
- Timestep: DT2MS = -1e-6 s, TSSFAC = 0.90

---

## 5. Directory & File Structure

```
Battery/
├── 01_main*.k              Entry files (30 total, see §3)
├── 02_mesh_stacked*.k      Stacked cell mesh (6 tiers + production)
├── 03_mesh_wound*.k        Wound cell mesh (5 tiers)
├── 04_materials.k          Structural + thermal material cards
├── 04_materials_expansion_*.k  Thermal expansion definitions per tier
├── 04_materials_tempdep.k  Temperature-dependent property tables
├── 05_contacts_mortar.k    Mortar contact base
├── 05_contacts_phase*.k    Phase-specific contact definitions
├── 06_boundary_loads.k     SPC, prescribed motion, convection/radiation, ICs
├── 07_control.k            CONTROL_TERMINATION, TIMESTEP, THERMAL, SOLUTION
├── 08_em_randles.k         Base EM Randles (stacked, tier0)
├── 08_em_randles_wound.k   EM Randles — wound cell
├── 08_em_randles_tier-1.k  EM Randles — tier -1 (5 cells)
├── 08_em_randles_tier0_5.k EM Randles — tier 0.5
├── 08_em_randles_tier1.k   EM Randles — tier 1
├── 09_database.k           OUTPUT database requests
├── 10_curves.k             Load curves, define tables
├── 11_sets.k               Part sets, segment sets
├── 12_venting.k            [PLACEHOLDER] Venting / gas release
├── 13_ale_electrolyte.k    [PLACEHOLDER] ALE electrolyte flow
│
├── battery_config.yaml     ⭐ Single source of truth for all parameters
├── battery_utils.py        ID constants (LT/MID/PID/SID/PSET)
├── battery_cli.py          CLI wrapper for generators
│
├── generate_mesh_stacked.py    Stacked cell mesh generator
├── generate_mesh_wound.py      Wound cell mesh generator
├── generate_em_randles.py      EM Randles k-file generator
├── generate_main.py            Main entry-file generator
├── generate_full_model.py      Master orchestrator (calls all generators)
├── generate_materials.py       Material card generator
├── generate_contacts.py        Contact definition generator
├── generate_control.py         Control keyword generator
├── generate_curves.py          Curve / table generator
├── generate_database.py        Database output generator
├── generate_boundary_loads.py  BC / load generator
│
├── doe_framework.py            Design-of-experiments sweep helper
├── convergence_study.py        Mesh convergence study automation
├── estimate_runtime.py         Runtime estimation utility
├── postprocess_results.py      Post-processing utilities
├── prepare_run.py              Run folder preparation
│
├── _keyword_check.py       Validates .k files (checks fields, duplicates)
├── _keyword_audit.py       Audits keyword completeness across all files
├── _overlap_check.py       Checks for mesh/geometry penetrations
├── _extract.py             Extracts specific keyword blocks
├── _fix_space_before_cmt.py  Fixes comment formatting
│
└── BATTERY_SIM_REFERENCE.md   ← This file
```

---

## 6. Python Generator Architecture

### Call Order (generate_full_model.py)

```
battery_config.yaml
        │
        ▼
generate_full_model.py
  ├── generate_materials.py      → 04_materials.k, 04_materials_expansion_*.k
  ├── generate_mesh_stacked.py   → 02_mesh_stacked_*.k
  ├── generate_mesh_wound.py     → 03_mesh_wound_*.k
  ├── generate_em_randles.py     → 08_em_randles*.k
  ├── generate_contacts.py       → 05_contacts_*.k
  ├── generate_control.py        → 07_control.k
  ├── generate_curves.py         → 10_curves.k
  ├── generate_database.py       → 09_database.k
  ├── generate_boundary_loads.py → 06_boundary_loads.k
  └── generate_main.py           → 01_main_*.k (all 30 entry files)
```

### Key Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `StackedMeshGenerator` | `generate_mesh_stacked.py` | Z-stacked prismatic cell mesh. Stores `tab_x_ranges` for pouch hole cutting. |
| `WoundMeshGenerator`   | `generate_mesh_wound.py`   | Archimedean spiral wound cell. Stores `_tab_x_ranges` for endcap hole cutting. |
| `EMRandlesGenerator`   | `generate_em_randles.py`   | All 6 `08_em_randles*.k` files. `write_em_mat()` writes exactly 10-char sigma fields. |
| `MainGenerator`        | `generate_main.py`         | Writes all 30 `01_main_*.k` include-file trees. |

### Running Generators

```powershell
# Regenerate everything
cd D:\KooDynaAdvanced\Battery
python generate_full_model.py

# Regenerate only mesh files
python generate_mesh_stacked.py
python generate_mesh_wound.py

# Regenerate only EM files
python generate_em_randles.py

# Validate all .k files
python _keyword_check.py
```

---

## 7. ID Scheme Reference

### Layer Types (LT) — used as part of unit-cell PID formula

| Name      | LT |
|-----------|----|
| AL_CC     |  1 |
| CATHODE   |  2 |
| SEPARATOR |  3 |
| ANODE     |  4 |
| CU_CC     |  5 |

### Material IDs (MID)

| Name         | MID | TMID (thermal offset +100) |
|--------------|-----|-----------------------------|
| AL           |   1 | 101 |
| CU           |   2 | 102 |
| NMC (cathode)|   3 | 103 |
| GRAPHITE     |   4 | 104 |
| SEPARATOR    |   5 | 105 |
| POUCH        |   6 | 106 |
| RIGID        |   7 | 107 |
| ELECTROLYTE  |   8 | 108 |

> Thermal material MIDs = structural MID + 100 (e.g., `*MAT_THERMAL_ISOTROPIC` for Al uses MID=101).

### Part IDs (PID)

| Name              | PID  | Formula / Note |
|-------------------|------|----------------|
| POUCH_TOP         |  10  | Upper endcap panel |
| POUCH_BOTTOM      |  11  | Lower endcap panel |
| POUCH_SIDE        |  12  | Side walls |
| ELECTROLYTE       |  13  | Electrolyte fill |
| TAB_POS           |  20  | Positive (Al) tab |
| TAB_NEG           |  21  | Negative (Cu) tab |
| PCM_POS           |  30  | Positive current collector mesh |
| PCM_NEG           |  31  | Negative current collector mesh |
| IMPACTOR          | 100  | Rigid impactor |
| MANDREL_CORE      | 200  | Wound cell mandrel |
| Unit cell (stacked)| 1000+uc×10+lt | uc=unit cell index, lt=layer type |
| Wound layer       | 2000+lt       | lt=layer type |

### Section IDs (SID)

| Name             | SID |
|------------------|-----|
| SHELL_BT         |   1 |
| SHELL_FULL       |   2 |
| SOLID_1PT        |   3 |
| SOLID_IMPACTOR   |   4 |
| SOLID_CORE       |   5 |
| SHELL_POUCH      |   6 |
| SHELL_CU_CC      |   7 |

### Part Set IDs (PSET)

| Name          | PSET |
|---------------|------|
| IMPACTOR      | 100  |
| POUCH         | 101  |
| ALL_CELL      | 102  |
| ALL_CATHODE   | 103  |
| ALL_ANODE     | 104  |
| ALL_SEPARATOR | 105  |
| ALL_AL_CC     | 106  |
| ALL_CU_CC     | 107  |
| ELECTROLYTE   | 108  |

---

## 8. Mesh Architecture

### Stacked Cell

- Electrodes stacked along **Z-axis**
- `n_cells` unit cells per configuration (tier-dependent)
- Each unit cell = AL_CC + CATHODE + SEPARATOR + ANODE + CU_CC (5 layers)
- **Tabs** protrude in **+Y direction** from top face of stack
  - Positive (Al) tab: x_center = 17.5 mm, width = 10 mm
  - Negative (Cu) tab: x_center = 52.5 mm, width = 10 mm
- **Pouch box**: 70 × 140 mm XY, wraps around stack in Z
  - Y-max side wall has **holes** cut at tab X-ranges (Fix 15)
- **PCM** (current collector buses): small rectangular shells at tab tops

### Wound Cell

- Flat jelly-roll wound around mandrel (radius = 2 mm)
- Cross-section is stadium (rectangle + two semicircles)
- Cell footprint: 60 × 100 mm
- Archimedean spiral: `r(θ) = r_core + t_ucell × θ / (2π)`
- Layers mapped from spiral parameterization into 3D shell elements
- **Tabs** at top and bottom Z-face along Y-edge
  - Positive tab: y_offset = +10 mm from top
  - Negative tab: y_offset = −10 mm from top
- **Endcap panels** (PID_POUCH_TOP) have **holes** cut at tab X-ranges (Fix 14)

### Tab/Pouch Hole Cutting (Fixes 14 & 15)

Both generators detect where tabs physically exit the pouch wall and skip generating those shell elements. This prevents initial mesh penetration that would cause contact instability.

**Stacked** (`generate_mesh_stacked.py`):
```python
self.tab_x_ranges: list = []              # set in __init__
# In _create_tab_strip(): appended with (x_lo_tab, x_hi_tab)
# In _create_pouch_box(): j==nj-1 panels skipped if overlapping tab X range
```

**Wound** (`generate_mesh_wound.py`):
```python
self._tab_x_ranges: list = []             # set in __init__
# In _create_wound_tabs(): appended with (x_lo, x_hi)
# In _create_pouch_and_electrolyte(): upper endcap panel skipped if overlapping
```

---

## 9. Material Models

| Component     | Structural Model        | Key Parameters |
|---------------|-------------------------|----------------|
| Al CC (shell) | `*MAT_JOHNSON_COOK` (MID=1) | A=148 MPa, B=345 MPa, n=0.183, failure strain |
| Cu CC (shell) | `*MAT_JOHNSON_COOK` (MID=2) | A=90 MPa, B=292 MPa, n=0.31 |
| NMC cathode   | `*MAT_CRUSHABLE_FOAM` (MID=3) | Compressive curve from nano-indentation |
| Graphite anode| `*MAT_CRUSHABLE_FOAM` (MID=4) | Compressive curve |
| Separator PE  | `*MAT_PIECEWISE_LINEAR_PLASTICITY` (MID=5) + `*MAT_ADD_EROSION` + GISSMO | Thermal shutdown: zero stiffness at T>135°C |
| Pouch film    | `*MAT_JOHNSON_COOK` (MID=6) | Al/PE laminate, 153 µm |
| PCM / Impactor| `*MAT_RIGID` (MID=7) | |
| Electrolyte   | Custom elastic fill (MID=8) | Incompressible-like bulk modulus |

Thermal counterparts (MID+100) defined in same `04_materials.k` using:
- `*MAT_THERMAL_ISOTROPIC` for isotropic conductors (Al, Cu, electrolyte)
- `*MAT_THERMAL_ORTHOTROPIC` for layered composites (separator, electrode coatings)

Temperature-dependent curves live in `04_materials_tempdep.k`.

---

## 10. EM Circuit Architecture

### Key Control Settings (`08_em_randles*.k`)

```
*EM_CONTROL
$    EMSOL    NUMLS  MACRODT   DIMTYPE    NCYLBEM
         2        1      0.0         3          0
```

- `EMSOL=2`: Randles equivalent circuit solver
- `DIMTYPE=3`: 3D conduction only — NO boundary element method (BEM)
- `NCYLBEM=0`: No cylindrical BEM mesh (consistent with DIMTYPE=3)
- No `*EM_CIRCUIT` block — Randles model is self-contained

### EM_MAT_001 (Conductors)

Defined **only** in `08_em_randles*.k` files — **NOT** in `04_materials.k`.

```
*EM_MAT_001
$      MID     MTYPE     SIGMA
         1         2  3.77e+04    ← Al  (3.77×10⁴ S/mm)
         2         2  5.96e+04    ← Cu  (5.96×10⁴ S/mm)
         3         1              ← NMC cathode (non-conductor)
         4         1              ← Graphite anode
         5         1              ← Separator
         6         1              ← Pouch
         7         1              ← Rigid (PCM/impactor)
         8         1              ← Electrolyte
```

> **Field width rule**: `3.77e+04` = 8 characters → occupies cols 21–28 within field 3 (cols 21–30). Safe. `3.77e4` = 6 chars but LS-DYNA still reads the trailing `4` as field 4 (EOSID) → causes **"EOS 4 not found"** error. Always use explicit `+` in exponent.

### Randles Equivalent Circuit

`*EM_RANDLES_SOLID` per electrode layer (one per LT = AL_CC, CATHODE, SEPARATOR, ANODE, CU_CC).  
Each references SOC-dependent lookup tables:

| Table ID | Contents |
|----------|---------|
| 8001 | R0 — charge (internal resistance, SOC × T 2D table) |
| 8002 | R0 — discharge |
| 8003 | R10 — charge (diffusion resistance at 10 s) |
| 8004 | R10 — discharge |
| 8005 | C10 — charge (RC capacitance at 10 s) |
| 8006 | C10 — discharge |

### Internal Short Circuit

`*EM_RANDLES_SHORT` — activates when separator part (PSET 105) elements reach failure criterion (from GISSMO erosion or temperature threshold).

### Exothermic Reaction

`*EM_RANDLES_EXOTHERMIC_REACTION` — SEI decomposition, cathode-electrolyte reaction, anode-binder reaction rates as functions of temperature.

### Six EM Files (one per tier/type)

| File | Tier / Cell type |
|------|-----------------|
| `08_em_randles.k`         | Stacked, tier 0 (15 cells) |
| `08_em_randles_tier-1.k`  | Stacked, tier -1 (5 cells) |
| `08_em_randles_tier0_5.k` | Stacked, tier 0.5 (20 cells) |
| `08_em_randles_tier1.k`   | Stacked, tier 1 (22 cells) |
| `08_em_randles_wound.k`   | Wound cell (default) |

---

## 11. Control Parameters

### Phase 3 Control (`07_control.k`)

```
*CONTROL_TERMINATION
  ENDTIM = 60.0          (s)

*CONTROL_TIMESTEP
  DT2MS  = -1.0e-6        (mass-scaled minimum, s)
  TSSFAC = 0.90

*CONTROL_THERMAL_SOLVER
  APTS   = 1             (fully implicit)
  SOLVER = 12            (direct sparse)
  FWORK  = 0.90          (90% plastic work → heat)

*CONTROL_SOLUTION
  SOTEFP = 1             (thermal-structural coupling)

*CONTROL_REFINE_SOLID
  PSIDL  = 102           (PSET ALL_CELL)
  NLVL   = 2             (adaptive refinement levels)
```

### Phase 1 / Phase 2 Differences
- Phase 1: No thermal/EM keywords; ENDTIM ≈ 5 ms
- Phase 2: Adds `CONTROL_THERMAL_*`; FWORK active; SOTEFP=1
- Phase 3: All of Phase 2 + EM; ENDTIM = 60 s

---

## 12. Boundary & Loading Conditions (`06_boundary_loads.k`)

| Keyword | Parameters | Description |
|---------|-----------|-------------|
| `*BOUNDARY_SPC_SET` | SID=1 | Fix all DOF on bottom face |
| `*BOUNDARY_PRESCRIBED_MOTION_SET` | SID=2, curve=3001 | Impactor displacement ramp |
| `*SET_SEGMENT_GENERAL` | SID=3, PART 10/11/12 | Outer surface of pouch |
| `*BOUNDARY_CONVECTION_SET` | SID=3, h=5×10⁻⁶ W/mm²K, T∞=298.15 K | Natural convection |
| `*BOUNDARY_RADIATION_SET` | SID=3, ε=5.67×10⁻¹⁴ W/mm²K⁴ | Stefan-Boltzmann radiation |
| `*INITIAL_TEMPERATURE` | T=298.15 K | Room temperature IC |

Curve 3001 = displacement vs. time ramp for impactor motion (defined in `10_curves.k`).

---

## 13. Battery Config Schema (`battery_config.yaml`)

Top-level structure:

```yaml
version: "1.0.0"
date: "2026-02-17"
units: {length: mm, mass: tonne, time: s, ...}

geometry:
  stacked:
    cell_dimensions: {width: 70, height: 140}
    layer_thickness:
      al_current_collector: 0.012
      cathode_coating:       0.065
      separator:             0.020
      anode_coating:         0.070
      cu_current_collector:  0.008
      pouch:                 0.153
      electrolyte_buffer:    0.2
    unit_cell:
      calculated_thickness: 0.25  # = 0.012+0.065×2+0.020+0.070×2+0.008
    stacking:
      default_n_cells: 15
      tier_definitions:
        tier_minus1: {n_cells:5, mesh_size_xy:5.0, typical_elements:6000}
        tier_0:      {n_cells:15, mesh_size_xy:2.5, typical_elements:57000}
        tier_0_5:    {n_cells:20, mesh_size_xy:0.5, typical_elements:1800000}
        tier_1:      {n_cells:22, mesh_size_xy:0.1, typical_elements:200000000}
    tabs:
      positive: {width:10, height:8, x_center:17.5}
      negative: {width:10, height:8, x_center:52.5}
    pcm: {width:20, height:3, thickness:1}
    fillet: {radius:2.0, n_segments:3}

  wound:
    cell_dimensions: {width:60, height:100}
    layer_thickness: (same as stacked)
    winding:
      default_n_windings: 15
      mandrel_radius: 2.0
      core_fill: electrolyte
      tier_definitions:
        tier_minus1:5, tier_0:15, tier_0_5:20, tier_1:25, tier_2:30
    tabs:
      positive: {width:10, height:8, y_offset:+10}
      negative: {width:10, height:8, y_offset:-10}

impactor:
  cylinder: {radius:7.5, length:80, offset:1.0, n_circ:24, n_radial:4}
  nail: {tip_length:3, tip_radius:0.5}

electrochemistry:
  soc_tables: (SOC×Temperature 2D for R0/R10/C10 charge/discharge)

materials:
  (yield stresses, hardening, thermal conductivities, heat capacities, ...)
```

**Modifying parameters**: Edit `battery_config.yaml` only, then run `python generate_full_model.py` to regenerate all k-files. Never hand-edit mesh or EM files directly.

---

## 14. All Applied Fixes (1–15)

### Fix 1–9 (prior session)
Various fixes including: TGRLC keyword format, thermal expansion PID assignments, GISSMO card format, PCM Jacobian error, separator GISSMO shutdown temperature, contact segment orientation, database output format, rigid body constraint conflicts, and part set completeness.

### Fix 10 — EM_CONTROL DIMTYPE and NCYLBEM
- **Root cause**: `DIMTYPE=0` (BEM mode) required a boundary element mesh that didn't exist; `NCYLBEM=1` triggered BEM cylinder setup.
- **Fix**: Set `DIMTYPE=3` (conduction only), `NCYLBEM=0`.
- **Files**: `08_em_randles*.k` (6 files) + `generate_em_randles.py`

### Fix 11 — EM_CIRCUIT Removed
- **Root cause**: `*EM_CIRCUIT` block defined an external circuit that conflicted with the self-contained Randles model.
- **Fix**: Removed `*EM_CIRCUIT` block entirely.
- **Files**: `08_em_randles*.k`, `generate_em_randles.py`

### Fix 12 — EM_MAT_001 Added to Randles Files
- **Root cause**: EM_MAT was missing from Randles files; LS-DYNA could not assign conductivity.
- **Fix**: Added `*EM_MAT_001` block (MID 1–8) to all 6 `08_em_randles*.k`.
- **Files**: All 6 em_randles files + generator

### Fix 13a — EM_MAT Duplicate Keyword
- **Root cause**: `04_materials.k` had an `*EM_MAT_001` block AND `08_em_randles_wound.k` also had one → LS-DYNA R16 enforces strict duplicate-keyword rejection.
- **Fix**: Removed `*EM_MAT_001` section from `04_materials.k`. Replaced with comment pointing to `08_em_randles*.k`.
- **File**: `04_materials.k`

### Fix 13b — EOS 4 Not Found (Field Width Overflow)
- **Root cause**: Sigma values `3.77e4` and `5.96e4` are 6 characters each. In LS-DYNA's fixed 10-char field format, field 3 = cols 21–30. The value `3.77e4` occupies cols 21–26, leaving columns 27–30 as spaces. However the trailing digit `4` (from a value like `3.77e4`) overflowed into field 4 (col 31 = EOSID), causing LS-DYNA to look for `*EOS` with ID 4.
- **Correct values**: `3.77e+04` (8 chars, cols 21–28) and `5.96e+04` (8 chars) — never overflow.
- **Fix**: Changed all sigma values in all 6 EM files and in `generate_em_randles.py`.

### Fix 14 — Wound Tab/Pouch Endcap Mesh Penetration
- **Root cause**: Wound cell tabs protrude through the `PID_POUCH_TOP` endcap panel (flat XZ panel at Y_max). Initial mesh penetration caused contact instability.
- **Fix**: `generate_mesh_wound.py` stores `_tab_x_ranges` from `_create_wound_tabs()`. `_create_pouch_and_electrolyte()` skips upper endcap panels whose X-range overlaps any tab X-range.
- **Files**: `generate_mesh_wound.py` + all 5 `03_mesh_wound_*.k` regenerated.

### Fix 15 — Stacked Tab/Pouch Side Wall Mesh Penetration
- **Root cause**: Stacked cell tabs protrude in +Y direction through the `PID_POUCH_SIDE` Y-max wall (j=nj-1 row of side wall panels).
- **Fix**: `generate_mesh_stacked.py` stores `tab_x_ranges` from `_create_tab_strip()`. `_create_pouch_box()` skips Y-max wall panels (j_p == nj-1) whose X-range overlaps any tab X-range.
- **Files**: `generate_mesh_stacked.py` + all 6 `02_mesh_stacked_*.k` regenerated.

---

## 15. Known Limitations & Future Work

### Placeholders (Not Yet Implemented)

| File | Status | Description |
|------|--------|-------------|
| `12_venting.k` | PLACEHOLDER | Gas venting model — pressure relief valve, mass flow boundary, SPH/ALE gas jet |
| `13_ale_electrolyte.k` | PLACEHOLDER | ALE electrolyte flow during cell crush — requires multi-material ALE setup |

### Known Limitations

1. **Tier 0.5+ wound**: 4M elements — requires cluster (128+ cores, 10+ GB).
2. **Tier 1 stacked**: 200M elements — requires HPC (1000+ cores).
3. **Fillet mesh**: Pouch corner fillets use `n_segments=3` — may not be smooth enough for fracture studies at tier 1. Increase to 6–8 in config for high-fidelity runs.
4. **Thermal runaway propagation**: Phase 3 models single-cell. Multi-cell module propagation not modelled.
5. **SEI layer growth**: Not modelled (only decomposition reaction is included).
6. **Electrolyte pressure**: Placeholder ALE file is empty; current model has no internal fluid pressure from electrolyte.

### Suggested Next Steps

- [ ] Implement `12_venting.k` using SPH or simple mass-flow BC
- [ ] Implement `13_ale_electrolyte.k` with MM-ALE multi-material setup
- [ ] Add `14_eos_electrolyte.k` for fluid equation of state
- [ ] Validate against nail penetration test data (force-displacement, temperature)
- [ ] Implement module-level propagation (N × pouch cells in series/parallel)
- [ ] Add `*MAT_COHESIVE_GENERAL` for delamination between electrode layers

---

## 16. How to Regenerate Files

### Full Regeneration

```powershell
cd D:\KooDynaAdvanced\Battery
python generate_full_model.py        # regenerates ALL .k files
python _keyword_check.py             # validates 78 files
```

Expected output: `78 files checked, 0 errors, 0 warnings`

### Partial Regeneration

```powershell
python generate_mesh_stacked.py      # → 02_mesh_stacked_*.k (6 files)
python generate_mesh_wound.py        # → 03_mesh_wound_*.k (5 files)
python generate_em_randles.py        # → 08_em_randles*.k (5 files)
python generate_main.py              # → 01_main_*.k (30 files)
python generate_materials.py         # → 04_materials*.k
python generate_contacts.py          # → 05_contacts_*.k
python generate_control.py           # → 07_control.k
python generate_boundary_loads.py    # → 06_boundary_loads.k
python generate_curves.py            # → 10_curves.k
python generate_database.py          # → 09_database.k
```

### Changing a Geometry Parameter

1. Edit `battery_config.yaml` (e.g., change `geometry.stacked.tabs.positive.x_center`)
2. Run `python generate_full_model.py`
3. Run `python _keyword_check.py`
4. Check `python _overlap_check.py` for new mesh penetrations

---

## 17. How to Run a Simulation

### Basic Run (Windows, MPP LS-DYNA)

```powershell
cd D:\KooDynaAdvanced\Battery
# Example: Phase 3, wound cell, baseline mesh
mpirun -np 8 lsdyna_mpp i=01_main_phase3_wound.k memory=2000m
```

### Recommended Tier by Purpose

| Purpose | Recommended Tier | Typical Runtime |
|---------|-----------------|-----------------|
| k-file syntax check | tier -1 | < 1 min |
| Quick parametric / DOE | tier 0 | minutes (laptop) |
| Production / certification | tier 0.5 | hours (cluster) |
| Research / fracture | tier 1 | days (HPC) |

### Output Files

| File | Content |
|------|---------|
| `d3plot` | Full field output (stress, strain, temperature, current) |
| `glstat` | Global energy history |
| `matsum` | Energy per material |
| `rcforc` | Reaction forces at contacts |
| `nodout` | Nodal time history |
| `elout`  | Element time history |

---

## 18. Development Checklist

When adding a new feature or fix:

- [ ] Edit `battery_config.yaml` if any parameter changes
- [ ] Update the relevant generator (`generate_*.py`)
- [ ] Run `python generate_full_model.py` (or targeted generator)
- [ ] Run `python _keyword_check.py` → must show 0 errors, 0 warnings
- [ ] Run `python _overlap_check.py` → must show 0 penetrations
- [ ] If adding new IDs, update `battery_utils.py` (LT / MID / PID / SID / PSET)
- [ ] If adding new keywords, check for duplicates across all include files
- [ ] Test with tier -1 run before submitting full job
- [ ] Document the fix in this file under §14

### LS-DYNA R16 Field Format Summary

```
LS-DYNA fixed-width card = 8 fields × 10 characters = 80 chars per line
Field 1: cols  1–10
Field 2: cols 11–20
Field 3: cols 21–30
Field 4: cols 31–40
...
```

Common pitfalls:
- Scientific notation: ALWAYS use form `Xe+YY` (never `XeYY` if value ≥ 5 chars)
- Negative exponent: `1.0e-06` = 7 chars ✓
- IDs must be positive integers; EOSID=0 means "no EOS"
- Duplicate `*KEYWORD` blocks are fatal errors in R16

---

*End of reference document. Last verified: 78 files, 0 keyword errors, 0 warnings, 0 overlap penetrations.*
