#!/usr/bin/python
import sys
import nltk
import optfunc
from readChart import log
def featureRule2Rule(line, keptFeats, removeFeats):
  #log(line)
  left, right = line.lhs(), line.rhs()
  newLeft = fcfg2cfg(left, keptFeats, removeFeats)
  newRight = ' '.join([fcfg2cfg(part, keptFeats, removeFeats) for part in right])
  return newLeft+' -> '+newRight
  
def fcfg2cfg(featStruct, keptFeats, removeFeats):
  out=''
  if type(featStruct) == str:
    return "'"+featStruct+"'"
  for feat in featStruct.items():
    #log(feat)
    if type(feat[0])!=str:
      if type(feat[1])==str:
        out = feat[1]+out # Ez a *type* erteke
        if removeFeats:
          return feat[1]
      else:
        out += '/'+feat[1].values()[0] #Ez a per jelhez kell, mert a *slash* erteke is FeatStruct
      continue
    elif feat[0] == 'BAR':
      if type(feat[1])==int:
        out+='_'+str(feat[1])
    elif feat[0] in keptFeats:
      if feat[1]==1:
        out+='_'+feat[0]
        continue
  return out  
      
def main(file='grammars/testRules.txt', keptFeats=['PLUR', 'POSS'], removeFeats=False):
  gr = open(file).readlines()
  seen=[]
  for line in gr:
    if line == '\n' or line[0]=='#':
      print line,
    else:
      parsedLine = nltk.grammar.parse_fcfg(line.strip('\n')).productions()
      assert len(parsedLine) == 1
      rule = parsedLine[0]
      outRule = featureRule2Rule(rule, keptFeats, removeFeats)
      if outRule in seen:
        pass
      else:
        print outRule
        seen.append(outRule)

optfunc.run(main)  