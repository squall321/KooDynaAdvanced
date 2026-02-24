*KEYWORD
*TITLE
Li-ion Pouch Cell - Gas Expansion Scenario: External Heat -> Venting -> Rupture (tier-1, Stacked) [+ALE Electrolyte]
$
$ ============================================================
$ Gas Expansion Scenario: External Heat -> Venting -> Rupture
$   - External heat source -> thermal runaway -> gas venting
$   - Heat flux = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011]
$   - EM Randles tracks SOC + exothermic reactions (FUNCTID 5002)
$   - AIRBAG_SIMPLE_AIRBAG_MODEL (12_venting.k, FUNCTID 12010) models rupture
$   - Stacked, tier-1, 5 unit cells
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== INCLUDE FILES ====================
$
*INCLUDE
02_mesh_stacked_tier-1.k
$
*INCLUDE
04_materials.k
$
*INCLUDE
04_materials_tempdep.k
$
*INCLUDE
04_materials_expansion_stacked_tier-1.k
$
*INCLUDE
05_contacts_tier-1.k
$
*INCLUDE
06_boundary_loads_gas.k
$
*INCLUDE
07_control_gas.k
$
*INCLUDE
08_em_randles_tier-1.k
$
*INCLUDE
09_database.k
$
*INCLUDE
10_define_curves_gas.k
$
*INCLUDE
16_gas_generation_standalone.k
$
$ ==================== VENTING + ALE MODULES ====================
$
*INCLUDE
12_venting.k
$ (ALE electrolyte ACTIVE)
$
*INCLUDE
13_ale_electrolyte.k
$
*END
