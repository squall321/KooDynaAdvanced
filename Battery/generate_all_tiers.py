"""
전 티어 메시 일괄 생성 스크립트 (YAML 설정 기반)
=================================================
Tier -1 (디버깅) ~ Tier 2 (입자 클러스터) 메시를 모두 생성.
Tier 3 (다중 스케일)은 별도 스크립트 필요 (submodel 전략).

설정: battery_config.yaml 파일에서 모든 파라미터 로드

사용법:
    python generate_all_tiers.py --config battery_config.yaml --tier -1 0
    python generate_all_tiers.py --tier -1 0 0.5
    python generate_all_tiers.py --type stacked
"""

import sys
import time
import argparse
import subprocess
import logging
from pathlib import Path

from battery_utils import (
    load_config, setup_logger,
)

logger = logging.getLogger(__name__)


def generate_support_files_yaml(tier_id: str, model_type: str, outdir: str, config_path: str) -> dict:
    """각 티어별 contacts, em_randles 및 materials/boundary/control/database/curves/main 파일 생성"""
    results = {"contacts": False, "em_randles": False,
               "materials": False, "boundary": False, "control": False,
               "database": False, "curves": False, "main": False,
               "errors": []}
    
    # 1. Contacts 생성
    try:
        contact_cmd = [
            sys.executable, "generate_contacts.py",
            "--config", config_path,
            "--tier", tier_id,
            "--type", model_type,
            "--phase", "all"
        ]
        
        result = subprocess.run(contact_cmd, cwd=outdir, capture_output=True, text=True, timeout=60, check=False)
        if result.returncode == 0:
            results["contacts"] = True
        else:
            results["errors"].append(f"Contacts 생성 실패: {result.stderr[:100]}")
    except (subprocess.SubprocessError, OSError) as e:
        results["errors"].append(f"Contacts 오류: {str(e)[:100]}")
    
    # 2. EM Randles 생성 (stacked only)
    if model_type == "stacked":
        try:
            em_cmd = [
                sys.executable, "generate_em_randles.py",
                "--config", config_path,
                "--tier", tier_id
            ]
            
            result = subprocess.run(em_cmd, cwd=outdir, capture_output=True, text=True, timeout=30, check=False)
            if result.returncode == 0:
                results["em_randles"] = True
            else:
                results["errors"].append(f"EM Randles 생성 실패: {result.stderr[:100]}")
        except (subprocess.SubprocessError, OSError) as e:
            results["errors"].append(f"EM Randles 오류: {str(e)[:100]}")
    else:
        # Wound는 em_randles_wound.k 사용 (수동 파일)
        results["em_randles"] = None  # N/A

    # 3. Materials 생성
    for gen, key in [
        ("generate_materials.py", "materials"),
        ("generate_boundary_loads.py", "boundary"),
        ("generate_control.py", "control"),
        ("generate_database.py", "database"),
        ("generate_curves.py", "curves"),
        ("generate_main.py", "main"),
    ]:
        try:
            cmd_args = [sys.executable, gen, "--config", config_path]
            if key != "materials":
                cmd_args += ["--phase", "all"]
            if key == "main":
                cmd_args += ["--type", model_type, "--tier", tier_id]
            result = subprocess.run(cmd_args, cwd=outdir, capture_output=True,
                                    text=True, timeout=60, check=False)
            if result.returncode == 0:
                results[key] = True
            else:
                results["errors"].append(f"{gen} 실패: {result.stderr[:100]}")
        except (subprocess.SubprocessError, OSError) as e:
            results["errors"].append(f"{gen} 오류: {str(e)[:100]}")

    return results


