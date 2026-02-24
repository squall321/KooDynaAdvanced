"""
리튬이온 파우치 배터리 셀 — 적층형(Stacked) 메시 생성기
=======================================================
LS-DYNA R16 k-file 노드/요소/파트/세트 자동 생성

구조:
  파우치(상) → [Al집전체/NMC양극/분리막/Graphite음극/Cu집전체] × N → 파우치(하)

요소 타입:
  - 집전체, 분리막, 파우치: Shell (ELFORM=2 or 16)
  - 전극 코팅 (NMC, Graphite): Solid (ELFORM=1)

단위: mm, ton(1e3 kg), s, N, MPa, mJ

설정: battery_config.yaml 파일에서 모든 파라미터 로드
"""

import numpy as np
import os
import sys
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, TextIO, Dict, Any

from battery_utils import (
    LT as _LT, PID as _PID, MID as _MID, SID as _SID, PSET as _PSET,
    LAYER_NAMES, tier_to_yaml_key, tier_to_suffix,
    load_config, setup_logger, add_common_args,
)

logger = logging.getLogger(__name__)


# ============================================================
# 설계 파라미터
# ============================================================
@dataclass
class CellDesign:
    """배터리 셀 설계변수"""
    # 전체 치수 (mm)
    cell_width: float = 70.0    # X 방향
    cell_height: float = 140.0  # Y 방향

    # 층 두께 (mm) — 실제 µm 단위를 mm로 변환
    t_al_cc: float = 0.012       # Al 집전체 12µm
    t_cathode: float = 0.065     # NMC 양극 코팅 65µm (편면)
    t_separator: float = 0.020   # PE 분리막 20µm
    t_anode: float = 0.070       # Graphite 음극 코팅 70µm (편면)
    t_cu_cc: float = 0.008       # Cu 집전체 8µm
    t_pouch: float = 0.153       # 파우치 153µm

    # 적층 수
    n_unit_cells: int = 15       # 단위셀 반복 수

    # 메시 크기 (mm)
    mesh_size_xy: float = 2.5    # 면내 요소 크기 (프로덕션: 0.5~1.0mm)

    # 전극 코팅 두께 방향 요소 수
    n_elem_cathode_thick: int = 1  # 양극 코팅 두께 요소 수
    n_elem_anode_thick: int = 1    # 음극 코팅 두께 요소 수

    # 탭 치수
    tab_width: float = 10.0         # 탭 폭 (X방향, mm)
    tab_height: float = 8.0         # 탭 돌출 높이 (Y방향, mm)
    tab_pos_x_center: float = 17.5  # 양극(Al) 탭 X 중심 (mm)
    tab_neg_x_center: float = 52.5  # 음극(Cu) 탭 X 중심 (mm)

    # 임팩터 (솔리드 원통)
    impactor_radius: float = 7.5    # 반경 (mm)
    impactor_length: float = 80.0   # 길이 (mm)
    impactor_offset: float = 1.0    # 셀 표면으로부터 초기 간격
    impactor_n_circ: int = 24       # 원주 방향 요소 수
    impactor_n_radial: int = 4      # 반경 방향 요소 층 수

    # B12: 네일 관통 옵션
    impactor_type: str = "cylinder"  # "cylinder" (기본) 또는 "nail" (원추+원통)
    nail_tip_length: float = 3.0     # 네일 원추부 길이 (mm)
    nail_tip_radius: float = 0.5     # 네일 팁 반경 (mm, 뾰족한 정도)
    nail_shaft_radius: float = 1.5   # 네일 축부 반경 (mm)

    # 전해질 버퍼 (파우치↔적층 사이)
    t_electrolyte_buffer: float = 0.2  # 파우치 내면과 적층 사이 전해질 층 두께 (mm)

    # PCM (보호회로모듈)
    pcm_width: float = 20.0        # PCM 보드 폭 (X방향, mm)
    pcm_height: float = 3.0         # PCM 보드 돌출 높이 (Y방향, mm)
    pcm_thickness: float = 1.0      # PCM 보드 두께 (Z방향, mm)

    # 파우치 모서리 필렛
    r_fillet: float = 2.0           # 수직 모서리 필렛 반경 (mm)
    n_fillet_segments: int = 3      # 필렛 호 분할 수

    @property
    def unit_cell_thickness(self) -> float:
        """단위셀 두께: Al + 양극×2 + 분리막 + 음극×2 + Cu"""
        return (self.t_al_cc
                + self.t_cathode * 2
                + self.t_separator
                + self.t_anode * 2
                + self.t_cu_cc)

    @property
    def total_jellyroll_thickness(self) -> float:
        return self.unit_cell_thickness * self.n_unit_cells

    @property
    def total_cell_thickness(self) -> float:
        return self.total_jellyroll_thickness + self.t_pouch * 2

    @property
    def nx(self) -> int:
        return int(round(self.cell_width / self.mesh_size_xy))

    @property
    def ny(self) -> int:
        return int(round(self.cell_height / self.mesh_size_xy))

    @classmethod
    def from_yaml(cls, config: Dict[str, Any], tier: int = 0, mesh_size: float = None) -> 'CellDesign':
        """YAML 설정에서 CellDesign 인스턴스 생성
        
        Args:
            config: battery_config.yaml 파싱 결과
            tier: 티어 (-1, 0, 0.5, 1, 2)
            mesh_size: 메시 크기 오버라이드 (None이면 tier에 따라 자동 결정)
        """
        geom = config['geometry']['stacked']
        imp = config['impactor']
        
        # 티어별 UC 수
        tier_map = geom['stacking']['tier_definitions']
        tier_key = tier_to_yaml_key(tier)
        tier_def = tier_map.get(tier_key, {})
        n_uc = tier_def.get('n_cells', geom['stacking']['default_n_cells']) if isinstance(tier_def, dict) else geom['stacking']['default_n_cells']
        
        # 티어별 메시 크기 (오버라이드 없으면 자동)
        if mesh_size is None:
            if tier <= -1:
                mesh_size = 5.0
            elif tier == 0:
                mesh_size = 2.5
            else:
                mesh_size = 1.0
        
        # 기하
        cell_dim = geom['cell_dimensions']
        lt = geom['layer_thickness']
        tabs = geom['tabs']
        pcm = geom['pcm']
        fillet = geom['fillet']
        
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
        
        return cls(
            cell_width=cell_dim['width'],
            cell_height=cell_dim['height'],
            t_al_cc=lt['al_current_collector']['value'],
            t_cathode=lt['cathode_coating']['value'],
            t_separator=lt['separator']['value'],
            t_anode=lt['anode_coating']['value'],
            t_cu_cc=lt['cu_current_collector']['value'],
            t_pouch=lt['pouch']['value'],
            t_electrolyte_buffer=lt['electrolyte_buffer']['value'],
            n_unit_cells=n_uc,
            mesh_size_xy=mesh_size,
            n_elem_cathode_thick=config['mesh']['stacked']['through_thickness_elements']['cathode'],
            n_elem_anode_thick=config['mesh']['stacked']['through_thickness_elements']['anode'],
            tab_width=tabs['positive']['width'],
            tab_height=tabs['positive']['height'],
            tab_pos_x_center=tabs['positive']['x_center'],
            tab_neg_x_center=tabs['negative']['x_center'],
            pcm_width=pcm['width'],
            pcm_height=pcm['height'],
            pcm_thickness=pcm['thickness'],
            r_fillet=fillet['radius'],
            n_fillet_segments=fillet['n_segments'],
            impactor_type=impactor_type,
            impactor_radius=impactor_radius,
            impactor_length=imp_data.get('length', imp_data.get('shaft_length', 80.0)),
            impactor_offset=imp_data['offset'],
            impactor_n_circ=imp_data['mesh']['n_circumferential'],
            impactor_n_radial=imp_data['mesh']['n_radial'],
            nail_tip_length=nail_tip_length,
            nail_tip_radius=nail_tip_radius,
            nail_shaft_radius=nail_shaft_radius,
        )


