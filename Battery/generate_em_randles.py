"""
EM Randles 회로 k-file 자동 생성 스크립트
========================================
주어진 단위셀(UC) 수에 맞춰 08_em_randles.k 파일 생성

설정: battery_config.yaml 파일에서 모든 파라미터 로드

사용법:
    python generate_em_randles.py --config battery_config.yaml --tier -1
    python generate_em_randles.py --config battery_config.yaml --tier -1 --em-step 1
    python generate_em_randles.py --model-type wound --n-uc 1
    python generate_em_randles.py --n-uc 5 --output 08_em_randles.k
"""

import argparse
import sys
import logging
from typing import TextIO

from battery_utils import (
    tier_to_yaml_key, tier_to_suffix,
    load_config, setup_logger,
    LT as _LT, PID as _PID,
)

logger = logging.getLogger(__name__)

# ============================================================
# SOC × Temperature 2D TABLE 데이터
# 08_em_randles.k (tier 0, 수동검증)에서 추출
# ============================================================
_TEMPS = [273.15, 298.15, 323.15, 373.15, 473.15]  # 5개 온도점 (K)

# TABLE 8001: R0 충전 (R0CHA) — SOC(0~1) vs R0(Ω)
_R0CHA = {
    273.15: [(0.0, 0.060), (0.2, 0.050), (0.5, 0.045), (0.8, 0.050), (1.0, 0.060)],
    298.15: [(0.0, 0.035), (0.2, 0.030), (0.5, 0.028), (0.8, 0.030), (1.0, 0.035)],
    323.15: [(0.0, 0.025), (0.2, 0.020), (0.5, 0.018), (0.8, 0.020), (1.0, 0.025)],
    373.15: [(0.0, 0.015), (0.2, 0.012), (0.5, 0.010), (0.8, 0.012), (1.0, 0.015)],
    473.15: [(0.0, 0.010), (0.2, 0.008), (0.5, 0.006), (0.8, 0.008), (1.0, 0.010)],
}

# TABLE 8002: R0 방전 (R0DIS)
_R0DIS = {
    273.15: [(0.0, 0.065), (0.2, 0.055), (0.5, 0.050), (0.8, 0.055), (1.0, 0.065)],
    298.15: [(0.0, 0.040), (0.2, 0.035), (0.5, 0.032), (0.8, 0.035), (1.0, 0.040)],
    323.15: [(0.0, 0.030), (0.2, 0.025), (0.5, 0.022), (0.8, 0.025), (1.0, 0.030)],
    373.15: [(0.0, 0.018), (0.2, 0.015), (0.5, 0.012), (0.8, 0.015), (1.0, 0.018)],
    473.15: [(0.0, 0.012), (0.2, 0.010), (0.5, 0.008), (0.8, 0.010), (1.0, 0.012)],
}

# TABLE 8003: R1 충전 (R10CHA) — 3-point SOC
_R10CHA = {
    273.15: [(0.0, 0.040), (0.5, 0.035), (1.0, 0.040)],
    298.15: [(0.0, 0.025), (0.5, 0.020), (1.0, 0.025)],
    323.15: [(0.0, 0.018), (0.5, 0.015), (1.0, 0.018)],
    373.15: [(0.0, 0.010), (0.5, 0.008), (1.0, 0.010)],
    473.15: [(0.0, 0.006), (0.5, 0.005), (1.0, 0.006)],
}

# TABLE 8004: R1 방전 (R10DIS)
_R10DIS = {
    273.15: [(0.0, 0.050), (0.5, 0.040), (1.0, 0.050)],
    298.15: [(0.0, 0.030), (0.5, 0.025), (1.0, 0.030)],
    323.15: [(0.0, 0.022), (0.5, 0.018), (1.0, 0.022)],
    373.15: [(0.0, 0.012), (0.5, 0.010), (1.0, 0.012)],
    473.15: [(0.0, 0.008), (0.5, 0.006), (1.0, 0.008)],
}

