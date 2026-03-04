#!/usr/bin/env python3
"""
generate_full_model.py — 원클릭 전체 모델 생성
===============================================
배터리 외곽 사이즈 + 용량만 지정하면 전체 LS-DYNA k-file 세트를 자동 생성.

사용법:
    # YAML 기본값 사용
    python generate_full_model.py --type stacked --tier -1

    # 외곽 사이즈 + 용량 오버라이드
    python generate_full_model.py --width 80 --height 160 --capacity 3.5 --type stacked --tier 0

    # 와인딩형 + 전 Phase
    python generate_full_model.py --type wound --tier -1 --phase 1 2 3

    # 양쪽 타입 한번에
    python generate_full_model.py --type both --tier -1 0

생성 파일:
    01_main*.k           (Phase × Type)
    02_mesh_stacked*.k   (적층 메시)
    03_mesh_wound*.k     (와인딩 메시)
    04_materials.k       (재료)
    04_materials_tempdep.k (온도 의존)
    05_contacts*.k       (접촉)
    06_boundary_loads*.k (경계조건)
    07_control*.k        (솔버 제어)
    08_em_randles*.k     (EM 회로)
    09_database*.k       (출력)
    10_define_curves*.k  (커브/함수)
"""
from __future__ import annotations

import argparse
import copy
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from battery_utils import (
    load_config, setup_logger, add_common_args,
    calculate_n_cells, get_geometry, get_n_cells_for_tier,
    tier_to_yaml_key, tier_to_suffix,
    get_scenario_params,
)

logger = logging.getLogger(__name__)


def _override_config(config: Dict[str, Any],
                     width: Optional[float] = None,
                     height: Optional[float] = None,
                     capacity: Optional[float] = None,
                     areal_cap: Optional[float] = None) -> Dict[str, Any]:
    """CLI에서 지정된 값으로 YAML config를 in-memory 오버라이드.

    오버라이드된 값으로 n_cells도 자동 재계산.
    """
    cfg = copy.deepcopy(config)

    for mtype in ("stacked", "wound"):
        geo = cfg.get("geometry", {}).get(mtype, {})
        if not geo:
            continue
        dim = geo.get("cell_dimensions", {})

        if width is not None:
            dim["width"] = width
        if height is not None:
            dim["height"] = height

    if capacity is not None:
        em = cfg.setdefault("em_randles", {}).setdefault("cell_parameters", {})
        em["capacity_Q"] = capacity

    # n_cells 자동 재계산 (capacity가 있을 때)
    if capacity is not None or width is not None or height is not None:
        for mtype in ("stacked", "wound"):
            geo = cfg.get("geometry", {}).get(mtype, {})
            if not geo:
                continue
            dim = geo.get("cell_dimensions", {})
            w = dim.get("width", 70.0)
            h = dim.get("height", 140.0)
            cap = cfg.get("em_randles", {}).get("cell_parameters", {}).get("capacity_Q", 2.6)
            ar_cap = areal_cap or 3.5
            n_auto = calculate_n_cells(cap, w, h, ar_cap)

            # Update default
            if mtype == "stacked":
                stk = geo.setdefault("stacking", {})
                stk["default_n_cells"] = n_auto
            else:
                wnd = geo.setdefault("winding", {})
                wnd["default_n_windings"] = n_auto

    return cfg


def _call_generator(script: str, args: List[str], log: logging.Logger) -> bool:
    """자식 프로세스로 generator 호출."""
    cmd = [sys.executable, script] + args
    log.info("  > %s %s", script, " ".join(args))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=600, check=False)
        if result.returncode != 0:
            log.error("    FAILED: %s", result.stderr[:200])
            return False
        return True
    except (subprocess.SubprocessError, OSError) as e:
        log.error("    ERROR: %s", e)
        return False


