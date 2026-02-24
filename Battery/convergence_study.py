"""
LS-DYNA 배터리 시뮬레이션 메시 수렴성 분석 자동화
===================================================
Tier -1 / Tier 0 / Tier 0.5 / Production 결과 비교

항목:
  1. 피크 반력 수렴  
  2. 최대 변형 수렴  
  3. 에너지 흡수량 수렴  
  4. 최대 온도 수렴 (Phase 2+)  
  5. Richardson 외삽 (GCI)  

Usage:
  python convergence_study.py --dirs tier-1=./res_t-1 tier0=./res_t0 tier0_5=./res_t05 prod=./res_prod
  python convergence_study.py --config convergence.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from battery_utils import setup_logger

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    logger.warning("matplotlib 없음 — 그래프 비활성")

# postprocess_results에서 파서 재활용
try:
    from postprocess_results import parse_glstat, parse_rcforc, compute_metrics
except ImportError:
    logger.error("postprocess_results.py를 같은 디렉토리에 배치하세요")
    sys.exit(1)


# ============================================================
# Tier 메시 사양
# ============================================================

TIER_SPECS = {
    'tier-1':  {'label': 'Tier -1 (Coarse)',   'h_mm': 4.0,  'n_jelly': 2 },
    'tier0':   {'label': 'Tier 0 (Standard)',   'h_mm': 2.0,  'n_jelly': 4 },
    'tier0_5': {'label': 'Tier 0.5 (Fine)',     'h_mm': 1.0,  'n_jelly': 6 },
    'prod':    {'label': 'Production (Finest)', 'h_mm': 0.5,  'n_jelly': 8 },
}


@dataclass
class TierResult:
    """한 Tier의 결과 데이터"""
    name: str
    label: str
    h: float           # 대표 요소 크기 (mm)
    n_jelly: int
    peak_force: float = 0.0
    peak_force_time: float = 0.0
    total_energy: float = 0.0
    energy_ratio: float = 1.0
    max_temperature: float = 298.15
    hg_ratio: float = 0.0
    wall_time_s: float = 0.0
    n_elements: int = 0


# ============================================================
# 결과 수집
# ============================================================

def collect_tier_results(tier_dirs: Dict[str, Path]) -> List[TierResult]:
    """각 Tier 디렉토리에서 결과 수집"""
    results = []
    
    for tier_name, dirpath in sorted(tier_dirs.items(), 
                                      key=lambda x: TIER_SPECS.get(x[0], {}).get('h_mm', 99)):
        spec = TIER_SPECS.get(tier_name, {
            'label': tier_name, 'h_mm': 1.0, 'n_jelly': 4
        })
        
        print(f"\n--- {spec['label']} ({dirpath}) ---")
        
        tr = TierResult(
            name=tier_name,
            label=spec['label'],
            h=spec['h_mm'],
            n_jelly=spec['n_jelly']
        )
        
        glstat = parse_glstat(dirpath)
        rcforc = parse_rcforc(dirpath)
        metrics = compute_metrics(glstat, rcforc)
        
        tr.peak_force = metrics.peak_force
        tr.peak_force_time = metrics.peak_force_time
        tr.total_energy = metrics.final_internal_energy
        tr.energy_ratio = metrics.energy_ratio
        tr.max_temperature = metrics.max_temperature
        tr.hg_ratio = metrics.max_hourglass_ratio
        
        # 요소 수: d3hsp 파일에서 파싱
        d3hsp = dirpath / "d3hsp"
        if d3hsp.exists():
            with open(d3hsp, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if 'total number of' in line.lower() and 'solid' in line.lower():
                        parts = line.split()
                        for p in parts:
                            try:
                                tr.n_elements = int(p)
                            except ValueError:
                                continue
        
        # 벽시계 시간
        messag = dirpath / "messag"
        if messag.exists():
            with open(messag, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if 'elapsed time' in content.lower():
                for line in content.split('\n'):
                    if 'elapsed time' in line.lower():
                        parts = line.split()
                        for p in parts:
                            try:
                                tr.wall_time_s = float(p)
                            except ValueError:
                                continue
        
        results.append(tr)
        print(f"  피크 반력: {tr.peak_force:.1f} N")
        print(f"  에너지 비율: {tr.energy_ratio:.6f}")
    
    # h 기준 정렬 (coarsest → finest)
    results.sort(key=lambda x: -x.h)
    return results


# ============================================================
# Richardson 외삽 & GCI
# ============================================================

def richardson_extrapolation(h_list: List[float], 
                              f_list: List[float],
                              p_formal: float = 2.0
                              ) -> Dict[str, float]:
    """
    3-grid Richardson 외삽 + GCI 계산
    
    Args:
        h_list: 메시 크기 [h1(coarse), h2, h3(fine)]
        f_list: 해당 결과값 [f1, f2, f3]
        p_formal: 공칭 수렴 차수 (2차 요소 → 2)
    
    Returns:
        dict: {extrapolated, p_observed, gci_fine, gci_coarse, asymptotic_ratio}
    """
    if len(h_list) < 3 or len(f_list) < 3:
        return {'extrapolated': f_list[-1], 'p_observed': p_formal, 
                'gci_fine': 0.0, 'gci_coarse': 0.0, 'asymptotic_ratio': 1.0}
    
    # 가장 미세한 3개 선택
    pairs = sorted(zip(h_list, f_list), key=lambda x: -x[0])
    h1, f1 = pairs[0]  # coarsest
    h2, f2 = pairs[1]  # medium
    h3, f3 = pairs[2]  # finest
    
    r21 = h1 / h2
    r32 = h2 / h3
    
    eps21 = f2 - f1
    eps32 = f3 - f2
    
    # 관측 수렴 차수
    if abs(eps32) > 1e-15 and abs(eps21) > 1e-15:
        s = np.sign(eps32 / eps21)
        if s > 0 and abs(eps32/eps21) < 1.0:
            p_obs = abs(np.log(abs(eps21/eps32)) / np.log(r21))
        else:
            p_obs = p_formal
    else:
        p_obs = p_formal
    
    # 외삽값
    f_exact = f3 + (f3 - f2) / (r32**p_obs - 1)
    
    # GCI (Grid Convergence Index), Fs=1.25 (3 grids)
    Fs = 1.25
    if abs(f3) > 1e-15:
        gci_fine = Fs * abs((f3 - f2) / f3) / (r32**p_obs - 1) * 100  # %
        gci_coarse = Fs * abs((f2 - f1) / f2) / (r21**p_obs - 1) * 100
    else:
        gci_fine = 0.0
        gci_coarse = 0.0
    
    # 점근 수렴 비율 (≈1이면 asymptotic range)
    if gci_fine > 1e-15:
        asym = gci_coarse / (r21**p_obs * gci_fine) if gci_fine > 0 else 1.0
    else:
        asym = 1.0
    
    return {
        'extrapolated': f_exact,
        'p_observed': p_obs,
        'gci_fine': gci_fine,
        'gci_coarse': gci_coarse,
        'asymptotic_ratio': asym
    }


# ============================================================
# 수렴 분석 리포트
# ============================================================

def convergence_report(results: List[TierResult]) -> Dict:
    """수렴 분석 리포트 생성"""
    print("\n" + "="*70)
    print("  메시 수렴성 분석 리포트")
    print("="*70)
    
    h_list = [r.h for r in results]
    
    # — 피크 반력 수렴 —
    f_force = [r.peak_force for r in results]
    print("\n  [피크 반력 수렴]")
    print(f"  {'Tier':<20s} {'h (mm)':<8s} {'F_peak (N)':<12s} {'변화율':<10s}")
    print(f"  {'-'*52}")
    for i, r in enumerate(results):
        change = ""
        if i > 0 and results[i-1].peak_force > 0:
            pct = (r.peak_force - results[i-1].peak_force) / results[i-1].peak_force * 100
            change = f"{pct:+.2f}%"
        print(f"  {r.label:<20s} {r.h:<8.1f} {r.peak_force:<12.1f} {change:<10s}")
    
    rich_force = richardson_extrapolation(h_list, f_force)
    print(f"\n  Richardson 외삽값:  {rich_force['extrapolated']:.1f} N")
    print(f"  관측 수렴 차수:    {rich_force['p_observed']:.2f}")
    print(f"  GCI (fine mesh):   {rich_force['gci_fine']:.2f}%")
    print(f"  GCI (coarse mesh): {rich_force['gci_coarse']:.2f}%")
    print(f"  점근 비율:         {rich_force['asymptotic_ratio']:.3f} (≈1.0이면 수렴)")
    
    # — 에너지 흡수 수렴 —
    f_energy = [r.total_energy for r in results]
    print("\n  [에너지 흡수 수렴]")
    print(f"  {'Tier':<20s} {'h (mm)':<8s} {'IE (mJ)':<12s} {'변화율':<10s}")
    print(f"  {'-'*52}")
    for i, r in enumerate(results):
        change = ""
        if i > 0 and results[i-1].total_energy > 0:
            pct = (r.total_energy - results[i-1].total_energy) / results[i-1].total_energy * 100
            change = f"{pct:+.2f}%"
        print(f"  {r.label:<20s} {r.h:<8.1f} {r.total_energy:<12.1f} {change:<10s}")
    
    rich_energy = richardson_extrapolation(h_list, f_energy)
    print(f"\n  Richardson 외삽값:  {rich_energy['extrapolated']:.1f} mJ")
    print(f"  GCI (fine mesh):   {rich_energy['gci_fine']:.2f}%")
    
    # — 수렴 판정 —
    print("\n  [수렴 판정]")
    converged = True
    if len(results) >= 2:
        last_change_force = abs(f_force[-1] - f_force[-2]) / max(abs(f_force[-2]), 1e-10) * 100
        last_change_energy = abs(f_energy[-1] - f_energy[-2]) / max(abs(f_energy[-2]), 1e-10) * 100
        
        print(f"    최신 2-tier 피크반력 변화: {last_change_force:.2f}%")
        print(f"    최신 2-tier 에너지 변화:   {last_change_energy:.2f}%")
        
        if last_change_force < 5.0 and last_change_energy < 5.0:
            print("    → ✓ 수렴 달성 (<5% 변화)")
        elif last_change_force < 10.0 and last_change_energy < 10.0:
            print("    → △ 근사 수렴 (5-10% 변화)")
            converged = False
        else:
            print("    → ✗ 미수렴 (>10% 변화) — 더 미세한 메시 필요")
            converged = False
    
    # — 비용-정확도 효율 —
    print("\n  [비용-정확도 효율]")
    print(f"  {'Tier':<20s} {'요소 수':<12s} {'벽시계(s)':<10s} {'HG비(%)':<8s}")
    print(f"  {'-'*52}")
    for r in results:
        n_str = f"{r.n_elements:,}" if r.n_elements > 0 else "N/A"
        w_str = f"{r.wall_time_s:.0f}" if r.wall_time_s > 0 else "N/A"
        print(f"  {r.label:<20s} {n_str:<12s} {w_str:<10s} {r.hg_ratio:<8.2f}")
    
    print("\n" + "="*70)
    
    return {
        'force_convergence': rich_force,
        'energy_convergence': rich_energy,
        'converged': converged,
        'results': [vars(r) for r in results]
    }


# ============================================================
# 그래프
# ============================================================

def plot_convergence(results: List[TierResult], 
                     rich_force: Dict,
                     rich_energy: Dict,
                     outdir: Path) -> None:
    """수렴 그래프 생성"""
    if not HAS_MPL:
        return
    
    h = np.array([r.h for r in results])
    f_peak = np.array([r.peak_force for r in results])
    ie = np.array([r.total_energy for r in results])
    labels = [r.label.split('(')[0].strip() for r in results]
    
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 피크 반력 vs 메시 크기
    ax1.plot(h, f_peak, 'bo-', markersize=8, linewidth=2)
    ax1.axhline(y=rich_force['extrapolated'], color='r', linestyle='--', 
                alpha=0.7, label=f"Richardson = {rich_force['extrapolated']:.0f} N")
    for i, (hi, fi) in enumerate(zip(h, f_peak)):
        ax1.annotate(labels[i], (hi, fi), textcoords="offset points",
                    xytext=(5, 10), fontsize=8)
    ax1.set_xlabel('Element Size h (mm)')
    ax1.set_ylabel('Peak Force (N)')
    ax1.set_title(f"Peak Force Convergence (p={rich_force['p_observed']:.1f})")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.invert_xaxis()
    
    # 에너지 vs 메시 크기
    ax2.plot(h, ie, 'rs-', markersize=8, linewidth=2)
    ax2.axhline(y=rich_energy['extrapolated'], color='b', linestyle='--',
                alpha=0.7, label=f"Richardson = {rich_energy['extrapolated']:.0f} mJ")
    for i, (hi, iei) in enumerate(zip(h, ie)):
        ax2.annotate(labels[i], (hi, iei), textcoords="offset points",
                    xytext=(5, 10), fontsize=8)
    ax2.set_xlabel('Element Size h (mm)')
    ax2.set_ylabel('Internal Energy (mJ)')
    ax2.set_title(f"Energy Convergence (p={rich_energy['p_observed']:.1f})")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.invert_xaxis()
    
    plt.tight_layout()
    out = outdir / 'convergence_study.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  [그래프] {out}")
    
    # GCI 바 차트
    _fig2, ax3 = plt.subplots(figsize=(8, 4))
    tier_labels = labels[1:]  # GCI는 coarse→fine 쌍
    if len(tier_labels) >= 2:
        gci_vals = []
        for i in range(1, len(f_peak)):
            if f_peak[i-1] != 0:
                gci = 1.25 * abs(f_peak[i] - f_peak[i-1]) / abs(f_peak[i]) * 100
            else:
                gci = 0
            gci_vals.append(gci)
        
        x_pos = range(len(gci_vals))
        pair_labels = [f"{labels[i]}→{labels[i+1]}" for i in range(len(gci_vals))]
        colors = ['green' if g < 5 else 'orange' if g < 10 else 'red' for g in gci_vals]
        
        ax3.bar(x_pos, gci_vals, color=colors, edgecolor='k', alpha=0.8)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(pair_labels, fontsize=8)
        ax3.set_ylabel('GCI (%)')
        ax3.set_title('Grid Convergence Index (Force)')
        ax3.axhline(y=5.0, color='gray', linestyle='--', alpha=0.5, label='5% target')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        out2 = outdir / 'gci_chart.png'
        plt.savefig(out2, dpi=150)
        plt.close()
        print(f"  [그래프] {out2}")


# ============================================================
# CSV 내보내기
# ============================================================

def export_csv(results: List[TierResult], rich_force: Dict, 
               rich_energy: Dict, outdir: Path) -> None:
    """수렴 데이터 CSV 내보내기"""
    out = outdir / 'convergence_data.csv'
    with open(out, 'w', encoding='utf-8') as f:
        f.write("Tier,h_mm,n_jelly,n_elements,peak_force_N,total_energy_mJ,"
                "energy_ratio,hg_ratio_pct,wall_time_s\n")
        for r in results:
            f.write(f"{r.name},{r.h},{r.n_jelly},{r.n_elements},"
                    f"{r.peak_force:.2f},{r.total_energy:.2f},"
                    f"{r.energy_ratio:.6f},{r.hg_ratio:.2f},{r.wall_time_s:.0f}\n")
        
        f.write("\n# Richardson Extrapolation\n")
        f.write(f"# Force: extrapolated={rich_force['extrapolated']:.2f} N, "
                f"p_obs={rich_force['p_observed']:.2f}, "
                f"GCI_fine={rich_force['gci_fine']:.2f}%\n")
        f.write(f"# Energy: extrapolated={rich_energy['extrapolated']:.2f} mJ, "
                f"p_obs={rich_energy['p_observed']:.2f}, "
                f"GCI_fine={rich_energy['gci_fine']:.2f}%\n")
    
    print(f"  [CSV] {out}")


# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 배터리 메시 수렴성 분석")
    parser.add_argument("--dirs", nargs='+', 
                        metavar="TIER=DIR",
                        help="Tier별 결과 디렉토리 (예: tier-1=./res_t-1 tier0=./res_t0)")
    parser.add_argument("--config", type=str, default=None,
                        help="JSON 설정 파일")
    parser.add_argument("--outdir", type=str, default="./convergence_output",
                        help="출력 디렉토리")
    parser.add_argument("--plot", action="store_true", default=True,
                        help="그래프 생성 (기본: true)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    args = parser.parse_args()

    log = setup_logger(
        "convergence",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    
    tier_dirs: Dict[str, Path] = {}
    
    if args.config:
        with open(args.config, encoding='utf-8') as f:
            cfg = json.load(f)
        tier_dirs = {k: Path(v) for k, v in cfg.get('tier_dirs', {}).items()}
    elif args.dirs:
        for item in args.dirs:
            if '=' not in item:
                print("[오류] 형식: TIER=DIR (예: tier0=./results)")
                sys.exit(1)
            name, dpath = item.split('=', 1)
            tier_dirs[name] = Path(dpath)
    else:
        # 기본: 현재 디렉토리에서 tier 하위폴더 자동탐색
        for tier_name in TIER_SPECS.keys():
            for pattern in [tier_name, tier_name.replace('-', '_'), 
                          f"results_{tier_name}", f"res_{tier_name}"]:
                p = Path(pattern)
                if p.exists():
                    tier_dirs[tier_name] = p
                    break
    
    if len(tier_dirs) < 2:
        log.error("최소 2개 Tier 결과 필요")
        log.error("사용법: python convergence_study.py --dirs tier-1=DIR1 tier0=DIR2")
        sys.exit(1)
    
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    print("=== LS-DYNA 배터리 메시 수렴성 분석 ===")
    print(f"  Tiers: {', '.join(tier_dirs.keys())}")
    
    # 결과 수집
    results = collect_tier_results(tier_dirs)
    
    # 수렴 분석
    report = convergence_report(results)
    
    # 그래프
    if args.plot and HAS_MPL:
        print("\n  [그래프 생성]")
        plot_convergence(results, 
                        report['force_convergence'],
                        report['energy_convergence'], 
                        outdir)
    
    # CSV
    export_csv(results, 
              report['force_convergence'],
              report['energy_convergence'],
              outdir)
    
    # JSON 결과
    json_out = outdir / 'convergence_results.json'
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  [JSON] {json_out}")
    
    print("\n=== 수렴 분석 완료 ===")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as e:
        logging.getLogger("convergence").error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)
