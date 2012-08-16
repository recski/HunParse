#!/usr/bin/python
import sys
import optfunc

class Chart():
  def __init__(self, text):
    krs, words = text[:2] 
    krs = eval(krs)
    words = eval(words)
    edges = []
    for line in text[2:]:
      strings = line.split()
      assert strings[0][0]=='['
      spanStr = strings[0].split(':')
      start = int(spanStr[0][1:])
      end = int(spanStr[1][:-1])
      span = (start, end)
      rest = strings[1:]
      edges.append((span, rest))
    
    self.krs = krs
    self.words = words
    self.edges = edges
    self.length = len(krs)
  
  def getMaxEdge(self):
    bestLen = 0
    bestEdge = None
    for edge in self.edges:
      span = edge[0]
      length = span[1]-span[0]
      if length > bestLen:
        bestEdge = edge
        bestLen = length
    
    return bestEdge, bestLen
  
  def isFullParsed(self):
    bestEdge, bestLength = self.getMaxEdge()
    #log ('length', self.length)
    #log ('best', bestLength)
    if bestLength == self.length:
      return True
    return False


def getCharts(input):
  lines = []
  for line in input:
    if line == '\n' or line == '[]\n':
      if lines == []: continue
      yield Chart(lines)
      lines=[]
    else:  
      lines.append(line)

def log(*a):
  for stuff in a:
    sys.stderr.write(str(stuff)+' ')
  sys.stderr.write('\n')
  

def main(stdin, advErrors=False, printErrors=False, krCountFile='krCount.txt', rawKr=False):
  parse = getCharts(stdin)
  krCountFile = open(krCountFile)
  krCount = eval(krCountFile.readline())
  errors = evalParse(parse, krCount)
  if advErrors:
    getAdvErrors(errors)
  if printErrors:
    dumpErrors(errors, rawKr)   
  
def dumpErrors(errors, rawKr):
  errors.sort()
  errors.reverse()
  for e in errors:
    if rawKr:
      print ' '.join(e[1])
    else:
      print e[0],' '.join(e[1]),'/'.join(e[2:])

def evalParse(parse, krCount):
  all=0.0
  full=0.0
  errors=[]
  seenKrs=[]
  for chart in parse:
    if chart.krs in seenKrs:
      continue
    else:
      seenKrs.append(chart.krs)
      
    value = krCount[' '.join(chart.krs)]
    c, chunks = value[0], value[1:]
    all+=c
    if chart.isFullParsed():
      full+=c
    else:
      errors.append([c, chart.krs]+chunks)
    
  
  log('charts: ', all)
  log('full: ', full)
  log((full/all)*100,'%')

  return errors
  
def getAdvErrors(errors):
  advErrors=[]
  for e in errors:
    if 'ADV' in e[1]:
      advErrors.append(e)
  
  adverbs = []
  for e in advErrors:
    for c, word in enumerate(e[1]):
      if word == 'ADV':
        adverbs+=[chunk.split()[c] for chunk in e[2:]]
  
  #print '\n'.join(adverbs)
  for e in errors:
    for c,kr in enumerate(e[1]):
      print '\t'.join([e[2].split()[c], kr])
    print
    
    
if __name__ == '__main__':
  optfunc.run(main)
  
  