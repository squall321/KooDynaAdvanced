"""
battery_utils — 배터리 시뮬레이션 공유 유틸리티 모듈
====================================================
모든 생성/후처리 스크립트가 공통으로 사용하는:
  - 상수 (Part/Material/Section/Set ID)
  - YAML 설정 로딩 + 스키마 검증
  - Tier 변환 함수
  - 로깅 설정
  - k-file 헤더/구분선 유틸리티

사용법:
    from battery_utils import (
        load_config, setup_logger, tier_to_yaml_key, tier_to_suffix,
        LT, PID, MID, SID, PSET, LAYER_NAMES,
        write_kfile_header, write_separator,
    )
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Union

import yaml


# ============================================================
# 상수 — Layer Type Codes
# ============================================================
class LT:
    """Layer type codes (단위셀 내 각 층 식별)"""
    AL_CC     = 1   # Al 집전체
    CATHODE   = 2   # NMC 양극 코팅
    SEPARATOR = 3   # PE 분리막
    ANODE     = 4   # Graphite 음극 코팅
    CU_CC     = 5   # Cu 집전체


# ============================================================
# 상수 — Part IDs
# ============================================================
class PID:
    """Part ID 체계
    
    PID 범위:
      1-9:       (예약)
      10-12:     파우치 (상면/하면/측면)
      13:        전해질 버퍼층
      20-21:     탭 (양극/음극)
      30-31:     PCM 보드 (양극/음극)
      100:       임팩터
      200:       와인딩 맨드릴 코어
      1000+:     적층별 파트 (UC_idx * 100 + layer_type)
      2000+:     와인딩 파트 (2000 + layer_type)
    """
    POUCH_TOP    = 10
    POUCH_BOTTOM = 11
    POUCH_SIDE   = 12   # stacked 측면 / wound 랩
    ELECTROLYTE  = 13   # 전해질 버퍼층
    TAB_POS      = 20   # 양극 탭
    TAB_NEG      = 21   # 음극 탭
    PCM_POS      = 30   # 양극 PCM 보드
    PCM_NEG      = 31   # 음극 PCM 보드
    IMPACTOR     = 100
    MANDREL_CORE = 200

    @staticmethod
    def unit_cell(uc_idx: int, layer_type: int) -> int:
        """적층형 단위셀 PID: UC_idx * 100 + layer_type + 1000"""
        return 1000 + uc_idx * 10 + layer_type

    @staticmethod
    def wound_layer(layer_type: int) -> int:
        """와인딩형 PID: 2000 + layer_type"""
        return 2000 + layer_type


# ============================================================
# 상수 — Material IDs
# ============================================================
class MID:
    """Material ID 체계 (구조/열/EM 공통)"""
    AL        = 1   # Al 집전체
    CU        = 2   # Cu 집전체
    NMC       = 3   # NMC 양극 코팅
    GRAPHITE  = 4   # Graphite 음극 코팅
    SEPARATOR = 5   # PE 분리막
    POUCH     = 6   # 파우치 외피
    RIGID     = 7   # 임팩터/PCM (강체)
    ELECTROLYTE = 8 # 전해질
    # 열 재료: TMID = MID + 100
    THERMAL_OFFSET = 100


# ============================================================
# 상수 — Section IDs
# ============================================================
class SID:
    """Section ID 체계"""
    SHELL_BT       = 1   # Belytschko-Tsay (Al CC)
    SHELL_FULL     = 2   # 완전적분 (분리막)
    TSHELL         = 3   # (legacy) was Thick shell, now Solid for EM compat
    SOLID_1PT      = 3   # 8-node hex solid (전극 코팅, 전해질) — EM solver 호환
    SOLID_IMPACTOR = 4   # 솔리드 (임팩터/PCM)
    TSHELL_CORE    = 5   # Thick shell (와인딩 코어/전해질)
    SOLID_CORE     = 5   # (하위호환) alias for TSHELL_CORE
    SHELL_POUCH    = 6   # 파우치 셸 (T=t_pouch)
    SHELL_CU_CC    = 7   # Cu 집전체 셸 (T=t_cu_cc)


# ============================================================
# 상수 — Part Set IDs
# ============================================================
class PSET:
    """SET_PART ID 체계"""
    IMPACTOR     = 100
    POUCH        = 101
    ALL_CELL     = 102
    ALL_CATHODE  = 103
    ALL_ANODE    = 104


# ============================================================
# 상수 — 층별 이름 매핑
# ============================================================
LAYER_NAMES: Dict[int, str] = {
    LT.AL_CC:     "Al_CC",
    LT.CATHODE:   "NMC_Cathode",
    LT.SEPARATOR: "PE_Separator",
    LT.ANODE:     "Graphite_Anode",
    LT.CU_CC:     "Cu_CC",
}


# ============================================================
# Tier 변환 함수
# ============================================================
def tier_to_yaml_key(tier: float) -> str:
    """티어 번호를 YAML 키로 변환
    
    Examples:
        -1   → 'tier_minus1'
        0    → 'tier_0'
        0.5  → 'tier_0_5'
        1    → 'tier_1'
    """
    if tier < 0:
        return f"tier_minus{abs(int(tier))}"
    elif tier % 1 == 0:
        return f"tier_{int(tier)}"
    else:
        return f"tier_{str(tier).replace('.', '_')}"


def tier_to_suffix(tier: float) -> str:
    """티어 번호를 파일명 서픽스로 변환
    
    Examples:
        -1   → '_tier-1'
        0    → '_tier0'
        0.5  → '_tier0_5'
        1    → '_tier1'
    """
    if tier < 0:
        return f"_tier-{abs(int(tier))}"
    elif tier % 1 == 0:
        return f"_tier{int(tier)}"
    else:
        return f"_tier{str(tier).replace('.', '_')}"


# ============================================================
# YAML 스키마 검증
# ============================================================
# 필수 최상위 키와 하위 구조 정의
_REQUIRED_SCHEMA: Dict[str, Any] = {
    "metadata": ["project_name", "version"],
    "geometry": {
        "stacked": {
            "cell_dimensions": ["width", "height"],
            "layer_thickness": [
                "al_current_collector",
                "cathode_coating",
                "separator",
                "anode_coating",
                "cu_current_collector",
                "pouch",
                "electrolyte_buffer",
            ],
            "stacking": ["default_n_cells", "tier_definitions"],
            "tabs": ["positive", "negative"],
            "pcm": ["width", "height", "thickness"],
            "fillet": ["radius", "n_segments"],
        },
    },
    "impactor": ["cylinder"],
    "mesh": {
        "stacked": {
            "through_thickness_elements": ["cathode", "anode"],
        },
    },
    "materials": [
        "aluminum_cc",
        "copper_cc",
        "nmc_cathode",
        "graphite_anode",
        "separator",
        "pouch",
    ],
    "em_randles": [],
    "contacts": [],
    "control": [],
    "output_files": [],
}


class ConfigValidationError(Exception):
    """YAML 설정 파일 검증 오류"""


def _validate_section(config: dict, schema: Any, path: str = "") -> List[str]:
    """재귀적으로 YAML 스키마를 검증하여 누락 키 목록을 반환"""
    errors: List[str] = []
    
    if isinstance(schema, dict):
        for key, sub_schema in schema.items():
            full_path = f"{path}.{key}" if path else key
            if key not in config:
                errors.append(f"  누락: '{full_path}'")
            elif isinstance(sub_schema, dict):
                errors.extend(_validate_section(config[key], sub_schema, full_path))
            elif isinstance(sub_schema, list) and sub_schema:
                # 리스트 → 해당 키 아래에 이 이름들이 있어야 함
                if isinstance(config[key], dict):
                    for sub_key in sub_schema:
                        if sub_key not in config[key]:
                            errors.append(f"  누락: '{full_path}.{sub_key}'")
    elif isinstance(schema, list) and schema:
        if isinstance(config, dict):
            for key in schema:
                full_path = f"{path}.{key}" if path else key
                if key not in config:
                    errors.append(f"  누락: '{full_path}'")
    
    return errors


def validate_config(config: Dict[str, Any]) -> None:
    """YAML 설정 스키마 검증. 필수 키 누락 시 ConfigValidationError 발생.
    
    Args:
        config: yaml.safe_load() 결과
    
    Raises:
        ConfigValidationError: 필수 키가 누락된 경우
    """
    if not isinstance(config, dict):
        raise ConfigValidationError("설정 파일이 유효한 YAML dict가 아닙니다")
    
    errors = _validate_section(config, _REQUIRED_SCHEMA)
    if errors:
        msg = "battery_config.yaml 검증 실패:\n" + "\n".join(errors)
        raise ConfigValidationError(msg)


# ============================================================
# YAML 설정 로딩
# ============================================================
def load_config(
    config_path: Union[str, Path] = "battery_config.yaml",
    validate: bool = True,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """YAML 설정 파일 로드 + 선택적 스키마 검증
    
    Args:
        config_path: YAML 파일 경로
        validate: True면 스키마 검증 수행
        logger: 로거 (None이면 모듈 기본 로거 사용)
    
    Returns:
        dict: 파싱된 설정 딕셔너리
    
    Raises:
        FileNotFoundError: 파일이 없는 경우
        yaml.YAMLError: YAML 파싱 실패
        ConfigValidationError: 스키마 검증 실패 (validate=True)
    """
    log = logger or logging.getLogger(__name__)
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(
            f"설정 파일을 찾을 수 없습니다: {path.resolve()}\n"
            f"  현재 디렉토리: {Path.cwd()}"
        )
    
    log.info("설정 파일 로드: %s", path)
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML 파싱 실패: {path}\n  {e}") from e
    
    if validate:
        validate_config(config)
        log.debug("설정 스키마 검증 통과")
    
    return config


# ============================================================
# 로깅 설정
# ============================================================
def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    fmt: str = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt: str = "%H:%M:%S",
) -> logging.Logger:
    """표준화된 로거 생성
    
    Args:
        name: 로거 이름 (보통 스크립트 이름)
        level: 로그 레벨 (기본: INFO)
        log_file: 파일 로그 경로 (None이면 콘솔만)
        fmt: 로그 포맷
        datefmt: 시간 포맷
    
    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)
    
    # 중복 핸들러 방지
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    formatter = logging.Formatter(fmt, datefmt=datefmt)
    
    # 콘솔 핸들러
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # 파일 핸들러 (선택)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger


