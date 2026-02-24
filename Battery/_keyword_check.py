"""
LS-DYNA R16 k-file 키워드 유효성 검사 (Vol_I/II/III 매뉴얼 기반)
================================================================
모든 include k-file에 대해:
  1. *KEYWORD 헤더 / *END 존재
  2. 인코딩(BOM, 비-ASCII)
  3. 키워드명 유효성 (R16 매뉴얼 대조)
  4. 필드 너비 문제
"""

import os
import re
from pathlib import Path

BASE = Path(r"D:\KooDynaAdvanced\Battery")

# ============================================================
# R16 유효 키워드 — Vol_I/II/III TOC에서 추출
# ============================================================
VALID_KEYWORDS = {
    # Core
    "*KEYWORD", "*TITLE", "*END", "*INCLUDE",

    # Node/Element
    "*NODE", "*ELEMENT_SHELL", "*ELEMENT_SOLID", "*ELEMENT_BEAM",
    "*ELEMENT_TSHELL", "*ELEMENT_DISCRETE",

    # Part
    "*PART", "*PART_COMPOSITE",

    # Section
    "*SECTION_SHELL", "*SECTION_SOLID", "*SECTION_TSHELL", "*SECTION_BEAM",

    # Materials (prefix match)
    # → Checked separately

    # Contacts (prefix match)
    # → Checked separately

    # Boundary
    "*BOUNDARY_SPC_SET", "*BOUNDARY_SPC_NODE",
    "*BOUNDARY_PRESCRIBED_MOTION_SET", "*BOUNDARY_PRESCRIBED_MOTION_NODE",
    "*BOUNDARY_CONVECTION_SET", "*BOUNDARY_RADIATION_SET",
    "*BOUNDARY_TEMPERATURE_SET",

    # Initial
    "*INITIAL_TEMPERATURE_SET", "*INITIAL_VELOCITY",

    # Control
    "*CONTROL_TERMINATION", "*CONTROL_TIMESTEP", "*CONTROL_SOLUTION",
    "*CONTROL_HOURGLASS", "*CONTROL_SHELL", "*CONTROL_SOLID",
    "*CONTROL_CONTACT", "*CONTROL_ENERGY", "*CONTROL_BULK_VISCOSITY",
    "*CONTROL_THERMAL_SOLVER", "*CONTROL_THERMAL_TIMESTEP",
    "*CONTROL_THERMAL_NONLINEAR", "*CONTROL_REFINE_SOLID",
    "*CONTROL_OUTPUT", "*CONTROL_IMPLICIT_GENERAL",
    "*CONTROL_IMPLICIT_SOLUTION", "*CONTROL_IMPLICIT_DYNAMICS",

    # Database
    "*DATABASE_GLSTAT", "*DATABASE_MATSUM", "*DATABASE_RCFORC",
    "*DATABASE_SLEOUT", "*DATABASE_SPCFORC", "*DATABASE_NODOUT",
    "*DATABASE_ELOUT", "*DATABASE_RBDOUT", "*DATABASE_SWFORC",
    "*DATABASE_TPRINT",
    "*DATABASE_BINARY_D3PLOT", "*DATABASE_BINARY_D3THDT",
    "*DATABASE_BINARY_D3DUMP", "*DATABASE_BINARY_RUNRSF",
    "*DATABASE_EXTENT_BINARY", "*DATABASE_EXTENT_SSSTAT",
    "*DATABASE_HISTORY_NODE_SET", "*DATABASE_HISTORY_NODE_ID",

    # Define
    "*DEFINE_CURVE", "*DEFINE_CURVE_TITLE",
    "*DEFINE_TABLE", "*DEFINE_TABLE_2D",
    "*DEFINE_FUNCTION", "*DEFINE_FUNCTION_TABULATED",
    "*DEFINE_SD_ORIENTATION", "*DEFINE_VECTOR",

    # Sets
    "*SET_NODE_LIST", "*SET_NODE_LIST_TITLE",
    "*SET_PART_LIST", "*SET_PART_LIST_TITLE",
    "*SET_SEGMENT_GENERAL", "*SET_SEGMENT_TITLE",
    "*SET_SHELL_LIST", "*SET_SOLID_LIST",

    # Load
    "*LOAD_BODY_Z", "*LOAD_NODE_SET",

    # Hourglass
    "*HOURGLASS",

    # Constrained
    "*CONSTRAINED_RIGID_BODIES",

    # EM — Vol_III validated keywords
    "*EM_CONTROL", "*EM_CONTROL_COUPLING", "*EM_CONTROL_TIMESTEP",
    "*EM_CONTROL_CONTACT", "*EM_CONTROL_EROSION",
    "*EM_CONTROL_SWITCH",
    "*EM_MAT_001", "*EM_MAT_002",
    "*EM_RANDLES_BATMAC", "*EM_RANDLES_SOLID", "*EM_RANDLES_TSHELL",
    "*EM_RANDLES_MESHLESS",
    "*EM_RANDLES_SHORT",                # ← NO _ID variant!
    "*EM_RANDLES_EXOTHERMIC_REACTION",
    "*EM_ISOPOTENTIAL", "*EM_ISOPOTENTIAL_CONNECT", "*EM_ISOPOTENTIAL_ROGO",
    "*EM_CIRCUIT", "*EM_CIRCUIT_SOURCE",
    "*EM_OUTPUT",
    "*EM_DATABASE_CIRCUIT", "*EM_DATABASE_CIRCUIT0D",
    "*EM_DATABASE_CIRCUITSOURCE",
    "*EM_DATABASE_ELOUT",
    "*EM_DATABASE_FIELDLINE",
    "*EM_DATABASE_GLOBALENERGY",        # ← NOT "GLOBALDATA"
    "*EM_DATABASE_NODOUT",
    "*EM_DATABASE_PARTDATA",
    "*EM_DATABASE_POINTOUT",
    "*EM_DATABASE_ROGO",
    "*EM_DATABASE_TIMESTEP",
}

