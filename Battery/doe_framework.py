"""
LS-DYNA 배터리 시뮬레이션 DOE (Design of Experiments) 프레임워크
================================================================
실험계획법 기반 파라미터 스터디 자동화:
  - Latin Hypercube Sampling (LHS)
  - Full/Fractional Factorial
  - Box-Behnken
  - 또는 사용자 정의 파라미터 조합

파라미터 변경 → k-file 자동 생성 → (선택) 실행 → 후처리 → 응답면

Usage:
  python doe_framework.py --method lhs --n 30 --outdir ./doe_runs
  python doe_framework.py --method factorial --levels 3 --outdir ./doe_runs
  python doe_framework.py --config doe_config.json
  python doe_framework.py --postprocess ./doe_runs

의존성:
  - numpy (필수)
  - scipy (LHS, 선택)
  - matplotlib (응답면 그래프, 선택)
"""

import argparse
import json
import logging
import shutil
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import numpy as np

from battery_utils import setup_logger

logger = logging.getLogger(__name__)

try:
    from scipy.stats import qmc
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.info("scipy 없음 — LHS 비활성")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    logger.info("matplotlib 없음 — 그래프 비활성")

# 후처리 모듈
try:
    from postprocess_results import parse_glstat, parse_rcforc, compute_metrics
    HAS_PP = True
except ImportError:
    HAS_PP = False
    logger.info("postprocess_results 없음 — 후처리 비활성")


# ============================================================
# DOE 파라미터 정의
# ============================================================

@dataclass
class DOEParameter:
    """단일 DOE 파라미터 정의"""
    name: str               # 파라미터 이름 (고유)
    kfile: str              # 대상 k-file (예: "06_boundary_loads.k")
    keyword: str            # LS-DYNA 키워드 (예: "*BOUNDARY_CONVECTION_SET")
    field: str              # 필드명 (예: "HMULT")
    card: int               # 카드 번호 (1-based)
    col: int                # 컬럼 위치 (1-based, 8개 필드 중)
    low: float              # 하한
    high: float             # 상한
    nominal: float          # 기본값
    units: str = ""         # 단위
    description: str = ""   # 설명
    log_scale: bool = False # 로그 스케일 샘플링


# ============================================================
# 기본 DOE 파라미터 세트 — 배터리 시뮬레이션 핵심 인자
# ============================================================

DEFAULT_PARAMETERS: List[DOEParameter] = [
    # --- 재료 물성 ---
    DOEParameter(
        name="separator_yield",
        kfile="04_materials.k",
        keyword="*MAT_PIECEWISE_LINEAR_PLASTICITY",
        field="SIGY",
        card=1, col=1,
        low=40.0, high=120.0, nominal=80.0,
        units="MPa",
        description="분리막 항복 응력 — 셀 강성 및 단락 시점 좌우"
    ),
    DOEParameter(
        name="separator_fail_strain",
        kfile="04_materials.k",
        keyword="*MAT_PIECEWISE_LINEAR_PLASTICITY",
        field="FAIL",
        card=1, col=5,
        low=0.10, high=0.50, nominal=0.25,
        units="-",
        description="분리막 파단 변형률 → 내부 단락 트리거"
    ),
    DOEParameter(
        name="foam_crush_strength",
        kfile="04_materials_tempdep.k",
        keyword="*DEFINE_CURVE",
        field="SFO",  # ordinate scale factor
        card=0, col=4,  # DEFINE_CURVE header card
        low=0.5, high=2.0, nominal=1.0,
        units="-",
        description="전극 압축 강도 스케일 팩터 (응력-변형률 커브 SFO)"
    ),
    # --- 경계 조건 ---
    DOEParameter(
        name="impactor_velocity",
        kfile="06_boundary_loads.k",
        keyword="*BOUNDARY_PRESCRIBED_MOTION_RIGID",
        field="SF",
        card=1, col=7,
        low=1.0, high=10.0, nominal=5.0,
        units="m/s",
        description="임팩터 속도 (관통 시험 기준)"
    ),
    DOEParameter(
        name="convection_htc",
        kfile="06_boundary_loads.k",
        keyword="*BOUNDARY_CONVECTION_SET",
        field="HMULT",
        card=2, col=2,
        low=2.0, high=20.0, nominal=5.0,
        units="W/m²·K → mW/mm²·K",
        description="자유 대류 열전달 계수"
    ),
    DOEParameter(
        name="ambient_temp",
        kfile="06_boundary_loads.k",
        keyword="*BOUNDARY_CONVECTION_SET",
        field="TMULT",
        card=2, col=4,
        low=253.15, high=328.15, nominal=298.15,
        units="K",
        description="환경 온도 (253K=-20°C ~ 328K=55°C)"
    ),
    # --- 솔버 파라미터 ---
    DOEParameter(
        name="contact_friction",
        kfile="05_contacts.k",
        keyword="*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_THERMAL",
        field="FS",
        card=2, col=1,
        low=0.05, high=0.50, nominal=0.20,
        units="-",
        description="접촉 마찰 계수 (층간 슬립 거동)"
    ),
    # --- EM 파라미터 ---
    DOEParameter(
        name="randles_R_sei",
        kfile="08_em_randles.k",
        keyword="*EM_RANDLES_SOLID",
        field="R_SEI",
        card=2, col=5,
        low=0.005, high=0.100, nominal=0.020,
        units="Ω",
        description="SEI 저항 — 발열량 및 내부저항 결정"
    ),
]


