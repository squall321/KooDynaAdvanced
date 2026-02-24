#!/usr/bin/env python3
"""
16_gas_generation_standalone.k 자동 생성
=========================================
가스팽창 시나리오 전용 독립 모듈.

이 파일이 정의하는 LS-DYNA 객체:
  - 없음 (BOUNDARY_HEAT_SET는 06_boundary_loads_gas.k에,
          FUNCTID 9013은 10_define_curves_gas.k에 정의)
  - 이 파일은 가스 발생-팽창 해석의 물리 모델 구성을 문서화하고,
    12_venting.k 및 13_ale_electrolyte.k 와의 연동을 명시하는 역할.

실제 포함 구조 (01_main_gas.k):
  *INCLUDE 02_mesh_stacked*.k      ← 메시 (공유)
  *INCLUDE 04_materials.k          ← 구조 재료 (공유)
  *INCLUDE 04_materials_tempdep.k  ← 열 재료 (공유)
  *INCLUDE 05_contacts*.k          ← 접촉 (Phase 3 재사용)
  *INCLUDE 06_boundary_loads_gas.k ← SPC + 열BC + BOUNDARY_HEAT_SET
  *INCLUDE 07_control_gas.k        ← 솔버 제어 (3600s, 열+EM)
  *INCLUDE 08_em_randles*.k        ← EM Randles (열폭주 추적)
  *INCLUDE 09_database.k           ← 출력 (Phase 3 재사용)
  *INCLUDE 10_define_curves_gas.k  ← 커브 + FUNCTID 9013 (가스 발생)
  *INCLUDE 16_gas_generation_standalone.k  ← 이 파일
  *INCLUDE 12_venting.k            ← AIRBAG 파우치 팽창 (항상 활성)
 [$*INCLUDE 13_ale_electrolyte.k]  ← ALE 전해질 (선택, _ale 변형)

사용법:
    python generate_gas_standalone.py --config battery_config.yaml
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, get_scenario_params,
)

logger = logging.getLogger(__name__)


def generate_gas_standalone(
    config: Dict[str, Any],
    output: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """16_gas_generation_standalone.k 생성.

    가스팽창 시나리오 전용 EM-열 연동 설정 파일.
    FUNCTID 9013 (가스 발생률)은 10_define_curves_gas.k 에 정의되며,
    이 파일은 EM 발열 반응과 가스 생성의 연동 관계를 명시하는
    *DEFINE_FUNCTION 9011 (열플럭스 함수, 온도 의존)을 포함.
    """
    log = log or logger
    if output is None:
        output = "16_gas_generation_standalone.k"
    outpath = Path(output)

    sp = get_scenario_params(config, "gas")
    gg = sp.get("gas_generation", {})
    hs = sp.get("heat_source", {})
    T_onset = float(gg.get("onset_temperature", 373.0))
    Ea      = float(gg.get("activation_energy", 80000))
    A_pre   = float(gg.get("pre_exponential", 1.0e12))
    q_raw   = float(hs.get("heat_flux_density", 5000.0))   # W/m²
    q_mmK   = q_raw * 1.0e-3  # W/m² → mJ/(s·mm²)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(
            f,
            "Gas Generation Standalone - Thermal-Driven Venting Module",
            description=(
                "Gas expansion scenario: external heat -> gas generation -> venting\n"
                "FUNCTID 9011: radiation heat flux q_rad(T) — connected to BOUNDARY_HEAT_SET (HLCID=-9011)\n"
                "FUNCTID 12010: Arrhenius gas rate — connected to AIRBAG (LCID=-12010 in 12_venting.k)\n"
                "12_venting.k: AIRBAG_SIMPLE_AIRBAG_MODEL (active)\n"
                "13_ale_electrolyte.k: ALE electrolyte (optional, see _ale variant)"
            ),
        )
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ── FUNCTID 9011: Temperature-dependent radiation heat flux ──
        # 온도에 따른 복사 열플럭스 추가분 계산 (Stefan-Boltzmann)
        # q_rad(T) = eps * sigma_SB * (T^4 - T_amb^4)   [mJ/(s*mm^2)]
        # BOUNDARY_HEAT_SET에서 HLCID=-9011 로 직접 호출
        # (기존 HLCID=9010 강제대류항에 추가로 적용됨)
        write_separator(f, "FUNCTID 9011: Temperature-Dependent Radiation Heat Flux")
        f.write("$ q_total = q_conv(t) [LCID 9010] + q_rad(T) [FUNCTID -9011]\n")
        f.write("$ q_rad(T) = eps * sigma_SB * (T^4 - T_amb^4)  [mJ/(s*mm^2)]\n")
        f.write("$ Connected via second BOUNDARY_HEAT_SET in 06_boundary_loads_gas.k\n")
        f.write("$\n")
        f.write("*DEFINE_FUNCTION\n")
        f.write("      9011\n")
        f.write("float heat_flux_radiation(float time, float temp)\n")
        f.write("{\n")
        f.write("    float T_amb    = 298.15;      // K — ambient reference\n")
        f.write("    float sigma_SB = 5.670e-14;   // W/(mm^2*K^4) Stefan-Boltzmann\n")
        f.write("    float eps      = 0.90;         // surface emissivity\n")
        f.write("\n")
        f.write("    float T = (temp > 200.0) ? temp : T_amb;\n")
        f.write("    float q_rad = eps * sigma_SB * (T*T*T*T - T_amb*T_amb*T_amb*T_amb);\n")
        f.write("    if (q_rad < 0.0) q_rad = 0.0;\n")
        f.write("    return q_rad;  // mJ/(s*mm^2), additional radiation flux\n")
        f.write("}\n")
        f.write("$\n")

        # ── Physical parameter summary ──
        write_separator(f, "GAS GENERATION PHYSICS SUMMARY")
        f.write(f"$ External heat flux: {q_raw:.0f} W/m^2 = {q_mmK:.4E} mJ/(s*mm^2)\n")
        f.write(f"$ Gas onset temperature: {T_onset:.1f} K ({T_onset - 273.15:.1f} C)\n")
        f.write(f"$ Arrhenius: A={A_pre:.2E} 1/s, Ea={Ea:.0f} J/mol (ref)\n")
        f.write("$ Gas rate: FUNCTID 12010 in 12_venting.k (2-stage SEI+electrolyte, LCID=-12010)\n")
        f.write("$ Radiation flux: FUNCTID 9011 (this file), connected via HLCID=-9011\n")
        f.write("$\n")
        f.write("$ Thermal runaway chain:\n")
        f.write("$   Forced convection (BOUNDARY_HEAT_SET, LCID 9010)\n")
        f.write("$   + Radiation correction (BOUNDARY_HEAT_SET, HLCID=-9011, FUNCTID 9011)\n")
        f.write("$   -> Temperature rise (CONTROL_THERMAL_SOLVER)\n")
        f.write("$   -> SEI decomposition (T > 353K, FUNCTID 5002 stage 1)\n")
        f.write("$   -> Anode-electrolyte reaction (T > 393K, stage 2)\n")
        f.write("$   -> Electrolyte decomposition (T > 423K, stage 3)\n")
        f.write("$   -> Gas generation (T > T_onset, FUNCTID 12010 via AIRBAG LCID=-12010)\n")
        f.write("$   -> Pouch inflation (AIRBAG_SIMPLE_AIRBAG_MODEL, 12_venting.k)\n")
        f.write("$   -> Pouch rupture (yield stress exceeded, MID=6)\n")
        f.write("$\n")

        f.write("*END\n")

    log.info("가스팽창 독립 모듈 생성 완료: %s", outpath)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(
        description="16_gas_generation_standalone.k 생성 (가스팽창 시나리오 모듈)")
    add_common_args(parser)
    args = parser.parse_args()

    log = setup_logger("gen_gas",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)
    generate_gas_standalone(config, log=log)


if __name__ == "__main__":
    main()