def generate_full_model(
    config: Dict[str, Any],
    model_types: List[str],
    tiers: List[float],
    phases: List[int],
    config_path: str = "battery_config.yaml",
    em_step: int = 3,
    log: logging.Logger | None = None,
) -> Dict[str, Any]:
    """전체 모델을 한번에 생성.

    Args:
        em_step: EM 단계 (1=Randles만, 2=+ISC, 3=전체). generate_em_randles.py에 전달.

    Returns:
        결과 요약 dict
    """
    log = log or logger
    t0 = time.time()
    results = {"ok": [], "fail": [], "skipped": []}

    log.info("=" * 70)
    log.info("FULL MODEL GENERATION")
    log.info("  Types: %s | Tiers: %s | Phases: %s", model_types, tiers, phases)
    log.info("=" * 70)

    # ── Step 1: Materials (type-independent core) ──
    log.info("\n[1/9] Materials")
    from generate_materials import generate_materials, generate_materials_tempdep, generate_thermal_expansion
    try:
        generate_materials(config, log=log)
        generate_materials_tempdep(config, log=log)
        results["ok"].extend(["04_materials.k", "04_materials_tempdep.k"])
    except Exception as e:
        log.error("Materials 생성 실패: %s", e)
        results["fail"].append("04_materials*.k")

    # Thermal expansion (model-type × tier specific)
    for mt in model_types:
        for tier in tiers:
            try:
                out = generate_thermal_expansion(config, model_type=mt, tier=tier, log=log)
                results["ok"].append(Path(out).name)
            except Exception as e:
                log.error("Thermal expansion %s tier %s 실패: %s", mt, tier, e)
                results["fail"].append(f"04_materials_expansion_{mt}.k")

    # ── Step 2: Boundary conditions (phase-dependent, type-independent) ──
    log.info("\n[2/9] Boundary Conditions")
    from generate_boundary_loads import generate_boundary_loads
    for ph in phases:
        try:
            f = generate_boundary_loads(config, phase=ph, log=log)
            results["ok"].append(Path(f).name)
        except Exception as e:
            log.error("BC Phase %d 실패: %s", ph, e)
            results["fail"].append(f"06_boundary_loads_phase{ph}.k")

    # ── Step 3: Control (phase-dependent) ──
    log.info("\n[3/9] Control")
    from generate_control import generate_control
    for ph in phases:
        try:
            f = generate_control(config, phase=ph, log=log)
            results["ok"].append(Path(f).name)
        except Exception as e:
            log.error("Control Phase %d 실패: %s", ph, e)
            results["fail"].append(f"07_control_phase{ph}.k")

    # ── Step 4: Database (phase-dependent) ──
    log.info("\n[4/9] Database")
    from generate_database import generate_database
    for ph in phases:
        try:
            f = generate_database(config, phase=ph, log=log)
            results["ok"].append(Path(f).name)
        except Exception as e:
            log.error("Database Phase %d 실패: %s", ph, e)

    # ── Step 5: Curves (phase-dependent) ──
    log.info("\n[5/9] Curves")
    from generate_curves import generate_curves
    for ph in phases:
        try:
            f = generate_curves(config, phase=ph, log=log)
            results["ok"].append(Path(f).name)
        except Exception as e:
            log.error("Curves Phase %d 실패: %s", ph, e)

    # ── Step 6: Mesh + Contacts + EM (type × tier dependent) ──
    log.info("\n[6/9] Mesh + Contacts + EM Randles")
    for mt in model_types:
        for tier in tiers:
            tier_str = str(tier) if tier != int(tier) else str(int(tier))
            log.info("  --- %s Tier %s ---", mt, tier_str)

            # Mesh
            mesh_script = "generate_mesh_stacked.py" if mt == "stacked" else "generate_mesh_wound.py"
            ok = _call_generator(mesh_script, [
                "--config", config_path, "--tier", tier_str,
            ], log)
            if ok:
                prefix = "02_mesh_stacked" if mt == "stacked" else "03_mesh_wound"
                results["ok"].append(f"{prefix}{tier_to_suffix(tier)}.k")
            else:
                results["fail"].append(f"mesh_{mt}_{tier_str}")

            # Contacts (all phases)
            for ph in phases:
                ok = _call_generator("generate_contacts.py", [
                    "--config", config_path, "--tier", tier_str,
                    "--type", mt, "--phase", str(ph),
                ], log)
                if ok:
                    results["ok"].append(f"contacts_{mt}_phase{ph}")
                else:
                    results["fail"].append(f"contacts_{mt}_phase{ph}")

            # EM Randles (stacked: config+tier, wound: --model-type wound)
            if mt == "stacked":
                em_args = [
                    "--config", config_path, "--tier", tier_str,
                    "--model-type", "stacked",
                ]
                if em_step != 3:
                    em_args += ["--em-step", str(em_step)]
                ok = _call_generator("generate_em_randles.py", em_args, log)
                if ok:
                    results["ok"].append(f"em_randles_stacked_tier{tier_str}")
                else:
                    results["fail"].append(f"em_randles_stacked_tier{tier_str}")
            else:  # wound
                em_args = ["--model-type", "wound"]
                if em_step != 3:
                    em_args += ["--em-step", str(em_step)]
                ok = _call_generator("generate_em_randles.py", em_args, log)
                if ok:
                    results["ok"].append("em_randles_wound")
                else:
                    results["fail"].append("em_randles_wound")

    # ── Step 7: Main files ──
    log.info("\n[7/9] Main Files")
    from generate_main import generate_main, generate_main_master
    for mt in model_types:
        for tier in tiers:
            for ph in phases:
                # 비활성 버전 (기본)
                try:
                    generate_main(config, phase=ph, model_type=mt,
                                  tier=tier, ale=False, log=log)
                    results["ok"].append(f"main_phase{ph}_{mt}")
                except Exception as e:
                    log.error("Main Phase %d %s 실패: %s", ph, mt, e)
                    results["fail"].append(f"main_phase{ph}_{mt}")

                # ALE 활성화 버전 (Phase 3 전용)
                if ph >= 3:
                    try:
                        generate_main(config, phase=ph, model_type=mt,
                                      tier=tier, ale=True, log=log)
                        results["ok"].append(f"main_phase{ph}_{mt}_ale")
                    except Exception as e:
                        log.error("Main Phase %d %s ALE 실패: %s", ph, mt, e)
                        results["fail"].append(f"main_phase{ph}_{mt}_ale")

            # Master files: 01_main.k (비활성) + 01_main_ale.k (활성)
            for ale_flag in (False, True):
                try:
                    generate_main_master(config, model_type=mt,
                                         tier=tier, ale=ale_flag, log=log)
                    label = "01_main_ale.k" if ale_flag else "01_main.k"
                    results["ok"].append(f"{label} ({mt})")
                except Exception as e:
                    log.error("Main master %s ale=%s 실패: %s", mt, ale_flag, e)

    # ── Step 8: Gas Expansion Scenario ──
    log.info("\n[8/9] Gas Expansion Scenario")
    from generate_boundary_loads import generate_boundary_loads
    from generate_control import generate_control
    from generate_curves import generate_curves
    from generate_gas_standalone import generate_gas_standalone
    from generate_venting import generate_venting
    from generate_main import generate_main_scenario

    try:
        generate_boundary_loads(config, scenario="gas", log=log)
        results["ok"].append("06_boundary_loads_gas.k")
    except Exception as e:
        log.error("Gas BC 생성 실패: %s", e)
        results["fail"].append("06_boundary_loads_gas.k")

    try:
        generate_control(config, scenario="gas", log=log)
        results["ok"].append("07_control_gas.k")
    except Exception as e:
        log.error("Gas Control 생성 실패: %s", e)
        results["fail"].append("07_control_gas.k")

    try:
        generate_curves(config, scenario="gas", log=log)
        results["ok"].append("10_define_curves_gas.k")
    except Exception as e:
        log.error("Gas Curves 생성 실패: %s", e)
        results["fail"].append("10_define_curves_gas.k")

    try:
        generate_gas_standalone(config, log=log)
        results["ok"].append("16_gas_generation_standalone.k")
    except Exception as e:
        log.error("Gas Standalone 생성 실패: %s", e)
        results["fail"].append("16_gas_generation_standalone.k")

    try:
        generate_venting(config, log=log)
        results["ok"].append("12_venting.k")
    except Exception as e:
        log.error("Venting 생성 실패: %s", e)
        results["fail"].append("12_venting.k")

    for mt in model_types:
        for tier in tiers:
            tier_suf = tier_to_suffix(tier)
            for ale_flag in (False, True):
                ale_suf = "_ale" if ale_flag else ""
                fname = f"01_main_gas_{mt}{tier_suf}{ale_suf}.k"
                try:
                    generate_main_scenario(config, scenario="gas",
                                           model_type=mt, tier=tier,
                                           ale=ale_flag, log=log)
                    results["ok"].append(fname)
                except Exception as e:
                    log.error("Main gas %s tier%s %s 실패: %s",
                               mt, tier_suf, "ale" if ale_flag else "", e)
                    results["fail"].append(fname)

    # ── Step 9: Swelling Scenario ──
    log.info("\n[9/9] Swelling Scenario")
    from generate_intercalation_strain import generate_intercalation_strain
    from generate_sei_growth import generate_sei_growth

    try:
        generate_boundary_loads(config, scenario="swelling", log=log)
        results["ok"].append("06_boundary_loads_swelling.k")
    except Exception as e:
        log.error("Swelling BC 생성 실패: %s", e)
        results["fail"].append("06_boundary_loads_swelling.k")

    try:
        generate_control(config, scenario="swelling", log=log)
        results["ok"].append("07_control_swelling.k")
    except Exception as e:
        log.error("Swelling Control 생성 실패: %s", e)
        results["fail"].append("07_control_swelling.k")

    try:
        generate_curves(config, scenario="swelling", log=log)
        results["ok"].append("10_define_curves_swelling.k")
    except Exception as e:
        log.error("Swelling Curves 생성 실패: %s", e)
        results["fail"].append("10_define_curves_swelling.k")

    for mt in model_types:
        for tier in tiers:
            tier_suf = tier_to_suffix(tier)
            try:
                generate_intercalation_strain(config, tier=tier,
                                              model_type=mt, log=log)
                results["ok"].append(f"14_intercalation_strain{tier_suf}.k ({mt})")
            except Exception as e:
                log.error("Intercalation strain %s tier%s 실패: %s", mt, tier_suf, e)
                results["fail"].append(f"intercalation_{mt}{tier_suf}")

            try:
                generate_sei_growth(config, tier=tier, model_type=mt, log=log)
                results["ok"].append(f"15_sei_growth{tier_suf}.k ({mt})")
            except Exception as e:
                log.error("SEI growth %s tier%s 실패: %s", mt, tier_suf, e)
                results["fail"].append(f"sei_growth_{mt}{tier_suf}")

            fname = f"01_main_swelling_{mt}{tier_suf}.k"
            try:
                generate_main_scenario(config, scenario="swelling",
                                       model_type=mt, tier=tier, log=log)
                results["ok"].append(fname)
            except Exception as e:
                log.error("Main swelling %s tier%s 실패: %s", mt, tier_suf, e)
                results["fail"].append(fname)

    # ── Summary ──
    elapsed = time.time() - t0
    log.info("\n" + "=" * 70)
    log.info("GENERATION COMPLETE")
    log.info("  OK:      %d files", len(results["ok"]))
    log.info("  FAILED:  %d files", len(results["fail"]))
    log.info("  Time:    %.1f s", elapsed)
    if results["fail"]:
        log.warning("  Failed items: %s", results["fail"])
    log.info("=" * 70)

    return results


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 배터리 전체 모델 원클릭 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # YAML 기본값으로 tier -1 적층형 전체 생성
  python generate_full_model.py --type stacked --tier -1

  # 외곽 사이즈 + 용량 오버라이드
  python generate_full_model.py --width 80 --height 160 --capacity 3.5 --type stacked --tier 0

  # 양쪽 타입 + 다중 tier
  python generate_full_model.py --type both --tier -1 0
