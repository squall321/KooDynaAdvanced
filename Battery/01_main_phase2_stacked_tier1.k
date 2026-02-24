*KEYWORD
*TITLE
Li-ion Pouch Cell - Phase 2: Thermo-Mechanical (tier1, Stacked)
$
$ ============================================================
$ Phase 2: Thermo-Mechanical
$   - Thermal solver ON (SOTEFP=1, FWORK=0.9)
$   - Separator erosion active
$   - Stacked, tier1, 22 unit cells
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== INCLUDE FILES ====================
$
*INCLUDE
02_mesh_stacked_tier1.k
$
*INCLUDE
04_materials.k
$
*INCLUDE
04_materials_tempdep.k
$
*INCLUDE
04_materials_expansion_stacked_tier1.k
$
*INCLUDE
05_contacts_phase2_tier1.k
$
*INCLUDE
06_boundary_loads_phase2.k
$
*INCLUDE
07_control_phase2.k
$
*INCLUDE
09_database_phase2.k
$
*INCLUDE
10_define_curves_phase2.k
$
*END
