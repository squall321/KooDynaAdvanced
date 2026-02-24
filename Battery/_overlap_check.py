"""Pouch vs Cell overlap analysis on actual mesh file."""
import re
from pathlib import Path
import numpy as np
from collections import defaultdict

def parse_mesh(fname):
    """Parse nodes, shells, solids, parts from k-file."""
    text = Path(fname).read_text(encoding='utf-8')
    lines = text.split('\n')
    
    nodes = {}       # nid -> (x, y, z)
    parts = {}       # eid -> pid
    shell_nodes = {} # eid -> (n1,n2,n3,n4)
    solid_nodes = {} # eid -> (n1..n8)
    part_names = {}  # pid -> name
    sections = {}    # sid -> {T}
    part_sid = {}    # pid -> sid
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line == '*NODE':
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('*'):
                if lines[i].strip().startswith('$') or not lines[i].strip():
                    i += 1; continue
                s = lines[i]
                try:
                    nid = int(s[0:8])
                    x = float(s[8:24])
                    y = float(s[24:40])
                    z = float(s[40:56])
                    nodes[nid] = (x, y, z)
                except:
                    pass
                i += 1
            continue
        
        elif line == '*ELEMENT_SHELL':
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('*'):
                if lines[i].strip().startswith('$') or not lines[i].strip():
                    i += 1; continue
                s = lines[i]
                try:
                    eid = int(s[0:8])
                    pid = int(s[8:16])
                    n1 = int(s[16:24])
                    n2 = int(s[24:32])
                    n3 = int(s[32:40])
                    n4 = int(s[40:48])
                    parts[eid] = pid
                    shell_nodes[eid] = (n1, n2, n3, n4)
                except:
                    pass
                i += 1
            continue
        
        elif line == '*ELEMENT_SOLID':
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('*'):
                if lines[i].strip().startswith('$') or not lines[i].strip():
                    i += 1; continue
                s = lines[i]
                try:
                    eid = int(s[0:8])
                    pid = int(s[8:16])
                    parts[eid] = pid
                    ns = []
                    for k in range(8):
                        ns.append(int(s[16+k*8:24+k*8]))
                    solid_nodes[eid] = tuple(ns)
                except:
                    pass
                i += 1
            continue
        
        elif line == '*PART':
            if i + 2 < len(lines):
                name = lines[i+1].strip()
                dl = lines[i+2]
                try:
                    pid = int(dl[0:10])
                    sid = int(dl[10:20])
                    part_names[pid] = name
                    part_sid[pid] = sid
                except:
                    pass
            i += 3
            continue
        
        elif line.startswith('*SECTION_SHELL'):
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('$'):
                j += 1
            if j < len(lines):
                try:
                    sid = int(lines[j][0:10])
                except:
                    sid = 0
                # Find thickness line
                k = j + 1
                while k < len(lines) and lines[k].strip().startswith('$'):
                    k += 1
                if k < len(lines):
                    try:
                        t1 = float(lines[k][0:10])
                        sections[sid] = t1
                    except:
                        pass
            i = k + 1 if 'k' in dir() else i + 1
            continue
        
        i += 1
    
    return nodes, parts, shell_nodes, solid_nodes, part_names, part_sid, sections


fname = '02_mesh_stacked_tier-1.k'
print(f'Parsing {fname}...')
nodes, parts, shells, solids, pnames, part_sid, sections = parse_mesh(fname)
print(f'  Nodes: {len(nodes)}, Shells: {len(shells)}, Solids: {len(solids)}')
print(f'  Parts: {len(pnames)}')

# Classify PIDs
pouch_pids = {10, 11, 12}  # Top, Bottom, Side
cell_pids = set()
for pid, name in sorted(pnames.items()):
    cat = 'POUCH' if pid in pouch_pids else 'OTHER'
    sid = part_sid.get(pid, 0)
    t = sections.get(sid, 0)
    print(f'    PID {pid:>5d}  SID={sid}  T={t:.4f}  {name}  [{cat}]')
    if pid not in pouch_pids and pid not in {30, 31, 100}:  # exclude PCM, impactor
        cell_pids.add(pid)

print(f'\n  Pouch PIDs: {sorted(pouch_pids)}')
print(f'  Cell PIDs:  {sorted(cell_pids)}')

# Collect Z ranges per PID
pid_z_ranges = defaultdict(lambda: [1e30, -1e30])
pid_x_ranges = defaultdict(lambda: [1e30, -1e30])
pid_y_ranges = defaultdict(lambda: [1e30, -1e30])

for eid, ns in shells.items():
    pid = parts[eid]
    for nid in ns:
        if nid in nodes:
            x, y, z = nodes[nid]
            pid_z_ranges[pid][0] = min(pid_z_ranges[pid][0], z)
            pid_z_ranges[pid][1] = max(pid_z_ranges[pid][1], z)
            pid_x_ranges[pid][0] = min(pid_x_ranges[pid][0], x)
            pid_x_ranges[pid][1] = max(pid_x_ranges[pid][1], x)
            pid_y_ranges[pid][0] = min(pid_y_ranges[pid][0], y)
            pid_y_ranges[pid][1] = max(pid_y_ranges[pid][1], y)

