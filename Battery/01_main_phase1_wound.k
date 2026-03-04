*KEYWORD
*TITLE
Li-ion Pouch Cell - Phase 1: Mechanical Only (tier0, Wound)
$
$ ============================================================
$ Phase 1: Mechanical Only
$   - Impactor lateral impact -> cell deformation
$   - Thermal/EM solver OFF
$   - Wound, tier0, 15 unit cells
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== INCLUDE FILES ====================
$
*INCLUDE
03_mesh_wound_tier0.k
$
*INCLUDE
04_materials.k
$
*INCLUDE
05_contacts_phase1_wound.k
$
*INCLUDE
06_boundary_loads_phase1.k
$
*INCLUDE
07_control_phase1.k
$
*INCLUDE
09_database_phase1.k
$
*INCLUDE
10_define_curves_phase1.k
$
*END