# TABLE 8005: C1 충전 (C10CHA) — 커패시턴스 (F)
_C10CHA = {
    273.15: [(0.0, 600.0), (0.5, 800.0), (1.0, 600.0)],
    298.15: [(0.0, 800.0), (0.5, 1000.0), (1.0, 800.0)],
    323.15: [(0.0, 1000.0), (0.5, 1200.0), (1.0, 1000.0)],
    373.15: [(0.0, 1200.0), (0.5, 1500.0), (1.0, 1200.0)],
    473.15: [(0.0, 1500.0), (0.5, 2000.0), (1.0, 1500.0)],
}

# TABLE 8006: C1 방전 (C10DIS)
_C10DIS = {
    273.15: [(0.0, 600.0), (0.5, 800.0), (1.0, 600.0)],
    298.15: [(0.0, 800.0), (0.5, 1000.0), (1.0, 800.0)],
    323.15: [(0.0, 1000.0), (0.5, 1200.0), (1.0, 1000.0)],
    373.15: [(0.0, 1200.0), (0.5, 1500.0), (1.0, 1200.0)],
    473.15: [(0.0, 1500.0), (0.5, 2000.0), (1.0, 1500.0)],
}

# TABLE 정의 목록: (TBID, name, data_dict, base_lcid)
_TABLE_DEFS = [
    (8001, "R0CHA", "R0 충전",  _R0CHA,  8010),
    (8002, "R0DIS", "R0 방전",  _R0DIS,  8020),
    (8003, "R10CHA", "R1 충전", _R10CHA, 8030),
    (8004, "R10DIS", "R1 방전", _R10DIS, 8040),
    (8005, "C10CHA", "C1 충전", _C10CHA, 8050),
    (8006, "C10DIS", "C1 방전", _C10DIS, 8060),
]


def write_header(f: TextIO):
    """파일 헤더 및 제어 키워드"""
    f.write("""*KEYWORD
*TITLE
Li-ion Cell - EM Randles Circuit & Electrochemistry
$
$ ============================================================
$ EM + Randles 분포 회로 (EM_RANDLES_SOLID 접근법)
$
$ 전략:
$   - 각 층(CCP, 양극, 분리막, 음극, CCN) 개별 Part 구성
$   - 분리막 erosion → EM_RANDLES_SHORT → 내부 단락
$   - Joule heating → 열솔버 → 온도 피드백
$   - 열폭주: EM_RANDLES_EXOTHERMIC_REACTION
$ ============================================================
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ==================== EM SOLVER CONTROL ====================
$
*EM_CONTROL
$    EMSOL     NUMLS              DIMTYPE    NPERIO            NCYLFEM   NCYLBEM
         3        50                    3         0                  1         0
$
$ EMSOL=3: Resistive heating (배터리 단락 줄열에 적합)
$ DIMTYPE=3: 전도 전용 (BEM 없음, SET_SEGMENT/외부 경계 불필요)
$ NCYLBEM=0: BEM 사이클 없음
$
*EM_CONTROL_COUPLING
$    THCPL     SMCPL     THLCID    SMLCID   THCPLFL   SMCPLFL
         2         0          0         0         0         0
$
$ THCPL=2: Element-level Joule heating (Randles 배터리에 권장)
$ SMCPL=0: Lorentz force OFF (배터리 셀에 불필요, BEM 세그먼트 불필요)
$
*EM_CONTROL_TIMESTEP
$   TSTYPE   DTCONST      LCID    FACTOR     TSMIN     TSMAX     RLCSF    MECATS
         5     0.001         0       1.0   1.0E-06       1.0       0.0         1
$
$ TSTYPE=5: EM 시간스텝 = 열 시간스텝 (동기화)
$
*EM_CONTROL_CONTACT
$     EMCT    CCONLY     CTYPE     DTYPE      EPS1      EPS2      EPS3        D0
         1         0         0         0     0.001     0.001     0.001       0.0
$
$ EM 접촉: 도체 간 접촉 감지 활성화
$
*EM_CONTROL_EROSION
$ 삭제된 요소를 EM 계산에서 제거
$ Card 1: ECTRL (1=ON: 침식 요소를 EM 행렬에서 제거)
         1
$
""")


