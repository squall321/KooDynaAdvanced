#!/usr/bin/env python3
"""
10_define_curves*.k 자동 생성 (Phase 1/2/3)
============================================
battery_config.yaml의 em_randles/impactor 설정에서 커브 데이터를 생성.

Phase 1: 전극 crush + 임팩터 속도 (LCID 1001, 1002, 3001)
Phase 2: Phase 1 + (동일, EM 불필요)
Phase 3: 전체 — OCV, dU/dT, 방전 전류, 단락 저항+함수, 열폭주 함수

사용법:
    python generate_curves.py --config battery_config.yaml
    python generate_curves.py --phase 1
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, TextIO

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, write_curve, fmt16,
    get_scenario_params, get_geometry, get_n_cells_for_tier,
)

logger = logging.getLogger(__name__)

_TITLES = {
    1: "Li-ion Cell - Load Curves (Phase 1: Mechanical Only)",
    2: "Li-ion Cell - Load Curves (Phase 2: Thermo-Mechanical)",
    3: "Li-ion Cell - Load Curves (Phase 3: Full Coupled)",
}

_SCENARIO_TITLES = {
    "swelling": "Li-ion Cell - Load Curves (Swelling Scenario)",
    "gas":      "Li-ion Cell - Load Curves (Gas Expansion Scenario)",
}

# ============================================================
# Curve data constants
# ============================================================

NMC_CRUSH = [
    (0.0, 0.0), (0.05, 5.0), (0.10, 15.0), (0.15, 35.0),
    (0.20, 70.0), (0.25, 130.0), (0.30, 250.0), (0.35, 500.0),
    (0.40, 1000.0), (0.45, 2000.0), (0.50, 4000.0),
]

GRAPHITE_CRUSH = [
    (0.0, 0.0), (0.05, 8.0), (0.10, 22.0), (0.15, 50.0),
    (0.20, 100.0), (0.25, 200.0), (0.30, 400.0), (0.35, 800.0),
    (0.40, 1500.0), (0.45, 3000.0), (0.50, 5000.0),
]

# NMC/Graphite OCV vs SOC(%) — typical discharge profile
OCV_VS_SOC = [
    (0.0, 3.000), (5.0, 3.300), (10.0, 3.450), (20.0, 3.550),
    (30.0, 3.600), (40.0, 3.640), (50.0, 3.680), (60.0, 3.750),
    (70.0, 3.850), (80.0, 3.950), (90.0, 4.080), (95.0, 4.150),
    (100.0, 4.200),
]

# dU/dT (entropy coefficient, V/K) vs SOC(%)
DUDT_VS_SOC = [
    (0.0, -1.0e-4), (10.0, -5.0e-5), (20.0, 5.0e-5),
    (30.0, 1.5e-4), (40.0, 2.5e-4), (50.0, 3.0e-4),
    (60.0, 2.0e-4), (70.0, 1.0e-4), (80.0, -5.0e-5),
    (90.0, -1.5e-4), (100.0, -2.0e-4),
]

# Separator thickness vs short resistance
SEP_RESISTANCE = [
    (0.000, 1.0e-3), (0.005, 1.0e-3), (0.010, 1.0e-1),
    (0.015, 1.0e+1), (0.020, 1.0e+6), (1.000, 1.0e+9),
]

SOC_SHIFT = [(0.0, 0.0), (50.0, 5.0), (100.0, 10.0)]


def _write_impactor_velocity(f: TextIO, velocity_mm_s: float,
                             impact_time_s: float) -> None:
    """LCID 3001: impactor velocity curve"""
    ramp = impact_time_s
    data = [
        (0.0, velocity_mm_s),
        (ramp, velocity_mm_s),
        (ramp * 1.2, 0.0),
        (ramp * 2.0, 0.0),
    ]
    write_curve(f, 3001, "Impactor Velocity vs Time", data)


def _write_short_resistance_function(f: TextIO) -> None:
    """FUNCTID 5001: ISC resistance (// comments inside function body)"""
    f.write("$ FUNCTID 5001: ISC resistance function\n")
    f.write("*DEFINE_FUNCTION\n")
    f.write("      5001\n")
    f.write("""float resistance_short_randle(float time,
                             float x_sep, float y_sep, float z_sep,
                             float x_sen, float y_sen, float z_sen,
                             float x_ccp, float y_ccp, float z_ccp,
                             float x_ccn, float y_ccn, float z_ccn,
                             float pres, float rho, float vmstress,
                             float cond, float temp, float efstrain,
                             float ero)
{
    if (ero < 0.5) return -1.0;

    float distCC;
    distCC = sqrt(
        pow((x_ccp - x_ccn), 2.0) +
        pow((y_ccp - y_ccn), 2.0) +
        pow((z_ccp - z_ccn), 2.0));

    float distSEP;
    distSEP = sqrt(
        pow((x_sep - x_sen), 2.0) +
        pow((y_sep - y_sen), 2.0) +
        pow((z_sep - z_sen), 2.0));

    float R_base;
    if (distCC < 0.05)
        R_base = 0.0001;     // Type 4: Al-Cu
    else if (distCC < 0.15)
        R_base = 0.001;      // Type 2/3: Al-An or Ca-Cu
    else
        R_base = 0.010;      // Type 1: Ca-An

    float R_short;
    R_short = R_base * exp(-0.002 * (temp - 298.15));
    if (R_short < 0.00001) R_short = 0.00001;

    if (vmstress > 50.0)
        R_short = R_short * 50.0 / vmstress;

    return R_short;
}
""")
    f.write("$\n")


def _write_exothermic_function(f: TextIO) -> None:
    """FUNCTID 5002: thermal runaway Arrhenius chain"""
    f.write("$ FUNCTID 5002: exothermic reaction (5-stage Arrhenius)\n")
    f.write("*DEFINE_FUNCTION\n")
    f.write("      5002\n")
    f.write("""float exothermic_reaction_randle(float time, float temp,
                                 float SOC, float emdt,
                                 float ocv, float curr,
                                 float volt, float r0,
                                 float vc, float H_ex)
{
    float H_max = 1.0e5;
    if (H_ex > H_max) return 0.0;

    float R_gas = 8.314;
    float total_q = 0.0;

    // Stage 1: SEI decomposition (353K+)
    if (temp > 353.0)
    {
        float q1 = 1.67e15 * 257000.0 * exp(-135000.0 / (R_gas * temp));
        total_q = total_q + q1;
    }

    // Stage 2: Anode-electrolyte (393K+)
    if (temp > 393.0)
    {
        float q2 = SOC * 2.5e13 * 155000.0 * exp(-90000.0 / (R_gas * temp));
        total_q = total_q + q2;
    }

    // Stage 3: Electrolyte decomposition (423K+)
    if (temp > 423.0)
    {
        float q3 = 5.0e12 * 180000.0 * exp(-110000.0 / (R_gas * temp));
        total_q = total_q + q3;
    }

    // Stage 4: Cathode decomposition (473K+)
    if (temp > 473.0)
    {
        float q4 = (1.0 - SOC) * 6.67e13 * 115000.0 * exp(-100000.0 / (R_gas * temp));
        total_q = total_q + q4;
    }

    // Stage 5: Binder decomposition (523K+)
    if (temp > 523.0)
    {
        float q5 = 1.0e14 * 60000.0 * exp(-150000.0 / (R_gas * temp));
        total_q = total_q + q5;
    }

    return total_q;
}
""")
    f.write("$\n")


def _write_cc_cv_curves(f: TextIO, config: Dict[str, Any],
                        scenario_params: Dict[str, Any]) -> None:
    """스웰링 시나리오용 CC-CV 사이클 전류 커브 (LCID 9001/9002).

    LCID 9001: CC 충전 전류 (시간 → A)
    LCID 9002: CC 방전 전류 (시간 → A, 부호 반전)
    """
    em = config.get("em_randles", {})
    cap_Q = em.get("cell_parameters", {}).get("capacity_Q", 2.6)
    c_ch  = scenario_params.get("c_rate_charge", 0.5)
    c_dis = scenario_params.get("c_rate_discharge", 1.0)
    soc_0 = em.get("cell_parameters", {}).get("initial_soc", 0.5)

    I_charge    = cap_Q * c_ch         # A
    I_discharge = cap_Q * c_dis        # A
    t_charge    = (1.0 - soc_0) / c_ch * 3600.0   # s
    t_cv        = t_charge * 0.10      # CV 단계 근사 (CC의 10%)
    t_discharge = 1.0 / c_dis * 3600.0            # s

    # LCID 9001: 충전 전류 (양수 = 충전)
    cc_data = [
        (0.0,              I_charge),
        (t_charge,         I_charge),
        (t_charge + t_cv,  I_charge * 0.05),   # CV 테이퍼
        (t_charge + t_cv * 2, 0.0),
    ]
    write_curve(f, 9001, "CC-CV Charge Current vs Time (A)", cc_data)
    f.write("$\n")

    # LCID 9002: 방전 전류 (음수 = 방전)
    t0_dis = t_charge + t_cv * 2
    dis_data = [
        (t0_dis,                -I_discharge),
        (t0_dis + t_discharge,  -I_discharge),
        (t0_dis + t_discharge + 10.0, 0.0),
    ]
    write_curve(f, 9002, "CC Discharge Current vs Time (A)", dis_data)
    f.write("$\n")


def _write_heat_flux_curve(f: TextIO, scenario_params: Dict[str, Any]) -> None:
    """가스팽창 시나리오용 외부 열플럭스 커브 (LCID 9010).

    단위: mJ/(s·mm²) = 10³ W/m²
    5000 W/m² = 5.0 mJ/(s·mm²)
    """
    hs = scenario_params.get("heat_source", {})
    q_raw  = hs.get("heat_flux_density", 5000.0)    # W/m²
    q_mmK  = q_raw * 1.0e-3                          # mJ/(s·mm²)
    t_ramp = hs.get("ramp_time", 60.0)
    t_plat = hs.get("plateau_time", 3600.0)

    data = [
        (0.0,                    0.0),
        (t_ramp,                 q_mmK),
        (t_ramp + t_plat,        q_mmK),
        (t_ramp + t_plat + 10.0, 0.0),
    ]
    write_curve(f, 9010, f"External Heat Flux vs Time ({q_raw:.0f} W/m2 peak)", data)
    f.write("$\n")


def generate_curves(config: Dict[str, Any], phase: int = 3,
                    scenario: str = "impact",
                    output: str | None = None,
                    log: logging.Logger | None = None) -> str:
    """커브/함수 정의 k-file 생성.

    Args:
        scenario: 'impact' (기본, phase 1/2/3) | 'swelling' | 'gas'
    """
    log = log or logger

    # ── 시나리오 모드 ──
    if scenario != "impact":
        if output is None:
            output = f"10_define_curves_{scenario}.k"
        outpath = Path(output)
        sp = get_scenario_params(config, scenario)
        em = config.get("em_randles", {})
        cap_Q = em.get("cell_parameters", {}).get("capacity_Q", 2.6)

        with open(outpath, "w", encoding="utf-8") as f:
            write_kfile_header(f, _SCENARIO_TITLES[scenario])
            f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

            # 전극 crush 커브: 모든 시나리오 공통 (구조 재료 비선형)
            write_separator(f, "ELECTRODE CRUSH CURVES (Structural)")
            write_curve(f, 1001, "NMC Cathode Crush Stress vs Volumetric Strain", NMC_CRUSH)
            f.write("$\n")
            write_curve(f, 1002, "Graphite Anode Crush Stress vs Volumetric Strain", GRAPHITE_CRUSH)
            f.write("$\n")

            if scenario == "swelling":
                # 스웰링 시나리오: EM Randles 없음
                # → CC-CV 전류(LCID 9001/9002), OCV/dU/dT(2001/2002) 불필요
                # → 14_intercalation_strain.k 가 LCID 9001을 변위 BC로 사용하므로
                #   여기서 LCID 9001을 정의하면 충돌 발생 → 제외
                f.write("$ Swelling scenario: structural crush curves only.\n")
                f.write("$ CC-CV current / OCV / dU/dT curves excluded (no EM Randles).\n")
                f.write("$ Displacement BC (LCID 9001) is defined in 14_intercalation_strain.k.\n")
                f.write("$\n")

            elif scenario == "gas":
                # 외부 열플럭스 커브
                write_separator(f, "EXTERNAL HEAT FLUX CURVE (Gas Scenario)")
                _write_heat_flux_curve(f, sp)

                # EM 커브 재사용 (열폭주 연쇄반응 구동)
                write_separator(f, "OCV vs SOC")
                write_curve(f, 2001, "Open Circuit Voltage vs SOC", OCV_VS_SOC)
                f.write("$\n")
                write_separator(f, "dU/dT vs SOC (Entropy Coefficient)")
                write_curve(f, 2002, "Entropy Coefficient dU/dT vs SOC", DUDT_VS_SOC)
                f.write("$\n")

                # 외부 회로 전류 (초기 방전 상태 유지)
                write_separator(f, "EXTERNAL CIRCUIT (Gas Scenario: no forced discharge)")
                I_hold = cap_Q * 0.1  # 0.1C 유지 방전
                write_curve(f, 2003, "Hold Discharge Current vs Time",
                            [(0.0, I_hold), (3600.0, I_hold)])
                f.write("$\n")

                write_separator(f, "SEPARATOR RESISTANCE CURVE")
                write_curve(f, 5003, "Separator Thickness vs Short Resistance", SEP_RESISTANCE)
                f.write("$\n")

                write_separator(f, "ISC RESISTANCE FUNCTION (FUNCTID 5001)")
                _write_short_resistance_function(f)

                write_separator(f, "EXOTHERMIC REACTION (FUNCTID 5002)")
                _write_exothermic_function(f)

                write_separator(f, "SOC SHIFT CURVE")
                write_curve(f, 2004, "SOC Shift vs SOC", SOC_SHIFT)
                f.write("$\n")

                # FUNCTID 9013 제거: AIRBAG은 4인수 규약(time,temp,pressure,volume)만 지원.
                # 3인수(time,temp,soc)인 9013은 AIRBAG에 직접 연결 불가.
                # 실제 가스 발생은 12_venting.k의 FUNCTID 12010 (LCID=-12010)이 담당.

            f.write("*END\n")

        log.info("커브 파일 생성 완료: %s (Scenario: %s)", outpath, scenario)
        return str(outpath)

    # ── Impact 시나리오 (기존 로직 그대로) ──
    if output is None:
        suffix = f"_phase{phase}" if phase < 3 else ""
        output = f"10_define_curves{suffix}.k"
    outpath = Path(output)

    imp = config.get("impactor", {})
    vel = imp.get("velocity", 5000.0)
    em = config.get("em_randles", {})
    cap_Q = em.get("cell_parameters", {}).get("capacity_Q", 2.6)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f, _TITLES[phase])
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        write_separator(f, "ELECTRODE CRUSH CURVES")
        write_curve(f, 1001, "NMC Cathode Crush Stress vs Volumetric Strain", NMC_CRUSH)
        f.write("$\n")
        write_curve(f, 1002, "Graphite Anode Crush Stress vs Volumetric Strain", GRAPHITE_CRUSH)
        f.write("$\n")

        write_separator(f, "IMPACTOR VELOCITY CURVE")
        _write_impactor_velocity(f, vel, impact_time_s=0.005)
        f.write("$\n")

        if phase >= 3:
            write_separator(f, "OCV vs SOC")
            write_curve(f, 2001, "Open Circuit Voltage vs SOC", OCV_VS_SOC)
            f.write("$\n")

            write_separator(f, "dU/dT vs SOC (Entropy Coefficient)")
            write_curve(f, 2002, "Entropy Coefficient dU/dT vs SOC", DUDT_VS_SOC)
            f.write("$\n")

            write_separator(f, "EXTERNAL DISCHARGE CURRENT")
            I_half_C = cap_Q / 2.0
            discharge_data = [
                (0.0, 0.0), (0.001, I_half_C),
                (5.0, I_half_C), (10.0, 0.0),
            ]
            write_curve(f, 2003, "External Discharge Current vs Time", discharge_data)
            f.write("$\n")

            write_separator(f, "SEPARATOR RESISTANCE CURVE")
            write_curve(f, 5003, "Separator Thickness vs Short Resistance", SEP_RESISTANCE)
            f.write("$\n")

            write_separator(f, "ISC RESISTANCE FUNCTION (FUNCTID 5001)")
            _write_short_resistance_function(f)

            write_separator(f, "EXOTHERMIC REACTION (FUNCTID 5002)")
            _write_exothermic_function(f)

            write_separator(f, "SOC SHIFT CURVE")
            write_curve(f, 2004, "SOC Shift vs SOC", SOC_SHIFT)
            f.write("$\n")

        f.write("*END\n")

    log.info("커브 파일 생성 완료: %s (Phase %d)", outpath, phase)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(description="10_define_curves*.k 생성")
    add_common_args(parser)
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (1, 2, 3)")
    parser.add_argument("--scenario", choices=["impact", "swelling", "gas"],
                        default="impact", help="시나리오 (기본: impact)")
    args = parser.parse_args()

    log = setup_logger("gen_curves",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)

    if args.scenario != "impact":
        generate_curves(config, scenario=args.scenario, log=log)
    else:
        for ph in args.phase:
            generate_curves(config, phase=ph, log=log)


if __name__ == "__main__":
    main()
