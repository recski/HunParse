import sys

def getRanges(input):
  seen=set()
  for line in input:
    l=line[1:]
    s=l.split(']')[0]
    x=s.split(':')
    assert len(x)==2
    if x[0]!=x[1]:
      seen.add((x[0],x[1]))
  
  return seen


def isMaximal(allInts, interval):
  allInts.remove(interval)
  a=interval[0]
  b=interval[1]
  for i in allInts:
    x=i[0]
    y=i[1]
    if x

print getRanges(sys.stdin)