def write_em_mat(f: TextIO):
    """EM_MAT_001 전기전도도 정의 (MID = 구조재 MID와 일치 필수)"""
    f.write("""$
$ ==================== EM MATERIAL CONDUCTIVITY ====================
$
$ *EM_MAT_001 Card1: MID MTYPE SIGMA SIGY SIGZ EOSID AOPT MACF
$ MTYPE=2: isotropic conductor  |  MTYPE=1: non-conductor (insulator)
$ Field8=MACF (NOT RANDLETYPE). Part roles set by EM_RANDLES_SOLID.
$
*EM_MAT_001
$      MID     MTYPE     SIGMA
         1         2  3.77e+04
$ MID 1: Al CC, conductor, sigma=3.77e4 S/mm
*EM_MAT_001
         2         2  5.96e+04
$ MID 2: Cu CC, conductor, sigma=5.96e4 S/mm
*EM_MAT_001
         3         1
$ MID 3: NMC cathode, non-conductor
*EM_MAT_001
         4         1
$ MID 4: Graphite anode, non-conductor
*EM_MAT_001
         5         1
$ MID 5: PE separator, non-conductor
*EM_MAT_001
         6         1
$ MID 6: Pouch, EM inactive
*EM_MAT_001
         7         1
$ MID 7: PCM/Impactor, EM inactive
*EM_MAT_001
         8         1
$ MID 8: Electrolyte, non-conductor
$
""")


def write_define_tables(f: TextIO):
    """DEFINE_TABLE + DEFINE_CURVE: R0/R1/C1 vs SOC × Temperature (2D 보간)

    LSTC batmac_table 예제 패턴:
      RANDLES 카드에서 음수 값(-8001 등) = TABLE ID 참조
      TABLE: 온도(K) → LCID 매핑
      CURVE: SOC(0~1) vs 파라미터 값
    """
    f.write("$ ==================== SOC×Temperature TABLES ====================\n")
    f.write("$\n")
    f.write("$ LSTC batmac_table 패턴: R0/R1/C1을 SOC×온도 2D TABLE로 정의\n")
    f.write("$ RANDLES 카드에서 음수 값 = TABLE ID 참조\n")
    f.write("$\n")

    for tbid, short_name, desc, data, base_lcid in _TABLE_DEFS:
        f.write(f"$ TABLE {tbid}: {desc} → {short_name}\n")
        f.write("*DEFINE_TABLE\n")
        f.write(f"$     TBID\n")
        f.write(f"{tbid:10d}\n")
        f.write(f"$           Temperature(K)    LCID\n")
        for idx, temp in enumerate(_TEMPS):
            lcid = base_lcid + idx + 1
            f.write(f"{temp:20.2f}{lcid:10d}\n")
        f.write("$\n")

        for idx, temp in enumerate(_TEMPS):
            lcid = base_lcid + idx + 1
            f.write("*DEFINE_CURVE\n")
            f.write(f"{lcid:10d}\n")
            for soc, val in data[temp]:
                f.write(f"{soc:16.1f}{val:16g}\n")

        f.write("$\n")


def _get_pids(uc: int, model_type: str):
    """UC 인덱스와 모델 타입에서 PID 5종 반환"""
    if model_type == "wound":
        pid_base = 2000
    else:
        pid_base = 1000 + uc * 10
    pid_al = pid_base + _LT.AL_CC        # +1
    pid_nmc = pid_base + _LT.CATHODE      # +2
    pid_sep = pid_base + _LT.SEPARATOR    # +3
    pid_graphite = pid_base + _LT.ANODE   # +4
    pid_cu = pid_base + _LT.CU_CC        # +5
    return pid_al, pid_nmc, pid_sep, pid_graphite, pid_cu