for eid, ns in solids.items():
    pid = parts[eid]
    for nid in ns:
        if nid in nodes:
            x, y, z = nodes[nid]
            pid_z_ranges[pid][0] = min(pid_z_ranges[pid][0], z)
            pid_z_ranges[pid][1] = max(pid_z_ranges[pid][1], z)
            pid_x_ranges[pid][0] = min(pid_x_ranges[pid][0], x)
            pid_x_ranges[pid][1] = max(pid_x_ranges[pid][1], x)
            pid_y_ranges[pid][0] = min(pid_y_ranges[pid][0], y)
            pid_y_ranges[pid][1] = max(pid_y_ranges[pid][1], y)

print('\n' + '='*80)
print('GEOMETRY RANGES')
print('='*80)
print(f'{"PID":>5s} {"Name":<30s} {"X_min":>8s} {"X_max":>8s} {"Y_min":>8s} {"Y_max":>8s} {"Z_min":>8s} {"Z_max":>8s}')
for pid in sorted(pid_z_ranges.keys()):
    name = pnames.get(pid, '?')[:30]
    xr = pid_x_ranges[pid]
    yr = pid_y_ranges[pid]
    zr = pid_z_ranges[pid]
    print(f'{pid:>5d} {name:<30s} {xr[0]:>8.4f} {xr[1]:>8.4f} {yr[0]:>8.4f} {yr[1]:>8.4f} {zr[0]:>8.4f} {zr[1]:>8.4f}')

# Check overlaps between pouch and cell parts
print('\n' + '='*80)
print('OVERLAP ANALYSIS (Pouch vs Cell)')
print('='*80)

for ppid in sorted(pouch_pids):
    pname = pnames.get(ppid, '?')
    pz = pid_z_ranges.get(ppid, [0,0])
    px = pid_x_ranges.get(ppid, [0,0])
    py = pid_y_ranges.get(ppid, [0,0])
    
    # Get section thickness for contact
    sid = part_sid.get(ppid, 0)
    ht = sections.get(sid, 0) / 2.0
    
    pz_lo = pz[0] - ht
    pz_hi = pz[1] + ht
    px_lo = px[0] - ht
    px_hi = px[1] + ht
    py_lo = py[0] - ht
    py_hi = py[1] + ht
    
    print(f'\n  Pouch PID {ppid} ({pname}):')
    print(f'    Node range:    X=[{px[0]:.4f}, {px[1]:.4f}]  Y=[{py[0]:.4f}, {py[1]:.4f}]  Z=[{pz[0]:.4f}, {pz[1]:.4f}]')
    print(f'    Contact range: X=[{px_lo:.4f}, {px_hi:.4f}]  Y=[{py_lo:.4f}, {py_hi:.4f}]  Z=[{pz_lo:.4f}, {pz_hi:.4f}]')
    print(f'    Section T={sections.get(sid, 0):.4f} (SID={sid})')
    
    for cpid in sorted(cell_pids):
        cname = pnames.get(cpid, '?')
        cz = pid_z_ranges.get(cpid, [0,0])
        cx = pid_x_ranges.get(cpid, [0,0])
        cy = pid_y_ranges.get(cpid, [0,0])
        
        csid = part_sid.get(cpid, 0)
        cht = sections.get(csid, 0) / 2.0
        
        cz_lo = cz[0] - cht
        cz_hi = cz[1] + cht
        cx_lo = cx[0] - cht
        cx_hi = cx[1] + cht
        cy_lo = cy[0] - cht
        cy_hi = cy[1] + cht
        
        # Check bounding box overlap
        x_overlap = px_hi > cx_lo and cx_hi > px_lo
        y_overlap = py_hi > cy_lo and cy_hi > py_lo
        z_overlap = pz_hi > cz_lo and cz_hi > pz_lo
        
        if x_overlap and y_overlap and z_overlap:
            print(f'    ** OVERLAP with PID {cpid} ({cname}):')
            print(f'       Cell range: X=[{cx[0]:.4f},{cx[1]:.4f}] Y=[{cy[0]:.4f},{cy[1]:.4f}] Z=[{cz[0]:.4f},{cz[1]:.4f}]')
            print(f'       Contact:    X=[{cx_lo:.4f},{cx_hi:.4f}] Y=[{cy_lo:.4f},{cy_hi:.4f}] Z=[{cz_lo:.4f},{cz_hi:.4f}]')

print('\n' + '='*80)
print('SECTION THICKNESS CHECK')
print('='*80)
thickness_map = {
    'Pouch': 0.153,
    'Al_CC': 0.012,
    'Cu_CC': 0.008,
    'PE_Sep': 0.020,
}
for pid in sorted(pnames.keys()):
    name = pnames[pid]
    sid = part_sid.get(pid, 0)
    actual_t = sections.get(sid, 0)
    
    expected = None
    if 'Pouch' in name:
        expected = 0.153
    elif 'Al_CC' in name:
        expected = 0.012
    elif 'Cu_CC' in name:
        expected = 0.008
    elif 'Separator' in name:
        expected = 0.020
    
    if expected is not None and abs(actual_t - expected) > 1e-6:
        print(f'  !! PID {pid:>5d} ({name}): SID={sid} T={actual_t:.4f} but EXPECTED T={expected:.4f}')
    elif expected is not None:
        print(f'     PID {pid:>5d} ({name}): T={actual_t:.4f} OK')
