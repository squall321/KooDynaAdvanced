# LS-DYNA Battery Example Analysis Report

## Comprehensive Keyword Inventory & Comparison

Four example directories analyzed:

1. **tshell_extshort/** — External short circuit with composite thick shells (prismatic, 10 cells)
2. **tshell_intshort/** — Internal short circuit with composite thick shells (prismatic, 10 cells)
3. **tshell_cylindrical/** — Internal short circuit with cylindrical cell geometry (single cell)
4. **meshless/** — External short circuit using the meshless Randles approach (prismatic, 10 cells)

All examples use **kg/m/s** units.

---

## 1. Complete Keyword Inventory by Example

### 1.1 tshell_extshort (External Short, Composite Thick Shells)

| File | Keywords |
| ------ | ---------- |
| **i.k** | `*KEYWORD`, `*TITLE`, `*PARAMETER`, `*INCLUDE`, `*DATABASE_ELOUT`, `*DATABASE_GLSTAT`, `*DATABASE_SPCFORC`, `*DATABASE_BINARY_D3PLOT`, `*DATABASE_EXTENT_BINARY`, `*DATABASE_HISTORY_TSHELL` |
| **em.k** | `*EM_CONTROL`, `*EM_CONTROL_CONTACT`, `*EM_CONTROL_TIMESTEP`, `*EM_CONTACT`, `*EM_OUTPUT`, `*EM_MAT_001` (×8), `*SET_PART` (×3), `*EM_RANDLES_TSHELL` (×10), `*EM_ISOPOTENTIAL` (×21), `*EM_ISOPOTENTIAL_CONNECT` |
| **structure.k** | `*CONTROL_TERMINATION`, `*CONTROL_TIMESTEP`, `*CONTROL_SHELL`, `*CONTROL_HOURGLASS`, `*CONTROL_CONTACT`, `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` (×10), `*PART` (sphere), `*SECTION_SOLID` (×2), `*MAT_RIGID` (×3), `*PART_COMPOSITE_TSHELL` (×10), `*MAT_CRUSHABLE_FOAM_TITLE` (×5), `*BOUNDARY_PRESCRIBED_MOTION_RIGID`, `*DEFINE_CURVE` (×2) |
| **thermal.k** | `*CONTROL_SOLUTION`, `*CONTROL_THERMAL_SOLVER`, `*INITIAL_TEMPERATURE_SET`, `*MAT_THERMAL_ISOTROPIC` (×3) |
| **current.k** | `*DEFINE_CURVE` (id=555) |
| **uVsSoc.k** | `*DEFINE_CURVE` (id=444) |
| **mesh4.k** | `*SET_NODE_LIST` (×22+), `*SET_NODE_LIST_TITLE` (×2), `*ELEMENT_TSHELL`, `*ELEMENT_SOLID`, `*NODE` |

### 1.2 tshell_intshort (Internal Short, Composite Thick Shells)

| File | Keywords |
| ------ | ---------- |
| **i.k** | `*KEYWORD`, `*TITLE`, `*PARAMETER`, `*INCLUDE`, `*DATABASE_ELOUT`, `*DATABASE_GLSTAT`, `*DATABASE_SPCFORC`, `*DATABASE_BINARY_D3PLOT`, `*DATABASE_EXTENT_BINARY`, `*DATABASE_HISTORY_TSHELL` |
| **em.k** | `*EM_CONTROL`, `*EM_CONTROL_TIMESTEP`, `*EM_OUTPUT`, `*EM_MAT_001` (×7), `*SET_PART` (×2), `*EM_RANDLES_TSHELL` (×10), `*EM_ISOPOTENTIAL` (×22), `*EM_ISOPOTENTIAL_CONNECT`, `*EM_RANDLES_SHORT`, `*DEFINE_FUNCTION_TABULATED`, `*DEFINE_FUNCTION`, `*DEFINE_CURVE` (id=200) |
| **structure.k** | `*CONTROL_TERMINATION`, `*CONTROL_TIMESTEP`, `*CONTROL_SHELL`, `*CONTROL_HOURGLASS`, `*CONTROL_CONTACT`, `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` (×10), `*PART` (sphere + solid tabs), `*SECTION_SOLID` (×2), `*MAT_ELASTIC` (×2), `*MAT_RIGID` (×1), `*PART_COMPOSITE_TSHELL` (×10), `*MAT_CRUSHABLE_FOAM_TITLE` (×5), `*INITIAL_VELOCITY_RIGID_BODY`, `*DEFINE_CURVE` |
| **thermal.k** | `*CONTROL_SOLUTION`, `*CONTROL_THERMAL_SOLVER`, `*INITIAL_TEMPERATURE_SET`, `*MAT_THERMAL_ISOTROPIC` (×3) |
| **current.k** | `*DEFINE_CURVE` (id=555) |
| **uVsSoc.k** | `*DEFINE_CURVE` (id=444) |
| **mesh.k** | `*SET_NODE_LIST` (×20+), `*ELEMENT_TSHELL`, `*ELEMENT_SOLID`, `*NODE` |

### 1.3 tshell_cylindrical (Internal Short, Cylindrical Geometry)

| File | Keywords (all in i.k + mesh.k) |
| ------ | ---------- |
| **i.k** | `*KEYWORD`, `*TITLE`, `*CONTROL_TERMINATION`, `*CONTROL_TIMESTEP`, `*DATABASE_BINARY_D3PLOT`, `*CONTROL_SOLUTION`, `*CONTROL_THERMAL_SOLVER`, `*CONTROL_THERMAL_TIMESTEP`, `*INITIAL_TEMPERATURE_SET`, `*MAT_THERMAL_ISOTROPIC`, `*PART` (×2), `*SECTION_SOLID` (×2), `*MAT_ELASTIC` (×2), `*CONTROL_SHELL`, `*PART_COMPOSITE_TSHELL`, `*MAT_CRUSHABLE_FOAM_TITLE` (×5), `*BOUNDARY_PRESCRIBED_MOTION_SET`, `*BOUNDARY_SPC_SET`, `*EM_CONTROL`, `*EM_CONTROL_TIMESTEP`, `*EM_RANDLES_TSHELL`, `*EM_MAT_001` (×7), `*EM_ISOPOTENTIAL` (×4), `*EM_ISOPOTENTIAL_CONNECT` (×2), `*EM_RANDLES_SHORT`, `*EM_OUTPUT`, `*DEFINE_CURVE` (×4), `*DEFINE_FUNCTION_TABULATED`, `*DEFINE_FUNCTION`, `*INCLUDE` |
| **mesh.k** | `*SET_NODE_LIST` (×7), `*ELEMENT_SOLID`, `*NODE` |

### 1.4 meshless (External Short, Meshless Randles Model)

| File | Keywords |
| ------ | ---------- |
| **i.k** | `*KEYWORD`, `*TITLE`, `*PARAMETER`, `*INCLUDE`, `*DATABASE_ELOUT`, `*DATABASE_GLSTAT`, `*DATABASE_SPCFORC`, `*DATABASE_BINARY_D3PLOT`, `*DATABASE_EXTENT_BINARY`, `*DATABASE_HISTORY_TSHELL` |
| **em.k** | `*EM_CONTROL`, `*EM_CONTROL_CONTACT`, `*EM_CONTROL_TIMESTEP`, `*EM_CONTACT`, `*EM_OUTPUT`, `*EM_MAT_001` (×8), `*SET_PART` (×3), `*EM_RANDLES_MESHLESS` (×10), `*EM_ISOPOTENTIAL` (×21), `*EM_ISOPOTENTIAL_CONNECT` (×11) |
| **structure.k** | `*CONTROL_TERMINATION`, `*CONTROL_TIMESTEP`, `*CONTROL_SHELL`, `*CONTROL_HOURGLASS`, `*CONTROL_CONTACT`, `*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE` (×10), `*PART` (sphere + solid tabs), `*SECTION_SOLID` (×2), `*MAT_RIGID` (×3), `*PART_COMPOSITE_TSHELL` (×10), `*MAT_CRUSHABLE_FOAM_TITLE` (×5), `*BOUNDARY_PRESCRIBED_MOTION_RIGID`, `*DEFINE_CURVE` (×2) |
| **thermal.k** | `*CONTROL_SOLUTION`, `*CONTROL_THERMAL_SOLVER`, `*INITIAL_TEMPERATURE_SET`, `*MAT_THERMAL_ISOTROPIC` (×3) — **commented out** in i.k |
| **current.k** | `*DEFINE_CURVE` (id=555) |
| **uVsSoc.k** | `*DEFINE_CURVE` (id=444) |
| **mesh5.k** | `*SET_NODE_LIST` (×22+), `*SET_NODE_LIST_TITLE` (×2), `*ELEMENT_SOLID`, `*ELEMENT_TSHELL`, `*NODE` |

---

## 2. EM Keywords Deep Dive

### 2.1 *EM_CONTROL

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ----------- | ---------------- | ----------------- | ------------------- | ---------- |
| emsol | 3 | 3 | 3 | 3 |
| ncyclFem | 2 | -200 (auto) | 5 | 2 |
| ncyclBem | 2 | -200 (auto) | 5 | 2 |

### 2.2 *EM_CONTROL_CONTACT

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ----------- | ---------------- | ----------------- | ------------------- | ---------- |
| Present? | YES | **NO** | **NO** | YES |
| Values | 1,1,1,1,,,,0.0002 | — | — | 1,1,1,1,,,,0.0002 |

### 2.3 *EM_CONTACT

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ----------- | ---------------- | ----------------- | ------------------- | ---------- |
| Present? | YES | **NO** | **NO** | YES |
| contid | 1 | — | — | 1 |
| setidS | 1 → SET_PART 20 | — | — | 1 → SET_PART 20 |
| setidM | 20,30 | — | — | 20,30 |
| Values | ,,,,,,0.0002 | — | — | ,,,,,,0.0002 |

> **Key insight**: EM_CONTROL_CONTACT and EM_CONTACT are only needed for **external short** scenarios where conductors from different cells can physically contact each other. Internal shorts use the EM_RANDLES_SHORT mechanism instead.

### 2.4 *EM_CONTROL_TIMESTEP

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ----------- | ---------------- | ----------------- | ------------------- | ---------- |
| tsType | 1 | 1 | 1 | 1 |
| dt | &em_dt = 1.0 | &em_dt = 5e-4 | 1e-2 | &em_dt = 1.0 |

### 2.5 *EM_OUTPUT

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ----------- | ---------------- | ----------------- | ------------------- | ---------- |
| matS/matF | 2/2 | 2/2 | 2/2 | **4/4** |
| solS/solF | 2/2 | 2/2 | 2/2 | **4/4** |
| d3plot | 0 | 0 | 0 | 0 |

### 2.6 *EM_MAT_001 (Electromagnetic Material Properties)

#### tshell_extshort

| mid | mtype | sigma | randletype | Description |
| ----- | ------- | ------- | ----------- | ------------- |
| 11 | **2** (conductor) | **6.e9** | 1 (positive CC) | Positive current collector |
| 12 | 1 (not used) | — | 2 (positive electrode) | Positive electrode |
| 13 | 1 | — | 3 (separator) | Separator |
| 14 | 1 | — | 4 (negative electrode) | Negative electrode |
| 15 | **2** | **3.e9** | 5 (negative CC) | Negative current collector |
| 1 | 2 | 1.e7 | — | Tab solid (positive) |
| 2 | 2 | 1.e7 | — | Tab solid (negative) |
| 3 | **4** (insulator) | 1.e7 | — | Sphere impactor |

#### tshell_intshort

| mid | mtype | sigma | randletype | Description |
| ----- | ------- | ------- | ----------- | ------------- |
| 11 | 2 | **6.e7** | 1 | Positive CC |
| 12 | 1 | — | 2 | Positive electrode |
| 13 | 1 | — | 3 | Separator |
| 14 | 1 | — | 4 | Negative electrode |
| 15 | 2 | **3.e7** | 5 | Negative CC |
| 1 | 2 | 1.e7 | — | Tab solid (positive) |
| 2 | 2 | 1.e7 | — | Tab solid (negative) |
| — | — | — | — | *No sphere EM material (no EM contact)* |

#### tshell_cylindrical

| mid | mtype | sigma | randletype | Description |
| ----- | ------- | ------- | ----------- | ------------- |
| 11 | 2 | **5.88e7** | 1 | Positive CC |
| 12 | 1 | — | 2 | Positive electrode |
| 13 | 1 | — | 3 | Separator |
| 14 | 1 | — | 4 | Negative electrode |
| 15 | 2 | **3.70e7** | 5 | Negative CC |
| 3 | 2 | 5.88e7 | — | End-cap solid (positive) |
| 4 | 2 | 3.70e7 | — | End-cap solid (negative) |

#### meshless

| mid | mtype | sigma | randletype | Description |
| ----- | ------- | ------- | ----------- | ------------- |
| 11 | **1** (not used) | 6.e7 | 1 | Positive CC — **mtype=1 not 2!** |
| 12 | 1 | — | 2 | Positive electrode |
| 13 | 1 | — | 3 | Separator |
| 14 | 1 | — | 4 | Negative electrode |
| 15 | 1 | 3.e7 | 5 | Negative CC — **mtype=1 not 2!** |
| 1 | **2** | 1.e7 | — | Tab solid (positive) |
| 2 | **2** | 1.e7 | — | Tab solid (negative) |
| 3 | **4** | 1.e7 | — | Sphere (insulator) |

> **Critical meshless difference**: In the meshless approach, the layer materials (mid 11–15) all use `mtype=1` (EM solver does not solve current flow through them). Only the solid tab parts (mid 1,2) use `mtype=2`. The Randles circuit is handled entirely through `*EM_ISOPOTENTIAL_CONNECT` with `connType=5`.

---

## 3. Randles Cards

### 3.1 *EM_RANDLES_TSHELL

Used in: **tshell_extshort**, **tshell_intshort**, **tshell_cylindrical**

#### Parameter Comparison

| Parameter | tshell_extshort | tshell_intshort | tshell_cylindrical |
| ----------- | ---------------- | ----------------- | ------------------- |
| Count | 10 (one per cell) | 10 (one per cell) | **1** (single cell) |
| **randlType** | **0** (external short) | **1** (internal short) | **1** (internal short) |
| partSetId | 2 | 2 | 2 |
| **areaType** | 1–10 (rdlArea IDs) | 1–10 (rdlArea IDs) | **10** (SET_PART reference) |
| **Q** (capacity, Ah) | 20.0 | 20.0 | **1.0** |
| cQ (C-rate factor) | 2.777e-2 | 2.777e-2 | **3e-2** |
| **SOCinit** (%) | 100.0 | 100.0 | **10.0** |
| SOCtoU (curve ID) | -444 | -444 | -444 |
| r0cha / r0dis (Ω) | 0.02 / 0.02 | 0.02 / 0.02 | 0.02 / 0.02 |
| r10cha / r10dis (Ω) | 0.008 / 0.008 | 0.008 / 0.008 | 0.008 / 0.008 |
| c10cha / c10dis (F) | 110.0 / 110.0 | 110.0 / 110.0 | **100.0 / 100.0** |
| temp (°C) | 25.0 | 25.0 | *(commented out)* |
| fromTherm | 0 | 0 | *(commented out)* |
| r0ToTherm | 1 | 1 | *(commented out)* |
| dUdT | 0 | 0 | *(commented out)* |
| useSocS | 0 | 0 | — |
| tauSocS | 0 | 0 | — |
| lcidSocS | 0 | 0 | — |

### 3.2 *EM_RANDLES_MESHLESS

Used in: **meshless** only

| Parameter | Value |
| ----------- | ------- |
| Count | 10 (one per cell) |
| randlType | 0 (external short) |
| partSetId | *(blank)* |
| rdlArea | *(blank)* |
| Q | 20.0 |
| cQ | 2.777e-2 |
| SOCinit | 100.0 |
| SOCtoU | -444 |
| r0cha / r0dis | 0.02 / 0.02 |
| r10cha / r10dis | 0.008 / 0.008 |
| c10cha / c10dis | 110.0 / 110.0 |
| temp | 25.0 |
| fromTherm | 0 |
| r0ToTherm | 1 |
| dUdT | 0 |

> **Key meshless difference**: `partSetId` and `rdlArea` fields are left blank. Connection to the mesh happens via `*EM_ISOPOTENTIAL_CONNECT` with `connType=5` instead of through explicit layer-resolved coupling.

### 3.3 *EM_RANDLES_SHORT

Used in: **tshell_intshort** and **tshell_cylindrical** only (internal short scenarios)

| Parameter | tshell_intshort | tshell_cylindrical |
| ----------- | ----------------- | ------------------- |
| **areaType** | **3** | **1** |
| functId | 501 | 501 |

#### Short Circuit Function (DEFINE_FUNCTION id=501)

Both use a function `resistance_short_randle()` that:

1. Calculates `distCC` = distance between positive and negative current collectors
2. Calculates `distSEP` = separator distance/thickness
3. If `distCC < threshold` → returns `resistanceVsThickSep(distSEP)` (short triggered)
4. Else returns `-1` (no short)

| Parameter | tshell_intshort | tshell_cylindrical |
| ----------- | ----------------- | ------------------- |
| distCC threshold | **0.000117 m** (117 µm) | **1e-3 m** (1 mm) |
| Short resistance | 5e-5 Ω (constant) | **2e-3 Ω** (constant) |

#### Resistance vs Separator Thickness (DEFINE_FUNCTION_TABULATED id=502)

| tshell_intshort | tshell_cylindrical |
| ----------------- | ------------------- |
| (0, 5e-5) | (0, 2e-3) |
| (1e-3, 5e-5) | (0.2e-3, 2e-3) |
| (3e-3, 5e-5) | (1e-3, 2e-3) |
| (2.0, 5e-5) | (0.1, 2e-3) |
| (1e2, 5e-5) | — |

---

## 4. EM_ISOPOTENTIAL and EM_ISOPOTENTIAL_CONNECT

### 4.1 *EM_ISOPOTENTIAL

| Example | Count | Configuration |
| --------- | ------- | --------------- |
| **tshell_extshort** | 21 | IDs 1–10: setType=2, randType=**1** (positive CC side); IDs 11–20: setType=2, randType=**5** (negative CC side); ID 37: setType=2 (ground, no randType) |
| **tshell_intshort** | 22 | IDs 1–10: randType=1; IDs 11–20: randType=5; ID 21: setType=2 (extra); ID 22: setType=2 (ground) |
| **tshell_cylindrical** | 4 | ID 1: setType=2 (no randType); ID 2: setType=2 (no randType); ID 3: setType=2, randType=**5** (neg CC); ID 4: setType=2, randType=**1** (pos CC) |
| **meshless** | 21 | IDs 1–10: setType=2, **no randType**; IDs 11–20: setType=2, **no randType**; ID 37: setType=2 (ground) |

> **Critical meshless difference**: No `randType` is assigned to any isopotential in the meshless approach. In the tshell approaches, randType links the isopotentials to the positive CC (1) / negative CC (5) sides of the Randles circuit.

### 4.2 *EM_ISOPOTENTIAL_CONNECT

| Example | Count | Configuration |
| --------- | ------- | --------------- |
| **tshell_extshort** | 1 | connid=1, **connType=3** (ground), isoPotId1=37, R/V/I=0.0 |
| **tshell_intshort** | 1 | connid=1, **connType=3** (ground), isoPotId1=22, R=0.0 |
| **tshell_cylindrical** | 2 | connid=1: **connType=2** (resistance), isoPotId1=1, val=0.05 Ω; connid=2: **connType=3** (ground), isoPotId1=2, val=0.0 |
| **meshless** | 11 | connid=1: **connType=3** (ground), isoPotId1=37; connid=2–11: **connType=5** (Randles circuit), linking isoPotId pairs (1↔11, 2↔12...10↔20), **lcid=1–10** |

> **connType values observed**:
>
> - `2` = Resistance connection
> - `3` = Ground (voltage = 0)
> - `5` = Randles circuit connection (**meshless only** — this is how the meshless approach wires Randles circuits between isopotential surfaces)

---

## 5. Structural Keywords

### 5.1 *PART_COMPOSITE_TSHELL (Thick Shell Element Formulation)

All four examples use `*PART_COMPOSITE_TSHELL` with **elform=5** and **shrf=0.833**.

#### Layer Composition — Prismatic Examples (tshell_extshort, tshell_intshort, meshless)

Each cell has **10 winding repeating units × 9 layers per unit = 90 layers** total.

Single winding unit pattern:

| Layer | mid | Material | Thickness (m) |
| ------- | ----- | ---------- | --------------- |
| 1 | 11 | Positive CC (Cu/Al) | 2.4e-5 |
| 2 | 12 | Positive electrode | 5.4e-5 |
| 3 | 13 | Separator | 1.7e-5 |
| 4 | 14 | Negative electrode | 5.8e-5 |
| 5 | 15 | Negative CC (Cu) | 2.8e-5 |
| 6 | 14 | Negative electrode (mirror) | 5.8e-5 |
| 7 | 13 | Separator | 1.7e-5 |
| 8 | 12 | Positive electrode | 5.4e-5 |
| 9 | 11 | Positive CC | 2.4e-5 |

Total thickness per cell: 10 × (2×2.4e-5 + 2×5.4e-5 + 2×1.7e-5 + 2×5.8e-5 + 2.8e-5) ≈ **3.14 mm**

#### Layer Composition — Cylindrical Example (tshell_cylindrical)

**2 winding units × 8 layers per unit = 16 layers** total.

Single winding unit:

| Layer | mid | Material | Thickness (m) |
| ------- | ----- | ---------- | --------------- |
| 1 | 12 | Positive electrode | 0.5e-3 |
| 2 | 11 | Positive CC | 0.8e-3 |
| 3 | 12 | Positive electrode | 0.5e-3 |
| 4 | 13 | Separator | 0.2e-3 |
| 5 | 14 | Negative electrode | 0.5e-3 |
| 6 | 15 | Negative CC | 0.8e-3 |
| 7 | 14 | Negative electrode | 0.5e-3 |
| 8 | 13 | Separator | 0.2e-3 |

> **Critical difference**: Cylindrical layer thicknesses are ~10–20× larger than prismatic (mm scale vs µm scale).

### 5.2 *MAT_CRUSHABLE_FOAM_TITLE

Used for all layer materials (mid=11–15) in ALL examples:

| Parameter | Value |
| ----------- | ------- |
| ro (density) | 2223 kg/m³ |
| E (Young's modulus) | 1e9 Pa |
| pr (Poisson's ratio) | 0.05 |
| lcid (crush curve) | 33 |
| tsc (tensile stress cutoff) | 3e9 Pa |
| damp | 0.1 |

### 5.3 Tab / End-Cap Materials

| Example | Material | mid | ro | E | pr | Notes |
| --------- | ---------- | ----- | ---- | ---- | ----- | ------- |
| tshell_extshort | **MAT_RIGID** | 1,2,3 | 8928.57 (tabs) / 4000 (sphere) | 200e9 / 1e9 | 0.3 / 0.05 | Tabs constrained (cmo=1, con1=7, con2=7) |
| tshell_intshort | **MAT_ELASTIC** | 1,2 | 8928.57 | 200e9 | 0.3 | Tabs deformable; MAT_RIGID for sphere only |
| tshell_cylindrical | **MAT_ELASTIC** | 3,4 | 2223 | 1e9 | 0.3 | End-cap solids |
| meshless | **MAT_RIGID** | 1,2,3 | 8928.57 (tabs) / 4000 (sphere) | 200e9 / 1e9 | 0.3 / 0.05 | Same as extshort |

### 5.4 *SECTION_SOLID

All examples use `elform=1` (constant stress solid) for solid parts (tabs/end-caps/sphere).

### 5.5 *CONTACT_AUTOMATIC_SURFACE_TO_SURFACE

Present in: **tshell_extshort**, **tshell_intshort**, **meshless** (10 contacts each)

| Parameter | Value | Notes |
| ----------- | ------- | ------- |
| Count | 10 | 9 cell-to-cell pairs + 1 sphere-to-cell |
| fs/fd | 0.2 | Friction |
| sfs/sfm | 10.0 | Scale factors |
| soft | 2 | Soft constraint formulation |
| sofscl | 0.1 | Soft constraint scale |
| depth | 2 | Contact depth checking |

**tshell_cylindrical** uses `*BOUNDARY_PRESCRIBED_MOTION_SET` and `*BOUNDARY_SPC_SET` instead of contacts.

### 5.6 Control Keywords

| Keyword | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| --------- | ---------------- | ----------------- | ------------------- | ---------- |
| *CONTROL_TERMINATION | T_end=100 s | T_end=**0.015 s** | endtim=**5 s** | T_end=100 s |
| *CONTROL_TIMESTEP (dtinit) | 0.1 | **1e-5** | **1e-2** | 0.1 |
| *CONTROL_TIMESTEP (dt2ms) | 0.1 | 1e-5 | 1e-2 | 0.1 |
| *CONTROL_SHELL | wrpang=20, irnxx=-1, theory=2, bwc=2, lamsht=4, cstyp6=1, irquad=2 | Same | Same | Same |
| *CONTROL_HOURGLASS | ihq=6, qh=0.1 | Same | — | Same |
| *CONTROL_CONTACT | slsfac=0.1, rwpnal=1.0, ignore=1, rwgaps=1 | Same | — | Same |

---

## 6. Thermal Keywords

| Keyword | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| --------- | ---------------- | ----------------- | ------------------- | ---------- |
| *CONTROL_SOLUTION | soln=2 (thermal coupling) | soln=2 | soln=2 | soln=2 **(commented out)** |
| *CONTROL_THERMAL_SOLVER | atype=1, solver=11, cgtol=1e-6, gpt=8 | Same | Same | Same |
| *CONTROL_THERMAL_TIMESTEP | — | — | its/tmin/tmax=1e-2 | — |
| *INITIAL_TEMPERATURE_SET | 25°C | 25°C | 25°C | 25°C |
| *MAT_THERMAL_ISOTROPIC | tro=7860, hc=460, tc=40 (tmid=1,2,3) | Same | tro=**2223**, hc=**1420**, tc=**3** (tmid=1 only) | Same as extshort |

---

## 7. Loading & Boundary Conditions

| Property | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ---------- | ---------------- | ----------------- | ------------------- | ---------- |
| **Loading type** | Prescribed motion (slow) | **Impact velocity** | Prescribed displacement | Prescribed motion (slow) |
| Sphere/impactor | pid=31, rigid, v=-0.001 m/s | pid=31, rigid, **vz=-11.7 m/s** | — | pid=31, rigid, v=-0.001 m/s |
| Applied current | -2.0 A constant | -2.0 A constant | **-200 A** constant | -2.0 A constant |
| SOC→Voltage curve | (0,3.0), (1,3.2), (100,4.0), (200,4.0) | Same | Same | Same |
| Boundary prescribed | BOUNDARY_PRESCRIBED_MOTION_RIGID | INITIAL_VELOCITY_RIGID_BODY | BOUNDARY_PRESCRIBED_MOTION_SET (ramp to -1mm) | BOUNDARY_PRESCRIBED_MOTION_RIGID |

---

## 8. Mesh / Element Types

| Property | tshell_extshort | tshell_intshort | tshell_cylindrical | meshless |
| ---------- | ---------------- | ----------------- | ------------------- | ---------- |
| Mesh file | mesh4.k (9106 lines) | mesh.k (10341 lines) | mesh.k (1539 lines) | mesh5.k (9147 lines) |
| Cell elements | ELEMENT_TSHELL | ELEMENT_TSHELL | ELEMENT_SOLID (cylindrical) | ELEMENT_TSHELL |
| Tab/cap elements | ELEMENT_SOLID | ELEMENT_SOLID | ELEMENT_SOLID | ELEMENT_SOLID |
| Node sets | 22+ SET_NODE_LIST | 20+ SET_NODE_LIST | 7 SET_NODE_LIST | 22+ SET_NODE_LIST |

---

## 9. Key Differences Summary

### 9.1 External Short (extshort) vs Internal Short (intshort)

| Aspect | External Short | Internal Short |
| -------- | --------------- | ---------------- |
| EM_RANDLES_TSHELL randlType | **0** | **1** |
| EM_CONTROL_CONTACT | Required | Not needed |
| EM_CONTACT | Required | Not needed |
| EM_RANDLES_SHORT | Not present | **Required** (short circuit trigger function) |
| EM_MAT_001 sigma (CCs) | 6e9 / 3e9 | 6e7 / 3e7 (100× lower) |
| Sphere EM material | mtype=4 (insulator) | Not defined |
| Simulation time | 100 s | 0.015 s |
| Structural timestep | 0.1 s | 1e-5 s |
| Tab material | MAT_RIGID | MAT_ELASTIC |
| Loading | Prescribed slow motion | Impact velocity 11.7 m/s |

### 9.2 Prismatic vs Cylindrical

| Aspect | Prismatic (extshort/intshort) | Cylindrical |
| -------- | ------------------------------ | ------------- |
| Cell count | 10 | **1** |
| Layer count | 90 per cell | **16** |
| Layer thickness | µm scale (17–58 µm) | **mm scale (0.2–0.8 mm)** |
| Battery capacity Q | 20 Ah | **1 Ah** |
| Initial SOC | 100% | **10%** |
| Applied current | 2 A | **200 A** |
| Contacts | 10× AUTOMATIC_SURFACE_TO_SURFACE | None (SPC + prescribed motion) |
| Thermal properties | tro=7860, hc=460, tc=40 | tro=2223, hc=1420, tc=3 |

### 9.3 Tshell vs Meshless Approach

| Aspect | Tshell (EM_RANDLES_TSHELL) | Meshless (EM_RANDLES_MESHLESS) |
| -------- | --------------------------- | ------------------------------- |
| Randles keyword | *EM_RANDLES_TSHELL | **\*EM_RANDLES_MESHLESS** |
| EM solver in layers | mtype=2 for CCs (current solved) | **mtype=1 for ALL layers (no current solve)** |
| EM solver in tabs | mtype=2 | mtype=2 (same) |
| ISOPOTENTIAL randType | Set on each isopotential (1=pos CC, 5=neg CC) | **Not set** (connections via ISOPOTENTIAL_CONNECT) |
| ISOPOTENTIAL_CONNECT | 1 (ground only) | **11** (1 ground + 10× connType=5 Randles) |
| connType=5 usage | Not used | **Core mechanism** — links pos/neg isopotential pairs through Randles circuit |
| Thermal coupling | Active (CONTROL_SOLUTION soln=2) | **Disabled** (thermal.k commented out) |
| Structural mesh | Identical (ELEMENT_TSHELL + ELEMENT_SOLID) | Identical |
| Short circuit | Can be activated | **Commented out** |

> **How meshless works**: Instead of resolving current flow through the composite thick shell layers (which requires mtype=2 and the tshell Randles mechanism), the meshless approach:
>
> 1. Treats all layer materials as `mtype=1` (EM solver ignores them)
> 2. Only solves current in the solid tab parts (`mtype=2`)
> 3. Defines isopotential surfaces on the positive and negative tab faces (node sets 1–10 and 11–20)
> 4. Connects each positive/negative isopotential pair through a Randles circuit using `*EM_ISOPOTENTIAL_CONNECT` with `connType=5`
> 5. The Randles circuit parameters (R0, R10, C10, SOC curve) are defined in `*EM_RANDLES_MESHLESS` and referenced by lcid in the ISOPOTENTIAL_CONNECT cards

---

## 10. Required LS-DYNA Versions

| Example | Minimum Version |
| --------- | ---------------- |
| tshell_extshort | Beta 132836+ (em.k), 141900+ (i.k) |
| tshell_intshort | 141900+ |
| tshell_cylindrical | 141900+ |
| meshless | 141900+ |

---

## 11. Authors

| Example | Author |
| --------- | -------- |
| tshell_extshort | Iñaki (LSTC) |
| tshell_intshort | Iñaki (LSTC) |
| tshell_cylindrical | Not specified |
| meshless | Pierre (LSTC) |