# ============================================================
# 샘플링 메서드
# ============================================================

def generate_lhs(params: List[DOEParameter], n_samples: int,
                 seed: int = 42) -> np.ndarray:
    """Latin Hypercube Sampling
    
    Returns: (n_samples, n_params) 배열, 각 파라미터 범위 내 실제값
    """
    if HAS_SCIPY:
        sampler = qmc.LatinHypercube(d=len(params), seed=seed)
        unit_samples = sampler.random(n=n_samples)
    else:
        # scipy 없을 때 수동 LHS 구현
        rng = np.random.default_rng(seed)
        unit_samples = np.zeros((n_samples, len(params)))
        for j in range(len(params)):
            perm = rng.permutation(n_samples)
            for i in range(n_samples):
                unit_samples[i, j] = (perm[i] + rng.random()) / n_samples
    
    # 실제 범위로 변환
    samples = np.zeros_like(unit_samples)
    for j, p in enumerate(params):
        if p.log_scale:
            log_low = np.log10(p.low)
            log_high = np.log10(p.high)
            samples[:, j] = 10 ** (log_low + unit_samples[:, j] * (log_high - log_low))
        else:
            samples[:, j] = p.low + unit_samples[:, j] * (p.high - p.low)
    
    return samples


def generate_factorial(params: List[DOEParameter], 
                       levels: int = 3) -> np.ndarray:
    """Full Factorial (levels^n_params 조합)"""
    # 레벨별 값 생성
    level_vals = []
    for p in params:
        if p.log_scale:
            vals = np.logspace(np.log10(p.low), np.log10(p.high), levels)
        else:
            vals = np.linspace(p.low, p.high, levels)
        level_vals.append(vals)
    
    # 전체 조합 (Cartesian product)
    grids = np.meshgrid(*level_vals, indexing='ij')
    samples = np.column_stack([g.ravel() for g in grids])
    
    return samples


def generate_box_behnken(params: List[DOEParameter]) -> np.ndarray:
    """Box-Behnken 디자인 (2차 응답면용)
    
    최소 3개 파라미터 필요. 코너점 없음 → 극단값 회피.
    """
    n_params = len(params)
    if n_params < 3:
        print("[경고] Box-Behnken은 최소 3개 파라미터 필요. 3-level factorial로 대체.")
        return generate_factorial(params, levels=3)
    
    # 중심점 + 에지점 조합
    # 코딩: -1, 0, +1
    coded = []
    
    # 2-factor 조합 (나머지는 center)
    for i in range(n_params):
        for j in range(i + 1, n_params):
            for vi in [-1, 1]:
                for vj in [-1, 1]:
                    point = [0] * n_params
                    point[i] = vi
                    point[j] = vj
                    coded.append(point)
    
    # 중심점 3회 반복 (순수 오차 추정)
    for _ in range(3):
        coded.append([0] * n_params)
    
    coded = np.array(coded, dtype=float)
    
    # 실제값 변환
    samples = np.zeros_like(coded)
    for j, p in enumerate(params):
        mid = (p.low + p.high) / 2
        half = (p.high - p.low) / 2
        if p.log_scale:
            log_mid = (np.log10(p.low) + np.log10(p.high)) / 2
            log_half = (np.log10(p.high) - np.log10(p.low)) / 2
            samples[:, j] = 10 ** (log_mid + coded[:, j] * log_half)
        else:
            samples[:, j] = mid + coded[:, j] * half
    
    return samples


