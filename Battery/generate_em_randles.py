"""
EM Randles 회로 k-file 자동 생성 스크립트
========================================
주어진 단위셀(UC) 수에 맞춰 08_em_randles.k 파일 생성

설정: battery_config.yaml 파일에서 모든 파라미터 로드

사용법:
    python generate_em_randles.py --config battery_config.yaml --n-uc 5
    python generate_em_randles.py --tier 0 --output 08_em_randles_tier0.k
    python generate_em_randles.py --n-uc 20
"""

import argparse
import sys
import logging
from typing import TextIO

from battery_utils import (
    tier_to_yaml_key,
    load_config, setup_logger,
)

logger = logging.getLogger(__name__)


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
    """EM_MAT_001 전기전도도 정의 (MID = 구조재 MID와 일치 필수)
    
    Card1: MID MTYPE SIGMA SIGY SIGZ EOSID AOPT MACF
    Field8 = MACF (좌표 규칙), NOT RANDLETYPE.
    Part 역할(CCPPART/CCNPART/PELPART/NELPART/SEPPART)은 EM_RANDLES_SOLID 자체에 정의.
    trailing 값 없이 MID/MTYPE/SIGMA만 명시.
    """
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


def write_randles_circuits(f: TextIO, n_uc: int):
    """EM_RANDLES_SOLID 회로 생성 (TABLE 기반 R0/R1/C1 + SOC Shift)"""
    f.write("$ ==================== RANDLES CIRCUITS ====================\n")
    f.write("$\n")
    f.write("$ R0/R1/C1: 음수 TABLE ID → SOC×Temperature 2D 보간\n")
    f.write("$   -8001: R0CHA, -8002: R0DIS\n")
    f.write("$   -8003: R10CHA, -8004: R10DIS\n")
    f.write("$   -8005: C10CHA, -8006: C10DIS\n")
    f.write("$ TABLE 정의 → 08_em_randles.k 에 포함\n")
    f.write("$\n")
    
    for uc in range(n_uc):
        rdlid = uc + 1
        pid_base = 1000 + uc * 10
        pid_al = pid_base + 1
        pid_nmc = pid_base + 2
        pid_sep = pid_base + 3
        pid_graphite = pid_base + 4
        pid_cu = pid_base + 5
        
        if uc == 0:
            # 첫 번째는 상세 주석 포함
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
            # 2번째는 짧은 주석
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
        elif uc == 2 and n_uc > 5:
            # 3번째부터는 compact 형식
            f.write("$\n")
            f.write(f"$ --- Randles for Unit Cells {uc}~{n_uc-1} (동일 패턴) ---\n")
            f.write("*EM_RANDLES_SOLID\n")
            f.write(f"{rdlid:8d}         1         2{pid_al:10d}{pid_cu:10d}{pid_sep:10d}{pid_nmc:10d}{pid_graphite:10d}\n")
            f.write("       2.6    2.78E-2       0.5     -2001\n")
            f.write("     -8001     -8002     -8003     -8004     -8005     -8006\n")
            f.write("    298.15         1         1     -2002         1\n")
            f.write("         1    1000.0     -2004\n")
        elif uc >= 2:
            # Compact 형식 계속
            f.write("*EM_RANDLES_SOLID\n")
            f.write(f"{rdlid:8d}         1         2{pid_al:10d}{pid_cu:10d}{pid_sep:10d}{pid_nmc:10d}{pid_graphite:10d}\n")
            f.write("       2.6    2.78E-2       0.5     -2001\n")
            f.write("     -8001     -8002     -8003     -8004     -8005     -8006\n")
            f.write("    298.15         1         1     -2002         1\n")
            f.write("         1    1000.0     -2004\n")
    
    f.write("$\n")
    f.write(f"$ --- Total Randles circuits: {n_uc} (RDLID 1~{n_uc}) ---\n")
    f.write("$\n")


def write_footer(f: TextIO, n_uc: int):
    """ISC, 열폭주, ISOPOTENTIAL, 회로, EM_OUTPUT, 데이터베이스"""
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
$ ==================== EXOTHERMIC REACTION (열폭주) ======================================
$
*EM_RANDLES_EXOTHERMIC_REACTION
$  AREATYPE   FUNCTID
         2      5002
