*KEYWORD
*TITLE
Li-ion Pouch Cell - Phase 3: Full Coupled (Struct + Thermal + EM) (tier0, Stacked)
$
$ ============================================================
$ Phase 3: Full Coupled (Struct + Thermal + EM)
$   - Full struct+thermal+EM coupling
$   - ISC -> Joule heating -> thermal runaway
$   - Stacked, tier0, 15 unit cells
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== INCLUDE FILES ====================
$
*INCLUDE
02_mesh_stacked_tier0.k
$
*INCLUDE
04_materials.k
$
*INCLUDE
04_materials_tempdep.k
$
*INCLUDE
04_materials_expansion_stacked_tier0.k
$
*INCLUDE
05_contacts_tier0.k
$
*INCLUDE
06_boundary_loads.k
$
*INCLUDE
07_control.k
$
*INCLUDE
08_em_randles_tier0.k
$
*INCLUDE
09_database.k
$
*INCLUDE
10_define_curves.k
$
$ ==================== ADVANCED MODULES ====================
$
$*INCLUDE
$12_venting.k
$
$*INCLUDE
$13_ale_electrolyte.k
$
*END