def generate_stacked_yaml(tier_id: str, outdir: str, config_path: str, impactor_type: str = "cylinder") -> dict:
    """적층형 메시 생성 (YAML 기반, subprocess 사용)"""
    _ = impactor_type  # reserved for future impactor-specific mesh generation
    t0 = time.time()

    try:
        # generate_mesh_stacked.py를 subprocess로 호출
        cmd = [
            sys.executable, "generate_mesh_stacked.py",
            "--config", config_path,
            "--tier", tier_id
        ]

        result = subprocess.run(cmd, cwd=outdir, capture_output=True, text=True, timeout=600, check=False)
        
        if result.returncode != 0:
            return {
                "tier": tier_id,
                "type": "stacked",
                "status": "error",
                "error": result.stderr[:200],
                "time": time.time() - t0
            }
        
        # 출력에서 파일 경로 추출
        output_file = None
        for line in result.stdout.split('\n'):
            if '출력:' in line:
                output_file = line.split('출력:')[-1].strip()
                break
        
        return {
            "tier": tier_id,
            "type": "stacked",
            "status": "ok",
            "output": output_file,
            "time": time.time() - t0
        }
    
    except (subprocess.SubprocessError, OSError) as e:
        return {
            "tier": tier_id,
            "type": "stacked",
            "status": "error",
            "error": str(e),
            "time": time.time() - t0
        }


def generate_wound_yaml(tier_id: str, outdir: str, config_path: str, impactor_type: str = "cylinder") -> dict:
    """와인딩형 메시 생성 (YAML 기반, subprocess 사용)"""
    _ = impactor_type  # reserved for future impactor-specific mesh generation
    t0 = time.time()

    try:
        # generate_mesh_wound.py를 subprocess로 호출
        cmd = [
            sys.executable, "generate_mesh_wound.py",
            "--config", config_path,
            "--tier", tier_id
        ]

        result = subprocess.run(cmd, cwd=outdir, capture_output=True, text=True, timeout=600, check=False)
        
        if result.returncode != 0:
            return {
                "tier": tier_id,
                "type": "wound",
                "status": "error",
                "error": result.stderr[:200],
                "time": time.time() - t0
            }
        
        # 출력에서 파일 경로 추출
        output_file = None
        for line in result.stdout.split('\n'):
            if '출력:' in line:
                output_file = line.split('출력:')[-1].strip()
                break
        
        return {
            "tier": tier_id,
            "type": "wound",
            "status": "ok",
            "output": output_file,
            "time": time.time() - t0
        }
    
    except (subprocess.SubprocessError, OSError) as e:
        return {
            "tier": tier_id,
            "type": "wound",
            "status": "error",
            "error": str(e),
            "time": time.time() - t0
        }




# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="전 티어 메시 일괄 생성 (YAML 설정 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
티어:
  -1   디버깅/검증 (5mm, 5셀)           ~5K 요소
   0   업계 기본 (2.5mm, 15셀)          ~130K 요소
   0.5 업계 프로덕션 (0.5mm, 20셀)      ~1.8M 요소
   1   층별 해상도 (0.1mm, 3elem/coat)   ~200M 요소
   2   입자 클러스터 (0.05mm, 5elem)     ~2B 요소
 
