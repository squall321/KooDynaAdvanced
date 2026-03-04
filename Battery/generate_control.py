#!/usr/bin/env python3
"""
07_control*.k 자동 생성 (Phase 1/2/3)
======================================
battery_config.yaml의 control 섹션에서 솔버 제어 카드를 생성.

Phase 1: 순수 구조 (SOTEFP=0, 5ms)
Phase 2: 구조+열 (SOTEFP=1, 10ms, erosion ON)
Phase 3: 구조+열+EM (SOTEFP=1, 60s, EM + REFINE)

사용법:
    python generate_control.py --config battery_config.yaml
    python generate_control.py --phase 1
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, get_scenario_params,
)

logger = logging.getLogger(__name__)

_TITLES = {
    1: "Li-ion Cell - Control Keywords (Phase 1: Mechanical Only)",
    2: "Li-ion Cell - Control Keywords (Phase 2: Thermo-Mechanical)",
    3: "Li-ion Cell - Control Keywords",
}

_SCENARIO_TITLES = {
    "swelling": "Li-ion Cell - Control Keywords (Swelling Scenario)",
    "gas":      "Li-ion Cell - Control Keywords (Gas Expansion Scenario)",
}

# Phase-specific defaults
_PHASE_PARAMS = {
    1: dict(endtim="5.0E-03", sotefp=0, dt2ms="       0.0", erode=1, endmas=0.10),
    2: dict(endtim="1.0E-02", sotefp=1, dt2ms="-1.00E-05", erode=1, endmas=0.10),
    3: dict(endtim="60.00",   sotefp=1, dt2ms="-1.00E-06", erode=1, endmas=0.0),
}

# Scenario-specific solver parameters
# swelling: 열+구조 연성, 장시간, 요소침식 불필요
# gas:      열+EM 완전연성, 열폭주 포함, 침식 ON (분리막 파손 추적)
_SCENARIO_PARAMS = {
    "swelling": dict(endtim="7200.0",  sotefp=1, dt2ms="-1.00E-06", erode=0, endmas=0.0),
    "gas":      dict(endtim="3600.0",  sotefp=1, dt2ms="-1.00E-06", erode=1, endmas=0.0),
}


def _write_termination(f, p: dict) -> None:
    f.write("$ ==================== Termination ====================\n$\n")
    f.write("*CONTROL_TERMINATION\n")
    f.write("$   ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS\n")
    endmas = p["endmas"]
    f.write(f"{p['endtim']:>10s}         0       0.0       0.0{endmas:>10.2f}\n")
    f.write("$\n")


def _write_solution(f, sotefp: int) -> None:
    f.write("$ ==================== Solution ====================\n$\n")
    f.write("*CONTROL_SOLUTION\n")
    f.write("$     SOTEFP    SOLVE     NL_EIGP     DC_IRE\n")
    f.write(f"         {sotefp}         0         0         0\n")
    f.write("$\n")


def _write_timestep(f, dt2ms: str, erode: int) -> None:
    f.write("$ ==================== Timestep ====================\n$\n")
    f.write("*CONTROL_TIMESTEP\n")
    f.write("$   DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS     LCTM     ERODE     MS1ST\n")
    f.write(f"       0.0      0.90         0  1.0E-08{dt2ms:>10s}         0         {erode}         0\n")
    f.write("$\n")


def _write_common_controls(f) -> None:
    """Hourglass, shell, solid, contact, energy, bulk viscosity."""
    f.write("$ ==================== Hourglass ====================\n")
    f.write("$ Global default only -- battery-specific HG via *HOURGLASS + HGID in mesh\n$\n")
    f.write("*CONTROL_HOURGLASS\n")
    f.write("$      IHQ        QH\n")
    f.write("         1      0.10\n")
    f.write("$\n")

    f.write("$ ==================== Shell ====================\n$\n")
    f.write("*CONTROL_SHELL\n")
    f.write("$   WRPANG     ESORT    IRNXX    ISTUPD    THEORY       BWC     MITER      PROJ\n")
    f.write("     20.0         1        -1         1         2         2         1         0\n")
    f.write("$ ROTASCL    INTGRD    LAMSHT    CSTYP6    THSHEL\n")
    f.write("       1.0         0         0         1         1\n")
    f.write("$\n")

    f.write("$ ==================== Solid ====================\n$\n")
    f.write("*CONTROL_SOLID\n")
    f.write("$    ESORT    FMATRX      NIPTETS   SWLOCL    PTEFP    NIPTSO\n")
    f.write("         1         0         0         0         0         0\n")
    f.write("$\n")

    f.write("$ ==================== Contact ====================\n$\n")
    f.write("*CONTROL_CONTACT\n")
    f.write("$   SLSFAC    RWPNAL    ISLCHK    SHLTHK    PENOPT    THKCHG     OTEFP    ENMASS\n")
    f.write("      0.10       0.0         2         1         1         0         1         0\n")
    f.write("$   USRSTR    USRFRC     NSBCS    INTERM     XPENE     SSTHK      ECDT   TIEDPRJ\n")
    f.write("         0         0        10         0       4.0         0         0         0\n")
    f.write("$\n")

    f.write("$ ==================== Energy ====================\n$\n")
    f.write("*CONTROL_ENERGY\n")
    f.write("$     HGEN      RWEN    SLNTEN     RYLEN\n")
    f.write("         2         2         2         2\n")
    f.write("$\n")

    f.write("$ ==================== Bulk Viscosity ====================\n$\n")
    f.write("*CONTROL_BULK_VISCOSITY\n")
    f.write("$       Q1        Q2      TYPE\n")
    f.write("      1.50      0.06         1\n")
    f.write("$\n")


def _write_thermal_solver(f) -> None:
    f.write("$ ==================== Thermal Solver ====================\n$\n")
    f.write("*CONTROL_THERMAL_SOLVER\n")
    f.write("         1         1        12 1.0000E-4         0       1.0      0.90       0.0\n")
    f.write("         0       5001.0000E-10 1.0000E-4       1.0                           1.0\n")
    f.write("*CONTROL_THERMAL_TIMESTEP\n")
    f.write("$#      ts       tip       its      tmin      tmax     dtemp      tscp      lcts\n")
    f.write("         0       0.5  1.00E-05       0.0       0.0       1.0       0.5         0\n")
    f.write("*CONTROL_THERMAL_NONLINEAR\n")
    f.write("        50   1.0E-04       0.5\n")
    f.write("$\n")


def _write_refine_solid(f) -> None:
    f.write("$ ==================== Solid Refinement ====================\n$\n")
    f.write("*CONTROL_REFINE_SOLID\n")
    f.write("$       ID      TYPE      NLVL      IBOX    IELOUT\n")
    f.write("       102         0         2         0         0\n")
    f.write("$   NTOTRF    NCYCRF    CRITRF     VALRF     BEGRF     ENDRF     LAYRF\n")
    f.write("      5000     0.001         3      25.0       0.0  1.0E+20         1\n")
    f.write("$    MAXRM    NCYCRM    CRITRM     VALRM     BEGRM     ENDRM\n")
    f.write("      1000     0.005         3      10.0      -0.10  1.0E+20\n")
    f.write("$\n")


def generate_control(config: Dict[str, Any], phase: int = 3,
                     scenario: str = "impact",
                     output: str | None = None,
                     log: logging.Logger | None = None) -> str:
    """솔버 제어 k-file 생성.

    Args:
        scenario: 'impact' (기본) | 'swelling' | 'gas'
                  시나리오 모드에서는 phase 인수 무시.
    """
    log = log or logger

    if scenario != "impact":
        # 시나리오 모드
        if output is None:
            output = f"07_control_{scenario}.k"
        outpath = Path(output)
        p = _SCENARIO_PARAMS[scenario]

        with open(outpath, "w", encoding="utf-8") as f:
            write_kfile_header(f, _SCENARIO_TITLES[scenario])
            f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")
            sp = get_scenario_params(config, scenario)
            end_time = sp.get("end_time", float(p["endtim"]))
            # end_time을 YAML에서 읽어 덮어쓰기
            p_used = dict(p)
            p_used["endtim"] = f"{end_time:.4E}" if end_time < 1.0 else f"{end_time:.2f}"

            _write_termination(f, p_used)
            _write_solution(f, p_used["sotefp"])
            _write_timestep(f, p_used["dt2ms"], p_used["erode"])
            _write_common_controls(f)
            # 열 솔버: swelling/gas 모두 열 해석 포함
            _write_thermal_solver(f)
            # 요소 세분화: 스웰링은 불필요, 가스는 선택적 (보수적으로 OFF)
            if scenario == "gas":
                _write_refine_solid(f)
            f.write("*END\n")

        log.info("제어 파일 생성 완료: %s (Scenario: %s)", outpath, scenario)
        return str(outpath)

    # ── Impact 시나리오 (기존 로직 그대로) ──
    if output is None:
        suffix = f"_phase{phase}" if phase < 3 else ""
        output = f"07_control{suffix}.k"
    outpath = Path(output)

    p = _PHASE_PARAMS[phase]

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f, _TITLES[phase])
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        _write_termination(f, p)
        _write_solution(f, p["sotefp"])
        _write_timestep(f, p["dt2ms"], p["erode"])
        _write_common_controls(f)

        if phase >= 2:
            _write_thermal_solver(f)
        # REFINE_SOLID: LS-DYNA Error 11087 — thermal solver와 비호환
        # Phase 3는 thermal solver가 필수이므로 REFINE_SOLID 비활성
        # if phase >= 3:
        #     _write_refine_solid(f)

        f.write("*END\n")

    log.info("제어 파일 생성 완료: %s (Phase %d)", outpath, phase)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(description="07_control*.k 생성")
    add_common_args(parser)
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (1, 2, 3)")
    parser.add_argument("--scenario", choices=["impact", "swelling", "gas"],
                        default="impact", help="시나리오 (기본: impact)")
    args = parser.parse_args()

    log = setup_logger("gen_ctrl",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)

    if args.scenario != "impact":
        generate_control(config, scenario=args.scenario, log=log)
    else:
        for ph in args.phase:
            generate_control(config, phase=ph, log=log)


if __name__ == "__main__":
    main()