""")
    add_common_args(parser)
    parser.add_argument("--type", choices=["stacked", "wound", "both"],
                        default="stacked", help="모델 타입 (기본: stacked)")
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (기본: 1 2 3)")

    # Override args
    parser.add_argument("--width", type=float, default=None,
                        help="셀 가로 mm (YAML 오버라이드)")
    parser.add_argument("--height", type=float, default=None,
                        help="셀 세로 mm (YAML 오버라이드)")
    parser.add_argument("--capacity", type=float, default=None,
                        help="셀 용량 Ah (YAML 오버라이드, n_cells 자동 계산)")
    parser.add_argument("--areal-capacity", type=float, default=3.5,
                        help="전극 면적당 용량 mAh/cm^2 (기본: 3.5)")
    parser.add_argument("--em-step", type=int, default=3, choices=[1, 2, 3],
                        help="EM 단계 (1=Randles만, 2=+ISC, 3=전체, 기본: 3)")

    args = parser.parse_args()

    log = setup_logger("full_model",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)

    config = load_config(args.config, validate=True, logger=log)

    # Apply overrides
    config = _override_config(
        config,
        width=args.width,
        height=args.height,
        capacity=args.capacity,
        areal_cap=args.areal_capacity,
    )

    # Show computed parameters
    for mt in (["stacked", "wound"] if args.type == "both" else [args.type]):
        geo = get_geometry(config, mt)
        log.info("모델: %s | W=%.1f H=%.1f | UC두께=%.3fmm | 기본n=%d",
                 mt, geo["width"], geo["height"],
                 geo["unit_cell_thickness"], geo["n_cells_default"])

    types = ["stacked", "wound"] if args.type == "both" else [args.type]
    tiers = [args.tier] if isinstance(args.tier, (int, float)) else args.tier

    results = generate_full_model(
        config=config,
        model_types=types,
        tiers=tiers,
        phases=args.phase,
        config_path=args.config,
        em_step=args.em_step,
        log=log,
    )

    if results["fail"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
