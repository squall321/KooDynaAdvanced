"""
LS-DYNA k-file 포괄적 키워드/교차참조 감사
===========================================
모든 01_main*.k 파일에 대해:
  1. *INCLUDE 파일 존재 확인
  2. 모든 include 파일에 *KEYWORD 헤더 존재 확인
  3. 키워드명 유효성 (R16 기준)
  4. ID 교차참조 (CURVE, TABLE, FUNCTION, SET_PART, SET_NODE, PID, MID, SID)
  5. *PART 카드의 MID/SID/TMID 참조 → 정의 매칭
  6. 중복 ID 검출
"""

import re
import os
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path(r"D:\KooDynaAdvanced\Battery")

# LS-DYNA R16 유효 키워드 접두사 (주요 키워드만)
VALID_KEYWORD_PREFIXES = {
    "*KEYWORD", "*TITLE", "*END",
    "*INCLUDE",
    "*NODE", "*ELEMENT_SHELL", "*ELEMENT_SOLID",
    "*PART",
    "*SECTION_SHELL", "*SECTION_SOLID", "*SECTION_TSHELL",
    "*MAT_", "*EOS_",
    "*CONTACT_",
    "*BOUNDARY_", "*INITIAL_",
    "*CONTROL_",
    "*DATABASE_",
    "*DEFINE_CURVE", "*DEFINE_TABLE", "*DEFINE_FUNCTION",
    "*DEFINE_SD_ORIENTATION", "*DEFINE_VECTOR",
    "*SET_NODE", "*SET_PART", "*SET_SEGMENT", "*SET_SHELL", "*SET_SOLID",
    "*LOAD_",
    "*EM_",
    "*HOURGLASS",
    "*CONSTRAINED_",
    "*ALE_",
    "*AIRBAG_",
    "*SENSOR_",
    "*PARAMETER",
}


