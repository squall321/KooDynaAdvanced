#!/usr/bin/env python3
"""
12_venting.k 자동 생성
======================
가스팽창 시나리오의 AIRBAG 벤팅 모델 + Arrhenius 가스 발생 함수를 자동 생성.

battery_config.yaml의 scenarios.gas.venting / gas_generation 에서 모든 파라미터를 읽어
하드코딩 없이 k-file을 출력합니다.

생성되는 LS-DYNA 객체:
  - *SET_SEGMENT_GENERAL (SID=503) — 파우치 내면 세그먼트
  - *AIRBAG_SIMPLE_AIRBAG_MODEL   — 파우치 가스 팽창 모델
  - *DEFINE_CURVE 12001            — 가스 발생율 placeholder
  - *DEFINE_CURVE 12003            — 벤팅 출구 면적 vs 절대압력
  - *DEFINE_FUNCTION 12010         — 온도 기반 Arrhenius 가스 발생율
  - *DEFINE_CURVE 12005            — 가스 온도 placeholder

사용법:
    python generate_venting.py --config battery_config.yaml
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, write_curve,
    get_scenario_params, PID, fmt8,
)

logger = logging.getLogger(__name__)

# ── 고정 ID ──────────────────────────────────────────────────
SEGSET_POUCH_INNER = 503   # 파우치 내면 세그먼트 셋 ID
LCID_GAS_RATE      = 12001 # placeholder gas rate vs time
LCID_VENT_AREA     = 12003 # vent exit area vs pressure
LCID_GAS_TEMP      = 12005 # placeholder gas temp vs time
FUNCTID_GAS_RATE   = 12010 # Arrhenius gas generation function


# ── Arrhenius stages 파싱 ─────────────────────────────────────
def _parse_gas_stages(gg: Dict[str, Any]) -> List[Tuple[str, float, float, float]]:
    """gas_generation config에서 Arrhenius stage 목록을 반환.

    Returns:
        [(name, onset_K, Ea_J_mol, A_pre), ...]
    """
    stages = gg.get("stages")
    if stages and isinstance(stages, dict):
        result = []
        for name, params in stages.items():
            result.append((
                str(name),
                float(params.get("onset_temperature", 373.0)),
                float(params.get("activation_energy", 80000)),
                float(params.get("pre_exponential", 1.0e8)),
            ))
        # onset_temperature 오름차순 정렬
        result.sort(key=lambda x: x[1])
        return result

    # 하위호환: flat 필드 → 1-stage
    return [(
        "gas_decomposition",
        float(gg.get("onset_temperature", 373.0)),
        float(gg.get("activation_energy", 80000)),
        float(gg.get("pre_exponential", 1.0e12)),
    )]


# ── FUNCTID 12010 C-함수 생성 ─────────────────────────────────
def _write_gas_rate_function(
    f,
    stages: List[Tuple[str, float, float, float]],
    mw: float,
    max_rate: float,
) -> None:
    """DEFINE_FUNCTION 12010: Arrhenius 가스 발생율 C 함수 작성.

    함수 본문 내 코멘트는 반드시 // 사용 ($ 사용 시 파싱 오류).
    """
    conv_factor = mw * 1.0e-6  # g/mol → ton/mol

    f.write("*DEFINE_FUNCTION\n")
    f.write(f"     {FUNCTID_GAS_RATE}\n")
    f.write("float gas_rate(float time, float temp, float pressure, float volume)\n")
    f.write("{\n")
    f.write("    // 인수: (time[s], temp[K], pressure[MPa], volume[mm3])\n")
    f.write("    // AIRBAG LCID=-12010 규약: 4-arg (time, temp, pressure, volume)\n")
    f.write("    float R_gas = 8.314;       // J/(mol*K)\n")
    f.write("    float rate  = 0.0;\n")
    f.write("    float T = (temp > 250.0) ? temp : 298.15;\n")
    f.write("\n")

    for name, t_onset, ea, a_pre in stages:
        label = name.replace("_", " ")
        f.write(f"    // {label} (T > {t_onset:.0f} K = {t_onset - 273.15:.0f} C)\n")
        f.write(f"    if (T > {t_onset:.1f})\n")
        f.write("    {\n")
        f.write(f"        rate = rate + {a_pre:.4E} * exp(-{ea:.1f} / (R_gas * T));\n")
        f.write("    }\n")
        f.write("\n")

    f.write(f"    // mol/s -> ton/s (MW={mw:.0f} g/mol, 1ton=1e6g -> {conv_factor:.1E} ton/mol)\n")
    f.write(f"    rate = rate * {conv_factor:.4E};\n")
    f.write("\n")
    f.write(f"    // 최대 발생율 제한\n")
    f.write(f"    if (rate > {max_rate:.1E}) rate = {max_rate:.1E};\n")
    f.write("\n")
    f.write("    return rate;\n")
    f.write("}\n")


# ── 메인 생성 함수 ────────────────────────────────────────────
def generate_venting(
    config: Dict[str, Any],
    output: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """12_venting.k 자동 생성.

    Args:
        config: battery_config dict
        output: 출력 파일 경로 (기본: 12_venting.k)
        log: 로거

    Returns:
        생성된 파일 경로 문자열
    """
    log = log or logger
    if output is None:
        output = "12_venting.k"
    outpath = Path(output)

    # ── config 파싱 ──
    sp = get_scenario_params(config, "gas")
    gg = sp.get("gas_generation", {})
    vt = sp.get("venting", {})

    # Arrhenius stages
    stages = _parse_gas_stages(gg)
    mw       = float(gg.get("molecular_weight", 40.0))
    max_rate = float(gg.get("max_rate", 1.0e-7))

    # AIRBAG 열역학 물성
    cv   = float(vt.get("cv", 723.0))
    cp   = float(vt.get("cp", 1004.0))
    t_gas = float(vt.get("initial_temperature", 298.15))
    mu   = float(vt.get("discharge_coefficient", 0.6))
    pe   = float(vt.get("atmospheric_pressure", 0.1))
    ro   = float(vt.get("atmospheric_density", 1.0e-9))

    # 벤팅 면적 커브
    vent_curve_raw = vt.get("vent_area_curve", [
        [0.0, 0.0], [0.2, 0.0], [0.3, 0.2], [0.6, 1.6],
        [1.0, 2.0], [2.0, 2.0], [10.0, 2.0],
    ])
    vent_curve = [(float(p[0]), float(p[1])) for p in vent_curve_raw]

    # 파우치 PIDs
    pid_top    = PID.POUCH_TOP
    pid_bottom = PID.POUCH_BOTTOM
    pid_side   = PID.POUCH_SIDE

    # ── k-file 출력 ──
    with open(outpath, "w", encoding="utf-8") as f:

        # ── Header ──
        write_kfile_header(
            f,
            "Li-ion Cell - Electrolyte Venting / Gas Generation Model",
            description=(
                "B11: 전해질 가스 발생 및 벤팅 모델\n"
                "  - 전해질 열분해 시 가스 발생 (80~200°C)\n"
                "  - *AIRBAG_SIMPLE_AIRBAG_MODEL 기반 파우치 팽창\n"
                "  - *DEFINE_FUNCTION 12010: 온도 기반 Arrhenius 가스 발생율\n"
                "\n"
                "물리적 배경:\n"
                "  1. 60~80°C: SEI 분해 → CO2, C2H4 발생 시작\n"
                "  2. 120°C: 전해질 환원 반응 → H2, CO, CH4\n"
                "  3. 150°C: 전해질 산화 분해 → CO2, H2O (대량)\n"
                "  4. 200°C+: 급격한 가스 발생, 벤팅 (파우치 파열)\n"
                "\n"
                "포함: Phase 3 main 파일에서 *INCLUDE\n"
                "자동 생성: generate_venting.py (battery_config.yaml → 12_venting.k)"
            ),
        )
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ── 1. SET_SEGMENT_GENERAL ──
        write_separator(f, "1. 파우치 내면 세그먼트 셋 (AIRBAG 밀폐면)")
        f.write("$ SET_SEGMENT_GENERAL PART 옵션: 파우치 셸 내면 자동 생성\n")
        f.write("$ AIRBAG은 밀폐된 세그먼트 셋 필요 — 파우치 전체면 사용\n")
        f.write("$\n")
        f.write("*SET_SEGMENT_GENERAL\n")
        f.write("$      SID       DA1       DA2       DA3       DA4\n")
        f.write(f"{SEGSET_POUCH_INNER:>10d}       0.0       0.0       0.0       0.0\n")
        f.write("$   OPTION        E1        E2        E3\n")
        f.write(f"      PART{pid_top:>10d}{pid_bottom:>10d}{pid_side:>10d}\n")
        f.write(f"$\n")
        f.write(f"$ SID={SEGSET_POUCH_INNER}: 파우치 전면 "
                f"(PID {pid_top}=상면, {pid_bottom}=하면, {pid_side}=측면)\n")

        # ── 2. AIRBAG_SIMPLE_AIRBAG_MODEL ──
        write_separator(f, "2. AIRBAG 모델 — 파우치 내부 가스 팽창")
        f.write("$ Per Vol_I p.408 (R16): AIRBAG_SIMPLE_AIRBAG_MODEL\n")
        f.write("$   Card 1 (core): SID, SIDTYP, RBID, VSCA, PSCA, VINI, MWD, SPSF\n")
        f.write("$   Card 3: CV, CP, T, LCID, MU, AREA, PE, RO\n")
        f.write("$   Card 4b (CV≠0): LOU\n")
        f.write("$\n")
        f.write("*AIRBAG_SIMPLE_AIRBAG_MODEL\n")

        # Card 1
        f.write("$ Card 1 (core): 파우치 내면 세그먼트 셋\n")
        f.write("$      SID    SIDTYP      RBID      VSCA      PSCA      VINI       MWD      SPSF\n")
        f.write(f"{SEGSET_POUCH_INNER:>10d}         0         0       1.0       1.0       0.0       0.0       0.0\n")

        # Card 3
        f.write("$ Card 3: 가스 열역학 특성\n")
        f.write("$       CV        CP         T      LCID        MU      AREA        PE        RO\n")
        f.write(f"{cv:>10.1f}{cp:>10.1f}{t_gas:>10.2f}"
                f"    {-FUNCTID_GAS_RATE}{mu:>10.1f}      {-LCID_VENT_AREA}"
                f"{pe:>10.1f}  {ro:.1E}\n")
        f.write(f"$ CV={cv:.0f} J/kg/K (분해가스 정적 비열)\n")
        f.write(f"$ CP={cp:.0f} J/kg/K (정압 비열)\n")
        f.write(f"$ T={t_gas:.2f} K (유입 가스 온도)\n")
        f.write(f"$ LCID=-{FUNCTID_GAS_RATE}: FUNCTID {FUNCTID_GAS_RATE} 호출 "
                "(온도 기반 Arrhenius 가스 발생율)\n")
        f.write(f"$ MU={mu}: 벤팅 오리피스 형상 계수\n")
        f.write(f"$ AREA=-{LCID_VENT_AREA}: 벤팅 면적 vs 절대압력 커브 (safety valve 모델)\n")
        f.write(f"$ PE={pe} MPa (대기압)\n")
        f.write(f"$ RO={ro:.1E} ton/mm³ (대기 밀도)\n")
        f.write("$\n")

        # Card 4b
        f.write("$ Card 4b (CV≠0이므로 Card 4b 사용):\n")
        f.write("$      LOU\n")
        f.write("         0\n")
        f.write("$ LOU=0: MU+AREA 방식으로 벤팅 (LOU curve 미사용)\n")

        # ── 3. LCID 12001 — placeholder gas rate ──
        write_separator(f, "3. 가스 발생율 커브 (placeholder, FUNCTID 12010이 우선)")
        f.write("$ LCID 12001: 질량유입율 (ton/s) vs 시간\n")
        f.write(f"$ 실제 구동은 DEFINE_FUNCTION {FUNCTID_GAS_RATE}으로 대체\n")
        f.write("$\n")
        placeholder_rate = [
            (0.0, 0.0), (0.001, 0.0), (0.005, 1.0e-12),
            (0.010, 5.0e-12), (0.050, 1.0e-10), (0.100, 5.0e-10),
            (1.0, 1.0e-9), (10.0, 5.0e-9), (60.0, 5.0e-9),
        ]
        write_curve(f, LCID_GAS_RATE, "Gas Generation Rate vs Time (placeholder)", placeholder_rate)

        # ── 4. LCID 12003 — vent area vs pressure ──
        write_separator(f, "4. 벤팅 면적 커브 (safety valve / burst disk 모델)")
        f.write(f"$ LCID {LCID_VENT_AREA}: 벤팅 출구 면적 (mm²) vs 절대압력 (MPa)\n")
        f.write("$ Per Vol_I p.409: AREA<0 → |AREA|=LCID, 면적 vs 절대압력\n")
        f.write("$\n")
        write_curve(f, LCID_VENT_AREA, "Vent Exit Area vs Absolute Pressure (safety valve model)",
                    vent_curve)

        # ── 5. FUNCTID 12010 — Arrhenius gas generation ──
        write_separator(f, "5. 가스 발생 온도 트리거 함수 (Arrhenius)")
        n_stages = len(stages)
        stage_desc = ", ".join(f"{s[0]}({s[1]-273.15:.0f}°C)" for s in stages)
        f.write(f"$ {n_stages}-stage Arrhenius: {stage_desc}\n")
        f.write(f"$ MW={mw:.0f} g/mol, max_rate={max_rate:.1E} ton/s\n")
        f.write("$\n")
        _write_gas_rate_function(f, stages, mw, max_rate)

        # ── 6. LCID 12005 — placeholder gas temp ──
        write_separator(f, "6. 가스 물성 보조 커브 (placeholder)")
        f.write("$ 온도 의존 가스 압력-체적 관계 (솔버 연동 시 자동 갱신)\n")
        f.write("$\n")
        placeholder_temp = [
            (0.0, 298.15), (0.005, 298.15), (0.010, 320.0),
            (0.050, 400.0), (0.100, 500.0), (1.0, 600.0),
            (10.0, 500.0), (60.0, 400.0),
        ]
        write_curve(f, LCID_GAS_TEMP, "Gas Temperature vs Time (from thermal solver coupling)",
                    placeholder_temp)

        # ── 7. 파우치 파열 기준 주석 ──
        write_separator(f, "7. 파우치 파열 기준 — 내압 연동")
        f.write("$ 파우치 압력 기반 파괴 (AMMGID 참조)\n")
        f.write("$ 내압 > 0.5MPa 이고 변형률 > 0.15 이면 파열\n")
        f.write("$ → 기존 MAT_ADD_EROSION에 MXPRS 추가 또는 여기서 별도 정의 가능\n")
        f.write("$\n")
        f.write("$ (MAT_024 MID=6에 이미 FAIL 미지정 → 필요 시 아래 활성화)\n")
        f.write("$*MAT_ADD_EROSION\n")
        f.write("$        6       0       0.5       0.0       0.0       0.0       0.2      0.0\n")
        f.write("$       0.0       0.0       0.0       0.0\n")

        # ── 8. Implementation notes ──
        write_separator(f, "참고 (Implementation Notes)")
        f.write("$\n")
        f.write("$ [활성화 방법]\n")
        f.write(f"$  1. 파우치 내부면 → *SET_SEGMENT (SID={SEGSET_POUCH_INNER}) 으로 밀폐면 정의\n")
        f.write("$     (generate_mesh_*.py에서 파우치 내면 세그먼트 셋 생성 필요)\n")
        f.write("$  2. Phase 3 main 파일에 *INCLUDE 12_venting.k 추가\n")
        f.write("$  3. 벤팅 면적(VNTCA) 및 개방 압력 → 실험 데이터로 보정\n")
        f.write("$\n")
        f.write("$ [대안: SPH 가스]\n")
        f.write("$  AIRBAG 대신 *PARTICLE_BLAST 또는 *ALE_MULTI-MATERIAL_GROUP\n")
        f.write("$  으로 가스 거동을 직접 시뮬레이션 가능 (C14와 통합 고려)\n")
        f.write("$\n")
        f.write("$ [보정 포인트]\n")
        for name, t_onset, ea, a_pre in stages:
            label = name.replace("_", " ")
            f.write(f"$  - {label}: A={a_pre:.1E}, Ea={ea:.0f} J/mol → ARC/DSC 실험으로 보정\n")
        f.write("$  - 벤팅 면적/압력: 파우치 씰 강도 실험으로 결정\n")
        f.write("$\n")

        f.write("*END\n")

    log.info("벤팅 모델 생성 완료: %s", outpath)
    return str(outpath)


# ── CLI ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="12_venting.k 자동 생성 (가스팽창 시나리오 벤팅 모듈)")
    add_common_args(parser)
    args = parser.parse_args()

    log = setup_logger("gen_venting",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)
    generate_venting(config, log=log)


if __name__ == "__main__":
    main()
