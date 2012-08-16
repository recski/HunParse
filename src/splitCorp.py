#!/usr/bin/python
import sys


def printSen(sen, file):
  for tok in sen:
    file.write('\t'.join(tok)+'\n')
  file.write('\n')  

def splitCorp(corp, n, outPath):
  senNo = len(corp)
  pieceLen = (senNo/n)+1
  for i in range(n):
    outFileName = outPath+'/'+str(i)
    outFile = open(outFileName, 'w')
    print outPath+'\t'+str(i)
    for c in range(i*pieceLen, (i+1)*pieceLen):
      if c >= senNo:
        continue
      else:
        printSen(corp[c], outFile)
  
def getCorp(input):
  corp = [[]]
  for line in input:
    if line == '\n':
      corp.append([])
      continue
    corp[-1].append(line.strip('\n').split())
    
  return corp  

def main(n=8, outPath='parallel/'):
  corp = getCorp(sys.stdin)
  splitCorp(corp, int(n), outPath)


import optfunc
optfunc.run(main)  