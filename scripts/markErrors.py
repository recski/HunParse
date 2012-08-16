import sys
for line in sys.stdin:
    if line == '\n':
        print
        continue
    l = line.strip().split()
    if l[-1]!=l[-2] and (l[-2] == 'O' or 'NP' in l[-2]):
        print '\t'.join(l+['@'])
    else:
        print line,
