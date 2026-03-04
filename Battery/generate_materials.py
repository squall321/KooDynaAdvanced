#!/usr/bin/env python3
"""
04_materials.k + 04_materials_tempdep.k 자동 생성
===================================================
battery_config.yaml의 materials 섹션에서 물성값을 읽어
구조/열/EM 재료 카드를 모두 생성합니다.

사용법:
    python generate_materials.py --config battery_config.yaml
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, TextIO

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header, write_separator, fmt10,
    MID, PID, LT, get_n_cells_for_tier, tier_to_suffix,
)

logger = logging.getLogger(__name__)


# ============================================================
# 구조 재료 작성
# ============================================================

def _write_mat_johnson_cook(f: TextIO, mid: int, m: Dict[str, Any], name: str) -> None:
    """MAT_JOHNSON_COOK (MID 1,2: Al/Cu CC)"""
    ro = m["density"]
    E = m["youngs_modulus"]
    pr = m["poisson_ratio"]
    G = E / (2 * (1 + pr))

    jc = m.get("johnson_cook", {})
    A = jc.get("A", m.get("yield_stress", 90.0))
    B = jc.get("B", m.get("tangent_modulus", 125.0))
    N = jc.get("N", 0.22)
    C = jc.get("C", 0.014)
    M = jc.get("M", 1.0)
    TM = jc.get("TM", 933.0)
    TR = jc.get("TR", 298.15)
    CP = m.get("specific_heat", 903.0)
    if isinstance(CP, str):
        CP = float(CP)
    # Specific heat: YAML stores in mJ/ton·K, JC wants J/kg/K — same numeric value
    # because 1 mJ/(1e3 kg·K) = 1e-3 J/(1e3 kg·K) ... actually YAML stores raw number
    # The YAML values are in mJ/ton·K = same as J/kg/K numerically? No:
    # 900e6 mJ/ton·K = 900e6 * 1e-3 J / (1e3 kg · K) = 900 J/kg/K. So divide by 1e6.
    cp_yaml = float(m.get("specific_heat", 903.0e6))
    if cp_yaml > 1e4:
        CP = cp_yaml / 1e6  # mJ/ton·K → J/kg·K (same as LS-DYNA CP in ton-mm-s)
    else:
        CP = cp_yaml

    # D1-D5=0: disable JC damage to prevent premature erosion under crush
    D1 = D2 = D3 = D4 = D5 = 0.0

    f.write(f"$--- MID {mid}: {name} ---\n")
    f.write("*MAT_JOHNSON_COOK\n")
    f.write("$      MID        RO         G         E        PR       DTF        VP    RATEOP\n")
    f.write(f"{mid:>10d}{ro:>10.3E}{G:>10.1f}{E:>10.1f}{pr:>10.2f}       0.0       0.0       0.0\n")
    f.write("$        A         B         N         C         M        TM        TR      EPS0\n")
    f.write(f"{A:>10.1f}{B:>10.1f}{N:>10.2f}{C:>10.3f}{M:>10.1f}{TM:>10.1f}{TR:>10.2f}       1.0\n")
    f.write("$       CP        PC     SPALL        IT        D1        D2        D3        D4\n")
    f.write(f"{CP:>10.1f}       0.0       0.0       0.0{D1:>10.2f}{D2:>10.2f}{D3:>10.2f}{D4:>10.3f}\n")
    f.write("$       D5                EROD     EFMIN    NUMINT\n")
    f.write(f"{D5:>10.1f}                 0.0   1.0E-06         0\n")
    f.write("$\n")


def _write_mat_crushable_foam(f: TextIO, mid: int, name: str,
                              ro: float, E: float, PR: float,
                              lcid: int, tsc: float) -> None:
    f.write(f"$--- MID {mid}: {name} ---\n")
    f.write("*MAT_CRUSHABLE_FOAM\n")
    f.write("$      MID        RO         E        PR      LCID       TSC      DAMP     MODEL\n")
    f.write(f"{mid:>10d}{ro:>10.3E}{E:>10.0f}{PR:>10.2f}{lcid:>10d}{tsc:>10.1f}      0.10         0\n")
    f.write("$\n")


def _write_mat_piecewise(f: TextIO, mid: int, name: str, m: Dict[str, Any],
                         cs_C: float, cs_P: float, fail: float = 0.0,
                         lcss: int = 0) -> None:
    ro = m["density"]
    E = m["youngs_modulus"]
    pr = m["poisson_ratio"]
    sigy = m["yield_stress"]
    etan = m.get("tangent_modulus", 500.0)
    # ETAN must be less than E (LS-DYNA Error 20430)
    if etan >= E:
        etan = E * 0.33
    # When LCSS is used, set SIGY=0, ETAN=0 (curve defines full response)
    if lcss > 0:
        sigy = 0.0
        etan = 0.0

    f.write(f"$--- MID {mid}: {name} ---\n")
    f.write("*MAT_PIECEWISE_LINEAR_PLASTICITY\n")
    f.write("$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL\n")
    f.write(f"{mid:>10d}{ro:>10.3E}{E:>10.0f}{pr:>10.2f}{sigy:>10.1f}{etan:>10.1f}{fail:>10.1f}       0.0\n")
    f.write("$        C         P      LCSS      LCSR        VP\n")
    f.write(f"{cs_C:>10.1f}{cs_P:>10.1f}{lcss:>10d}         0       0.0\n")
    f.write("$     EPS1      EPS2      EPS3      EPS4      EPS5      EPS6      EPS7      EPS8\n")
    f.write("       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$      ES1       ES2       ES3       ES4       ES5       ES6       ES7       ES8\n")
    f.write("       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0\n")


def _write_mat_add_erosion(f: TextIO, mid: int, mxprs: float = 0.0,
                           sigp1: float = 0.0, sigvm: float = 0.0,
                           mxeps: float = 0.0) -> None:
    f.write("*MAT_ADD_EROSION\n")
    f.write("$      MID    EXCL    MXPRS    MNPRS    SIGP1    SIGVM    MXEPS    EPSSH\n")
    f.write(f"{mid:>10d}         0{mxprs:>10.1f}       0.0{sigp1:>10.1f}{sigvm:>10.1f}{mxeps:>10.1f}      0.0\n")
    f.write("$   MNEPS   SIGTH    IMPULSE  FATEFP\n")
    f.write("       0.0       0.0       0.0       0.0\n")
    f.write("$\n")


def _write_mat_rigid(f: TextIO, mid: int, m: Dict[str, Any]) -> None:
    ro = m["density"]
    E = m["youngs_modulus"]
    pr = m["poisson_ratio"]
    f.write(f"$--- MID {mid}: Rigid ---\n")
    f.write("*MAT_RIGID\n")
    f.write("$      MID        RO         E        PR         N    COUPLE         M     ALIAS\n")
    f.write(f"{mid:>10d}{ro:>10.3E}{E:>10.0f}{pr:>10.2f}       0.0       0.0       0.0       0.0\n")
    f.write("$      CMO      CON1      CON2\n")
    f.write("       1.0         7         7\n")
    f.write("$  LCO_or_A1       A2        A3       V1        V2        V3\n")
    f.write("       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$\n")


def _write_mat_elastic(f: TextIO, mid: int, m: Dict[str, Any], name: str) -> None:
    ro = m["density"]
    E = m.get("youngs_modulus", m.get("bulk_modulus", 100.0))
    pr = m.get("poisson_ratio", 0.45)
    f.write(f"$--- MID {mid}: {name} ---\n")
    f.write("*MAT_ELASTIC\n")
    f.write("$      MID        RO         E        PR        DA        DB  NOT_USED\n")
    f.write(f"{mid:>10d}{ro:>10.3E}{E:>10.0f}{pr:>10.2f}       0.0       0.0       0.0\n")
    f.write("$\n")


# ============================================================
# 열 재료 작성
# ============================================================

def _write_thermal_iso(f: TextIO, tmid: int, name: str,
                       ro: float, hc: float, tc: float,
                       tlat: float = 0.0, hlat: float = 0.0) -> None:
    f.write(f"$--- TMID {tmid}: {name} ---\n")
    f.write("*MAT_THERMAL_ISOTROPIC\n")
    f.write("$     TMID       TRO     TGRLC    TGMULT      TLAT      HLAT\n")
    f.write(f"{tmid:>10d}{ro:>10.3E}         0       0.0{tlat:>10.1f}{hlat:>10.1f}\n")
    f.write("$       HC        TC\n")
    f.write(f"{hc:>10.1f}{tc:>10.5f}\n")
    f.write("$\n")


def _write_thermal_ortho(f: TextIO, tmid: int, name: str,
                         ro: float, hc: float,
                         k1: float, k2: float, k3: float) -> None:
    f.write(f"$--- TMID {tmid}: {name} ---\n")
    f.write("*MAT_THERMAL_ORTHOTROPIC\n")
    f.write("$     TMID       TRO     TGRLC    TGMULT      AOPT      TLAT      HLAT\n")
    f.write(f"{tmid:>10d}{ro:>10.3E}         0       0.0       0.0       0.0       0.0\n")
    f.write("$       HC        K1        K2        K3\n")
    f.write(f"{hc:>10.1f}{k1:>10.4f}{k2:>10.4f}{k3:>10.4f}\n")
    f.write("$       XP        YP        ZP        A1        A2        A3\n")
    f.write("       0.0       0.0       0.0       0.0       0.0       1.0\n")
    f.write("$       D1        D2        D3\n")
    f.write("       1.0       0.0       0.0\n")
    f.write("$\n")


# ============================================================
# EM 재료 카드
# ============================================================

def _write_em_mat(f: TextIO, mid: int, mtype: int, sigma: float = 0.0) -> None:
    f.write("*EM_MAT_001\n")
    f.write("$      MID     MTYPE     SIGMA     EOSID\n")
    if sigma == 0 or sigma == int(sigma):
        f.write(f"{mid:>10d}{mtype:>10d}{sigma:>10.0f}         0\n")
    else:
        f.write(f"{mid:>10d}{mtype:>10d}{sigma:>10.1E}         0\n")
    f.write("$\n")


# ============================================================
# 열팽창 카드
# ============================================================

def _write_thermal_expansion(f: TextIO, pid: int, cte: float, comment: str) -> None:
    f.write("*MAT_ADD_THERMAL_EXPANSION\n")
    f.write(f"$      PID      LCID      MULT\n")
    f.write(f"{pid:>10d}         0{cte:>10.1E}\n")
    f.write(f"$ {comment}\n")
    f.write("$\n")


# ============================================================
# GISSMO 손상 (분리막)
# ============================================================

def _write_gissmo(f: TextIO, mid: int) -> None:
    """IDAM=1 GISSMO 손상 모델 (6 cards: Card1 + HIS + D-diag + D-offdiag + LCSDG + LCSRS)
    
    R16 Vol_II p.2-98: Card 1은 8필드(PDDT, NHIS 포함), 
    HIS/D-matrix는 PDDT=1일 때 값은 무시되지만 카드 자체는 파싱됨.
    """
    f.write("*MAT_ADD_GENERALIZED_DAMAGE\n")
    # Card 1: MID, IDAM, DTYP, REFSZ, NUMFIP, LP2BI, PDDT, NHIS (8 fields)
    f.write("$      MID      IDAM      DTYP     REFSZ    NUMFIP     LP2BI      PDDT      NHIS\n")
    f.write(f"{mid:>10d}         1         1       0.5         1         0         1         1\n")
    # Card 2: HIS1, HIS2, HIS3, IFLG1-4 (7 fields)
    f.write("$     HIS1      HIS2      HIS3     IFLG1     IFLG2     IFLG3     IFLG4\n")
    f.write("         0         0         0         0         0         0         0\n")
    # Card 3: D-diagonal (6 fields)
    f.write("$      D11       D22       D33       D44       D55       D66\n")
    f.write("         0         0         0         0         0         0\n")
    # Card 4a: D-off-diagonal for shell elements (6 fields)
    f.write("$      D12       D21       D24       D42       D14       D41\n")
    f.write("         0         0         0         0         0         0\n")
    # Card 5.1: LCSDG, ECRIT, DMGEXP, DCRIT, FADEXP, LCREG
    f.write("$    LCSDG     ECRIT    DMGEXP     DCRIT    FADEXP     LCREG\n")
    f.write("      7001       0.0       2.0       0.9       1.0         0\n")
    # Card 5.2: LCSRS, SHRF, BIAXF, LCDLIM, MIDFAIL, NFLOC
    f.write("$    LCSRS      SHRF     BIAXF    LCDLIM   MIDFAIL     NFLOC\n")
    f.write("         0       0.0       0.0         0         0         0\n")
    f.write("$\n")


# ============================================================
# 메인 생성 함수
# ============================================================

def _get_val(mat: Dict[str, Any], key: str, default: Any = 0.0) -> Any:
    """YAML 물성 dict에서 값 추출 (dict/scalar 모두 지원)"""
    v = mat.get(key, default)
    if isinstance(v, dict):
        return v.get("value", default)
    return v


def generate_materials(config: Dict[str, Any], output: str = "04_materials.k",
                       em_sigma_tempdep: bool = True,
                       log: logging.Logger | None = None) -> str:
    """04_materials.k 생성.

    Args:
        em_sigma_tempdep: True(기본) = 전극 온도의존 전도도 활성
                          (NMC → FUNCTID -6003, Graphite → -6004, Separator → -6005).
                          False = EM_RANDLES 회로만 사용, 전극 SIGMA=0 (단순 모드).
    """
    log = log or logger
    mat = config["materials"]
    outpath = Path(output)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f,
            "Li-ion Pouch Cell Materials (Structural + Thermal + EM)",
            "단위: mm, ton(1e3 kg), s, N, MPa, mJ")
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ── Structural ──
        write_separator(f, "STRUCTURAL MATERIALS")

        # MID 1: Al CC — Johnson-Cook
        al = mat["aluminum_cc"]
        _write_mat_johnson_cook(f, MID.AL, al, "Al CC (Johnson-Cook)")

        # MID 2: Cu CC — Johnson-Cook
        cu = mat["copper_cc"]
        cu_jc = cu.get("johnson_cook", {})
        if not cu_jc:
            # Inject defaults for Cu if not in YAML
            cu = dict(cu)
            cu["johnson_cook"] = {
                "A": 200.0, "B": 292.0, "N": 0.31, "C": 0.025,
                "M": 1.09, "TM": 1356.0, "TR": 298.15,
                "damage": {"D1": 0.54, "D2": 4.89, "D3": -3.03, "D4": 0.014, "D5": 1.12},
            }
        _write_mat_johnson_cook(f, MID.CU, cu, "Cu CC (Johnson-Cook)")

        # MID 3: NMC Cathode — PLP with LCSS crush curve (TSHELL compatible)
        # MAT_063/057 incompatible with TSHELL → using MAT_024 with LCSS
        nmc = mat["nmc_cathode"]
        _write_mat_piecewise(f, MID.NMC, "NMC Cathode (PLP with crush curve)",
                             nmc, cs_C=0.0, cs_P=0.0, fail=0.3, lcss=1001)

        # MID 4: Graphite Anode — PLP with LCSS crush curve (TSHELL compatible)
        gr = mat["graphite_anode"]
        _write_mat_piecewise(f, MID.GRAPHITE, "Graphite Anode (PLP with crush curve)",
                             gr, cs_C=0.0, cs_P=0.0, fail=0.3, lcss=1002)

        # MID 5: Separator — Piecewise Linear
        sep = mat["separator"]
        _write_mat_piecewise(f, MID.SEPARATOR, "PE Separator (PLP)",
                             sep, cs_C=100.0, cs_P=4.0, fail=0.3)

        # MID 6: Pouch
        pch = mat["pouch"]
        _write_mat_piecewise(f, MID.POUCH, "Pouch (Al-laminate)",
                             pch, cs_C=6500.0, cs_P=4.0, fail=0.4)

        # Erosion for Al/Cu CC: max effective strain = 0.4
        _write_mat_add_erosion(f, MID.AL, mxeps=0.4)
        _write_mat_add_erosion(f, MID.CU, mxeps=0.4)

        # MID 7: Impactor (Elastic Steel)
        rig = mat["rigid_material"]
        _write_mat_elastic(f, MID.RIGID, rig, "Impactor (Elastic Steel)")

        # MID 8: Electrolyte
        ely = mat["electrolyte"]
        _write_mat_elastic(f, MID.ELECTROLYTE, ely, "Electrolyte (Elastic)")
        # Erosion for electrolyte: max effective strain = 0.1
        _write_mat_add_erosion(f, MID.ELECTROLYTE, mxeps=0.1)

        # ── Thermal ──
        write_separator(f, "THERMAL MATERIALS")

        # Helper: extract thermal conductivity
        def _tc(m):
            tc = _get_val(m, "thermal_conductivity", 0.001)
            return tc

        def _hc(m):
            cp = float(_get_val(m, "specific_heat", 900.0e6))
            return cp / 1e6 if cp > 1e4 else cp

        _write_thermal_iso(f, 101, "Al CC", al["density"],
                           _hc(al), _tc(al))
        _write_thermal_iso(f, 102, "Cu CC", cu["density"],
                           _hc(cu), _tc(cu))
        _write_thermal_ortho(f, 103, "NMC Cathode (aniso)", nmc["density"],
                             700.0, 0.0030, 0.0030, 0.0015)
        _write_thermal_ortho(f, 104, "Graphite Anode (aniso)", gr["density"],
                             700.0, 0.0050, 0.0050, 0.0020)

        sep_hc = _hc(sep)
        _write_thermal_iso(f, 105, "PE Separator", sep["density"],
                           sep_hc, _tc(sep), tlat=403.0, hlat=145000.0)
        _write_thermal_iso(f, 106, "Pouch", pch["density"],
                           _hc(pch), _tc(pch))
        _write_thermal_iso(f, 107, "Rigid (Steel)", rig["density"],
                           477.0, 0.0519)
        _write_thermal_iso(f, 108, "Electrolyte", ely["density"],
                           _hc(ely), _tc(ely))

        # ── EM ──
        write_separator(f, "EM MATERIALS → Phase 3 전용, Phase 1/2에서는 비활성")
        f.write("$ NOTE: EM_MAT_001 disabled for Phase 1 (SP solver, no EM needed)\n$\n")

        # ── GISSMO ──
        write_separator(f, "SEPARATOR SHUTDOWN MODEL (GISSMO)")
        f.write("$ [DISABLED] GISSMO for MID 5 — triple failure causes premature erosion\n$\n")

        # NOTE: Thermal expansion moved to 04_materials_expansion_{type}.k
        # (PID-specific, generated by generate_thermal_expansion)

        f.write("*END\n")

    log.info("04_materials.k 생성 완료: %s", outpath)
    return str(outpath)


# ============================================================
# 열팽창 파일 생성 (모델 타입별 — PID 기반)
# ============================================================

# MID → CTE mapping (non-rigid materials)
_MID_CTE = {
    MID.AL:          23.1e-6,   # Al CC
    MID.CU:          16.5e-6,   # Cu CC
    MID.NMC:          5.0e-6,   # NMC Cathode
    MID.GRAPHITE:     3.0e-6,   # Graphite Anode
    MID.SEPARATOR:  200.0e-6,   # PE Separator
    MID.POUCH:       23.0e-6,   # Pouch
    MID.ELECTROLYTE: 100.0e-6,  # Electrolyte
}

# Layer Type → MID mapping
_LT_MID = {
    LT.AL_CC:     MID.AL,
    LT.CATHODE:   MID.NMC,
    LT.SEPARATOR: MID.SEPARATOR,
    LT.ANODE:     MID.GRAPHITE,
    LT.CU_CC:     MID.CU,
}

# Layer Type → name mapping
_LT_NAME = {
    LT.AL_CC:     "Al CC",
    LT.CATHODE:   "NMC Cathode",
    LT.SEPARATOR: "PE Separator",
    LT.ANODE:     "Graphite Anode",
    LT.CU_CC:     "Cu CC",
}


def generate_thermal_expansion(config: Dict[str, Any],
                               model_type: str = "stacked",
                               tier: float = -1,
                               output: str | None = None,
                               log: logging.Logger | None = None) -> str:
    """04_materials_expansion_{type}[tier].k 생성 (Part ID 기반 열팝시 카드).

    - Stacked: tier마다 UC 수가 다르므로 tier-specific 파일 생성
      (04_materials_expansion_stacked_tier-1.k, etc.)
    - Wound: PID 2001-2005 고정 → tier-independent
      (04_materials_expansion_wound.k 단일 파일)
    """
    log = log or logger
    if output is None:
        if model_type == "stacked":
            output = f"04_materials_expansion_stacked{tier_to_suffix(tier)}.k"
        else:
            output = f"04_materials_expansion_{model_type}.k"
    outpath = Path(output)

    n_cells = get_n_cells_for_tier(config, tier, model_type)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f,
            f"Li-ion Cell - Thermal Expansion ({model_type})",
            f"PID-based *MAT_ADD_THERMAL_EXPANSION — {n_cells} unit cells")
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        write_separator(f, "LAYERED CELL PARTS")

        if model_type == "wound":
            # Wound: single set of PIDs 2001-2005
            for lt in (LT.AL_CC, LT.CATHODE, LT.SEPARATOR, LT.ANODE, LT.CU_CC):
                pid = PID.wound_layer(lt)
                mid = _LT_MID[lt]
                cte = _MID_CTE[mid]
                name = _LT_NAME[lt]
                _write_thermal_expansion(f, pid, cte, f"PID {pid}: {name} (CTE={cte:.1E} /K)")
        else:
            # Stacked: one set per unit cell
            for uc in range(n_cells):
                f.write(f"$ --- Unit Cell {uc} ---\n")
                for lt in (LT.AL_CC, LT.CATHODE, LT.SEPARATOR, LT.ANODE, LT.CU_CC):
                    pid = PID.unit_cell(uc, lt)
                    mid = _LT_MID[lt]
                    cte = _MID_CTE[mid]
                    name = _LT_NAME[lt]
                    _write_thermal_expansion(f, pid, cte, f"PID {pid}: UC{uc} {name}")

        # Special parts (same for both model types)
        write_separator(f, "SPECIAL PARTS")

        # Pouch (PID 10, 11, 12)
        pouch_cte = _MID_CTE[MID.POUCH]
        for pid, label in [(PID.POUCH_TOP, "Pouch Top"),
                           (PID.POUCH_BOTTOM, "Pouch Bottom"),
                           (PID.POUCH_SIDE, "Pouch Side/Wrap")]:
            _write_thermal_expansion(f, pid, pouch_cte, f"PID {pid}: {label}")

        # Electrolyte (PID 13)
        ely_cte = _MID_CTE[MID.ELECTROLYTE]
        _write_thermal_expansion(f, PID.ELECTROLYTE, ely_cte, f"PID {PID.ELECTROLYTE}: Electrolyte")

        # Tabs (PID 20=Al, PID 21=Cu) — Wound mesh only; stacked mesh has no tab parts
        if model_type == "wound":
            _write_thermal_expansion(f, PID.TAB_POS, _MID_CTE[MID.AL],
                                     f"PID {PID.TAB_POS}: Tab Positive (Al)")
            _write_thermal_expansion(f, PID.TAB_NEG, _MID_CTE[MID.CU],
                                     f"PID {PID.TAB_NEG}: Tab Negative (Cu)")

        # PCM boards (rigid → no CTE needed, skip)
        f.write("$ PCM boards (PID 30,31) and Impactor (PID 100) are RIGID — no CTE\n")
        f.write("$\n")

        f.write("*END\n")

    log.info("04_materials_expansion_%s.k 생성 완료: %s", model_type, outpath)
    return str(outpath)


def generate_materials_tempdep(config: Dict[str, Any],
                               output: str = "04_materials_tempdep.k",
                               log: logging.Logger | None = None) -> str:
    """04_materials_tempdep.k 생성 (온도 의존 커브 + 전도도 함수)"""
    log = log or logger
    outpath = Path(output)

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f,
            "Li-ion Cell - Temperature-Dependent Material Data",
            "DEFINE_TABLE (crush), DEFINE_CURVE (GISSMO), DEFINE_FUNCTION (EM sigma)")
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ── TABLE + CURVE blocks ──
        # LS-DYNA: TABLE 뒤에 참조하는 CURVE들이 바로 와야 함
        write_separator(f, "TEMPERATURE-DEPENDENT CRUSH (TABLE → CURVES)")

        nmc_data = [
            (0.0, 0.0), (0.05, 5.0), (0.10, 15.0), (0.15, 35.0),
            (0.20, 70.0), (0.25, 130.0), (0.30, 250.0), (0.35, 500.0),
            (0.40, 1000.0), (0.45, 2000.0), (0.50, 4000.0),
        ]
        gr_data = [
            (0.0, 0.0), (0.05, 8.0), (0.10, 22.0), (0.15, 50.0),
            (0.20, 100.0), (0.25, 200.0), (0.30, 400.0), (0.35, 800.0),
            (0.40, 1500.0), (0.45, 3000.0), (0.50, 5000.0),
        ]

        # TABLE 4003: NMC crush vs Temperature → then its curves
        f.write("$ TABLE 4003: NMC crush vs Temperature\n")
        f.write("*DEFINE_TABLE\n")
        f.write("$    TBID      SPTS\n")
        f.write("      4003\n")
        f.write("$      Temperature(K)   LCID\n")
        for temp, lcid in [(298.0, 4031), (373.0, 4032), (473.0, 4033)]:
            f.write(f"{temp:>20.1f}{lcid:>10d}\n")
        f.write("$\n")
        for lcid, scale, label in [
            (4031, 1.0, "298K"), (4032, 0.7, "373K"), (4033, 0.4, "473K")
        ]:
            f.write(f"*DEFINE_CURVE_TITLE\n")
            f.write(f"NMC Crush @ {label}\n")
            f.write(f"$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP\n")
            f.write(f"{lcid:>10d}         0       1.0       1.0       0.0       0.0         0\n")
            for x, y in nmc_data:
                f.write(f"{x:>20.3f}{y * scale:>16.2f}\n")
            f.write("$\n")

        # TABLE 4004: Graphite crush vs Temperature → then its curves
        f.write("$ TABLE 4004: Graphite crush vs Temperature\n")
        f.write("*DEFINE_TABLE\n")
        f.write("$    TBID      SPTS\n")
        f.write("      4004\n")
        f.write("$      Temperature(K)   LCID\n")
        for temp, lcid in [(298.0, 4041), (373.0, 4042), (473.0, 4043)]:
            f.write(f"{temp:>20.1f}{lcid:>10d}\n")
        f.write("$\n")
        for lcid, scale, label in [
            (4041, 1.0, "298K"), (4042, 0.65, "373K"), (4043, 0.35, "473K")
        ]:
            f.write(f"*DEFINE_CURVE_TITLE\n")
            f.write(f"Graphite Crush @ {label}\n")
            f.write(f"$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP\n")
            f.write(f"{lcid:>10d}         0       1.0       1.0       0.0       0.0         0\n")
            for x, y in gr_data:
                f.write(f"{x:>20.3f}{y * scale:>16.2f}\n")
            f.write("$\n")

        # ── GISSMO damage curve ──
        write_separator(f, "GISSMO DAMAGE CURVE")
        f.write("*DEFINE_CURVE_TITLE\n")
        f.write("GISSMO Critical Strain vs Triaxiality\n")
        f.write("$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP\n")
        f.write("      7001         0       1.0       1.0       0.0       0.0         0\n")
        for eta, eps in [(-0.333, 1.2), (0.0, 0.8), (0.333, 0.55), (0.667, 0.35), (1.0, 0.25)]:
            f.write(f"{eta:>20.3f}{eps:>16.2f}\n")
        f.write("$\n")

        # EM sigma functions → 별도 파일 (04_materials_em_functions.k, Phase 3 전용)
        # SP 기본 솔버에서 *DEFINE_FUNCTION 미지원, Phase 2에서 에러 방지

        f.write("*END\n")

    log.info("04_materials_tempdep.k 생성 완료: %s", outpath)
    return str(outpath)


def _write_sigma_functions(f: TextIO) -> None:
    """EM 전도도 DEFINE_FUNCTION 블록 (// 주석 사용)"""
    funcs = [
        (6001, "sigma_al", 3.5e7, 0.0038, "Al CC"),
        (6002, "sigma_cu", 5.96e7, 0.0039, "Cu CC"),
        (6003, "sigma_nmc", 0.5, 0.001, "NMC Cathode"),
        (6004, "sigma_gr", 3.0e4, 0.0005, "Graphite Anode"),
        (6005, "sigma_sep", 1.0e-10, 0.0, "Separator (insulator)"),
        (6008, "sigma_elyte", 1.0, 0.02, "Electrolyte"),
    ]
    for fid, fname, sigma0, alpha, desc in funcs:
        f.write(f"$ FUNCTID {fid}: {desc}\n")
        f.write("*DEFINE_FUNCTION\n")
        f.write(f"      {fid}\n")
        f.write(f"float {fname}(float x, float y, float z, float temp)\n")
        f.write("{\n")
        if alpha > 0:
            f.write(f"    // {desc}: sigma = sigma0 / (1 + alpha*(T-298))\n")
            f.write(f"    float sigma0 = {sigma0:.4E};\n")
            f.write(f"    float alpha  = {alpha};\n")
            f.write(f"    float T_ref  = 298.15;\n")
            f.write(f"    float ratio  = 1.0 + alpha * (temp - T_ref);\n")
            f.write(f"    if (ratio < 0.1) ratio = 0.1;\n")
            f.write(f"    return sigma0 / ratio;\n")
        else:
            f.write(f"    // {desc}: constant\n")
            f.write(f"    return {sigma0:.4E};\n")
        f.write("}\n")
        f.write("$\n")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="04_materials*.k 생성")
    add_common_args(parser)
    parser.add_argument("--type", choices=["stacked", "wound"], default=None,
                        help="모델 타입 (thermal expansion 생성 시 필요)")
    parser.add_argument("--em-sigma-simplified", action="store_true", default=False,
                        help="전극 EM_MAT SIGMA=0 (단순 모드). 기본은 온도의존 FUNCTID 연결.")
    args = parser.parse_args()

    log = setup_logger("gen_mat",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)

    config = load_config(args.config, validate=True, logger=log)
    generate_materials(config, output="04_materials.k",
                       em_sigma_tempdep=not args.em_sigma_simplified, log=log)
    generate_materials_tempdep(config, output="04_materials_tempdep.k", log=log)

    # Thermal expansion (model-type-specific)
    if args.type:
        generate_thermal_expansion(config, model_type=args.type,
                                   tier=args.tier, log=log)
    else:
        for mt in ("stacked", "wound"):
            generate_thermal_expansion(config, model_type=mt,
                                       tier=args.tier, log=log)


if __name__ == "__main__":
    main()
