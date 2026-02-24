#!/usr/bin/env python3
"""
15_sei_growth.k 자동 생성
===========================
SEI 성장 독립 모듈 — 열화(aging) 연구 및 고온 사이클링 전용.

물리 모델:
  δ_SEI(t, T) = δ₀ + A_pre·√t·exp(-Ea/(R·T))

  • 실온(298K) 단기 시뮬레이션: SEI 기여 무시 가능 (~pm 수준)
  • 고온(333K+) 장기 시뮬레이션: 누적 수십 nm → 구조 변위에 기여

구현:
  - FUNCTID 7002: SEI 두께 함수 float sei_thickness(float time, float temp)
  - DEFINE_CURVE 9003: SEI 유발 변위 vs 시간 (T=T_ref 고정 기준값)
  - 14_intercalation_strain.k 의 LCID 9001에 이미 SEI 오프셋이 합산되어 있음
  - 이 파일은 SEI 만의 독립 추적 용도 (aging 파라미터 스터디)

사용법:
    python generate_sei_growth.py --config battery_config.yaml
    python generate_sei_growth.py --tier 0 --T-ref 333.15
"""
from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
from typing import Any, Dict

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, write_curve,
    get_geometry, get_n_cells_for_tier, get_scenario_params,
    fmt16,
)

logger = logging.getLogger(__name__)