# ============================================================
# k-file 작성 유틸리티
# ============================================================
def write_kfile_header(f: TextIO, title: str, description: str = "") -> None:
    """k-file 표준 헤더 작성
    
    Args:
        f: 파일 핸들
        title: TITLE 카드에 쓸 제목
        description: 추가 설명 주석(선택)
    """
    f.write("*KEYWORD\n")
    f.write("*TITLE\n")
    f.write(f"{title}\n")
    if description:
        for line in description.strip().split("\n"):
            f.write(f"$ {line}\n")
    f.write("$\n")


def write_separator(f: TextIO, text: str, char: str = "=", width: int = 60) -> None:
    """k-file 내 구분선 주석 작성"""
    f.write(f"$\n$ {char * width}\n$ {text}\n$ {char * width}\n$\n")


def fmt8(value: Any) -> str:
    """LS-DYNA 8칸 고정폭 필드 포맷팅
    
    Args:
        value: 숫자나 문자열
    
    Returns:
        8자 오른쪽 정렬 문자열
    """
    if isinstance(value, float):
        s = f"{value:8g}"
        if len(s) > 8:
            s = f"{value:.3E}"[:8]
    elif isinstance(value, int):
        s = f"{value:>8d}"
    else:
        s = f"{str(value):>8s}"
    return f"{s:>8s}"