# ============================================================
# Part ID 체계 — battery_utils에서 가져온 호환 별칭
# ============================================================
# PID 범위:
#   1-99:     구조 파트
#   100-199:  임팩터/지그
#   1000+:    적층별 파트 (unit_cell_idx * 100 + layer_type)

# Layer type codes (battery_utils.LT 호환)
LT_AL_CC    = _LT.AL_CC
LT_CATHODE  = _LT.CATHODE
LT_SEPARATOR = _LT.SEPARATOR
LT_ANODE    = _LT.ANODE
LT_CU_CC   = _LT.CU_CC

PID_POUCH_TOP    = _PID.POUCH_TOP
PID_POUCH_BOTTOM = _PID.POUCH_BOTTOM
PID_POUCH_SIDE   = _PID.POUCH_SIDE
PID_TAB_POS      = _PID.TAB_POS
PID_TAB_NEG      = _PID.TAB_NEG
PID_PCM_POS      = _PID.PCM_POS
PID_PCM_NEG      = _PID.PCM_NEG
PID_ELECTROLYTE  = _PID.ELECTROLYTE
PID_IMPACTOR     = _PID.IMPACTOR

# Material IDs (battery_utils.MID 호환)
MID_AL      = _MID.AL
MID_CU      = _MID.CU
MID_NMC     = _MID.NMC
MID_GRAPHITE = _MID.GRAPHITE
MID_SEPARATOR = _MID.SEPARATOR
MID_POUCH   = _MID.POUCH
MID_RIGID   = _MID.RIGID
MID_ELECTROLYTE = _MID.ELECTROLYTE
MID_PCM     = _MID.RIGID   # PCM 보드 = 강체 (FR4)

# Section IDs (battery_utils.SID 호환)
SID_SHELL_BT    = _SID.SHELL_BT
SID_SHELL_FULL  = _SID.SHELL_FULL
SID_SOLID_1PT   = _SID.SOLID_1PT
SID_SOLID_IMPACTOR = _SID.SOLID_IMPACTOR
SID_SHELL_POUCH = _SID.SHELL_POUCH
SID_SHELL_CU_CC = _SID.SHELL_CU_CC

# LAYER_NAMES — battery_utils에서 import 완료