def write_randles_circuits(f: TextIO, n_uc: int, model_type: str = "stacked"):
    """EM_RANDLES_SOLID 회로 생성 (TABLE 기반 R0/R1/C1 + SOC Shift)"""
    f.write("$ ==================== RANDLES CIRCUITS ====================\n")
    f.write("$\n")
    f.write("$ R0/R1/C1: 음수 TABLE ID → SOC×Temperature 2D 보간\n")
    f.write("$   -8001: R0CHA, -8002: R0DIS\n")
    f.write("$   -8003: R10CHA, -8004: R10DIS\n")
    f.write("$   -8005: C10CHA, -8006: C10DIS\n")
    f.write("$\n")

    for uc in range(n_uc):
        rdlid = uc + 1
        pid_al, pid_nmc, pid_sep, pid_graphite, pid_cu = _get_pids(uc, model_type)

        if uc == 0:
            f.write(f"$ --- Randles for Unit Cell {uc} ---\n")
            f.write("*EM_RANDLES_SOLID\n")
            f.write("$ Card 1: RDLID, RDLTYPE, RDLAREA, CCPPART, CCNPART, SEPPART, PELPART, NELPART\n")
            f.write("$  RDLID   RDLTYPE   RDLAREA   CCPPART   CCNPART   SEPPART   PELPART   NELPART\n")
            f.write(f"{rdlid:8d}         1         2{pid_al:10d}{pid_cu:10d}{pid_sep:10d}{pid_nmc:10d}{pid_graphite:10d}\n")
            f.write("$\n")
            f.write("$ Card 2: Q, CQ, SOCINIT, SOCTOU\n")
            f.write("$        Q        CQ   SOCINIT    SOCTOU\n")
            f.write("       2.6    2.78E-2       0.5     -2001\n")
            f.write("$\n")
            f.write("$ Card 3: R0/R1/C1 (TABLE 참조)\n")
            f.write("$    R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS\n")
            f.write("     -8001     -8002     -8003     -8004     -8005     -8006\n")
            f.write("$\n")
            f.write("$ Card 5: Thermal coupling\n")
            f.write("$     TEMP    FRTHER    R0TOTH      DUDT     TEMPU\n")
            f.write("    298.15         1         1     -2002         1\n")
            f.write("$\n")
            f.write("$ Card 6: SOC Shift (LSTC basic_socshift 패턴)\n")
            f.write("$  USESOCS   TAUSOCS  SICSLCID\n")
            f.write("         1    1000.0     -2004\n")
        elif uc == 1 and n_uc <= 5:
            f.write("$\n")
            f.write(f"$ --- Randles for Unit Cell {uc} ---\n")
            f.write("*EM_RANDLES_SOLID\n")
            f.write("$  RDLID   RDLTYPE   RDLAREA   CCPPART   CCNPART   SEPPART   PELPART   NELPART\n")
            f.write(f"{rdlid:8d}         1         2{pid_al:10d}{pid_cu:10d}{pid_sep:10d}{pid_nmc:10d}{pid_graphite:10d}\n")
            f.write("$        Q        CQ   SOCINIT    SOCTOU\n")
            f.write("       2.6    2.78E-2       0.5     -2001\n")
            f.write("$    R0CHA     R0DIS    R10CHA    R10DIS    C10CHA    C10DIS\n")
            f.write("     -8001     -8002     -8003     -8004     -8005     -8006\n")
            f.write("$     TEMP    FRTHER    R0TOTH      DUDT     TEMPU\n")
            f.write("    298.15         1         1     -2002         1\n")
            f.write("$  USESOCS   TAUSOCS  SICSLCID\n")
            f.write("         1    1000.0     -2004\n")
        else:
            if uc == 2 and n_uc > 5:
                f.write("$\n")
                f.write(f"$ --- Randles for Unit Cells {uc}~{n_uc-1} (동일 패턴) ---\n")
            f.write("*EM_RANDLES_SOLID\n")
            f.write(f"{rdlid:8d}         1         2{pid_al:10d}{pid_cu:10d}{pid_sep:10d}{pid_nmc:10d}{pid_graphite:10d}\n")
            f.write("       2.6    2.78E-2       0.5     -2001\n")
            f.write("     -8001     -8002     -8003     -8004     -8005     -8006\n")
            f.write("    298.15         1         1     -2002         1\n")
            f.write("         1    1000.0     -2004\n")

    f.write("$\n")
    f.write(f"$ --- Total Randles circuits: {n_uc} (RDLID 1~{n_uc}) ---\n")
    f.write("$\n")