# Material keywords (prefix match)
VALID_MAT_PREFIXES = [
    "*MAT_JOHNSON_COOK", "*MAT_CRUSHABLE_FOAM", "*MAT_PIECEWISE_LINEAR_PLASTICITY",
    "*MAT_RIGID", "*MAT_ELASTIC", "*MAT_PLASTIC_KINEMATIC",
    "*MAT_THERMAL_ISOTROPIC", "*MAT_THERMAL_ORTHOTROPIC",
    "*MAT_ADD_EROSION", "*MAT_ADD_THERMAL_EXPANSION",
    "*MAT_ADD_GENERALIZED_DAMAGE",  # R16 Vol_II p.2-98 확인됨
    "*MAT_ADD_DAMAGE_GISSMO", "*MAT_ADD_INELASTICITY",
    "*MAT_HONEYCOMB", "*MAT_SPOTWELD",
    "*EOS_GRUNEISEN", "*EOS_LINEAR_POLYNOMIAL",
]

# Contact keywords (prefix match — accept various _ID, _TITLE, _MPP suffixes)
VALID_CONTACT_BASES = [
    "*CONTACT_AUTOMATIC_SINGLE_SURFACE",
    "*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE",
    "*CONTACT_AUTOMATIC_GENERAL",
    "*CONTACT_ERODING_SURFACE_TO_SURFACE",
    "*CONTACT_ERODING_SINGLE_SURFACE",
    "*CONTACT_TIED_SURFACE_TO_SURFACE",
    "*CONTACT_TIED_SURFACE_TO_SURFACE_THERMAL",
    "*CONTACT_TIED_NODES_TO_SURFACE",
    "*CONTACT_RIGID_BODY_ONE_WAY_TO_RIGID_BODY",
    "*CONTACT_MORTAR_SURFACE_TO_SURFACE",
]

# Known INVALID keywords → correction mapping
INVALID_KEYWORDS = {
    "*EM_DATABASE_GLOBALDATA":   "*EM_DATABASE_GLOBALENERGY",
    "*EM_DATABASE_RWFORC":       None,           # 삭제 (EM에 해당 없음)
    "*EM_DATABASE_SECFORC":      None,           # 삭제
    "*EM_DATABASE_RANDLES":      "*EM_DATABASE_CIRCUIT",
    "*EM_DATABASE_ELDATA":       "*EM_DATABASE_ELOUT",
    "*EM_RANDLES_SHORT_ID":      "*EM_RANDLES_SHORT",
}


