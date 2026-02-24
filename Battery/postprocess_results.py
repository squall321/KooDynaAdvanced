"""
LS-DYNA 배터리 시뮬레이션 후처리 자동화 스크립트
================================================
binout/ASCII 출력 파일 파싱 → 에너지, 온도, 반력, 단락 지표 추출 → 그래프

Usage:
  python postprocess_results.py --dir ./results_phase1
  python postprocess_results.py --dir ./results_phase2 --plot
  python postprocess_results.py --dir . --all
"""

import argparse
import sys
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np

from battery_utils import setup_logger

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use('Agg')  # 비대화형 백엔드
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    logger.warning("matplotlib 없음 — 그래프 출력 비활성. pip install matplotlib")


# ============================================================
# ASCII 출력 파싱 (glstat, matsum, rcforc 등)
# ============================================================

def parse_ascii_file(filepath: Path) -> Dict[str, List[float]]:
    """LS-DYNA ASCII 출력 파일 (glstat, matsum 등) 파싱
    
    Returns:
        dict: {컬럼명: [값 리스트]}
    """
    if not filepath.exists():
        return {}
    
    data = {}
    headers = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 헤더 파싱
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('$') or line.startswith('*') or not line:
            i += 1
            continue
        # 첫 숫자 행을 찾으면 그 이전까지 헤더
        try:
            float(line.split()[0])
            break
        except (ValueError, IndexError):
            headers.append(line)
            i += 1
    
    # 데이터 파싱
    values = []
    while i < len(lines):
        line = lines[i].strip()
        if line and not line.startswith('$') and not line.startswith('*'):
            try:
                row = [float(x) for x in line.split()]
                values.append(row)
            except ValueError:
                pass
        i += 1
    
    if not values:
        return {}
    
    # numpy 배열화
    arr = np.array(values)
    n_cols = arr.shape[1]
    
    # 기본 컬럼명
    default_names = [f"col_{i}" for i in range(n_cols)]
    if n_cols >= 2:
        default_names[0] = "time"
    
    for j in range(n_cols):
        name = default_names[j] if j >= len(headers) else headers[j]
        data[name] = arr[:, j].tolist()
    
    return data