def write_footer(f: TextIO, n_uc: int, model_type: str = "stacked",
                 em_step: int = 3):
    """ISC, 열폭주, ISOPOTENTIAL, 회로, EM_OUTPUT, 데이터베이스

    Args:
        em_step: 1=Randles only, 2=+ISC, 3=+Exothermic (full)
    """
    # ISC
    if em_step >= 2:
        f.write("""$ ==================== INTERNAL SHORT CIRCUIT ====================
$
*EM_RANDLES_SHORT
$  AREATYPE   FUNCTID
         2      5001
$
$ AREATYPE=2: 전체 셀 면적 대비 스케일링
$ FUNCTID=5001: LSTC 20인수 공식 시그니처
$   양수 반환 = 단락 저항(Ω), 음수 반환 = 단락 없음
$
""")
    else:
        f.write("$ ==================== INTERNAL SHORT CIRCUIT ====================\n")
        f.write("$ (Step 1: ISC 비활성 — Step 2에서 활성화)\n")
        f.write("$*EM_RANDLES_SHORT\n")
        f.write("$         2      5001\n")
        f.write("$\n")

    # Exothermic
    if em_step >= 3:
        f.write("""$ ==================== EXOTHERMIC REACTION (열폭주) ====================
$
*EM_RANDLES_EXOTHERMIC_REACTION
$  AREATYPE   FUNCTID
         2      5002
$
$ FUNCTID=5002: LSTC 10인수 공식 시그니처
$   exothermic_reaction_randle(time, temp, SOC, emdt, ocv, curr, volt, r0, vc, H_ex)
$
""")
    else:
        f.write("$ ==================== EXOTHERMIC REACTION (열폭주) ====================\n")
        step_msg = "Step 3" if em_step == 1 else "Step 3"
        f.write(f"$ ({step_msg}에서 활성화)\n")
        f.write("$*EM_RANDLES_EXOTHERMIC_REACTION\n")
        f.write("$         2      5002\n")
        f.write("$\n")

    # ISOPOTENTIAL
    # R16 Vol III p.6-105: SETTYPE: EQ.1=Segment Set, EQ.2=Node Set
    # RDLTYPE: EQ.1=CCP(양극CC), EQ.5=CCN(음극CC)
    f.write("$ ==================== TAB ISOPOTENTIAL (동전위면) ====================\n")
    f.write("$\n")
    f.write(f"$ {n_uc} unit cells → CCP/CCN 각 {n_uc}개 = {n_uc * 2} ISOs\n")
    f.write("$ SETTYPE=2: Node Set (SET_NODE_GENERAL로 Part→Node 변환)\n")
    f.write("$ RDLTYPE: 1=CCP(Al CC), 5=CCN(Cu CC) — R16 Vol III p.6-105\n")
    f.write("$\n")

    # SID 오프셋: 메쉬 파일의 SET_NODE SID(1,2,1002,1003)와 충돌 방지
    em_nsid_base = 200  # EM Node Set SID: 201, 202, 203, ...

    iso_id = 0
    for uc in range(n_uc):
        pid_al, _, _, _, pid_cu = _get_pids(uc, model_type)

        # CCP tab (Al CC) → RDLTYPE=1 (Current Collector Positive)
        iso_id += 1
        nsid = em_nsid_base + iso_id
        if uc == 0:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write("$    isoId   setType     setId  rdlType\n")
            f.write(f"{iso_id:10d}         2{nsid:10d}         1\n")
            f.write(f"$ UC{uc} Al CC (PID {pid_al}), rdlType=1: CCP 양극 집전체\n")
        else:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{nsid:10d}         1\n")
            f.write(f"$ UC{uc} Al CC (PID {pid_al})\n")

        # CCN tab (Cu CC) → RDLTYPE=5 (Current Collector Negative)
        iso_id += 1
        nsid = em_nsid_base + iso_id
        if uc == 0:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{nsid:10d}         5\n")
            f.write(f"$ UC{uc} Cu CC (PID {pid_cu}), rdlType=5: CCN 음극 집전체\n")
        else:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{nsid:10d}         5\n")
            f.write(f"$ UC{uc} Cu CC (PID {pid_cu})\n")

    total_iso = iso_id

    # ISOPOTENTIAL CONNECTIONS
    f.write("$\n")
    f.write("$ ==================== ISOPOTENTIAL CONNECTIONS ====================\n")
    f.write("$\n")

    # External load resistor
    f.write("$ --- 외부 부하 저항 ---\n")
    f.write("*EM_ISOPOTENTIAL_CONNECT\n")
    f.write("$   connId  connType  isoId1  isoId2     val      lcid\n")
    f.write("         1         2       1       2    0.05\n")
    f.write("$ connType=2: R=0.05Ω 외부 부하 (ISO 1 양극 ↔ ISO 2 음극)\n")
    f.write("$\n")

    # Series connections
    if n_uc > 1:
        f.write("$ --- 직렬 연결 (UC_n 음극 → UC_{n+1} 양극) ---\n")
        conn_id = 1
        for uc in range(n_uc - 1):
            conn_id += 1
            neg_iso = 2 + uc * 2
            pos_iso = 3 + uc * 2
            f.write("*EM_ISOPOTENTIAL_CONNECT\n")
            f.write(f"{conn_id:10d}         1{neg_iso:8d}{pos_iso:8d}     0.0\n")
            f.write(f"$ V=0: UC{uc} 음극 → UC{uc+1} 양극 (직렬)\n")
        f.write("$\n")
    else:
        conn_id = 1

    # Ground
    conn_id += 1
    f.write("$ --- 접지 ---\n")
    f.write("*EM_ISOPOTENTIAL_CONNECT\n")
    f.write(f"{conn_id:10d}         3{total_iso:8d}       0     0.0\n")
    f.write(f"$ connType=3: 최종 음극탭 (ISO {total_iso}) → 접지 (기준 전위)\n")
    f.write("$\n")

    # NODE SETS for ISOPOTENTIAL (SID 201~210)
    # em_randleSetCircArea2 요구사항: CCP/CCN isopotential set은
    # 오직 자유 외부면(free outer face) 노드만 포함해야 함.
    # → PART 기반 SET_NODE_GENERAL 대신, 메쉬 생성기(generate_mesh_stacked.py)가
    #   SID 201-210을 SET_NODE_LIST로 직접 작성 (자유 외부면 노드 only).
    f.write("$ ==================== NODE SETS for ISOPOTENTIAL ====================\n")
    f.write(f"$ SID 201~{em_nsid_base + n_uc*2}: 메쉬 파일(02_mesh_stacked_tier-1.k)에서 정의됨\n")
    f.write(f"$ EM_CCP_OUTER_UC0~UC{n_uc-1}: Al CC 자유 외부면 노드만 포함 (SID 201,203,...)\n")
    f.write(f"$ EM_CCN_OUTER_UC0~UC{n_uc-1}: Cu CC 자유 외부면 노드만 포함 (SID 202,204,...)\n")
    f.write("$\n")

    # OUTPUT / DATABASE
    f.write("""$
$ ==================== EM OUTPUT ====================
$
*EM_OUTPUT
$     matS      matF      solS      solF      mesh    memory    timing    d3plot
         4         4         4         4                                       0
$      mf2       gmv                                            randle
                                                                     0
$
$ ==================== EM DATABASE ====================
$
*EM_DATABASE_GLOBALENERGY
$    OUTLV
        10
$
*EM_DATABASE_PARTDATA
$    OUTLV
        10
$
*EM_DATABASE_CIRCUIT
$    OUTLV
        10
$
*END
""")


