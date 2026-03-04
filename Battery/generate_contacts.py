"""
LS-DYNA 배터리 접촉 k-file 자동 생성기 (YAML 설정 기반)
===========================================================
적층형(Stacked) / 와인딩형(Wound) 모델의 TIED 층간 접합 자동 생성

설정: battery_config.yaml 파일에서 모든 파라미터 로드

Usage:
  python generate_contacts.py --config battery_config.yaml --tier 0 --phase all
  python generate_contacts.py --type stacked --n-uc 15 --phase 3
  python generate_contacts.py --type both --n-uc 15 --phase all
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any

from battery_utils import (
    LT as _LT, PID as _PID, PSET as _PSET,
    tier_to_yaml_key, tier_to_suffix,
    load_config, setup_logger,
)

logger = logging.getLogger(__name__)


# ============================================================
# PID / PSET 상수 (메시 생성기와 동기화)
# ============================================================
# 상수 — battery_utils에서 가져온 호환 별칭
LT_AL_CC     = _LT.AL_CC
LT_CATHODE   = _LT.CATHODE
LT_SEPARATOR = _LT.SEPARATOR
LT_ANODE     = _LT.ANODE
LT_CU_CC     = _LT.CU_CC

PID_POUCH_TOP    = _PID.POUCH_TOP
PID_POUCH_BOTTOM = _PID.POUCH_BOTTOM
PID_POUCH_SIDE   = _PID.POUCH_SIDE
PID_IMPACTOR     = _PID.IMPACTOR

# PSET SID
PSET_IMPACTOR    = _PSET.IMPACTOR
PSET_POUCH       = _PSET.POUCH
PSET_ALL_CELL    = _PSET.ALL_CELL
PSET_ALL_CATHODE = _PSET.ALL_CATHODE
PSET_ALL_ANODE   = _PSET.ALL_ANODE


def write_header(f, title: str) -> None:
    f.write("*KEYWORD\n")
    f.write("*TITLE\n")
    f.write(f"{title}\n")
    f.write("$\n")


def write_separator(f, text: str) -> None:
    f.write(f"$\n$ {'='*60}\n$ {text}\n$ {'='*60}\n$\n")


def write_impactor_contact(f, fs: float = 0.30, fd: float = 0.20) -> None:
    """CID 1: 임팩터 ↔ 파우치 ASTS"""
    write_separator(f, "1. 임팩터 ↔ 파우치 충돌")
    f.write("*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID\n")
    f.write("$      CID     TITLE\n")
    f.write("         1Impactor to Pouch\n")
    f.write("$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR\n")
    f.write(f"       {PSET_IMPACTOR}       {PSET_POUCH}         2         2         0         0         1         1\n")
    f.write("$       FS        FD        DC        VC       VDC    PENCHK        BT        DT\n")
    f.write(f"      {fs:4.2f}      {fd:4.2f}       0.0       0.0      40.0         2       0.0  1.0E+20\n")
    f.write("$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF\n")
    f.write("      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$ Optional Card A: SOFT=0 penalty\n")
    f.write("$     SOFT    SOFSCL    LCIDAB    MAXPAR     SBOPT     DEPTH     BSORT    FRCFRQ\n")
    f.write("         0       1.0         0     1.375         3         5         0         1\n")


def write_self_contact(f, fs: float = 0.20, fd: float = 0.15) -> None:
    """CID 2: 셀 내부 자기접촉 ASS"""
    write_separator(f, "2. 셀 내부 자기접촉")
    f.write("*CONTACT_AUTOMATIC_SINGLE_SURFACE_ID\n")
    f.write("$      CID     TITLE\n")
    f.write("         2Cell Internal Self-Contact\n")
    f.write("$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR\n")
    f.write(f"       {PSET_ALL_CELL}         0         2         0         0         0         0         0\n")
    f.write("$       FS        FD        DC        VC       VDC    PENCHK        BT        DT\n")
    f.write(f"      {fs:4.2f}      {fd:4.2f}       0.0       0.0      40.0         2       0.0  1.0E+20\n")
    f.write("$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF\n")
    f.write("      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$ Optional Card A: SOFT=0 penalty (avoid segment-timestep issue with eroded TSHELL)\n")
    f.write("$     SOFT    SOFSCL    LCIDAB    MAXPAR     SBOPT     DEPTH     BSORT    FRCFRQ\n")
    f.write("         0       0.1         0     1.375         3         5         0         1\n")


def write_tied_thermal(f, cid: int, title: str, ssid: int, msid: int, k_val: float) -> None:
    """단일 TIED_SURFACE_TO_SURFACE_THERMAL 접촉 카드"""
    f.write("*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL_ID\n")
    f.write(f"{cid:>10d}{title}\n")
    f.write(f"{ssid:>10d}{msid:>10d}         3         3         0         0         0         0\n")
    f.write("       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20\n")
    f.write("       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write(f"{k_val:>10.1f}       0.0       0.0       0.0       0.0       0.5         0         0\n")


def write_tied_nonthermal(f, cid: int, title: str, ssid: int, msid: int) -> None:
    """TIED_SURFACE_TO_SURFACE (비열적) — Phase 1 구조만"""
    f.write("*CONTACT_TIED_SURFACE_TO_SURFACE_ID\n")
    f.write(f"{cid:>10d}{title}\n")
    f.write(f"{ssid:>10d}{msid:>10d}         3         3         0         0         0         0\n")
    f.write("       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20\n")
    f.write("       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0\n")


def write_stacked_tied_contacts(f, n_uc: int, thermal: bool = True, 
                                 k_metal_metal: float = 100.0,
                                 k_coating_sep: float = 50.0,
                                 k_inter_uc: float = 80.0) -> None:
    """적층형 모델 전체 TIED 접합 생성
    
    Args:
        n_uc: 단위셀 수
        thermal: True=TIED_THERMAL, False=TIED (비열적)
        k_metal_metal: Al↔cathode, anode↔Cu 열전도도 (W/mm·K)
        k_coating_sep: cathode↔sep, sep↔anode 열전도도 (W/mm·K)
        k_inter_uc: UC 간 Cu↔Al 열전도도 (W/mm·K)
    """
    cid = 301

    for uc in range(n_uc):
        base = 1000 + uc * 10
        pid_al   = base + LT_AL_CC
        pid_cath = base + LT_CATHODE
        pid_sep  = base + LT_SEPARATOR
        pid_an   = base + LT_ANODE
        pid_cu   = base + LT_CU_CC

        f.write(f"$\n$ --- Unit Cell {uc} (PID {pid_al}~{pid_cu}) ---\n")

        # 1) Al ↔ Cathode
        if thermal:
            write_tied_thermal(f, cid, f"Al-CC to Cathode UC{uc}", pid_al, pid_cath, k_metal_metal)
        else:
            write_tied_nonthermal(f, cid, f"Al-CC to Cathode UC{uc}", pid_al, pid_cath)
        cid += 1

        # 2) Cathode ↔ Separator
        if thermal:
            write_tied_thermal(f, cid, f"Cathode to Sep UC{uc}", pid_cath, pid_sep, k_coating_sep)
        else:
            write_tied_nonthermal(f, cid, f"Cathode to Sep UC{uc}", pid_cath, pid_sep)
        cid += 1

        # 3) Separator ↔ Anode
        if thermal:
            write_tied_thermal(f, cid, f"Sep to Anode UC{uc}", pid_sep, pid_an, k_coating_sep)
        else:
            write_tied_nonthermal(f, cid, f"Sep to Anode UC{uc}", pid_sep, pid_an)
        cid += 1

        # 4) Anode ↔ Cu
        if thermal:
            write_tied_thermal(f, cid, f"Anode to Cu-CC UC{uc}", pid_an, pid_cu, k_metal_metal)
        else:
            write_tied_nonthermal(f, cid, f"Anode to Cu-CC UC{uc}", pid_an, pid_cu)
        cid += 1

        # 5) Inter-UC: Cu(uc) ↔ Al(uc+1) — except last UC
        if uc < n_uc - 1:
            next_al = 1000 + (uc + 1) * 10 + LT_AL_CC
            if thermal:
                write_tied_thermal(f, cid, f"Cu UC{uc} to Al UC{uc+1}", pid_cu, next_al, k_inter_uc)
            else:
                write_tied_nonthermal(f, cid, f"Cu UC{uc} to Al UC{uc+1}", pid_cu, next_al)
            cid += 1

    total = n_uc * 4 + (n_uc - 1)
    f.write(f"$\n$ --- Total TIED contacts: {total} (CID 301~{300 + total}) ---\n")


def write_wound_tied_contacts(f, thermal: bool = True,
                              k_metal_metal: float = 100.0,
                              k_coating_sep: float = 50.0) -> None:
    """와인딩형 모델 TIED 접합 (단일 PID 세트: 2001~2005)
    
    연속 나선이므로 레이어 간 4개만 필요 (inter-UC 없음)
    """
    base = 2000
    pid_al   = base + LT_AL_CC
    pid_cath = base + LT_CATHODE
    pid_sep  = base + LT_SEPARATOR
    pid_an   = base + LT_ANODE
    pid_cu   = base + LT_CU_CC

    cid = 301

    f.write(f"$\n$ --- Wound Jellyroll (PID {pid_al}~{pid_cu}, 연속나선) ---\n")

    if thermal:
        write_tied_thermal(f, cid, "Al-CC to Cathode", pid_al, pid_cath, k_metal_metal)
        cid += 1
        write_tied_thermal(f, cid, "Cathode to Separator", pid_cath, pid_sep, k_coating_sep)
        cid += 1
        write_tied_thermal(f, cid, "Separator to Anode", pid_sep, pid_an, k_coating_sep)
        cid += 1
        write_tied_thermal(f, cid, "Anode to Cu-CC", pid_an, pid_cu, k_metal_metal)
    else:
        write_tied_nonthermal(f, cid, "Al-CC to Cathode", pid_al, pid_cath)
        cid += 1
        write_tied_nonthermal(f, cid, "Cathode to Separator", pid_cath, pid_sep)
        cid += 1
        write_tied_nonthermal(f, cid, "Separator to Anode", pid_sep, pid_an)
        cid += 1
        write_tied_nonthermal(f, cid, "Anode to Cu-CC", pid_an, pid_cu)

    f.write("$\n$ --- Total TIED contacts: 4 (CID 301~304) ---\n")


def write_eroding_contact(f) -> None:
    """CID 401: 분리막 삭제 후 양극-음극 ERODING"""
    write_separator(f, "ERODING 접촉 (분리막 erosion 후)")
    f.write("*CONTACT_ERODING_SURFACE_TO_SURFACE_ID\n")
    f.write("$      CID     TITLE\n")
    f.write("       401Eroding - Separator Region\n")
    f.write("$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR\n")
    f.write(f"       {PSET_ALL_CATHODE}       {PSET_ALL_ANODE}         2         2         0         0         1         1\n")
    f.write("$       FS        FD        DC        VC       VDC    PENCHK        BT        DT\n")
    f.write("      0.30      0.20       0.0       0.0       0.0         2       0.0  1.0E+20\n")
    f.write("$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF\n")
    f.write("      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$     ISYM    EROSOP      IADJ\n")
    f.write("         0         1         1\n")


def write_nail_eroding_contact(f) -> None:
    """CID 402: 네일 임팩터 ↔ 전체 셀 ERODING (관통 시뮬레이션)
    
    네일은 셀 층을 직접 관통하므로 ERODING_SURFACE_TO_SURFACE 필요.
    기존 CID 1(ASTS)는 파우치 표면 접촉용, CID 402는 관통 후 내부 접촉용.
    """
    write_separator(f, "네일 관통 접촉 (B12)")
    f.write("*CONTACT_ERODING_SURFACE_TO_SURFACE_ID\n")
    f.write("$      CID     TITLE\n")
    f.write("       402Nail Penetration - All Cell\n")
    f.write("$     SSID      MSID     SSTYP     MSTYP    SBOXID    MBOXID       SPR       MPR\n")
    f.write(f"       {PSET_IMPACTOR}       {PSET_ALL_CELL}         2         2         0         0         1         1\n")
    f.write("$       FS        FD        DC        VC       VDC    PENCHK        BT        DT\n")
    f.write("      0.30      0.20       0.0       0.0       0.0         2       0.0  1.0E+20\n")
    f.write("$      SFS       SFM       SST       MST      SFST      SFMT       FSF       VSF\n")
    f.write("      1.00      1.00       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$     ISYM    EROSOP      IADJ\n")
    f.write("         0         1         1\n")
    f.write("$ Optional Card A:\n")
    f.write("$     SOFT    SOFSCL    LCIDAB    MAXPAR     SBOPT     DEPTH     BSORT    FRCFRQ\n")
    f.write("         2       0.1         0     1.375         4         5         0         1\n")
    f.write("$ SOFT=2: segment-based, 관통 시뮬레이션에 필수\n")
    f.write("$ DEPTH=5: 관통 깊이 확인 (all layers)\n")


def write_pouch_tied_stacked(f, n_uc: int) -> None:
    """CID 501~502: 파우치 ↔ 셀스택 TIED (적층형만)"""
    write_separator(f, "파우치 ↔ 셀 스택 접합")
    top_pid = 1000 + (n_uc - 1) * 10 + LT_CU_CC  # 최상위 UC의 Cu CC

    write_tied_nonthermal(f, 501, "Pouch Bottom to Stack",
                          PID_POUCH_BOTTOM, 1001)
    write_tied_nonthermal(f, 502, "Pouch Top to Stack",
                          PID_POUCH_TOP, top_pid)


def write_pouch_tied_wound(f) -> None:
    """CID 501~502: 파우치 ↔ 젤리롤 TIED (와인딩형)"""
    write_separator(f, "파우치 ↔ 젤리롤 접합")
    # 와인딩형: 파우치 캡이 젤리롤 전체와 접합
    write_tied_nonthermal(f, 501, "Pouch Bottom to Jelly",
                          PID_POUCH_BOTTOM, 2001)
    write_tied_nonthermal(f, 502, "Pouch Top to Jellyroll",
                          PID_POUCH_TOP, 2005)


# PSET SID for EM materials
PSET_ALL_AL_CC   = 106
PSET_ALL_CU_CC   = 107


def write_pcm_contacts(f) -> None:
    """CID 601~602: PCM ↔ 탭 TIED (적층형만)
    
    PCM Positive (PID 30) → Al 집전체 탭 면 (PSET 106)
    PCM Negative (PID 31) → Cu 집전체 탭 면 (PSET 107)
    SSTYP=3 (part ID), MSTYP=2 (part set)
    """
    write_separator(f, "PCM ↔ 탭 접합 (적층형 전용)")
    f.write("*CONTACT_TIED_NODES_TO_SURFACE_ID\n")
    f.write("       601PCM Positive to Al Tab\n")
    f.write(f"        30       {PSET_ALL_AL_CC}         3         2         0         0         0         0\n")
    f.write("       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20\n")
    f.write("       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0\n")
    f.write("$\n")
    f.write("*CONTACT_TIED_NODES_TO_SURFACE_ID\n")
    f.write("       602PCM Negative to Cu Tab\n")
    f.write(f"        31       {PSET_ALL_CU_CC}         3         2         0         0         0         0\n")
    f.write("       0.0       0.0       0.0       0.0       0.0         0       0.0  1.0E+20\n")
    f.write("       1.0       1.0       0.0       0.0       0.0       0.0       0.0       0.0\n")


# ============================================================
# 메인 생성 함수
# ============================================================

def generate_stacked_contacts(outdir: Path, n_uc: int, phases: list, nail: bool = False, suffix: str = "", config: Dict[str, Any] = None) -> None:
    """적층형 접촉 k-file 생성"""
    
    # YAML에서 friction, thermal conductance 로드
    if config:
        friction = config.get('contacts', {}).get('friction', {})
        fs_imp = friction.get('static', 0.30)
        fd_imp = friction.get('dynamic', 0.20)
        fs_self = friction.get('static', 0.30) * 0.67  # 자기접촉은 약간 낮게
        fd_self = friction.get('dynamic', 0.20) * 0.75
        
        thermal_cond = config.get('contacts', {}).get('thermal_conductance', {})
        k_metal = thermal_cond.get('metal_to_metal', 100.0)
        k_coating = thermal_cond.get('coating_to_separator', 50.0)
        k_inter = thermal_cond.get('inter_unit_cell', 80.0)
    else:
        fs_imp, fd_imp = 0.30, 0.20
        fs_self, fd_self = 0.20, 0.15
        k_metal, k_coating, k_inter = 100.0, 50.0, 80.0
    
    if 1 in phases:
        fname = outdir / f"05_contacts_phase1{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, "Li-ion Cell - Contacts Phase 1: Mechanical Only (Stacked)")
            write_separator(f, "Phase 1: 임팩터 + 자기접촉만")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            f.write("$\n*END\n")
        print(f"  [Stacked] Phase 1 contacts → {fname.name}")

    if 2 in phases:
        fname = outdir / f"05_contacts_phase2{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, f"Li-ion Cell - Contacts Phase 2: Thermo-Mechanical (Stacked, {n_uc} UC)")
            write_separator(f, f"Phase 2: 전체 접촉 (TIED THERMAL, {n_uc} UC)")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            write_separator(f, f"층간 TIED THERMAL 접합 ({n_uc} 단위셀)")
            write_stacked_tied_contacts(f, n_uc, thermal=True, k_metal_metal=k_metal, k_coating_sep=k_coating, k_inter_uc=k_inter)
            write_eroding_contact(f)
            write_pouch_tied_stacked(f, n_uc)
            write_pcm_contacts(f)
            f.write("$\n*END\n")
        print(f"  [Stacked] Phase 2 contacts → {fname.name} ({n_uc*4 + n_uc-1} TIED)")

    if 3 in phases:
        fname = outdir / f"05_contacts{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, f"Li-ion Cell - Contacts Phase 3: Full Coupled (Stacked, {n_uc} UC)")
            write_separator(f, f"Phase 3: 전체 접촉 (TIED THERMAL, {n_uc} UC)")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            write_separator(f, f"층간 TIED THERMAL 접합 ({n_uc} 단위셀)")
            write_stacked_tied_contacts(f, n_uc, thermal=True, k_metal_metal=k_metal, k_coating_sep=k_coating, k_inter_uc=k_inter)
            write_eroding_contact(f)
            write_pouch_tied_stacked(f, n_uc)
            write_pcm_contacts(f)
            f.write("$\n*END\n")
        print(f"  [Stacked] Phase 3 contacts → {fname.name} ({n_uc*4 + n_uc-1} TIED)")


def generate_wound_contacts(outdir: Path, phases: list, nail: bool = False, suffix: str = "", config: Dict[str, Any] = None) -> None:
    """와인딩형 접촉 k-file 생성"""
    
    # YAML에서 friction, thermal conductance 로드
    if config:
        friction = config.get('contacts', {}).get('friction', {})
        fs_imp = friction.get('static', 0.30)
        fd_imp = friction.get('dynamic', 0.20)
        fs_self = friction.get('static', 0.30) * 0.67
        fd_self = friction.get('dynamic', 0.20) * 0.75
        
        thermal_cond = config.get('contacts', {}).get('thermal_conductance', {})
        k_metal = thermal_cond.get('metal_to_metal', 100.0)
        k_coating = thermal_cond.get('coating_to_separator', 50.0)
    else:
        fs_imp, fd_imp = 0.30, 0.20
        fs_self, fd_self = 0.20, 0.15
        k_metal, k_coating = 100.0, 50.0
    
    if 1 in phases:
        fname = outdir / f"05_contacts_phase1_wound{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, "Li-ion Cell - Contacts Phase 1: Mechanical Only (Wound)")
            write_separator(f, "Phase 1: 임팩터 + 자기접촉만")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            f.write("$\n*END\n")
        print(f"  [Wound] Phase 1 contacts → {fname.name}")

    if 2 in phases:
        fname = outdir / f"05_contacts_phase2_wound{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, "Li-ion Cell - Contacts Phase 2: Thermo-Mechanical (Wound)")
            write_separator(f, "Phase 2: 전체 접촉 (TIED THERMAL, 연속나선)")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            write_separator(f, "층간 TIED THERMAL 접합 (와인딩 연속나선)")
            write_wound_tied_contacts(f, thermal=True, k_metal_metal=k_metal, k_coating_sep=k_coating)
            write_eroding_contact(f)
            write_pouch_tied_wound(f)
            f.write("$\n*END\n")
        print(f"  [Wound] Phase 2 contacts → {fname.name} (4 TIED)")

    if 3 in phases:
        fname = outdir / f"05_contacts_wound{suffix}.k"
        with open(fname, "w", encoding="utf-8") as f:
            write_header(f, "Li-ion Cell - Contacts Phase 3: Full Coupled (Wound)")
            write_separator(f, "Phase 3: 전체 접촉 (TIED THERMAL, 연속나선)")
            write_impactor_contact(f, fs_imp, fd_imp)
            write_self_contact(f, fs_self, fd_self)
            if nail:
                write_nail_eroding_contact(f)
            write_separator(f, "층간 TIED THERMAL 접합 (와인딩 연속나선)")
            write_wound_tied_contacts(f, thermal=True, k_metal_metal=k_metal, k_coating_sep=k_coating)
            write_eroding_contact(f)
            write_pouch_tied_wound(f)
            f.write("$\n*END\n")
        print(f"  [Wound] Phase 3 contacts → {fname.name} (4 TIED)")


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 배터리 접촉 k-file 생성기 (YAML 설정 기반)")
    parser.add_argument("--config", type=str, default=None,
                        help="YAML 설정 파일 경로 (기본: battery_config.yaml)")
    parser.add_argument("--tier", type=float, default=None,
                        help="티어 (-1, 0, 0.5, 1, 2) --config와 함께 사용")
    parser.add_argument("--type", choices=["stacked", "wound", "both"],
                        default="both", help="모델 타입 (default: both)")
    parser.add_argument("--n-uc", type=int, default=None,
                        help="단위셀 수 (직접 지정 또는 tier에서 자동)")
    parser.add_argument("--phase", nargs="+", default=["all"],
                        help="Phase 번호: 1 2 3 또는 all (default: all)")
    parser.add_argument("--outdir", type=str, default=".",
                        help="출력 디렉토리 (default: 현재)")
    parser.add_argument("--output-suffix", type=str, default=None,
                        help="출력 파일명 suffix (예: _tier0, None이면 tier 기반 자동)")
    parser.add_argument("--nail", action="store_true",
                        help="네일 관통 접촉 추가 (B12: CONTACT_ERODING CID 402)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    parser.add_argument("--log-file", type=str, default=None, help="파일 로그")
    args = parser.parse_args()

    log = setup_logger(
        "contacts",
        level=logging.DEBUG if args.verbose else logging.INFO,
        log_file=args.log_file,
    )

    try:
        # YAML 설정 로드 (옵션)
        config = None
        if args.config or (args.tier is not None and args.n_uc is None):
            config_path = args.config or "battery_config.yaml"
            config = load_config(config_path, validate=True, logger=log)

            if args.tier is not None:
                tier_map = config['geometry']['stacked']['stacking']['tier_definitions']
                tier_key = tier_to_yaml_key(args.tier)
                tier_def = tier_map.get(tier_key, {})
                n_uc = tier_def.get('n_cells', config['geometry']['stacked']['stacking']['default_n_cells']) if isinstance(tier_def, dict) else config['geometry']['stacked']['stacking']['default_n_cells']

                if args.output_suffix is None:
                    args.output_suffix = config['output_files']['mesh']['tier_suffixes'].get(
                        tier_key, tier_to_suffix(args.tier)
                    )
            else:
                n_uc = args.n_uc if args.n_uc else 15
        else:
            n_uc = args.n_uc if args.n_uc else 15

        if args.output_suffix is None:
            args.output_suffix = ""

        # Phase 파싱
        if "all" in args.phase:
            phases = [1, 2, 3]
        else:
            phases = [int(p) for p in args.phase]

        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        log.info("배터리 접촉 k-file 생성 | 타입: %s | UC: %d | Phase: %s%s%s",
                 args.type, n_uc, phases,
                 f" | Tier: {args.tier}" if args.tier is not None else "",
                 " | 네일" if args.nail else "")

        if args.type in ("stacked", "both"):
            generate_stacked_contacts(outdir, n_uc, phases, nail=args.nail,
                                      suffix=args.output_suffix, config=config)

        if args.type in ("wound", "both"):
            # Wound contacts는 tier에 무관 (PID 고정) → suffix 없이 생성
            generate_wound_contacts(outdir, phases, nail=args.nail,
                                    suffix="", config=config)

        log.info("완료!")

    except FileNotFoundError as e:
        log.error("%s", e)
        sys.exit(1)
    except (KeyError, ValueError, OSError) as e:
        log.error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
