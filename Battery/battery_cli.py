#!/usr/bin/env python3
"""
battery-simulation 통합 CLI
==============================
모든 배터리 시뮬레이션 자동화 스크립트를 하나의 진입점으로 제공합니다.

Usage:
    python battery_cli.py mesh-stacked --config battery_config.yaml --tier 0
    python battery_cli.py mesh-wound   --config battery_config.yaml --tier -1
    python battery_cli.py contacts     --config battery_config.yaml --tier 0
    python battery_cli.py em-randles   --config battery_config.yaml --tier 0
    python battery_cli.py generate-all --config battery_config.yaml --type both
    python battery_cli.py prepare      --tier -1 --type stacked --phase 1
    python battery_cli.py estimate     --all
    python battery_cli.py postprocess  --dir ./results --plot
    python battery_cli.py convergence  --dirs tier-1=DIR1 tier0=DIR2
    python battery_cli.py doe          --method lhs --n 30
    python battery_cli.py export-docx  --input MODELING_TECHNICAL_DOCUMENT.md
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="battery",
        description="LS-DYNA 배터리 시뮬레이션 통합 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
서브커맨드 목록:
  mesh-stacked   적층형 메시 생성
  mesh-wound     와인딩형 메시 생성
  contacts       접촉 정의 생성
  em-randles     EM Randles 회로 생성
  materials      재료 카드 생성
  boundary-loads 경계조건/하중 생성
  control        솔버 제어 카드 생성
  database       출력 제어 생성
  curves         커브/함수 정의 생성
  main-files     메인 include 파일 생성
  full-model     전체 모델 원클릭 생성
  generate-all   전 티어 일괄 생성
  prepare        LS-DYNA 실행 파일 준비
  estimate       해석 시간 추정
  postprocess    후처리 (에너지/반력 분석)
  convergence    메시 수렴성 분석
  doe            실험계획법 (DOE)
  export-docx    기술 문서 → Word 변환

예시:
  battery mesh-stacked --config battery_config.yaml --tier 0
  battery estimate --all
  battery postprocess --dir ./results --plot --all
""",
    )
    parser.add_argument("--version", action="version", version="battery-simulation 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="실행할 명령")

    # ── mesh-stacked ──
    sub = subparsers.add_parser("mesh-stacked", help="적층형 메시 생성")
    sub.set_defaults(func=_cmd_mesh_stacked)

    # ── mesh-wound ──
    sub = subparsers.add_parser("mesh-wound", help="와인딩형 메시 생성")
    sub.set_defaults(func=_cmd_mesh_wound)

    # ── contacts ──
    sub = subparsers.add_parser("contacts", help="접촉 정의 생성")
    sub.set_defaults(func=_cmd_contacts)

    # ── em-randles ──
    sub = subparsers.add_parser("em-randles", help="EM Randles 회로 생성")
    sub.set_defaults(func=_cmd_em_randles)

    # ── generate-all ──
    sub = subparsers.add_parser("generate-all", help="전 티어 일괄 생성")
    sub.set_defaults(func=_cmd_generate_all)

    # ── prepare ──
    sub = subparsers.add_parser("prepare", help="LS-DYNA 실행 파일 준비")
    sub.set_defaults(func=_cmd_prepare)

    # ── estimate ──
    sub = subparsers.add_parser("estimate", help="해석 시간 추정")
    sub.set_defaults(func=_cmd_estimate)

    # ── postprocess ──
    sub = subparsers.add_parser("postprocess", help="후처리")
    sub.set_defaults(func=_cmd_postprocess)

    # ── convergence ──
    sub = subparsers.add_parser("convergence", help="메시 수렴성 분석")
    sub.set_defaults(func=_cmd_convergence)

    # ── doe ──
    sub = subparsers.add_parser("doe", help="실험계획법 (DOE)")
    sub.set_defaults(func=_cmd_doe)

    # ── export-docx ──
    sub = subparsers.add_parser("export-docx", help="기술 문서 → Word 변환")
    sub.set_defaults(func=_cmd_export_docx)

    # ── materials ──
    sub = subparsers.add_parser("materials", help="재료 카드 생성")
    sub.set_defaults(func=_cmd_materials)

    # ── boundary-loads ──
    sub = subparsers.add_parser("boundary-loads", help="경계조건/하중 생성")
    sub.set_defaults(func=_cmd_boundary_loads)

    # ── control ──
    sub = subparsers.add_parser("control", help="솔버 제어 카드 생성")
    sub.set_defaults(func=_cmd_control)

    # ── database ──
    sub = subparsers.add_parser("database", help="출력 제어 생성")
    sub.set_defaults(func=_cmd_database)

    # ── curves ──
    sub = subparsers.add_parser("curves", help="커브/함수 정의 생성")
    sub.set_defaults(func=_cmd_curves)

    # ── main-files ──
    sub = subparsers.add_parser("main-files", help="메인 include 파일 생성")
    sub.set_defaults(func=_cmd_main_files)

    # ── full-model ──
    sub = subparsers.add_parser("full-model", help="전체 모델 원클릭 생성")
    sub.set_defaults(func=_cmd_full_model)

    # 인수가 없으면 help 출력
    args, remaining = parser.parse_known_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # 서브커맨드의 main()에 남은 인수 전달
    args.func(remaining)


# ════════════════════════════════════════════
# 서브커맨드 디스패처
# ════════════════════════════════════════════

def _cmd_mesh_stacked(argv):
    """적층형 메시 생성"""
    sys.argv = ["generate_mesh_stacked.py"] + argv
    import generate_mesh_stacked
    generate_mesh_stacked.main()

def _cmd_mesh_wound(argv):
    """와인딩형 메시 생성"""
    sys.argv = ["generate_mesh_wound.py"] + argv
    import generate_mesh_wound
    generate_mesh_wound.main()

def _cmd_contacts(argv):
    """접촉 정의 생성"""
    sys.argv = ["generate_contacts.py"] + argv
    import generate_contacts
    generate_contacts.main()

def _cmd_em_randles(argv):
    """EM Randles 회로 생성"""
    sys.argv = ["generate_em_randles.py"] + argv
    import generate_em_randles
    generate_em_randles.main()

def _cmd_generate_all(argv):
    """전 티어 일괄 생성"""
    sys.argv = ["generate_all_tiers.py"] + argv
    import generate_all_tiers
    generate_all_tiers.main()

def _cmd_prepare(argv):
    """LS-DYNA 실행 파일 준비"""
    sys.argv = ["prepare_run.py"] + argv
    import prepare_run
    prepare_run.main()

def _cmd_estimate(argv):
    """해석 시간 추정"""
    sys.argv = ["estimate_runtime.py"] + argv
    import estimate_runtime
    estimate_runtime.main()

def _cmd_postprocess(argv):
    """후처리"""
    sys.argv = ["postprocess_results.py"] + argv
    import postprocess_results
    postprocess_results.main()

def _cmd_convergence(argv):
    """메시 수렴성 분석"""
    sys.argv = ["convergence_study.py"] + argv
    import convergence_study
    convergence_study.main()

def _cmd_doe(argv):
    """실험계획법 (DOE)"""
    sys.argv = ["doe_framework.py"] + argv
    import doe_framework
    doe_framework.main()

def _cmd_export_docx(argv):
    """기술 문서 → Word 변환"""
    sys.argv = ["export_docx.py"] + argv
    import export_docx
    export_docx.main()

def _cmd_materials(argv):
    """재료 카드 생성"""
    sys.argv = ["generate_materials.py"] + argv
    import generate_materials
    generate_materials.main()

def _cmd_boundary_loads(argv):
    """경계조건/하중 생성"""
    sys.argv = ["generate_boundary_loads.py"] + argv
    import generate_boundary_loads
    generate_boundary_loads.main()

def _cmd_control(argv):
    """솔버 제어 카드 생성"""
    sys.argv = ["generate_control.py"] + argv
    import generate_control
    generate_control.main()

def _cmd_database(argv):
    """출력 제어 생성"""
    sys.argv = ["generate_database.py"] + argv
    import generate_database
    generate_database.main()

def _cmd_curves(argv):
    """커브/함수 정의 생성"""
    sys.argv = ["generate_curves.py"] + argv
    import generate_curves
    generate_curves.main()

def _cmd_main_files(argv):
    """메인 include 파일 생성"""
    sys.argv = ["generate_main.py"] + argv
    import generate_main
    generate_main.main()

def _cmd_full_model(argv):
    """전체 모델 원클릭 생성"""
    sys.argv = ["generate_full_model.py"] + argv
    import generate_full_model
    generate_full_model.main()


if __name__ == "__main__":
    main()