def generate_one_at_a_time(params: List[DOEParameter],
                           levels: int = 5) -> np.ndarray:
    """One-at-a-time (OAT) 민감도 분석
    각 인자를 개별적으로 변화, 나머지는 nominal값 유지
    """
    samples_list = []
    
    # 기준점 (nominal)
    nominal = np.array([p.nominal for p in params])
    samples_list.append(nominal.copy())
    
    for j, p in enumerate(params):
        if p.log_scale:
            vals = np.logspace(np.log10(p.low), np.log10(p.high), levels)
        else:
            vals = np.linspace(p.low, p.high, levels)
        
        for v in vals:
            if abs(v - p.nominal) / max(abs(p.nominal), 1e-15) > 0.01:
                point = nominal.copy()
                point[j] = v
                samples_list.append(point)
    
    return np.array(samples_list)


# ============================================================
# k-file 파라미터 치환
# ============================================================

def modify_kfile(src_dir: Path, dest_dir: Path, kfile: str,
                 modifications: Dict[str, float],
                 params: List[DOEParameter]) -> None:
    """k-file 복사 후 파라미터 치환
    
    접근: 주석 기반 마커 또는 행 위치 기반 치환
    → 단순하고 안정적: SFO, HMULT 등 고유 필드명 주석 검색
    """
    src_path = src_dir / kfile
    dest_path = dest_dir / kfile
    
    if not src_path.exists():
        # 대상 파일이 없으면 다른 k-file에서 해당 파라미터가 있을 수 있음
        return
    
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 파일별 수정할 파라미터 필터
    file_params = [p for p in params if p.kfile == kfile and p.name in modifications]
    
    if not file_params:
        # 수정 필요 없음 → 원본 복사
        shutil.copy2(src_path, dest_path)
        return
    
    lines = content.split('\n')
    
    for param in file_params:
        new_val = modifications[param.name]
        
        # 전략: 키워드 블록을 찾고, 해당 카드의 해당 컬럼을 교체
        # 키워드 매칭
        kw_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith(param.keyword):
                kw_idx = i
                break
        
        if kw_idx is None:
            print(f"  [경고] 키워드 '{param.keyword}' 미발견: {kfile}")
            continue
        
        # 키워드 이후 데이터 카드 카운트 (주석/빈줄 건너뜀)
        card_count = 0
        target_line = None
        for i in range(kw_idx + 1, min(kw_idx + 30, len(lines))):
            line = lines[i].strip()
            if not line or line.startswith('$'):
                continue
            card_count += 1
            if card_count == param.card:
                target_line = i
                break
        
        if target_line is None:
            print(f"  [경고] Card {param.card} 미발견: {param.name} in {kfile}")
            continue
        
        # 고정폭 필드 교체 (LS-DYNA 8칸 × 10문자 또는 자유형식)
        original_line = lines[target_line]
        
        # 자유형식 (공백 구분) 파싱
        fields = original_line.split()
        if param.col <= len(fields):
            old_val = fields[param.col - 1]
            
            # 새 값 포맷팅 (원래 필드 길이 유지 시도)
            if '.' in old_val or 'E' in old_val.upper():
                # 부동소수점
                if abs(new_val) >= 1e4 or (abs(new_val) < 0.01 and new_val != 0):
                    new_str = f"{new_val:.4E}"
                else:
                    new_str = f"{new_val:.4f}"
            else:
                new_str = str(int(new_val)) if new_val == int(new_val) else f"{new_val:.4f}"
            
            # 필드 교체
            fields[param.col - 1] = new_str
            
            # 고정폭 복원 (10칸 필드)
            new_line = ""
            for fld in fields:
                new_line += fld.rjust(10)
            
            lines[target_line] = new_line
        else:
            print(f"  [경고] Col {param.col} > 필드 수 {len(fields)}: {param.name}")
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def create_run_directory(base_dir: Path, src_dir: Path, run_id: int,
                         sample: np.ndarray, params: List[DOEParameter]) -> Path:
    """단일 DOE run 디렉토리 생성: 모든 k-file 복사 + 파라미터 치환"""
    run_dir = base_dir / f"run_{run_id:04d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # 파라미터 매핑
    modifications = {p.name: sample[j] for j, p in enumerate(params)}
    
    # 변경 대상 파일 목록
    affected_kfiles = set(p.kfile for p in params)
    
    # 모든 k-file 복사 (변경 대상은 수정, 나머지는 원본 복사)
    for item in src_dir.glob("*.k"):
        if item.name in affected_kfiles:
            modify_kfile(src_dir, run_dir, item.name, modifications, params)
        else:
            shutil.copy2(item, run_dir / item.name)
    
    # 파라미터 메타데이터 저장
    meta = {
        'run_id': run_id,
        'parameters': {p.name: float(sample[j]) for j, p in enumerate(params)},
        'parameter_details': {p.name: {
            'value': float(sample[j]),
            'nominal': p.nominal,
            'low': p.low,
            'high': p.high,
            'units': p.units,
            'kfile': p.kfile,
            'description': p.description
        } for j, p in enumerate(params)}
    }
    
    with open(run_dir / 'doe_params.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    return run_dir


# ============================================================
# 후처리 — 결과 수집 + 응답면
# ============================================================

@dataclass
class DOEResult:
    """단일 run의 결과"""
    run_id: int
    params: Dict[str, float]
    peak_force: float = 0.0
    total_energy: float = 0.0
    energy_ratio: float = 1.0
    max_temperature: float = 298.15
    hg_ratio: float = 0.0
    short_circuit_time: float = -1.0
    thermal_runaway: bool = False
    converged: bool = True


def collect_doe_results(base_dir: Path, _params: List[DOEParameter]) -> List[DOEResult]:
    """모든 DOE run 디렉토리에서 결과 수집"""
    results = []
    
    for run_dir in sorted(base_dir.glob("run_*")):
        if not run_dir.is_dir():
            continue
        
        # 메타데이터 로드
        meta_path = run_dir / 'doe_params.json'
        if not meta_path.exists():
            continue
        
        with open(meta_path, encoding='utf-8') as f:
            meta = json.load(f)
        
        run_id = meta['run_id']
        param_vals = meta['parameters']
        
        dr = DOEResult(run_id=run_id, params=param_vals)
        
        # 결과 파싱
        if HAS_PP:
            glstat = parse_glstat(run_dir)
            rcforc = parse_rcforc(run_dir)
            
            if glstat is not None or rcforc is not None:
                metrics = compute_metrics(glstat, rcforc)
                dr.peak_force = metrics.peak_force
                dr.total_energy = metrics.final_internal_energy
                dr.energy_ratio = metrics.energy_ratio
                dr.max_temperature = metrics.max_temperature
                dr.hg_ratio = metrics.max_hourglass_ratio
                dr.short_circuit_time = metrics.short_circuit_time
                dr.thermal_runaway = metrics.max_temperature > 473.15  # >200°C
                dr.converged = abs(1.0 - metrics.energy_ratio) < 0.10
        
        results.append(dr)
    
    return results


def sensitivity_analysis(results: List[DOEResult],
                         params: List[DOEParameter]) -> Dict[str, Dict[str, float]]:
    """선형 민감도 분석 (정규화된 편회귀 계수)"""
    if len(results) < 3:
        print("[경고] 민감도 분석에 최소 3개 run 필요")
        return {}
    
    # 입력 행렬 X, 응답 벡터 Y
    _param_names = [p.name for p in params]  # reserved for extended analysis
    X = np.zeros((len(results), len(params)))
    responses = {
        'peak_force': np.zeros(len(results)),
        'total_energy': np.zeros(len(results)),
        'max_temperature': np.zeros(len(results)),
    }
    
    for i, r in enumerate(results):
        for j, p in enumerate(params):
            X[i, j] = r.params.get(p.name, p.nominal)
        responses['peak_force'][i] = r.peak_force
        responses['total_energy'][i] = r.total_energy
        responses['max_temperature'][i] = r.max_temperature
    
    # 정규화 (z-score)
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_norm = (X - X_mean) / X_std
    
    sensitivity = {}
    
    for resp_name, y in responses.items():
        y_mean = y.mean()
        y_std = y.std()
        if y_std == 0:
            sensitivity[resp_name] = {p.name: 0.0 for p in params}
            continue
        
        y_norm = (y - y_mean) / y_std
        
        # 최소자승 선형 회귀
        # β = (XᵀX)⁻¹ Xᵀ y
        try:
            # 절편항 추가
            X_aug = np.column_stack([np.ones(len(results)), X_norm])
            beta = np.linalg.lstsq(X_aug, y_norm, rcond=None)[0]
            
            # 표준화 회귀 계수 (절편 제외)
            sensitivity[resp_name] = {}
            for j, p in enumerate(params):
                sensitivity[resp_name][p.name] = float(beta[j + 1])
        except np.linalg.LinAlgError:
            sensitivity[resp_name] = {p.name: 0.0 for p in params}
    
    return sensitivity


# ============================================================
# 리포트 & 그래프
# ============================================================

def print_doe_report(results: List[DOEResult], params: List[DOEParameter],
                     sensitivity: Dict) -> None:
    """DOE 결과 리포트 출력"""
    print("\n" + "=" * 78)
    print("  DOE (Design of Experiments) 결과 리포트")
    print("=" * 78)
    
    print(f"\n  총 Run 수:   {len(results)}")
    print(f"  파라미터 수: {len(params)}")
    
    converged = [r for r in results if r.converged]
    _failures = [r for r in results if not r.converged]  # reserved for future report
    print(f"  수렴:        {len(converged)} / {len(results)}")
    
    # 응답 통계
    if results:
        forces = [r.peak_force for r in results if r.peak_force > 0]
        temps = [r.max_temperature for r in results if r.max_temperature > 298]
        energies = [r.total_energy for r in results if r.total_energy > 0]
        
        print("\n  [응답 통계]")
        if forces:
            print(f"    피크 반력:  min={min(forces):.0f} / mean={np.mean(forces):.0f} "
                  f"/ max={max(forces):.0f} N")
        if energies:
            print(f"    흡수 에너지: min={min(energies):.0f} / mean={np.mean(energies):.0f} "
                  f"/ max={max(energies):.0f} mJ")
        if temps:
            print(f"    최대 온도:  min={min(temps):.0f} / mean={np.mean(temps):.0f} "
                  f"/ max={max(temps):.0f} K")
        
        tr_count = sum(1 for r in results if r.thermal_runaway)
        print(f"    열폭주 발생: {tr_count} / {len(results)} runs")
    
    # 민감도
    if sensitivity:
        print("\n  [민감도 분석 — 표준화 회귀 계수 (SRC)]")
        for resp_name, sens in sensitivity.items():
            print(f"\n  {resp_name}:")
            sorted_sens = sorted(sens.items(), key=lambda x: abs(x[1]), reverse=True)
            for pname, val in sorted_sens:
                bar = "█" * int(abs(val) * 20)
                sign = "+" if val > 0 else "-"
                print(f"    {pname:<25s} {sign}{abs(val):.3f}  {bar}")
    
    print("\n" + "=" * 78)


def plot_doe_results(results: List[DOEResult], params: List[DOEParameter],
                     sensitivity: Dict, outdir: Path) -> None:
    """DOE 결과 그래프"""
    if not HAS_MPL or not results:
        return
    
    # 1. 민감도 토네이도 차트
    for resp_name, sens in sensitivity.items():
        _fig, ax = plt.subplots(figsize=(10, max(4, len(params) * 0.5)))
        
        sorted_items = sorted(sens.items(), key=lambda x: abs(x[1]))
        labels = [x[0] for x in sorted_items]
        values = [x[1] for x in sorted_items]
        
        colors = ['green' if v >= 0 else 'red' for v in values]
        y_pos = range(len(labels))
        
        ax.barh(y_pos, values, color=colors, edgecolor='k', alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel('Standardized Regression Coefficient (SRC)')
        ax.set_title(f'Sensitivity: {resp_name}')
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        out = outdir / f'sensitivity_{resp_name}.png'
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"  [그래프] {out}")
    
    # 2. 파라미터 vs 응답 산점도 (상위 4 민감 인자)
    if 'peak_force' in sensitivity:
        top_params = sorted(sensitivity['peak_force'].items(),
                           key=lambda x: abs(x[1]), reverse=True)[:4]
        
        if top_params:
            _fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            axes = axes.ravel()
            
            forces = np.array([r.peak_force for r in results])
            
            for idx, (pname, _) in enumerate(top_params):
                if idx >= 4:
                    break
                ax = axes[idx]
                x_vals = np.array([r.params.get(pname, 0) for r in results])
                
                # 열폭주 여부로 색 구분
                colors = ['red' if r.thermal_runaway else 'blue' for r in results]
                ax.scatter(x_vals, forces, c=colors, alpha=0.6, edgecolors='k', s=30)
                ax.set_xlabel(pname)
                ax.set_ylabel('Peak Force (N)')
                ax.set_title(f'{pname} vs Peak Force')
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            out = outdir / 'scatter_top4.png'
            plt.savefig(out, dpi=150)
            plt.close()
            print(f"  [그래프] {out}")
    
    # 3. 파라미터 상관 행렬 히트맵
    if len(results) >= 5 and len(params) >= 2:
        param_names = [p.name for p in params]
        resp_names = ['peak_force', 'total_energy', 'max_temperature']
        all_names = param_names + resp_names
        
        matrix = np.zeros((len(results), len(all_names)))
        for i, r in enumerate(results):
            for j, p in enumerate(params):
                matrix[i, j] = r.params.get(p.name, p.nominal)
            matrix[i, len(params)] = r.peak_force
            matrix[i, len(params) + 1] = r.total_energy
            matrix[i, len(params) + 2] = r.max_temperature
        
        # 상관 계수
        corr = np.corrcoef(matrix.T)
        
        _fig, ax = plt.subplots(figsize=(max(8, len(all_names) * 0.8),
                                        max(6, len(all_names) * 0.6)))
        im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
        ax.set_xticks(range(len(all_names)))
        ax.set_yticks(range(len(all_names)))
        short_names = [n[:12] for n in all_names]
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=7)
        ax.set_yticklabels(short_names, fontsize=7)
        
        for i in range(len(all_names)):
            for j in range(len(all_names)):
                ax.text(j, i, f'{corr[i, j]:.2f}', ha='center', va='center',
                       fontsize=6, color='white' if abs(corr[i, j]) > 0.5 else 'black')
        
        plt.colorbar(im, ax=ax, label='Correlation')
        ax.set_title('Parameter-Response Correlation Matrix')
        plt.tight_layout()
        out = outdir / 'correlation_matrix.png'
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"  [그래프] {out}")