$
$ FUNCTID=5002: LSTC 10인수 공식 시그니처
$   exothermic_reaction_randle(time, temp, SOC, emdt, ocv, curr, volt, r0, vc, H_ex)
$
""")

    # ==================== ISOPOTENTIAL ====================
    f.write("$ ==================== TAB ISOPOTENTIAL (동전위면) ====================\n")
    f.write("$\n")
    f.write(f"$ {n_uc} unit cells → 양극/음극 각 {n_uc}개 = {n_uc * 2} ISOs\n")
    f.write("$\n")

    iso_id = 0
    for uc in range(n_uc):
        pid_base = 1000 + uc * 10
        pid_al = pid_base + 1
        pid_cu = pid_base + 5

        # Positive tab (Al CC) → randType=5
        iso_id += 1
        if uc == 0:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write("$    isoId   setType     setId  randType\n")
            f.write(f"{iso_id:10d}         2{iso_id:10d}         5\n")
            f.write(f"$ UC{uc} Al CC (PID {pid_al}), randType=5: Randles 양극 탭\n")
        else:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{iso_id:10d}         5\n")
            f.write(f"$ UC{uc} Al CC (PID {pid_al})\n")

        # Negative tab (Cu CC) → randType=1
        iso_id += 1
        if uc == 0:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{iso_id:10d}         1\n")
            f.write(f"$ UC{uc} Cu CC (PID {pid_cu}), randType=1: 음극 탭\n")
        else:
            f.write("*EM_ISOPOTENTIAL\n")
            f.write(f"{iso_id:10d}         2{iso_id:10d}         1\n")
            f.write(f"$ UC{uc} Cu CC (PID {pid_cu})\n")

    total_iso = iso_id

    # ==================== ISOPOTENTIAL CONNECTIONS ====================
    f.write("$\n")
    f.write("$ ==================== ISOPOTENTIAL CONNECTIONS ====================\n")
    f.write("$\n")

    # External load resistor: ISO 1 (UC0 positive) ↔ ISO 2 (UC0 negative)
    f.write("$ --- 외부 부하 저항 ---\n")
    f.write("*EM_ISOPOTENTIAL_CONNECT\n")
    f.write("$   connId  connType  isoId1  isoId2     val      lcid\n")
    f.write("         1         2       1       2    0.05\n")
    f.write("$ connType=2: R=0.05Ω 외부 부하 (ISO 1 양극 ↔ ISO 2 음극)\n")
    f.write("$\n")

    # Series connections: UC_n negative → UC_{n+1} positive
    if n_uc > 1:
        f.write("$ --- 직렬 연결 (UC_n 음극 → UC_{n+1} 양극) ---\n")
        conn_id = 1
        for uc in range(n_uc - 1):
            conn_id += 1
            neg_iso = 2 + uc * 2        # UC_n negative
            pos_iso = 3 + uc * 2        # UC_{n+1} positive
            f.write("*EM_ISOPOTENTIAL_CONNECT\n")
            f.write(f"{conn_id:10d}         1{neg_iso:8d}{pos_iso:8d}     0.0\n")
            f.write(f"$ V=0: UC{uc} 음극 → UC{uc+1} 양극 (직렬)\n")
        f.write("$\n")
    else:
        conn_id = 1

    # Ground: last negative tab
    conn_id += 1
    f.write("$ --- 접지 ---\n")
    f.write("*EM_ISOPOTENTIAL_CONNECT\n")
    f.write(f"{conn_id:10d}         3{total_iso:8d}       0     0.0\n")
    f.write(f"$ connType=3: 최종 음극탭 (ISO {total_iso}) → 접지 (기준 전위)\n")
    f.write("$\n")

    # ==================== SET_PART for ISOPOTENTIAL ====================
    f.write("$ ==================== SET_PART for ISOPOTENTIAL ====================\n")
    f.write("$\n")
    sid = 0
    for uc in range(n_uc):
        pid_base = 1000 + uc * 10

        # Positive (Al CC)
        sid += 1
        if sid == 1:
            f.write("*SET_PART_LIST\n")
            f.write("$      SID\n")
            f.write(f"{sid:10d}\n")
            f.write("$     PID1\n")
            f.write(f"{pid_base + 1:10d}\n")
        else:
            f.write("*SET_PART_LIST\n")
            f.write(f"{sid:10d}\n")
            f.write(f"{pid_base + 1:10d}\n")

        # Negative (Cu CC)
        sid += 1
        f.write("*SET_PART_LIST\n")
        f.write(f"{sid:10d}\n")
        f.write(f"{pid_base + 5:10d}\n")

    # ==================== OUTPUT / DATABASE ====================
    # EM_CIRCUIT 제거: EM_RANDLES_SOLID + EM_ISOPOTENTIAL + EM_ISOPOTENTIAL_CONNECT로
    # 회로가 완전히 정의됨. 외부 EM_CIRCUIT은 불필요하며 R16에서 SET_SEGMENT/PART 오류 유발.
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
$       DT
     0.010
$
*EM_DATABASE_PARTDATA
$       DT
     0.010
$
*EM_DATABASE_CIRCUIT
$       DT
     0.010
$
*EM_DATABASE_ELOUT
$       DT
     0.100
$
*END
""")


