"""
battery_utils 단위 테스트
=========================
공용 모듈의 상수, 유틸리티, YAML 로드/검증 테스트
"""

import io
import logging
from pathlib import Path

import pytest
import yaml

# 테스트 대상
from battery_utils import (
    LT, PID, MID, SID, PSET, LAYER_NAMES,
    tier_to_yaml_key, tier_to_suffix,
    load_config, validate_config, ConfigValidationError,
    setup_logger,
    write_kfile_header, write_separator, fmt8, fmt10,
)


# ============================================================
# Constants
# ============================================================

class TestConstants:
    """상수 클래스 값 검증"""

    def test_lt_values(self):
        assert LT.AL_CC == 1
        assert LT.CATHODE == 2
        assert LT.SEPARATOR == 3
        assert LT.ANODE == 4
        assert LT.CU_CC == 5

    def test_pid_unit_cell(self):
        """PID.unit_cell()이 올바른 PID 반환"""
        result = PID.unit_cell(0, LT.AL_CC)
        assert isinstance(result, int)
        assert result == 1000 + 0 * 10 + 1

    def test_pid_wound_layer(self):
        result = PID.wound_layer(LT.AL_CC)
        assert isinstance(result, int)
        assert result == 2001

    def test_mid_thermal_offset(self):
        assert MID.THERMAL_OFFSET == 100

    def test_sid(self):
        assert SID.SHELL_BT == 1
        assert SID.SOLID_CORE == 5

    def test_pset(self):
        assert PSET.IMPACTOR == 100
        assert PSET.ALL_ANODE == 104

    def test_layer_names(self):
        assert LAYER_NAMES[1] == "Al_CC"
        assert LAYER_NAMES[5] == "Cu_CC"
        assert len(LAYER_NAMES) == 5


# ============================================================
# tier_to_yaml_key / tier_to_suffix
# ============================================================

class TestTierConversions:

    @pytest.mark.parametrize("tier, expected", [
        (-1,  "tier_minus1"),
        (0,   "tier_0"),
        (0.5, "tier_0_5"),
        (1,   "tier_1"),
        (2,   "tier_2"),
    ])
    def test_tier_to_yaml_key(self, tier, expected):
        assert tier_to_yaml_key(tier) == expected

    @pytest.mark.parametrize("tier, expected", [
        (-1,   "_tier-1"),
        (0,    "_tier0"),
        (0.5,  "_tier0_5"),
        (1,    "_tier1"),
        (2,    "_tier2"),
    ])
    def test_tier_to_suffix(self, tier, expected):
        assert tier_to_suffix(tier) == expected


# ============================================================
# fmt8 / fmt10
# ============================================================

class TestFormatters:

    def test_fmt8_integer(self):
        result = fmt8(123)
        assert len(result) == 8

    def test_fmt8_float(self):
        result = fmt8(1.5)
        assert len(result) == 8

    def test_fmt8_string(self):
        result = fmt8("HELLO")
        assert len(result) == 8

    def test_fmt10_integer(self):
        result = fmt10(99)
        assert len(result) == 10

    def test_fmt10_float(self):
        result = fmt10(3.14159)
        assert len(result) == 10

    def test_fmt10_string(self):
        result = fmt10("TEST")
        assert len(result) == 10


# ============================================================
# load_config / validate_config
# ============================================================

class TestConfig:

    @pytest.fixture
    def minimal_yaml(self, tmp_path):
        """최소 유효 YAML — _REQUIRED_SCHEMA에 맞춤"""
        data = {
            'metadata': {'project_name': 'test', 'version': '1.0'},
            'geometry': {
                'stacked': {
                    'cell_dimensions': {'width': 100, 'height': 80},
                    'layer_thickness': {
                        'al_current_collector': 0.015,
                        'cathode_coating': 0.070,
                        'separator': 0.025,
                        'anode_coating': 0.085,
                        'cu_current_collector': 0.010,
                        'pouch': 0.100,
                        'electrolyte_buffer': 0.050,
                    },
                    'stacking': {'default_n_cells': 20, 'tier_definitions': {}},
                    'tabs': {'positive': {}, 'negative': {}},
                    'pcm': {'width': 5, 'height': 5, 'thickness': 1},
                    'fillet': {'radius': 1, 'n_segments': 4},
                },
            },
            'impactor': {'cylinder': {}},
            'materials': {
                'aluminum_cc': {}, 'copper_cc': {},
                'nmc_cathode': {}, 'graphite_anode': {},
                'separator': {}, 'pouch': {},
            },
            'mesh': {
                'stacked': {
                    'through_thickness_elements': {'cathode': 1, 'anode': 1},
                },
            },
            'em_randles': {},
            'contacts': {},
            'control': {},
            'output_files': {},
        }
        p = tmp_path / "test.yaml"
        p.write_text(yaml.dump(data, default_flow_style=False), encoding='utf-8')
        return p

    @pytest.fixture
    def real_config(self):
        """실제 battery_config.yaml 경로 (있을 때만)"""
        p = Path(__file__).parent.parent / "battery_config.yaml"
        if not p.exists():
            pytest.skip("battery_config.yaml not found")
        return p

    def test_load_config_basic(self, minimal_yaml):
        cfg = load_config(str(minimal_yaml), validate=True)
        assert 'metadata' in cfg
        assert cfg['metadata']['project_name'] == 'test'

    def test_load_config_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file_xyz.yaml")

    def test_load_config_no_validate(self, tmp_path):
        """validate=False이면 불완전한 YAML도 로드"""
        p = tmp_path / "partial.yaml"
        p.write_text(yaml.dump({'only': 'one_key'}), encoding='utf-8')
        cfg = load_config(str(p), validate=False)
        assert cfg['only'] == 'one_key'

    def test_validate_config_missing_key(self):
        with pytest.raises(ConfigValidationError):
            validate_config({'units': {}})

    def test_load_real_config(self, real_config):
        """실제 battery_config.yaml 로드 + 검증"""
        cfg = load_config(str(real_config), validate=True)
        assert 'metadata' in cfg
        assert 'materials' in cfg


# ============================================================
# setup_logger
# ============================================================

class TestLogger:

    def test_setup_logger_returns_logger(self):
        log = setup_logger("test_logger_unit")
        assert isinstance(log, logging.Logger)
        assert log.name == "test_logger_unit"

    def test_setup_logger_with_file(self, tmp_path):
        logfile = tmp_path / "test.log"
        log = setup_logger("file_logger", log_file=str(logfile))
        log.info("hello")
        # Flush handlers
        for h in log.handlers:
            h.flush()
        assert logfile.exists()


# ============================================================
# write_kfile_header / write_separator
# ============================================================

class TestKfileUtils:

    def test_write_kfile_header(self):
        buf = io.StringIO()
        write_kfile_header(buf, "Test file", description="A test description")
        text = buf.getvalue()
        assert "*KEYWORD" in text
        assert "Test file" in text

    def test_write_separator(self):
        buf = io.StringIO()
        write_separator(buf, "Section Title")
        text = buf.getvalue()
        assert "Section Title" in text


# ============================================================
# estimate_runtime 모듈
# ============================================================

class TestEstimateRuntime:

    def test_estimate_function(self):
        from estimate_runtime import estimate_runtime
        result = estimate_runtime(tier=-1, phase=1, ncpu=4, model_type="stacked")
        assert 'walltime_hours' in result
        assert result['elements'] > 0
        assert result['walltime_hours'] >= 0

    def test_estimate_unknown_tier(self):
        from estimate_runtime import estimate_runtime
        result = estimate_runtime(tier=99, phase=1, ncpu=1)
        assert 'error' in result