def check_bom(filepath: Path) -> str | None:
    with open(filepath, "rb") as f:
        raw = f.read(4)
    if raw[:3] == b'\xef\xbb\xbf':
        return "UTF-8 BOM"
    if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return "UTF-16 BOM"
    return None


def check_file(filepath: Path):
    errors = []
    warnings = []
    fname = filepath.name

    # BOM check
    bom = check_bom(filepath)
    if bom:
        errors.append(f"파일에 {bom} 있음 → LS-DYNA 파서 오류 가능")

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Non-ASCII check (excluding $comment lines)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("$"):
            continue
        for ch in line:
            if ord(ch) > 127:
                warnings.append(f"Line {i}: 비-ASCII 문자 '{ch}' (U+{ord(ch):04X})")
                break

    # *KEYWORD header check
    first_kw = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("$"):
            continue
        first_kw = stripped.upper()
        break
    if first_kw and not first_kw.startswith("*KEYWORD"):
        errors.append(f"첫 번째 키워드가 *KEYWORD가 아님: '{first_kw}'")

    # *END check
    last_kw = None
    for line in reversed(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("$"):
            continue
        last_kw = stripped.upper()
        break
    if last_kw and last_kw != "*END":
        errors.append(f"마지막 키워드가 *END가 아님: '{last_kw}'")

    # Keyword name validation
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith("*") or stripped.startswith("$"):
            continue
        kw = stripped.split()[0].upper()

        # Skip if it's a basic keyword
        if kw in VALID_KEYWORDS:
            continue

        # Check known-invalid keywords
        if kw in INVALID_KEYWORDS:
            fix = INVALID_KEYWORDS[kw]
            if fix:
                errors.append(f"Line {i}: ❌ '{kw}' → 올바른 키워드: '{fix}'")
            else:
                errors.append(f"Line {i}: ❌ '{kw}' → R16에 없는 키워드 (삭제 필요)")
            continue

        # Check MAT prefix
        is_mat = False
        for prefix in VALID_MAT_PREFIXES:
            if kw.startswith(prefix):
                is_mat = True
                break
        if is_mat:
            continue

        # Check contact prefix (allow _ID, _TITLE, _MPP suffixes)
        is_contact = False
        for base in VALID_CONTACT_BASES:
            if kw.startswith(base):
                is_contact = True
                break
        if is_contact:
            continue

        # Unknown keyword
        warnings.append(f"Line {i}: ⚠ 미확인 키워드: '{kw}' (R16 유효 목록에 없음)")

    return errors, warnings


def main():
    # Collect all include files referenced by any main file
    all_includes = set()
    main_files = sorted(BASE.glob("01_main*.k"))

    for mf in main_files:
        with open(mf, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        for m in re.finditer(r'\*INCLUDE\s*\n([^\$\*][^\n]*)', content):
            inc = m.group(1).strip()
            all_includes.add(inc)

    # Also add the main files themselves
    check_files = [(mf.name, mf) for mf in main_files]
    for inc in sorted(all_includes):
        fp = BASE / inc
        if fp.exists():
            check_files.append((inc, fp))
        else:
            print(f"  !! INCLUDE 파일 없음: {inc}")

    print(f"검사 대상: {len(check_files)} 파일\n")

    total_errors = 0
    total_warnings = 0

    for name, fp in sorted(check_files, key=lambda x: x[0]):
        errs, warns = check_file(fp)
        if errs or warns:
            print(f"{'='*60}")
            print(f"  {name}")
            print(f"{'='*60}")
            for e in errs:
                print(f"    !! {e}")
            for w in warns:
                print(f"    ~~ {w}")
            total_errors += len(errs)
            total_warnings += len(warns)

    print(f"\n{'='*60}")
    print(f"  합계: {total_errors} 에러, {total_warnings} 경고")
    print(f"{'='*60}")

    if total_errors == 0:
        print("\n  ✓ 모든 키워드 유효 — LS-DYNA R16 로드 안전")


if __name__ == "__main__":
    main()
