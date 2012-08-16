#!/usr/bin/python
import sys
import optfunc
import pickle
import kr2terminals
from nltk import grammar, parse

def log(x):
  sys.stderr.write(str(x)+'\n')

def splitCorp(file):
  corp=[[]]
  for line in open(file):
    if line =='\n':
      corp.append([])
    else:
      corp[-1].append(line)
  
  return corp

def main(grammarWoTerminals='', text='', serialize=None, uncrossing=False, countCrosses=False, max_maxNpTag=False, min_minNpTag=False, findWrongChunks=False, useCfg=False):
  sys.stderr.write('loading nltk...')
  import nltk
  corp = splitCorp(text)
  
  cLength=len(corp)
  grWoTerm = [l.strip('\n') for l in open(grammarWoTerminals).readlines()]
  sys.stderr.write('done!\nparsing...')  
  
  
  if serialize:
    parseOut = open(serialize, 'w')
  
  allCrosses=0.0
  allSens=0.0
  for c,sen in enumerate(corp):
    allSens+=1
    if c*100/cLength>(c-1)*100/cLength: sys.stderr.write(str(c*100/cLength)+'% ')
    toks = [l.strip('\n').split()[1].split('/')[-1] for l in sen]
    words = [l.strip('\n').split()[0] for l in sen]
    
    chart = parseSentence(toks, grWoTerm, useCfg)
    
    if max_maxNpTag:
      tagMaxNPs(chart, sen, useCfg)
      print
    
    if min_minNpTag:
      tagMinNPs(chart, sen)
      print
      
    if findWrongChunks:
      getWrongChunks(chart, sen)
    if serialize:
      serializeParse(chart, toks, words, parseOut)
    if uncrossing:
      findUncrossingNPs(chart, words, useCfg)
    if countCrosses:  
      allCrosses+=findUncrossingNPs(chart, words, useCfg, countCrosses)
  
  if countCrosses:
    print 'No. of sentences:', str(allSens)
    print 'No. of crosses:', str(allCrosses)
    print 'Average no. of crosses per sentence:', str(allCrosses/allSens)
    

def getWrongChunks(chart, sen):
  npSpans = findNPs(chart)
  #log(npSpans)
  chunkSpans = getChunks(sen)
  #log(chunkSpans)
  for chunk in chunkSpans:
    if chunk not in npSpans:
      printChunk(chunk, sen)

def printChunk(chunk, sen):
  words=[line.split()[0] for line in sen[chunk[0]:chunk[1]]]
  krs=[line.split()[1] for line in sen[chunk[0]:chunk[1]]]
  print ' '.join(words)+'\t'+' '.join(krs)      

def getChunks(sen):
  spans=set()
  inNP=False
  currStart = 0
  for c,tok in enumerate(sen):
    tag = tok.split()[-1]
    if tag[0]=='B':
      if inNP:
        spans.add((currStart, c))
      else:
        inNP=True
      currStart = c  
    elif tag[0]=='O':
      if inNP:
        spans.add((currStart, c))
        inNP=False

  return spans


def keepUnCrossing(spans):
  newSpans=set()
  for span in spans:
    keep = True
    for span2 in spans:
      if isCrossing(span, span2):
        keep = False
    if keep:
      newSpans.add(span)
  
  return newSpans


def tagMaxNPs(chart, sen, useCfg):
  spans = findNPs(chart, useCfg)
  unContainedSpans = [span for span in spans if not isContained(span, spans)]
  
  keepLonger = False
  
  if keepLonger:
    filteredSpans = keepLonger(unContainedSpans)
  else:
    filteredSpans = keepUnCrossing(unContainedSpans)
    
  printTagging(sen, filteredSpans)


def tagMinNPs(chart, sen):
  spans = findNPs(chart, False)
  minSpans = [ span for span in spans if True not in [isContained(x, set([span])) for x in spans ] ]
  unCrossingMinSpans = keepUnCrossing(minSpans)
  printTagging(sen, minSpans)

def printTagging(sen, spans):
  
  posStart=set()
  posInt=set()
  for span in spans:
    posStart.add(span[0])
    for i in range(span[0]+1, span[1]):
      posInt.add(i)
      
  for c, line in enumerate(sen):
    if c in posInt:
      tag = 'I-NP'
    elif c in posStart:
      tag = 'B-NP'
    else:
      tag = 'O'
    
    print '\t'.join((line.strip('\n'),tag))

def parseSentence(toks, grammarWoTerm, cfg):
  if cfg:
    gr = grammar.parse_cfg(grammarWoTerm)
    parser = parse.BottomUpChartParser(gr)
  else:
    termRules=[]
    for kr in toks:
      termRules.append(kr2terminals.getRuleFromKr(kr))
    
    fullGrammar = '\n'.join(grammarWoTerm+termRules)
  
    gr = grammar.parse_fcfg(fullGrammar) 
    parser = parse.FeatureBottomUpChartParser(gr)
  
  
  chart = parser.chart_parse(toks)
  return chart  

def serializeParse(chart, toks, words, out):    
    out.write(' '.join(toks)+'\n'+' '.join(words)+'\n')
    for edge in chart.edges():
      if edge.is_complete():
        out.write(repr(edge)+'\n')
    
    print  
    

def findNPs(chart, useCfg):
    spans=set()
    
    for edge in chart.edges():
      if type(edge.lhs()) == str or not edge.is_complete():
        continue
        
      leftS = edge.lhs()
        
      for key in leftS.keys():
        if type(key)!=str:
          if leftS[key]=='NOUN' and edge.lhs().has_key('BAR') and edge.lhs()['BAR']!=0:
            spans.add(edge.span())
    
    return spans


def isContained(span, spans):      
    for span2 in spans:
      if span2 == span: continue
      a=span[0]
      b=span[1]
      c=span2[0]
      d=span2[1]  
      if not (a<c or b>d):
        return True
    return False


def findUncrossingNPs(chart, words, useCfg, countCrosses=False):    
    crosses=0
    cross=[]
    spans = findNPs(chart, useCfg)
    if not countCrosses:
      for i in range(len(words)):
        sys.stdout.write('_')
      print
    keptSpans=set()
    for span in spans:
      #displaySpan(span)
      if not isContained(span, spans):
        keptSpans.add(span)
    
    
    for span in keptSpans:  
      if not countCrosses:
        displaySpan(span, len(words))
      for span2 in keptSpans:
        if isCrossing(span, span2):
          cross.append((span, span2))
          crosses+=1
      
    if not countCrosses:
      print ' '.join(words)
      for cr in cross:
        print '\t'.join([' '.join(words[sp[0]:sp[1]]) for sp in cr])
    
    else:
      return crosses
  
def isCrossing(span1, span2):        
  a=span1[0]
  b=span1[1]
  c=span2[0]
  d=span2[1]
  if a<c and c<b and b<d:
    return True
  return False

def displaySpan(span, senLength):
  for i in range(senLength):
      if i<span[0] or i>=span[1]:
        sys.stdout.write('.')
      else:
        sys.stdout.write('_')
  print
    

def x():
#if __name__=='__main__':
  optfunc.run(main)

profile = False

if profile:  
  import cProfile
  cProfile.run('x()')
else:
  x()