예시:
  python generate_all_tiers.py --config battery_config.yaml --tier -1 0 0.5
  python generate_all_tiers.py --tier -1 --type stacked
  python generate_all_tiers.py --tier 1 --type wound
  python generate_all_tiers.py --include-tier2    # Tier 2 포함 (수십 GB)
        """)
    parser.add_argument("--config", type=str, default="battery_config.yaml",
                        help="YAML 설정 파일 경로 (기본: battery_config.yaml)")
    parser.add_argument("--tier", nargs="+", default=None,
                        help="생성할 티어 ID (-1, 0, 0.5, 1, 2)")
    parser.add_argument("--type", choices=["stacked", "wound", "both"],
                        default="both", help="모델 타입")
    parser.add_argument("--include-tier2", action="store_true",
                        help="Tier 2 포함 (주의: 수십 GB 파일 생성)")
    parser.add_argument("--impactor", choices=["cylinder", "nail"],
                        default="cylinder",
                        help="임팩터 형상: cylinder(기본) 또는 nail(관통)")
    args = parser.parse_args()

    # 로거 설정
    log = setup_logger(
        "all_tiers",
        level=logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO,
    )

    try:
        # YAML 로드
        load_config(args.config, validate=True, logger=log)  # pre-flight validation

        outdir = Path(__file__).parent

        # 티어 선택
        if args.tier:
            selected_tiers = args.tier
        else:
            # 기본: Tier 2 제외 (너무 큼)
            selected_tiers = ["-1", "0", "0.5", "1"]
            if args.include_tier2:
                selected_tiers.append("2")

        log.info("=" * 70)
        log.info("전 티어 메시 일괄 생성 | 티어: %s | 타입: %s | 임팩터: %s",
                 selected_tiers, args.type, args.impactor)
        log.info("=" * 70)

        results = []

        for tier_id in selected_tiers:
            log.info("─" * 60)
            log.info("  Tier %s", tier_id)
            log.info("─" * 60)

            if args.type in ("stacked", "both"):
                try:
                    r = generate_stacked_yaml(tier_id, str(outdir), args.config, impactor_type=args.impactor)
                    results.append(r)
                    
                    # Contacts + EM Randles 자동 생성
                    log.info("  → Contacts/EM Randles 생성 중...")
                    support_result = generate_support_files_yaml(
                        tier_id, "stacked", str(outdir), args.config
                    )
                    if support_result['contacts']:
                        log.info("    Contacts (3 files)")
                    if support_result['em_randles']:
                        log.info("    EM Randles")
                    if support_result['errors']:
                        for err in support_result['errors']:
                            log.warning("    %s", err)
                except (subprocess.SubprocessError, OSError, ValueError) as e:
                    log.error("  적층형 실패: %s", e)
                    results.append({"tier": tier_id, "type": "stacked", "status": "error", "error": str(e)})

            if args.type in ("wound", "both"):
                try:
                    r = generate_wound_yaml(tier_id, str(outdir), args.config, impactor_type=args.impactor)
                    results.append(r)
                    
                    # Contacts 자동 생성 (EM Randles는 wound 전용 수동 파일 사용)
                    log.info("  → Contacts 생성 중...")
                    support_result = generate_support_files_yaml(
                        tier_id, "wound", str(outdir), args.config
                    )
                    if support_result['contacts']:
                        log.info("    Contacts (3 files)")
                    if support_result['errors']:
                        for err in support_result['errors']:
                            log.warning("    %s", err)
                except (subprocess.SubprocessError, OSError, ValueError) as e:
                    log.error("  와인딩형 실패: %s", e)
                    results.append({"tier": tier_id, "type": "wound", "status": "error", "error": str(e)})

        # ── 결과 요약 테이블 ──
        log.info("=" * 70)
        log.info("결과 요약")
        log.info("=" * 70)
        header = f"{'Tier':>6s} {'Type':>8s} {'Status':>12s} {'Output':>40s} {'Time':>7s}"
        log.info(header)
        log.info("-" * 85)
        for r in results:
            if r.get('status') == 'ok':
                output_name = Path(r['output']).name if r.get('output') else 'N/A'
                log.info("%6s %8s %12s %40s %6.1fs", r['tier'], r['type'], 'OK', output_name, r['time'])
            elif r.get('status') == 'error':
                error_msg = r.get('error', 'Unknown error')[:30]
                log.error("%6s %8s %12s %40s %7s", r['tier'], r['type'], 'ERROR', error_msg, 'N/A')
            elif 'nodes' in r:
                log.info("%6s %8s %12s %12s %12s %12s %8.1fMB %6.1fs",
                         r['tier'], r['type'], r['nodes'], r['shells'], r['solids'], r['total'],
                         r['size_mb'], r['time_s'])
            else:
                log.warning("%6s %8s %12s %40s %7s", r['tier'], r['type'], 'UNKNOWN', '?', 'N/A')

        log.info("\n생성 완료: %d 파일", len(results))

    except FileNotFoundError as e:
        log.error("%s", e)
        sys.exit(1)
    except (KeyError, ValueError, OSError) as e:
        log.error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