class MeshGenerator:
    """적층형 배터리 셀 메시 생성기 (3-임시파일 스트리밍)"""

    def __init__(self, design: CellDesign):
        self.d = design
        self.next_nid = 1
        self.next_eid = 1

        # 임시파일 핸들
        self._f_nodes = None
        self._f_shells = None
        self._f_solids = None

        # 세트 추적 (메모리 최소화)
        self.part_ids = []
        self.tab_tip_rows = {'positive': [], 'negative': []}  # 탭 끝 노드행 저장
        self.tab_x_ranges: list = []  # [(x_lo, x_hi), ...] 파우치 측면 홀 생성용
        self.node_sets = {}
        self.part_sets = {}
        self.total_shells = 0
        self.total_solids = 0
        self.total_nodes = 0

    def add_node(self, x: float, y: float, z: float) -> int:
        nid = self.next_nid
        self._f_nodes.write(
            f"{nid:>8d}{x:>16.6f}{y:>16.6f}{z:>16.6f}       0       0\n")
        self.next_nid += 1
        self.total_nodes += 1
        return nid

    def add_shell(self, pid: int, n1: int, n2: int, n3: int, n4: int) -> int:
        # 퇴화 요소 방지: 고유 노드가 3개 미만이면 스킵
        if len({n1, n2, n3, n4}) < 3:
            return -1
        eid = self.next_eid
        self._f_shells.write(
            f"{eid:>8d}{pid:>8d}{n1:>8d}{n2:>8d}{n3:>8d}{n4:>8d}\n")
        self.next_eid += 1
        self.total_shells += 1
        return eid

    def add_solid(self, pid: int, nodes8: tuple) -> int:
        # 퇴화 요소 방지: 고유 노드가 4개 미만이면 스킵
        if len(set(nodes8)) < 4:
            return -1
        eid = self.next_eid
        ns = nodes8
        self._f_solids.write(
            f"{eid:>8d}{pid:>8d}"
            f"{ns[0]:>8d}{ns[1]:>8d}{ns[2]:>8d}{ns[3]:>8d}"
            f"{ns[4]:>8d}{ns[5]:>8d}{ns[6]:>8d}{ns[7]:>8d}\n")
        self.next_eid += 1
        self.total_solids += 1
        return eid

    # ----------------------------------------------------------------
    # 파우치 내면 필렛 클리핑
    # ----------------------------------------------------------------
    def _clip_to_inner_fillet(self, x: float, y: float) -> Tuple[float, float]:
        """파우치 내면 필렛 영역 밖의 노드를 필렛 호 안쪽으로 투영.

        파우치 모서리가 둥글지만 젤리롤은 직사각형이므로,
        4개 모서리에서 젤리롤이 파우치 밖으로 돌출하는 것을 방지.
        """
        d = self.d
        R = d.r_fillet
        if R <= 0:
            return x, y

        ht = d.t_pouch / 2.0
        # 파우치 내면의 유효 필렛 반경 (중앙면 - 반두께)
        Ri = R - ht
        if Ri <= 0:
            return x, y

        W, H = d.cell_width, d.cell_height
        clearance = 0.005  # 0.005mm 여유 (접촉 안정성)
        R_eff = Ri - clearance

        # 4 모서리 필렛 중심 (젤리롤 좌표계: 0..W, 0..H)
        corners = [
            (Ri, Ri,       lambda xx, yy: xx < Ri and yy < Ri),      # BL
            (W - Ri, Ri,   lambda xx, yy: xx > W - Ri and yy < Ri),  # BR
            (W - Ri, H - Ri, lambda xx, yy: xx > W - Ri and yy > H - Ri),  # TR
            (Ri, H - Ri,   lambda xx, yy: xx < Ri and yy > H - Ri), # TL
        ]

        for cx, cy, in_region in corners:
            if not in_region(x, y):
                continue
            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > R_eff and dist > 1e-12:
                # 필렛 호 안쪽으로 투영
                x = cx + R_eff * dx / dist
                y = cy + R_eff * dy / dist
            break  # 한 모서리만 해당

        return x, y

    # ----------------------------------------------------------------
    # 2D 격자 노드 생성 (xy 평면, 지정 z)
    # ----------------------------------------------------------------
    def create_plane_nodes(self, z: float) -> np.ndarray:
        """
        z 평면에 nx+1 × ny+1 격자 노드 생성.
        파우치 필렛 영역의 모서리 노드는 자동 클리핑.
        Returns: (ny+1, nx+1) 배열의 nid
        """
        nx, ny = self.d.nx, self.d.ny
        dx = self.d.cell_width / nx
        dy = self.d.cell_height / ny

        nid_grid = np.zeros((ny + 1, nx + 1), dtype=int)
        for j in range(ny + 1):
            for i in range(nx + 1):
                x = i * dx
                y = j * dy
                x, y = self._clip_to_inner_fillet(x, y)
                nid_grid[j, i] = self.add_node(x, y, z)
        return nid_grid

    # ----------------------------------------------------------------
    # 셸 레이어 생성
    # ----------------------------------------------------------------
    def create_shell_layer(self, pid: int, z: float, _thickness: float,
                           _set_name: str = None) -> np.ndarray:
        """
        z 위치에 셸 레이어 생성 (두께는 섹션에서 정의)
        Returns: 노드 그리드
        """
        nid_grid = self.create_plane_nodes(z)
        nx, ny = self.d.nx, self.d.ny
        eids = []
        for j in range(ny):
            for i in range(nx):
                n1 = nid_grid[j, i]
                n2 = nid_grid[j, i + 1]
                n3 = nid_grid[j + 1, i + 1]
                n4 = nid_grid[j + 1, i]
                eid = self.add_shell(pid, n1, n2, n3, n4)
                eids.append(eid)

        if pid not in self.part_ids:
            self.part_ids.append(pid)

        return nid_grid

    # ----------------------------------------------------------------
    # 솔리드 레이어 생성 (두 평면 노드 그리드 사이)
    # ----------------------------------------------------------------
    def create_solid_layer_between(self, pid: int,
                                   bot_grid: np.ndarray,
                                   top_grid: np.ndarray,
                                   _set_name: str = None) -> list:
        """
        bottom/top 노드 그리드 사이에 솔리드 요소 생성
        """
        nx, ny = self.d.nx, self.d.ny
        eids = []
        for j in range(ny):
            for i in range(nx):
                # bottom face: n1,n2,n3,n4 (반시계)
                n1 = bot_grid[j, i]
                n2 = bot_grid[j, i + 1]
                n3 = bot_grid[j + 1, i + 1]
                n4 = bot_grid[j + 1, i]
                # top face: n5,n6,n7,n8
                n5 = top_grid[j, i]
                n6 = top_grid[j, i + 1]
                n7 = top_grid[j + 1, i + 1]
                n8 = top_grid[j + 1, i]
                eid = self.add_solid(pid, (n1, n2, n3, n4, n5, n6, n7, n8))
                eids.append(eid)

        if pid not in self.part_ids:
            self.part_ids.append(pid)
        return eids

    # ----------------------------------------------------------------
    # 솔리드 코팅 레이어 (여러 요소 두께)
    # ----------------------------------------------------------------
    def create_solid_coating(self, pid: int, z_bot: float, z_top: float,
                             n_thick: int, bot_grid: np.ndarray = None,
                             set_name: str = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        z_bot ~ z_top 사이에 n_thick 층의 솔리드 요소 생성.
        bot_grid 제공 시 바닥면 노드 재사용.
        Returns: (bottom_grid, top_grid)
        """
        dz = (z_top - z_bot) / n_thick

        if bot_grid is None:
            bot_grid = self.create_plane_nodes(z_bot)

        current_bot = bot_grid
        for k in range(n_thick):
            z_next = z_bot + (k + 1) * dz
            top = self.create_plane_nodes(z_next)
            self.create_solid_layer_between(pid, current_bot, top, set_name)
            current_bot = top

        return bot_grid, current_bot  # 최초 바닥, 최종 상면

    # ----------------------------------------------------------------
    # 전극 탭 스트립 생성
    # ----------------------------------------------------------------
    def _create_tab_strip(self, pid: int, z: float, nid_grid: np.ndarray,
                          tab_side: str):
        """CC 층의 가장자리에서 돌출하는 탭 스트립 생성

        Args:
            pid: 파트 ID (CC 층과 동일)
            z: CC 층의 Z 좌표
            nid_grid: CC 층의 노드 그리드 (ny+1, nx+1)
            tab_side: 'positive' (Al, +Y방향) / 'negative' (Cu, -Y방향)
        """
        d = self.d
        dx = d.cell_width / d.nx

        if tab_side == 'positive':
            x_center = d.tab_pos_x_center
        else:
            x_center = d.tab_neg_x_center
        # 탭 X 범위 저장 (파우치 측면 Y-max 벽 홀 생성용)
        x_lo_tab = x_center - d.tab_width / 2
        x_hi_tab = x_center + d.tab_width / 2
        if (x_lo_tab, x_hi_tab) not in self.tab_x_ranges:
            self.tab_x_ranges.append((x_lo_tab, x_hi_tab))
        # 실제 파우치 배터리: 양극/음극 탭 모두 상단(+Y)에서 돌출
        edge_row = nid_grid[d.ny, :]   # Y=cell_height 가장자리
        y_start = d.cell_height
        dy_dir = 1.0

        # 탭 X 범위 → 격자 인덱스
        ix_start = int(round((x_center - d.tab_width / 2) / dx))
        ix_end = int(round((x_center + d.tab_width / 2) / dx))
        ix_start = max(0, min(ix_start, d.nx))
        ix_end = max(ix_start + 1, min(ix_end, d.nx))
        n_tab_cols = ix_end - ix_start

        n_tab_rows = max(2, int(round(d.tab_height / d.mesh_size_xy)))
        dy_tab = d.tab_height / n_tab_rows

        prev_row = edge_row[ix_start: ix_end + 1]  # shape: (n_tab_cols+1,)

        for row_idx in range(n_tab_rows):
            y = y_start + (row_idx + 1) * dy_tab * dy_dir
            new_nids = []
            for ii in range(ix_start, ix_end + 1):
                x = ii * dx
                nid = self.add_node(x, y, z)
                new_nids.append(nid)

            for ii in range(n_tab_cols):
                if dy_dir > 0:
                    self.add_shell(pid, prev_row[ii], prev_row[ii + 1],
                                   new_nids[ii + 1], new_nids[ii])
                else:
                    self.add_shell(pid, prev_row[ii + 1], prev_row[ii],
                                   new_nids[ii], new_nids[ii + 1])

            prev_row = np.array(new_nids, dtype=int)

        # 탭 끝 노드행 저장 (PCM 연결용)
        self.tab_tip_rows[tab_side].append((z, prev_row.copy()))

    # ----------------------------------------------------------------
    # 전체 적층 셀 생성
    # ----------------------------------------------------------------
    def build_stacked_cell(self):
        """전체 적층형 배터리 셀 메시 생성"""
        d = self.d
        z = 0.0

        # ---- 파우치 하면 (두께 건너뛰기 — 파우치 박스에서 통합 생성) ----
        print(f"  파우치 하면 두께 z={z:.4f}~{z + d.t_pouch:.4f}")
        z += d.t_pouch

        # ---- 전해질 버퍼 (하부) ----
        if d.t_electrolyte_buffer > 0:
            print(f"  전해질 버퍼 (하) z={z:.4f}~{z + d.t_electrolyte_buffer:.4f}")
            self.create_solid_coating(
                PID_ELECTROLYTE, z, z + d.t_electrolyte_buffer, 1)
            z += d.t_electrolyte_buffer

        # ---- 단위셀 적층 ----
        _prev_top_grid = None
        separator_pids = []
        al_cc_pids = []
        cu_cc_pids = []
        cathode_pids = []
        anode_pids = []

        for uc in range(d.n_unit_cells):
            base_pid = 1000 + uc * 10
            print(f"  단위셀 {uc+1}/{d.n_unit_cells}, z={z:.4f}")

            # 1) Al 집전체 (Shell) + 양극 탭
            pid_al = base_pid + LT_AL_CC
            al_grid = self.create_shell_layer(pid_al, z, d.t_al_cc,
                                               f"SET_AL_CC_{uc}")
            self._create_tab_strip(pid_al, z, al_grid, 'positive')
            al_cc_pids.append(pid_al)
            z += d.t_al_cc

            # 2) NMC 양극 코팅 (Solid) — 상면
            pid_cath = base_pid + LT_CATHODE
            z_cath_top = z + d.t_cathode
            _, _cath_top = self.create_solid_coating(
                pid_cath, z, z_cath_top, d.n_elem_cathode_thick,
                set_name=f"SET_CATHODE_{uc}")
            cathode_pids.append(pid_cath)
            z = z_cath_top

            # 3) PE 분리막 (Shell)
            pid_sep = base_pid + LT_SEPARATOR
            _sep_grid = self.create_shell_layer(pid_sep, z, d.t_separator,
                                                f"SET_SEP_{uc}")
            separator_pids.append(pid_sep)
            z += d.t_separator

            # 4) Graphite 음극 코팅 (Solid) — 하면
            pid_an = base_pid + LT_ANODE
            z_an_top = z + d.t_anode
            _, _an_top = self.create_solid_coating(
                pid_an, z, z_an_top, d.n_elem_anode_thick,
                set_name=f"SET_ANODE_{uc}")
            anode_pids.append(pid_an)
            z = z_an_top

            # 5) Cu 집전체 (Shell) + 음극 탭
            pid_cu = base_pid + LT_CU_CC
            cu_grid = self.create_shell_layer(pid_cu, z, d.t_cu_cc,
                                               f"SET_CU_CC_{uc}")
            self._create_tab_strip(pid_cu, z, cu_grid, 'negative')
            cu_cc_pids.append(pid_cu)
            z += d.t_cu_cc

        # ---- 전해질 버퍼 (상부) ----
        if d.t_electrolyte_buffer > 0:
            print(f"  전해질 버퍼 (상) z={z:.4f}~{z + d.t_electrolyte_buffer:.4f}")
            self.create_solid_coating(
                PID_ELECTROLYTE, z, z + d.t_electrolyte_buffer, 1)
            z += d.t_electrolyte_buffer

        # ---- 파우치 상면 (두께 건너뛰기 — 파우치 박스에서 통합 생성) ----
        print(f"  파우치 상면 두께 z={z:.4f}~{z + d.t_pouch:.4f}")
        z += d.t_pouch

        # ---- 파트 세트 저장 (05_contacts.k 호환 SID) ----
        self.part_sets["PSET_IMPACTOR"] = [PID_IMPACTOR]
        self.part_sets["PSET_POUCH"] = [PID_POUCH_TOP, PID_POUCH_BOTTOM,
                                          PID_POUCH_SIDE]
        self.part_sets["PSET_ALL_CELL"] = (al_cc_pids + cu_cc_pids +
                                            cathode_pids + anode_pids +
                                            separator_pids +
                                            [PID_POUCH_TOP, PID_POUCH_BOTTOM,
                                             PID_POUCH_SIDE, PID_ELECTROLYTE])
        self.part_sets["PSET_ALL_CATHODE"] = cathode_pids
        self.part_sets["PSET_ALL_ANODE"] = anode_pids
        self.part_sets["PSET_ALL_SEPARATOR"] = separator_pids
        self.part_sets["PSET_ALL_AL_CC"] = al_cc_pids
        self.part_sets["PSET_ALL_CU_CC"] = cu_cc_pids
        self.part_sets["PSET_ELECTROLYTE"] = [PID_ELECTROLYTE]
        self.part_sets["PSET_PCM"] = [PID_PCM_POS, PID_PCM_NEG]

        # ---- 파우치 육면 박스 (필렛 모서리 + 노드 공유) ----
        self._create_pouch_box(z)

        # ---- PCM 보드 ----
        self._create_pcm(z)

        # ---- 임팩터 생성 ----
        if d.impactor_type == "nail":
            self._create_nail_impactor(z)
        else:
            self._create_impactor(z)

        # ---- 경계 노드 세트 ----
        self._create_boundary_node_sets()

        print(f"\n  총 노드: {self.total_nodes:,}")
        print(f"  총 셸 요소: {self.total_shells:,}")
        print(f"  총 솔리드 요소: {self.total_solids:,}")
        print(f"  총 요소: {self.total_shells + self.total_solids:,}")
        print(f"  총 두께: {z:.4f} mm")

    # ----------------------------------------------------------------
    # PCM 보드 (보호회로모듈)
    # ----------------------------------------------------------------
    def _create_pcm(self, cell_top_z: float):
        """상단에 하나의 PCM 보드 생성 (양극/음극 탭 양쪽을 아우름)

        실제 파우치 배터리: 탭이 모두 상단에서 나오고,
        PCM 보드 1장이 양쪽 탭을 연결.
        """
        d = self.d
        z_mid = cell_top_z / 2.0

        # 양쪽 탭 팁이 없으면 스킵
        if not self.tab_tip_rows['positive'] and not self.tab_tip_rows['negative']:
            return

        # PCM 보드 X 범위: 양극 탭 좌측 ~ 음극 탭 우측을 아우름
        x_left = min(d.tab_pos_x_center, d.tab_neg_x_center) - d.tab_width / 2
        x_right = max(d.tab_pos_x_center, d.tab_neg_x_center) + d.tab_width / 2
        pcm_full_width = x_right - x_left

        y_tip = d.cell_height + d.tab_height  # 양쪽 탭 모두 상단

        pcm_z_bot = z_mid - d.pcm_thickness / 2
        pcm_z_top = z_mid + d.pcm_thickness / 2

        nx_pcm = max(2, int(round(pcm_full_width / d.mesh_size_xy)))
        nz_pcm = max(1, int(round(d.pcm_thickness / d.mesh_size_xy)))
        ny_pcm = max(1, int(round(d.pcm_height / d.mesh_size_xy)))

        dx_p = pcm_full_width / nx_pcm
        dz_p = (pcm_z_top - pcm_z_bot) / nz_pcm
        dy_p = d.pcm_height / ny_pcm

        # 솔리드 노드 (ny_pcm+1) × (nz_pcm+1) × (nx_pcm+1)
        nids = np.zeros((ny_pcm + 1, nz_pcm + 1, nx_pcm + 1), dtype=int)
        for jy in range(ny_pcm + 1):
            y = y_tip + jy * dy_p
            for jz in range(nz_pcm + 1):
                z = pcm_z_bot + jz * dz_p
                for jx in range(nx_pcm + 1):
                    x = x_left + jx * dx_p
                    nids[jy, jz, jx] = self.add_node(x, y, z)

        # PCM_POS: 양극 탭 쪽 절반, PCM_NEG: 음극 탭 쪽 절반
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
                    # 양극쪽/음극쪽 PID 분리 (EM 경로 구분)
                    pid = PID_PCM_POS if jx < ix_mid else PID_PCM_NEG
                    self.add_solid(pid, ns)

        if PID_PCM_POS not in self.part_ids:
            self.part_ids.append(PID_PCM_POS)
        if PID_PCM_NEG not in self.part_ids:
            self.part_ids.append(PID_PCM_NEG)

        # PCM 접합면 노드 세트 (탭과의 Tied Contact 용)
        contact_nids = []
        for jz in range(nz_pcm + 1):
            for jx in range(nx_pcm + 1):
                contact_nids.append(nids[0, jz, jx])
        self.node_sets["NSET_PCM_CONTACT"] = contact_nids

        print(f"  PCM 보드 (통합): X=[{x_left:.1f}~{x_right:.1f}], "
              f"Y=[{y_tip:.1f}~{y_tip + d.pcm_height:.1f}], "
              f"{nx_pcm}x{ny_pcm}x{nz_pcm} 요소")

    # ----------------------------------------------------------------
    # 파우치 육면 박스 (필렛 모서리 + 노드 공유)
    # ----------------------------------------------------------------
    def _create_pouch_box(self, cell_top_z: float):
        """파우치 6면을 하나의 연속 셸 메시로 생성

        - 상/하면: 필렛이 적용된 XY 평면 셸
        - 4개 측면: 상/하면 가장자리 노드를 공유
        - 4개 수직 모서리: 필렛 곡면 (절점 투영 방식)
        """
        d = self.d
        ht = d.t_pouch / 2.0
        R = d.r_fillet
        n_f = d.n_fillet_segments

        z_bot = ht                    # 하면 셸 중앙면 Z
        z_top = cell_top_z - ht       # 상면 셸 중앙면 Z

        # ── XY 좌표 배열 (필렛 포함) ──
        x0, x1 = -ht, d.cell_width + ht
        y0, y1 = -ht, d.cell_height + ht
        xf0, xf1 = x0 + R, x1 - R    # 필렛/직선 경계 X
        yf0, yf1 = y0 + R, y1 - R    # 필렛/직선 경계 Y

        n_str_x = max(1, int(round((xf1 - xf0) / d.mesh_size_xy)))
        n_str_y = max(1, int(round((yf1 - yf0) / d.mesh_size_xy)))

        xs = np.concatenate([
            np.linspace(x0, xf0, n_f + 1),
            np.linspace(xf0, xf1, n_str_x + 1)[1:],
            np.linspace(xf1, x1, n_f + 1)[1:]
        ])
        ys = np.concatenate([
            np.linspace(y0, yf0, n_f + 1),
            np.linspace(yf0, yf1, n_str_y + 1)[1:],
            np.linspace(yf1, y1, n_f + 1)[1:]
        ])

        ni = len(xs)   # 총 X 노드 수
        nj = len(ys)   # 총 Y 노드 수

        # 필렛 경계 인덱스
        i_fl = n_f                  # 좌측 필렛 끝 열
        i_fr = n_f + n_str_x        # 우측 필렛 시작 열
        j_ff = n_f                  # 전면 필렛 끝 행
        j_fb = n_f + n_str_y        # 후면 필렛 시작 행

        # 4개 모서리 필렛 중심
        corners = [(xf0, yf0), (xf1, yf0), (xf1, yf1), (xf0, yf1)]

        def face_xy(i, j):
            """격자 (i,j) → 필렛 투영된 (x,y) 좌표"""
            x, y = xs[i], ys[j]
            # 모서리 영역 판별
            in_left  = (i <= i_fl)
            in_right = (i >= i_fr)
            in_front = (j <= j_ff)
            in_back  = (j >= j_fb)

            if in_left and in_front:
                cx, cy = corners[0]
            elif in_right and in_front:
                cx, cy = corners[1]
            elif in_right and in_back:
                cx, cy = corners[2]
            elif in_left and in_back:
                cx, cy = corners[3]
            else:
                return x, y   # 직선 영역 — 투영 불필요

            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > R and dist > 1e-12:
                x = cx + R * dx / dist
                y = cy + R * dy / dist
            return x, y

        # ── 측면벽 Z 레벨 ──
        nz = max(2, int(round((z_top - z_bot) / d.mesh_size_xy)))
        zs = np.linspace(z_bot, z_top, nz + 1)

        # ── 둘레 인덱스 경로 (CCW, +Z 방향에서 봤을 때) ──
        perim = []
        for i in range(ni - 1):         # Bottom edge j=0
            perim.append((i, 0))
        for j in range(nj - 1):         # Right edge i=ni-1
            perim.append((ni - 1, j))
        for i in range(ni - 1, 0, -1):  # Top edge j=nj-1
            perim.append((i, nj - 1))
        for j in range(nj - 1, 0, -1):  # Left edge i=0
            perim.append((0, j))
        n_p = len(perim)

        # ── 하면 노드 (z = z_bot) ──
        bot = np.zeros((nj, ni), dtype=int)
        for j in range(nj):
            for i in range(ni):
                x, y = face_xy(i, j)
                bot[j, i] = self.add_node(x, y, z_bot)

        # ── 상면 노드 (z = z_top) ──
        top = np.zeros((nj, ni), dtype=int)
        for j in range(nj):
            for i in range(ni):
                x, y = face_xy(i, j)
                top[j, i] = self.add_node(x, y, z_top)

        # 상면 노드 ID 보존 → NSET_STACK_TOP (NSID=1002, 스웰링 BC용)
        self._pouch_top_nids = top.flatten().tolist()

        # ── 둘레 노드 링 (측면벽) ──
        rings = [np.array([bot[j, i] for i, j in perim], dtype=int)]
        for kz in range(1, nz):
            z = zs[kz]
            ring = np.zeros(n_p, dtype=int)
            for p, (i, j) in enumerate(perim):
                x, y = face_xy(i, j)
                ring[p] = self.add_node(x, y, z)
            rings.append(ring)
        rings.append(np.array([top[j, i] for i, j in perim], dtype=int))

        # ── 하면 셸 (PID_POUCH_BOTTOM) ──
        for j in range(nj - 1):
            for i in range(ni - 1):
                n1, n2 = bot[j, i], bot[j, i + 1]
                n3, n4 = bot[j + 1, i + 1], bot[j + 1, i]
                if len({n1, n2, n3, n4}) >= 3:
                    self.add_shell(PID_POUCH_BOTTOM, n1, n2, n3, n4)
        if PID_POUCH_BOTTOM not in self.part_ids:
            self.part_ids.append(PID_POUCH_BOTTOM)

        # ── 상면 셸 (PID_POUCH_TOP) ──
        for j in range(nj - 1):
            for i in range(ni - 1):
                n1, n2 = top[j, i], top[j, i + 1]
                n3, n4 = top[j + 1, i + 1], top[j + 1, i]
                if len({n1, n2, n3, n4}) >= 3:
                    self.add_shell(PID_POUCH_TOP, n1, n2, n3, n4)
        if PID_POUCH_TOP not in self.part_ids:
            self.part_ids.append(PID_POUCH_TOP)

        # ── 측면벽 셸 (PID_POUCH_SIDE) ──
        # Y-max 벽(j=nj-1)에서 탭 통과 X 범위는 구멍으로 남김
        tab_x_ranges = self.tab_x_ranges
        for kz in range(nz):
            rb = rings[kz]
            rt = rings[kz + 1]
            for p in range(n_p):
                pn = (p + 1) % n_p
                i_p,  j_p  = perim[p]
                i_pn, j_pn = perim[pn]
                if j_p == nj - 1 and j_pn == nj - 1 and tab_x_ranges:
                    x_p  = face_xy(i_p,  j_p )[0]
                    x_pn = face_xy(i_pn, j_pn)[0]
                    x_lo_seg = min(x_p, x_pn)
                    x_hi_seg = max(x_p, x_pn)
                    if any(x_lo_seg < xh and x_hi_seg > xl
                           for xl, xh in tab_x_ranges):
                        continue  # 탭 통과 영역 — 측면벽 구멍
                self.add_shell(PID_POUCH_SIDE, rb[p], rb[pn], rt[pn], rt[p])
        if PID_POUCH_SIDE not in self.part_ids:
            self.part_ids.append(PID_POUCH_SIDE)

        print(f"  파우치 박스: {ni}×{nj} 면, {nz} 측벽층, "
              f"R_fillet={R:.1f}mm, n_fillet={n_f}")

    # ----------------------------------------------------------------
    # 임팩터 (솔리드 원통 — O-grid hex)
    # ----------------------------------------------------------------
    def _create_impactor(self, cell_top_z: float):
        """측면 임팩터 — 솔리드 원통 (Y축 방향, hex 요소)"""
        d = self.d
        R = d.impactor_radius
        L = d.impactor_length

        cx = d.cell_width + d.impactor_offset + R
        cy = d.cell_height / 2.0
        cz = cell_top_z / 2.0

        n_circ = d.impactor_n_circ
        n_radial = d.impactor_n_radial
        n_axial = max(4, int(round(L / d.mesh_size_xy)))

        dr = R / n_radial
        dy = L / n_axial
        dtheta = 2.0 * np.pi / n_circ

        # 노드: 축 중심선 + 반경 링
        center_nids = np.zeros(n_axial + 1, dtype=int)
        ring_nids = np.zeros((n_axial + 1, n_radial, n_circ), dtype=int)

        for j in range(n_axial + 1):
            y = cy - L / 2 + j * dy
            center_nids[j] = self.add_node(cx, y, cz)
            for k in range(n_radial):
                r = (k + 1) * dr
                for i in range(n_circ):
                    theta = i * dtheta
                    x = cx - r * np.cos(theta)
                    z = cz + r * np.sin(theta)
                    ring_nids[j, k, i] = self.add_node(x, y, z)

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
                self.add_solid(pid, ns)

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
                    self.add_solid(pid, ns)

        self.part_ids.append(pid)

        # 임팩터 중심축 노드 세트 (처방운동 BC용)
        self.node_sets["NSET_IMPACTOR_CENTER"] = list(center_nids)

    # ----------------------------------------------------------------
    # 네일 임팩터 (B12: 원추 팁 + 원통 축)
    # ----------------------------------------------------------------
    def _create_nail_impactor(self, cell_top_z: float):
        """네일 관통 임팩터 — 원추 팁 + 원통 축 (X방향 관통)
        
        네일 구조:
          상단: 원통 축 (shaft_radius, shaft_length)
          하단: 원추 팁 (shaft_radius → tip_radius, tip_length)
          총 길이 = nail_tip_length + (impactor_length - nail_tip_length)
        
        관통 방향: -X (셀 측면에서 중심 방향)
        """
        d = self.d
        R_shaft = d.nail_shaft_radius
        R_tip = d.nail_tip_radius
        tip_len = d.nail_tip_length
        total_len = d.impactor_radius * 2  # 네일 총 길이 (원통 반경 대신 사용)
        shaft_len = total_len - tip_len

        # 네일 중심축 위치
        cx_start = d.cell_width + d.impactor_offset  # 팁 끝 X
        cy = d.cell_height / 2.0
        cz = cell_top_z / 2.0

        n_circ = d.impactor_n_circ
        n_radial = max(2, d.impactor_n_radial // 2)
        n_shaft = max(4, int(round(shaft_len / d.mesh_size_xy)))
        n_tip = max(3, int(round(tip_len / (d.mesh_size_xy * 0.5))))

        _n_total = n_shaft + n_tip
        dtheta = 2.0 * np.pi / n_circ

        # 각 축방향 슬라이스의 반경과 X 위치
        slice_x = []
        slice_r = []

        # 팁 부분: cx_start → cx_start + tip_len, R: tip_radius → shaft_radius
        for j in range(n_tip + 1):
            frac = j / n_tip
            x = cx_start + frac * tip_len
            r = R_tip + frac * (R_shaft - R_tip)
            slice_x.append(x)
            slice_r.append(r)

        # 축 부분: 이어서
        for j in range(1, n_shaft + 1):
            frac = j / n_shaft
            x = cx_start + tip_len + frac * shaft_len
            slice_x.append(x)
            slice_r.append(R_shaft)

        n_slices = len(slice_x)  # n_total + 1

        # 노드 생성
        center_nids = np.zeros(n_slices, dtype=int)
        ring_nids = np.zeros((n_slices, n_radial, n_circ), dtype=int)

        for j in range(n_slices):
            x = slice_x[j]
            center_nids[j] = self.add_node(x, cy, cz)
            R_local = slice_r[j]
            dr = R_local / n_radial
            for k in range(n_radial):
                r = (k + 1) * dr
                for i in range(n_circ):
                    theta = i * dtheta
                    y = cy + r * np.cos(theta)
                    z = cz + r * np.sin(theta)
                    ring_nids[j, k, i] = self.add_node(x, y, z)

        pid = PID_IMPACTOR

        for j in range(n_slices - 1):
            # 내부 wedge (중심 → 첫 링)
            for i in range(n_circ):
                i_next = (i + 1) % n_circ
                ns = (
                    center_nids[j],
                    ring_nids[j, 0, i],
                    ring_nids[j, 0, i_next],
                    center_nids[j],
                    center_nids[j + 1],
                    ring_nids[j + 1, 0, i],
                    ring_nids[j + 1, 0, i_next],
                    center_nids[j + 1],
                )
                self.add_solid(pid, ns)

            # 외부 hex 링
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
                    self.add_solid(pid, ns)

        self.part_ids.append(pid)
        self.node_sets["NSET_IMPACTOR_CENTER"] = list(center_nids)

    # ----------------------------------------------------------------
    # 경계 노드 세트
    # ----------------------------------------------------------------
    def _create_boundary_node_sets(self):
        """하면 고정 노드 — 파우치 하면 가장자리 직접 계산"""
        d = self.d
        nx, ny = d.nx, d.ny
        # 파우치 하면(z=0)의 첫 번째 평면 노드 ID: 1 ~ (nx+1)*(ny+1)
        # 가장자리만 선택
        bottom_nids = []
        for j in range(ny + 1):
            for i in range(nx + 1):
                if i == 0 or i == nx or j == 0 or j == ny:
                    nid = 1 + j * (nx + 1) + i  # 첫 평면의 노드 ID
                    bottom_nids.append(nid)

        self.node_sets["NSET_FIX_BOTTOM_EDGE"] = bottom_nids

        # 파우치 상면 노드 (스웰링 BC: BOUNDARY_PRESCRIBED_MOTION_SET NSID=1002)
        if hasattr(self, "_pouch_top_nids") and self._pouch_top_nids:
            self.node_sets["NSET_STACK_TOP"] = self._pouch_top_nids

    # ================================================================
    # k-file 출력 (스트리밍 — 3 pass: nodes, shells, solids)
    # ================================================================
    def write_kfile(self, filepath: str):
        """k-file 출력: 3개 임시파일에 스트리밍 → 합치기"""
        import shutil
        print(f"\n  k-file 쓰기: {filepath}")
        
        tmpdir = os.path.dirname(os.path.abspath(filepath))
        tmp_nodes = os.path.join(tmpdir, "_tmp_nodes.k")
        tmp_shells = os.path.join(tmpdir, "_tmp_shells.k")
        tmp_solids = os.path.join(tmpdir, "_tmp_solids.k")
        
        # 임시파일 열기
        self._f_nodes = open(tmp_nodes, 'w', encoding='utf-8')
        self._f_shells = open(tmp_shells, 'w', encoding='utf-8')
        self._f_solids = open(tmp_solids, 'w', encoding='utf-8')
        
        # 리셋
        self.next_nid = 1
        self.next_eid = 1
        self.total_nodes = 0
        self.total_shells = 0
        self.total_solids = 0
        self.part_ids = []
        
        # 빌드 (3개 파일에 동시 스트리밍)
        print("  메시 생성 중 (스트리밍)...")
        self.build_stacked_cell()
        
        # 임시파일 닫기
        self._f_nodes.close()
        self._f_shells.close()
        self._f_solids.close()
        
        # 합치기
        print("  파일 합치기...")
        with open(filepath, 'w', encoding='utf-8') as fout:
            fout.write("*KEYWORD\n")
            fout.write("*TITLE\n")
            fout.write("Stacked Li-ion Pouch Cell Mesh - Auto Generated\n")
            
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
        
        # 임시파일 삭제
        for tmp in [tmp_nodes, tmp_shells, tmp_solids]:
            os.remove(tmp)
        
        fsize = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  파일 크기: {fsize:.1f} MB")

    def _get_part_name(self, pid: int) -> str:
        """PID → 명확한 파트 이름"""
        if pid == PID_IMPACTOR:
            return "Impactor_Solid"
        if pid == PID_ELECTROLYTE:
            return "Electrolyte_Buffer_Solid"
        if pid == PID_PCM_POS:
            return "PCM_Positive_Solid"
        if pid == PID_PCM_NEG:
            return "PCM_Negative_Solid"
        if pid == PID_POUCH_TOP:
            return "Pouch_Top_Shell"
        if pid == PID_POUCH_BOTTOM:
            return "Pouch_Bottom_Shell"
        if pid == PID_POUCH_SIDE:
            return "Pouch_Side_Shell"
        if pid == PID_TAB_POS:
            return "Tab_Positive_Al"
        if pid == PID_TAB_NEG:
            return "Tab_Negative_Cu"
        # 적층별 파트 (1000+)
        uc_idx = (pid - 1000) // 10
        lt = pid % 10
        base_name = LAYER_NAMES.get(lt, f"Unknown_{lt}")
        elem = "Shell" if lt in (LT_AL_CC, LT_CU_CC, LT_SEPARATOR) else "Solid"
        return f"{base_name}_UC{uc_idx:02d}_{elem}"

    def _write_parts(self, f: TextIO):
        """*PART 카드: PID, SECID, MID, EOSID, HGID, GRAV, ADPOPT, TMID"""
        f.write("$\n$ ============ PARTS ============\n$\n")

        for pid in sorted(self.part_ids):
            sid, mid, tmid, eosid = self._get_part_properties(pid)
            name = self._get_part_name(pid)
            f.write("*PART\n")
            f.write(f"{name}\n")
            eos_str = f"{eosid:>10d}" if eosid else f"{'':>10s}"
            f.write(f"{pid:>10d}{sid:>10d}{mid:>10d}{eos_str}"
                    f"{'':>10s}{'':>10s}{'':>10s}{tmid:>10d}\n")

    def _get_part_properties(self, pid: int) -> Tuple[int, int, int, int]:
        """PID → (SID, MID, TMID, EOSID) 매핑
        EOSID: 셸 요소는 EOS 불필요 → 0 (Al/Cu CC 포함)
        솔리드 요소로 변경 시 EOS_GRUNEISEN 활성화 + EOSID 지정"""
        if pid == PID_IMPACTOR:
            return SID_SOLID_IMPACTOR, MID_RIGID, 0, 0
        if pid == PID_ELECTROLYTE:
            return SID_SOLID_1PT, MID_ELECTROLYTE, 108, 0
        if pid in (PID_PCM_POS, PID_PCM_NEG):
            return SID_SOLID_IMPACTOR, MID_PCM, 0, 0
        if pid in (PID_POUCH_TOP, PID_POUCH_BOTTOM, PID_POUCH_SIDE):
            return SID_SHELL_POUCH, MID_POUCH, 106, 0
        if pid in (PID_TAB_POS,):
            return SID_SHELL_BT, MID_AL, 101, 0
        if pid in (PID_TAB_NEG,):
            return SID_SHELL_CU_CC, MID_CU, 102, 0

        # 적층별 파트 (1000+)
        layer_type = pid % 10
        if layer_type == LT_AL_CC:
            return SID_SHELL_BT, MID_AL, 101, 0
        elif layer_type == LT_CATHODE:
            return SID_SOLID_1PT, MID_NMC, 103, 0
        elif layer_type == LT_SEPARATOR:
            return SID_SHELL_FULL, MID_SEPARATOR, 105, 0
        elif layer_type == LT_ANODE:
            return SID_SOLID_1PT, MID_GRAPHITE, 104, 0
        elif layer_type == LT_CU_CC:
            return SID_SHELL_CU_CC, MID_CU, 102, 0
        else:
            return SID_SHELL_BT, MID_AL, 0, 0

    def _write_sections(self, f: TextIO):
        """섹션 정의"""
        d = self.d
        f.write("$\n$ ============ SECTIONS ============\n$\n")

        # Shell BT (ELFORM=2) — 집전체, 파우치
        f.write("*SECTION_SHELL\n")
        f.write(f"${'SID':>9s}{'ELFORM':>10s}{'SHRF':>10s}{'NIP':>10s}"
                f"{'PROPT':>10s}{'QR/IRID':>10s}{'ICOMP':>10s}{'SETYP':>10s}\n")
        f.write(f"{SID_SHELL_BT:>10d}{2:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"${'T1':>9s}{'T2':>10s}{'T3':>10s}{'T4':>10s}\n")
        f.write(f"{d.t_al_cc:>10.4f}{d.t_al_cc:>10.4f}"
                f"{d.t_al_cc:>10.4f}{d.t_al_cc:>10.4f}\n")

        # Shell 완전적분 (ELFORM=16) — 분리막
        f.write("*SECTION_SHELL\n")
        f.write(f"{SID_SHELL_FULL:>10d}{16:>10d}{0.833:>10.3f}{5:>10d}"
                f"{1:>10d}{0:>10d}{0:>10d}{1:>10d}\n")
        f.write(f"{d.t_separator:>10.4f}{d.t_separator:>10.4f}"
                f"{d.t_separator:>10.4f}{d.t_separator:>10.4f}\n")

        # Solid 1-point (ELFORM=1) — 전극 코팅
        f.write("*SECTION_SOLID\n")
        f.write(f"${'SID':>9s}{'ELFORM':>10s}\n")
        f.write(f"{SID_SOLID_1PT:>10d}{1:>10d}\n")

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

        # Solid Impactor (ELFORM=1)
        f.write("$ Impactor solid section\n")
        f.write("*SECTION_SOLID\n")
        f.write(f"{SID_SOLID_IMPACTOR:>10d}{1:>10d}\n")

    def _write_node_sets(self, f: TextIO):
        """노드 세트 출력 — 고정 SID 매핑 (06_boundary_loads.k 호환)"""
        f.write("$\n$ ============ NODE SETS ============\n$\n")
        # 고정 SID 매핑: boundary_loads.k가 참조하는 순서
        FIXED_SID = {
            "NSET_FIX_BOTTOM_EDGE": 1,
            "NSET_IMPACTOR_CENTER": 2,
            "NSET_STACK_TOP":       1002,
        }
        next_sid = max(FIXED_SID.values()) + 1
        # 고정 SID 세트 먼저 출력 (SID 순서)
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
                chunk = nids[i:i+8]
                line = "".join(f"{n:>10d}" for n in chunk)
                f.write(line + "\n")
        # 나머지 세트 자동 SID
        for name, nids in self.node_sets.items():
            if name in FIXED_SID:
                continue
            if len(nids) == 0:
                continue
            f.write(f"*SET_NODE_LIST_TITLE\n{name}\n")
            f.write(f"{next_sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(nids), 8):
                chunk = nids[i:i+8]
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
            "PSET_PCM":           109,
        }
        next_sid = max(FIXED_SID.values()) + 1
        # 고정 SID 먼저 (SID 순서)
        for name in sorted(FIXED_SID, key=lambda n: FIXED_SID[n]):
            if name not in self.part_sets:
                continue
            pids = self.part_sets[name]
            sid = FIXED_SID[name]
            f.write(f"*SET_PART_LIST_TITLE\n{name}\n")
            f.write(f"{sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(pids), 8):
                chunk = pids[i:i+8]
                line = "".join(f"{p:>10d}" for p in chunk)
                f.write(line + "\n")
        # 나머지 자동 SID
        for name, pids in self.part_sets.items():
            if name in FIXED_SID:
                continue
            f.write(f"*SET_PART_LIST_TITLE\n{name}\n")
            f.write(f"{next_sid:>10d}{0.0:>10.1f}{0.0:>10.1f}"
                    f"{0.0:>10.1f}{0.0:>10.1f}\n")
            for i in range(0, len(pids), 8):
                chunk = pids[i:i+8]
                line = "".join(f"{p:>10d}" for p in chunk)
                f.write(line + "\n")
            next_sid += 1


# ============================================================
# 메인 실행
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="적층형 배터리 메시 생성기 (YAML 설정 기반)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_mesh_stacked.py --config battery_config.yaml --tier 0
  python generate_mesh_stacked.py --tier -1 --mesh-size 5.0
  python generate_mesh_stacked.py --tier 0.5 --output 02_mesh_stacked_production.k
        """
    )
    add_common_args(parser)
    parser.add_argument('--mesh-size', type=float, default=None,
                       help='메시 크기 (mm, 기본: 티어별 자동 결정)')
    args = parser.parse_args()

    # 로거 설정
    log = setup_logger(
        "mesh_stacked",
        level=logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO,
        log_file=getattr(args, 'log_file', None),
    )

    try:
        # YAML 로드 + 검증
        config = load_config(args.config, validate=True, logger=log)

        log.info("=" * 60)
        log.info("적층형 배터리 메시 생성기 (YAML 기반)")
        log.info("=" * 60)
        log.info("설정: %s | 프로젝트: %s v%s",
                 args.config,
                 config['metadata']['project_name'],
                 config['metadata']['version'])

        # CellDesign 생성 (YAML 기반)
        design = CellDesign.from_yaml(config, tier=args.tier, mesh_size=args.mesh_size)

        log.info("셀 크기: %.1f×%.1f×%.3f mm",
                 design.cell_width, design.cell_height, design.total_cell_thickness)
        log.info("단위셀 두께: %.1f µm | 적층: %d (Tier %.1f)",
                 design.unit_cell_thickness * 1000, design.n_unit_cells, args.tier)
        log.info("메시 크기: %.1f mm | 면내: %d×%d",
                 design.mesh_size_xy, design.nx, design.ny)

        gen = MeshGenerator(design)

        # 출력 파일명 결정
        if args.output:
            outpath = args.output
        else:
            outdir = Path(__file__).parent
            tier_sfx = config['output_files']['mesh']['tier_suffixes'].get(
                f"tier_{str(args.tier).replace('.', '_').replace('-', 'minus')}",
                tier_to_suffix(args.tier),
            )
            filename = f"{config['output_files']['mesh']['stacked_prefix']}{tier_sfx}.k"
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