def main():
    parser = argparse.ArgumentParser(
        description="EM Randles 회로 k-file 자동 생성 (YAML 설정 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_em_randles.py --config battery_config.yaml --tier -1
  python generate_em_randles.py --config battery_config.yaml --tier -1 --em-step 1
  python generate_em_randles.py --model-type wound --n-uc 1
  python generate_em_randles.py --n-uc 5 --output 08_em_randles.k

em-step:
  1: EM_RANDLES_SOLID만 (ISC/열폭주 OFF) — 기본 전기화학 검증
  2: + EM_RANDLES_SHORT (ISC ON) — 내부 단락 검증
  3: 전체 (ISC + 열폭주) — 완전 커플링 (기본값)
        """)
    parser.add_argument("--config", type=str, default=None,
                        help="YAML 설정 파일 경로 (기본: battery_config.yaml)")
    parser.add_argument("--tier", type=float, default=None,
                        help="티어 (-1, 0, 0.5, 1, 2) --config와 함께 사용")
    parser.add_argument("--n-uc", type=int, default=None,
                        help="단위셀(UC) 개수 (5, 15, 20 등) - 직접 지정")
    parser.add_argument("--model-type", type=str, default="stacked",
                        choices=["stacked", "wound"],
                        help="모델 타입 (stacked: PID 1000+, wound: PID 2000+)")
    parser.add_argument("--em-step", type=int, default=3, choices=[1, 2, 3],
                        help="EM 단계 (1=Randles만, 2=+ISC, 3=전체)")
    parser.add_argument("--output", type=str, default=None,
                        help="출력 파일명 (기본: 08_em_randles.k 또는 tier 기반)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="상세 로그 출력")
    parser.add_argument("--log-file", type=str, default=None,
                        help="로그를 파일로도 저장")
    args = parser.parse_args()

    log = setup_logger(
        "em_randles",
        level=logging.DEBUG if args.verbose else logging.INFO,
        log_file=args.log_file,
    )

    try:
        model_type = args.model_type

        # wound는 항상 1 UC
        if model_type == "wound":
            n_uc = 1
        elif args.config or (args.tier is not None and args.n_uc is None):
            config_path = args.config or "battery_config.yaml"
            config = load_config(config_path, validate=True, logger=log)

            if args.tier is not None:
                tier_map = config['geometry']['stacked']['stacking']['tier_definitions']
                tier_key = tier_to_yaml_key(args.tier)
                tier_def = tier_map.get(tier_key, {})
                n_uc = tier_def.get('n_cells', config['geometry']['stacked']['stacking']['default_n_cells']) if isinstance(tier_def, dict) else config['geometry']['stacked']['stacking']['default_n_cells']
            else:
                n_uc = config['geometry']['stacked']['stacking']['default_n_cells']
        else:
            if args.n_uc is None:
                log.error("--n-uc 또는 --config --tier 중 하나 필요")
                parser.print_help()
                sys.exit(1)
            n_uc = args.n_uc

        # 출력 파일명 결정
        if not args.output:
            if model_type == "wound":
                args.output = "08_em_randles_wound.k"
            elif args.config and args.tier is not None:
                config_path = args.config or "battery_config.yaml"
                if 'config' not in dir():
                    config = load_config(config_path, validate=True, logger=log)
                tier_key = tier_to_yaml_key(args.tier)
                tier_sfx = config['output_files']['mesh']['tier_suffixes'].get(tier_key, "")
                args.output = f"{config['output_files']['em_randles']['prefix']}{tier_sfx}.k"
            else:
                args.output = "08_em_randles.k"

        if n_uc < 1 or n_uc > 50:
            raise ValueError(f"n_uc={n_uc} 범위 초과 (1~50만 허용)")

        step_desc = {1: "Randles만 (ISC/열폭주 OFF)", 2: "+ISC", 3: "전체 (ISC+열폭주)"}
        log.info("=" * 70)
        log.info("EM Randles 회로 k-file 생성")
        log.info("  모델: %s | 단위셀: %d | 티어: %s | EM Step: %d (%s)",
                 model_type, n_uc,
                 args.tier if args.tier is not None else "N/A",
                 args.em_step, step_desc[args.em_step])
        log.info("  출력: %s", args.output)
        log.info("=" * 70)

        with open(args.output, 'w', encoding='utf-8') as f:
            write_header(f)
            write_em_mat(f)
            write_define_tables(f)
            write_randles_circuits(f, n_uc, model_type)
            write_footer(f, n_uc, model_type, args.em_step)

        pid_last = (2000 + 5) if model_type == "wound" else (1000 + (n_uc - 1) * 10 + 5)
        log.info("완료! %s (RDLID 1~%d, PID 범위 ~%d, ISO %d, CONN %d, TABLE 6개)",
                 args.output, n_uc, pid_last,
                 n_uc * 2, n_uc + 1)

    except FileNotFoundError as e:
        log.error("%s", e)
        sys.exit(1)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)
    except (KeyError, OSError) as e:
        log.error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