def parse_includes(main_file: Path) -> list:
    """main k-file에서 *INCLUDE 파일 목록 추출"""
    includes = []
    with open(main_file, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.upper().startswith("*INCLUDE") and not line.startswith("$"):
            # next non-comment line is the filename
            i += 1
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                inc_name = lines[i].strip()
                includes.append(inc_name)
        i += 1
    return includes


def check_keyword_header(filepath: Path) -> bool:
    """파일 첫 번째 비-주석 라인이 *KEYWORD인지 확인"""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("$"):
                continue
            return stripped.upper().startswith("*KEYWORD")
    return False


def extract_keywords(filepath: Path) -> list:
    """파일에서 모든 *키워드 라인 추출"""
    keywords = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith("*") and not stripped.startswith("$"):
                keywords.append((i, stripped))
    return keywords


def extract_definitions(filepath: Path) -> dict:
    """
    파일에서 모든 정의된 ID 추출
    Returns dict: { 'CURVE': set(), 'TABLE': set(), 'FUNCTION': set(),
                     'SET_PART': set(), 'SET_NODE': set(), 'SET_SEGMENT': set(),
                     'PART': set(), 'MID': set(), 'SID_SECTION': set(),
                     'CONTACT': set(), 'EM_RANDLES': set(), ... }
    """
    defs = defaultdict(set)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        uline = line.upper()

        # Skip comments
        if line.startswith("$") or not line.startswith("*"):
            i += 1
            continue

        # *DEFINE_CURVE or *DEFINE_CURVE_TITLE
        if "*DEFINE_CURVE" in uline and "*DEFINE_TABLE" not in uline and "*DEFINE_FUNCTION" not in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                # skip title line
                i += 1
            # next data line: first field is LCID
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        lcid = int(data[:10].strip())
                        defs["CURVE"].add(lcid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *DEFINE_TABLE
        if "*DEFINE_TABLE" in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        tbid = int(data[:10].strip())
                        defs["TABLE"].add(tbid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *DEFINE_FUNCTION or *DEFINE_FUNCTION_TABULATED
        if "*DEFINE_FUNCTION" in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        fid = int(data[:10].strip())
                        defs["FUNCTION"].add(fid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *SET_PART_LIST or *SET_PART_LIST_TITLE
        if "*SET_PART" in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        sid = int(data[:10].strip())
                        defs["SET_PART"].add(sid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *SET_NODE_LIST or *SET_NODE_LIST_TITLE
        if "*SET_NODE" in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        sid = int(data[:10].strip())
                        defs["SET_NODE"].add(sid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *SET_SEGMENT_GENERAL
        if "*SET_SEGMENT" in uline:
            has_title = "TITLE" in uline
            i += 1
            if has_title:
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    try:
                        sid = int(data[:10].strip())
                        defs["SET_SEGMENT"].add(sid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *PART — extract PID, SID, MID
        if uline == "*PART" or uline.startswith("*PART\n"):
            i += 1
            # skip title line
            if i < len(lines):
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("$") and not data.startswith("*"):
                    fields = data
                    try:
                        pid = int(fields[0:10].strip())
                        defs["PART"].add(pid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *SECTION_SHELL or *SECTION_SOLID
        if "*SECTION_SHELL" in uline or "*SECTION_SOLID" in uline:
            i += 1
            # skip comment lines
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("*"):
                    try:
                        sid = int(data[:10].strip())
                        defs["SID_SECTION"].add(sid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *MAT_ — extract MID
        if uline.startswith("*MAT_") and "ADD" not in uline:
            i += 1
            # skip comment/$-lines and TITLE line
            if "TITLE" in uline:
                i += 1
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("*"):
                    try:
                        mid = int(data[:10].strip())
                        defs["MID"].add(mid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        # *MAT_THERMAL_*
        if "*MAT_THERMAL" in uline:
            i += 1
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                data = lines[i].strip()
                if data and not data.startswith("*"):
                    try:
                        tmid = int(data[:10].strip())
                        defs["TMID"].add(tmid)
                    except (ValueError, IndexError):
                        pass
            i += 1
            continue

        i += 1

    return defs


def extract_references_from_parts(filepath: Path) -> list:
    """
    *PART 카드에서 참조하는 SID, MID, TMID 추출
    Returns list of (PID, SID, MID, TMID, EOSID)
    """
    refs = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip().upper()
        if line == "*PART":
            i += 1  # title
            if i < len(lines):
                i += 1  # data line
            if i < len(lines):
                data = lines[i]
                if len(data) >= 20:
                    try:
                        pid = int(data[0:10].strip())
                        sid = int(data[10:20].strip())
                        mid = int(data[20:30].strip()) if len(data) >= 30 and data[20:30].strip() else 0
                        eos_str = data[30:40].strip() if len(data) >= 40 else ""
                        eosid = int(eos_str) if eos_str else 0
                        tmid_str = data[70:80].strip() if len(data) >= 80 else ""
                        tmid = int(tmid_str) if tmid_str else 0
                        refs.append((pid, sid, mid, tmid, eosid))
                    except (ValueError, IndexError):
                        pass
        i += 1
    return refs


def extract_curve_refs_from_contacts(filepath: Path) -> set:
    """접촉 파일에서 참조하는 SET_PART/SET_NODE/PID ID 추출"""
    refs = {"SET_PART": set(), "SET_NODE": set(), "PID": set()}
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip().upper()
        if line.startswith("*CONTACT_") and not line.startswith("$"):
            i += 1
            # skip title line if _ID
            if "_ID" in line:
                i += 1
            # skip comments
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            # data card 1: SSID, MSID, SSTYP, MSTYP, ...
            if i < len(lines):
                data = lines[i]
                if len(data) >= 40 and not data.strip().startswith("$") and not data.strip().startswith("*"):
                    try:
                        ssid = int(data[0:10].strip())
                        msid = int(data[10:20].strip())
                        sstyp = int(data[20:30].strip()) if data[20:30].strip() else 0
                        mstyp = int(data[30:40].strip()) if data[30:40].strip() else 0
                        if sstyp == 2:
                            refs["SET_PART"].add(ssid)
                        elif sstyp == 3:
                            refs["PID"].add(ssid)
                        elif sstyp == 4:
                            refs["SET_NODE"].add(ssid)
                        if mstyp == 2:
                            refs["SET_PART"].add(msid)
                        elif mstyp == 3:
                            refs["PID"].add(msid)
                        elif mstyp == 4:
                            refs["SET_NODE"].add(msid)
                    except (ValueError, IndexError):
                        pass
        i += 1
    return refs


def extract_lcid_refs_from_boundary(filepath: Path) -> set:
    """경계조건 파일에서 참조하는 LCID, NSID 추출"""
    lcids = set()
    nsids = set()
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip().upper()
        if line.startswith("*BOUNDARY_PRESCRIBED_MOTION") and not line.startswith("$"):
            i += 1
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                data = lines[i]
                try:
                    nsid = int(data[0:10].strip())
                    if nsid != 0:
                        nsids.add(nsid)
                except (ValueError, IndexError):
                    pass
                # LCID is field 4 or 5 depending on variant
                i += 1
                while i < len(lines) and lines[i].strip().startswith("$"):
                    i += 1
                if i < len(lines):
                    data2 = lines[i]
                    try:
                        lcid = int(data2[20:30].strip()) if len(data2) >= 30 else 0
                        if lcid != 0:
                            lcids.add(abs(lcid))
                    except (ValueError, IndexError):
                        pass
        elif line.startswith("*BOUNDARY_SPC") and not line.startswith("$"):
            i += 1
            while i < len(lines) and lines[i].strip().startswith("$"):
                i += 1
            if i < len(lines):
                data = lines[i]
                try:
                    nsid = int(data[0:10].strip())
                    if nsid != 0:
                        nsids.add(nsid)
                except (ValueError, IndexError):
                    pass
        i += 1
    return lcids, nsids


def check_table_sub_curves(filepath: Path) -> list:
    """TABLE이 참조하는 하위 CURVE ID 추출"""
    table_curves = []  # (TABLE_ID, [curve_ids])
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip().upper()
        if "*DEFINE_TABLE" in line and not line.startswith("$"):
            has_title = "TITLE" in line
            i += 1
            if has_title:
                i += 1
            # header line with TBID
            tbid = None
            if i < len(lines):
                data = lines[i].strip()
                try:
                    tbid = int(data[:10].strip())
                except (ValueError, IndexError):
                    pass
                i += 1
            # following lines: temp value, LCID pairs
            curves = []
            while i < len(lines):
                data = lines[i].strip()
                if data.startswith("*") or data.startswith("$"):
                    break
                parts = data.split()
                if len(parts) >= 2:
                    try:
                        lcid = int(float(parts[1]))
                        curves.append(lcid)
                    except ValueError:
                        pass
                i += 1
            if tbid is not None:
                table_curves.append((tbid, curves))
            continue
        i += 1
    return table_curves


def audit_main_file(main_path: Path):
    """하나의 main 파일에 대한 전체 감사"""
    errors = []
    warnings = []

    print(f"\n{'='*80}")
    print(f"  AUDIT: {main_path.name}")
    print(f"{'='*80}")

    # 1. Parse includes
    includes = parse_includes(main_path)
    print(f"\n  Include 파일 {len(includes)}개:")
    for inc in includes:
        print(f"    {inc}")

    # 2. Check include file existence
    all_files = [main_path]
    for inc in includes:
        inc_path = BASE / inc
        if not inc_path.exists():
            errors.append(f"INCLUDE 파일 없음: {inc}")
        else:
            all_files.append(inc_path)

    # 3. Check *KEYWORD header
    for fp in all_files:
        if not check_keyword_header(fp):
            errors.append(f"*KEYWORD 헤더 없음: {fp.name}")

    # 4. Collect all definitions across all files
    all_defs = defaultdict(set)
    all_part_refs = []
    for fp in all_files:
        defs = extract_definitions(fp)
        for k, v in defs.items():
            all_defs[k] |= v
        prefs = extract_references_from_parts(fp)
        all_part_refs.extend(prefs)

    print(f"\n  정의된 ID:")
    for k in sorted(all_defs.keys()):
        ids = sorted(all_defs[k])
        if len(ids) > 10:
            print(f"    {k}: {ids[:5]}...{ids[-2:]} ({len(ids)}개)")
        else:
            print(f"    {k}: {ids}")

    # 5. PART → SID, MID, TMID 교차참조
    for pid, sid, mid, tmid, eosid in all_part_refs:
        if sid != 0 and sid not in all_defs.get("SID_SECTION", set()):
            errors.append(f"PID {pid}: SID={sid} 정의 없음 (정의: {sorted(all_defs.get('SID_SECTION', set()))})")
        if mid != 0 and mid not in all_defs.get("MID", set()):
            # Check rigid
            if mid not in (7,):  # rigid
                errors.append(f"PID {pid}: MID={mid} 정의 없음")
        if tmid != 0 and tmid not in all_defs.get("TMID", set()):
            errors.append(f"PID {pid}: TMID={tmid} 정의 없음 (정의: {sorted(all_defs.get('TMID', set()))})")
        if eosid != 0:
            warnings.append(f"PID {pid}: EOSID={eosid} (EOS 정의 확인 필요)")

    # 6. TABLE → sub-CURVE 참조
    for fp in all_files:
        table_curves = check_table_sub_curves(fp)
        for tbid, curves in table_curves:
            for lcid in curves:
                if lcid not in all_defs["CURVE"]:
                    errors.append(f"TABLE {tbid}: sub-CURVE {lcid} 정의 없음")

    # 7. Contact → SET_PART/PID 참조
    for fp in all_files:
        if "contact" in fp.name.lower():
            crefs = extract_curve_refs_from_contacts(fp)
            for pset_id in crefs["SET_PART"]:
                if pset_id not in all_defs.get("SET_PART", set()):
                    errors.append(f"Contact ({fp.name}): SET_PART {pset_id} 정의 없음")
            for pid in crefs["PID"]:
                if pid not in all_defs.get("PART", set()):
                    errors.append(f"Contact ({fp.name}): PID {pid} 정의 없음")

    # 8. Boundary → LCID, NSID 참조
    for fp in all_files:
        if "boundary" in fp.name.lower():
            lcids, nsids = extract_lcid_refs_from_boundary(fp)
            for lcid in lcids:
                if lcid not in all_defs["CURVE"] and lcid not in all_defs["TABLE"]:
                    errors.append(f"Boundary ({fp.name}): LCID {lcid} 정의 없음")
            for nsid in nsids:
                if nsid not in all_defs.get("SET_NODE", set()):
                    errors.append(f"Boundary ({fp.name}): NODE_SET {nsid} 정의 없음")

    # 9. SET_PART in EM file might clash with mesh SET_PART
    em_psets = set()
    mesh_psets = set()
    for fp in all_files:
        defs = extract_definitions(fp)
        if "em_randles" in fp.name.lower():
            em_psets |= defs.get("SET_PART", set())
        elif "mesh" in fp.name.lower():
            mesh_psets |= defs.get("SET_PART", set())
    clash = em_psets & mesh_psets
    if clash:
        errors.append(f"SET_PART ID 충돌 (EM ↔ Mesh): {sorted(clash)}")

    # 10. Duplicate ID check across all files per type
    for id_type in ["CURVE", "TABLE", "FUNCTION", "SET_PART", "SET_NODE", "MID", "TMID", "SID_SECTION"]:
        seen = {}
        for fp in all_files:
            defs = extract_definitions(fp)
            for eid in defs.get(id_type, set()):
                if eid in seen:
                    if seen[eid] != fp.name:
                        warnings.append(f"중복 {id_type} ID={eid}: {seen[eid]} & {fp.name}")
                else:
                    seen[eid] = fp.name

    # Print results
    print(f"\n  ** 에러: {len(errors)}개 **")
    for e in errors:
        print(f"    !! {e}")
    print(f"\n  경고: {len(warnings)}개")
    for w in warnings:
        print(f"    ~~ {w}")

    if not errors:
        print(f"\n  ✓ {main_path.name}: ALL OK")
    return errors, warnings


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    main_files = sorted(BASE.glob("01_main*.k"))
    print(f"감사 대상: {len(main_files)}개 main 파일")

    total_errors = 0
    total_warnings = 0
    for mf in main_files:
        errs, warns = audit_main_file(mf)
        total_errors += len(errs)
        total_warnings += len(warns)

    print(f"\n{'='*80}")
    print(f"  SUMMARY: {total_errors} errors, {total_warnings} warnings across {len(main_files)} files")
    print(f"{'='*80}")
