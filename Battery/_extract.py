import sys
lines = open('02_mesh_stacked.k','r').readlines()
pids = []
for i,line in enumerate(lines):
    if line.strip()=='*PART':
        title = lines[i+1].strip() if i+1<len(lines) else ''
        data = lines[i+2].strip().split() if i+2<len(lines) else []
        pid = data[0] if data else '?'
        mid = data[2] if len(data)>2 else '?'
        pids.append((pid,mid,title))
print('Total PARTs:', len(pids))
for p in pids[:10]:
    print('  PID='+p[0].rjust(6)+' MID='+p[1].rjust(4)+' '+p[2])
print('...')
for p in pids[-5:]:
    print('  PID='+p[0].rjust(6)+' MID='+p[1].rjust(4)+' '+p[2])
