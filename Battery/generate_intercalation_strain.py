#!/usr/bin/env python3
"""
14_intercalation_strain.k 자동 생성
=====================================
인터칼레이션 + SEI 성장 유발 스웰링 경계조건 k-file 생성.

물리 모델:
  • 인터칼레이션 변형 (가역): d_interc(SOC) = n_uc × (2·t_an·CTE_gr + 2·t_ca·CTE_NMC) × SOC
  • SEI 성장 (비가역):        d_SEI(t)    ≈ n_uc × L_an × (A_pre·√t·exp(-Ea/RT)) / L_an
                                           = n_uc × A_pre·√t·exp(-Ea/RT)  [mm 단위 변환]

구현:
  - CC-CV 사이클 SOC 프로파일로부터 시간-변위 DEFINE_CURVE 9001 생성
  - SEI 기여분을 누적 오프셋으로 DEFINE_CURVE 9001에 합산
  - BOUNDARY_PRESCRIBED_MOTION_SET: NSID=1002 (전극 스택 상단), DOF=3(Z), VAD=2(displacement)

사용법:
    python generate_intercalation_strain.py --config battery_config.yaml --tier -1
    python generate_intercalation_strain.py --tier 0 --type stacked
"""
from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, write_curve,
    get_geometry, get_n_cells_for_tier, get_scenario_params,
)

logger = logging.getLogger(__name__)


def _compute_swelling_curve(
    config: Dict[str, Any],
    n_cells: int,
    model_type: str = "stacked",
) -> List[Tuple[float, float]]:
    """시간-변위 커브 계산 (CC-CV 다중 사이클 + SEI 비가역 성장).

    Returns:
        [(time_s, displacement_mm), ...] 포인트 목록
    """
    geo = get_geometry(config, model_type)
    t_anode   = geo["t_anode"]    # mm (편면)
    t_cathode = geo["t_cathode"]  # mm (편면)

    sp    = get_scenario_params(config, "swelling")
    interc = sp.get("intercalation", {})
    sei    = sp.get("sei_growth", {})
    c_ch   = sp.get("c_rate_charge", 0.5)
    c_dis  = sp.get("c_rate_discharge", 1.0)
    n_cyc  = sp.get("n_cycles", 2)
    end_t  = sp.get("end_time", 7200.0)

    cte_gr  = interc.get("graphite_cte", 0.035)   # 흑연 인터칼레이션 선형 변형률
    cte_nmc = interc.get("nmc_cte", 0.015)         # NMC 인터칼레이션 선형 변형률

    # SEI 파라미터
    A_pre   = sei.get("pre_exponential", 1.5e-6)   # m/√s
    Ea      = sei.get("activation_energy", 40000)   # J/mol
    T_ref   = 313.15                                # K (40°C, 보수적 기준)
    R_gas   = 8.314
    # SEI 성장량 (m) → mm 단위 변환, n_cells 스택 전체 기여
    # 각 UC의 anode 양면(2×t_anode mm) 대비 SEI 두께 변형률 = δ_SEI / L_an_meter
    L_an_m  = 2.0 * t_anode * 1.0e-3              # m (양면 anode 두께)
    sei_rate = A_pre * math.exp(-Ea / (R_gas * T_ref))  # m/√s at T_ref

    def d_sei_mm(t_s: float) -> float:
        """SEI 기여 변위 (mm): 누적값"""
        delta_m = A_pre * math.sqrt(max(t_s, 0.0)) * math.exp(-Ea / (R_gas * T_ref))
        strain  = delta_m / L_an_m if L_an_m > 0 else 0.0
        return n_cells * L_an_m * 1.0e3 * strain  # mm

    # 최대 인터칼레이션 변위 (SOC=1.0 기준)
    d_max_mm = n_cells * (2.0 * t_anode * cte_gr + 2.0 * t_cathode * cte_nmc)

    # 초기 SOC
    em   = config.get("em_randles", {})
    soc0 = em.get("cell_parameters", {}).get("initial_soc", 0.5)

    # 각 사이클의 소요 시간 계산
    # 1번째 사이클: charge (soc0 → 1.0) + cv + discharge (1.0 → 0.0)
    # 이후 사이클:  charge (0.0 → 1.0) + cv + discharge (1.0 → 0.0)
    t_ch1   = (1.0 - soc0) / c_ch * 3600.0   # s (첫 충전, SOC_0→1.0)
    t_cv1   = t_ch1 * 0.05                    # s (CV 단계 근사)
    t_dis   = 1.0 / c_dis * 3600.0            # s (방전, 1.0→0.0)
    t_ch_n  = 1.0 / c_ch * 3600.0             # s (2번째 이후 충전, 0.0→1.0)
    t_cv_n  = t_ch_n * 0.05

    points: List[Tuple[float, float]] = []
    t = 0.0
    soc = soc0

    for cyc in range(n_cyc):
        t_ch  = t_ch1  if cyc == 0 else t_ch_n
        t_cv  = t_cv1  if cyc == 0 else t_cv_n
        soc_start = soc

        # ── 충전 시작 ──
        d0 = soc_start * d_max_mm + d_sei_mm(t)
        points.append((round(t, 4), round(d0, 8)))

        # ── CC 충전 끝 (SOC → 1.0) ──
        t += t_ch
        if t > end_t:
            t = end_t
            soc = soc_start + (1.0 - soc_start) * (t - points[-1][0]) / t_ch
            d = soc * d_max_mm + d_sei_mm(t)
            points.append((round(t, 4), round(d, 8)))
            break
        soc = 1.0
        d = soc * d_max_mm + d_sei_mm(t)
        points.append((round(t, 4), round(d, 8)))

        # ── CV 단계 (SOC ≈ 1.0 유지, 테이퍼) ──
        t += t_cv
        if t > end_t:
            t = end_t
        d = soc * d_max_mm + d_sei_mm(t)
        points.append((round(t, 4), round(d, 8)))

        # ── CC 방전 (SOC → 0.0) ──
        t_dis_end = t + t_dis
        if t_dis_end > end_t:
            # 부분 방전
            frac = (end_t - t) / t_dis
            t = end_t
            soc = max(0.0, 1.0 - frac)
            d = soc * d_max_mm + d_sei_mm(t)
            points.append((round(t, 4), round(d, 8)))
            break
        t = t_dis_end
        soc = 0.0
        d = soc * d_max_mm + d_sei_mm(t)
        points.append((round(t, 4), round(d, 8)))

        if t >= end_t:
            break

    # end_time 보장
    if points and points[-1][0] < end_t:
        last_d = points[-1][1]
        points.append((end_t, last_d))

    return points


