"""
LS-DYNA 배터리 시뮬레이션 해석 시간 추정기
==========================================
티어별 요소 수, 시간스텝, 종료시간 기반 실행 시간 추정

Usage:
    python estimate_runtime.py --tier -1 --phase 1 --ncpu 1
    python estimate_runtime.py --tier 0 --phase 3 --ncpu 8
"""

import argparse
import logging
import sys
from typing import Dict

from battery_utils import setup_logger

logger = logging.getLogger(__name__)


# 티어별 요소 수 (approximate)
TIER_ELEMENTS = {
    -1: {"stacked": 6_000, "wound": 23_000},
    0: {"stacked": 57_000, "wound": 210_000},
    0.5: {"stacked": 1_800_000, "wound": 4_000_000},
    1: {"stacked": 200_000_000, "wound": 500_000_000},
    2: {"stacked": 2_000_000_000, "wound": 5_000_000_000},
}

# Phase별 종료 시간 (ms)
PHASE_ENDTIME = {
    1: 5.0,   # 구조만
    2: 10.0,  # 구조-열
    3: 20.0,  # 구조-열-전기 (ISC 후 열폭주까지)
}

# 시간스텝 (µs, 질량스케일링 기준)
TIMESTEP_US = {
    -1: 9.0,    # DT2MS = -1.0e-5
    0: 4.0,     # DT2MS = -5.0e-6
    0.5: 1.0,   # DT2MS = -1.0e-6
    1: 0.3,     # DT2MS = -3.0e-7
    2: 0.1,     # DT2MS = -1.0e-7
}

# CPU 성능 (요소·스텝/초, 코어당)
# Intel Xeon E5-2690 v4 기준 (2.6 GHz, 2016년)
PERF_ELEM_STEP_PER_SEC = {
    "shell_only": 1_000_000,     # Shell 요소만 (빠름)
    "shell_solid": 500_000,      # Shell + Solid 혼합
    "thermal": 300_000,          # 열 연성 (느림)
    "thermal_em": 200_000,       # 열-전기 연성 (가장 느림)
}

# Phase별 성능 카테고리
PHASE_PERF_CATEGORY = {
    1: "shell_solid",
    2: "thermal",
    3: "thermal_em",
}

# 병렬 효율 (코어 수별)
PARALLEL_EFFICIENCY = {
    1: 1.00,
    2: 0.95,
    4: 0.85,
    8: 0.70,
    16: 0.55,
    32: 0.40,
}


def estimate_runtime(tier: int, phase: int, ncpu: int, model_type: str = "stacked") -> Dict:
    """해석 시간 추정
    
    Returns:
        dict: {
            'elements': 요소 수,
            'endtime_ms': 종료 시간 (ms),
            'timestep_us': 시간스텝 (µs),
            'total_steps': 총 스텝 수,
            'perf_category': 성능 카테고리,
            'perf_elem_step_per_sec': 요소·스텝/초,
            'parallel_efficiency': 병렬 효율,
            'walltime_hours': 벽시계 시간 (시간),
            'walltime_str': 시간 문자열
        }
    """
    
    # 요소 수
    elements = TIER_ELEMENTS.get(tier, {}).get(model_type, 0)
    if elements == 0:
        return {"error": f"Tier {tier}, {model_type} 정보 없음"}
    
    # 종료 시간
    endtime_ms = PHASE_ENDTIME.get(phase, 5.0)
    
    # 시간스텝
    timestep_us = TIMESTEP_US.get(tier, 1.0)
    
    # 총 스텝 수
    total_steps = int((endtime_ms * 1000) / timestep_us)
    
    # 성능 카테고리
    perf_category = PHASE_PERF_CATEGORY.get(phase, "shell_solid")
    perf_elem_step_per_sec = PERF_ELEM_STEP_PER_SEC[perf_category]
    
    # 병렬 효율
    parallel_eff = PARALLEL_EFFICIENCY.get(ncpu, 0.40)
    
    # 총 연산량 (요소 × 스텝)
    total_work = elements * total_steps
    
    # 단일 코어 시간 (초)
    single_core_sec = total_work / perf_elem_step_per_sec
    
    # 병렬 시간 (초)
    parallel_sec = single_core_sec / (ncpu * parallel_eff)
    
    # 시간 변환
    walltime_hours = parallel_sec / 3600
    
    if walltime_hours < 0.017:  # < 1분
        walltime_str = f"{parallel_sec:.1f}초"
    elif walltime_hours < 1.0:  # < 1시간
        walltime_str = f"{parallel_sec/60:.1f}분"
    elif walltime_hours < 24:  # < 1일
        walltime_str = f"{walltime_hours:.1f}시간"
    else:
        walltime_str = f"{walltime_hours/24:.1f}일"
    
    return {
        'elements': elements,
        'endtime_ms': endtime_ms,
        'timestep_us': timestep_us,
        'total_steps': total_steps,
        'perf_category': perf_category,
        'perf_elem_step_per_sec': perf_elem_step_per_sec,
        'parallel_efficiency': parallel_eff,
        'walltime_hours': walltime_hours,
        'walltime_str': walltime_str,
        'ncpu': ncpu,
    }


