"""
LS-DYNA 실행 준비 스크립트
=========================
Tier별로 생성된 파일을 main이 기대하는 이름으로 복사

Usage:
    python prepare_run.py --tier -1 --type stacked --phase 1
    python prepare_run.py --tier 0 --type wound --phase 3
    python prepare_run.py --tier -1 --type both --phase all
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path

from battery_utils import tier_to_suffix, setup_logger

logger = logging.getLogger(__name__)


def prepare_stacked(tier: float, phases: list, workdir: Path) -> None:
    """적층형 실행 파일 준비"""
    tier_suffix = tier_to_suffix(tier)
    
    # Mesh 파일 (생성기가 _0 suffix를 추가함)
    mesh_src = workdir / f"02_mesh_stacked{tier_suffix}_0.k"
    mesh_dst = workdir / f"02_mesh_stacked{tier_suffix}.k"
    
    if mesh_src.exists():
        shutil.copy2(mesh_src, mesh_dst)
        print(f"  ✓ Mesh: {mesh_src.name} → {mesh_dst.name}")
    else:
        print(f"  ⚠ Mesh 파일 없음: {mesh_src.name}")
        return
    
    # Phase별 contacts
    for phase in phases:
        if phase == 1:
            src = workdir / f"05_contacts_phase1{tier_suffix}.k"
            dst = workdir / "05_contacts_phase1.k"
        elif phase == 2:
            src = workdir / f"05_contacts_phase2{tier_suffix}.k"
            dst = workdir / "05_contacts_phase2.k"
        elif phase == 3:
            src = workdir / f"05_contacts{tier_suffix}.k"
            dst = workdir / "05_contacts.k"
        else:
            continue
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Contacts P{phase}: {src.name} → {dst.name}")
        else:
            print(f"  ⚠ Contacts 파일 없음: {src.name}")
    
    # EM Randles (Phase 2, 3에서 사용)
    if 2 in phases or 3 in phases:
        em_src = workdir / f"08_em_randles{tier_suffix}.k"
        em_dst = workdir / "08_em_randles.k"
        
        if em_src.exists():
            shutil.copy2(em_src, em_dst)
            print(f"  ✓ EM Randles: {em_src.name} → {em_dst.name}")
        else:
            print(f"  ⚠ EM Randles 파일 없음: {em_src.name}")


def prepare_wound(tier: float, phases: list, workdir: Path) -> None:
    """와인딩형 실행 파일 준비"""
    tier_suffix = tier_to_suffix(tier)
    
    # Mesh 파일
    mesh_src = workdir / f"03_mesh_wound{tier_suffix}.k"
    _mesh_dst = workdir / f"03_mesh_wound{tier_suffix}.k"  # wound는 이미 올바른 이름
    
    if not mesh_src.exists():
        print(f"  ⚠ Wound mesh 파일 없음: {mesh_src.name}")
        return
    
    print(f"  ✓ Wound mesh: {mesh_src.name}")
    
    # Phase별 contacts
    for phase in phases:
        if phase == 1:
            src = workdir / f"05_contacts_phase1_wound{tier_suffix}.k"
            dst = workdir / "05_contacts_phase1_wound.k"
        elif phase == 2:
            src = workdir / f"05_contacts_phase2_wound{tier_suffix}.k"
            dst = workdir / "05_contacts_phase2_wound.k"
        elif phase == 3:
            src = workdir / f"05_contacts_wound{tier_suffix}.k"
            dst = workdir / "05_contacts_wound.k"
        else:
            continue
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Contacts P{phase}: {src.name} → {dst.name}")
        else:
            print(f"  ⚠ Contacts 파일 없음: {src.name}")
    
    # EM Randles (wound는 공용 파일 사용)
    em_file = workdir / "08_em_randles_wound.k"
    if em_file.exists():
        print(f"  ✓ EM Randles (wound 공용): {em_file.name}")
    else:
        print(f"  ⚠ EM Randles (wound) 파일 없음: {em_file.name}")


def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 실행을 위한 파일 준비 (tier별 파일명 → main이 기대하는 파일명)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python prepare_run.py --tier -1 --type stacked --phase 1
  python prepare_run.py --tier 0 --type both --phase all
  python prepare_run.py --tier 0.5 --type stacked --phase 2 3
        """)
    parser.add_argument("--tier", type=float, required=True,
                        help="티어 (-1, 0, 0.5, 1, 2)")
    parser.add_argument("--type", choices=["stacked", "wound", "both"],
                        default="both", help="모델 타입")
    parser.add_argument("--phase", nargs="+", default=["all"],
                        help="Phase 번호: 1 2 3 또는 all")
    parser.add_argument("--workdir", type=str, default=".",
                        help="작업 디렉토리 (default: 현재)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    args = parser.parse_args()

    log = setup_logger(
        "prepare_run",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    workdir = Path(args.workdir)

    # Phase 파싱
    if "all" in args.phase:
        phases = [1, 2, 3]
    else:
        phases = [int(p) for p in args.phase]

    log.info("LS-DYNA 실행 파일 준비 (Tier %.1f, %s, Phase %s)", args.tier, args.type, phases)

    try:
        if args.type in ("stacked", "both"):
            log.info("[Stacked] Phase %s", phases)
            prepare_stacked(args.tier, phases, workdir)

        if args.type in ("wound", "both"):
            log.info("[Wound] Phase %s", phases)
            prepare_wound(args.tier, phases, workdir)

        log.info("준비 완료!")
        log.info("실행 명령:")
        if args.type in ("stacked", "both"):
            for phase in phases:
                log.info("  ls-dyna i=01_main_phase%d_stacked.k ncpu=4 memory=2000m", phase)
        if args.type in ("wound", "both"):
            for phase in phases:
                log.info("  ls-dyna i=01_main_phase%d_wound.k ncpu=4 memory=2000m", phase)
    except (OSError, ValueError) as e:
        log.error("오류: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