def export_doe_csv(results: List[DOEResult], params: List[DOEParameter],
                   outdir: Path) -> None:
    """DOE 결과 CSV 내보내기"""
    out = outdir / 'doe_results.csv'
    
    param_names = [p.name for p in params]
    header = "run_id," + ",".join(param_names) + \
             ",peak_force_N,total_energy_mJ,energy_ratio," \
             "max_temp_K,hg_ratio_pct,short_circuit_s,thermal_runaway,converged\n"
    
    with open(out, 'w', encoding='utf-8') as f:
        f.write(header)
        for r in results:
            vals = [str(r.params.get(pn, '')) for pn in param_names]
            f.write(f"{r.run_id},{','.join(vals)},"
                    f"{r.peak_force:.2f},{r.total_energy:.2f},{r.energy_ratio:.6f},"
                    f"{r.max_temperature:.1f},{r.hg_ratio:.2f},{r.short_circuit_time:.4f},"
                    f"{int(r.thermal_runaway)},{int(r.converged)}\n")
    
    print(f"  [CSV] {out}")


# ============================================================
# 실행 스크립트 생성
# ============================================================

def generate_run_scripts(base_dir: Path, n_runs: int, 
                         solver: str = "ls-dyna",
                         ncpu: int = 4,
                         main_file: str = "01_main.k") -> None:
    """LS-DYNA 일괄 실행 스크립트 생성"""
    
    # Windows batch
    bat_path = base_dir / "run_all_doe.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("REM LS-DYNA DOE 일괄 실행 스크립트\n")
        f.write(f"REM 총 {n_runs} runs\n\n")
        f.write(f"SET SOLVER={solver}\n")
        f.write(f"SET NCPU={ncpu}\n\n")
        
        for i in range(n_runs):
            run_dir = f"run_{i:04d}"
            f.write(f"echo === Run {i}/{n_runs} ===\n")
            f.write(f"cd {run_dir}\n")
            f.write(f"%SOLVER% i={main_file} ncpu=%NCPU% memory=2000m\n")
            f.write("cd ..\n\n")
    
    # Linux/PBS 제출 스크립트
    pbs_path = base_dir / "submit_all_doe.sh"
    with open(pbs_path, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n")
        f.write("# LS-DYNA DOE PBS 제출 스크립트\n")
        f.write(f"# 총 {n_runs} runs\n\n")
        
        for i in range(n_runs):
            run_dir = f"run_{i:04d}"
            f.write(f'echo "Submitting run {i}/{n_runs}"\n')
            f.write(f"cd {run_dir}\n")
            f.write(f'{solver} i={main_file} ncpu={ncpu} memory=2000m &\n')
            f.write("cd ..\n\n")
            # 동시 실행 제한 (8개씩)
            if (i + 1) % 8 == 0:
                f.write("wait  # 8개 동시 완료 대기\n\n")
        
        f.write("wait\necho 'All DOE runs completed'\n")
    
    print(f"  [스크립트] {bat_path}")
    print(f"  [스크립트] {pbs_path}")


# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="LS-DYNA 배터리 시뮬레이션 DOE 프레임워크")
    parser.add_argument("--method", choices=["lhs", "factorial", "box_behnken", "oat"],
                        default="lhs",
                        help="샘플링 메서드 (default: lhs)")
    parser.add_argument("--n", type=int, default=30,
                        help="LHS 샘플 수 (default: 30)")
    parser.add_argument("--levels", type=int, default=3,
                        help="Factorial 레벨 수 (default: 3)")
    parser.add_argument("--seed", type=int, default=42,
                        help="난수 시드")
    parser.add_argument("--srcdir", type=str, default=".",
                        help="원본 k-file 디렉토리 (default: 현재)")
    parser.add_argument("--outdir", type=str, default="./doe_runs",
                        help="DOE 실행 디렉토리 (default: ./doe_runs)")
    parser.add_argument("--config", type=str, default=None,
                        help="JSON 설정 파일 (파라미터 정의 포함)")
    parser.add_argument("--postprocess", type=str, default=None,
                        help="후처리 모드: DOE 결과 디렉토리 경로")
    parser.add_argument("--solver", type=str, default="ls-dyna",
                        help="LS-DYNA 실행 파일 경로")
    parser.add_argument("--ncpu", type=int, default=4,
                        help="CPU 수")
    parser.add_argument("--main", type=str, default="01_main.k",
                        help="메인 입력 파일")
    parser.add_argument("--params", nargs='*', default=None,
                        help="활성 파라미터 이름 (기본: 전체)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    
    args = parser.parse_args()

    log = setup_logger(
        "doe",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        _run_doe(args, log)
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as e:
        log.error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)


def _run_doe(args, log):
    
    # ========== 후처리 모드 ==========
    if args.postprocess:
        base_dir = Path(args.postprocess)
        if not base_dir.exists():
            log.error("디렉토리 없음: %s", base_dir)
            sys.exit(1)
        
        log.info("=== DOE 후처리 모드 ===")
        
        params = load_params(args)
        results = collect_doe_results(base_dir, params)
        
        if not results:
            log.error("결과 없음. doe_params.json이 있는 run_XXXX 폴더 확인")
            sys.exit(1)
        
        sensitivity = sensitivity_analysis(results, params)
        print_doe_report(results, params, sensitivity)
        
        output_dir = base_dir / "doe_analysis"
        output_dir.mkdir(exist_ok=True)
        
        export_doe_csv(results, params, output_dir)
        plot_doe_results(results, params, sensitivity, output_dir)
        
        # JSON 요약
        summary = {
            'n_runs': len(results),
            'n_converged': sum(1 for r in results if r.converged),
            'sensitivity': sensitivity,
            'response_stats': {
                'peak_force': {
                    'min': min(r.peak_force for r in results),
                    'max': max(r.peak_force for r in results),
                    'mean': float(np.mean([r.peak_force for r in results]))
                },
                'max_temperature': {
                    'min': min(r.max_temperature for r in results),
                    'max': max(r.max_temperature for r in results),
                    'mean': float(np.mean([r.max_temperature for r in results]))
                }
            }
        }
        with open(output_dir / 'doe_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        log.info("  [요약] %s", output_dir / 'doe_summary.json')
        log.info("=== 후처리 완료 ===")
        return
    
    # ========== DOE 생성 모드 ==========
    log.info("=== LS-DYNA 배터리 DOE 프레임워크 ===")
    
    params = load_params(args)
    
    log.info("  메서드: %s", args.method)
    log.info("  파라미터 (%d):", len(params))
    for p in params:
        log.info("    %s [%.3g, %.3g] (nominal=%.3g) %s",
                 p.name, p.low, p.high, p.nominal, p.units)
    
    # 샘플 생성
    if args.method == "lhs":
        samples = generate_lhs(params, args.n, args.seed)
    elif args.method == "factorial":
        samples = generate_factorial(params, args.levels)
    elif args.method == "box_behnken":
        samples = generate_box_behnken(params)
    elif args.method == "oat":
        samples = generate_one_at_a_time(params, args.levels)
    else:
        samples = generate_lhs(params, args.n, args.seed)
    
    n_runs = samples.shape[0]
    log.info("  총 Run 수: %d", n_runs)
    
    if n_runs > 1000:
        log.warning("  %d개 run — Full factorial은 파라미터 수가 적을 때만 권장", n_runs)
    
    # 디렉토리 생성
    src_dir = Path(args.srcdir)
    base_dir = Path(args.outdir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    log.info("  [DOE 디렉토리 생성]")
    for i in range(n_runs):
        _run_dir = create_run_directory(base_dir, src_dir, i, samples[i], params)
        if (i + 1) % 10 == 0 or i == n_runs - 1:
            log.info("    %d/%d runs 생성 완료", i + 1, n_runs)
    
    # 실행 스크립트 생성
    generate_run_scripts(base_dir, n_runs, args.solver, args.ncpu, args.main)
    
    # DOE 설계 매트릭스 저장
    design_matrix = {
        'method': args.method,
        'n_runs': n_runs,
        'seed': args.seed,
        'parameters': [asdict(p) for p in params],
        'samples': samples.tolist()
    }
    
    dm_path = base_dir / 'doe_design_matrix.json'
    with open(dm_path, 'w', encoding='utf-8') as f:
        json.dump(design_matrix, f, indent=2, ensure_ascii=False)
    log.info("  [설계 행렬] %s", dm_path)
    
    # CSV 설계 행렬
    csv_path = base_dir / 'doe_design_matrix.csv'
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("run_id," + ",".join(p.name for p in params) + "\n")
        for i in range(n_runs):
            f.write(f"{i}," + ",".join(f"{samples[i,j]:.6f}" for j in range(len(params))) + "\n")
    log.info("  [CSV] %s", csv_path)
    
    log.info("=== DOE 설계 완료: %d runs in %s ===", n_runs, base_dir)
    log.info("  실행: %s/run_all_doe.bat (Windows)", base_dir)
    log.info("  실행: bash %s/submit_all_doe.sh (Linux)", base_dir)
    log.info("  후처리: python doe_framework.py --postprocess %s", base_dir)


def load_params(args) -> List[DOEParameter]:
    """설정에서 파라미터 로드"""
    if args.config:
        with open(args.config, encoding='utf-8') as f:
            cfg = json.load(f)
        params = []
        for p_cfg in cfg.get('parameters', []):
            params.append(DOEParameter(**p_cfg))
        return params
    
    # 기본 파라미터 세트
    params = DEFAULT_PARAMETERS.copy()
    
    # --params로 필터링
    if args.params:
        params = [p for p in params if p.name in args.params]
        if not params:
            logger.error("유효한 파라미터 없음: %s", args.params)
            logger.error("  사용 가능: %s", [p.name for p in DEFAULT_PARAMETERS])
            sys.exit(1)
    
    return params


if __name__ == "__main__":
    main()