def fmt10(value: Any) -> str:
    """LS-DYNA 10칸 고정폭 필드 포맷팅"""
    if isinstance(value, float):
        s = f"{value:10g}"
        if len(s) > 10:
            s = f"{value:.4E}"[:10]
    elif isinstance(value, int):
        s = f"{value:>10d}"
    else:
        s = f"{str(value):>10s}"
    return f"{s:>10s}"


def fmt16(value: float) -> str:
    """LS-DYNA 16칸 고정폭 필드 (커브 데이터 등)"""
    s = f"{value:16g}"
    if len(s) > 16:
        s = f"{value:.6E}"[:16]
    return f"{s:>16s}"


def write_curve(f: TextIO, lcid: int, title: str, xy_data: List[tuple],
                sfa: float = 1.0, sfo: float = 1.0) -> None:
    """DEFINE_CURVE_TITLE 블록 출력

    Args:
        f: 파일 핸들
        lcid: 로드커브 ID
        title: 커브 제목
        xy_data: [(x, y), ...] 데이터 쌍
        sfa, sfo: 스케일 팩터
    """
    f.write("*DEFINE_CURVE_TITLE\n")
    f.write(f"{title}\n")
    f.write("$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP\n")
    f.write(f"{lcid:>10d}         0{sfa:>10g}{sfo:>10g}       0.0       0.0         0\n")
    for x, y in xy_data:
        f.write(f"{fmt16(x)}{fmt16(y)}\n")