def parse_glstat(dirpath: Path) -> Optional[Dict[str, np.ndarray]]:
    """glstat 파일 파싱 — 전역 에너지/질량 스케일링 이력"""
    filepath = dirpath / "glstat"
    if not filepath.exists():
        # 대안: glstat_out 등
        for alt in ["glstat_out", "GLSTAT", "glstat.csv"]:
            alt_path = dirpath / alt
            if alt_path.exists():
                filepath = alt_path
                break
    
    if not filepath.exists():
        return None
    
    print(f"  [glstat] {filepath}")
    logger.debug("glstat 파싱: %s", filepath)
    
    # LS-DYNA glstat 형식: 블록 단위
    # 각 시간스텝에서 KE, IE, TE, etc 출력
    result = {
        'time': [], 'kinetic_energy': [], 'internal_energy': [],
        'total_energy': [], 'ratio': [], 'added_mass': [],
        'contact_energy': [], 'hourglass_energy': []
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 블록 기반 파싱
    blocks = content.split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        t_val = ke_val = ie_val = te_val = None
        ratio_val = mass_val = ce_val = hg_val = 0.0
        
        for line in lines:
            line_lower = line.lower()
            parts = line.split()
            if len(parts) < 2:
                continue
            
            try:
                val = float(parts[-1])
            except ValueError:
                continue
            
            if 'time' in line_lower and 'timestep' not in line_lower:
                t_val = val
            elif 'kinetic energy' in line_lower:
                ke_val = val
            elif 'internal energy' in line_lower:
                ie_val = val
            elif 'total energy' in line_lower:
                te_val = val
            elif 'energy ratio' in line_lower:
                ratio_val = val
            elif 'added mass' in line_lower or 'mass increase' in line_lower:
                mass_val = val
            elif 'contact energy' in line_lower or 'sliding' in line_lower:
                ce_val = val
            elif 'hourglass' in line_lower:
                hg_val = val
        
        if t_val is not None and ke_val is not None:
            result['time'].append(t_val)
            result['kinetic_energy'].append(ke_val)
            result['internal_energy'].append(ie_val or 0)
            result['total_energy'].append(te_val or 0)
            result['ratio'].append(ratio_val)
            result['added_mass'].append(mass_val)
            result['contact_energy'].append(ce_val)
            result['hourglass_energy'].append(hg_val)
    
    if not result['time']:
        return None
    
    return {k: np.array(v) for k, v in result.items()}


def parse_rcforc(dirpath: Path) -> Optional[Dict[str, np.ndarray]]:
    """rcforc 파일 파싱 — 접촉 반력 이력"""
    filepath = dirpath / "rcforc"
    if not filepath.exists():
        return None
    
    print(f"  [rcforc] {filepath}")
    logger.debug("rcforc 파싱: %s", filepath)
    result = {'time': [], 'force_x': [], 'force_y': [], 'force_z': [], 'force_mag': []}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('$') or line.startswith('*'):
                continue
            parts = line.split()
            if len(parts) >= 4:
                try:
                    t = float(parts[0])
                    fx = float(parts[1])
                    fy = float(parts[2])
                    fz = float(parts[3])
                    result['time'].append(t)
                    result['force_x'].append(fx)
                    result['force_y'].append(fy)
                    result['force_z'].append(fz)
                    result['force_mag'].append(np.sqrt(fx**2 + fy**2 + fz**2))
                except ValueError:
                    continue
    
    if not result['time']:
        return None
    
    return {k: np.array(v) for k, v in result.items()}


# ============================================================
# 결과 분석 지표
# ============================================================

@dataclass
class AnalysisMetrics:
    """해석 결과 주요 지표"""
    # 에너지
    peak_kinetic_energy: float = 0.0
    final_internal_energy: float = 0.0
    energy_ratio: float = 0.0
    max_added_mass_pct: float = 0.0
    max_hourglass_ratio: float = 0.0
    
    # 반력
    peak_force: float = 0.0
    peak_force_time: float = 0.0
    mean_plateau_force: float = 0.0
    
    # 온도
    max_temperature: float = 298.15
    thermal_runaway_time: float = -1.0  # -1 = 미발생
    
    # 단락
    short_circuit_time: float = -1.0    # -1 = 미발생
    
    # 시뮬레이션
    end_time: float = 0.0
    total_cycles: int = 0


def compute_metrics(glstat: Optional[Dict], rcforc: Optional[Dict]) -> AnalysisMetrics:
    """결과 데이터에서 주요 지표 계산"""
    m = AnalysisMetrics()
    
    if glstat is not None:
        m.peak_kinetic_energy = float(np.max(glstat['kinetic_energy']))
        m.final_internal_energy = float(glstat['internal_energy'][-1])
        m.energy_ratio = float(glstat['ratio'][-1]) if len(glstat['ratio']) > 0 else 0
        m.end_time = float(glstat['time'][-1])
        
        # 질량 스케일링 비율
        if np.max(np.abs(glstat['added_mass'])) > 0:
            # 상대 질량 증가량 추정
            m.max_added_mass_pct = float(np.max(glstat['added_mass']))
        
        # 아워글라스 에너지 비율
        if m.final_internal_energy > 0:
            max_hg = float(np.max(glstat['hourglass_energy']))
            m.max_hourglass_ratio = max_hg / m.final_internal_energy * 100
    
    if rcforc is not None:
        m.peak_force = float(np.max(rcforc['force_mag']))
        idx_peak = int(np.argmax(rcforc['force_mag']))
        m.peak_force_time = float(rcforc['time'][idx_peak])
        
        # 평탄부 평균 (피크의 50%~80% 시간 구간)
        t = rcforc['time']
        f = rcforc['force_mag']
        t_half = t[idx_peak] * 0.5 if idx_peak > 0 else 0
        t_80 = t[idx_peak] * 0.8 if idx_peak > 0 else 0
        mask = (t >= t_half) & (t <= t_80)
        if np.any(mask):
            m.mean_plateau_force = float(np.mean(f[mask]))
    
    return m


# ============================================================
# 그래프 생성
# ============================================================

def plot_energy(glstat: Dict, outdir: Path) -> None:
    """에너지 이력 그래프"""
    if not HAS_MPL:
        return
    
    _fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    t = glstat['time'] * 1000  # ms
    
    ax1.plot(t, glstat['kinetic_energy'], 'b-', label='Kinetic Energy', linewidth=1.5)
    ax1.plot(t, glstat['internal_energy'], 'r-', label='Internal Energy', linewidth=1.5)
    ax1.plot(t, glstat['total_energy'], 'k--', label='Total Energy', linewidth=1)
    if np.any(glstat['contact_energy'] != 0):
        ax1.plot(t, glstat['contact_energy'], 'g-', label='Contact Energy', linewidth=1)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Energy (mJ)')
    ax1.set_title('Energy History')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 에너지 비율
    ax2.plot(t, glstat['ratio'], 'k-', linewidth=1.5)
    ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Target=1.0')
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Energy Ratio')
    ax2.set_title('Energy Balance Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out = outdir / 'energy_history.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  [그래프] {out}")


def plot_force(rcforc: Dict, outdir: Path) -> None:
    """반력 이력 그래프"""
    if not HAS_MPL:
        return
    
    _fig, ax = plt.subplots(figsize=(10, 5))
    
    t = rcforc['time'] * 1000  # ms
    
    ax.plot(t, rcforc['force_x'], 'r-', label='Fx', alpha=0.7)
    ax.plot(t, rcforc['force_y'], 'g-', label='Fy', alpha=0.7)
    ax.plot(t, rcforc['force_z'], 'b-', label='Fz', alpha=0.7)
    ax.plot(t, rcforc['force_mag'], 'k-', label='|F|', linewidth=2)
    
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Force (N)')
    ax.set_title('Contact Force History (Impactor → Cell)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out = outdir / 'force_history.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  [그래프] {out}")


def plot_force_displacement(rcforc: Dict, glstat: Dict, outdir: Path, impactor_velocity: float = 5000.0) -> None:
    """반력-변위 커브 (에너지 흡수 특성)
    
    Args:
        rcforc: 반력 데이터
        glstat: 전역 통계 데이터
        outdir: 출력 디렉토리
        impactor_velocity: 임팩터 속도 (mm/s, 기본 5000 = 5 m/s)
    """
    if not HAS_MPL or glstat is None:
        return
    
    _fig, ax = plt.subplots(figsize=(8, 6))
    
    # 변위 = ∫v·dt
    t = rcforc['time']
    dt = np.diff(t, prepend=0)
    v = impactor_velocity  # mm/s
    disp = np.cumsum(dt * v)
    
    ax.plot(disp, rcforc['force_mag'], 'b-', linewidth=1.5)
    ax.set_xlabel('Displacement (mm)')
    ax.set_ylabel('Force (N)')
    ax.set_title('Force-Displacement Curve')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    out = outdir / 'force_displacement.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  [그래프] {out}")


# ============================================================
# 검증 리포트
# ============================================================

def print_report(metrics: AnalysisMetrics) -> None:
    """결과 검증 리포트 출력"""
    print("\n" + "="*60)
    print("  LS-DYNA 배터리 시뮬레이션 결과 리포트")
    print("="*60)
    
    print(f"\n  해석 종료 시간: {metrics.end_time*1000:.3f} ms")
    
    print("\n  [에너지]")
    print(f"    피크 운동에너지:    {metrics.peak_kinetic_energy:.2f} mJ")
    print(f"    최종 내부에너지:    {metrics.final_internal_energy:.2f} mJ")
    print(f"    에너지 비율:        {metrics.energy_ratio:.6f}")
    print(f"    아워글라스 비율:    {metrics.max_hourglass_ratio:.2f}%")
    
    # 검증 판정
    energy_ok = abs(1.0 - metrics.energy_ratio) < 0.05
    hg_ok = metrics.max_hourglass_ratio < 10.0
    
    print(f"    에너지 보존:        {'✓ PASS' if energy_ok else '✗ FAIL'} "
          f"(|1-ratio| < 5%)")
    print(f"    아워글라스:         {'✓ PASS' if hg_ok else '⚠ WARNING'} "
          f"(< 10%)")
    
    print("\n  [반력]")
    print(f"    피크 반력:          {metrics.peak_force:.1f} N")
    print(f"    피크 시점:          {metrics.peak_force_time*1000:.3f} ms")
    print(f"    평탄부 평균:        {metrics.mean_plateau_force:.1f} N")
    
    if metrics.max_temperature > 298.15:
        print("\n  [온도]")
        print(f"    최대 온도:          {metrics.max_temperature:.1f} K "
              f"({metrics.max_temperature-273.15:.1f}°C)")
        if metrics.thermal_runaway_time > 0:
            print(f"    열폭주 시점:        {metrics.thermal_runaway_time:.3f} s")
    
    print("\n" + "="*60)


# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 배터리 시뮬레이션 후처리 도구")
    parser.add_argument("--dir", type=str, default=".",
                        help="결과 디렉토리 (default: 현재)")
    parser.add_argument("--plot", action="store_true",
                        help="그래프 생성")
    parser.add_argument("--all", action="store_true",
                        help="모든 분석 + 그래프")
    parser.add_argument("--outdir", type=str, default=None,
                        help="그래프 출력 디렉토리 (default: --dir)")
    parser.add_argument("--config", type=str, default="battery_config.yaml",
                        help="YAML 설정 파일 경로 (default: battery_config.yaml)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    args = parser.parse_args()

    log = setup_logger(
        "postprocess",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    dirpath = Path(args.dir)
    if not dirpath.exists():
        log.error("디렉토리 없음: %s", dirpath)
        sys.exit(1)
    
    outdir = Path(args.outdir) if args.outdir else dirpath
    outdir.mkdir(parents=True, exist_ok=True)
    
    # YAML 설정 로드 (optional, 임팩터 속도 가져오기 위함)
    impactor_velocity = 5000.0  # 기본값 (5 m/s = 5000 mm/s)
    config_path = Path(args.config)
    if config_path.exists():
        try:
            from battery_utils import load_config  # lazy import — optional dependency
            config = load_config(str(config_path), validate=False, logger=log)
            impactor_velocity = config.get('boundary_conditions', {}).get('loads', {}).get('impactor_velocity', {}).get('magnitude', 5000.0)
        except (FileNotFoundError, KeyError, ValueError, OSError) as e:
            log.warning("YAML 로드 실패 (%s), 기본값 사용: %s mm/s", e, impactor_velocity)
    
    do_plot = args.plot or args.all
    
    print("=== LS-DYNA 배터리 후처리 ===")
    print(f"  결과 디렉토리: {dirpath}")
    print(f"  임팩터 속도: {impactor_velocity} mm/s ({impactor_velocity/1000:.1f} m/s)")
    
    # 파싱
    glstat = parse_glstat(dirpath)
    rcforc = parse_rcforc(dirpath)
    
    if glstat is None and rcforc is None:
        log.warning("파싱 가능한 출력 파일 없음 (glstat, rcforc)")
        log.warning("LS-DYNA 실행 후 이 스크립트를 실행하세요.")
        sys.exit(0)
    
    # 지표 계산
    metrics = compute_metrics(glstat, rcforc)
    
    # 리포트 출력
    print_report(metrics)
    
    # 그래프 생성
    if do_plot and HAS_MPL:
        print("\n  [그래프 생성]")
        if glstat is not None:
            plot_energy(glstat, outdir)
        if rcforc is not None:
            plot_force(rcforc, outdir)
            if glstat is not None:
                plot_force_displacement(rcforc, glstat, outdir, impactor_velocity=impactor_velocity)
    
    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()
