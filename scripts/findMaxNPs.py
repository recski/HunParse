import sys
bestlines=[]
bestsize = 0
for line in sys.stdin:
  l=line.split()
  index=l[0]
  assert index[0]=='[' and index[-1]==']'
  mid = index.find(':')
  start = int(index[1:mid])
  end = int(index[mid+1:-1])
  size = end-start
  if bestsize < size:
    bestlines = [line]
    bestsize = size
  elif bestsize == size:
    bestlines+=[line]
  
  else:
    pass
  

for line in bestlines: print line
  