# ============================================================
# 용량 → 적층 수 자동 계산
# ============================================================
def calculate_n_cells(
    capacity_ah: float,
    width_mm: float,
    height_mm: float,
    areal_capacity_mah_cm2: float = 3.5,
) -> int:
    """셀 용량 + 외곽 치수로 필요한 단위셀(양면 전극 쌍) 수 계산.

    공식: n = Q_total / (q_areal × A_electrode × 2)
      - 양면 코팅(double-sided) 전극 1쌍 = 2배 면적 기여
      - q_areal: 전극 면적당 용량 (mAh/cm²), NMC622 표준 ≈ 3.0-4.0

    Args:
        capacity_ah: 셀 공칭 용량 (Ah)
        width_mm: 전극 가로 길이 (mm)
        height_mm: 전극 세로 길이 (mm)
        areal_capacity_mah_cm2: 전극 면적당 용량 (mAh/cm², 기본 3.5)

    Returns:
        단위셀 수 (정수, 최소 1)
    """
    area_cm2 = (width_mm / 10.0) * (height_mm / 10.0)
    cap_per_uc_mah = areal_capacity_mah_cm2 * area_cm2 * 2.0  # 양면
    n = capacity_ah * 1000.0 / cap_per_uc_mah
    return max(1, round(n))


def get_geometry(config: Dict[str, Any], model_type: str = "stacked") -> Dict[str, Any]:
    """YAML config에서 기하 정보 추출 + 단위셀 두께 자동 계산.

    Returns:
        dict with keys: width, height, layer_thickness (dict),
        unit_cell_thickness, n_cells_default, tier_definitions, ...
    """
    geo = config["geometry"][model_type]
    dim = geo["cell_dimensions"]
    lt = geo["layer_thickness"]

    t_al = lt["al_current_collector"]
    if isinstance(t_al, dict):
        t_al = t_al["value"]
    t_cath = lt["cathode_coating"]
    if isinstance(t_cath, dict):
        t_cath = t_cath["value"]
    t_sep = lt["separator"]
    if isinstance(t_sep, dict):
        t_sep = t_sep["value"]
    t_an = lt["anode_coating"]
    if isinstance(t_an, dict):
        t_an = t_an["value"]
    t_cu = lt["cu_current_collector"]
    if isinstance(t_cu, dict):
        t_cu = t_cu["value"]
    t_pouch = lt["pouch"]
    if isinstance(t_pouch, dict):
        t_pouch = t_pouch["value"]
    t_ebuf = lt.get("electrolyte_buffer", 0.2)
    if isinstance(t_ebuf, dict):
        t_ebuf = t_ebuf.get("value", 0.2)

    uc_t = t_al + 2 * t_cath + t_sep + 2 * t_an + t_cu

    # stacking / winding
    if model_type == "stacked":
        stk = geo.get("stacking", {})
        n_default = stk.get("default_n_cells", 15)
        tier_defs = stk.get("tier_definitions", {})
    else:
        wnd = geo.get("winding", {})
        n_default = wnd.get("default_n_windings", 15)
        tier_defs = wnd.get("tier_definitions", {})

    return {
        "width": dim["width"],
        "height": dim["height"],
        "t_al": t_al,
        "t_cathode": t_cath,
        "t_separator": t_sep,
        "t_anode": t_an,
        "t_cu": t_cu,
        "t_pouch": t_pouch,
        "t_electrolyte_buffer": t_ebuf,
        "unit_cell_thickness": uc_t,
        "n_cells_default": n_default,
        "tier_definitions": tier_defs,
    }


