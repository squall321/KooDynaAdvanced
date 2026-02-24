"""
리튬이온 파우치 배터리 셀 — 납작 와인딩형(Flat Wound / Jellyroll) 메시 생성기
=============================================================================
LS-DYNA R16 k-file 노드/요소/파트/세트 자동 생성

실제 스마트폰 파우치 배터리의 납작 젤리롤 구조:
  - 단면: 레이스트랙(stadium) 형상 = 직선부 + 반원부
  - 경로: 아르키메데스 나선(Archimedean spiral) — 점점 감기는 연속 와인딩
  - 적층: [Al CC → NMC양극 → PE분리막 → Graphite음극 → Cu CC] 연속 감김

요소 타입:
  - 집전체, 분리막: Shell (두께 → 섹션 정의)
  - 전극 코팅 (NMC, Graphite): Solid (두께 방향 1~2 요소)
  - 파우치 외피: Shell

단위: mm, ton(1e3 kg), s, N, MPa, mJ

좌표계:
  - X: 셀 폭 방향 (직선부 길이 방향)
  - Y: 셀 높이 방향 (와인딩 축 방향)
  - Z: 셀 두께 방향 (와인딩 반경 방향)
"""

import numpy as np
import os
import sys
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, TextIO, Dict, Any
import shutil

from battery_utils import (
    LT as _LT, PID as _PID, MID as _MID, SID as _SID,
    LAYER_NAMES, tier_to_yaml_key, tier_to_suffix,
    load_config, setup_logger, add_common_args,
)

logger = logging.getLogger(__name__)


# ============================================================
# 설계 파라미터
# ============================================================
@dataclass
class FlatWoundDesign:
    """납작 와인딩 젤리롤 설계변수"""
    # 전체 외형 치수 (mm) — 파우치 내부 공간
    cell_width: float = 60.0     # X 방향 (직선부 + 반원부 양쪽)
    cell_height: float = 130.0   # Y 방향 (와인딩 축 = 전극 폭)

    # 층 두께 (mm) — 실제 µm 단위를 mm 변환
    t_al_cc: float = 0.012       # Al 집전체 12µm
    t_cathode: float = 0.065     # NMC 양극 코팅 65µm
    t_separator: float = 0.020   # PE 분리막 20µm
    t_anode: float = 0.070       # Graphite 음극 코팅 70µm
    t_cu_cc: float = 0.008       # Cu 집전체 8µm
    t_pouch: float = 0.153       # 파우치 외피 153µm

    # 와인딩 설계
    n_winds: int = 15            # 와인딩 감김 수 (= 단위셀 수)
    r_mandrel: float = 1.5       # 내부 맨드릴(심) 반경 (mm)

    # 메시 크기
    mesh_size_y: float = 2.5     # 축방향(Y) 요소 크기 (mm)
    mesh_size_path: float = 2.0  # 경로방향(XZ) 요소 크기 목표 (mm)
                                  # 직선부와 반원부 모두 이 간격 기준

    # 전극 코팅 두께 방향 요소 수
    n_elem_cathode_thick: int = 1
    n_elem_anode_thick: int = 1

    # 전해질 버퍼 (파우치↔젤리롤 사이)
    t_electrolyte_buffer: float = 0.2  # 전해질 층 두께 (mm)

    # 임팩터
    impactor_radius: float = 7.5      # 원통 반경 (mm)
    impactor_length: float = 80.0     # 원통 길이, Y방향 (mm)
    impactor_offset: float = 1.0      # 셀 외면과 임팩터 간 간극 (mm)
    impactor_n_circ: int = 24         # 원주 방향 요소 수
    impactor_n_radial: int = 4        # 반경 방향 요소 층 수

    # B12: 네일 관통 옵션
    impactor_type: str = "cylinder"    # "cylinder" 또는 "nail"
    nail_tip_length: float = 3.0       # 네일 원추부 길이 (mm)
    nail_tip_radius: float = 0.5       # 네일 팁 반경 (mm)
    nail_shaft_radius: float = 1.5     # 네일 축부 반경 (mm)

    # 탭 치수 (양극/음극 모두 상단 +Y 방향)
    tab_width: float = 10.0            # 탭 폭 (X방향, mm)
    tab_height: float = 8.0            # 탭 돌출 높이 (Y방향, mm)
    tab_pos_x_center: float = 15.0     # 양극(Al) 탭 X 중심 (mm)
    tab_neg_x_center: float = 45.0     # 음극(Cu) 탭 X 중심 (mm)

    # PCM (보호회로모듈)
    pcm_height: float = 3.0            # PCM 보드 돌출 높이 (Y방향, mm)
    pcm_thickness: float = 1.0         # PCM 보드 두께 (Z방향, mm)

    # 내부 코어 처리 (맨드릴 제거 후 빈 공간)
    core_fill: str = "electrolyte"      # "electrolyte" (전해질 충전) 또는 "void" (빈 공간)

    @property
    def unit_cell_thickness(self) -> float:
        """한 바퀴 감길 때 반경 증가량 (편면 코팅 기준)
        와인딩 구조: Al CC | cathode | separator | anode | Cu CC
        각 전극 코팅은 편면만 (양면 코팅은 적층형에서만)"""
        return (self.t_al_cc
                + self.t_cathode     # 편면
                + self.t_separator
                + self.t_anode       # 편면
                + self.t_cu_cc)

    @property
    def straight_length(self) -> float:
        """레이스트랙 직선부 길이 (반원 중심 간 거리)
        cell_width = straight_length + 2 × 최외곽 반경"""
        # 최외곽 = 마지막 와인딩의 마지막 층(Cu CC) 바깥면
        r_outer = (self.r_mandrel
                   + self.unit_cell_thickness * (self.n_winds + 1))
        return max(0.0, self.cell_width - 2.0 * r_outer)

    @property
    def total_jellyroll_thickness(self) -> float:
        """젤리롤 전체 두께 (Z방향, 양쪽 반원 + 직선부 합산)"""
        return 2.0 * (self.r_mandrel + self.unit_cell_thickness * self.n_winds)

    @property
    def n_y(self) -> int:
        return int(round(self.cell_height / self.mesh_size_y))

    @property
    def n_arc_seg(self) -> int:
        """반원부 분할 수 — 외곽 반경 기준 목표 호 길이"""
        r_outer = (self.r_mandrel
                   + self.unit_cell_thickness * (self.n_winds + 1))
        arc_len = np.pi * r_outer  # 최외곽 반원 호 길이
        return max(6, int(round(arc_len / self.mesh_size_path)))

    @property
    def n_straight_seg(self) -> int:
        """직선부 분할 수 — 경로 방향 목표 간격 기준"""
        L = self.straight_length
        if L < 1e-6:
            return 0
        return max(2, int(round(L / self.mesh_size_path)))

    @property
    def n_path(self) -> int:
        """와인딩 경로 분할 수 (레이스트랙 한 바퀴)"""
        return 2 * self.n_arc_seg + 2 * self.n_straight_seg

    @classmethod
    def from_yaml(cls, config: Dict[str, Any], tier: int = 0, mesh_size_y: float = None, mesh_size_path: float = None) -> 'FlatWoundDesign':
        """YAML 설정에서 FlatWoundDesign 인스턴스 생성
        
        Args:
            config: battery_config.yaml 파싱 결과
            tier: 티어 (-1, 0, 0.5, 1, 2)
            mesh_size_y: 축방향 메시 크기 오버라이드 (None이면 tier 기반 자동)
            mesh_size_path: 경로방향 메시 크기 오버라이드
        """
        geom = config['geometry']['wound']
        imp = config['impactor']
        
        # 티어별 와인딩 수
        tier_map = geom['winding']['tier_definitions']
        tier_key = tier_to_yaml_key(tier)
        n_winds = tier_map.get(tier_key, geom['winding']['default_n_windings'])
        
        # 티어별 메시 크기 (오버라이드 없으면 자동)
        if mesh_size_y is None:
            if tier <= -1:
                mesh_size_y = 5.0
            elif tier == 0:
                mesh_size_y = 2.5
            else:
                mesh_size_y = 1.0
        
        if mesh_size_path is None:
            mesh_size_path = mesh_size_y * 0.8  # 경로방향은 축방향보다 약간 작게
        
        # 기하
        cell_dim = geom['cell_dimensions']
        lt = geom['layer_thickness']
        
        # 임팩터
        imp_type = config.get('impactor_type', 'cylinder')
        if imp_type == 'nail' and 'nail' in imp:
            imp_data = imp['nail']
            impactor_type = 'nail'
            impactor_radius = imp_data['shaft_radius']
            nail_tip_length = imp_data['tip_length']
            nail_tip_radius = imp_data['tip_radius']
            nail_shaft_radius = imp_data['shaft_radius']
        else:
            imp_data = imp['cylinder']
            impactor_type = 'cylinder'
            impactor_radius = imp_data['radius']
            nail_tip_length = 3.0
            nail_tip_radius = 0.5
            nail_shaft_radius = 1.5
        
        # 탭/PCM 설정
        tabs_cfg = geom.get('tabs', {})
        tabs_pos = tabs_cfg.get('positive', {})
        tabs_neg = tabs_cfg.get('negative', {})
        pcm_cfg = config.get('geometry', {}).get('stacked', {}).get('pcm',
                  geom.get('pcm', {}))  # wound에 없으면 stacked 꺼 사용
        if not pcm_cfg:
            pcm_cfg = {}
        
        return cls(
            cell_width=cell_dim['width'],
            cell_height=cell_dim['height'],
            t_al_cc=lt['al_current_collector'],
            t_cathode=lt['cathode_coating'],
            t_separator=lt['separator'],
            t_anode=lt['anode_coating'],
            t_cu_cc=lt['cu_current_collector'],
            t_pouch=lt['pouch'],
            t_electrolyte_buffer=geom.get('electrolyte_buffer', 0.2),
            n_winds=n_winds,
            r_mandrel=geom['winding']['mandrel_radius'],
            mesh_size_y=mesh_size_y,
            mesh_size_path=mesh_size_path,
            n_elem_cathode_thick=config['mesh']['wound']['through_thickness_elements']['cathode'],
            n_elem_anode_thick=config['mesh']['wound']['through_thickness_elements']['anode'],
            impactor_type=impactor_type,
            impactor_radius=impactor_radius,
            impactor_length=imp_data.get('length', imp_data.get('shaft_length', 80.0)),
            impactor_offset=imp_data['offset'],
            impactor_n_circ=imp_data['mesh']['n_circumferential'],
            impactor_n_radial=imp_data['mesh']['n_radial'],
            nail_tip_length=nail_tip_length,
            nail_tip_radius=nail_tip_radius,
            nail_shaft_radius=nail_shaft_radius,
            tab_width=tabs_pos.get('width', 10.0),
            tab_height=tabs_pos.get('height', 8.0),
            tab_pos_x_center=cell_dim['width'] * 0.25,
            tab_neg_x_center=cell_dim['width'] * 0.75,
            pcm_height=pcm_cfg.get('height', 3.0),
            pcm_thickness=pcm_cfg.get('thickness', 1.0),
            core_fill=geom.get('winding', {}).get('core_fill', 'electrolyte'),
        )


