*KEYWORD
*TITLE
Li-ion Pouch Cell - Swelling Scenario: Intercalation + SEI Growth (tier0, Stacked)
$
$ ============================================================
$ Swelling Scenario: Intercalation + SEI Growth
$   - Pseudo-thermal swelling via BOUNDARY_PRESCRIBED_MOTION_SET
$   - Intercalation (reversible) + SEI growth (irreversible)
$   - No impactor, no ISC, no EM solver
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
05_contacts_phase2_tier0.k
$
*INCLUDE
06_boundary_loads_swelling.k
$
*INCLUDE
07_control_swelling.k
$
*INCLUDE
09_database_phase2.k
$
*INCLUDE
10_define_curves_swelling.k
$
*INCLUDE
14_intercalation_strain.k
$
*INCLUDE
15_sei_growth.k
$
*END