def generate_intercalation_strain(
    config: Dict[str, Any],
    tier: float = -1,
    model_type: str = "stacked",
    output: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """14_intercalation_strain.k 생성.

    인터칼레이션 + SEI 성장 유발 스웰링 경계조건.
    BOUNDARY_PRESCRIBED_MOTION_SET 으로 전극 스택 상단 면에 Z변위 부여.
    """
    log = log or logger
    if output is None:
        output = "14_intercalation_strain.k"
    outpath = Path(output)

    n_cells = get_n_cells_for_tier(config, tier, model_type)
    geo     = get_geometry(config, model_type)
    sp      = get_scenario_params(config, "swelling")
    interc  = sp.get("intercalation", {})
    cte_gr  = interc.get("graphite_cte", 0.035)
    cte_nmc = interc.get("nmc_cte", 0.015)
    d_max   = n_cells * (2.0 * geo["t_anode"] * cte_gr + 2.0 * geo["t_cathode"] * cte_nmc)
    end_t   = sp.get("end_time", 7200.0)

    points = _compute_swelling_curve(config, n_cells, model_type)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(
            f,
            "Li-ion Intercalation Strain + SEI Swelling BC",
            description=(
                "Swelling scenario: prescribed displacement on electrode stack top\n"
                f"n_cells={n_cells}, CTE_graphite={cte_gr:.3f}, CTE_NMC={cte_nmc:.3f}\n"
                f"d_max(SOC=1) = {d_max:.4f} mm, end_time = {end_t:.0f} s"
            ),
        )
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        write_separator(f, "INTERCALATION + SEI DISPLACEMENT CURVE (LCID 9001)")
        f.write("$ x = time [s], y = displacement [mm] (Z-direction, stack growth)\n")
        f.write("$ Displacement = intercalation(SOC) + SEI_growth(t,T_ref=313K)\n")
        f.write(f"$ d_max_intercalation = {d_max:.6f} mm at SOC=1.0\n")
        f.write("$\n")
        write_curve(f, 9001,
                    "Swelling Displacement vs Time (Intercalation + SEI)",
                    points)
        f.write("$\n")

        write_separator(f, "BOUNDARY PRESCRIBED MOTION — STACK TOP (NSID=1002)")
        f.write("$ NSID=1002: electrode stack top-face node set\n")
        f.write("$ DOF=3: Z-direction (thickness, stack growth direction)\n")
        f.write("$ VAD=2: displacement-controlled\n")
        f.write("$ LCID=9001: swelling displacement curve (above)\n")
        f.write("$\n")
        f.write("*BOUNDARY_PRESCRIBED_MOTION_SET\n")
        f.write("$     NSID       DOF       VAD      LCID        SF       VID     DEATH     BIRTH\n")
        f.write(f"      1002         3         2      9001       1.0         0  1.0E+28       0.0\n")
        f.write("$\n")

        f.write("*END\n")

    log.info("인터칼레이션 변형 파일 생성 완료: %s (n_cells=%d, d_max=%.4f mm)",
             outpath, n_cells, d_max)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(
        description="14_intercalation_strain.k 생성 (스웰링 시나리오 BC)")
    add_common_args(parser)
    parser.add_argument("--type", choices=["stacked", "wound"],
                        default="stacked", help="모델 타입 (기본: stacked)")
    args = parser.parse_args()

    log = setup_logger("gen_intercalation",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)
    generate_intercalation_strain(config, tier=args.tier, model_type=args.type, log=log)


if __name__ == "__main__":
    main()