def generate_sei_growth(
    config: Dict[str, Any],
    tier: float = -1,
    model_type: str = "stacked",
    T_ref: float = 313.15,         # K (40°C, 보수적 고온 기준)
    output: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """15_sei_growth.k 생성.

    SEI 성장 모델 파라미터 + DEFINE_FUNCTION 7002 + 참조 곡선 LCID 9003.

    Args:
        T_ref: SEI 성장률 계산 기준 온도 (K). 기본 313.15 K (40°C).
               실온(298K) 결과는 거의 0이므로 고온 기준 사용.
    """
    log = log or logger
    if output is None:
        output = "15_sei_growth.k"
    outpath = Path(output)

    n_cells = get_n_cells_for_tier(config, tier, model_type)
    geo     = get_geometry(config, model_type)
    sp      = get_scenario_params(config, "swelling")
    sei     = sp.get("sei_growth", {})
    end_t   = sp.get("end_time", 7200.0)

    A_pre    = sei.get("pre_exponential", 1.5e-6)   # m/√s
    Ea       = sei.get("activation_energy", 40000)   # J/mol
    delta_0  = sei.get("initial_thickness", 5.0e-9)  # m
    delta_max = sei.get("max_thickness", 50.0e-9)    # m
    R_gas    = 8.314                                  # J/(mol·K)

    # SEI 두께 → 변위 변환 인수
    # 각 UC: anode 양면 두께 = 2 × t_anode mm = 2 × t_anode × 1e-3 m
    L_an_m   = 2.0 * geo["t_anode"] * 1.0e-3         # m

    # 참조 곡선 계산: δ_SEI(t, T_ref) → 스택 변위 [mm]
    # strain = (δ_SEI - δ_0) / L_an, displacement = n_cells × L_an_m × 1e3 × strain
    def sei_disp_mm(t_s: float) -> float:
        delta = delta_0 + A_pre * math.sqrt(max(t_s, 0.0)) * math.exp(-Ea / (R_gas * T_ref))
        delta = min(delta, delta_max)
        strain = (delta - delta_0) / L_an_m if L_an_m > 0 else 0.0
        return n_cells * L_an_m * 1.0e3 * strain

    # 시간 포인트: 로그 스케일 + 선형 (단기 시뮬레이션에 적합)
    t_points = [0.0, 60.0, 300.0, 600.0, 1800.0, 3600.0, end_t]
    t_points = sorted(set(t_points + [end_t]))
    ref_curve = [(t, sei_disp_mm(t)) for t in t_points]

    # 정보 값 계산
    d_at_end = sei_disp_mm(end_t)
    d_at_1h  = sei_disp_mm(3600.0)
    sei_at_end_nm = (delta_0 + A_pre * math.sqrt(end_t) * math.exp(-Ea / (R_gas * T_ref))) * 1e9

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(
            f,
            "SEI Growth Model - Irreversible Swelling Component",
            description=(
                f"SEI kinetics: delta(t,T) = delta_0 + A*sqrt(t)*exp(-Ea/RT)\n"
                f"A_pre={A_pre:.2E} m/sqrt(s), Ea={Ea:.0f} J/mol, T_ref={T_ref:.2f} K\n"
                f"At T_ref={T_ref:.0f}K, t={end_t:.0f}s: delta_SEI~{sei_at_end_nm:.2f} nm, "
                f"stack disp~{d_at_end:.6f} mm\n"
                f"Note: SEI displacement is already included in 14_intercalation_strain.k LCID 9001.\n"
                f"This file provides standalone SEI tracking for aging parameter studies."
            ),
        )
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ── FUNCTID 7002: SEI 두께 함수 ──
        write_separator(f, "FUNCTID 7002: SEI Growth Thickness (Arrhenius)")
        f.write("$ float sei_thickness(float time, float temp) -> SEI thickness [m]\n")
        f.write("$ Usage: EM_RANDLES_SOLID SEI tracking, aging parameter study\n")
        f.write("$ Note: for displacement, convert using stack geometry:\n")
        f.write(f"$   L_anode(per UC) = {L_an_m*1e3:.4f} mm (both sides)\n")
        f.write(f"$   d_SEI(mm) = n_cells * L_an(mm) * (delta_SEI / L_an_m)\n")
        f.write("$\n")
        f.write("*DEFINE_FUNCTION\n")
        f.write("      7002\n")
        f.write("float sei_growth_thickness(float time, float temp)\n")
        f.write("{\n")
        f.write(f"    float A_pre    = {A_pre:.4E};  // m/sqrt(s)\n")
        f.write(f"    float Ea       = {Ea:.2E};   // J/mol\n")
        f.write(f"    float delta_0  = {delta_0:.4E};  // m (initial SEI thickness)\n")
        f.write(f"    float delta_max = {delta_max:.4E}; // m (maximum SEI thickness)\n")
        f.write("    float R_gas    = 8.314;         // J/(mol*K)\n")
        f.write("\n")
        f.write("    // Safety: use 298K if temperature not physically reasonable\n")
        f.write("    float T = (temp > 250.0) ? temp : 298.15;\n")
        f.write("\n")
        f.write("    float delta = delta_0 + A_pre * sqrt(time) * exp(-Ea / (R_gas * T));\n")
        f.write("    if (delta > delta_max) delta = delta_max;\n")
        f.write("    if (delta < delta_0)   delta = delta_0;\n")
        f.write("    return delta;\n")
        f.write("}\n")
        f.write("$\n")

        # ── LCID 9003: SEI 변위 참조 곡선 (T=T_ref 기준) ──
        write_separator(f, f"LCID 9003: SEI-Only Displacement Reference (T={T_ref:.0f}K)")
        f.write(f"$ Pre-computed at T_ref = {T_ref:.2f} K ({T_ref - 273.15:.1f} C)\n")
        f.write(f"$ At t={end_t:.0f}s: disp = {d_at_end:.6f} mm"
                f"  (delta_SEI ~ {sei_at_end_nm:.2f} nm)\n")
        f.write(f"$ At t=3600s:  disp = {d_at_1h:.6f} mm\n")
        f.write("$ This curve is for reference/visualization only.\n")
        f.write("$ The combined intercalation+SEI curve is in 14_intercalation_strain.k.\n")
        f.write("$\n")
        write_curve(f, 9003,
                    f"SEI Displacement vs Time (T_ref={T_ref:.0f}K)",
                    ref_curve)
        f.write("$\n")

        f.write("*END\n")

    log.info("SEI 성장 모듈 생성 완료: %s (T_ref=%.1fK, d_SEI@end=%.2e mm)",
             outpath, T_ref, d_at_end)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(
        description="15_sei_growth.k 생성 (SEI 성장 독립 모듈)")
    add_common_args(parser)
    parser.add_argument("--type", choices=["stacked", "wound"],
                        default="stacked", help="모델 타입 (기본: stacked)")
    parser.add_argument("--T-ref", type=float, default=313.15,
                        help="SEI 기준 온도 K (기본: 313.15 = 40°C)")
    args = parser.parse_args()

    log = setup_logger("gen_sei",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)
    generate_sei_growth(config, tier=args.tier, model_type=args.type,
                        T_ref=args.T_ref, log=log)


if __name__ == "__main__":
    main()