# ============================================================
# Part ID 체계 (적층형과 동일 패턴)
# ============================================================
# 상수 — battery_utils에서 가져온 호환 별칭
LT_AL_CC     = _LT.AL_CC
LT_CATHODE   = _LT.CATHODE
LT_SEPARATOR = _LT.SEPARATOR
LT_ANODE     = _LT.ANODE
LT_CU_CC     = _LT.CU_CC

PID_POUCH_TOP    = _PID.POUCH_TOP
PID_POUCH_BOTTOM = _PID.POUCH_BOTTOM
PID_POUCH_WRAP   = _PID.POUCH_SIDE   # 레이스트랙 형상 파우치 보디 (= POUCH_SIDE)
PID_ELECTROLYTE_FILL = _PID.ELECTROLYTE
PID_IMPACTOR     = _PID.IMPACTOR
PID_MANDREL_CORE = _PID.MANDREL_CORE
PID_TAB_POS      = _PID.TAB_POS
PID_TAB_NEG      = _PID.TAB_NEG
PID_PCM_POS      = _PID.PCM_POS
PID_PCM_NEG      = _PID.PCM_NEG

MID_AL       = _MID.AL
MID_CU       = _MID.CU
MID_NMC      = _MID.NMC
MID_GRAPHITE = _MID.GRAPHITE
MID_SEPARATOR = _MID.SEPARATOR
MID_POUCH    = _MID.POUCH
MID_RIGID    = _MID.RIGID
MID_ELECTROLYTE = _MID.ELECTROLYTE

SID_SHELL_BT    = _SID.SHELL_BT
SID_SHELL_FULL  = _SID.SHELL_FULL
SID_SOLID_1PT   = _SID.SOLID_1PT
SID_SOLID_IMPACTOR = _SID.SOLID_IMPACTOR
SID_SOLID_CORE  = _SID.SOLID_CORE
SID_SHELL_POUCH = _SID.SHELL_POUCH
SID_SHELL_CU_CC = _SID.SHELL_CU_CC

# LAYER_NAMES — battery_utils에서 import 완료


# ============================================================
# 레이스트랙 경로 계산
# ============================================================
class RacetrackPath:
    """레이스트랙(stadium) 형상의 아르키메데스 나선 경로 생성

    XZ 평면 단면 (시계방향 순회):

              Seg 1: 상부 직선 (좌 → 우)
              ┌──────────────────┐
        Seg 4 │                  │ Seg 2
        좌측  │  L_center  L_cen │ 우측
        반원  │  (cx-L/2)  (cx+L/2) │ 반원
        (하→상)╰──────────────────╯ (상→하)
              Seg 3: 하부 직선 (우 → 좌)

    반원 중심: (cx ± L/2, 0)
    반경 R = r_mandrel + offset (법선방향 오프셋)
    상부 직선: z = +R,  하부 직선: z = -R
    """

    def __init__(self, design: FlatWoundDesign):
        self.d = design

    def get_racetrack_point(self, s: float, offset: float) -> Tuple[float, float]:
        """레이스트랙 경로 위의 점

        Args:
            s: 경로 매개변수 [0, 1) — 한 바퀴 기준
            offset: r_mandrel에 더해지는 반경 오프셋 (양=바깥)

        Returns:
            (x, z) 좌표

        세그먼트 비율은 노드 분할 수 기반 (일정한 요소 배분):
            Seg 1: 상부 직선  f_str = n_str / n_path
            Seg 2: 우측 반원  f_arc = n_arc / n_path
            Seg 3: 하부 직선  f_str
            Seg 4: 좌측 반원  f_arc
        """
        d = self.d
        L = d.straight_length
        half_L = L / 2.0
        R = d.r_mandrel + offset   # 유효 반경
        cx = d.cell_width / 2.0

        n_path = d.n_path
        n_arc = d.n_arc_seg
        n_str = d.n_straight_seg

        if n_path == 0:
            return (cx, 0.0)

        f_str = n_str / n_path if n_str > 0 else 0.0
        f_arc = n_arc / n_path

        # 세그먼트 경계
        b1 = f_str                     # 상부 직선 끝
        b2 = f_str + f_arc             # 우측 반원 끝
        b3 = 2 * f_str + f_arc         # 하부 직선 끝
        # b4 = 1.0                     # 좌측 반원 끝

        if f_str > 0 and s < b1:
            # ── Seg 1: 상부 직선 (좌 → 우) ──
            t = s / f_str
            x = (cx - half_L) + t * L
            z = R

        elif s < b2:
            # ── Seg 2: 우측 반원 (상 → 하) ──
            # θ: π/2 → −π/2  (시계방향, 우측 돌이)
            t = (s - b1) / f_arc if f_arc > 0 else 0.5
            theta = 0.5 * np.pi * (1.0 - 2.0 * t)
            x = (cx + half_L) + R * np.cos(theta)
            z = R * np.sin(theta)

        elif f_str > 0 and s < b3:
            # ── Seg 3: 하부 직선 (우 → 좌) ──
            t = (s - b2) / f_str
            x = (cx + half_L) - t * L
            z = -R

        else:
            # ── Seg 4: 좌측 반원 (하 → 상) ──
            # θ: −π/2 → −3π/2 (= π/2)  (시계방향, 좌측 돌이)
            t = (s - b3) / f_arc if f_arc > 0 else 0.5
            theta = -0.5 * np.pi - np.pi * t
            x = (cx - half_L) + R * np.cos(theta)
            z = R * np.sin(theta)

        return (x, z)


