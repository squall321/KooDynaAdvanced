#!/usr/bin/env python3
"""
06_boundary_loads*.k 자동 생성 (Phase 1/2/3)
=============================================
battery_config.yaml의 boundary_conditions + impactor 설정에서
SPC, 임팩터 속도, 대류/복사, 초기 온도를 생성.

사용법:
    python generate_boundary_loads.py --config battery_config.yaml
    python generate_boundary_loads.py --phase 1
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, get_scenario_params,
)

logger = logging.getLogger(__name__)

_TITLES = {
    1: "Li-ion Cell - Boundary Conditions (Phase 1: Mechanical Only)",
    2: "Li-ion Cell - Boundary Conditions (Phase 2: Thermo-Mechanical)",
    3: "Li-ion Cell - Boundary Conditions, Loads, Initial Conditions",
}

_SCENARIO_TITLES = {
    "swelling": "Li-ion Cell - Boundary Conditions (Swelling Scenario)",
    "gas":      "Li-ion Cell - Boundary Conditions (Gas Expansion Scenario)",
}


def _write_spc(f, nsid: int = 1) -> None:
    f.write("$\n$ ==================== SPC ====================\n$\n")
    f.write("*BOUNDARY_SPC_SET\n")
    f.write("$     NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ\n")
    f.write(f"{nsid:>10d}         0         1         1         1         1         1         1\n")
    f.write("$\n")


def _write_impactor_motion(f, lcid: int = 3001, nsid: int = 2) -> None:
    f.write("$ ==================== Impactor ====================\n$\n")
    f.write("*BOUNDARY_PRESCRIBED_MOTION_SET\n")
    f.write("$     NSID       DOF       VAD      LCID        SF       VID     DEATH     BIRTH\n")
    f.write(f"{nsid:>10d}         1         0{lcid:>10d}      -1.0         0  1.0E+28       0.0\n")
    f.write("$\n")


def _write_thermal_bc(f, config: Dict[str, Any]) -> None:
    """대류 + 복사 + 초기온도"""
    bc = config.get("boundary_conditions", {})
    T0 = bc.get("initial_conditions", {}).get("temperature", 298.15)
    h_conv = 5.0e-6   # W/(mm^2·K) = 5 W/(m^2·K)
    sigma_rad = 5.670e-14  # Stefan-Boltzmann in mm units

    # Segment set for pouch exterior
    f.write("$ ==================== Segment Set (Pouch exterior) ====================\n$\n")
    f.write("*SET_SEGMENT_GENERAL\n")
    f.write("$      SID       DA1       DA2       DA3       DA4\n")
    f.write("         3       0.0       0.0       0.0       0.0\n")
    f.write("$   OPTION        E1        E2        E3\n")
    f.write("      PART        10        11        12\n")
    f.write("$\n")

    # Convection
    f.write("$ ==================== Convection ====================\n$\n")
    f.write("*BOUNDARY_CONVECTION_SET\n")
    f.write("$     SSID    PSEROD\n")
    f.write("         3         0\n")
    f.write("$    HLCID     HMULT     TLCID     TMULT       LOC\n")
    f.write(f"         0{h_conv:>10.1E}         0{T0:>10.2f}         0\n")
    f.write("$\n")

    # Radiation
    f.write("$ ==================== Radiation ====================\n$\n")
    f.write("*BOUNDARY_RADIATION_SET\n")
    f.write("$     SSID      TYPE                                    PSEROD\n")
    f.write("         3         1                                         0\n")
    f.write("$    FLCID     FMULT     TLCID     TMULT       LOC\n")
    f.write(f"         0{sigma_rad:>10.3E}         0{T0:>10.2f}         0\n")
    f.write("$\n")

    # Initial temperature
    f.write("$ ==================== Initial Temperature ====================\n$\n")
    f.write("*INITIAL_TEMPERATURE_SET\n")
    f.write("$     NSID      TEMP       LOC\n")
    f.write(f"         0{T0:>10.2f}         0\n")
    f.write("$\n")


def _write_heat_flux_bc(f, config: Dict[str, Any]) -> None:
    """외부 히터 열플럭스 BC (가스팽창 시나리오 전용).

    두 개의 BOUNDARY_HEAT_SET으로 구성:
      1) HLCID=9010  : 강제대류 열플럭스 vs 시간 (10_define_curves_gas.k)
      2) HLCID=-9011 : 복사 열플럭스 보정 q_rad(T) = eps*sigma*(T^4-T_amb^4)
                       (16_gas_generation_standalone.k, FUNCTID 9011)
    두 항이 SID=3 세그먼트에 합산 적용됨.
    단위: mJ/(s·mm²) = 10⁻³ W/mm²
    """
    sp = get_scenario_params(config, "gas")
    hs = sp.get("heat_source", {})
    q_density = hs.get("heat_flux_density", 5000.0) * 1.0e-3  # W/m² → mJ/(s·mm²)

    f.write("$ ==================== External Heat Flux (Gas Scenario) ====================\n$\n")
    f.write(f"$ Total: q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID 9011]\n")
    f.write(f"$ q_conv_max = {hs.get('heat_flux_density', 5000.0):.0f} W/m^2"
            f" = {q_density:.4E} mJ/(s*mm^2)\n")
    f.write("$\n")

    f.write("$ --- 1. Forced convection (time-history) ---\n")
    f.write("*BOUNDARY_HEAT_SET\n")
    f.write("$     SSID    PSEROD\n")
    f.write("         3         0\n")
    f.write("$    HLCID     HMULT     TLCID     TMULT       LOC\n")
    f.write("      9010       1.0         0       0.0         0\n")
    f.write("$\n")

    f.write("$ --- 2. Radiation correction (temperature-dependent, FUNCTID 9011) ---\n")
    f.write("$ q_rad(T) = eps*sigma_SB*(T^4 - T_amb^4)  [mJ/(s*mm^2)]\n")
    f.write("*BOUNDARY_HEAT_SET\n")
    f.write("$     SSID    PSEROD\n")
    f.write("         3         0\n")
    f.write("$    HLCID     HMULT     TLCID     TMULT       LOC\n")
    f.write("     -9011       1.0         0       0.0         0\n")
    f.write("$\n")


def generate_boundary_loads(config: Dict[str, Any], phase: int = 3,
                            scenario: str = "impact",
                            output: str | None = None,
                            log: logging.Logger | None = None) -> str:
    """경계조건 k-file 생성.

    Args:
        scenario: 'impact' (기본, phase 1/2/3) | 'swelling' | 'gas'
                  시나리오별 분기: impact=임팩터+SPC, swelling=SPC+열,
                  gas=SPC+열+외부히터
    """
    log = log or logger

    if scenario != "impact":
        # 시나리오 모드: phase 인수 무시, 독립 파일 생성
        if output is None:
            output = f"06_boundary_loads_{scenario}.k"
        outpath = Path(output)
        title = _SCENARIO_TITLES[scenario]

        with open(outpath, "w", encoding="utf-8") as f:
            write_kfile_header(f, title)
            f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")
            f.write(f"$ Scenario: {scenario.upper()} — 임팩터 없음, 스웰링/가스 전용 BC\n$\n")

            # SPC: 하단 고정 (impact와 동일)
            _write_spc(f)

            # 열 BC: 항상 포함 (swelling/gas 모두 열 해석)
            _write_thermal_bc(f, config)

            if scenario == "gas":
                _write_heat_flux_bc(f, config)
            elif scenario == "swelling":
                f.write("$ ==================== Swelling Note ====================\n$\n")
                f.write("$ 임팩터 BC 없음. 인터칼레이션 변형은 14_intercalation_strain.k 에서\n")
                f.write("$ BOUNDARY_PRESCRIBED_MOTION_SET (NSID=1002, DOF=3, VAD=2) 로 적용됨.\n")
                f.write("$\n")

            f.write("*END\n")

        log.info("경계조건 생성 완료: %s (Scenario: %s)", outpath, scenario)
        return str(outpath)

    # ── Impact 시나리오 (기존 로직 그대로) ──
    if output is None:
        suffix = f"_phase{phase}" if phase < 3 else ""
        output = f"06_boundary_loads{suffix}.k"
    outpath = Path(output)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f, _TITLES.get(phase, _TITLES[3]))
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        _write_spc(f)
        _write_impactor_motion(f)

        if phase >= 2:
            _write_thermal_bc(f, config)

        f.write("*END\n")

    log.info("경계조건 생성 완료: %s (Phase %d)", outpath, phase)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(description="06_boundary_loads*.k 생성")
    add_common_args(parser)
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (1, 2, 3)")
    parser.add_argument("--scenario", choices=["impact", "swelling", "gas"],
                        default="impact", help="시나리오 (기본: impact)")
    args = parser.parse_args()

    log = setup_logger("gen_bc",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)

    if args.scenario != "impact":
        generate_boundary_loads(config, scenario=args.scenario, log=log)
    else:
        for ph in args.phase:
            generate_boundary_loads(config, phase=ph, log=log)


if __name__ == "__main__":
    main()
