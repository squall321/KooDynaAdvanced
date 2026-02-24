*KEYWORD
*TITLE
Li-ion Pouch Cell - Phase 2: Thermo-Mechanical (tier-1, Wound)
$
$ ============================================================
$ Phase 2: Thermo-Mechanical
$   - Thermal solver ON (SOTEFP=1, FWORK=0.9)
$   - Separator erosion active
$   - Wound, tier-1, 5 unit cells
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== INCLUDE FILES ====================
$
*INCLUDE
03_mesh_wound_tier-1.k
$
*INCLUDE
04_materials.k
$
*INCLUDE
04_materials_tempdep.k
$
*INCLUDE
04_materials_expansion_wound.k
$
*INCLUDE
05_contacts_phase2_wound.k
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