def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 해석 시간 추정",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python estimate_runtime.py --tier -1 --phase 1 --ncpu 1
  python estimate_runtime.py --tier 0 --phase 3 --ncpu 8 --type wound
  python estimate_runtime.py --all
        """)
    parser.add_argument("--tier", type=int, default=None,
                        help="티어 (-1, 0, 0.5, 1, 2)")
    parser.add_argument("--phase", type=int, default=1,
                        help="Phase (1, 2, 3)")
    parser.add_argument("--ncpu", type=int, default=4,
                        help="CPU 코어 수 (기본: 4)")
    parser.add_argument("--type", choices=["stacked", "wound"], default="stacked",
                        help="모델 타입")
    parser.add_argument("--all", action="store_true",
                        help="모든 티어 비교 테이블 출력")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    args = parser.parse_args()

    log = setup_logger(
        "estimate_runtime",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        _run(args, log)
    except (KeyError, ValueError, OSError) as e:
        log.error("오류: %s", e, exc_info=True)
        sys.exit(1)


def _run(args, log):
    if args.all:
        print("=" * 90)
        print("LS-DYNA 배터리 시뮬레이션 해석 시간 추정 (Intel Xeon E5-2690 v4 기준)")
        print("=" * 90)
        print()
        
        for phase in [1, 2, 3]:
            print(f"\n{'─' * 90}")
            print(f"Phase {phase}: {['구조', '구조-열', '구조-열-전기'][phase-1]}, "
                  f"종료시간 {PHASE_ENDTIME[phase]} ms, 4-core")
            print(f"{'─' * 90}")
            print(f"{'Tier':>6s} {'Model':>8s} {'Elements':>12s} {'Steps':>10s} "
                  f"{'Timestep(µs)':>13s} {'Walltime':>15s}")
            print("─" * 90)
            
            for tier in [-1, 0, 0.5, 1, 2]:
                for model_type in ["stacked", "wound"]:
                    result = estimate_runtime(tier, phase, 4, model_type)
                    if "error" not in result:
                        print(f"{tier:>6} {model_type:>8s} {result['elements']:>12,d} "
                              f"{result['total_steps']:>10,d} {result['timestep_us']:>13.1f} "
                              f"{result['walltime_str']:>15s}")
            print()
        
        print("\n주의사항:")
        print("  - 실제 성능은 CPU 모델, 메모리 속도, I/O에 따라 ±30% 변동")
        print("  - Tier 1, 2는 메모리 부족 가능 (수백 GB ~ TB 필요)")
        print("  - 상용 HPC 클러스터 권장 (Tier 0.5 이상)")
        print()
    
    elif args.tier is not None:
        result = estimate_runtime(args.tier, args.phase, args.ncpu, args.type)
        
        if "error" in result:
            print(f"오류: {result['error']}")
            return
        
        print("=" * 60)
        print("LS-DYNA 해석 시간 추정")
        print("=" * 60)
        print(f"  Tier {args.tier} ({args.type})")
        print(f"  Phase {args.phase} ({PHASE_PERF_CATEGORY[args.phase]})")
        print(f"  CPU 코어: {args.ncpu} (병렬 효율 {result['parallel_efficiency']:.0%})")
        print()
        print(f"  요소 수: {result['elements']:,}")
        print(f"  종료 시간: {result['endtime_ms']} ms")
        print(f"  시간스텝: {result['timestep_us']} µs")
        print(f"  총 스텝: {result['total_steps']:,}")
        print(f"  성능: {result['perf_elem_step_per_sec']:,} 요소·스텝/초/코어")
        print()
        print(f"  ⏱ 예상 실행 시간: {result['walltime_str']}")
        print(f"     ({result['walltime_hours']:.4f} 시간)")
        print()
    else:
        log.error("--tier 또는 --all 옵션 필요")
        sys.exit(1)


if __name__ == "__main__":
    main()