def get_n_cells_for_tier(config: Dict[str, Any], tier: float,
                         model_type: str = "stacked") -> int:
    """주어진 tier에 대한 단위셀 수 반환."""
    geo = get_geometry(config, model_type)
    key = tier_to_yaml_key(tier)
    td = geo["tier_definitions"]
    if key in td:
        val = td[key]
        if isinstance(val, dict):
            return val.get("n_cells", geo["n_cells_default"])
        return int(val)
    return geo["n_cells_default"]


def get_scenario_params(config: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """시나리오 파라미터를 YAML config에서 추출. 누락 시 기본값 적용.

    Args:
        config: yaml.safe_load() 결과
        scenario: 'impact' | 'swelling' | 'gas'

    Returns:
        시나리오별 파라미터 dict
    """
    if scenario == "impact":
        return {}  # impact는 기존 phase 1/2/3 메커니즘 그대로

    params = config.get("scenarios", {}).get(scenario, {})
    if params:
        return params

    # YAML 섹션 없을 때 기본값 반환
    if scenario == "swelling":
        return {
            "n_cycles": 2,
            "c_rate_charge": 0.5,
            "c_rate_discharge": 1.0,
            "cv_cutoff_voltage": 4.2,
            "cv_cutoff_current_frac": 0.05,
            "intercalation": {"graphite_cte": 0.035, "nmc_cte": 0.015},
            "sei_growth": {
                "pre_exponential": 1.5e-6,
                "activation_energy": 40000,
                "initial_thickness": 5.0e-9,
                "max_thickness": 50.0e-9,
            },
            "end_time": 7200.0,
        }
    if scenario == "gas":
        return {
            "heat_source": {
                "type": "external",
                "heat_flux_density": 5000.0,
                "ramp_time": 60.0,
                "plateau_time": 3600.0,
            },
            "gas_generation": {
                "onset_temperature": 373.0,
                "activation_energy": 80000,
                "pre_exponential": 1.0e12,
            },
            "end_time": 3600.0,
        }
    return {}


# ============================================================
# 공통 argparse 인자 추가
# ============================================================
def add_common_args(parser: "argparse.ArgumentParser") -> None:
    """모든 생성 스크립트에 공통인 argparse 인자 추가
    
    추가되는 인자:
        --config: YAML 설정 파일 경로
        --tier: 티어 번호
        --output: 출력 파일 경로
        --verbose / -v: 상세 로그
        --log-file: 파일 로그 경로
    """
    parser.add_argument(
        "--config", type=str, default="battery_config.yaml",
        help="YAML 설정 파일 경로 (기본: battery_config.yaml)",
    )
    parser.add_argument(
        "--tier", type=float, default=0,
        help="티어 번호 (-1, 0, 0.5, 1, 2, 기본: 0)",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="출력 파일 경로 (기본: 자동 결정)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="상세 로그 출력 (DEBUG 레벨)",
    )
    parser.add_argument(
        "--log-file", type=str, default=None,
        help="로그를 파일로도 저장",
    )


# ============================================================
# 모듈 정보
# ============================================================
__version__ = "1.0.0"
__all__ = [
    # 상수
    "LT", "PID", "MID", "SID", "PSET", "LAYER_NAMES",
    # 함수
    "tier_to_yaml_key", "tier_to_suffix",
    "load_config", "validate_config", "ConfigValidationError",
    "setup_logger", "add_common_args",
    "write_kfile_header", "write_separator", "fmt8", "fmt10", "fmt16",
    "write_curve",
    "calculate_n_cells", "get_geometry", "get_n_cells_for_tier",
    "get_scenario_params",
]
