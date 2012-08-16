#!/usr/bin/python
import sys
corp=[[]]
for line in sys.stdin:
  if line == '\n':
    corp.append([])
  else:
    corp[-1].append(line)
print '\n\n'.join(['\n'.join([str(c)+' '+line.strip('\n') for c,line in enumerate(sen)]) for sen in corp])