def main():
    parser = argparse.ArgumentParser(
        description="EM Randles 회로 k-file 자동 생성 (YAML 설정 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_em_randles.py --config battery_config.yaml --tier 0
  python generate_em_randles.py --n-uc 5 --output 08_em_randles.k
  python generate_em_randles.py --n-uc 15 --output 08_em_randles_tier0.k

생성 파일:
  - EM_CONTROL 섹션
  - EM_RANDLES_SOLID × n_uc (각 단위셀당 1개 회로)
  - EM_RANDLES_SHORT (내부 단락)
  - EM_RANDLES_EXOTHERMIC_REACTION (열폭주)
  - EM_CIRCUIT (외부 회로)
  - EM_DATABASE (출력 제어)
        """)
    parser.add_argument("--config", type=str, default=None,
                        help="YAML 설정 파일 경로 (기본: battery_config.yaml)")
    parser.add_argument("--tier", type=float, default=None,
                        help="티어 (-1, 0, 0.5, 1, 2) --config와 함께 사용")
    parser.add_argument("--n-uc", type=int, default=None,
                        help="단위셀(UC) 개수 (5, 15, 20 등) - 직접 지정")
    parser.add_argument("--output", type=str, default=None,
                        help="출력 파일명 (기본: 08_em_randles.k 또는 tier 기반)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="상세 로그 출력")
    parser.add_argument("--log-file", type=str, default=None,
                        help="로그를 파일로도 저장")
    args = parser.parse_args()

    # 로거 설정
    log = setup_logger(
        "em_randles",
        level=logging.DEBUG if args.verbose else logging.INFO,
        log_file=args.log_file,
    )

    try:
        # YAML 설정 또는 직접 지정
        if args.config or (args.tier is not None and args.n_uc is None):
            config_path = args.config or "battery_config.yaml"
            config = load_config(config_path, validate=True, logger=log)

            # 티어에서 n_uc 결정
            if args.tier is not None:
                tier_map = config['geometry']['stacked']['stacking']['tier_definitions']
                tier_key = tier_to_yaml_key(args.tier)
                tier_def = tier_map.get(tier_key, {})
                n_uc = tier_def.get('n_cells', config['geometry']['stacked']['stacking']['default_n_cells']) if isinstance(tier_def, dict) else config['geometry']['stacked']['stacking']['default_n_cells']
            else:
                n_uc = config['geometry']['stacked']['stacking']['default_n_cells']

            # 출력 파일명
            if not args.output:
                tier_key = tier_to_yaml_key(args.tier) if args.tier is not None else None
                tier_sfx = config['output_files']['mesh']['tier_suffixes'].get(tier_key, "") if tier_key else ""
                args.output = f"{config['output_files']['em_randles']['prefix']}{tier_sfx}.k"
        else:
            if args.n_uc is None:
                log.error("--n-uc 또는 --config --tier 중 하나 필요")
                parser.print_help()
                sys.exit(1)
            n_uc = args.n_uc
            if not args.output:
                args.output = "08_em_randles.k"

        if n_uc < 1 or n_uc > 50:
            raise ValueError(f"n_uc={n_uc} 범위 초과 (1~50만 허용)")

        log.info("=" * 70)
        log.info("EM Randles 회로 k-file 생성")
        log.info("  단위셀: %d | 티어: %s | 출력: %s",
                 n_uc, args.tier if args.tier is not None else "N/A", args.output)
        log.info("=" * 70)

        with open(args.output, 'w', encoding='utf-8') as f:
            write_header(f)
            write_em_mat(f)
            write_randles_circuits(f, n_uc)
            write_footer(f, n_uc)

        log.info("완료! %s (RDLID 1~%d, PID 1001~%d, ISO %d, CONN %d)",
                 args.output, n_uc, 1000 + (n_uc - 1) * 10 + 5,
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
