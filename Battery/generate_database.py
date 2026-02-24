#!/usr/bin/env python3
"""
09_database*.k 자동 생성 (Phase 1/2/3)
=======================================
Phase별 출력 빈도와 변수 범위를 설정.

사용법:
    python generate_database.py --config battery_config.yaml
    python generate_database.py --phase 1
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict

from battery_utils import (
    load_config, setup_logger, add_common_args,
    write_kfile_header,
)

logger = logging.getLogger(__name__)

_TITLES = {
    1: "Li-ion Cell - Database Output (Phase 1: Mechanical Only)",
    2: "Li-ion Cell - Database Output (Phase 2: Thermo-Mechanical)",
    3: "Li-ion Cell - Database / Output Control",
}

# Phase → (ascii_dt, d3plot_dt, d3thdt_dt, neiph, neips, maxint, therm_flag)
_DB_PARAMS = {
    1: dict(asc="2.0E-05", d3p="2.5E-04", d3t="5.0E-04",
            neiph=12, neips=12, maxint=3, therm=0),
    2: dict(asc="2.0E-05", d3p="2.5E-04", d3t="2.0E-04",
            neiph=16, neips=16, maxint=3, therm=2),
    3: dict(asc="1.0E-03", d3p="5.0E-02", d3t="1.0E-02",
            neiph=24, neips=24, maxint=5, therm=0),
}


def generate_database(config: Dict[str, Any], phase: int = 3,
                      output: str | None = None,
                      log: logging.Logger | None = None) -> str:
    log = log or logger
    if output is None:
        suffix = f"_phase{phase}" if phase < 3 else ""
        output = f"09_database{suffix}.k"
    outpath = Path(output)
    p = _DB_PARAMS[phase]

    with open(outpath, "w", encoding="utf-8") as f:
        write_kfile_header(f, _TITLES[phase])
        f.write("$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")

        # ASCII outputs
        f.write("$\n$ ==================== ASCII ====================\n$\n")
        for kw in ["GLSTAT", "MATSUM", "RCFORC", "SLEOUT", "SPCFORC"]:
            fmt = "1" if phase < 3 else "1         0         0         1"
            f.write(f"*DATABASE_{kw}\n")
            if phase < 3:
                f.write(f"$       DT\n")
                f.write(f"  {p['asc']}\n")
            else:
                f.write(f"$       DT    BINARY      LCUR     IOOPT\n")
                f.write(f"   {p['asc']}         0         0         1\n")
            f.write("$\n")

        if phase >= 2:
            f.write(f"*DATABASE_TPRINT\n")
            f.write(f"  1.0E-04\n")
            f.write("$\n")

        if phase == 3:
            for kw in ["NODOUT", "ELOUT"]:
                f.write(f"*DATABASE_{kw}\n")
                f.write(f"   {p['asc']}         0         0         1\n")
                f.write("$\n")
            f.write("*DATABASE_RBDOUT\n")
            f.write("   1.0E-02         0         0         1\n")
            f.write("$\n")

        # Binary
        f.write("$ ==================== Binary ====================\n$\n")
        f.write("*DATABASE_BINARY_D3PLOT\n")
        f.write("$       DT      LCDT     BEAM    NPLTC    PSETID\n")
        f.write(f"  {p['d3p']}         0         0       0         0\n")
        f.write("$\n")

        f.write("*DATABASE_BINARY_D3THDT\n")
        f.write(f"$       DT      LCDT\n")
        f.write(f"  {p['d3t']}         0\n")
        f.write("$\n")

        if phase == 3:
            f.write("*DATABASE_BINARY_D3DUMP\n")
            f.write("$   DT/CYCL\n")
            f.write("         0\n")
            f.write("$\n")
            f.write("*DATABASE_BINARY_RUNRSF\n")
            f.write("$   DT/CYCL\n")
            f.write("     100000\n")
            f.write("$\n")

        # Extent binary
        f.write("$ ==================== Extent Binary ====================\n$\n")
        f.write("*DATABASE_EXTENT_BINARY\n")
        f.write("$     NEIPH     NEIPS    MAXINT    STRFLG    SIGFLG    EPSFLG    RLTFLG    ENGFLG\n")
        f.write(f"        {p['neiph']}        {p['neips']}         {p['maxint']}")
        f.write("         1         1         1         1         1\n")

        if phase < 3:
            f.write("$   CMPFLG    IEVERP    BEAMIP     DCOMP      SHGE     STSSZ    N3THDT   IALEMAT\n")
            f.write(f"         0         0         0         1         1         1         2         0\n")
            f.write(f"$  NINTSLD   PKP_SEN     SCLP    HYDRO     MSSCL     THERM    INTOUT    NODOUT\n")
            f.write(f"         0         0       1.0         0         0         {p['therm']}         0         0\n")
        else:
            f.write("$   CMPFLG    IEVERP    BEAMIP     DTEFP    GRTEFP    SHTEFP    STSSZ    N3THDT\n")
            f.write("         0         0         0         0         0         0         0         2\n")
            f.write("$   IALEDR    ISDNDS    UNUSED    UNUSED    ENGOUT    IBURN     VTEFP    DTEFSP\n")
            f.write("         0         0                              0         0         0         0\n")

        f.write("$\n")

        # History nodes (phase 3 only)
        if phase == 3:
            f.write("*DATABASE_HISTORY_NODE_SET\n")
            f.write("$     NSID1     NSID2\n")
            f.write("         1         2         0         0         0\n")
            f.write("$\n")

        f.write("*END\n")

    log.info("DB 출력 파일 생성 완료: %s (Phase %d)", outpath, phase)
    return str(outpath)


def main():
    parser = argparse.ArgumentParser(description="09_database*.k 생성")
    add_common_args(parser)
    parser.add_argument("--phase", type=int, nargs="+", default=[1, 2, 3],
                        help="생성할 phase (1, 2, 3)")
    args = parser.parse_args()

    log = setup_logger("gen_db",
                       level=logging.DEBUG if args.verbose else logging.INFO,
                       log_file=args.log_file)
    config = load_config(args.config, validate=True, logger=log)

    for ph in args.phase:
        generate_database(config, phase=ph, log=log)


if __name__ == "__main__":
    main()