# ============================================================
# 메시 생성기
# ============================================================
class FlatWoundMeshGenerator:
    """납작 와인딩형 젤리롤 메시 생성기 (아르키메데스 나선)"""

    def __init__(self, design: FlatWoundDesign):
        self.d = design
        self.path = RacetrackPath(design)
        self.next_nid = 1
        self.next_eid = 1

        self._f_nodes = None
        self._f_shells = None
        self._f_solids = None

        self.part_ids = []
        self.node_sets = {}
        self.part_sets = {}
        self.total_nodes = 0
        self.total_shells = 0
        self.total_solids = 0
        self._bottom_cap_perimeter: list = []
        self._al_cc_grid: np.ndarray = None   # Al CC 나선 노드 그리드
        self._cu_cc_grid: np.ndarray = None   # Cu CC 나선 노드 그리드

    # ── 노드/요소 스트리밍 ──

    def _add_node_xyz(self, x: float, y: float, z: float) -> int:
        """직교좌표 노드 추가"""
        nid = self.next_nid
        self._f_nodes.write(
            f"{nid:>8d}{x:>16.6f}{y:>16.6f}{z:>16.6f}       0       0\n")
        self.next_nid += 1
        self.total_nodes += 1
        return nid

    def _add_shell(self, pid: int, n1: int, n2: int, n3: int, n4: int) -> int:
        eid = self.next_eid
        self._f_shells.write(
            f"{eid:>8d}{pid:>8d}{n1:>8d}{n2:>8d}{n3:>8d}{n4:>8d}\n")
        self.next_eid += 1
        self.total_shells += 1
        return eid

    def _add_solid(self, pid: int, ns: tuple) -> int:
        eid = self.next_eid
        self._f_solids.write(
            f"{eid:>8d}{pid:>8d}"
            f"{ns[0]:>8d}{ns[1]:>8d}{ns[2]:>8d}{ns[3]:>8d}"
            f"{ns[4]:>8d}{ns[5]:>8d}{ns[6]:>8d}{ns[7]:>8d}\n")
        self.next_eid += 1
        self.total_solids += 1
        return eid

    # ── 레이스트랙 나선 경로 위 노드 스트립 생성 ──

    def _create_strip_nodes(self, offset: float, s_values: np.ndarray
                            ) -> np.ndarray:
        """나선 경로 위 한 줄의 노드 스트립 생성

        Args:
            offset: 법선 방향 오프셋 (내→외)
            s_values: 경로 매개변수 배열 (n_path_total+1,)

        Returns:
            nid_grid (n_y+1, n_s) — Y축 × 경로
        """
        d = self.d
        n_y = d.n_y
        dy = d.cell_height / n_y

        n_s = len(s_values)
        nid_grid = np.zeros((n_y + 1, n_s), dtype=np.int64)

        for js in range(n_s):
            s = s_values[js]
            # 나선 경로: 매개변수 s는 [0, n_winds) 범위
            # 한 바퀴 = 1.0, offset은 s에 비례하여 증가
            wind_idx = s  # 연속 와인딩 인덱스
            spiral_offset = offset + wind_idx * d.unit_cell_thickness
            s_local = s % 1.0  # 한 바퀴 내 위치

            x, z = self.path.get_racetrack_point(s_local, spiral_offset)

            for jy in range(n_y + 1):
                y = jy * dy
                nid_grid[jy, js] = self._add_node_xyz(x, y, z)

        return nid_grid

    # ── 셸 레이어 (나선 경로 위) ──

    def _create_spiral_shell_layer(self, pid: int, offset: float,
                                   s_values: np.ndarray
                                   ) -> np.ndarray:
        """나선 경로 위에 셸 레이어 생성

        Returns: nid_grid (n_y+1, n_s)
        """
        nid_grid = self._create_strip_nodes(offset, s_values)
        n_y = self.d.n_y
        n_s = len(s_values)

        for js in range(n_s - 1):
            for jy in range(n_y):
                n1 = nid_grid[jy, js]
                n2 = nid_grid[jy, js + 1]
                n3 = nid_grid[jy + 1, js + 1]
                n4 = nid_grid[jy + 1, js]
                self._add_shell(pid, n1, n2, n3, n4)

        if pid not in self.part_ids:
            self.part_ids.append(pid)

        return nid_grid

    # ── 솔리드 레이어 (두 스트립 사이) ──

    def _create_solid_between_strips(self, pid: int,
                                     inner_grid: np.ndarray,
                                     outer_grid: np.ndarray):
        """두 노드 스트립 사이 솔리드 요소 생성"""
        n_y = self.d.n_y
        n_s = inner_grid.shape[1]

        for js in range(n_s - 1):
            for jy in range(n_y):
                # inner face
                n1 = inner_grid[jy, js]
                n2 = inner_grid[jy, js + 1]
                n3 = inner_grid[jy + 1, js + 1]
                n4 = inner_grid[jy + 1, js]
                # outer face
                n5 = outer_grid[jy, js]
                n6 = outer_grid[jy, js + 1]
                n7 = outer_grid[jy + 1, js + 1]
                n8 = outer_grid[jy + 1, js]
                self._add_solid(pid, (n1, n2, n3, n4, n5, n6, n7, n8))

        if pid not in self.part_ids:
            self.part_ids.append(pid)

    # ── 솔리드 코팅 (다중 두께) ──

    def _create_spiral_solid_coating(self, pid: int,
                                     offset_inner: float,
                                     offset_outer: float,
                                     n_thick: int,
                                     s_values: np.ndarray,
                                     inner_grid: np.ndarray = None
                                     ) -> Tuple[np.ndarray, np.ndarray]:
        """나선 경로 위 솔리드 코팅 (두께 방향 n_thick 요소)

        Returns: (inner_grid, outer_grid)
        """
        d_offset = (offset_outer - offset_inner) / n_thick

        if inner_grid is None:
            inner_grid = self._create_strip_nodes(offset_inner, s_values)

        current_inner = inner_grid
        for k in range(n_thick):
            off_next = offset_inner + (k + 1) * d_offset
            outer = self._create_strip_nodes(off_next, s_values)
            self._create_solid_between_strips(pid, current_inner, outer)
            current_inner = outer

        if pid not in self.part_ids:
            self.part_ids.append(pid)

        return inner_grid, current_inner

    # ── 경로 매개변수 생성 ──

    def _make_s_values(self) -> np.ndarray:
        """전체 나선 경로의 s 매개변수 배열 생성

        s ∈ [0, n_winds) — 한 바퀴=1.0, s가 증가하면 반경도 증가
        분할: 한 바퀴당 n_path 세그먼트
        """
        d = self.d
        n_per_wind = d.n_path
        n_total = n_per_wind * d.n_winds  # 전체 세그먼트 수
        # s 값: 0, 1/n_per_wind, 2/n_per_wind, ..., n_winds
        s_values = np.linspace(0, d.n_winds, n_total + 1)
        return s_values

    # ── 전체 젤리롤 빌드 ──

    def build_wound_cell(self):
        """전체 납작 와인딩 젤리롤 메시 생성

        각 층의 법선 방향 오프셋:
          offset = 0 → 맨드릴 표면
          한 바퀴 감길 때마다 unit_cell_thickness 만큼 증가 (s_values로 자동)

        따라서 모든 레이어는 offset ∈ [0, unit_cell_thickness) 범위에서 정의하고,
        나선 증가분은 _create_strip_nodes 내부에서 자동 처리됨.
        """
        d = self.d

        s_values = self._make_s_values()
        print(f"  경로 세그먼트: {len(s_values)-1} (한 바퀴당 {d.n_path})")

        # 누적 오프셋 추적
        off = 0.0

        separator_pids = []
        al_cc_pids = []
        cu_cc_pids = []
        cathode_pids = []
        anode_pids = []

        # --- 각 단위셀 층을 순서대로 감는다 ---
        # 단위셀 구조: Al CC → cathode(양면) → separator → anode(양면) → Cu CC
        # 모든 와인딩이 하나의 연속 나선이므로 PID를 층별로 분류

        # 1) Al 집전체 (Shell)
        pid_al = 2000 + LT_AL_CC
        print(f"  [Layer] Al CC (Shell), offset={off:.4f}")
        self._al_cc_grid = self._create_spiral_shell_layer(pid_al, off, s_values)
        al_cc_pids.append(pid_al)
        off += d.t_al_cc

        # 2) NMC 양극 코팅 (Solid)
        pid_cath = 2000 + LT_CATHODE
        off_cath_top = off + d.t_cathode
        print(f"  [Layer] Cathode (Solid), offset={off:.4f}~{off_cath_top:.4f}")
        _, _cath_top_grid = self._create_spiral_solid_coating(
            pid_cath, off, off_cath_top, d.n_elem_cathode_thick, s_values)
        cathode_pids.append(pid_cath)
        off = off_cath_top

        # 3) PE 분리막 (Shell)
        pid_sep = 2000 + LT_SEPARATOR
        print(f"  [Layer] Separator (Shell), offset={off:.4f}")
        self._create_spiral_shell_layer(pid_sep, off, s_values)
        separator_pids.append(pid_sep)
        off += d.t_separator

        # 4) Graphite 음극 코팅 (Solid)
        pid_an = 2000 + LT_ANODE
        off_an_top = off + d.t_anode
        print(f"  [Layer] Anode (Solid), offset={off:.4f}~{off_an_top:.4f}")
        _, _an_top_grid = self._create_spiral_solid_coating(
            pid_an, off, off_an_top, d.n_elem_anode_thick, s_values)
        anode_pids.append(pid_an)
        off = off_an_top

        # 5) Cu 집전체 (Shell)
        pid_cu = 2000 + LT_CU_CC
        print(f"  [Layer] Cu CC (Shell), offset={off:.4f}")
        self._cu_cc_grid = self._create_spiral_shell_layer(pid_cu, off, s_values)
        cu_cc_pids.append(pid_cu)
        off += d.t_cu_cc

        print(f"  [완료] 최종 오프셋: {off:.4f} mm (= unit_cell_thickness: "
              f"{d.unit_cell_thickness:.4f})")

        # --- 파우치 + 전해질 ---
        self._create_pouch_and_electrolyte()

        # --- 내부 코어 (맨드릴 제거 후 빈 공간) ---
        if d.core_fill == 'electrolyte':
            self._fill_inner_core_electrolyte()
        else:
            print("  [Core] void — 내부 빈 공간 (메시 없음)")

        # --- 임팩터 ---
        if d.impactor_type == "nail":
            self._create_nail_impactor()
        else:
            self._create_impactor()

        # --- 탭 + PCM ---
        self._create_wound_tabs()
        self._create_wound_pcm()

        # --- 파트 세트 (05_contacts.k 호환 SID 순서) ---
        self.part_sets["PSET_IMPACTOR"] = [PID_IMPACTOR]
        self.part_sets["PSET_POUCH"] = [PID_POUCH_WRAP, PID_POUCH_TOP,
                                          PID_POUCH_BOTTOM]
        self.part_sets["PSET_ALL_CELL"] = (al_cc_pids + cu_cc_pids +
                                            cathode_pids + anode_pids +
                                            separator_pids +
                                            [PID_POUCH_WRAP, PID_POUCH_TOP,
                                             PID_POUCH_BOTTOM,
                                             PID_ELECTROLYTE_FILL])
        self.part_sets["PSET_ALL_CATHODE"] = cathode_pids
        self.part_sets["PSET_ALL_ANODE"] = anode_pids
        self.part_sets["PSET_ALL_SEPARATOR"] = separator_pids
        self.part_sets["PSET_ALL_AL_CC"] = al_cc_pids
        self.part_sets["PSET_ALL_CU_CC"] = cu_cc_pids
        self.part_sets["PSET_ELECTROLYTE"] = [PID_ELECTROLYTE_FILL]
        self.part_sets["PSET_PCM"] = [PID_PCM_POS, PID_PCM_NEG]

        # --- 경계 노드 세트 ---
        self._create_boundary_node_sets()

        print(f"\n  총 노드: {self.total_nodes:,}")
        print(f"  총 셸 요소: {self.total_shells:,}")
        print(f"  총 솔리드 요소: {self.total_solids:,}")
        print(f"  총 요소: {self.total_shells + self.total_solids:,}")

    # ── 파우치 + 전해질 (레이스트랙 형상 감싸기) ──

    def _create_single_loop_nodes(self, offset: float) -> np.ndarray:
        """레이스트랙 경로 한 바퀴를 고정 오프셋으로 순회, Y축 압출 노드 그리드 생성

        Args:
            offset: r_mandrel로부터의 반경 오프셋 (mm)

        Returns:
            nid_grid (n_y+1, n_path+1) — 마지막 열은 첫 열과 공유 (폐합)
        """
        d = self.d
        n_path = d.n_path
        n_y = d.n_y
        dy = d.cell_height / n_y
        s_values = np.linspace(0, 1, n_path + 1)

        nid_grid = np.zeros((n_y + 1, n_path + 1), dtype=np.int64)

        for js in range(n_path + 1):
            if js == n_path:
                # 폐합: 마지막 열 = 첫 열
                nid_grid[:, js] = nid_grid[:, 0]
                continue
            s = s_values[js]
            x, z = self.path.get_racetrack_point(s, offset)
            for jy in range(n_y + 1):
                y = jy * dy
                nid_grid[jy, js] = self._add_node_xyz(x, y, z)

        return nid_grid

    def _create_loop_shell(self, pid: int, nid_grid: np.ndarray):
        """한 바퀴 루프 노드 그리드로부터 셸 요소 생성"""
        d = self.d
        n_path = d.n_path
        n_y = d.n_y
        for jy in range(n_y):
            for js in range(n_path):
                n1 = nid_grid[jy, js]
                n2 = nid_grid[jy, js + 1]
                n3 = nid_grid[jy + 1, js + 1]
                n4 = nid_grid[jy + 1, js]
                self._add_shell(pid, n1, n2, n3, n4)
        if pid not in self.part_ids:
            self.part_ids.append(pid)

    def _create_loop_solid(self, pid: int, inner_grid: np.ndarray,
                           outer_grid: np.ndarray):
        """두 루프 노드 그리드(내면/외면) 사이에 솔리드 요소 생성"""
        d = self.d
        n_path = d.n_path
        n_y = d.n_y
        for jy in range(n_y):
            for js in range(n_path):
                ns = (
                    inner_grid[jy, js],
                    outer_grid[jy, js],
                    outer_grid[jy, js + 1],
                    inner_grid[jy, js + 1],
                    inner_grid[jy + 1, js],
                    outer_grid[jy + 1, js],
                    outer_grid[jy + 1, js + 1],
                    inner_grid[jy + 1, js + 1],
                )
                self._add_solid(pid, ns)
        if pid not in self.part_ids:
            self.part_ids.append(pid)

    def _create_pouch_and_electrolyte(self):
        """레이스트랙 형상 파우치 감싸기 + 전해질 버퍼 + 캡 (노드 공유)

        구조:
          젤리롤 외면 (r_outer) → 전해질 솔리드 → 파우치 셸 (포장재)
          + Y 양끝 캡: 파우치 랩 경계 노드 공유, 레이스트랙 형상
                       직선부 = 구조격자, 반원부 = 삼각 팬
        """
        d = self.d
        r_outer = d.r_mandrel + d.unit_cell_thickness * d.n_winds

        # 전해질 내면 = 젤리롤 외면
        elec_inner_offset = r_outer - d.r_mandrel  # mandrel 기준 오프셋
        elec_outer_offset = elec_inner_offset + d.t_electrolyte_buffer
        pouch_offset = elec_outer_offset + d.t_pouch / 2.0  # 셸 중앙면

        print(f"  [Electrolyte] r={r_outer:.3f}~"
              f"{r_outer + d.t_electrolyte_buffer:.3f} mm")
        print(f"  [Pouch wrap] r={r_outer + d.t_electrolyte_buffer:.3f} mm")

        # 노드 그리드 생성
        inner_grid = self._create_single_loop_nodes(elec_inner_offset)
        outer_grid = self._create_single_loop_nodes(elec_outer_offset)
        pouch_grid = self._create_single_loop_nodes(pouch_offset)

        # 전해질 솔리드
        self._create_loop_solid(PID_ELECTROLYTE_FILL, inner_grid, outer_grid)

        # 파우치 바디 셸 (레이스트랙 형상)
        self._create_loop_shell(PID_POUCH_WRAP, pouch_grid)

        # ── Y 양끝 캡 (레이스트랙 형상, 노드 공유) ──
        n_path = d.n_path
        n_str = d.n_straight_seg
        n_arc = d.n_arc_seg
        n_y = d.n_y
        cx = d.cell_width / 2.0
        half_L = d.straight_length / 2.0
        s_values = np.linspace(0, 1, n_path + 1)

        for pid, y_wrap_idx, y_cap in [
                (PID_POUCH_TOP,    n_y,  d.cell_height + d.t_pouch / 2.0),
                (PID_POUCH_BOTTOM, 0,   -d.t_pouch / 2.0)]:
            is_back = (pid == PID_POUCH_TOP)
            wrap_row = pouch_grid[y_wrap_idx, :]  # 랩 경계행

            # ① 연장 행 (캡 y에서 랩과 동일 XZ 좌표) ─ 공유 경계
            ext = np.zeros(n_path + 1, dtype=np.int64)
            for js in range(n_path + 1):
                if js == n_path:
                    ext[js] = ext[0]
                    continue
                x, z = self.path.get_racetrack_point(s_values[js],
                                                     pouch_offset)
                ext[js] = self._add_node_xyz(x, y_cap, z)

            # 하면 캡 가장자리 노드 저장 (SPC 경계용)
            if pid == PID_POUCH_BOTTOM:
                self._bottom_cap_perimeter = list(set(
                    list(ext[:n_path]) + list(wrap_row[:n_path])))

            # 상면 캡 가장자리 노드 저장 (스웰링 BC: NSID=1002용)
            if pid == PID_POUCH_TOP:
                self._top_cap_perimeter = list(set(
                    list(ext[:n_path]) + list(wrap_row[:n_path])))

            # ② 연결 스트립 (랩 경계 → 연장행, PID_POUCH_WRAP)
            for js in range(n_path):
                if is_back:
                    self._add_shell(PID_POUCH_WRAP,
                                    wrap_row[js], wrap_row[js + 1],
                                    ext[js + 1], ext[js])
                else:
                    self._add_shell(PID_POUCH_WRAP,
                                    ext[js + 1], ext[js],
                                    wrap_row[js], wrap_row[js + 1])

            # ③ 중심선 (z=0, 직선부 x 범위)
            if n_str > 0:
                dx_str = d.straight_length / n_str
                center = np.zeros(n_str + 1, dtype=np.int64)
                for i in range(n_str + 1):
                    x = cx - half_L + i * dx_str
                    center[i] = self._add_node_xyz(x, y_cap, 0.0)

                # ④ 상부 패널: 상부 직선(z=+R) → 중심선(z=0)
                # PID_POUCH_TOP(상단 끝캡): 탭 통과 X 범위는 구멍으로 남김
                tab_x_ranges = getattr(self, '_tab_x_ranges', [])
                for i in range(n_str):
                    x_i  = cx - half_L + i       * dx_str
                    x_i1 = cx - half_L + (i + 1) * dx_str
                    if is_back and any(x_i < xh and x_i1 > xl
                                      for xl, xh in tab_x_ranges):
                        continue  # 탭 통과 영역 — 끝캡에 구멍
                    if is_back:
                        self._add_shell(pid,
                                        ext[i], ext[i + 1],
                                        center[i + 1], center[i])
                    else:
                        self._add_shell(pid,
                                        ext[i + 1], ext[i],
                                        center[i], center[i + 1])

                # ⑤ 하부 패널: 중심선(z=0) → 하부 직선(z=-R, 뒤집힌 순서)
                for i in range(n_str):
                    lo = ext[2 * n_str + n_arc - i]  # 하부직선 뒤집기
                    lo_next = ext[2 * n_str + n_arc - i - 1]
                    if is_back:
                        self._add_shell(pid,
                                        center[i], center[i + 1],
                                        lo_next, lo)
                    else:
                        self._add_shell(pid,
                                        center[i + 1], center[i],
                                        lo, lo_next)

                # ⑥ 우측 반원 팬 (center[n_str] → 우측 호)
                rc = center[n_str]
                for k in range(n_arc):
                    n1 = ext[n_str + k]
                    n2 = ext[n_str + k + 1]
                    if is_back:
                        self._add_shell(pid, rc, n1, n2, rc)
                    else:
                        self._add_shell(pid, rc, n2, n1, rc)

                # ⑦ 좌측 반원 팬 (center[0] → 좌측 호)
                lc = center[0]
                for k in range(n_arc):
                    js = 2 * n_str + n_arc + k
                    n1 = ext[js]
                    n2 = ext[js + 1]
                    if is_back:
                        self._add_shell(pid, lc, n1, n2, lc)
                    else:
                        self._add_shell(pid, lc, n2, n1, lc)

            else:
                # n_str == 0: 원형 → 중심 1점에서 팬
                center_nid = self._add_node_xyz(cx, y_cap, 0.0)
                for js in range(n_path):
                    n1 = ext[js]
                    n2 = ext[js + 1]
                    if is_back:
                        self._add_shell(pid, center_nid, n1, n2, center_nid)
                    else:
                        self._add_shell(pid, center_nid, n2, n1, center_nid)

            if pid not in self.part_ids:
                self.part_ids.append(pid)

        print("  [Caps] 노드공유 레이스트랙 캡 생성 완료")

    # ── 내부 코어 전해질 충전 (맨드릴 제거 후 빈 공간) ──

    def _fill_inner_core_electrolyte(self):
        """맨드릴 제거 후 빈 공간(0 ~ r_mandrel)을 전해질 솔리드로 채움

        동심 레이스트랙 루프를 n_layers 층으로 쌓아서 채움.
        O-grid 축퇴 요소 없이 깔끔한 hex 요소만 사용.
        최내층은 r_min > 0 으로 유지 (완전 퇴화 방지, 매우 작은 타원).
        """
        d = self.d
        r_mand = d.r_mandrel

        if r_mand < 0.05:
            print("  [Core] r_mandrel 너무 작음 → 스킵")
            return

        # 레이어 수: 반경/mesh_size_path 기준, 최소 2층
        n_layers = max(2, int(round(r_mand / d.mesh_size_path)))
        # 최내층 반경 (완전 퇴화 방지: 최소 r_mandrel의 15%)
        r_min = max(0.1, r_mand * 0.15)
        dr = (r_mand - r_min) / n_layers

        print(f"  [Core] 내부 전해질 충전: r=[{r_min:.2f}~{r_mand:.2f}] mm, "
              f"{n_layers} 층")

        # 동심 루프 노드 그리드 생성 (안쪽 → 바깥쪽)
        # offset = 0 → r_mandrel 표면, 음수 offset → 내부
        grids = []
        for i_layer in range(n_layers + 1):
            r_cur = r_min + i_layer * dr
            # _create_single_loop_nodes 는 r_mandrel + offset 기준
            # r_cur = r_mandrel + offset  →  offset = r_cur - r_mandrel
            loop_offset = r_cur - r_mand
            grid = self._create_single_loop_nodes(loop_offset)
            grids.append(grid)

        # 솔리드 요소: 인접 루프 사이
        pid = PID_ELECTROLYTE_FILL
        for i_layer in range(n_layers):
            self._create_loop_solid(pid, grids[i_layer], grids[i_layer + 1])

        print(f"  [Core] 전해질 솔리드 {n_layers} 층 완료")

    # ── 임팩터 (솔리드 원통) ──

    def _create_impactor(self):
        """측면 임팩터 — 솔리드 원통 (Y축 방향, hex 요소)"""
        d = self.d
        R = d.impactor_radius
        L = d.impactor_length

        _r_outer = d.r_mandrel + d.unit_cell_thickness * d.n_winds
        cx = d.cell_width + d.impactor_offset + R   # X 중심
        cy = d.cell_height / 2.0                     # Y 중심
        cz = 0.0                                     # Z 중심

        n_circ  = d.impactor_n_circ
        n_radial = d.impactor_n_radial
        n_axial = max(4, int(round(L / d.mesh_size_y)))

        dr = R / n_radial
        dy_imp = L / n_axial
        dtheta = 2.0 * np.pi / n_circ

        # 노드 생성: 축 중심선 + 반경 링
        center_nids = np.zeros(n_axial + 1, dtype=np.int64)
        ring_nids = np.zeros((n_axial + 1, n_radial, n_circ), dtype=np.int64)

        for j in range(n_axial + 1):
            y = cy - L / 2 + j * dy_imp
            center_nids[j] = self._add_node_xyz(cx, y, cz)
            for k in range(n_radial):
                r = (k + 1) * dr
                for i in range(n_circ):
                    theta = i * dtheta
                    x = cx - r * np.cos(theta)
                    z = cz + r * np.sin(theta)
                    ring_nids[j, k, i] = self._add_node_xyz(x, y, z)

        pid = PID_IMPACTOR

        for j in range(n_axial):
            # 내부 링 (중심 → 첫 번째 링): 축퇴 hex (wedge)
            for i in range(n_circ):
                i_next = (i + 1) % n_circ
                ns = (
                    center_nids[j],
                    ring_nids[j, 0, i],
                    ring_nids[j, 0, i_next],
                    center_nids[j],           # collapsed
                    center_nids[j + 1],
                    ring_nids[j + 1, 0, i],
                    ring_nids[j + 1, 0, i_next],
                    center_nids[j + 1],       # collapsed
                )
                self._add_solid(pid, ns)

            # 외부 링 (ring k-1 → ring k): 정규 hex
            for k in range(1, n_radial):
                for i in range(n_circ):
                    i_next = (i + 1) % n_circ
                    ns = (
                        ring_nids[j, k - 1, i],
                        ring_nids[j, k,     i],
                        ring_nids[j, k,     i_next],
                        ring_nids[j, k - 1, i_next],
                        ring_nids[j + 1, k - 1, i],
                        ring_nids[j + 1, k,     i],
                        ring_nids[j + 1, k,     i_next],
                        ring_nids[j + 1, k - 1, i_next],
                    )
                    self._add_solid(pid, ns)

        self.part_ids.append(pid)

        # 임팩터 중심 노드 세트 (강체 구속 / 처방 운동 BC 용)
        self.node_sets["NSET_IMPACTOR_CENTER"] = list(center_nids)

    # ── 네일 임팩터 (B12) ──

    def _create_nail_impactor(self):
        """네일 관통 임팩터 — 원추 팁 + 원통 축 (X방향)"""
        d = self.d
        R_shaft = d.nail_shaft_radius
        R_tip = d.nail_tip_radius
        tip_len = d.nail_tip_length
        total_len = d.impactor_radius * 2
        shaft_len = total_len - tip_len

        cx_start = d.cell_width + d.impactor_offset
        cy = d.cell_height / 2.0
        cz = 0.0

        n_circ = d.impactor_n_circ
        n_radial = max(2, d.impactor_n_radial // 2)
        n_shaft = max(4, int(round(shaft_len / d.mesh_size_y)))
        n_tip = max(3, int(round(tip_len / (d.mesh_size_y * 0.5))))

        dtheta = 2.0 * np.pi / n_circ

        slice_x, slice_r = [], []
        for j in range(n_tip + 1):
            frac = j / n_tip
            slice_x.append(cx_start + frac * tip_len)
            slice_r.append(R_tip + frac * (R_shaft - R_tip))
        for j in range(1, n_shaft + 1):
            frac = j / n_shaft
            slice_x.append(cx_start + tip_len + frac * shaft_len)
            slice_r.append(R_shaft)

        n_slices = len(slice_x)
        center_nids = np.zeros(n_slices, dtype=np.int64)
        ring_nids = np.zeros((n_slices, n_radial, n_circ), dtype=np.int64)

        for j in range(n_slices):
            x = slice_x[j]
            center_nids[j] = self._add_node_xyz(x, cy, cz)
            R_local = slice_r[j]
            dr = R_local / n_radial
            for k in range(n_radial):
                r = (k + 1) * dr
                for i in range(n_circ):
                    theta = i * dtheta
                    y = cy + r * np.cos(theta)
                    z = cz + r * np.sin(theta)
                    ring_nids[j, k, i] = self._add_node_xyz(x, y, z)

        pid = PID_IMPACTOR
        for j in range(n_slices - 1):
            for i in range(n_circ):
                i_next = (i + 1) % n_circ
                ns = (
                    center_nids[j], ring_nids[j, 0, i],
                    ring_nids[j, 0, i_next], center_nids[j],
                    center_nids[j+1], ring_nids[j+1, 0, i],
                    ring_nids[j+1, 0, i_next], center_nids[j+1],
                )
                self._add_solid(pid, ns)
            for k in range(1, n_radial):
                for i in range(n_circ):
                    i_next = (i + 1) % n_circ
                    ns = (
                        ring_nids[j, k-1, i], ring_nids[j, k, i],
                        ring_nids[j, k, i_next], ring_nids[j, k-1, i_next],
                        ring_nids[j+1, k-1, i], ring_nids[j+1, k, i],
                        ring_nids[j+1, k, i_next], ring_nids[j+1, k-1, i_next],
                    )
                    self._add_solid(pid, ns)

        self.part_ids.append(pid)
        self.node_sets["NSET_IMPACTOR_CENTER"] = list(center_nids)

    # ── 탭 + PCM (와인딩 구조) ──

    def _create_wound_tabs(self):
        """와인딩 구조 탭 생성 — Al(+)/Cu(-) 모두 상단(+Y)에서 돌출

        최외곽 와인딩의 상부 직선부(Seg 1)에서 탭 X 범위에 해당하는
        노드들로부터 +Y 방향 셸 스트립을 생성한다.
        """
        d = self.d
        if self._al_cc_grid is None or self._cu_cc_grid is None:
            print("  [SKIP] CC 그리드 없음 — 탭 생략")
            return

        n_path = d.n_path
        n_str = d.n_straight_seg

        # 최외곽 와인딩의 상부 직선부 s_local ∈ [0, f_str]
        # → 글로벌 인덱스: (n_winds-1)*n_path ~ (n_winds-1)*n_path + n_str
        last_wind_start = (d.n_winds - 1) * n_path

        # 상부 직선부 X 좌표 계산 (Seg 1: 좌→우)
        cx = d.cell_width / 2.0
        half_L = d.straight_length / 2.0
        x_left_str = cx - half_L
        dx_str = d.straight_length / n_str if n_str > 0 else 0

        self._tab_tip_nids = {'positive': [], 'negative': []}
        self._tab_x_ranges: list = []  # [(x_lo, x_hi), ...] 끝캡 홀 생성에 사용

        for tab_side, cc_grid, pid_tab, x_center in [
            ('positive', self._al_cc_grid, PID_TAB_POS, d.tab_pos_x_center),
            ('negative', self._cu_cc_grid, PID_TAB_NEG, d.tab_neg_x_center),
        ]:
            # 탭 X 범위
            x_lo = x_center - d.tab_width / 2
            x_hi = x_center + d.tab_width / 2
            self._tab_x_ranges.append((x_lo, x_hi))  # 끝캡 홀용 저장

            # 상부 직선부 노드 중 탭 범위 안의 컬럼 인덱스 찾기
            tab_col_indices = []
            for i_seg in range(n_str + 1):
                js = last_wind_start + i_seg
                if js >= cc_grid.shape[1]:
                    continue
                x_node = x_left_str + i_seg * dx_str
                if x_lo - 0.01 <= x_node <= x_hi + 0.01:
                    tab_col_indices.append(js)

            if len(tab_col_indices) < 2:
                print(f"  [SKIP] {tab_side} 탭: 충분한 노드 없음")
                continue

            # CC 그리드 상단 행 (Y=cell_height)에서 탭 앵커 노드
            anchor_nids = cc_grid[d.n_y, tab_col_indices]

            # 탭 스트립 — +Y 방향으로 확장
            n_tab_rows = max(2, int(round(d.tab_height / d.mesh_size_y)))
            dy_tab = d.tab_height / n_tab_rows
            n_cols = len(tab_col_indices)

            # Z 좌표 계산 (최외곽 와인딩의 상부 직선: Z = R)
            # 각 CC 레이어의 법선 오프셋
            if tab_side == 'positive':
                layer_offset = 0.0  # Al CC = 첫 번째 층
            else:
                layer_offset = (d.t_al_cc + d.t_cathode
                                + d.t_separator + d.t_anode)  # Cu CC 오프셋
            spiral_offset = layer_offset + (d.n_winds - 1) * d.unit_cell_thickness
            z_tab = d.r_mandrel + spiral_offset  # 상부 직선부 Z

            prev_row = anchor_nids.copy()

            for row_idx in range(n_tab_rows):
                y = d.cell_height + (row_idx + 1) * dy_tab
                new_nids = []
                for ic, js in enumerate(tab_col_indices):
                    x_node = x_left_str + (js - last_wind_start) * dx_str
                    nid = self._add_node_xyz(x_node, y, z_tab)
                    new_nids.append(nid)

                new_nids_arr = np.array(new_nids, dtype=np.int64)

                for ic in range(n_cols - 1):
                    self._add_shell(pid_tab,
                                    prev_row[ic], prev_row[ic + 1],
                                    new_nids_arr[ic + 1], new_nids_arr[ic])

                prev_row = new_nids_arr

            self._tab_tip_nids[tab_side] = prev_row.copy()

            if pid_tab not in self.part_ids:
                self.part_ids.append(pid_tab)

            print(f"  탭 ({tab_side}): X=[{x_lo:.1f}~{x_hi:.1f}], "
                  f"Y=[{d.cell_height:.1f}~{d.cell_height + d.tab_height:.1f}], "
                  f"Z={z_tab:.2f}, {n_cols}x{n_tab_rows} 요소")

    def _create_wound_pcm(self):
        """와인딩 구조 PCM 보드 생성 — 양극/음극 탭 끝에 하나의 보드

        실제 파우치 배터리: 탭이 모두 상단에서 나오고,
        PCM 보드 1장이 양쪽 탭을 연결.
        """
        d = self.d
        tip_pos = getattr(self, '_tab_tip_nids', {}).get('positive', [])
        tip_neg = getattr(self, '_tab_tip_nids', {}).get('negative', [])

        if len(tip_pos) == 0 and len(tip_neg) == 0:
            print("  [SKIP] 탭 팁 없음 — PCM 생략")
            return

        # PCM 보드 X 범위: 양극 탭 좌측 ~ 음극 탭 우측
        x_left = min(d.tab_pos_x_center, d.tab_neg_x_center) - d.tab_width / 2
        x_right = max(d.tab_pos_x_center, d.tab_neg_x_center) + d.tab_width / 2
        pcm_full_width = x_right - x_left

        y_tip = d.cell_height + d.tab_height  # 탭 끝 Y 좌표

        # Z 좌표: 두 탭의 Z 중간 (또는 젤리롤 중심면 z=0)
        z_mid = 0.0
        pcm_z_bot = z_mid - d.pcm_thickness / 2
        pcm_z_top = z_mid + d.pcm_thickness / 2

        mesh_sz = d.mesh_size_y  # PCM 요소 크기 기준
        nx_pcm = max(2, int(round(pcm_full_width / mesh_sz)))
        nz_pcm = max(1, int(round(d.pcm_thickness / mesh_sz)))
        ny_pcm = max(1, int(round(d.pcm_height / mesh_sz)))

        dx_p = pcm_full_width / nx_pcm
        dz_p = (pcm_z_top - pcm_z_bot) / nz_pcm
        dy_p = d.pcm_height / ny_pcm

        # 솔리드 노드 (ny_pcm+1) × (nz_pcm+1) × (nx_pcm+1)
        nids = np.zeros((ny_pcm + 1, nz_pcm + 1, nx_pcm + 1), dtype=np.int64)
        for jy in range(ny_pcm + 1):
            y = y_tip + jy * dy_p
            for jz in range(nz_pcm + 1):
                z = pcm_z_bot + jz * dz_p
                for jx in range(nx_pcm + 1):
                    x = x_left + jx * dx_p
                    nids[jy, jz, jx] = self._add_node_xyz(x, y, z)

        # PCM_POS / PCM_NEG 분할 (X 중점 기준)
        x_mid_pcm = (d.tab_pos_x_center + d.tab_neg_x_center) / 2.0
        ix_mid = 0
        for jx in range(nx_pcm + 1):
            if x_left + jx * dx_p >= x_mid_pcm:
                ix_mid = jx
                break

        for jy in range(ny_pcm):
            for jz in range(nz_pcm):
                for jx in range(nx_pcm):
                    # LS-DYNA hex 양의 Jacobian 순서:
                    # (n2-n1)×(n4-n1)·(n5-n1) > 0
                    # n1,n4=Z방향, n2,n3=X+Z방향으로 CCW 배치
                    ns = (
                        nids[jy,   jz,   jx  ],   # n1 (X0,Y0,Z0)
                        nids[jy,   jz+1, jx  ],   # n2 (X0,Y0,Z1)
                        nids[jy,   jz+1, jx+1],   # n3 (X1,Y0,Z1)
                        nids[jy,   jz,   jx+1],   # n4 (X1,Y0,Z0)
                        nids[jy+1, jz,   jx  ],   # n5 (X0,Y1,Z0)
                        nids[jy+1, jz+1, jx  ],   # n6 (X0,Y1,Z1)
                        nids[jy+1, jz+1, jx+1],   # n7 (X1,Y1,Z1)
                        nids[jy+1, jz,   jx+1],   # n8 (X1,Y1,Z0)
                    )
                    pid = PID_PCM_POS if jx < ix_mid else PID_PCM_NEG
                    self._add_solid(pid, ns)

        if PID_PCM_POS not in self.part_ids:
            self.part_ids.append(PID_PCM_POS)
        if PID_PCM_NEG not in self.part_ids:
            self.part_ids.append(PID_PCM_NEG)

        # PCM 접합면 노드 세트
        contact_nids = []
        for jz in range(nz_pcm + 1):
            for jx in range(nx_pcm + 1):
                contact_nids.append(nids[0, jz, jx])
        self.node_sets["NSET_PCM_CONTACT"] = contact_nids

        print(f"  PCM 보드 (통합): X=[{x_left:.1f}~{x_right:.1f}], "
              f"Y=[{y_tip:.1f}~{y_tip + d.pcm_height:.1f}], "
              f"{nx_pcm}x{ny_pcm}x{nz_pcm} 요소")

    # ── 경계 노드 ──

    def _create_boundary_node_sets(self):
        """파우치 하면 가장자리 — SPC용"""
        bottom_nids = getattr(self, '_bottom_cap_perimeter', [])
        self.node_sets["NSET_FIX_BOTTOM_EDGE"] = sorted(bottom_nids)

        # 파우치 상면 노드 (스웰링 BC: BOUNDARY_PRESCRIBED_MOTION_SET NSID=1002)
        top_nids = getattr(self, '_top_cap_perimeter', [])
        if top_nids:
            self.node_sets["NSET_STACK_TOP"] = sorted(top_nids)

    # ================================================================
    # k-file 출력
    # ================================================================
    def write_kfile(self, filepath: str):
        """k-file 출력: 3개 임시파일 → 합치기"""
        print(f"\n  k-file 쓰기: {filepath}")

        tmpdir = os.path.dirname(os.path.abspath(filepath))
        tmp_nodes = os.path.join(tmpdir, "_tmp_w_nodes.k")
        tmp_shells = os.path.join(tmpdir, "_tmp_w_shells.k")
        tmp_solids = os.path.join(tmpdir, "_tmp_w_solids.k")

        self._f_nodes = open(tmp_nodes, 'w', encoding='utf-8')
        self._f_shells = open(tmp_shells, 'w', encoding='utf-8')
        self._f_solids = open(tmp_solids, 'w', encoding='utf-8')

        self.next_nid = 1
        self.next_eid = 1
        self.total_nodes = 0
        self.total_shells = 0
        self.total_solids = 0
        self.part_ids = []

        print("  메시 생성 중 (나선 스트리밍)...")
        self.build_wound_cell()

        self._f_nodes.close()
        self._f_shells.close()
        self._f_solids.close()

        print("  파일 합치기...")
        with open(filepath, 'w', encoding='utf-8') as fout:
            fout.write("*KEYWORD\n")
            fout.write("*TITLE\n")
            fout.write("Flat Wound Jellyroll Pouch Cell - Archimedean Spiral\n")

            fout.write("$\n$ ============ NODES ============\n$\n")
            fout.write("*NODE\n")
            with open(tmp_nodes, 'r', encoding='utf-8') as fin:
                shutil.copyfileobj(fin, fout)

            fout.write("$\n$ ============ SHELL ELEMENTS ============\n$\n")
            fout.write("*ELEMENT_SHELL\n")
            with open(tmp_shells, 'r', encoding='utf-8') as fin:
                shutil.copyfileobj(fin, fout)

            fout.write("$\n$ ============ SOLID ELEMENTS ============\n$\n")
            fout.write("*ELEMENT_SOLID\n")
            with open(tmp_solids, 'r', encoding='utf-8') as fin:
                shutil.copyfileobj(fin, fout)

            self._write_parts(fout)
            self._write_sections(fout)
            self._write_node_sets(fout)
            self._write_part_sets(fout)
            fout.write("*END\n")

        for tmp in [tmp_nodes, tmp_shells, tmp_solids]:
            os.remove(tmp)

        fsize = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  파일 크기: {fsize:.1f} MB")

    def _get_part_name(self, pid: int) -> str:
        """PID → 명확한 파트 이름"""
        if pid == PID_IMPACTOR:
            return "Impactor_Solid"
        if pid == PID_ELECTROLYTE_FILL:
            return "Electrolyte_Fill_Solid"
        if pid == PID_POUCH_WRAP:
            return "Pouch_Wrap_Shell"
        if pid == PID_POUCH_TOP:
            return "Pouch_EndCap_Back"
        if pid == PID_POUCH_BOTTOM:
            return "Pouch_EndCap_Front"
        lt = pid % 10
        base_name = LAYER_NAMES.get(lt, f"Unknown_{lt}")
        elem = "Shell" if lt in (LT_AL_CC, LT_CU_CC, LT_SEPARATOR) else "Solid"
        return f"{base_name}_Spiral_{elem}"

    def _write_parts(self, f: TextIO):
        f.write("$\n$ ============ PARTS ============\n$\n")
        for pid in sorted(self.part_ids):
            sid, mid, tmid, eosid = self._get_part_props(pid)
            name = self._get_part_name(pid)
            f.write("*PART\n")
            f.write(f"{name}\n")
            eos_str = f"{eosid:>10d}" if eosid else f"{'':>10s}"
            f.write(f"{pid:>10d}{sid:>10d}{mid:>10d}{eos_str}"
                    f"{'':>10s}{'':>10s}{'':>10s}{tmid:>10d}\n")

    def _get_part_props(self, pid: int) -> Tuple[int, int, int, int]:
        """PID → (SID, MID, TMID, EOSID)
        EOSID: 셸 요소는 EOS 불필요 → 0 (Al/Cu CC 포함)
        솔리드 요소로 변경 시 EOS_GRUNEISEN 활성화 + EOSID 지정"""
        if pid == PID_IMPACTOR:
            return SID_SOLID_IMPACTOR, MID_RIGID, 0, 0
        if pid == PID_ELECTROLYTE_FILL:
            return SID_SOLID_CORE, MID_ELECTROLYTE, 108, 0
        if pid == PID_POUCH_WRAP:
            return SID_SHELL_POUCH, MID_POUCH, 106, 0
        if pid in (PID_POUCH_TOP, PID_POUCH_BOTTOM):
            return SID_SHELL_POUCH, MID_POUCH, 106, 0
        lt = pid % 10
        if lt == LT_AL_CC:
            return SID_SHELL_BT, MID_AL, 101, 0
        elif lt == LT_CATHODE:
            return SID_SOLID_1PT, MID_NMC, 103, 0
        elif lt == LT_SEPARATOR:
            return SID_SHELL_FULL, MID_SEPARATOR, 105, 0
        elif lt == LT_ANODE:
            return SID_SOLID_1PT, MID_GRAPHITE, 104, 0
        elif lt == LT_CU_CC:
            return SID_SHELL_CU_CC, MID_CU, 102, 0
        return SID_SHELL_BT, MID_AL, 0, 0

    def _write_sections(self, f: TextIO):
        d = self.d
        f.write("$\n$ ============ SECTIONS ============\n$\n")
        f.write("*SECTION_SHELL\n")
        f.write(f"{SID_SHELL_BT:>10d}{2:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"{d.t_al_cc:>10.4f}{d.t_al_cc:>10.4f}"
                f"{d.t_al_cc:>10.4f}{d.t_al_cc:>10.4f}\n")

        f.write("*SECTION_SHELL\n")
        f.write(f"{SID_SHELL_FULL:>10d}{16:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"{d.t_separator:>10.4f}{d.t_separator:>10.4f}"
                f"{d.t_separator:>10.4f}{d.t_separator:>10.4f}\n")

        f.write("*SECTION_SOLID\n")
        f.write(f"{SID_SOLID_1PT:>10d}{1:>10d}\n")

        f.write("$ Impactor solid section\n")
        f.write("*SECTION_SOLID\n")
        f.write(f"{SID_SOLID_IMPACTOR:>10d}{1:>10d}\n")

        f.write("$ Mandrel core solid section\n")
        f.write("*SECTION_SOLID\n")
        f.write(f"{SID_SOLID_CORE:>10d}{1:>10d}\n")

        # Shell Pouch (ELFORM=2) — 파우치
        f.write("*SECTION_SHELL\n")
        f.write(f"{SID_SHELL_POUCH:>10d}{2:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"{d.t_pouch:>10.4f}{d.t_pouch:>10.4f}"
                f"{d.t_pouch:>10.4f}{d.t_pouch:>10.4f}\n")

        # Shell Cu CC (ELFORM=2) — Cu 집전체
        f.write("*SECTION_SHELL\n")
        f.write(f"{SID_SHELL_CU_CC:>10d}{2:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"{d.t_cu_cc:>10.4f}{d.t_cu_cc:>10.4f}"
                f"{d.t_cu_cc:>10.4f}{d.t_cu_cc:>10.4f}\n")

    def _write_node_sets(self, f: TextIO):
        """노드 세트 출력 — 고정 SID 매핑 (06_boundary_loads.k 호환)"""
        f.write("$\n$ ============ NODE SETS ============\n$\n")
        FIXED_SID = {
            "NSET_FIX_BOTTOM_EDGE": 1,
            "NSET_IMPACTOR_CENTER": 2,
            "NSET_STACK_TOP":       1002,
        }
        next_sid = max(FIXED_SID.values()) + 1
        for name in sorted(FIXED_SID, key=lambda n: FIXED_SID[n]):
            if name not in self.node_sets:
                continue
            nids = self.node_sets[name]
            if len(nids) == 0:
                continue
            sid = FIXED_SID[name]
            f.write(f"*SET_NODE_LIST_TITLE\n{name}\n")
            f.write(f"{sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(nids), 8):
                chunk = nids[i:i + 8]
                line = "".join(f"{n:>10d}" for n in chunk)
                f.write(line + "\n")
        for name, nids in self.node_sets.items():
            if name in FIXED_SID:
                continue
            if len(nids) == 0:
                continue
            f.write(f"*SET_NODE_LIST_TITLE\n{name}\n")
            f.write(f"{next_sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(nids), 8):
                chunk = nids[i:i + 8]
                line = "".join(f"{n:>10d}" for n in chunk)
                f.write(line + "\n")
            next_sid += 1

    def _write_part_sets(self, f: TextIO):
        """파트 세트 출력 — 고정 SID 매핑 (05_contacts.k 호환)"""
        f.write("$\n$ ============ PART SETS ============\n$\n")
        FIXED_SID = {
            "PSET_IMPACTOR":      100,
            "PSET_POUCH":         101,
            "PSET_ALL_CELL":      102,
            "PSET_ALL_CATHODE":   103,
            "PSET_ALL_ANODE":     104,
            "PSET_ALL_SEPARATOR": 105,
            "PSET_ALL_AL_CC":     106,
            "PSET_ALL_CU_CC":     107,
            "PSET_ELECTROLYTE":   108,
        }
        next_sid = max(FIXED_SID.values()) + 1
        for name in sorted(FIXED_SID, key=lambda n: FIXED_SID[n]):
            if name not in self.part_sets:
                continue
            pids = self.part_sets[name]
            sid = FIXED_SID[name]
            f.write(f"*SET_PART_LIST_TITLE\n{name}\n")
            f.write(f"{sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(pids), 8):
                chunk = pids[i:i + 8]
                line = "".join(f"{p:>10d}" for p in chunk)
                f.write(line + "\n")
        for name, pids in self.part_sets.items():
            if name in FIXED_SID:
                continue
            f.write(f"*SET_PART_LIST_TITLE\n{name}\n")
            f.write(f"{next_sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(pids), 8):
                chunk = pids[i:i + 8]
                line = "".join(f"{p:>10d}" for p in chunk)
                f.write(line + "\n")
            next_sid += 1

# ============================================================
# 메인
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="와인딩형 배터리 메시 생성기 (YAML 설정 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_mesh_wound.py --config battery_config.yaml --tier 0
  python generate_mesh_wound.py --tier -1 --mesh-size-y 5.0
  python generate_mesh_wound.py --tier 0.5 --output 03_mesh_wound_production.k
        """
    )
    add_common_args(parser)
    parser.add_argument('--mesh-size-y', type=float, default=None,
                       help='축방향 메시 크기 (mm, 기본: 티어별 자동 결정)')
    parser.add_argument('--mesh-size-path', type=float, default=None,
                       help='경로방향 메시 크기 (mm, 기본: Y의 80%%)')
    args = parser.parse_args()

    # 로거 설정
    log = setup_logger(
        "mesh_wound",
        level=logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO,
        log_file=getattr(args, 'log_file', None),
    )

    try:
        # YAML 로드 + 검증
        config = load_config(args.config, validate=True, logger=log)

        log.info("=" * 60)
        log.info("납작 와인딩(Flat Wound) 메시 생성기 (YAML 기반)")
        log.info("=" * 60)
        log.info("설정: %s | 프로젝트: %s v%s",
                 args.config, config['metadata']['project_name'],
                 config['metadata']['version'])

        # FlatWoundDesign 생성 (YAML 기반)
        design = FlatWoundDesign.from_yaml(
            config,
            tier=args.tier,
            mesh_size_y=args.mesh_size_y,
            mesh_size_path=args.mesh_size_path
        )

        r_outer = design.r_mandrel + design.unit_cell_thickness * design.n_winds
        log.info("셀: %.0f×%.0f mm | 맨드릴 R=%.1f mm | 외곽 R=%.3f mm",
                 design.cell_width, design.cell_height, design.r_mandrel, r_outer)
        log.info("단위셀: %.1f µm | 와인딩: %d (Tier %.1f)",
                 design.unit_cell_thickness * 1000, design.n_winds, args.tier)
        log.info("경로: 반원=%d×2 직선=%d×2 → %d/바퀴 | 축=%d",
                 design.n_arc_seg, design.n_straight_seg, design.n_path, design.n_y)

        gen = FlatWoundMeshGenerator(design)

        # 출력 파일명 결정
        if args.output:
            outpath = args.output
        else:
            outdir = Path(__file__).parent
            tier_sfx = config['output_files']['mesh']['tier_suffixes'].get(
                tier_to_yaml_key(args.tier),
                tier_to_suffix(args.tier),
            )
            filename = f"{config['output_files']['mesh']['wound_prefix']}{tier_sfx}.k"
            outpath = str(outdir / filename)

        gen.write_kfile(outpath)

        log.info("완료! 출력: %s", outpath)

    except FileNotFoundError as e:
        log.error("%s", e)
        sys.exit(1)
    except (KeyError, ValueError, OSError) as e:
        log.error("예기치 않은 오류: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
