"""Fix SpaceBeforeCmtFlag in mesh files: move $ to column 1 for section comment headers."""
import re
import sys

files = sys.argv[1:] if len(sys.argv) > 1 else ['02_mesh_stacked.k']

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        c = fh.read()
    # Replace indented $SID and $T1 comment lines with $ at column 1
    c = re.sub(r'(?m)^[ \t]+(\$SID\s+ELFORM)', r'$      SID    ELFORM', c)
    c = re.sub(r'(?m)^[ \t]+(\$T1\s+)', r'$       T1        ', c)
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(c)
    print(f'{f}: done')
