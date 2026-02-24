#!/usr/bin/env python3
"""
01_main*.k 자동 생성 (Phase 1/2/3 × Stacked/Wound)
=====================================================
각 Phase/Type 조합별 main include 파일을 생성합니다.

사용법:
    python generate_main.py --config battery_config.yaml --tier -1 --type stacked
    python generate_main.py --type both --tier 0 --phase 1 2 3
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List

from battery_utils import (
    load_config, setup_logger, add_common_args,
    tier_to_suffix, get_n_cells_for_tier,
    write_kfile_header,
)

logger = logging.getLogger(__name__)

# Phase descriptions
_PHASE_DESC = {
    1: "Phase 1: Mechanical Only",
    2: "Phase 2: Thermo-Mechanical",
    3: "Phase 3: Full Coupled (Struct + Thermal + EM)",
}

# k-file model type descriptions
_TYPE_DESC = {
    "stacked": "Stacked",
    "wound":   "Wound",
}

_SCENARIO_DESC = {
    "swelling": "Swelling Scenario: Intercalation + SEI Growth",
    "gas":      "Gas Expansion Scenario: External Heat -> Venting -> Rupture",
}


def _mesh_file(model_type: str, tier: float) -> str:
    prefix = "02_mesh_stacked" if model_type == "stacked" else "03_mesh_wound"
    return f"{prefix}{tier_to_suffix(tier)}.k"


def _contact_file(phase: int, model_type: str, tier: float = 0) -> str:
    from battery_utils import tier_to_suffix
    parts = ["05_contacts"]
    if phase < 3:
        parts.append(f"_phase{phase}")
    if model_type == "wound":
        parts.append("_wound")
    # 적층형: TIED 컨택트가 n_uc별로 다르므로 tier suffix 필수
    # 와인딩형: PID가 고정(2001-2005)이므로 tier suffix 불필요
    if model_type == "stacked":
        parts.append(tier_to_suffix(tier))
    return "".join(parts) + ".k"


def _bc_file(phase: int) -> str:
    suffix = f"_phase{phase}" if phase < 3 else ""
    return f"06_boundary_loads{suffix}.k"


def _control_file(phase: int) -> str:
    suffix = f"_phase{phase}" if phase < 3 else ""
    return f"07_control{suffix}.k"


def _em_file(model_type: str, tier: float = -1) -> str:
    if model_type == "wound":
        return "08_em_randles_wound.k"
    # Stacked: use tier-specific EM file so UC count matches the mesh
    return f"08_em_randles{tier_to_suffix(tier)}.k"


def _db_file(phase: int) -> str:
    suffix = f"_phase{phase}" if phase < 3 else ""
    return f"09_database{suffix}.k"


def _curves_file(phase: int) -> str:
    suffix = f"_phase{phase}" if phase < 3 else ""
    return f"10_define_curves{suffix}.k"


def generate_main(config: Dict[str, Any],
                  phase: int = 3,
                  model_type: str = "stacked",
                  tier: float = -1,
                  ale: bool = False,
                  output: str | None = None,
                  log: logging.Logger | None = None) -> str:
    """Generate 01_main_phase{N}_{type}.k for a specific phase/type combo.

    Args:
        ale: Phase 3 전용. True이면 12_venting.k 와 13_ale_electrolyte.k 를
             활성 *INCLUDE 로 삽입 (파일명에 _ale suffix 추가).
             False(기본)이면 주석 처리된 상태로 삽입.
    """
    log = log or logger

    ale_suffix = "_ale" if (ale and phase >= 3) else ""

    if output is None:
        if phase == 3:
            output = f"01_main_phase3_{model_type}{ale_suffix}.k"
        else:
            output = f"01_main_phase{phase}_{model_type}.k"
    outpath = Path(output)

    n_cells = get_n_cells_for_tier(config, tier, model_type)
    tier_label = tier_to_suffix(tier).replace("_", " ").strip()
    type_label = _TYPE_DESC[model_type]
    phase_label = _PHASE_DESC[phase]

    ale_tag = " [+Venting+ALE]" if (ale and phase >= 3) else ""
    title = f"Li-ion Pouch Cell - {phase_label} ({tier_label}, {type_label}){ale_tag}"

    includes: List[str] = []

    # Mesh
    includes.append(_mesh_file(model_type, tier))
    # Structural materials (always included)
    includes.append("04_materials.k")
    # Thermal materials: only needed for phase 2+ (thermal solver ON)
    if phase >= 2:
        includes.append("04_materials_tempdep.k")
        # Thermal expansion: stacked is tier-specific, wound is shared
        if model_type == "stacked":
            includes.append(f"04_materials_expansion_stacked{tier_to_suffix(tier)}.k")
        else:
            includes.append(f"04_materials_expansion_{model_type}.k")
    # Contacts
    includes.append(_contact_file(phase, model_type, tier))
    # Boundary
    includes.append(_bc_file(phase))
    # Control
    includes.append(_control_file(phase))
    # EM (phase 3 only)
    if phase >= 3:
        includes.append(_em_file(model_type, tier))
    # Database
    includes.append(_db_file(phase))
    # Curves
    includes.append(_curves_file(phase))

    with open(outpath, "w", encoding="utf-8") as f:
        f.write("*KEYWORD\n")
        f.write("*TITLE\n")
        f.write(f"{title}\n")
        f.write("$\n")
        f.write(f"$ ============================================================\n")
        f.write(f"$ {phase_label}\n")
        if phase == 1:
            f.write("$   - Impactor lateral impact -> cell deformation\n")
            f.write("$   - Thermal/EM solver OFF\n")
        elif phase == 2:
            f.write("$   - Thermal solver ON (SOTEFP=1, FWORK=0.9)\n")
            f.write("$   - Separator erosion active\n")
        else:
            f.write("$   - Full struct+thermal+EM coupling\n")
            f.write("$   - ISC -> Joule heating -> thermal runaway\n")
        f.write(f"$   - {type_label}, {tier_label}, {n_cells} unit cells\n")
        f.write(f"$ ============================================================\n")
        f.write("$\n")
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")
        f.write("$\n")
        f.write("$ ==================== INCLUDE FILES ====================\n")

        for inc in includes:
            f.write("$\n")
            f.write("*INCLUDE\n")
            f.write(f"{inc}\n")

        # Advanced modules (phase 3 only)
        if phase >= 3:
            f.write("$\n")
            f.write("$ ==================== ADVANCED MODULES ====================\n")
            if ale:
                # 활성화 버전: venting + ALE electrolyte 포함
                f.write("$ (Venting + ALE electrolyte ACTIVE)\n")
                f.write("$\n")
                f.write("*INCLUDE\n")
                f.write("12_venting.k\n")
                f.write("$\n")
                f.write("*INCLUDE\n")
                f.write("13_ale_electrolyte.k\n")
            else:
                # 비활성화 버전: 주석 처리 (기본)
                f.write("$ (Venting + ALE electrolyte commented out — use _ale variant to activate)\n")
                f.write("$\n")
                f.write("$*INCLUDE\n")
                f.write("$12_venting.k\n")
                f.write("$\n")
                f.write("$*INCLUDE\n")
                f.write("$13_ale_electrolyte.k\n")

        f.write("$\n")
        f.write("*END\n")

    log.info("Main 파일 생성 완료: %s", outpath)
    return str(outpath)


def generate_main_master(config: Dict[str, Any],
                         model_type: str = "stacked",
                         tier: float = -1,
                         ale: bool = False,
                         log: logging.Logger | None = None) -> str:
    """Generate 01_main[_ale].k — default phase 3 master file."""
    out = "01_main_ale.k" if ale else "01_main.k"
    return generate_main(config, phase=3, model_type=model_type,
                         tier=tier, ale=ale, output=out, log=log)


def generate_main_scenario(
    config: Dict[str, Any],
    scenario: str,
    model_type: str = "stacked",
    tier: float = -1,
    ale: bool = False,
    output: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """시나리오별 01_main_{scenario}[_ale].k 생성.

    Args:
        scenario: 'swelling' | 'gas'
        ale: True이면 ALE 전해질 활성화 버전 (_ale suffix). gas 시나리오 전용.
    """
    log = log or logger

    ale_suffix = "_ale" if (ale and scenario == "gas") else ""
    tier_suf  = tier_to_suffix(tier)
    if output is None:
        output = f"01_main_{scenario}_{model_type}{tier_suf}{ale_suffix}.k"
    outpath = Path(output)

    n_cells   = get_n_cells_for_tier(config, tier, model_type)
    tier_label = tier_suf.replace("_", " ").strip()
    type_label = _TYPE_DESC[model_type]
    scen_label = _SCENARIO_DESC[scenario]

    ale_tag = " [+ALE Electrolyte]" if (ale and scenario == "gas") else ""
    title   = f"Li-ion Pouch Cell - {scen_label} ({tier_label}, {type_label}){ale_tag}"

    # ── include 목록 구성 ──
    includes: List[str] = []

    # 메시 (공유)
    includes.append(_mesh_file(model_type, tier))
    # 구조 재료 (공유)
    includes.append("04_materials.k")
    # 열 재료 (swelling/gas 모두 열 해석)
    includes.append("04_materials_tempdep.k")
    # 열 팽창: stacked만 tier별, wound는 공통
    if model_type == "stacked":
        includes.append(f"04_materials_expansion_stacked{tier_suf}.k")
    else:
        includes.append(f"04_materials_expansion_{model_type}.k")

    if scenario == "swelling":
        # 접촉: Phase 2 수준 (ERODING 없음, ISC 없음)
        includes.append(_contact_file(phase=2, model_type=model_type, tier=tier))
        includes.append("06_boundary_loads_swelling.k")
        includes.append("07_control_swelling.k")
        # EM 없음 (SOC는 DEFINE_CURVE 9001로 근사)
        includes.append("09_database_phase2.k")
        includes.append("10_define_curves_swelling.k")
        # 스웰링 전용 모듈
        includes.append("14_intercalation_strain.k")
        includes.append("15_sei_growth.k")

    elif scenario == "gas":
        # 접촉: Phase 3 (ERODING 포함, ISC 추적)
        includes.append(_contact_file(phase=3, model_type=model_type, tier=tier))
        includes.append("06_boundary_loads_gas.k")
        includes.append("07_control_gas.k")
        # EM Randles: 열폭주 연쇄반응 추적
        includes.append(_em_file(model_type, tier))
        includes.append("09_database.k")
        includes.append("10_define_curves_gas.k")
        # 가스 생성 모듈
        includes.append("16_gas_generation_standalone.k")

    with open(outpath, "w", encoding="utf-8") as f:
        f.write("*KEYWORD\n")
        f.write("*TITLE\n")
        f.write(f"{title}\n")
        f.write("$\n")
        f.write(f"$ ============================================================\n")
        f.write(f"$ {scen_label}\n")
        if scenario == "swelling":
            f.write("$   - Pseudo-thermal swelling via BOUNDARY_PRESCRIBED_MOTION_SET\n")
            f.write("$   - Intercalation (reversible) + SEI growth (irreversible)\n")
            f.write("$   - No impactor, no ISC, no EM solver\n")
        else:
            f.write("$   - External heat source -> thermal runaway -> gas venting\n")
            f.write("$   - Heat flux = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011]\n")
            f.write("$   - EM Randles tracks SOC + exothermic reactions (FUNCTID 5002)\n")
            f.write("$   - AIRBAG_SIMPLE_AIRBAG_MODEL (12_venting.k, FUNCTID 12010) models rupture\n")
        f.write(f"$   - {type_label}, {tier_label}, {n_cells} unit cells\n")
        f.write(f"$ ============================================================\n")
        f.write("$\n")
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")
        f.write("$\n")
        f.write("$ ==================== INCLUDE FILES ====================\n")

        for inc in includes:
            f.write("$\n")
            f.write("*INCLUDE\n")
            f.write(f"{inc}\n")

        # 가스 시나리오: 벤팅 + ALE 모듈
        if scenario == "gas":
            f.write("$\n")
            f.write("$ ==================== VENTING + ALE MODULES ====================\n")
            f.write("$\n")
            f.write("*INCLUDE\n")
            f.write("12_venting.k\n")
            if ale:
                f.write("$ (ALE electrolyte ACTIVE)\n")
                f.write("$\n")
                f.write("*INCLUDE\n")
                f.write("13_ale_electrolyte.k\n")
            else:
                f.write("$ (ALE electrolyte commented out — use _ale variant to activate)\n")
                f.write("$\n")
                f.write("$*INCLUDE\n")
                f.write("$13_ale_electrolyte.k\n")

        f.write("$\n")
        f.write("*END\n")

    log.info("시나리오 Main 파일 생성 완료: %s (%s)", outpath, scenario)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(
        description="01_main*.k 생성 (Phase × Type 조합)")
    add_common_args(parser)
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (1, 2, 3)")
    parser.add_argument("--type", choices=["stacked", "wound", "both"],
                        default="both", help="모델 타입")
    parser.add_argument("--ale", action="store_true",
                        help="ALE 전해질 활성화 버전만 생성 (_ale suffix)")
    parser.add_argument("--both-ale", action="store_true",
                        help="ALE 활성/비활성 두 버전 모두 생성 (기본 동작)")
    args = parser.parse_args()

    log = setup_logger("gen_main",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)

    types = ["stacked", "wound"] if args.type == "both" else [args.type]
    # ALE 변형 결정: --ale → ALE만, --both-ale → 둘 다, 기본 → 둘 다
    if args.ale:
        ale_variants = [True]
    else:
        ale_variants = [False, True]  # 기본: 비활성 + 활성 둘 다 생성

    for mt in types:
        for ph in args.phase:
            for ale_flag in ale_variants:
                # Phase 1/2는 ALE 무관 → 비활성 버전만
                if ph < 3 and ale_flag:
                    continue
                generate_main(config, phase=ph, model_type=mt,
                              tier=args.tier, ale=ale_flag, log=log)
        # 01_main.k 및 01_main_ale.k (phase3 alias)
        for ale_flag in ale_variants:
            generate_main_master(config, model_type=mt,
                                 tier=args.tier, ale=ale_flag, log=log)


if __name__ == "__main__":
    main()
